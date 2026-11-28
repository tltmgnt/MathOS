import json,random,sys
from collections import Counter
from itertools import combinations
from mathos.research.pnp_hall_library_router import solve
from mathos.research.pnp_signed_hall_subsystem import solve as cold
from mathos.research.pnp_hall_witness_memory import admit
from independent_pnp_v18_auto_embedding_audit import witness

def record(h):
    gs=[[i*h+j+1 for j in range(h)] for i in range(h+1)]
    bs=[list(x) for x in zip(*gs)];f=gs+[[-x,-y] for b in bs for x,y in combinations(b,2)]
    return admit(h*(h+1),f,{'decision':'unsat','groups':gs,'buckets':bs})

def probe(prior):
    rng=random.Random(189321);lib=[record(h) for h in (9,7,4,10,2,8,5,3,6)]
    rows=[];counts=Counter();strata={}
    def one(n,f,kind,ref,model=None):
        a=solve(n,f,lib);b=solve(n,f,lib,indexed=False);c=cold(n,f)
        row={'n':n,'clauses':f,'kind':kind,'reference':ref,'model':model,'indexed':a,'scan':b,'cold':c}
        for name,r in [('indexed',a),('scan',b),('cold',c)]:
            assert r['decision'] in ('unsat','unknown') and 0<=r['work_steps']<=25000
            if r['decision']=='unsat':assert ref=='unsat';witness(n,f,r['certificate'])
            for d in (counts,strata.setdefault(kind,Counter())):d[name+'_'+r['decision']]+=1;d[name+'_work']+=r['work_steps']
        rows.append(row)
    for row in prior['rows']:one(row['n'],row['clauses'],'related_unsat','unsat')
    for row in prior['negative']:one(row['n'],row['clauses'],'deletion_sat','sat',row['model'])
    # Actual multi-candidate ambiguity: attach a satisfiable width-three decoy.
    # Missing conflict restored in degree only by two auxiliary false choices.
    for row in [x for x in prior['rows'] if x['h'] in (4,5,6)][::2]:
        n=row['n'];g=[q[:] for q in row['clauses']];d=record(3)['guards'];missing=next(q for q in d if len(q)==2);d=[q for q in d if q!=missing]
        d += [[missing[0],-13],[missing[1],-14]]
        g += [[(abs(x)+n)*(1 if x>0 else -1) for x in q] for q in d]
        one(n+14,g,'ambiguous_unsat','unsat')
    # No Hall structure required: planted SAT and contradictory unit pair controls.
    for i in range(40):
        n=20+i%5;m=[bool(rng.randrange(2)) for _ in range(n)];f=[]
        for _ in range(70):
            q=[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
            if not any(m[abs(x)-1]==(x>0) for x in q):q[0]=-q[0]
            f.append(q)
        one(n,f,'nonmatching_sat','sat',m);one(n,f+[[1],[-1]],'unit_unsat','unsat')
    return {'library':lib,'counts':dict(counts),'strata':{k:dict(v) for k,v in strata.items()},'rows':rows,'scope':'archived related development and synthetic controls; no supplied record or mapping to router'}
if __name__=='__main__':print(json.dumps(probe(json.load(open(sys.argv[1]))),sort_keys=True))
