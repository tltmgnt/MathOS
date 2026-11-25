"""Encode existence of a satisfiable input defeating a fixed selector.
MILP only proposes witnesses; all returned counterexamples are checked.
"""
from itertools import combinations, product
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix
import numpy as np


def vocabulary(n):
    return tuple(tuple(v*s for v,s in zip(scope,signs))
                 for k in range(1,min(3,n)+1)
                 for scope in combinations(range(1,n+1),k)
                 for signs in product((-1,1),repeat=k))


def holds(c,x):
    return any(x[abs(l)]==(l>0) for l in c)


def run_policy(f,n):
    rows=list(f)
    x={}
    for v in range(1,n+1):
        p=sum(v in c for c in rows)
        q=sum(-v in c for c in rows)
        b=(v,) in rows or ((-v,) not in rows and p>=q)
        x[v]=b
        rows=[tuple(l for l in c if abs(l)!=v) for c in rows
              if (v if b else -v) not in c]
    return x


class Circuit:
    def __init__(self):
        self.n=0
        self.rows=[]
        self.gates=[]
        self.one=self.new()
        self.rows.append((self.one,))

    def new(self):
        self.n+=1
        return self.n

    def AND(self,*ls):
        if not ls:
            return self.one
        if len(ls)==1:
            return ls[0]
        v=self.new()
        self.rows.extend((-v,l) for l in ls)
        self.rows.append((v,*(-l for l in ls)))
        self.gates.append((v,ls))
        return v

    def OR(self,*ls):
        return -self.AND(*(-l for l in ls))

    def threshold(self,ls,k):
        if k<=0:
            return self.one
        dp=[self.one]+[-self.one]*k
        for l in ls:
            dp=[self.one]+[self.OR(dp[j],self.AND(l,dp[j-1]))
                           for j in range(1,k+1)]
        return dp[k]

    def eval(self,x):
        y={**x,self.one:True}
        def val(l):
            return y[abs(l)]==(l>0)
        for v,ls in self.gates:
            y[v]=all(val(l) for l in ls)
        return y


def encode(n,cs):
    c=Circuit()
    flags=[c.new() for _ in cs]
    witness={v:c.new() for v in range(1,n+1)}
    for flag,row in zip(flags,cs):
        c.rows.append((-flag,*(witness[abs(l)] if l>0 else -witness[-l] for l in row)))
    active=flags[:]
    chosen={}
    for v in range(1,n+1):
        p=[a for a,r in zip(active,cs) if v in r]
        q=[a for a,r in zip(active,cs) if -v in r]
        up=c.OR(*(a for a,r in zip(active,cs) if v in r and max(map(abs,r))==v))
        un=c.OR(*(a for a,r in zip(active,cs) if -v in r and max(map(abs,r))==v))
        major=c.threshold(p+[-a for a in q],len(q))
        b=c.OR(up,c.AND(-un,major))
        chosen[v]=b
        active=[c.AND(a,-b) if v in r else c.AND(a,b) if -v in r else a
                for a,r in zip(active,cs)]
    c.rows.append((c.OR(*active),))
    return c,flags,witness,chosen


def value(x,l):
    return x[abs(l)]==(l>0)


def propose(c):
    ii,jj,aa,lb=[],[],[],[]
    for i,row in enumerate(c.rows):
        lb.append(1-sum(l<0 for l in row))
        for l in row:
            ii.append(i); jj.append(abs(l)-1); aa.append(1 if l>0 else -1)
    mat=coo_matrix((aa,(ii,jj)),shape=(len(c.rows),c.n)).tocsc()
    r=milp(np.zeros(c.n),integrality=np.ones(c.n),bounds=Bounds(0,1),
           constraints=LinearConstraint(mat,lb,np.inf),options={'time_limit':20})
    if r.x is None:
        return None
    x={v+1:bool(a>.5) for v,a in enumerate(r.x)}
    return x if all(holds(row,x) for row in c.rows) else None


def audit():
    n=2; cs=vocabulary(n)
    c,flags,witness,chosen=encode(n,cs)
    checked=0
    for mask in range(1<<len(cs)):
        f=tuple(row for j,row in enumerate(cs) if mask&(1<<j))
        run=run_policy(f,n)
        for bits in product((False,True),repeat=n):
            w=dict(zip(range(1,n+1),bits))
            x=c.eval({**{v:bool(mask&(1<<j)) for j,v in enumerate(flags)},
                      **{witness[v]:w[v] for v in w}})
            assert {v:value(x,l) for v,l in chosen.items()}==run
            assert all(holds(row,x) for row in c.rows)==(
                all(holds(row,w) for row in f) and not all(holds(row,run) for row in f))
            checked+=1
    n=3;cs=vocabulary(n)
    c,flags,witness,chosen=encode(n,cs)
    x=propose(c)
    assert x is not None, 'no checked counterexample returned by candidate solver'
    f=tuple(row for v,row in zip(flags,cs) if x[v])
    w={v:x[a] for v,a in witness.items()}
    run=run_policy(f,n)
    assert all(holds(row,w) for row in f) and not all(holds(row,run) for row in f)
    assert run=={v:value(x,l) for v,l in chosen.items()}
    while True:
        for i in range(len(f)):
            g=f[:i]+f[i+1:]
            if not all(holds(row,run_policy(g,n)) for row in g):
                f=g;break
        else:
            break
    assert all(holds(row,w) for row in f) and not all(holds(row,run_policy(f,n)) for row in f)
    print(f'counterexample={f} witness={w} candidate={run_policy(f,n)} gate_vars={c.n} gate_clauses={len(c.rows)}')
    assert checked==1024
    print('F037_ADVERSARIAL_SELECTOR_OK bounded_pairs=1024 variables=3 vocabulary=26 witness=1')


if __name__=='__main__':
    audit()
