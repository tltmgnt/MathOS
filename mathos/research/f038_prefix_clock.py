"""Real prefix-UP solver, exact bounded gate compiler, and finite regression."""
from mathos.research.f038_rule_certification import ROWS


def holds(f,n,w):
    return all(any(bool(w&(1<<(n-abs(l))))==(l>0) for l in c) for c in f)


def conflict(f,n,w,k):
    a=[(w>>(n-i-1))&1 if i<k else -1 for i in range(n)]
    while True:
        changed=False
        for c in f:
            if any(a[abs(l)-1]==int(l>0) for l in c):
                continue
            u=[l for l in c if a[abs(l)-1]<0]
            if not u:
                return True
            if len(u)==1:
                l=u[0]
                a[abs(l)-1]=int(l>0)
                changed=True
        if not changed:
            return False


def solve(f,n):
    w=0
    events=[]
    while w<1<<n:
        k=next((k for k in range(n+1) if conflict(f,n,w,k)),None)
        if k is None:
            assert holds(f,n,w)
            events.append((w,None))
            return w,events
        nxt=((w>>(n-k))+1)<<(n-k)
        events.append((w,nxt))
        w=nxt
    return None,events


def reference(f,n):
    events=[]
    def visit(p,k):
        w=p<<(n-k)
        # Independent synchronous unit-propagation reference.
        a={i+1:(p>>(k-i-1))&1 for i in range(k)}
        while True:
            todo={}
            bad=False
            for c in f:
                if any(a.get(abs(l),-1)==int(l>0) for l in c):
                    continue
                u=[l for l in c if abs(l) not in a]
                if not u:
                    bad=True
                    break
                if len(u)==1:
                    l=u[0]
                    i,b=abs(l),int(l>0)
                    if i in todo and todo[i]!=b:
                        bad=True
                        break
                    todo[i]=b
            if bad:
                events.append((w,w+(1<<(n-k))))
                return None
            if not todo:
                break
            a.update(todo)
        if k==n:
            assert holds(f,n,w)
            events.append((w,None))
            return w
        v=visit(p*2,k+1)
        return v if v is not None else visit(p*2+1,k+1)
    return visit(0,0),events


class Gates:
    def __init__(self,inputs):
        self.inputs=inputs
        self.top=inputs+1
        self.defs=[]
        self.cnf=[(1,)]
        self.cache={}

    def and2(self,a,b):
        if a==-1 or b==-1 or a==-b:
            return -1
        if a==1 or a==b:
            return b
        if b==1:
            return a
        key=tuple(sorted((a,b)))
        if key in self.cache:
            return self.cache[key]
        self.top+=1
        z=self.top
        self.defs.append((z,a,b))
        self.cnf.extend(((-z,a),(-z,b),(z,-a,-b)))
        self.cache[key]=z
        return z

    def conj(self,ls):
        z=1
        for l in ls:
            z=self.and2(z,l)
        return z

    def disj(self,ls):
        return -self.conj(-l for l in ls)

    def xor(self,a,b):
        return self.disj((self.and2(a,-b),self.and2(-a,b)))


def up_circuit(g,rows,pres,cursor,k):
    n=len(cursor)
    pos=[cursor[i] if i<k else -1 for i in range(n)]
    neg=[-cursor[i] if i<k else -1 for i in range(n)]
    def false(l):
        return neg[l-1] if l>0 else pos[-l-1]
    for _ in range(n):
        pp=[[v] for v in pos]
        nn=[[v] for v in neg]
        for e,c in zip(pres,rows):
            fs=[false(l) for l in c]
            for i,l in enumerate(c):
                derived=g.conj([e]+fs[:i]+fs[i+1:])
                (pp if l>0 else nn)[abs(l)-1].append(derived)
        pos=[g.disj(v) for v in pp]
        neg=[g.disj(v) for v in nn]
    return g.disj([g.and2(a,b) for a,b in zip(pos,neg)]+[
        g.conj([e]+[false(l) for l in c]) for e,c in zip(pres,rows)])


def increment(g,cursor,k):
    n=len(cursor)
    result=[-1]*n
    carry=1
    for i in reversed(range(k)):
        result[i]=g.xor(cursor[i],carry)
        carry=g.and2(cursor[i],carry)
    return result,carry


def compile_miss(rows,n,T):
    g=Gates(len(rows)+n)
    pres=list(range(2,2+len(rows)))
    witness=list(range(2+len(rows),2+len(rows)+n))
    cursor=[-1]*n
    active=1
    accepted=-1
    for _ in range(T):
        prior=1
        choices=[]
        successors=[]
        for k in range(n+1):
            bad=up_circuit(g,rows,pres,cursor,k)
            choose=g.conj((active,prior,bad))
            prior=g.and2(prior,-bad)
            successor,overflow=increment(g,cursor,k)
            choices.append(g.and2(choose,-overflow))
            successors.append(successor)
        accepted=g.disj((accepted,g.and2(active,prior)))
        active=g.disj(choices)
        cursor=[g.disj(g.and2(ch,s[i]) for ch,s in zip(choices,successors))
                for i in range(n)]
    valid=g.conj(g.disj([-e]+[
        witness[l-1] if l>0 else -witness[-l-1] for l in c])
        for e,c in zip(pres,rows))
    out=g.and2(valid,-accepted)
    return g,out,accepted


def pattern(i,bits):
    run=1<<i
    block=((1<<run)-1)<<run
    width=2*run
    while width<bits:
        block|=block<<width
        width*=2
    return block


def evaluate_all(g):
    size=1<<g.inputs
    full=(1<<size)-1
    values=[0,full]+[pattern(i,size) for i in range(g.inputs)]
    def val(l):
        v=values[abs(l)]
        return v if l>0 else full^v
    for z,a,b in g.defs:
        assert z==len(values)
        values.append(val(a)&val(b))
    assert len(values)==g.top+1
    for c in g.cnf:
        assert len(c)<=3
        v=0
        for l in c:
            v|=val(l)
        assert v==full
    return val


def audit():
    n=3
    source=[]
    hist=[0]*9
    jumps=skipped=events=misses=yes=no=deadlines=0
    for mask in range(1<<len(ROWS)):
        f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
        w,ev=solve(f,n)
        assert (w,ev)==reference(f,n)
        models=tuple(v for v in range(1<<n) if holds(f,n,v))
        assert (w is not None)==bool(models)
        for lo,hi in ev:
            if hi is not None:
                assert all(v not in models for v in range(lo,hi))
                jumps+=1
                skipped+=hi-lo
        events+=len(ev)
        hist[len(ev)]+=1
        yes+=bool(models)
        no+=not models
        for T in range(9):
            misses+=bool(models) and len(ev)>T
            deadlines+=1
        source.append((models,len(ev)))
    assert (yes,no,events,jumps,skipped,deadlines,misses,hist)==(
        1360,2736,5888,4528,25648,36864,3152,[0,2992,432,656,16,0,0,0,0])
    print(f'F038_PREFIX_SEARCH_OK formulas={len(source)} sat={yes} unsat={no} '
          f'events={events} jumps={jumps} skipped={skipped} '
          f'deadline_checks={deadlines} misses={misses} max_events=4 '
          f'hist={",".join(map(str,hist))}')
    miss_counts=[]
    cert_counts=[]
    accepted_counts=[]
    for T in range(5):
        g,out,accept=compile_miss(ROWS,n,T)
        value=evaluate_all(g)
        k=0
        accepted=0
        expected=bytearray((1<<g.inputs)//8)
        want_accept=bytearray(len(expected))
        for mask,(models,steps) in enumerate(source):
            hit=bool(models) and steps<=T
            accepted+=hit
            k+=bool(models) and not hit
            for w in range(1<<n):
                # Circuit input index: witness variable 1 is first bit,
                # whereas solver's numeric cursor is MSB first.
                raw=sum(((w>>(n-i-1))&1)<<i for i in range(n))
                idx=mask|(raw<<len(ROWS))
                if hit:
                    want_accept[idx//8]|=1<<(idx%8)
                elif w in models:
                    expected[idx//8]|=1<<(idx%8)
        assert value(accept)==int.from_bytes(want_accept,'little')
        assert value(out)==int.from_bytes(expected,'little')
        # Asserted output plus the checked definitional clauses is the CNF.
        assert all(len(c)<=3 for c in g.cnf+[(out,)])
        miss_counts.append(k)
        cert_counts.append(value(out).bit_count())
        accepted_counts.append(accepted)
    assert (miss_counts,cert_counts,accepted_counts)==(
        [1360,1104,672,16,0],[2304,1688,834,16,0],[0,256,688,1344,1360])
    print('F038_PREFIX_COMPILER_OK deadlines=5 patterns=163840 '
          f'misses={",".join(map(str,miss_counts))} '
          f'certificates={",".join(map(str,cert_counts))} '
          f'accepted={",".join(map(str,accepted_counts))}')


def bad_family(m):
    n=2*m+3
    u,v=n-1,n
    f=[(1,u,v),(1,u,-v),(1,-u,v),(1,-u,-v)]
    for i in range(m):
        a=2+2*i
        b=a+1
        f.extend(((a,b),(-a,-b)))
    return tuple(f),n


def barrier_audit():
    counts=[]
    for m in range(1,7):
        f,n=bad_family(m)
        w,events=solve(f,n)
        assert w is not None and holds(f,n,w) and w&(1<<(n-1))
        assert len(events)>1<<m
        counts.append(len(events))
    assert counts==[8,17,34,67,132,261]
    print(f'F038_PREFIX_CLOCK_BARRIER_OK families=6 events={",".join(map(str,counts))}')


if __name__=='__main__':
    audit()
    barrier_audit()
