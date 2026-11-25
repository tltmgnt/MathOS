"""Symbolic interface DAG and logarithmic-width certification reduction."""
from mathos.research.f038_factored_interface import BAGS, CHILDREN, ROWS, mask_of, vals
from mathos.research.f038_rule_certification import ROWS as MATRIX
from mathos.research.f038_horn_cover import satisfies
from mathos.research.f038_monotone_choice import sat, restrict


def compile_dag(bags, children, fs, u):
    gates=[]
    def make(op,args):
        gates.append((op,tuple(args)))
        return len(gates)-1
    zero=make('const',(False,))
    one=make('const',(True,))
    tables=[None]*len(bags)
    for i in reversed(range(len(bags))):
        b=bags[i]
        t={}
        for a in vals(b):
            terms=[one if satisfies(fs[i],a) else zero]
            bits=b&u
            while bits:
                bit=bits&-bits
                bits^=bit
                terms.append(make('lit',(bit,bool(a&bit))))
            for j in children[i]:
                sep=b&bags[j]
                terms.append(make('or',(g for d,g in tables[j].items()
                                        if not (a^d)&sep)))
            t[a]=make('and',terms)
        tables[i]=t
    root=make('or',tables[0].values())
    return gates,tables,root


def evaluate(gates,x):
    ev=[]
    for op,args in gates:
        if op=='const':
            v=args[0]
        elif op=='lit':
            v=bool(x&args[0])==args[1]
        elif op=='or':
            v=any(ev[g] for g in args)
        else:
            assert op=='and'
            v=all(ev[g] for g in args)
        ev.append(v)
    return ev


def subsets(rows,mask):
    return tuple(c for i,c in enumerate(rows) if mask&(1<<i))


def tree_audit():
    bags=tuple(mask_of(b) for b in BAGS)
    sub=list(bags)
    for i in reversed(range(4)):
        for j in CHILDREN[i]:
            sub[i]|=sub[j]
    families=params=checks=total=maximum=0
    for mask in range(4096):
        fs=[]
        bit=0
        for rs in ROWS:
            fs.append(subsets(rs,mask>>bit))
            bit+=len(rs)
        assert bit==12
        sf=list(fs)
        for i in reversed(range(4)):
            for j in CHILDREN[i]:
                sf[i]+=sf[j]
        models=[tuple(w for w in range(64) if satisfies(f,w)) for f in sf]
        for u in (21,42):
            gates,tables,root=compile_dag(bags,CHILDREN,fs,u)
            valid=True
            for x in vals(u):
                ev=evaluate(gates,x)
                for i,b in enumerate(bags):
                    rows={w&b for w in models[i] if not (w^x)&sub[i]&u}
                    for a,g in tables[i].items():
                        assert ev[g]==(a in rows)
                        checks+=1
                want=any(not (w^x)&u for w in models[0])
                assert ev[root]==want
                valid &= want
                params+=1
            families+=1
            total+=valid
            maximum=max(maximum,len(gates))
    assert (families,params,checks,total,maximum)==(8192,65536,1835008,592,91)
    print(f'F038_SYMBOLIC_INTERFACE_OK families={families} parameters={params} '
          f'row_checks={checks} total={total} max_nodes={maximum}')


def address_reduction(d,n):
    k=max(1,(max(1,len(d))-1).bit_length())
    p=tuple(range(n+1,n+k+1))
    base=mask_of(p)
    bags=[base]
    children=[[]]
    fs=[[]]
    top=n+k

    def node(parent,b):
        i=len(bags)
        bags.append(b)
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
            c=(row[0],row[1],top)
            child=node(parent,scope|prev|1<<(top-1))
            fs[child].append(c)
            parent=child
            prev=1<<(top-1)
            row=(-top,*row[2:])
        child=node(parent,scope|prev)
        fs[child].append(row)

    for j in range(1<<k):
        mismatch=tuple(-v if j&(1<<i) else v for i,v in enumerate(p))
        if j>=len(d):
            add(mismatch,0)
        else:
            for l in d[j]:
                add(mismatch+(-l,),groups[abs(l)])
    return top,p,tuple(bags),tuple(tuple(c) for c in children),tuple(tuple(f) for f in fs)


def check_decomposition(top,bags,children,fs):
    edges=[(i,j) for i,cs in enumerate(children) for j in cs]
    assert sorted(j for i,j in edges)==list(range(1,len(bags)))
    assert all(i<j for i,j in edges)
    for b,f in zip(bags,fs):
        assert all(1<=len(c)<=3 and all(b&(1<<(abs(l)-1)) for l in c) for c in f)
    for v in range(top):
        bit=1<<v
        ids={i for i,b in enumerate(bags) if b&bit}
        assert ids
        assert sum(i in ids and j in ids for i,j in edges)==len(ids)-1


def reduction_audit():
    formulas=unsat=source_sat=params=feasible=checks=max_b=max_v=max_c=0
    n=3
    u=(1<<n)-1
    for mask in range(1<<len(MATRIX)):
        d=subsets(MATRIX,mask)
        top,p,bags,children,fs=address_reduction(d,n)
        check_decomposition(top,bags,children,fs)
        assert max(b.bit_count() for b in bags)<=len(p)+3
        f=tuple(c for local in fs for c in local)
        gates,_,root=compile_dag(bags,children,fs,u)
        total=True
        for x in range(1<<n):
            g=restrict(f,{i+1:bool(x&(1<<i)) for i in range(n)})
            found=False
            for j in range(1<<len(p)):
                want=j<len(d) and not satisfies((d[j],),x)
                got=sat(restrict(g,{v:bool(j&(1<<i)) for i,v in enumerate(p)}))
                assert got==want
                found|=got
                checks+=1
            assert found== (not satisfies(d,x))
            assert evaluate(gates,x)[root]==found
            total &= found
            params+=1
            feasible+=found
        formulas+=1
        unsat+=total
        source_sat+=not total
        max_b=max(max_b,max(b.bit_count() for b in bags))
        max_v=max(max_v,top)
        max_c=max(max_c,len(f))
    assert (formulas,unsat,source_sat,params,feasible,checks,max_b,max_v,max_c)==(
        4096,2736,1360,32768,30464,254608,7,55,74)
    print(f'F038_LOG_WIDTH_CERTIFICATION_OK formulas={formulas} unsat={unsat} '
          f'sat={source_sat} parameters={params} feasible={feasible} '
          f'address_checks={checks} max_bag={max_b} max_variables={max_v} max_clauses={max_c}')


if __name__=='__main__':
    tree_audit()
    reduction_audit()
