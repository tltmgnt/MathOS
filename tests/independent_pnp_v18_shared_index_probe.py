"""Paired archived regression: no retuning of the 80% retrieval allowance."""
import copy,json,sys
from collections import Counter
from mathos.research.pnp_hall_shared_index import solve


def probe(prior):
    counts=Counter();strata={};rows=[];lib=prior['library']
    for row in prior['rows']:
        n,f=row['n'],row['clauses'];a=solve(n,f,lib)
        rows.append(dict(row,shared=a))
        for c in (counts,strata.setdefault(row['kind'],Counter())):
            for key,r in [('old',row['indexed']),('shared',a)]:
                c[key+'_'+r['decision']]+=1;c[key+'_work']+=r['work_steps'];c[key+'_selection']+=r['selection_work']
            if a['decision']=='unsat' and row['indexed']['decision']=='unknown':c['recovered']+=1
            if a['decision']=='unknown' and row['indexed']['decision']=='unsat':c['regressed']+=1
        assert a['decision']!='unsat' or row['reference']=='unsat'
    row=prior['rows'][0];n,f=row['n'],row['clauses']
    a=solve(n,f,lib);assert a['decision']=='unsat' and a['fallback'] is None
    w=a['work_steps'];threshold=(5*w+3)//4
    for q in (5,threshold-1,threshold):
        t=solve(n,f,lib,steps=q);assert t['work_steps']<=q
        retrieval=any(x['report']['decision']=='unsat' for x in t['attempts'])
        assert retrieval==(q==threshold)
    bad=copy.deepcopy(lib);i=a['attempts'][-1]['record'];bad[i]['guards'].pop()
    try:solve(n,f,bad)
    except ValueError:pass
    else:raise AssertionError('selected corrupt record accepted')
    return {'library':lib,'rows':rows,'counts':dict(counts),'strata':{k:dict(v) for k,v in strata.items()},
            'controls':{'boundary_checks':3,'corrupt_record_rejected':1,'first_positive_retrieval_threshold':threshold},
            'scope':'archived development regression; same 25k work and 80% retrieval cap; no blind generalization'}


if __name__=='__main__':print(json.dumps(probe(json.load(open(sys.argv[1]))),sort_keys=True))
