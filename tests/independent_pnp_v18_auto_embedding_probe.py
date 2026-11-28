"""Automatic vs supplied mapping vs cold, related synthetic development only."""
import json, random, copy
from collections import Counter
from mathos.research.pnp_signed_hall_subsystem import solve as cold
from mathos.research.pnp_hall_witness_memory import admit, transfer
from mathos.research.pnp_hall_embedding_search import solve, replay
from independent_pnp_v18_hall_memory_probe import base,mapped,independent,sat


def probe():
    rng=random.Random(187102);rows=[];negative=[];tot=Counter(); controls=Counter()
    for h in range(3,9):
        n,f=base(h,rng);record=admit(n,f,cold(n,f)['certificate'])
        for i in range(20):
            m=n+3;p=list(range(1,m+1));rng.shuffle(p)
            p=[x if rng.randrange(2) else -x for x in p[:n]]
            g=mapped(f,p)
            for _ in range(3):
                g.append([x if rng.randrange(2) else -x for x in rng.sample(range(1,m+1),rng.randint(1,4))])
            rng.shuffle(g)
            e=[p[v-1] for v in record['source_embedding']]
            a=solve(m,g,record);replay(m,g,record,a)
            c=cold(m,g);t=transfer(m,g,record,e)
            assert t['decision']=='unsat'
            for label,r in [('auto',a),('cold',c),('supplied',t)]:
                tot[label+'_'+r['decision']]+=1;tot[label+'_work']+=r['work_steps']
                if r['certificate']:independent(m,g,r['certificate'])
            if a['decision']=='unsat' and c['decision']=='unknown':tot['auto_only']+=1
            if a['decision']=='unknown' and c['decision']=='unsat':tot['cold_only']+=1
            rows.append({'h':h,'n':m,'clauses':g,'record':record,'auto':a,'cold':c,'supplied':t})
        # Verify a concrete SAT model after each selected guard deletion.
        guard=record['guards'];k=record['n'];cert=record['certificate'];gs=cert['groups'];bs=cert['buckets']
        owner={x:i for i,g in enumerate(gs) for x in g};bucket={x:j for j,b in enumerate(bs) for x in b}
        for idx in rng.sample(range(len(guard)),min(10,len(guard))):
            missing=guard[idx];g=guard[:idx]+guard[idx+1:];chosen=[]
            if frozenset(missing) in {frozenset(q) for q in gs}:
                skipped=owner[missing[0]];pairs=zip([i for i in range(len(gs)) if i!=skipped],range(len(bs)))
            else:
                x,y=(-missing[0],-missing[1]);chosen=[x,y]
                pairs=zip([i for i in range(len(gs)) if i not in (owner[x],owner[y])],[j for j in range(len(bs)) if j!=bucket[x]])
            for i,j in pairs:chosen.append(next(x for x in gs[i] if bucket[x]==j))
            assignment={abs(x):(x>0)==(x in chosen) for q in gs for x in q}
            assert all(any(assignment[abs(x)]==(x>0) for x in q) for q in g)
            if h==3:assert sat(k,g)
            p=list(range(1,k+1));rng.shuffle(p);p=[x if rng.randrange(2) else -x for x in p]
            g=mapped(g,p);r=solve(k,g,record);replay(k,g,record,r)
            assert r['decision']=='unknown';controls['sat_'+r['status']]+=1
            model=[False]*k
            for v,y in enumerate(p,1):model[abs(y)-1]=assignment[v]==(y>0)
            negative.append({'n':k,'clauses':g,'model':model,'record':record,'auto':r})
    n,f=base(3,rng);record=admit(n,f,cold(n,f)['certificate']);r=solve(n,f,record);q=r['work_steps'];assert r['decision']=='unsat'
    for budget in (1,q-1,q):
        a=solve(n,f,record,steps=budget);assert a['decision']==('unsat' if budget==q else 'unknown');replay(n,f,record,a,steps=budget);controls['boundary']+=1
    bad=copy.deepcopy(record);bad['guards'].pop()
    for rec,x in [(bad,r),(record,dict(r,embedding=[1]*record['n'])),(record,dict(r,certificate=None)),(record,dict(r,work_steps=1))]:
        try:replay(n,f,rec,x)
        except (ValueError,RuntimeError):controls['tamper_rejected']+=1
        else:raise AssertionError('tamper accepted')
    f=[[9,-7,-11],[-4,1,6,7],[5,-8],[-9,5],[-2,-8],[-2,-9],[10,4,2],
       [12,-1],[11,-4],[-12,8,3],[12,7],[1,9,-4,7],[5,-2],[-4,-3],
       [-8,-9],[7,-10],[-5,-6,1],[7,-8,9,3],[1],[-10,12],[6,-4],
       [10,6,-8,11],[-1,7],[6,11],[11,-3],[-1,-10],[6,-3]]
    c=cold(12,f);record=admit(12,f,c['certificate']);g=f+[[11,12]]
    a=solve(12,g,record);replay(12,g,record,a);miss=cold(12,g)
    assert a['decision']=='unsat' and miss['decision']=='unknown'
    independent(12,g,a['certificate'])
    counterexample={'n':12,'clauses':g,'record':record,'auto':a,'cold':miss}
    return {'counts':dict(tot),'controls':dict(controls),'boundary':q,'rows':rows,'negative':negative,'counterexample':counterexample,
            'scope':'one preselected source record; no target correspondence given to automatic search; related synthetic development'}


if __name__=='__main__':print(json.dumps(probe(),sort_keys=True))
