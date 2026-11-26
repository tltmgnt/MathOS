"""Witness-separated reflection on diamond implication pools; exact proof restriction."""
import json
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research import f038_reflection_transfer as R

PLAN='docs/research/tga-universal/f038-mrax-reflection-restriction.json'


def diamond(k):
    require(type(k) is int and k>=1,'positive chain length required')
    n=3*k+1
    F=[(1,),(-(k+1),)]
    for i in range(k):
        a=k+2+2*i
        b=a+1
        F.extend(R.norm(c) for c in ((-(i+1),a),(-a,i+2),(-(i+1),b),(-b,i+2)))
    return n,tuple(F)


def encode(k):
    n,F=diamond(k)
    m=len(F)
    p=tuple(n+i+1 for i in range(m))
    guard=tuple(R.norm((-p[i],)+c) for i,c in enumerate(F))
    gates=[]
    outputs=[(p[0],),(p[1],)]
    for i in range(k):
        a,b,q=(n+m+3*i+j for j in (1,2,3))
        for t,j in ((a,2+4*i),(b,4+4*i)):
            u,v=p[j:j+2]
            gates.extend(R.norm(c) for c in ((-t,u),(-t,v),(t,-u,-v)))
        gates.extend(R.norm(c) for c in ((-a,q),(-b,q),(-q,a,b)))
        outputs.append((q,))
    return n,F,p,guard+tuple(gates)+tuple(outputs),tuple(gates),tuple(outputs)


def extension(k,mask):
    n,F,p,H,gates,outputs=encode(k)
    w=mask<<n
    for i in range(k):
        a,b,q=(n+len(F)+3*i+j for j in (1,2,3))
        x=(mask>>(2+4*i)&3)==3
        y=(mask>>(4+4*i)&3)==3
        w|=(int(x)<<(a-1))|(int(y)<<(b-1))|(int(x or y)<<(q-1))
    return w


def rejects(k,mask):
    return mask&3==3 and all((mask>>(2+4*i)&3)==3 or
                             (mask>>(4+4*i)&3)==3 for i in range(k))


def source(k,mask):
    n,F=diamond(k)
    return tuple(c for i,c in enumerate(F) if mask>>i&1)


def proof(k):
    n,F,p,H,gates,outputs=encode(k)
    index={c:i for i,c in enumerate(H)}
    out=[]
    def ax(c):
        c=R.norm(c)
        require(c in index,'missing axiom')
        out.append((c,('ax',index[c])))
        return len(out)-1
    def res(i,j,v):
        c=R.resolve(out[i][0],out[j][0],v)
        out.append((c,('res',i,j,v)))
        return len(out)-1
    cur=res(ax((p[0],)),ax((-p[0],1)),p[0])
    end=res(ax((p[1],)),ax((-p[1],-(k+1))),p[1])
    for i in range(k):
        a,b,q=(n+len(F)+3*i+j for j in (1,2,3))
        branches=[]
        for t,j,v in ((a,2+4*i,k+2+2*i),(b,4+4*i,k+3+2*i)):
            l=res(ax((-t,p[j])),ax((-p[j],-(i+1),v)),p[j])
            r=res(ax((-t,p[j+1])),ax((-p[j+1],-v,i+2)),p[j+1])
            mid=res(l,r,v)
            branches.append(res(cur,mid,i+1))
        choice=res(ax((q,)),ax((-q,a,b)),q)
        one=res(choice,branches[0],a)
        cur=res(one,branches[1],b)
    res(cur,end,k+1)
    out=tuple(out)
    require(len(out)==7+21*k,'unexpected reflection proof line count')
    require(R.width(out)<=3,'reflection proof width exceeded')
    require(R.verify(H,out),'reflection proof replay failed')
    return out


def specialize(k,mask,pi):
    n,F,p,H,gates,outputs=encode(k)
    w=extension(k,mask)
    require(rejects(k,mask) and R.sat(gates+outputs,w),'not a rejecting computation')
    pins=tuple(i if w>>(i-1)&1 else -i for i in range(n+1,n+len(F)+3*k+1))
    G,q=R.restrict(H,pi,pins)
    require(G==source(k,mask) and R.verify(G,q) and len(q)<=len(pi)
            and R.width(q)<=R.width(pi),'bad specialization')
    return q


def small():
    result=[]
    for k in range(1,4):
        n,F,p,H,gates,outputs=encode(k)
        pi=proof(k)
        rejected=other=minimal=checks=models=0
        for mask in range(1<<len(F)):
            w=extension(k,mask)
            yes=rejects(k,mask)
            require(R.sat(gates,w) and R.sat(outputs,w)==yes,'gate mismatch')
            if k==1:
                for z in range(1<<(3*k)):
                    v=(mask<<n)|(z<<(n+len(F)))
                    require(R.sat(gates,v)==(v==w),'nonunique gate extension')
            G=source(k,mask)
            if k<=2:
                count=0
                for x in range(1<<n):
                    good=R.sat(G,x)
                    require(R.sat(H,w|x)==(yes and good),'reflection model mismatch')
                    count+=good
                    checks+=1
                require(yes==(count==0),'rejection mismatch')
                models+=count
            if yes:
                specialize(k,mask,pi)
                rejected+=1
                minimal+=all(not rejects(k,mask^(1<<i)) for i in range(len(F)) if mask>>i&1)
            else:
                other+=1
        result.append([k,1<<len(F),rejected,other,minimal,checks,models,len(pi)])
    return result


def large():
    result=[]
    for k in (8,16,32):
        n,F,p,H,gates,outputs=encode(k)
        pi=proof(k)
        mask=3|sum(3<<(2+4*i) for i in range(k))
        specialize(k,mask,pi)
        require(all(not rejects(k,mask^(1<<i)) for i in range(len(F)) if mask>>i&1),
                'selected path not minimal')
        result.append([k,1<<k,len(pi)])
    return result


def controls():
    n,F,p,H,gates,outputs=encode(1)
    pi=proof(1)
    require(not R.verify(H,pi[:-1]),'unfinished proof accepted')
    require(not R.verify(H,pi[:-1]+(((),('res',0,len(pi),2)),)),'forward reference accepted')
    try:
        specialize(1,0,pi)
    except ValueError:
        pass
    else:
        raise ValueError('nonrejecting input specialized')
    return 3


def audit():
    result={'small':small(),'large':large(),'controls':controls()}
    print('F038_MRAX_REFLECTION_RESTRICTION_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
