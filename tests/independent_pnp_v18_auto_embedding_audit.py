"""Standard-library-only replay of exported individual evidence; no search imports."""
import json,sys
from collections import Counter
from itertools import combinations


def witness(n,f,c):
    known={frozenset(q) for q in f}; gs,bs=c['groups'],c['buckets']
    flat=[x for g in gs for x in g]; prem={frozenset(g) for g in gs}
    assert c['decision']=='unsat' and gs and all(gs) and all(bs)
    assert all(type(x) is int and 0<abs(x)<=n for x in flat)
    assert len({abs(x) for x in flat})==len(flat)
    assert len(bs)<len(gs) and sorted(x for b in bs for x in b)==sorted(flat)
    prem.update(frozenset((-x,-y)) for b in bs for x,y in combinations(b,2))
    assert prem<=known
    return prem


def auto(n,f,rec,r):
    k=rec['n'];c=rec['certificate'];prem=witness(k,rec['guards'],c)
    assert prem=={frozenset(g) for g in rec['guards']}
    assert type(r['work_steps']) is int and 0<=r['work_steps']<=25000
    if r['decision']=='unknown':
        assert r['embedding'] is None and r['certificate'] is None
        assert r['status'] in ('not_found','support_limit','resource_exhausted')
        if r['status']=='resource_exhausted':assert r['work_steps']==25000
        return
    assert r['decision']=='unsat' and r['status']=='verified'
    e=r['embedding'];assert len(e)==k and len({abs(x) for x in e})==k
    assert all(type(x) is int and 0<abs(x)<=n for x in e)
    def mapped(x):return e[abs(x)-1]*(1 if x>0 else -1)
    target={'decision':'unsat', **{key:[[mapped(x) for x in g] for g in c[key]] for key in ('groups','buckets')}}
    assert target==r['certificate'];witness(n,f,target)


def audit(report):
    counts=Counter();control=Counter();positive=0
    assert len(report['rows'])==120 and len(report['negative'])==60
    for row in report['rows']:
        n,f,rec=row['n'],row['clauses'],row['record'];auto(n,f,rec,row['auto'])
        for key in ('auto','cold','supplied'):
            r=row[key];d=r['decision'];assert d in ('unsat','unknown')
            assert type(r['work_steps']) is int and 0<=r['work_steps']<=25000
            counts[key+'_'+d]+=1;counts[key+'_work']+=r['work_steps']
            if d=='unsat':witness(n,f,r['certificate']);positive+=1
            else:assert r['certificate'] is None
        assert row['supplied']['decision']=='unsat'
        if row['auto']['decision']=='unsat' and row['cold']['decision']=='unknown':counts['auto_only']+=1
        if row['auto']['decision']=='unknown' and row['cold']['decision']=='unsat':counts['cold_only']+=1
    assert dict(counts)==report['counts']
    for row in report['negative']:
        n,f,m=row['n'],row['clauses'],row['model'];assert len(m)==n and all(type(x) is bool for x in m)
        assert all(any(m[abs(x)-1]==(x>0) for x in q) for q in f)
        r=row['auto'];auto(n,f,row['record'],r);assert r['decision']=='unknown';control['sat_'+r['status']]+=1
    assert all(report['controls'][k]==v for k,v in control.items())
    row=report['counterexample'];auto(row['n'],row['clauses'],row['record'],row['auto'])
    assert row['auto']['decision']=='unsat' and row['cold']['decision']=='unknown'
    return {'comparison_rows':120,'comparison_reports':360,'positive_certificates_replayed':positive,
            'sat_models_replayed':60,'counterexample_replayed':1,'counts':dict(counts),'negative_controls':dict(control),
            'scope':'mathematical replay and report arithmetic, not runtime/search authentication'}


if __name__=='__main__':print(json.dumps(audit(json.load(open(sys.argv[1]))),sort_keys=True,indent=2))
