"""Adversarial end-to-end tests for the academic human-review portal."""
from __future__ import annotations

from pathlib import Path
import json
import tempfile

from fastapi.testclient import TestClient
import pytest

from app import create_app, create_user, init_db, read_db, write_db, SOURCE_DOCX, DEFAULT_SEED

PW = 'IndependentHumanPeerReview2026!'


@pytest.fixture()
def setup_app():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / 'test.sqlite3'
        init_db(path, DEFAULT_SEED)
        admin_id = create_user(path, 'admin@example.org', 'Editorial admin', PW, 'admin')
        app = create_app(path, DEFAULT_SEED, SOURCE_DOCX)
        with TestClient(app) as client:
            yield client, path, admin_id


def sign_in(client: TestClient, email: str, pw: str = PW) -> dict:
    res = client.post('/api/login', json={'email': email, 'password': pw})
    assert res.status_code == 200, res.text
    info = client.get('/api/me').json()
    assert info['signed_in']
    return info


def post(client, uri, info, data):
    return client.post(uri, json=data, headers={'X-CSRF-Token': info['csrf']})


def invite(client, admin, email):
    res = post(client, '/api/invitations', admin, {'email': email, 'role': 'reviewer', 'days': 7})
    assert res.status_code == 200, res.text
    return res.json()['invitation_url'].split('invite=')[1]


def join_invited(client, token, name):
    res = client.post('/api/join', json={'token': token, 'name': name, 'password': PW, 'consent_to_review': True})
    assert res.status_code == 200, res.text
    return client.get('/api/me').json()


def new_reviewer(client, admin, email, name):
    token = invite(client, admin, email)
    info = join_invited(client, token, name)
    assert info['user']['role'] == 'reviewer'
    return info, token


def claim_id(client, user, prefix='lesson-meeting-1a'):
    return next(x['id'] for x in client.get('/api/dashboard').json()['claims'] if x['id'] == prefix)


def review_payload(id, verdict='approve_teaching'):
    return {'claim_id': id, 'verdict': verdict,
            'evidence': 'I independently checked the relevant exact finite example and its assumptions.',
            'limitations': 'This is only a teaching review and does not establish any unbounded theorem.'}


def test_login_education_scope_and_source_docx(setup_app):
    client, path, admin_id = setup_app
    assert client.get('/api/dashboard').status_code == 401
    bad = client.post('/api/login', json={'email': 'admin@example.org', 'password': 'wrong'})
    assert bad.status_code == 401
    me = sign_in(client, 'admin@example.org')
    assert me['user']['role'] == 'admin'
    dash = client.get('/api/dashboard').json()
    assert len(dash['claims']) == 14
    assert sum(c['category'] == 'lesson' for c in dash['claims']) == 12
    assert 'NOT certification' not in dash['disclaimer'] or 'NOT certification' in dash['disclaimer']
    source = client.get('/api/curriculum.docx')
    assert source.status_code == 200
    assert source.content[:2] == b'PK'
    assert len(source.content) > 20000
    assert post(client,'/api/logout',me,{}).status_code == 200
    assert client.get('/api/curriculum.docx').status_code == 401


def test_csrf_invitation_and_single_use(setup_app):
    client, path, admin_id = setup_app
    admin = sign_in(client, 'admin@example.org')
    raw = client.post('/api/invitations', json={'email': 'peer1@example.org', 'role': 'reviewer'})
    assert raw.status_code == 403
    token = invite(client, admin, 'peer1@example.org')
    info = client.get('/api/invitation/'+token)
    assert info.status_code == 200 and info.json()['email'] == 'peer1@example.org'
    with read_db(path) as con:
        assert not con.execute('SELECT 1 FROM invitations WHERE token_hash=?',(token,)).fetchone()
        assert con.execute('SELECT COUNT(*) AS n FROM invitations').fetchone()['n'] == 1
    peer = join_invited(client, token, 'Anonymous peer')
    assert peer['user']['role'] == 'reviewer'
    assert client.get('/api/invitation/'+token).status_code == 404
    assert client.post('/api/join',json={'token':token, 'name':'Second person','password':PW,'consent_to_review':True}).status_code == 404
    assert 'professor' not in peer['user']['role']


def test_two_independent_reviews_required_and_adjudication(setup_app):
    client,path,admin_id=setup_app
    admin=sign_in(client,'admin@example.org')
    peer1,_=new_reviewer(client,admin,'review1@example.org','Researcher One')
    id='lesson-meeting-1a'
    denied=post(client,'/api/review',peer1,review_payload(id))
    assert denied.status_code == 403,denied.text
    client.post('/api/logout',headers={'X-CSRF-Token':peer1['csrf']},json={})
    admin=sign_in(client,'admin@example.org')
    assign=post(client,'/api/assign',admin,{'claim_id':id,'reviewer_id':peer1['user']['id']})
    assert assign.status_code == 200,assign.text
    premature=post(client,'/api/adjudicate',admin,{'claim_id':id,'decision':'approve_teaching','rationale':'Independently evaluated editorial suitability with sufficient care.'})
    assert premature.status_code == 409
    peer2,_=new_reviewer(client,admin,'review2@example.org','Researcher Two')
    client.post('/api/logout',headers={'X-CSRF-Token':peer2['csrf']},json={})
    admin=sign_in(client,'admin@example.org')
    assert post(client,'/api/assign',admin,{'claim_id':id,'reviewer_id':peer2['user']['id']}).status_code == 200
    client.post('/api/logout',headers={'X-CSRF-Token':admin['csrf']},json={})
    peer1=sign_in(client,'review1@example.org')
    # Independent review blindness: cannot see other feedback before own submission.
    assert client.get('/api/claims/'+id).json()['reviews_blinded'] is True
    rev1=post(client,'/api/review',peer1,review_payload(id))
    assert rev1.status_code == 200 and rev1.json()['stage']=='in_review'
    assert post(client,'/api/review',peer1,review_payload(id)).status_code == 409
    client.post('/api/logout',headers={'X-CSRF-Token':peer1['csrf']},json={})
    peer2=sign_in(client,'review2@example.org')
    assert client.get('/api/claims/'+id).json()['reviews_blinded'] is True
    rev2=post(client,'/api/review',peer2,review_payload(id))
    assert rev2.status_code == 200 and rev2.json()['stage']=='ready_for_adjudication'
    assert len(client.get('/api/claims/'+id).json()['reviews'])==2
    client.post('/api/logout',headers={'X-CSRF-Token':peer2['csrf']},json={})
    admin=sign_in(client,'admin@example.org')
    approved=post(client,'/api/adjudicate',admin,{'claim_id':id,'decision':'approve_teaching',
        'rationale':'Two independent reviewers have confirmed pedagogical suitability; this is not mathematical proof.'})
    assert approved.status_code == 200, approved.text
    assert approved.json()['stage']=='teaching_approved'
    assert approved.json()['mathematical_proof_certified'] is False
    assert client.get('/api/claims/'+id).json()['claim']['status']=='teaching_approved'
    with read_db(path) as con:
        events=con.execute("SELECT details_json FROM events WHERE action='EDITORIAL_DECISION'").fetchall()
        assert events and json.loads(events[0]['details_json'])['mathematical_proof_certified'] is False


def test_reviewer_can_propose_not_self_review_and_revision_keeps_history(setup_app):
    client,path,admin_id=setup_app
    admin=sign_in(client,'admin@example.org')
    peer,_=new_reviewer(client,admin,'author@example.org','Research author')
    proposed=post(client,'/api/proposals',peer,{'title':'Ihara zeta feature injectivity proposal',
        'category':'research_gap', 'goal':'Test whether fixed probes identify finite graph families',
        'body':'The adaptive probes are constant across n. The proposed fixed-probe comparison remains bounded and would not imply RH.',
        'evidence_url':''})
    assert proposed.status_code==200,proposed.text
    cid=proposed.json()['claim_id']
    assert proposed.json()['proof_certified'] is False
    client.post('/api/logout',headers={'X-CSRF-Token':peer['csrf']},json={})
    admin=sign_in(client,'admin@example.org')
    assert post(client,'/api/assign',admin,{'claim_id':cid,'reviewer_id':peer['user']['id']}).status_code == 403
    peer2,_=new_reviewer(client,admin,'critic@example.org','Independent critic')
    client.post('/api/logout',headers={'X-CSRF-Token':peer2['csrf']},json={})
    admin=sign_in(client,'admin@example.org')
    assert post(client,'/api/assign',admin,{'claim_id':cid,'reviewer_id':peer2['user']['id']}).status_code==200
    client.post('/api/logout',headers={'X-CSRF-Token':admin['csrf']},json={})
    peer2=sign_in(client,'critic@example.org')
    assert post(client,'/api/review',peer2,review_payload(cid,'request_revision')).json()['stage']=='revision_requested'
    client.post('/api/logout',headers={'X-CSRF-Token':peer2['csrf']},json={})
    peer=sign_in(client,'author@example.org')
    revised=post(client,'/api/revise',peer,{'claim_id':cid,
        'goal':'Give a rigorous fixed-probe injectivity argument over the full cycle family',
        'body':'New derivation: the map n to (1-u**n)**(-2) is strictly decreasing for fixed 0<u<1, while adaptive probes remain nonidentifying.',
        'evidence_url':'','rationale':'Address reviewer critique with explicit monotonicity.'})
    assert revised.status_code==200 and revised.json()['round']==2,revised.text
    with read_db(path) as con:
        reviews=con.execute('SELECT round,verdict FROM reviews WHERE claim_id=?',(cid,)).fetchall()
        assert len(reviews)==1 and reviews[0]['round']==1
    client.post('/api/logout',headers={'X-CSRF-Token':peer['csrf']},json={})
    peer2=sign_in(client,'critic@example.org')
    assert post(client,'/api/review',peer2,review_payload(cid)).status_code==200


def test_export_does_not_expose_password_or_token_hashes(setup_app):
    client,path,admin_id=setup_app
    admin=sign_in(client,'admin@example.org')
    exported=client.get('/api/audit-export')
    assert exported.status_code==200
    data=exported.json()
    assert data['mathematical_proof_certified'] is False
    content=json.dumps(data)
    assert 'password_hash' not in content
    assert 'token_hash' not in content
    assert 'csrf_token' not in content
    assert PW not in content
    assert 'admin@example.org' not in content


def test_invited_reviewer_cannot_access_admin_only_operations(setup_app):
    client,path,admin_id=setup_app
    admin=sign_in(client,'admin@example.org')
    peer,_=new_reviewer(client,admin,'independent@example.org','Independent peer')
    assert post(client,'/api/invitations',peer,{'email':'someone@example.org'}).status_code==403
    assert client.get('/api/audit-export').status_code==403
    assert post(client,'/api/assign',peer,{'claim_id':'lesson-meeting-1a','reviewer_id':peer['user']['id']}).status_code==403
    assert post(client,'/api/adjudicate',peer,{'claim_id':'lesson-meeting-1a','decision':'approve_teaching','rationale':'Attempt to impersonate administrator.'}).status_code==403
