"""Exact clocked witness counterexamples: finite interpreter and output-convention audits."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import (
    encoded,valid,encode_tm,decode_tm,tape_run)
from mathos.research.f038_unrestricted_cubic_interval import tables

PLAN='docs/research/tga-universal/f038-unrestricted-diagonal-discovery.json'


def clocked(C,n,p,d,c,e):
    require(type(c) is int and c>=1 and type(e) is int and e>=1 and
            decode_tm(d) is not None,'invalid clocked descriptor')
    L=n+1+len(C)
    return tape_run(C,n,p,d,c*(L+1)**e)


def pin_selectors():
    n=3
    C=pool(n)
    P=[]
    for x in range(8):
        # All seven satisfied signed ternary clauses; exactly one model.
        p=sum(1<<j for j,c in enumerate(C) if len(c)==3 and
              any(bool(x>>(abs(l)-1)&1)==(l>0) for l in c))
        require(p.bit_count()==7 and
                [w for w in range(8) if valid(C,n,p,w)]==[x],'pin model mismatch')
        P.append(p)
    return C,P


def linear():
    n=3
    C,P=pin_selectors()
    rows=[]
    for c in (1,2,4):
        st=[c,0,0,0,0,0,0,0]
        for T in tables():
            d=encode_tm(T,1)
            require(decode_tm(d)==(1,list(T)),'description mismatch')
            W=[]
            for x,p in enumerate(P):
                w=clocked(C,n,p,d,c,1)
                ok=valid(C,n,p,w)
                require(ok==(w==x),'pin acceptance mismatch')
                W.append(w)
                st[2]+=1
                st[3]+=w is not None
                st[4]+=ok
                st[5]+=not ok
            require(len(set(W))==1,'one-state suffix invariance failed')
            failures=sum(x!=w for x,w in enumerate(W))
            require(failures>=7,'no linear counterexample')
            st[1]+=1
            st[6]+=failures>=7
            st[7]+=failures==8
        rows.append(st)
    return rows


def writer(n,w):
    require(type(n) is int and n>=1 and type(w) is int and 0<=w<1<<n,
            'invalid witness writer')
    T=[]
    for i in range(n):
        T.extend([(i+1,(w>>i)&1,1)]*3)
    for i in range(n,2*n):
        T.extend((i+1,a,-1) for a in range(3))
    return encode_tm(T,2*n),T


def writers():
    rows=[]
    for n in range(1,7):
        C=pool(n)
        st=[n,0,0,0,0]
        for w in range(1<<n):
            d,T=writer(n,w)
            require(decode_tm(d)==(2*n,T),'writer encoding failed')
            require(tape_run(C,n,0,d,2*n)==w and
                    tape_run(C,n,0,d,2*n-1) is None,'writer boundary failed')
            st[1]+=1
            st[2]+=2
            st[3]+=len(T)
            st[4]+=w
        rows.append(st)
    return rows


def counterexample_fixture(d,c):
    C,P=pin_selectors()
    for x,p in enumerate(P):
        if not valid(C,3,p,clocked(C,3,p,d,c,1)):
            return p,x
    return None


def pack(parts):
    # Elias-gamma length+1 then the literal component.
    out=''
    for p in parts:
        require(all(x in '01' for x in p),'nonbinary component')
        b=format(len(p)+1,'b')
        out+='0'*(len(b)-1)+b+p
    return out


def unpack(s):
    parts=[]
    i=0
    while i<len(s):
        j=i
        while j<len(s) and s[j]=='0':
            j+=1
        require(j<len(s) and j+(j-i)+1<=len(s),'invalid length')
        end=j+(j-i)+1
        n=int(s[j:end],2)-1
        require(end+n<=len(s),'truncated component')
        parts.append(s[end:end+n])
        i=end+n
    return tuple(parts)


def controls():
    C,P=pin_selectors()
    d=encode_tm([(1,1,0)]*3,1)
    p,x=counterexample_fixture(d,1)
    require(valid(C,3,p,x) and not valid(C,3,p,clocked(C,3,p,d,1,1)),
            'counterexample reconstruction failed')
    d2,T=writer(3,x)
    require(valid(C,3,p,clocked(C,3,p,d2,1,1)),'fixed witness writer failed')
    for h in (1,2,4,16,64,256,1024):
        parts=(d,'1'+'0'*h,'1')
        s=pack(parts)
        require(unpack(s)==parts and len(s)<=sum(map(len,parts))+6*(len(s).bit_length()+1),
                'binary clock tuple length')
    try:
        clocked(C,3,p,d,0,1)
    except ValueError:
        pass
    else:
        raise ValueError('zero clock accepted')
    return 4


def audit():
    result={'linear':linear(),'writers':writers(),'controls':controls()}
    print('F038_UNRESTRICTED_DIAGONAL_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
