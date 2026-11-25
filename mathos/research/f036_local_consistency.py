"""Exact finite audit of a scalable local-consistency obstruction.

Each pigeon has k placement variables and k prefix OR-gate variables.
All retained scope assignments come from injective placements of the
pigeons touched by that scope. They need not extend to a global model.
"""
from itertools import combinations, permutations

def instance(k):
    variables = [(p,kind,j) for p in range(k+1)
                 for kind in ("x","s") for j in range(k)]
    def ident(p,kind,j):
        return 1+p*2*k+(k if kind=="s" else 0)+j
    rows=[]
    for p in range(k+1):
        a,b=ident(p,"x",0),ident(p,"s",0)
        rows.extend([(-a,b),(a,-b)])
        for j in range(1,k):
            u,v,t=ident(p,"s",j-1),ident(p,"x",j),ident(p,"s",j)
            rows.extend([(-u,t),(-v,t),(u,v,-t)])
        rows.append((ident(p,"s",k-1),))
    for p,q in combinations(range(k+1),2):
        for j in range(k):
            rows.append((-ident(p,"x",j),-ident(q,"x",j)))
    return variables,rows

def values(variables,scope,k):
    touched=sorted({variables[v][0] for v in scope})
    out=set()
    for places in permutations(range(k),len(touched)):
        placement=dict(zip(touched,places))
        a=0
        for i,v in enumerate(scope):
            p,kind,j=variables[v]
            h=placement[p]
            if (h==j if kind=="x" else h<=j):
                a|=1<<i
        out.add(a)
    return out

def project(scope,a,sub):
    return sum(((a>>scope.index(v))&1)<<i for i,v in enumerate(sub))

def audit(k):
    variables,rows=instance(k)
    scopes=[s for j in range(k+1)
            for s in combinations(range(len(variables)),j)]
    table={}
    states=local=restrictions=extensions=0
    for s in scopes:
        vs=values(variables,s,k)
        assert vs
        table[s]=vs
        states+=len(vs)
        contained=[c for c in rows if all(abs(l)-1 in s for l in c)]
        for a in vs:
            for c in contained:
                local+=1
                assert any(bool(a&(1<<s.index(abs(l)-1)))==(l>0) for l in c)
    for s,vs in table.items():
        for i in range(len(s)):
            sub=s[:i]+s[i+1:]
            for a in vs:
                restrictions+=1
                assert project(s,a,sub) in table[sub]
        if len(s)==k:
            continue
        for v in range(len(variables)):
            if v in s:
                continue
            sup=tuple(sorted((*s,v)))
            projected={project(sup,a,s) for a in table[sup]}
            for a in vs:
                extensions+=1
                assert a in projected
    return len(variables),len(rows),len(scopes),states,local,restrictions,extensions

if __name__=="__main__":
    expected={
        2:(12,24,79,151,99,279,243),
        3:(24,54,2325,9061,7002,26268,19164),
        4:(40,100,102091,745326,666455,2924900,1990540),
    }
    for k,e in expected.items():
        result=audit(k)
        assert result==e,(k,result,e)
        print(k,*result)
    print("F036_LOCAL_CONSISTENCY_OK widths=2,3,4")
