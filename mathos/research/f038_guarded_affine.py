"""Guarded hybrid CNF/XOR persistent learning and ResearchOS/TECT-X attempt audit."""
from mathos.research.f038_rule_certification import satisfies
from mathos.research.f038_guarded_learning import base_db,canonical,valid_assumptions,matching,mode
from mathos.research import f038_hybrid_affine as H
from mathos.research.f038_resolution_certificate import split_cube,encode
from mathos.research.f038_adaptive_rup import propagate as ordinary
from mathos.research.f038_tectx_cycle import run_attempt


PLAN='docs/research/tga-universal/f038-tectx-guarded-affine.json'


def source(f,n):
    assert all(0<abs(l)<=n for c in f for l in c)
    rows,rest=H.extract(f)
    assert H.verify_partition(f,rows,rest)
    base,N=base_db(f,n)
    guarded=tuple((a,b,tuple(n+i+1 for i in ids)) for a,b,ids in rows)
    return base,N,guarded


def active(guarded,p):
    pins=set(p)
    return tuple((a,b,()) for a,b,g in guarded if all(l in pins for l in g))


def conflict(db,N,guarded,p):
    return H.propagate(active(guarded,p),db,N,p)


def check_add(db,N,guarded,c,trace):
    if canonical(c)!=c or not valid_assumptions(c,N):
        return False
    p=tuple(-l for l in c)
    return H.verify_conflict(active(guarded,p),db,N,p,trace)


def check_step(db,N,guarded,A,result):
    try:
        additions,w,j=result
        if not valid_assumptions(A,N):
            return False
        trial=list(db)
        for c,trace in additions:
            if not check_add(trial,N,guarded,c,trace):
                return False
            trial.append(c)
        if w is None:
            if type(j) is not int or not 0<=j<len(trial) or not all(-l in A for l in trial[j]):
                return False
        elif j is not None or type(w) is not int or not 0<=w<1<<N or not (
                satisfies(trial,w) and satisfies(tuple((l,) for l in A),w)):
            return False
        db[:]=trial
        return True
    except (TypeError,ValueError,IndexError,KeyError):
        return False


class Session:
    def __init__(self,f,n):
        self.base,self.N,self.guarded=source(f,n)
        self.db=list(self.base)
        self.index={canonical(c):i for i,c in enumerate(self.base)}
        self.reused=0
        self.branches=0

    def ask(self,A):
        A=tuple(A)
        assert valid_assumptions(A,self.N)
        additions=[]
        def add(p):
            c=canonical(-l for l in p)
            if c in self.index:
                return self.index[c]
            # Recompute under the canonical negated clause, so the proof row
            # indices and pin order are exactly those the checker uses.
            state,trace=conflict(self.db,self.N,self.guarded,tuple(-l for l in c))
            assert state is None and check_add(self.db,self.N,self.guarded,c,trace)
            j=len(self.db)
            self.db.append(c)
            self.index[c]=j
            additions.append((c,trace))
            return j

        def visit(p):
            j=matching(self.db,p)
            if j is not None:
                self.reused+=1
                return None,j
            state,trace=conflict(self.db,self.N,self.guarded,p)
            if state is None:
                return None,add(p)
            known,value,basis=state
            w=value
            for bit,(a,b,_) in basis.items():
                if b:
                    w|=bit
            if satisfies(self.db,w):
                assert satisfies(tuple((l,) for l in p),w)
                return w,None
            counts={}
            for c in self.db:
                if any(H.true(l,known,value) for l in c):
                    continue
                for l in c:
                    if not known&(1<<(abs(l)-1)):
                        counts[abs(l)]=counts.get(abs(l),0)+1
            assert counts
            v=max(counts,key=lambda i:(counts[i],-i))
            self.branches+=1
            w,j=visit(p+(-v,))
            if w is not None:
                return w,None
            w,j=visit(p+(v,))
            if w is not None:
                return w,None
            return None,add(p)

        w,j=visit(A)
        return tuple(additions),w,j


def fixture(rows,n):
    formulas=queries=yes=no=checks=active_queries=active_rows=guard_checks=0
    for mask in range(1<<len(rows)):
        f=tuple(c for j,c in enumerate(rows) if mask&(1<<j))
        S=Session(f,n)
        base,N,g=source(f,n)
        db=list(base)
        formulas+=1
        for i in range(-1,len(f)):
            A=mode(f,n,i)
            models=tuple(w for w in range(1<<n) if all(
                satisfies((c,),w)==(j!=i) for j,c in enumerate(f)))
            checks+=1<<n
            for pin in ((),)+tuple((l,) for v in range(1,n+1) for l in (-v,v)):
                p=A+pin
                ms=tuple(w for w in models if satisfies(tuple((l,) for l in pin),w))
                a=active(g,p)
                active_queries+=bool(a)
                active_rows+=len(a)
                for w in ms:
                    for v,b,_ in a:
                        assert H.parity(w&v)==b
                        guard_checks+=1
                result=S.ask(p)
                assert check_step(db,N,g,p,result)
                assert (result[1] is not None)==bool(ms)
                if ms:
                    assert result[1]&((1<<n)-1) in ms
                queries+=1
                yes+=bool(ms)
                no+=not ms
        assert db==S.db
    return [formulas,queries,yes,no,checks,active_queries,active_rows,guard_checks]


def split_source(f,n):
    out=[]
    for j,c in enumerate(f,1):
        assert 2<=len(c)<=3
        u=n+j
        out.extend((c[:-1]+(u,),(-u,c[-1])))
    return tuple(out),n+len(f)


def topology_audit():
    cases=split_cases=0
    for d in (2,3,4):
        n,edges=split_cube(d)
        z=len(edges)+1
        f=encode(n,edges,1)
        S=Session(f,z)
        base,N,g=source(f,z)
        db=list(base)
        assert len(g)==n
        A=mode(f,z,-1)
        wrong=A+(-z,)
        assert ordinary(db,N,wrong) is not None
        result=S.ask(wrong)
        assert result[1] is None and len(result[0])==1 and S.branches==0
        c,trace=result[0][0]
        assert trace[-1][0]=='x' and trace[-1][2]==0
        assert check_step(db,N,g,wrong,result)
        q=S.ask(A+(z,))
        assert q[1] is not None and S.branches==0 and check_step(db,N,g,A+(z,),q)
        assert S.ask(wrong)[0]==()
        cases+=1
        f2,n2=split_source(f,z)
        assert not source(f2,n2)[2]
        for j,C in enumerate(f):
            pair=f2[2*j:2*j+2]
            u=z+j+1
            vs=tuple(abs(l) for l in C)
            for bits in range(1<<len(vs)):
                w=sum(1<<(v-1) for k,v in enumerate(vs) if bits>>k&1)
                want=satisfies((C,),w)
                assert want==any(satisfies(pair,w|(b<<(u-1))) for b in (0,1))
                b=int(satisfies(((C[-1],),),w))
                assert satisfies(pair,w|(b<<(u-1)))==want
        split_cases+=1
    return cases,split_cases


def guard_audit():
    f=((1,2),(-1,-2))
    S=Session(f,2)
    base,N,g=source(f,2)
    db=list(base)
    A=(3,4,-1,-2)
    state,trace=conflict(db,N,g,A)
    assert state is None and trace[-1][0]=='x'
    # Removing the positive guard makes the original assignment feasible.
    p=(-3,4,-1,-2)
    q=S.ask(p)
    assert q[1] is not None and check_step(db,N,g,p,q)
    # A valid XOR proof cannot be replayed under disabled guards.
    c=canonical(-l for l in p)
    assert not check_add(db,N,g,c,trace)
    c=canonical(-l for l in A)
    corrupt=trace[:-1]+(('x',1<<len(active(g,A)),0),)
    assert not check_add(db,N,g,c,corrupt)
    assert not check_step(db,N,g,A,((((),trace),),None,len(db)))
    r=S.ask(A)
    assert r[1] is None and check_step(db,N,g,A,r)
    return 4


def audit():
    full=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3)) for w in range(8))
    binary=((-1,),(1,),(-2,),(2,),(-1,-2),(-1,2),(1,-2),(1,2))
    a=fixture(full,3)
    b=fixture(binary,2)
    p,s=topology_audit()
    g=guard_audit()
    print('F038_TECTX_GUARDED_AFFINE_OK full='+','.join(map(str,a))+
          ' binary='+','.join(map(str,b))+' parity_cases='+str(p)+
          ' split_cases='+str(s)+' guard_controls='+str(g))
    return {'full':a,'binary':b,'parity_cases':p,'split_cases':s,'guard_controls':g}


if __name__=='__main__':
    run_attempt(PLAN,audit)
