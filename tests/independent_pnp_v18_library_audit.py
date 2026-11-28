"""Independent replay of bounded library experiment; no solver imports."""
import json,sys
from collections import Counter
from independent_pnp_v18_auto_embedding_audit import witness,auto


def audit(report,prior):
    lib=report['library'];assert len(lib)==9
    for rec in lib:assert witness(rec['n'],rec['guards'],rec['certificate'])=={frozenset(q) for q in rec['guards']}
    counts=Counter();strata={};positive=0;models=0
    rows=report['rows'];assert len(rows)==290
    originals=prior['rows']+prior['negative']
    for row,old in zip(rows,originals):assert (row['n'],row['clauses'])==(old['n'],old['clauses'])
    amb=[x for x in prior['rows'] if x['h'] in (4,5,6)][::2]
    for row,old in zip(rows[180:210],amb):
        assert row['kind']=='ambiguous_unsat' and row['n']==old['n']+14
        assert {frozenset(q) for q in old['clauses']}<={frozenset(q) for q in row['clauses']}
        witness(row['n'],row['clauses'],old['auto']['certificate'])
    for row in rows:
        n,f=row['n'],row['clauses'];kind=row['kind'];ref=row['reference'];m=row['model']
        if ref=='sat':
            assert len(m)==n and all(type(x) is bool for x in m)
            assert all(any(m[abs(x)-1]==(x>0) for x in q) for q in f);models+=1
        else:
            assert ref=='unsat' and kind in ('related_unsat','ambiguous_unsat','unit_unsat')
            if kind=='unit_unsat':assert [1] in f and [-1] in f
        for label in ('indexed','scan','cold'):
            r=row[label];d=r['decision'];w=r['work_steps'];assert d in ('unknown','unsat') and type(w) is int and 0<=w<=25000
            if d=='unsat':assert ref=='unsat';witness(n,f,r['certificate']);positive+=1
            else:assert r['certificate'] is None
            if label!='cold':
                used=r['selection_work'];assert type(used) is int and 0<=used<=20000
                ids=r['candidates'];assert len(set(ids))==len(ids) and all(type(i) is int and 0<=i<len(lib) for i in ids)
                assert r['indexed']==(label=='indexed')
                if label=='scan':assert ids==list(range(len(lib)))
                a=r['attempts'];assert len(a)<=4 and [x['record'] for x in a]==ids[:len(a)]
                verdict='unknown';cert=None
                for x in a:
                    q=x['quota'];t=x['report'];assert verdict=='unknown' and q==20000-used and q>0
                    assert 0<=t['work_steps']<=q
                    if t['status']=='resource_exhausted':assert t['work_steps']==q
                    # prior independent checker expects exhaustion at 25000; here quota varies.
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
            for c in (counts,strata.setdefault(kind,Counter())):c[label+'_'+d]+=1;c[label+'_work']+=w
    assert dict(counts)==report['counts'] and {k:dict(v) for k,v in strata.items()}==report['strata']
    assert models==100
    return {'rows':len(rows),'arm_reports':3*len(rows),'positive_certificates':positive,'sat_models':models,'counts':dict(counts),'scope':'replay and budget arithmetic, not timing or negative-search authentication'}
if __name__=='__main__':print(json.dumps(audit(json.load(open(sys.argv[1])),json.load(open(sys.argv[2]))),indent=2,sort_keys=True))
