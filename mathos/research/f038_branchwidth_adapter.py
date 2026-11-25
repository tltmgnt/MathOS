"""Connectivity oracle and checked arbitrary-tree affine message adapter."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_hybrid_affine import extract, verify_partition, combination, parity
from mathos.research.f038_affine_direct_sum import coordinate_forms
from mathos.research.f038_affine_separator import (
    span, intersection, signature, equations, lift, clause, cycle)
from mathos.research.f038_separator_discovery import (
    tree_width, discover_cycle, balanced)


class Oracle:
    def __init__(self,scopes):
        self.scopes=tuple(tuple(s) for s in scopes)
        self.full=(1<<len(scopes))-1
        self.total=len(span(v for s in self.scopes for v in s))

    def space(self,mask):
        if type(mask) is not int or not 0<=mask<=self.full:
            raise ValueError('invalid subset')
        return span(v for i,s in enumerate(self.scopes) if mask&(1<<i)
                    for v in s)

    def __call__(self,mask):
        return len(self.space(mask))+len(self.space(self.full^mask))-self.total


def comb(ids):
    if len(ids)<=1:
        return ids[0] if ids else 0
    return ids[0],comb(ids[1:])


def setup(f,n,rows,rest,tree,budget=None):
    forms,bad=coordinate_forms(rows,n)
    if forms is None:
        return None,bad
    db=tuple(f[i] for i in rest)
    scopes=tuple(span(forms[abs(l)-1][0] for l in c) for c in db)
    if tree is None:
        tree=balanced([1<<i for i in range(len(db))])
    width=tree_width(scopes,tree)
    if budget is not None and width>budget:
        raise ValueError('separator budget exceeded')
    oracle=Oracle(scopes)
    nodes=[]
    def visit(t):
        if type(t) is int:
            mask=t
            children=()
        else:
            a,b=visit(t[0]),visit(t[1])
            mask=nodes[a][0]|nodes[b][0]
            children=(a,b)
        w=oracle.space(mask)
        s=span(intersection(w,oracle.space(oracle.full^mask),n))
        assert len(s)==oracle(mask)
        i=len(nodes)
        nodes.append((mask,w,s,children))
        return i
    visit(tree)
    return (forms,db,tuple(nodes),width),None


def local(db,forms,mask,t):
    return all(clause(c,forms,t) for i,c in enumerate(db) if mask&(1<<i))


def leaves(node,forms,db):
    mask,w,s,_=node
    for z in range(1<<len(w)):
        t=lift(equations(w,z))
        assert t is not None
        if local(db,forms,mask,t):
            yield signature(t,s),t


def verify_negative(f,n,rows,rest,tree,cert,budget=None):
    if not verify_partition(f,rows,rest):
        return False
    kind,data=cert
    if kind=='xor':
        return combination(rows,data)==(0,1)
    try:
        p,bad=setup(f,n,rows,rest,tree,budget)
    except (ValueError,TypeError):
        return False
    if p is None or kind!='tables':
        return False
    forms,db,nodes,width=p
    if len(data)!=len(nodes) or data[-1]:
        return False
    for i,node in enumerate(nodes):
        mask,w,s,ch=node
        given=data[i]
        if tuple(sorted(set(given)))!=given or any(z<0 or z>=1<<len(s) for z in given):
            return False
        if not ch:
            expected={z for z,t in leaves(node,forms,db)}
        else:
            a,b=ch
            sa,sb=nodes[a][2],nodes[b][2]
            expected=set()
            for za in data[a]:
                for zb in data[b]:
                    t=lift(equations(sa,za)+equations(sb,zb))
                    if t is not None:
                        expected.add(signature(t,s))
        if set(given)!=expected:
            return False
    return True


def run(f,n,tree=None,budget=None):
    rows,rest=extract(f)
    assert verify_partition(f,rows,rest)
    p,bad=setup(f,n,rows,rest,tree,budget)
    if p is None:
        cert=('xor',bad)
        assert verify_negative(f,n,rows,rest,tree,cert,budget)
        return None,cert,None,None
    forms,db,nodes,width=p
    tables=[]
    joins=pairs=compatible=entries=0
    for node in nodes:
        mask,w,s,ch=node
        table={}
        if not ch:
            table.update(leaves(node,forms,db))
        else:
            joins+=1
            a,b=ch
            wa,sa=nodes[a][1:3]
            wb,sb=nodes[b][1:3]
            for za,ta in tables[a].items():
                for zb,tb in tables[b].items():
                    pairs+=1
                    t=lift(equations(sa,za)+equations(sb,zb))
                    if t is None:
                        continue
                    compatible+=1
                    z=signature(t,s)
                    glued=lift(equations(wa,signature(ta,wa))+
                               equations(wb,signature(tb,wb)))
                    assert glued is not None and signature(glued,s)==z
                    table[z]=glued
        entries+=len(table)
        tables.append(table)
    cert=('tables',tuple(tuple(sorted(t)) for t in tables))
    stats=(len(nodes),joins,pairs,compatible,entries,width)
    if not tables[-1]:
        assert verify_negative(f,n,rows,rest,tree,cert,budget)
        return None,cert,p,stats
    t=tables[-1][0]
    w=sum(1<<i for i,(a,b) in enumerate(forms) if parity(a&t)^b)
    assert satisfies(f,w)
    return w,cert,p,stats


def oracle_audit():
    fixture=((1,),(2,),(3,),(4,),(5,6),(1,2),(2,4),(1,4))
    cases=queries=sym=submod=strict=0
    for mask in range(256):
        scopes=tuple(s for i,s in enumerate(fixture) if mask&(1<<i))
        if len(scopes)>5:
            continue
        o=Oracle(scopes)
        c=tuple(o(x) for x in range(o.full+1))
        assert c[0]==c[-1]==0
        for x in range(o.full+1):
            assert c[x]>=0 and c[x]==c[o.full^x]
            assert c[x]==len(intersection(o.space(x),o.space(o.full^x),3))
            queries+=1
            sym+=1
            for y in range(o.full+1):
                delta=c[x]+c[y]-c[x|y]-c[x&y]
                assert delta>=0
                submod+=1
                strict+=delta>0
        cases+=1
    assert (cases,queries,sym,submod,strict)==(219,3489,3489,79329,34572)
    print('F038_CONNECTIVITY_ORACLE_OK cases=219 cuts=3489 symmetry=3489 '
          'submodularity=79329 strict=34572')


def comb_audit():
    yes=no=inconsistent=checks=0
    totals=[0]*6
    for mask in range(4096):
        f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
        rows,rest=extract(f)
        tree=comb([1<<i for i in reversed(range(len(rest)))])
        w,cert,p,stats=run(f,3,tree)
        models=tuple(x for x in range(8) if satisfies(f,x))
        assert (w is not None)==bool(models)
        yes+=bool(models)
        no+=not models
        if w is None:
            assert verify_negative(f,3,rows,rest,tree,cert)
        else:
            assert w in models
        if p is None:
            inconsistent+=1
            continue
        forms,db,nodes,width=p
        free=span(a for a,b in forms)
        for node,table in zip(nodes,cert[1]):
            subset,_,s,_=node
            want=set()
            for z in range(1<<len(free)):
                t=lift(equations(free,z))
                assert t is not None
                if local(db,forms,subset,t):
                    want.add(signature(t,s))
                checks+=1
            assert set(table)==want
        for i,v in enumerate(stats):
            totals[i]=max(totals[i],v) if i==5 else totals[i]+v
    assert (yes,no,inconsistent,*totals,checks)==(
        1360,2736,2384,7860,3074,11483,4000,11676,3,18496)
    print('F038_ARBITRARY_TREE_OK formulas=4096 sat=1360 unsat=2736 '
          'inconsistent=2384 nodes=7860 joins=3074 pairs=11483 compatible=4000 '
          'entries=11676 max_width=3 projection_checks=18496')


def cycle_audit():
    invalid=budget_fail=corrupt=0
    for m in (3,4,7,8,15,16,31,32):
        f,n=cycle(m)
        f=tuple(c for c in f if len(c)==2)+tuple(
            c for c in f if len(c)==3 and c[0]>0)+tuple(
            c for c in f if len(c)==3 and c[0]<0)
        rows,rest=extract(f)
        forms,bad=coordinate_forms(rows,n)
        assert forms is not None and bad is None
        scopes=tuple(span(forms[abs(l)-1][0] for l in f[i]) for i in rest)
        tree=discover_cycle(scopes,n)
        assert tree is not None
        w,cert,p,stats=run(f,n,tree,2)
        assert stats[-1]==2 and (w is not None)==(m%2==0)
        for broken in (1,(1,1)):
            try:
                run(f,n,broken,2)
            except ValueError:
                invalid+=1
            else:
                raise AssertionError('malformed tree accepted')
        try:
            run(f,n,balanced([1<<i for i in range(len(rest))]),2)
        except ValueError:
            budget_fail+=1
        else:
            raise AssertionError('excess width accepted')
        if w is None:
            assert verify_negative(f,n,rows,rest,tree,cert,2)
            data=list(cert[1])
            assert data[0]
            data[0]=data[0][1:]
            assert not verify_negative(f,n,rows,rest,tree,('tables',tuple(data)),2)
            corrupt+=1
    assert (invalid,budget_fail,corrupt)==(16,8,4)
    print('F038_DISCOVERY_EXECUTION_OK cycles=8 sat=4 unsat=4 width_each=2 '
          'malformed_rejected=16 budget_rejected=8 corrupt_rejected=4')


if __name__=='__main__':
    oracle_audit()
    comb_audit()
    cycle_audit()
