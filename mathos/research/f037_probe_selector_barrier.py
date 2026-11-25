"""A scalable adversary for bounded binary lookahead plus majority.
Probe returns REJECT, MODEL, or OPEN, never calls OPEN a proof.
"""
from itertools import product
from mathos.research.f037_guarded_choice import guarded
from mathos.research.f037_log_backdoor import normalize, restrict, satisfies


def propagate(f):
    while True:
        if () in f:
            return "REJECT", f
        if not f:
            return "MODEL", f
        u=next((c[0] for c in f if len(c)==1),None)
        if u is None:
            return "OPEN", f
        f=restrict(f,{abs(u):u>0})


def probe(f,d,reverse=False):
    state,f=propagate(f)
    if state!="OPEN" or d==0:
        return state,1
    vs={abs(l) for c in f for l in c}
    v=max(vs) if reverse else min(vs)
    a,na=probe(restrict(f,{v:False}),d-1,reverse)
    b,nb=probe(restrict(f,{v:True}),d-1,reverse)
    state="MODEL" if "MODEL" in (a,b) else "REJECT" if a==b=="REJECT" else "OPEN"
    return state,1+na+nb


def choose(f,v,d,reverse=False):
    a,na=probe(restrict(f,{v:False}),d,reverse)
    b,nb=probe(restrict(f,{v:True}),d,reverse)
    if a=="MODEL" and b!="MODEL":
        return False,(a,b),na+nb
    if b=="MODEL" and a!="MODEL":
        return True,(a,b),na+nb
    if a=="REJECT" and b!="REJECT":
        return True,(a,b),na+nb
    if b=="REJECT" and a!="REJECT":
        return False,(a,b),na+nb
    return sum(v in c for c in f)>=sum(-v in c for c in f),(a,b),na+nb


def adversary(d,good):
    k=d+3
    f,tags,w=guarded(k,good)
    g=1 if good else -1
    # In the wrong branch these bias clauses vanish. In the good
    # branch they are units, so they do not conceal a contradiction.
    # A separate disjoint equality chain prevents the bounded
    # probe from finding a complete model in the good branch.
    first=max(tags)+1
    bias=sum(g in c for c in f)+1
    pad=tuple((-g,first+i) for i in range(bias))
    w.update({first+i:True for i in range(bias)})
    # d+1 disjoint positive binary clauses, on fresh variables,
    # gated to be active ONLY in the correct branch. Each needs
    # a branch or a unit from that branch to be removed.
    first+=bias
    open_good=[]
    for i in range(d+1):
        a,b=first+2*i,first+2*i+1
        open_good.append((-g,a,b))
        w[a]=w[b]=True
    f=normalize(f+pad+tuple(open_good))
    assert satisfies(f,w)
    return f,w,k


def audit():
    total=0
    for d in range(5):
        for good in (False,True):
            f,w,k=adversary(d,good)
            state,_=propagate(f)
            assert state=="OPEN"
            for reverse in (False,True):
                b,flags,nodes=choose(f,1,d,reverse)
                assert flags==("OPEN","OPEN"),(d,good,reverse,flags)
                assert b!=good
                total+=nodes
            # Given a checked satisfying witness, the failure is
            # a choice of the impossible guard value. The original
            # prefix-OR pigeonhole proof establishes impossibility;
            # no numeric solver is trusted.
            print(f"depth={d} capacity={k} good={good} variables={len(w)} clauses={len(f)}")
    # Complete probe on a tiny unit contradiction and a model.
    assert probe(((1,),(-1,)),0)[0]=="REJECT"
    assert probe(((1,),),0)[0]=="MODEL"
    assert probe(((1,2),),0)[0]=="OPEN"
    print(f"probe_nodes={total}")
    print("F037_PROBE_SELECTOR_BARRIER_OK depths=0..4 polarities=2 orders=2 controls=3")


if __name__=="__main__":
    audit()
