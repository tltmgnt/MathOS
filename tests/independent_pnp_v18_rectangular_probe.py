"""Archived regression for rectangular symmetry reduction, not a new holdout."""
import json,sys,copy,random
from collections import Counter
from itertools import combinations, product, permutations
from mathos.research.pnp_hall_rectangular_embedding import solve
from mathos.research.pnp_hall_witness_memory import admit
from independent_pnp_v18_auto_embedding_audit import auto


def probe(report):
    counts=Counter();by_size={};rows=[];negative=[]
    for row in report['rows']:
        n,f,rec=row['n'],row['clauses'],row['record']
        a=solve(n,f,rec);auto(n,f,rec,a)
        h=str(row['h']);c=by_size.setdefault(h,Counter())
        for label,r in [('old',row['auto']),('rectangular',a)]:
            for d in (counts,c):d[label+'_'+r['decision']]+=1;d[label+'_work']+=r['work_steps']
        if a['decision']=='unsat' and row['auto']['decision']=='unknown':counts['recovered']+=1
        if a['decision']=='unknown' and row['auto']['decision']=='unsat':counts['regressed']+=1
        rows.append({'n':n,'clauses':f,'record':rec,'auto':a,'old':row['auto'],'h':row['h']})
    for row in report['negative']:
        n,f,rec=row['n'],row['clauses'],row['record'];a=solve(n,f,rec);auto(n,f,rec,a)
        assert a['decision']=='unknown'
        counts['negative_'+a['status']]+=1;counts['negative_work']+=a['work_steps'];counts['old_negative_work']+=row['auto']['work_steps']
        negative.append(dict(row,auto=a))
    row=report['counterexample'];n,f,rec=row['n'],row['clauses'],row['record'];a=solve(n,f,rec);auto(n,f,rec,a)
    assert a['decision']=='unsat'
    w=a['work_steps'];counterexample=dict(row,auto=a)
    for q in (1,w-1,w):
        t=solve(n,f,rec,steps=q);assert t['decision']==('unsat' if q==w else 'unknown');counts['boundary_checks']+=1
    c={'decision':'unsat','groups':[[1,2],[3],[4]],'buckets':[[1,3],[2,4]]}
    f2=[[1,2],[3],[4],[-1,-3],[-2,-4]]
    rec2=admit(4,f2,c);assert solve(4,f2,rec2)['status']=='nonrectangular';counts['nonrectangular_controls']+=1
    rng=random.Random(188091);extra=[]
    for i in range(60):
        row=report['rows'][i];n,f,rec=row['n'],row['clauses'],row['record']
        g=copy.deepcopy(f)
        for j in range(8):
            x,y=rng.sample(range(1,n+1),2);g.append([x if rng.randrange(2) else -x,y if rng.randrange(2) else -y])
        a2=solve(n,g,rec);auto(n,g,rec,a2);counts['extra_conflicts_'+a2['decision']]+=1
        extra.append({'n':n,'clauses':g,'record':rec,'auto':a2})
    # Independent exact-embedding oracle for a 3-by-2 rectangular guard.
    small=[[1,2],[3,4],[5,6],[-1,-3],[-1,-5],[-3,-5],[-2,-4],[-2,-6],[-4,-6]]
    sc={'decision':'unsat','groups':small[:3],'buckets':[[1,3,5],[2,4,6]]}
    sr=admit(6,small,sc);small_rows=[]
    def exact(f):
        known={frozenset(c) for c in f if len(set(c))==2 and not any(-x in c for x in c)}
        for qs in combinations(known,3):
            if len({abs(x) for q in qs for x in q})!=6:continue
            for a in product(*(list(permutations(q)) for q in qs)):
                if all(frozenset((-x,-y)) in known for col in zip(*a) for x,y in combinations(col,2)):
                    return True
        return False
    for i in range(300):
        f=copy.deepcopy(small) if i%3!=0 else []
        for _ in range(rng.randrange(1,6)):
            if f and rng.randrange(2):f.pop(rng.randrange(len(f)))
            else:
                x,y=rng.sample(range(1,7),2);f.append([x if rng.randrange(2) else -x,y if rng.randrange(2) else -y])
        p=list(range(1,7));rng.shuffle(p);p=[x if rng.randrange(2) else -x for x in p]
        # A signed permutation maps -x to the negation of the image of x.
        # Multiplying by -x instead would manufacture out-of-range variables.
        assert sorted(map(abs,p))==list(range(1,7))
        f=[[p[abs(x)-1]*(1 if x>0 else -1) for x in q] for q in f]
        assert all(0<abs(x)<=6 for q in f for x in q)
        ref=exact(f);a=solve(6,f,sr);auto(6,f,sr,a)
        assert a['status']!='resource_exhausted' and (a['decision']=='unsat')==ref
        counts['exact_oracle_'+str(ref).lower()]+=1
        small_rows.append({'n':6,'clauses':f,'record':sr,'auto':a,'reference_embedding':ref})
    return {'counts':dict(counts),'by_size':{k:dict(v) for k,v in by_size.items()},'counterexample':counterexample,'counterexample_work':w,'rows':rows,'negative':negative,'extra':extra,'small':small_rows,'scope':'archived regression; one preselected rectangular record; no library selection'}

if __name__=='__main__':print(json.dumps(probe(json.load(open(sys.argv[1]))),sort_keys=True))
