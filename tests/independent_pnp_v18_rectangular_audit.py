"""Separate mathematical replay and aggregate audit; no MathOS search imports."""
import json,sys
from collections import Counter
from itertools import combinations,product,permutations
from independent_pnp_v18_auto_embedding_audit import auto


def exact(f):
    known={frozenset(q) for q in f if len(set(q))==2 and not any(-x in q for x in q)}
    for qs in combinations(known,3):
        if len({abs(x) for q in qs for x in q})!=6:continue
        for a in product(*(tuple(permutations(q)) for q in qs)):
            if all(frozenset((-x,-y)) in known for col in zip(*a) for x,y in combinations(col,2)):
                return True
    return False


def audit(r,prior):
    counts=Counter();by_size={};positive=0
    assert len(r['rows'])==len(prior['rows'])==120
    for row,old in zip(r['rows'],prior['rows']):
        n,f,rec=row['n'],row['clauses'],row['record']
        assert (n,f,rec,row['h'],row['old'])==(old['n'],old['clauses'],old['record'],old['h'],old['auto'])
        a=row['auto'];auto(n,f,rec,a);auto(n,f,rec,row['old'])
        positive+=sum(x['decision']=='unsat' for x in (a,row['old']))
        c=by_size.setdefault(str(row['h']),Counter())
        for label,x in [('old',row['old']),('rectangular',a)]:
            for d in (counts,c):d[label+'_'+x['decision']]+=1;d[label+'_work']+=x['work_steps']
        if a['decision']=='unsat' and row['old']['decision']=='unknown':counts['recovered']+=1
        if a['decision']=='unknown' and row['old']['decision']=='unsat':counts['regressed']+=1
    assert len(r['negative'])==len(prior['negative'])==60
    for row,old in zip(r['negative'],prior['negative']):
        n,f,rec,m=row['n'],row['clauses'],row['record'],row['model']
        assert (n,f,rec,m)==(old['n'],old['clauses'],old['record'],old['model'])
        assert len(m)==n and all(type(x) is bool for x in m)
        assert all(any(m[abs(x)-1]==(x>0) for x in q) for q in f)
        a=row['auto'];auto(n,f,rec,a);assert a['decision']=='unknown'
        counts['negative_'+a['status']]+=1;counts['negative_work']+=a['work_steps'];counts['old_negative_work']+=old['auto']['work_steps']
    assert len(r['extra'])==60 and len(r['small'])==300
    for row in r['extra']:
        a=row['auto'];auto(row['n'],row['clauses'],row['record'],a);counts['extra_conflicts_'+a['decision']]+=1;positive+=a['decision']=='unsat'
    for row in r['small']:
        a=row['auto'];assert row['n']==6;auto(6,row['clauses'],row['record'],a)
        ref=exact(row['clauses']);assert ref==row['reference_embedding'] and (a['decision']=='unsat')==ref and a['status']!='resource_exhausted'
        counts['exact_oracle_'+str(ref).lower()]+=1;positive+=a['decision']=='unsat'
    row=r['counterexample'];old=prior['counterexample'];assert (row['n'],row['clauses'],row['record'])==(old['n'],old['clauses'],old['record'])
    auto(row['n'],row['clauses'],row['record'],row['auto']);assert row['auto']['decision']=='unsat' and row['auto']['work_steps']==r['counterexample_work'];positive+=1
    assert dict(counts)=={k:v for k,v in r['counts'].items() if k not in ('boundary_checks','nonrectangular_controls')}
    assert {k:dict(v) for k,v in by_size.items()}==r['by_size']
    return {'counts':dict(counts),'positive_certificates_replayed':positive,'sat_models_replayed':60,'exact_embedding_oracles':300,
            'scope':'archived and related synthetic data; mathematical replay and arithmetic only'}


if __name__=='__main__':print(json.dumps(audit(json.load(open(sys.argv[1])),json.load(open(sys.argv[2]))),sort_keys=True,indent=2))
