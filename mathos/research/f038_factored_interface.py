"""Factored witness interfaces, exact message DP, and state diversity audit."""
from itertools import product
from mathos.research.f038_horn_cover import satisfies
from mathos.research.f038_monotone_choice import sat, restrict

BAGS=((1,2),(2,3,4),(1,2,5),(3,4,6))
CHILDREN=((1,2),(3,),(),())
ROWS=(((1,-2),(2,)),((2,3,-4),(-2,4),(-3,4)),
      ((1,5),(-1,-5),(2,-5)),((3,4,6),(-3,-6),(-4,6),(-6,)))


def mask_of(vs):
    return sum(1<<(v-1) for v in vs)


def vals(mask):
    """Enumerate only assignments to the indicated bits."""
    v=mask
    while True:
        yield v
        if v==0:
            break
        v=(v-1)&mask


def messages(bags,children,fs,u,pin=None):
    """Nodes in parent-before-child order; masks encode bag assignments."""
    out=[None]*len(bags)
    for i in reversed(range(len(bags))):
        b=bags[i]
        tagmask=b&u
        result=set()
        for tag in vals(tagmask):
            if pin is not None and pin&tagmask!=tag:
                continue
            local=frozenset(v for v in vals(b) if v&tagmask==tag
                            and satisfies(fs[i],v))
            ts={local}
            for c in children[i]:
                sep=b&bags[c]
                next_ts=set()
                for ctag,ct in out[c]:
                    if (ctag^tag)&sep&u:
                        continue
                    projected={v&sep for v in ct}
                    for t in ts:
                        next_ts.add(frozenset(v for v in t if v&sep in projected))
                ts=next_ts
            result.update((tag,t) for t in ts)
        out[i]=result
    return out


def reconstruct(bags,children,fs,u,x):
    out=messages(bags,children,fs,u,x)
    assert all(len(s)==1 for s in out)
    tables=[next(iter(s))[1] for s in out]
    if not tables[0]:
        return None

    def walk(i,row):
        w=row
        for c in children[i]:
            sep=bags[i]&bags[c]
            child=next(v for v in tables[c] if (v^row)&sep==0)
            w|=walk(c,child)
        return w

    w=walk(0,next(iter(tables[0])))
    assert w&u==x and all(satisfies(f,w) for f in fs)
    return w


def tree_audit():
    bags=tuple(mask_of(vs) for vs in BAGS)
    sub=list(bags)
    for i in reversed(range(4)):
        for j in CHILDREN[i]:
            sub[i]|=sub[j]
    families=total=non=params=witnesses=checks=maximum=0
    domain=tuple(range(64))
    for mask in range(4096):
        fs=[]
        bit=0
        for rs in ROWS:
            fs.append(tuple(c for i,c in enumerate(rs,bit) if mask&(1<<i)))
            bit+=len(rs)
        assert bit==12
        subfs=list(fs)
        for i in reversed(range(4)):
            for j in CHILDREN[i]:
                subfs[i]+=subfs[j]
        models=tuple(w for w in domain if satisfies(subfs[0],w))
        for u in (mask_of((1,3,5)),mask_of((2,4,6))):
            out=messages(bags,CHILDREN,fs,u)
            valid=True
            for x in vals(u):
                want=any(w&u==x for w in models)
                w=reconstruct(bags,CHILDREN,fs,u,x)
                assert (w is not None)==want
                valid &= want
                params+=1
                witnesses+=want
            assert all(t for _,t in out[0])==valid
            for i,b in enumerate(bags):
                ref=set()
                sm=sub[i]&u
                ms=tuple(w for w in domain if satisfies(subfs[i],w))
                for x in vals(sm):
                    table=frozenset(w&b for w in ms if w&sm==x)
                    ref.add((x&b&u,table))
                assert ref==out[i]
                checks+=1
                maximum=max(maximum,len(ref))
            families+=1
            total+=valid
            non+=not valid
    assert (families,total,non,params,witnesses,checks,maximum)==(
        8192,592,7600,65536,27344,32768,8)
    print(f'F038_FACTORED_INTERFACE_OK families={families} total={total} '
          f'non_total={non} parameters={params} witnesses={witnesses} '
          f'message_checks={checks} max_messages={maximum}')


def address_template(k):
    d=1<<k
    top=k+d
    f=[]
    for s in range(d):
        row=tuple(-i-1 if s&(1<<i) else i+1 for i in range(k))+(k+s+1,)
        while len(row)>3:
            top+=1
            f.append((row[0],row[1],top))
            row=(-top,*row[2:])
        f.append(row)
    assert all(1<=len(c)<=3 for c in f)
    return tuple(f)


def shatter_audit():
    families=tables=contexts=0
    for k in range(1,4):
        d=1<<k
        f=address_template(k)
        seen=set()
        for x in range(1<<d):
            g=restrict(f,{k+s+1:bool(x&(1<<s)) for s in range(d)})
            table=0
            for s in range(d):
                got=sat(restrict(g,{i+1:bool(s&(1<<i)) for i in range(k)}))
                assert got==bool(x&(1<<s))
                table|=got<<s
                contexts+=1
            assert table==x and table not in seen
            seen.add(table)
            families+=1
        assert len(seen)==1<<d
        tables+=len(seen)
    assert (families,tables,contexts)==(276,276,2120)
    print(f'F038_INTERFACE_SHATTER_OK families={families} tables={tables} '
          f'context_checks={contexts}')


if __name__=='__main__':
    tree_audit()
    shatter_audit()
