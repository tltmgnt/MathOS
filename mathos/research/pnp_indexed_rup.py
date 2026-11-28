"""Independent persistent watched-literal RUP checker and stage-cost ablation.

Only a proved addition enters the index. All assignments are reset per
query; watch positions may survive because unassignment relaxes clauses.
No implication graph or search state is imported from the proposer.
"""
from collections import defaultdict
from .pnp_structural_kernel import Budget, Exhausted, validate
from .pnp_proof_abstraction import _original_clauses
from .pnp_proof_library import MAX_ADDITIONS
from . import pnp_conflict_learning as cdcl
from .pnp_hall_certificate import verify as verify_model


class Index:
    def __init__(self,n,known,b):
        self.n=n
        self.db=[]
        self.pos=[]
        self.watch=defaultdict(list)
        self.units=[]
        self.empty=False
        self.literals=0
        for c in known:
            self.add(c,b)

    def add(self,c,b):
        b.tick(1+len(c))
        i=len(self.db)
        self.db.append(c)
        self.pos.append([0,1] if len(c)>=2 else [0,0])
        if not c:
            self.empty=True
        elif len(c)==1:
            self.units.append(c[0])
        else:
            self.watch[c[0]].append(i)
            self.watch[c[1]].append(i)
        self.literals+=len(c)
        b.cells(3*len(self.db)+self.literals+2*(self.n+1))

    def rup(self,c,b):
        b.tick(1+len(c))
        if self.empty:
            return True
        value=[0]*(self.n+1)
        queue=[]
        def val(x):
            return value[abs(x)] if x>0 else -value[abs(x)]
        def enqueue(x):
            b.tick()
            if val(x):
                return val(x)==1
            value[abs(x)]=1 if x>0 else -1
            queue.append(x)
            return True
        for x in c:
            if not enqueue(-x):
                return True
        for x in self.units:
            if not enqueue(x):
                return True
        head=0
        while head<len(queue):
            false=-queue[head]
            head+=1
            b.tick()
            entries=self.watch[false]
            k=0
            while k<len(entries):
                b.tick()
                i=entries[k]
                a,w=self.db[i],self.pos[i]
                side=0 if a[w[0]]==false else 1
                other=a[w[1-side]]
                if val(other)==1:
                    k+=1
                    continue
                replacement=None
                for j,x in enumerate(a):
                    b.tick()
                    if j not in w and val(x)!=-1:
                        replacement=j
                        break
                if replacement is not None:
                    w[side]=replacement
                    entries[k]=entries[-1]
                    entries.pop()
                    self.watch[a[replacement]].append(i)
                    continue
                if val(other)==-1 or not enqueue(other):
                    return True
                k+=1
        return False


def verify(n,f,p,b):
    if p["decision"]=="sat":
        return verify_model(n,f,p,b)
    if p["decision"]!="unsat":
        raise ValueError("unknown is not proof")
    additions=validate(n,p["certificate"])
    if not additions or additions[-1]!=():
        raise ValueError("missing final empty addition")
    if len(additions)>MAX_ADDITIONS:
        raise Exhausted("certificate addition cap")
    index=Index(n,sorted(_original_clauses(n,f)),b)
    for c in additions:
        if c!=tuple(sorted(set(c))) or any(-x in c for x in c):
            raise ValueError("noncanonical or tautological addition")
        if not index.rup(c,b):
            raise ValueError("addition is not RUP")
        index.add(c,b)
    return True


def attempt(n,f,total,seconds,*,proposer=cdcl.propose):
    b=Budget(seconds=seconds,max_steps=total,max_cells=200_000)
    p=None
    search_steps=None
    stage="search"
    try:
        p=proposer(n,f,b)
        search_steps=b.steps
        stage="replay"
        verify(n,f,p,b)
        stage="replayed"
    except Exhausted:
        p=None
    return {"decision":p["decision"] if p else "unknown","proof":p,
            "status":stage if p else stage+"_exhausted","work_steps":b.steps,
            "search_steps":b.steps if search_steps is None else search_steps,
            "replay_steps":0 if search_steps is None else b.steps-search_steps}


def replay(n,f,r,total):
    w,s,v=r["work_steps"],r["search_steps"],r["replay_steps"]
    if (any(type(x) is not int or x<0 for x in (w,s,v))
            or w>total or s+v!=w):
        raise ValueError("invalid phase work")
    if r["status"]=="replayed":
        p=r["proof"]
        if p is None or p["decision"]!=r["decision"]:
            raise ValueError("missing proof")
        verify(n,f,p,Budget(seconds=15,max_steps=4_000_000,max_cells=200_000))
        # Deliberate independent cross-check of every credited result
        # against the frozen full-scan checker, outside decision budget.
        cdcl.verify(n,f,p,Budget(seconds=15,max_steps=4_000_000,max_cells=200_000))
    elif (r["status"] not in ("search_exhausted","replay_exhausted")
          or r["proof"] is not None or r["decision"]!="unknown"
          or (r["status"]=="search_exhausted" and v!=0)):
        raise ValueError("invalid unknown")
    return True


def profile(n,f,total=100_000,seconds=5,*,proposer=cdcl.propose):
    """Diagnostic only: search then both independent checkers with
    separate audit budgets. Does not credit a combined-budget decision.
    """
    b=Budget(seconds=seconds,max_steps=total,max_cells=200_000)
    try:
        p=proposer(n,f,b)
    except Exhausted:
        return {"proof":None,"search_steps":b.steps,"slow_steps":None,"fast_steps":None}
    out={"proof":p,"search_steps":b.steps}
    for name,checker in (("slow_steps",cdcl.verify),("fast_steps",verify)):
        q=Budget(seconds=15,max_steps=4_000_000,max_cells=200_000)
        try:
            checker(n,f,p,q)
        except Exhausted:
            out[name]=None
        else:
            out[name]=q.steps
    return out


def audit_profile(n,f,r,total):
    if type(r["search_steps"]) is not int or not 0<=r["search_steps"]<=total:
        raise ValueError("invalid diagnostic search work")
    if r["proof"] is None:
        if r["slow_steps"] is not None or r["fast_steps"] is not None:
            raise ValueError("invalid absent proof")
        return True
    for name,checker in (("slow_steps",cdcl.verify),("fast_steps",verify)):
        w=r[name]
        if w is not None and (type(w) is not int or not 0<=w<=4_000_000):
            raise ValueError("invalid diagnostic replay work")
        q=Budget(seconds=15,max_steps=4_000_000,max_cells=200_000)
        try:
            checker(n,f,r["proof"],q)
        except Exhausted:
            if w is not None:
                raise
        else:
            if w is not None and q.steps!=w:
                raise ValueError("diagnostic work mismatch")
    return True
