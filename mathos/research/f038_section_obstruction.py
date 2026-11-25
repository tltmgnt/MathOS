"""Section-preserving representation obstruction and explicit nonlinear decoder escape."""
import json
from itertools import product,combinations
from mathos.research.f038_bounded_inference import require
from mathos.research import f038_mixed_polymorphisms as M
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-section-obstruction.json'
D=tuple(range(4))
NAE=tuple(range(1,7))
C=(0,3,2,1)


def block_op(T,x,y,z):
    return sum(M.op(t,x>>i&1,y>>i&1,z>>i&1)<<i for i,t in enumerate(T))


def induced(dec,reps,T):
    require(len(dec)==1<<len(T) and tuple(dec[r] for r in reps)==(0,1))
    a=dec[block_op(T,reps[0],reps[0],reps[1])]
    b=dec[block_op(T,reps[0],reps[1],reps[1])]
    return C.index(a+2*b)


def section_audit():
    configs=checks=violations=types=0
    for mask in range(1,15):
        dec=tuple(mask>>i&1 for i in D)
        for reps in product(D,repeat=2):
            if tuple(dec[r] for r in reps)!=(0,1):
                continue
            for T in product(D,repeat=2):
                label=induced(dec,reps,T)
                configs+=1
                for a,b,c in product((0,1),repeat=3):
                    require(dec[block_op(T,reps[a],reps[b],reps[c])]==M.op(label,a,b,c))
                    checks+=1
                require(not M.closed(NAE,(label,)*3))
                violations+=1
    for T in product(D,repeat=3):
        require(not M.closed(NAE,T))
        types+=1
    return [configs,checks,violations,types]


def cover_audit():
    counts=[0]*7
    for mask in range(64):
        P=tuple(i for i in NAE if mask>>(i-1)&1)
        if any(M.closed(P,T) for T in product(D,repeat=3)):
            counts[len(P)]+=1
    points=lower=0
    for m in range(1,6):
        cube=tuple(product(range(6),repeat=m))
        for p in cube:
            require(any(all(a!=j for a in p) for j in range(m+1)))
            points+=1
        if m<=2:
            for k in range(1,m+1):
                for charts in combinations(cube,k):
                    p=tuple(charts[i][i] if i<k else 0 for i in range(m))
                    require(all(any(a==b for a,b in zip(p,c)) for c in charts))
                    lower+=1
    return counts+[points,lower]


def decode(t):
    u,v=t&1,t>>1&1
    return (u,v,u^v,u)[t>>2]


def packed_pattern(t):
    return decode(t)|(decode(t^1)<<1)|(decode(t^2)<<2)


def gadget(a,b,c):
    out=[]
    for j in range(4):
        for block,mask in ((b,1),(c,2)):
            I=tuple(sorted((4*a+j,4*block+j)))
            out.append((I,(1,2) if mask>>j&1 else (0,3)))
    return tuple(out)


def source_ok(w,atoms):
    return all(M.project(w,I) in NAE for I in atoms)


def gadget_audit():
    S=tuple(sorted(t|((t^1)<<4)|((t^2)<<8) for t in range(16)))
    require(M.closed(S,(3,)*12))
    R=gadget(0,1,2)
    require(tuple(w for w in range(1<<12) if M.evaluate(R,w))==S)
    mult=[0]*8
    for t in range(16):
        mult[packed_pattern(t)]+=1
    require(tuple(i for i,m in enumerate(mult) if m)==NAE)
    pairs=tuple((a,b) for a,b in product(range(16),repeat=2)
                if decode(a)==0 and decode(b)==1)
    hist=[0]*7
    for A,B,C in product(pairs,repeat=3):
        count=0
        for p in NAE:
            t=A[p&1]
            count+=B[p>>1&1]==(t^1) and C[p>>2&1]==(t^2)
        hist[count]+=1
    require(len(pairs)==64 and hist[-1]==0)
    r=M.solve(R,12,(3,)*12)
    require(r[0]=='SAT' and M.verify(R,12,(3,)*12,r))
    w=r[1]
    require(sum(decode(w>>(4*i)&15)<<i for i in range(3)) in NAE)
    atoms=((0,1,2),(0,2,3))
    source_models=sum(source_ok(w,atoms) for w in range(16))
    require(source_models and source_ok(6,atoms))
    R2=R+gadget(0,2,3)
    r2=M.solve(R2,16,(3,)*16)
    require(r2[0]=='UNSAT' and M.verify(R2,16,(3,)*16,r2))
    return {'multiplicities':mult,'section_histogram':hist,'source_models':source_models,
            'typed_single_sat':1,'typed_double_unsat':1}


def audit():
    result={'sections':section_audit(),'charts':cover_audit(),'gadget':gadget_audit()}
    print('F038_MRAX_SECTION_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
