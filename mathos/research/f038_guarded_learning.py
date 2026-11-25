"""Persistent guarded RUP proof streams for changing clause and pin queries."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_adaptive_rup import propagate, solve


def base_db(f,n):
    out=[]
    for j,c in enumerate(f,1):
        e=n+j
        out.append((-e,)+tuple(c))
        out.extend((e,-l) for l in c)
    return tuple(out),n+len(f)


def canonical(c):
    s=set(c)
    if any(-l in s for l in s):
        return None
    return tuple(sorted(s,key=lambda l:(abs(l),l)))


def valid_assumptions(A,n):
    return (all(type(l) is int and 1<=abs(l)<=n for l in A)
            and len({abs(l) for l in A})==len(A))


def lifted(c,A):
    return canonical(tuple(c)+tuple(-l for l in A))


def rup(db,n,c):
    return (all(type(l) is int and 1<=abs(l)<=n for l in c)
            and canonical(c)==c
            and propagate(db,n,tuple(-l for l in c)) is None)


def matching(db,A):
    s=set(A)
    return next((j for j,c in enumerate(db) if all(-l in s for l in c)),None)


class Session:
    def __init__(self,f,n):
        self.base,self.n=base_db(f,n)
        self.db=list(self.base)
        self.index={canonical(c):i for i,c in enumerate(self.db)}
        self.reused=0
        self.scoped=0

    def add(self,c):
        assert c is not None
        if c in self.index:
            return self.index[c]
        assert rup(self.db,self.n,c)
        i=len(self.db)
        self.db.append(c)
        self.index[c]=i
        return i

    def ask(self,A):
        A=tuple(A)
        assert valid_assumptions(A,self.n)
        start=len(self.db)
        j=matching(self.db,A)
        if j is not None:
            self.reused+=1
            return (),None,j
        if propagate(self.db,self.n,A) is None:
            w=None
        else:
            self.scoped+=1
            w,trace,_=solve(tuple(self.db)+tuple((l,) for l in A),self.n)
            for c in trace:
                d=lifted(c,A)
                if d is not None:
                    self.add(d)
        if w is not None:
            assert satisfies(self.base,w) and satisfies(tuple((l,) for l in A),w)
            return tuple(self.db[start:]),w,None
        core=list(A)
        for l in A:
            trial=tuple(q for q in core if q!=l)
            if propagate(self.db,self.n,trial) is None:
                core=list(trial)
        c=lifted((),core)
        j=self.add(c)
        assert all(-l in A for l in c)
        return tuple(self.db[start:]),None,j


def check_step(db,n,A,result):
    # Only append after the entire result has been checked.
    try:
        additions,w,j=result
        if not valid_assumptions(A,n):
            return False
        trial=list(db)
        for c in additions:
            if not rup(trial,n,c):
                return False
            trial.append(c)
        if w is None:
            if type(j) is not int or not 0<=j<len(trial):
                return False
            if not all(-l in A for l in trial[j]):
                return False
        else:
            if j is not None or type(w) is not int or not 0<=w<1<<n:
                return False
            if not satisfies(trial,w) or not satisfies(tuple((l,) for l in A),w):
                return False
        db[:]=trial
        return True
    except (TypeError,ValueError,IndexError):
        return False


def mode(f,n,i):
    return tuple(-(n+j+1) if j==i else n+j+1 for j in range(len(f)))


def fixture_audit(rows,n):
    formulas=queries=yes=no=model_checks=bad_queries=bad_sat=pinned_queries=pinned_sat=0
    learned=reused=scoped=0
    for mask in range(1<<len(rows)):
        f=tuple(c for j,c in enumerate(rows) if mask&(1<<j))
        S=Session(f,n)
        db=list(S.base)
        formulas+=1
        for i in range(-1,len(f)):
            A=mode(f,n,i)
            models=tuple(w for w in range(1<<n) if all(
                satisfies((c,),w)==(j!=i) for j,c in enumerate(f)))
            model_checks+=1<<n
            bad_queries+=i>=0
            bad_sat+=i>=0 and bool(models)
            pins=((),)+tuple((l,) for v in range(1,n+1) for l in (-v,v))
            for pin in pins:
                want=any(satisfies(tuple((l,) for l in pin),w) for w in models)
                result=S.ask(A+pin)
                assert check_step(db,S.n,A+pin,result)
                assert (result[1] is not None)==want
                if want:
                    assert result[1]&((1<<n)-1) in models
                queries+=1
                yes+=want
                no+=not want
                pinned_queries+=bool(pin)
                pinned_sat+=bool(pin) and want
                learned+=len(result[0])
        assert db==S.db
        reused+=S.reused
        scoped+=S.scoped
    print('F038_GUARDED_LEARNING_WORK learned='+str(learned)+
          ' direct_reuse='+str(reused)+' scoped_search='+str(scoped))
    return formulas,queries,yes,no,model_checks,bad_queries,bad_sat,pinned_queries,pinned_sat


def reuse_audit():
    f=((1,2),(1,-2),(-1,2),(-1,-2))
    S=Session(f,2)
    db=list(S.base)
    A=mode(f,2,-1)
    assert propagate(db,S.n,A) is not None
    r=S.ask(A)
    assert r[1] is None and r[0] and S.scoped==1
    assert check_step(db,S.n,A,r)
    assert S.db[r[2]] and all(-l in A for l in S.db[r[2]])
    for pin in (-1,1,-2,2):
        q=S.ask(A+(pin,))
        assert q[0]==() and q[1] is None and check_step(db,S.n,A+(pin,),q)
    assert S.reused==4
    for i in range(4):
        a=mode(f,2,i)
        q=S.ask(a)
        assert q[1] is not None and check_step(db,S.n,a,q)
    assert db==S.db
    fresh=list(S.base)
    assert not check_step(fresh,S.n,A,(((),),None,len(fresh)))
    assert fresh==list(S.base)
    assert not check_step(list(S.db),S.n,mode(f,2,0),((),None,r[2]))
    assert not check_step(list(S.db),S.n,A,((),0,None))
    print('F038_GUARDED_REUSE_OK non_up_refutation=1 direct_reuse=4 '
          'changed_mode_sat=4 corrupt_rejected=3')


def audit():
    a=fixture_audit(ROWS,3)
    assert a==(4096,200704,34112,166592,229376,24576,6416,172032,26336)
    print('F038_GUARDED_LEARNING_OK formulas=4096 queries=200704 sat=34112 '
          'unsat=166592 model_checks=229376 bad_queries=24576 bad_sat=6416 '
          'pinned_queries=172032 pinned_sat=26336')
    rows=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
               for w in range(8))
    a=fixture_audit(rows,3)
    assert a==(256,8960,5791,3169,10240,1024,1024,7680,4512)
    print('F038_GUARDED_LEARNING_FULL_OK formulas=256 queries=8960 sat=5791 '
          'unsat=3169 model_checks=10240 bad_queries=1024 bad_sat=1024 '
          'pinned_queries=7680 pinned_sat=4512')
    reuse_audit()


if __name__=='__main__':
    audit()
