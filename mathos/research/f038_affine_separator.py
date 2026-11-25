"""Exact affine separator DP and independently checked table certificates."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_hybrid_affine import extract, verify_partition, reduce, combination, parity
from mathos.research.f038_affine_direct_sum import coordinate_forms, plan


def span(vs):
    b,bad=reduce(tuple((v,0,()) for v in vs))
    assert bad is None
    return tuple(b[k][0] for k in sorted(b))


def orthogonal(vs,n):
    b,bad=reduce(tuple((v,0,()) for v in vs))
    assert bad is None
    return tuple(bit|sum(k for k,(a,_,_) in b.items() if a&bit)
                 for i in range(n) if (bit:=1<<i) not in b)


def intersection(a,b,n):
    return orthogonal(orthogonal(a,n)+orthogonal(b,n),n)


def signature(t,b):
    return sum(parity(t&v)<<i for i,v in enumerate(b))


def equations(b,z):
    return tuple((v,(z>>i)&1,()) for i,v in enumerate(b))


def lift(eqs):
    b,bad=reduce(eqs)
    if b is None:
        return None
    return sum(k for k,(_,rhs,_) in b.items() if rhs)


def make_tree(scopes,n):
    nodes=[]
    def visit(lo,hi):
        w=span(v for s in scopes[lo:hi] for v in s)
        o=span(v for s in scopes[:lo]+scopes[hi:] for v in s)
        s=span(intersection(w,o,n))
        children=()
        if hi-lo>1:
            mid=(lo+hi)//2
            children=(visit(lo,mid),visit(mid,hi))
        i=len(nodes)
        nodes.append((lo,hi,w,s,children))
        return i
    visit(0,len(scopes))
    return tuple(nodes)


def setup(f,n,rows,rest):
    forms,bad=coordinate_forms(rows,n)
    if forms is None:
        return None,bad
    db=tuple(f[i] for i in rest)
    scopes=tuple(span(forms[abs(l)-1][0] for l in c) for c in db)
    return (forms,db,make_tree(scopes,n)),None


def clause(c,forms,t):
    return any((parity(forms[abs(l)-1][0]&t)^forms[abs(l)-1][1])==int(l>0)
               for l in c)


def leaf_rows(node,forms,db):
    lo,hi,w,s,_=node
    for z in range(1<<len(w)):
        t=lift(equations(w,z))
        assert t is not None
        if all(clause(c,forms,t) for c in db[lo:hi]):
            yield signature(t,s),t


def run(f,n):
    rows,rest=extract(f)
    assert verify_partition(f,rows,rest)
    p,bad=setup(f,n,rows,rest)
    if p is None:
        return None,('xor',bad),None,None
    forms,db,nodes=p
    tables=[]
    stats=[len(nodes),0,0,0,0,0,0,0,0]
    for lo,hi,w,s,children in nodes:
        stats[7]=max(stats[7],len(s))
        table={}
        if not children:
            stats[1]+=1
            stats[4]+=1<<len(w)
            stats[8]=max(stats[8],len(w))
            for z,t in leaf_rows((lo,hi,w,s,children),forms,db):
                table[z]=t
        else:
            stats[2]+=1
            a,b=children
            wa,sa=nodes[a][2:4]
            wb,sb=nodes[b][2:4]
            for za,ta in tables[a].items():
                for zb,tb in tables[b].items():
                    stats[5]+=1
                    t=lift(equations(sa,za)+equations(sb,zb))
                    if t is None:
                        continue
                    stats[6]+=1
                    z=signature(t,s)
                    glued=lift(equations(wa,signature(ta,wa))+
                               equations(wb,signature(tb,wb)))
                    assert glued is not None and signature(glued,s)==z
                    table[z]=glued
        stats[3]+=len(table)
        tables.append(table)
    cert=('tables',tuple(tuple(sorted(t)) for t in tables))
    if not tables[-1]:
        assert verify_negative(f,n,rows,rest,cert)
        return None,cert,p,tuple(stats)
    t=tables[-1][0]
    x=sum(1<<i for i,(a,b) in enumerate(forms) if parity(a&t)^b)
    assert satisfies(f,x)
    return x,cert,p,tuple(stats)


def verify_negative(f,n,rows,rest,cert):
    if not verify_partition(f,rows,rest):
        return False
    kind,data=cert
    if kind=='xor':
        return combination(rows,data)==(0,1)
    p,bad=setup(f,n,rows,rest)
    if kind!='tables' or p is None:
        return False
    forms,db,nodes=p
    if len(data)!=len(nodes) or data[-1]:
        return False
    for i,(lo,hi,w,s,children) in enumerate(nodes):
        given=data[i]
        if tuple(sorted(set(given)))!=given or any(z<0 or z>=1<<len(s) for z in given):
            return False
        if not children:
            expected={z for z,t in leaf_rows(nodes[i],forms,db)}
        else:
            a,b=children
            sa,sb=nodes[a][3],nodes[b][3]
            expected=set()
            for za in data[a]:
                for zb in data[b]:
                    t=lift(equations(sa,za)+equations(sb,zb))
                    if t is not None:
                        expected.add(signature(t,s))
        if set(given)!=expected:
            return False
    return True


def audit_fixture(fixture):
    yes=no=inconsistent=empty=checks=0
    totals=[0]*9
    for mask in range(1<<len(fixture)):
        f=tuple(c for i,c in enumerate(fixture) if mask&(1<<i))
        x,cert,p,stats=run(f,3)
        models=tuple(w for w in range(8) if satisfies(f,w))
        assert (x is not None)==bool(models)
        yes+=bool(models)
        no+=not models
        if x is not None:
            assert x in models
        else:
            rows,rest=extract(f)
            assert verify_negative(f,3,rows,rest,cert)
        if p is None:
            inconsistent+=1
            continue
        forms,db,nodes=p
        free=span(a for a,b in forms)
        for node,table in zip(nodes,cert[1]):
            lo,hi,w,s,children=node
            expected=set()
            for z in range(1<<len(free)):
                t=lift(equations(free,z))
                assert t is not None
                if all(clause(c,forms,t) for c in db[lo:hi]):
                    expected.add(signature(t,s))
                checks+=1
            assert set(table)==expected
        for i,v in enumerate(stats):
            totals[i]=max(totals[i],v) if i>=7 else totals[i]+v
        empty+=not cert[1][-1]
    return yes,no,inconsistent,*totals,checks,empty


def cycle(m):
    f=[]
    for i in range(m):
        a,b=2*i+1,2*i+2
        c=2*((i+1)%m)+1
        f.extend(((-a,b),(a,-b),(a,b,c),(-a,-b,-c)))
    return tuple(f),2*m


def audit():
    a=audit_fixture(ROWS)
    assert a==(1360,2736,2384,7860,4786,3074,11948,10226,12666,4308,3,3,18496,352)
    print('F038_AFFINE_SEPARATOR_OK formulas=4096 sat=1360 unsat=2736 '
          'inconsistent=2384 nodes=7860 leaves=4786 joins=3074 entries=11948 '
          'leaf_trials=10226 join_trials=12666 compatible=4308 '
          'max_boundary=3 max_leaf=3 projection_checks=18496 empty_roots=352')
    fixture=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
                  for w in range(8))
    a=audit_fixture(fixture)
    assert a==(255,1,1,1543,899,644,8559,6947,27280,3264,3,3,12000,0)
    print('F038_AFFINE_SEPARATOR_FULL_OK formulas=256 sat=255 unsat=1 '
          'inconsistent=1 nodes=1543 leaves=899 joins=644 entries=8559 '
          'leaf_trials=6947 join_trials=27280 compatible=3264 '
          'max_boundary=3 max_leaf=3 projection_checks=12000 empty_roots=0')
    widths=[]
    corrupt=0
    for m in (3,4,7,8,15,16,31,32):
        f,n=cycle(m)
        x,cert,p,stats=run(f,n)
        rows,rest=extract(f)
        ds,bad=plan(f,n,rows,rest)
        assert len(ds[1])==m and len(ds[4])==1
        assert ds[4][0][0].bit_count()==m
        assert (x is not None)==(m%2==0)
        assert stats[0]==4*m-1 and stats[4]==8*m and stats[8]==2
        widths.append(stats[7])
        if x is None:
            assert verify_negative(f,n,rows,rest,cert)
            data=list(cert[1])
            assert data[0]
            data[0]=data[0][1:]
            assert not verify_negative(f,n,rows,rest,('tables',tuple(data)))
            data=list(cert[1])
            data[-1]=(0,)
            assert not verify_negative(f,n,rows,rest,('tables',tuple(data)))
            corrupt+=2
    assert widths==[3,2,4,2,4,2,4,2] and corrupt==8
    print('F038_AFFINE_SEPARATOR_CYCLE_OK sizes=3,4,7,8,15,16,31,32 '
          'widths=3,2,4,2,4,2,4,2 sat=4 unsat=4 max_global_rank=32 '
          'corrupt_rejected=8')


if __name__=='__main__':
    audit()
