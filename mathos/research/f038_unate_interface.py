"""Syntactic unate seed synthesis and semantic-polarity hardness regression."""
from mathos.research.f038_factored_interface import (
    BAGS, CHILDREN, ROWS, mask_of, vals, reconstruct,
)
from mathos.research.f038_rule_certification import ROWS as MATRIX
from mathos.research.f038_horn_cover import satisfies
from mathos.research.f038_monotone_choice import sat, restrict
from mathos.research.f038_symbolic_interface import check_decomposition


def polarity(f,u):
    pos=neg=0
    for c in f:
        for l in c:
            bit=1<<(abs(l)-1)
            if l>0:
                pos|=bit
            else:
                neg|=bit
    return u&pos&neg,u&neg&~pos


def seeds(bags,children,fs,u):
    f=tuple(c for local in fs for c in local)
    h,worst=polarity(f,u)
    return h,{a:reconstruct(bags,children,fs,u,a|worst)
              for a in vals(h)}


def reuse(h,table,u,x):
    seed=table[x&h]
    return None if seed is None else (seed&~u)|x


def positive():
    bags=tuple(mask_of(b) for b in BAGS)
    families=total=non=probes=missing=witnesses=slices=maximum=params=0
    for mask in range(4096):
        fs=[]
        bit=0
        for rs in ROWS:
            fs.append(tuple(c for i,c in enumerate(rs,bit) if mask&(1<<i)))
            bit+=len(rs)
        assert bit==12
        f=tuple(c for local in fs for c in local)
        models=tuple(w for w in range(64) if satisfies(f,w))
        for u in (21,42):
            h,table=seeds(bags,CHILDREN,fs,u)
            valid=True
            for a,seed in table.items():
                success=seed is not None
                probes+=1
                missing+=not success
                slices+=success
                slice_total=True
                for x0 in vals(u&~h):
                    x=a|x0
                    feasible=any(w&u==x for w in models)
                    slice_total &= feasible
                    w=reuse(h,table,u,x)
                    if w is not None:
                        assert w&u==x and satisfies(f,w)
                        witnesses+=1
                    params+=1
                assert slice_total==success
                valid &= success
            assert valid==all(any(w&u==x for w in models) for x in vals(u))
            families+=1
            total+=valid
            non+=not valid
            maximum=max(maximum,len(table))
    assert (families,total,non,probes,missing,slices,witnesses,params,maximum)==(
        8192,592,7600,30964,24508,6456,13421,65536,8)
    print(f'F038_UNATE_SEEDS_OK families={families} total={total} non_total={non} '
          f'seed_probes={probes} missing={missing} successful_slices={slices} '
          f'reused_witnesses={witnesses} parameters={params} max_probes={maximum}')


def reduction(d,n):
    k=max(1,(max(1,len(d))-1).bit_length())
    t,r=n+1,n+2
    p=tuple(range(n+3,n+k+3))
    top=n+k+2
    base=mask_of((t,r)+p)
    bags=[base]
    children=[[]]
    fs=[[(r,t)]]

    def node(parent,scope):
        i=len(bags)
        bags.append(scope)
        children.append([])
        fs.append([])
        children[parent].append(i)
        return i

    groups={i:node(0,base|1<<(i-1)) for i in range(1,n+1)}

    def add(row,parent):
        nonlocal top
        scope=bags[parent]
        prev=0
        while len(row)>3:
            top+=1
            bit=1<<(top-1)
            child=node(parent,scope|prev|bit)
            fs[child].append((row[0],row[1],top))
            parent=child
            prev=bit
            row=(-top,*row[2:])
        child=node(parent,scope|prev)
        fs[child].append(row)

    for j in range(1<<k):
        mismatch=tuple(-v if j&(1<<i) else v for i,v in enumerate(p))
        prefix=(-t,-r)+mismatch
        if j>=len(d):
            add(prefix,0)
        else:
            for l in d[j]:
                add(prefix+(-l,),groups[abs(l)])
    return top,tuple(bags),tuple(tuple(c) for c in children),tuple(tuple(f) for f in fs)


def negative():
    matrices=unsat=source_sat=checks=rises=falls=unate=max_v=max_c=0
    for mask in range(1<<len(MATRIX)):
        d=tuple(c for i,c in enumerate(MATRIX) if mask&(1<<i))
        top,bags,children,fs=reduction(d,3)
        check_decomposition(top,bags,children,fs)
        k=max(1,(max(1,len(d))-1).bit_length())
        assert max(b.bit_count() for b in bags)<=k+5
        f=tuple(c for local in fs for c in local)
        rise=fall=False
        is_unsat=True
        for x in range(8):
            good=satisfies(d,x)
            is_unsat &= not good
            for r in (0,1):
                bits=[]
                for t in (0,1):
                    w=x|(t<<3)|(r<<4)
                    got=sat(restrict(f,{i+1:bool(w&(1<<i)) for i in range(5)}))
                    want=bool((r or t) and (not r or not t or not good))
                    assert got==want
                    bits.append(got)
                    checks+=1
                up=not bits[0] and bits[1]
                down=bits[0] and not bits[1]
                rises+=up
                falls+=down
                rise|=up
                fall|=down
        assert rise and fall== (not is_unsat)
        matrices+=1
        unsat+=is_unsat
        source_sat+=not is_unsat
        unate+=not fall
        max_v=max(max_v,top)
        max_c=max(max_c,len(f))
    assert (matrices,unsat,source_sat,checks,rises,falls,unate,max_v,max_c)==(
        4096,2736,1360,131072,32768,2304,2736,109,127)
    print(f'F038_SEMANTIC_POLARITY_OK matrices={matrices} unsat={unsat} '
          f'sat={source_sat} projection_checks={checks} rising_edges={rises} '
          f'falling_edges={falls} unate={unate} max_variables={max_v} max_clauses={max_c}')


if __name__=='__main__':
    positive()
    negative()
