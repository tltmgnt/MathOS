"""Guarded width-three resolution DAG and exact supplied-interface private blocks."""
import copy
import json
from pathlib import Path
from mathos.research.f038_rule_certification import ROWS,satisfies
from mathos.research import f038_hybrid_affine as H
from mathos.research import f038_guarded_affine as G
from mathos.research.f038_guarded_learning import base_db,canonical,mode
from mathos.research.f038_affine_recovery import cycle_source
from mathos.research.f038_resolution_certificate import split_cube,encode
from mathos.research.f038_mrax_cycle import run_mrax,gate

PLAN='docs/research/tga-universal/f038-mrax-bounded-inference.json'


def require(v,msg='regression failed'):
    if not v:
        raise ValueError(msg)


def originals(f):
    out=[]
    seen=set()
    for i,c in enumerate(f):
        d=canonical(c)
        require(d is not None and len(d)<=3,'normalized width-three source required')
        if d not in seen:
            out.append((d,(i,),()))
            seen.add(d)
    return tuple(out)


def resolvent(a,b,p):
    if p not in a or -p not in b:
        return None
    return canonical(tuple(l for l in a if l!=p)+tuple(l for l in b if l!=-p))


def pairs(db,i):
    a=db[i][0]
    for j in range(i):
        b=db[j][0]
        for p in a:
            if -p in b:
                c=resolvent(a,b,p)
                if c is not None and len(c)<=3:
                    yield j,p,c


def close(f,one_round=False):
    db=list(originals(f))
    seen={r[0] for r in db}
    start=len(db)
    i=0
    while i<(start if one_round else len(db)):
        for j,p,c in pairs(db,i):
            if c not in seen:
                db.append((c,tuple(sorted(set(db[i][1]+db[j][1]))),(i,j,p)))
                seen.add(c)
        i+=1
    return tuple(db)


def verify_closure(f,n,db,one_round=False):
    try:
        start=originals(f)
        if tuple(db[:len(start)])!=start or len(db)<len(start):
            return False
        seen=set()
        for k,(c,s,parents) in enumerate(db):
            if c in seen or canonical(c)!=c or any(not 1<=abs(l)<=n for l in c):
                return False
            seen.add(c)
            if k<len(start):
                continue
            i,j,p=parents
            if not 0<=j<i<k or (one_round and i>=len(start)):
                return False
            if c!=resolvent(db[i][0],db[j][0],p) or len(c)>3:
                return False
            if s!=tuple(sorted(set(db[i][1]+db[j][1]))):
                return False
        return all(c in seen for i in range(len(start) if one_round else len(db))
                   for j,p,c in pairs(db,i))
    except (ValueError,TypeError,IndexError,KeyError):
        return False


def guarded_rows(f,n,db,one_round=False):
    require(verify_closure(f,n,db,one_round),'invalid resolution certificate')
    clauses=tuple(r[0] for r in db)
    rows,rest=H.extract(clauses)
    require(H.verify_partition(clauses,rows,rest),'invalid parity extraction')
    return tuple(sorted((a,b,tuple(sorted({n+j+1 for i in ids for j in db[i][1]})))
                        for a,b,ids in rows))


class Session(G.Session):
    def __init__(self,f,n,db,one_round=False):
        self.base,self.N=base_db(f,n)
        self.guarded=guarded_rows(f,n,db,one_round)
        self.db=list(self.base)
        self.index={canonical(c):i for i,c in enumerate(self.base)}
        self.reused=0
        self.branches=0


def block_project(f,n,interface,h):
    I=set(interface)
    require(all(1<=v<=n for v in I),'invalid interface')
    parent={v:v for v in range(1,n+1) if v not in I}
    def root(v):
        while parent[v]!=v:
            v=parent[v]
        return v
    for c in f:
        V=sorted(set(map(abs,c))-I)
        for v in V[1:]:
            a,b=root(V[0]),root(v)
            if a!=b:
                parent[max(a,b)]=min(a,b)
    groups={}
    for j,c in enumerate(f):
        V=sorted(set(map(abs,c))-I)
        key=(0,root(V[0])) if V else (1,j)
        groups.setdefault(key,[]).append(j)
    out=[]
    for ids in groups.values():
        scope=tuple(sorted({abs(l) for j in ids for l in f[j]}))
        if len(scope)>h:
            return None
        boundary=tuple(v for v in scope if v in I)
        private=sum(1<<(v-1) for v in scope if v not in I)
        table={}
        for z in range(1<<len(scope)):
            w=sum(1<<(v-1) for i,v in enumerate(scope) if z>>i&1)
            if satisfies(tuple(f[j] for j in ids),w):
                p=sum(((w>>(v-1))&1)<<i for i,v in enumerate(boundary))
                table.setdefault(p,w&private)
        out.append((tuple(ids),boundary,tuple(sorted(table.items()))))
    return tuple(out)


def lift_blocks(f,n,interface,w,blocks,h):
    if blocks is None or blocks!=block_project(f,n,interface,h):
        return None
    I=sum(1<<(v-1) for v in set(interface))
    w&=I
    for ids,B,table in blocks:
        z=sum(((w>>(v-1))&1)<<i for i,v in enumerate(B))
        rows=dict(table)
        if z not in rows:
            return None
        w|=rows[z]
    require(satisfies(f,w),'invalid glued witness')
    return w


def fixture(rows,n,run_queries):
    formulas=derived=records=clause_checks=row_count=row_checks=queries=yes=no=0
    for mask in range(1<<len(rows)):
        f=tuple(c for j,c in enumerate(rows) if mask>>j&1)
        db=close(f)
        require(verify_closure(f,n,db))
        g=guarded_rows(f,n,db)
        for c,ids,_ in db:
            for w in range(1<<n):
                require(not satisfies(tuple(f[i] for i in ids),w) or satisfies((c,),w))
                clause_checks+=1
        for a,b,guards in g:
            for w in range(1<<n):
                require(not satisfies(tuple(f[i-n-1] for i in guards),w) or H.parity(w&a)==b)
                row_checks+=1
        formulas+=1
        records+=len(db)
        derived+=len(db)-len(originals(f))
        row_count+=len(g)
        if run_queries:
            S=Session(f,n,db)
            checked=list(S.base)
        for i in range(-1,len(f)):
            A=mode(f,n,i)
            ms=tuple(w for w in range(1<<n) if all(
                satisfies((c,),w)==(j!=i) for j,c in enumerate(f)))
            for pin in ((),)+tuple((l,) for v in range(1,n+1) for l in (-v,v)):
                want=any(satisfies(tuple((l,) for l in pin),w) for w in ms)
                if run_queries:
                    result=S.ask(A+pin)
                    require(G.check_step(checked,S.N,S.guarded,A+pin,result))
                    require((result[1] is not None)==want)
                queries+=1
                yes+=want
                no+=not want
        if run_queries:
            require(checked==S.db)
    return [formulas,derived,records,clause_checks,row_count,row_checks,queries,yes,no]


def families():
    out=[]
    for d in (2,3,4):
        nv,edges=split_cube(d)
        z=len(edges)+1
        f=encode(nv,edges,1)
        hard,n=cycle_source(f,z)
        require(not G.source(hard,n)[2])
        db=close(hard,True)
        require(verify_closure(hard,n,db,True))
        require({canonical(c) for c in f}<={r[0] for r in db})
        S=Session(hard,n,db,True)
        interface_rows=tuple((a,b,()) for a,b,g in S.guarded if a<(1<<z))
        require(len(interface_rows)==nv)
        A=mode(hard,n,-1)
        checked=list(S.base)
        wrong=A+(-z,)
        r=S.ask(wrong)
        require(r[1] is None and len(r[0])==1 and S.branches==0)
        require(r[0][0][1][-1][0]=='x' and G.check_step(checked,S.N,S.guarded,wrong,r))
        I=tuple(range(1,z+1))
        blocks=block_project(hard,n,I,6)
        require(blocks is not None and len(blocks)==len(f))
        for ids,B,table in blocks:
            require(len(ids)==9 and ids[0]%9==0)
            C=f[ids[0]//9]
            require(set(B)==set(map(abs,C)))
            expected={p for p in range(1<<len(B)) if satisfies((C,),
                      sum(1<<(v-1) for j,v in enumerate(B) if p>>j&1))}
            require(set(dict(table))==expected)
        basis,bad=H.reduce(interface_rows,1<<(z-1),1<<(z-1))
        require(basis is not None)
        w=1<<(z-1)
        for bit,(a,b,p) in basis.items():
            if b:
                w|=bit
        w=lift_blocks(hard,n,I,w,blocks,6)
        require(w is not None)
        w|=((1<<len(hard))-1)<<n
        require(G.check_step(checked,S.N,S.guarded,A+(z,),((),w,None)))
        out.append([d,len(db)-len(originals(hard)),len(S.guarded),len(interface_rows),len(blocks)])
    return out


def controls():
    f=((1,3),(-3,2))
    db=close(f)
    require(verify_closure(f,3,db) and len(db)==3)
    bad=list(db)
    bad[-1]=(bad[-1][0],(),bad[-1][2])
    require(not verify_closure(f,3,tuple(bad)))
    require(not verify_closure(f,3,db[:-1]))
    require(block_project(f,3,(),2) is None)
    plan=json.loads(Path(PLAN).read_text())
    p=copy.deepcopy(plan)
    p['mrax']['critic']['objections']=[]
    require(gate(p)=='PROCEED_RESTRICTED')
    p['mrax']['critic']['objections']='not an array'
    try:
        gate(p)
    except ValueError:
        pass
    else:
        raise ValueError('invalid schema passed')
    p=copy.deepcopy(plan)
    p['mrax']['planner']['target_id']='cook_levin'
    try:
        gate(p)
    except ValueError:
        pass
    else:
        raise ValueError('closed target passed')
    p=copy.deepcopy(plan)
    p['mrax']['critic']['recommended_disposition']='revise'
    require(gate(p)=='STOP_CRITIC')
    p=copy.deepcopy(plan)
    p['mrax']['verify']['verdict']='rejected'
    require(gate(p)=='STOP_VERIFY')
    return 8


def audit():
    full=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3)) for w in range(8))
    binary=((-1,),(1,),(-2,),(2,),(-1,-2),(-1,2),(1,-2),(1,2))
    result={'primary':fixture(ROWS,3,False),'full':fixture(full,3,True),
            'binary':fixture(binary,2,True),'families':families(),'controls':controls()}
    print('F038_MRAX_BOUNDED_INFERENCE_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
