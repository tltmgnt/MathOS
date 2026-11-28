"""Independent verification of original premises and shared route allowances."""
import json,sys,copy
from collections import Counter
from itertools import product
from independent_pnp_v18_auto_embedding_audit import witness,auto
from independent_pnp_v18_shared_index_audit import audit as prior_audit

STEPS=25000


def model(n,f,a):
    assert isinstance(a,list) and len(a)==n and all(type(x) is bool for x in a)
    assert all(any(a[abs(x)-1]==(x>0) for x in q) for q in f)


def unit(n,f,trace):
    assert isinstance(trace,list) and 1<=len(trace)<=n+1
    values={}
    for j,i in enumerate(trace):
        assert type(i) is int and 0<=i<len(f)
        q=set(f[i]);assert not any(-x in q for x in q)
        assert not any(abs(x) in values and values[abs(x)]==(x>0) for x in q)
        free=[x for x in q if abs(x) not in values]
        if not free:
            assert j==len(trace)-1;return
        assert len(free)==1 and j<len(trace)-1
        x=free[0];values[abs(x)]=x>0
    raise AssertionError('no contradiction')


def dual(n,f,rows):
    assert isinstance(rows,list) and rows
    parity=set();rhs=0
    for row in rows:
        vs,v,ids=row['scope'],row['rhs'],row['sources']
        assert vs==sorted(set(vs)) and len(vs)<=4 and all(type(x) is int and 1<=x<=n for x in vs)
        assert type(v) is int and v in (0,1) and ids and len(set(ids))==len(ids)
        assert all(type(i) is int and 0<=i<len(f) and set(map(abs,f[i]))==set(vs) for i in ids)
        for bits in product((False,True),repeat=len(vs)):
            if sum(bits)%2==v:continue
            a=dict(zip(vs,bits));assert any(not any(a[abs(x)]==(x>0) for x in f[i]) for i in ids)
        parity.symmetric_difference_update(vs);rhs^=v
    assert not parity and rhs==1


def hall_report(n,f,lib,r,q):
    used=r['selection_work'];cap=q*4//5;assert type(used) is int and 0<=used<=cap
    ids=r['candidates'];assert r['indexed'] is True and len(set(ids))==len(ids) and all(type(i) is int and 0<=i<len(lib) for i in ids)
    a=r['attempts'];assert len(a)<=4 and [x['record'] for x in a]==ids[:len(a)]
    d='unknown';c=None
    for x in a:
        t=x['report'];z=x['quota'];assert d=='unknown' and z==cap-used and z>0 and 0<=t['work_steps']<=z
        if t['status']=='resource_exhausted':assert t['work_steps']==z
        if t['decision']=='unsat':auto(n,f,lib[x['record']],t);d='unsat';c=t['certificate']
        else:assert t['decision']=='unknown' and t['certificate'] is None and t['embedding'] is None
        used+=t['work_steps']
    fb=r['fallback']
    if fb is not None:
        assert d=='unknown' and 0<=fb['work_steps']<=q-used
        used+=fb['work_steps'];d=fb['decision'];c=fb['certificate']
        if d=='unsat':witness(n,f,c)
        else:assert d=='unknown' and c is None
    assert (used,d,c)==(r['work_steps'],r['decision'],r['certificate'])
    if d=='unsat':witness(n,f,c)


def portfolio(n,f,lib,r,use_hall):
    assert r['use_hall'] is use_hall
    routes=['quick','hall','propagation','affine'] if use_hall else ['quick','propagation','affine']
    a=r['attempts'];assert len(a)<=len(routes) and [x['route'] for x in a]==routes[:len(a)]
    used=0;d='unknown';c=None
    for x in a:
        route=x['route'];t=x['report'];left=STEPS-used
        q=min(left,STEPS//10) if route=='quick' else left//2 if route=='propagation' else left
        assert d=='unknown' and left>=5 and x['quota']==q and type(t['work_steps']) is int and 0<=t['work_steps']<=q
        d,c=t['decision'],t['certificate'];assert d in ('sat','unsat','unknown')
        if route=='hall':hall_report(n,f,lib,t,q)
        elif route=='affine':
            if d=='unknown':assert c is None and t['status'] in ('resource_exhausted','unrecognized')
            else:
                assert c['decision']==d and t['status']=='replayed'
                if d=='sat':model(n,f,c['certificate'])
                else:dual(n,f,c['certificate'])
        else:
            if d=='unknown':
                assert c is None and t['status'] in ('not_found','resource_exhausted')
                if t['status']=='resource_exhausted':assert t['work_steps']==q
            else:
                assert t['status']=='verified' and c['decision']==d
                if d=='sat':assert route=='propagation';model(n,f,c['model'])
                else:unit(n,f,c['trace'])
        used+=t['work_steps']
    assert (used,d,c)==(r['work_steps'],r['decision'],r['certificate'])


def audit(report,prior,library_report,rectangular):
    pa=prior_audit(prior,library_report,rectangular)
    assert report['library']==prior['library'] and len(report['rows'])==350
    assert report['envelope']=={'work_steps':25000,'cooperative_seconds':1.25,'process_wall_seconds':3,'address_space_bytes':512*1024*1024,'cpu_cores':1}
    lib=report['library'];counts=Counter();strata={};routes=Counter();refs=Counter();positive=Counter()
    for i,row in enumerate(report['rows']):
        n,f,ref,m=row['n'],row['clauses'],row['reference'],row['model'];kind=row['kind']
        assert type(n) is int and 0<=n<=512 and all(type(x) is int and 0<abs(x)<=n for q in f for x in q)
        if i<290:
            old=prior['rows'][i];assert row['archive_index']==i and all(row[k]==old[k] for k in ('n','clauses','kind','reference','model'))
            if ref=='unsat':
                if kind=='unit_unsat':assert [1] in f and [-1] in f
                else:witness(n,f,old['shared']['certificate'])
                refs['archived_unsat']+=1
            else:model(n,f,m);refs['explicit_sat_models']+=1
        elif kind=='random3':
            assert n<=12
            sat=any(all(any(a[abs(x)-1]==(x>0) for x in q) for q in f) for a in product((False,True),repeat=n))
            assert ref==('sat' if sat else 'unsat');refs['exhaustive_random3']+=1
        elif ref=='sat':model(n,f,m);refs['explicit_sat_models']+=1
        elif kind=='signed_horn':unit(n,f,row['reference_certificate']['trace']);refs['fresh_unit_unsat']+=1
        elif kind=='affine':dual(n,f,row['reference_certificate']['dual']);refs['fresh_affine_unsat']+=1
        else:raise AssertionError('unknown reference')
        assert set(row['arms'])=={'hall','multi','no_hall'}
        for arm,a in row['arms'].items():
            r=a['result'];d=r['decision'];w=r['work_steps'];assert d in ('unknown',ref) and type(w) is int and 0<=w<=STEPS
            if 'process_resource' in r:assert d=='unknown' and r['certificate'] is None and w==STEPS
            elif arm=='hall':hall_report(n,f,lib,r,STEPS)
            else:portfolio(n,f,lib,r,arm=='multi')
            for c in (counts,strata.setdefault(kind,Counter())):
                c[arm+'_'+d]+=1;c[arm+'_work']+=w
                if 'process_resource' in r:c[arm+'_process_resource']+=1
            if d!='unknown':
                positive[arm]+=1
                if arm!='hall':routes[arm+'_'+r['attempts'][-1]['route']+'_'+d]+=1
    assert dict(counts)==report['counts'] and {k:dict(v) for k,v in strata.items()}==report['strata'] and dict(routes)==report['routes']
    assert sum(refs.values())==350 and refs['explicit_sat_models']==118
    return {'rows':350,'arm_reports':1050,'positive_certificates':dict(positive),'references':dict(refs),'counts':dict(counts),'strata':report['strata'],'routes':dict(routes),'prior_replayed':pa['new_positive_certificates'],'scope':'independent mathematical evidence and budget arithmetic; not runtime authentication'}


def tamper_controls(report):
    lib=report['library'];count=0
    for route,d in [('quick','unsat'),('propagation','sat'),('affine','unsat'),('hall','unsat')]:
        row=next(x for x in report['rows'] if x['arms']['multi']['result']['decision']==d and x['arms']['multi']['result']['attempts'][-1]['route']==route)
        r=copy.deepcopy(row['arms']['multi']['result']);a=r['attempts'][-1]['report'];c=a['certificate']
        if route=='quick':c['trace']=[c['trace'][0]]
        elif route=='propagation':c['model']=[False]*row['n'];c['model'][0]=None
        elif route=='affine':c['certificate'][0]['rhs']^=1
        else:c['buckets'].pop()
        try:portfolio(row['n'],row['clauses'],lib,r,True)
        except (AssertionError,ValueError):count+=1
        else:raise AssertionError('invalid proof accepted')
    return count


if __name__=='__main__':
    data=[json.load(open(x)) for x in sys.argv[1:]];r=audit(*data);r['tamper_rejected']=tamper_controls(data[0]);print(json.dumps(r,sort_keys=True,indent=2))
