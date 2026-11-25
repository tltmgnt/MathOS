"""Provenance-checked width-three degree-two elimination and guarded XOR recovery."""
from mathos.research.f038_rule_certification import ROWS,satisfies
from mathos.research import f038_hybrid_affine as H
from mathos.research import f038_guarded_affine as G
from mathos.research.f038_guarded_learning import base_db,canonical,mode
from mathos.research.f038_resolution_certificate import split_cube,encode
from mathos.research.f038_tectx_cycle import run_attempt

PLAN='docs/research/tga-universal/f038-tectx-affine-recovery.json'


def eligible(pool,live,n):
    for u in range(1,n+1):
        pos=[i for i in live if u in pool[i][0]]
        neg=[i for i in live if -u in pool[i][0]]
        if len(pos)!=1 or len(neg)!=1:
            continue
        i,j=pos[0],neg[0]
        c=canonical(tuple(l for l in pool[i][0] if l!=u)+
                    tuple(l for l in pool[j][0] if l!=-u))
        if c is None or len(c)<=3:
            return u,i,j,c
    return None


def eliminate(f,n):
    pool=[(tuple(c),(i,)) for i,c in enumerate(f)]
    live=list(range(len(f)))
    trace=[]
    while True:
        step=eligible(pool,live,n)
        if step is None:
            break
        u,i,j,c=step
        live=[k for k in live if k not in (i,j)]
        k=-1
        if c is not None:
            k=len(pool)
            pool.append((c,tuple(sorted(set(pool[i][1]+pool[j][1])))))
            live.append(k)
        trace.append((u,i,j,k))
    return tuple(pool),tuple(live),tuple(trace)


def verify_elimination(f,n,cert):
    try:
        pool,live,trace=cert
        if tuple(pool[:len(f)])!=tuple((tuple(c),(i,)) for i,c in enumerate(f)):
            return False
        current=list(range(len(f)))
        top=len(f)
        for u,i,j,k in trace:
            expected=eligible(pool,current,n)
            if expected is None or expected[:3]!=(u,i,j):
                return False
            c=expected[3]
            if c is None:
                if k!=-1:
                    return False
            else:
                support=tuple(sorted(set(pool[i][1]+pool[j][1])))
                if k!=top or pool[k]!=(c,support):
                    return False
                top+=1
            current=[a for a in current if a not in (i,j)]
            if k!=-1:
                current.append(k)
        return (tuple(current)==live and top==len(pool)
                and eligible(pool,current,n) is None)
    except (TypeError,ValueError,IndexError,KeyError):
        return False


def reduced(cert):
    pool,live,_=cert
    return tuple(pool[i][0] for i in live)


def restore(cert,w):
    pool,_,trace=cert
    for u,i,j,k in reversed(trace):
        bit=1<<(u-1)
        w&=~bit
        if not satisfies((pool[i][0],),w):
            w|=bit
        assert satisfies((pool[i][0],pool[j][0]),w)
    return w


def guarded_rows(f,n,cert):
    assert verify_elimination(f,n,cert)
    pool,live,_=cert
    out=set()
    for ids in (tuple(range(len(f))),live):
        clauses=tuple(pool[i][0] for i in ids)
        rows,rest=H.extract(clauses)
        assert H.verify_partition(clauses,rows,rest)
        for a,b,local in rows:
            guards=tuple(sorted({n+q+1 for i in local for q in pool[ids[i]][1]}))
            out.add((a,b,guards))
    return tuple(sorted(out))


class Session(G.Session):
    def __init__(self,f,n):
        self.f=tuple(f)
        self.n=n
        self.cert=eliminate(self.f,n)
        self.base,self.N=base_db(self.f,n)
        self.guarded=guarded_rows(self.f,n,self.cert)
        self.db=list(self.base)
        self.index={canonical(c):i for i,c in enumerate(self.base)}
        self.reused=0
        self.branches=0
        self.fast=0

    def ask(self,A):
        A=tuple(A)
        assert G.valid_assumptions(A,self.N)
        pins=tuple(l for l in A if abs(l)<=self.n)
        eliminated={u for u,i,j,k in self.cert[2]}
        if all(l in A for l in mode(self.f,self.n,-1)) and not any(
                abs(l) in eliminated for l in pins):
            rows,rest=H.extract(reduced(self.cert))
            if not rest:
                known,value=H.pins(pins,self.n)
                basis,bad=H.reduce(rows,known,value)
                if basis is not None:
                    w=value
                    for bit,(a,b,p) in basis.items():
                        if b:
                            w|=bit
                    w=restore(self.cert,w)
                    w|=((1<<len(self.f))-1)<<self.n
                    assert satisfies(self.db,w) and satisfies(tuple((l,) for l in A),w)
                    self.fast+=1
                    return (),w,None
        return super().ask(A)


def projection_audit(rows,n):
    formulas=steps=checks=projections=yes=extensions=0
    for mask in range(1<<len(rows)):
        f=tuple(c for i,c in enumerate(rows) if mask&(1<<i))
        cert=eliminate(f,n)
        assert verify_elimination(f,n,cert)
        d=reduced(cert)
        removed=sum(1<<(u-1) for u,i,j,k in cert[2])
        models=tuple(w for w in range(1<<n) if satisfies(f,w))
        ps={w&~removed for w in models}
        checks+=1<<n
        yes+=bool(models)
        for w in range(1<<n):
            if w&removed:
                continue
            assert satisfies(d,w)==(w in ps)
            projections+=1
            if w in ps:
                x=restore(cert,w)
                assert x in models and x&~removed==w
                extensions+=1
        formulas+=1
        steps+=len(cert[2])
    return [formulas,steps,checks,projections,yes,extensions]


def guarded_audit(rows,n):
    formulas=queries=yes=no=active_queries=active_rows=checks=total=0
    for mask in range(1<<len(rows)):
        f=tuple(c for i,c in enumerate(rows) if mask&(1<<i))
        S=Session(f,n)
        cert=eliminate(f,n)
        g=guarded_rows(f,n,cert)
        db,N=base_db(f,n)
        db=list(db)
        total+=len(g)
        for i in range(-1,len(f)):
            A=mode(f,n,i)
            models=tuple(w for w in range(1<<n) if all(
                satisfies((c,),w)==(j!=i) for j,c in enumerate(f)))
            for pin in ((),)+tuple((l,) for v in range(1,n+1) for l in (-v,v)):
                p=A+pin
                ms=tuple(w for w in models if satisfies(tuple((l,) for l in pin),w))
                a=G.active(g,p)
                active_queries+=bool(a)
                active_rows+=len(a)
                for w in ms:
                    for v,b,_ in a:
                        assert H.parity(w&v)==b
                        checks+=1
                result=S.ask(p)
                assert G.check_step(db,N,g,p,result)
                assert (result[1] is not None)==bool(ms)
                if ms:
                    assert result[1]&((1<<n)-1) in ms
                queries+=1
                yes+=bool(ms)
                no+=not ms
        assert db==S.db
        formulas+=1
    return [formulas,queries,yes,no,active_queries,active_rows,checks,total]


def cycle_source(f,n):
    out=[]
    for j,c in enumerate(f):
        us=tuple(n+3*j+i for i in (1,2,3))
        for u in us:
            out.extend((c[:-1]+(u,),(-u,c[-1])))
        out.extend((-u,us[(i+1)%3]) for i,u in enumerate(us))
    return tuple(out),n+3*len(f)


def family_audit():
    cases=steps=rows_count=local_checks=blocked=0
    for d in (2,3,4):
        nv,edges=split_cube(d)
        z=len(edges)+1
        f=encode(nv,edges,1)
        f2,n=G.split_source(f,z)
        S=Session(f2,n)
        assert not G.source(f2,n)[2]
        assert len(S.cert[2])==len(f)
        assert set(reduced(S.cert))=={canonical(c) for c in f}
        assert len(S.guarded)==nv
        A=mode(f2,n,-1)
        db=list(S.base)
        wrong=A+(-z,)
        r=S.ask(wrong)
        assert r[1] is None and len(r[0])==1 and S.branches==0
        assert r[0][0][1][-1][0]=='x'
        assert G.check_step(db,S.N,S.guarded,wrong,r)
        q=S.ask(A+(z,))
        assert q[1] is not None and S.fast==1 and S.branches==0
        assert G.check_step(db,S.N,S.guarded,A+(z,),q)
        assert S.ask(wrong)[0]==()
        hard,hn=cycle_source(f,z)
        cert=eliminate(hard,hn)
        assert not cert[2] and not guarded_rows(hard,hn,cert)
        for j,c in enumerate(f):
            gadget=hard[9*j:9*j+9]
            us=tuple(z+3*j+i for i in (1,2,3))
            vs=tuple(abs(l) for l in c)
            for a in range(1<<len(c)):
                w=sum(1<<(v-1) for i,v in enumerate(vs) if a>>i&1)
                want=satisfies((c,),w)
                assert want==any(satisfies(gadget,w|sum(
                    1<<(u-1) for i,u in enumerate(us) if t>>i&1)) for t in range(8))
                local_checks+=1
        cases+=1
        steps+=len(S.cert[2])
        rows_count+=len(S.guarded)
        blocked+=1
    return [cases,steps,rows_count,local_checks,blocked]


def control_audit():
    f=((1,3),(-3,2))
    cert=eliminate(f,3)
    pool,live,trace=cert
    assert trace and verify_elimination(f,3,cert)
    bad=list(pool)
    k=next(k for u,i,j,k in trace if k!=-1)
    bad[k]=(bad[k][0],())
    assert not verify_elimination(f,3,(tuple(bad),live,trace))
    assert not verify_elimination(f,3,(pool,live,trace[:-1]))
    # An isolated split parity gadget with original bits protected from
    # elimination by repeated occurrences on distinct scopes.
    f0=((1,2),(-1,-2))
    f2,n=G.split_source(f0,2)
    f2+=((1,5),(1,6),(-1,7),(-1,8),
          (2,9),(2,10),(-2,11),(-2,12))
    n=12
    S=Session(f2,n)
    g=S.guarded
    row=next((a,b,p) for a,b,p in g if a==3 and b==1)
    A=row[2]+(-1,-2)
    state,proof=G.conflict(S.db,S.N,g,A)
    assert state is None and proof[-1][0]=='x'
    c=canonical(-l for l in A)
    assert G.check_add(S.db,S.N,g,c,proof)
    p=tuple(l for l in A if l!=row[2][0])
    assert not G.check_add(S.db,S.N,g,canonical(-l for l in p),proof)
    assert not G.check_add(S.db,S.N,g,c,proof[:-1]+(('x',1<<len(G.active(g,A)),0),))
    assert not G.check_step(list(S.db),S.N,g,A,((((),proof),),None,len(S.db)))
    return 5


def audit():
    full=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3)) for w in range(8))
    binary=((-1,),(1,),(-2,),(2,),(-1,-2),(-1,2),(1,-2),(1,2))
    a=projection_audit(ROWS,3)
    b=projection_audit(full,3)
    c=projection_audit(binary,2)
    g=guarded_audit(binary,2)
    f=family_audit()
    k=control_audit()
    print('F038_TECTX_RECOVERY_OK primary='+','.join(map(str,a))+
          ' full='+','.join(map(str,b))+' binary='+','.join(map(str,c))+
          ' guarded='+','.join(map(str,g))+' families='+','.join(map(str,f))+
          ' controls='+str(k))
    return {'primary':a,'full':b,'binary':c,'guarded':g,'families':f,'controls':k}


if __name__=='__main__':
    run_attempt(PLAN,audit)
