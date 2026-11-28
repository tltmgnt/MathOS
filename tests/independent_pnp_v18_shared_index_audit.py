"""Independent replay of shared-index results and paired budget arithmetic."""
import json,sys
from collections import Counter
from independent_pnp_v18_auto_embedding_audit import witness,auto
from independent_pnp_v18_library_audit import audit as prior_audit


def audit(report,prior,rectangular):
    pa=prior_audit(prior,rectangular)
    assert report['library']==prior['library'] and len(report['rows'])==len(prior['rows'])==290
    lib=report['library'];counts=Counter();strata={};positive=0;models=0
    for row,old in zip(report['rows'],prior['rows']):
        assert {k:v for k,v in row.items() if k!='shared'}==old
        n,f=row['n'],row['clauses'];r=row['shared'];d=r['decision'];w=r['work_steps']
        assert type(w) is int and 0<=w<=25000 and d in ('unsat','unknown') and r['indexed'] is True
        if d=='unsat':assert row['reference']=='unsat';witness(n,f,r['certificate']);positive+=1
        else:assert r['certificate'] is None
        if row['reference']=='sat':
            m=row['model'];assert len(m)==n and all(type(x) is bool for x in m)
            assert all(any(m[abs(x)-1]==(x>0) for x in q) for q in f);models+=1
        used=r['selection_work'];assert type(used) is int and 0<=used<=20000
        ids=r['candidates'];assert len(set(ids))==len(ids) and all(type(i) is int and 0<=i<len(lib) for i in ids)
        assert ids==old['indexed']['candidates']
        a=r['attempts'];assert len(a)<=4 and [x['record'] for x in a]==ids[:len(a)]
        verdict='unknown';cert=None
        for x in a:
            q=x['quota'];t=x['report'];assert verdict=='unknown' and q==20000-used and q>0
            assert type(t['work_steps']) is int and 0<=t['work_steps']<=q
            if t['status']=='resource_exhausted':assert t['work_steps']==q
            if t['decision']=='unsat':auto(n,f,lib[x['record']],t);verdict='unsat';cert=t['certificate']
            else:assert t['decision']=='unknown' and t['certificate'] is None and t['embedding'] is None
            used+=t['work_steps']
        fb=r['fallback']
        if fb is not None:
            assert verdict=='unknown' and 0<=fb['work_steps']<=25000-used
            used+=fb['work_steps'];verdict=fb['decision'];cert=fb['certificate']
            if verdict=='unsat':witness(n,f,cert)
            else:assert verdict=='unknown' and cert is None
        assert (used,verdict,cert)==(w,d,r['certificate'])
        for c in (counts,strata.setdefault(row['kind'],Counter())):
            for key,t in [('old',old['indexed']),('shared',r)]:
                c[key+'_'+t['decision']]+=1;c[key+'_work']+=t['work_steps'];c[key+'_selection']+=t['selection_work']
            if d=='unsat' and old['indexed']['decision']=='unknown':c['recovered']+=1
            if d=='unknown' and old['indexed']['decision']=='unsat':c['regressed']+=1
    assert dict(counts)==report['counts'] and {k:dict(v) for k,v in strata.items()}==report['strata']
    assert models==100
    return {'rows':290,'paired_reports':580,'new_positive_certificates':positive,'prior_positive_certificates':pa['positive_certificates'],
            'sat_models':models,'counts':dict(counts),'strata':report['strata'],'scope':'certificate replay and budget arithmetic, not timing or search authentication'}


if __name__=='__main__':print(json.dumps(audit(*(json.load(open(x)) for x in sys.argv[1:])),sort_keys=True,indent=2))
