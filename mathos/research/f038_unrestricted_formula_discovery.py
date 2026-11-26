"""Formula-only discovery: explicit model recovery and exact original output clocks."""
import json
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import encoded, valid, tape_run, encode_tm
from mathos.research.f038_unrestricted_diagonal_discovery import (
    clocked, counterexample_fixture, writer, pack, unpack, pin_selectors)

PLAN='docs/research/tga-universal/f038-unrestricted-formula-discovery.json'


def recover(C,n,p):
    """No witness input: direct finite exhaustive recovery with charged attempts."""
    require(type(n) is int and n>=1 and type(p) is int and 0<=p<1<<len(C),
            'invalid formula-only selector')
    for x in range(1<<n):
        if valid(C,n,p,x):
            return x,x+1
    return None,1<<n


def dimensions(n):
    require(type(n) is int and n>=1,'invalid variable count')
    return n+1+2*n+4*comb(n,2)+8*comb(n,3)


def recovery():
    rows=[]
    for n in (1,2,3):
        C=pool(n)
        N=len(C)
        mask=(1<<N)-1
        P=range(1<<N) if n<3 else [0,mask]+[((i+1)*2654435761)&mask for i in range(256)]
        st=[n,len(P),0,0,0,0,0,0]
        for p in P:
            x,attempts=recover(C,n,p)
            W=[w for w in range(1<<n) if valid(C,n,p,w)]
            require(x==(W[0] if W else None),'formula-only recovery mismatch')
            require(len(encoded(n,p,C))==dimensions(n),'explicit length mismatch')
            st[2]+=x is not None
            st[3]+=x is None
            st[4]+=attempts
            st[7]+=len(W)
            if x is not None:
                d,T=writer(n,x)
                require(tape_run(C,n,p,d,2*n)==x and
                        tape_run(C,n,p,d,2*n-1) is None and valid(C,n,p,x),
                        'recovered witness output failed')
                st[5]+=x
                st[6]+=2*n
        rows.append(st)
    return rows


def formula_only_fixture(d,c):
    """A finite fixture, not a total generator for arbitrary descriptions."""
    C,P=pin_selectors()
    for p in P:
        x,_=recover(C,3,p)
        require(x is not None,'fixture not satisfiable')
        if not valid(C,3,p,clocked(C,3,p,d,c,1)):
            return p
    return None


def controls():
    for n in range(1,4097):
        L=dimensions(n)
        require(2*L>=n**3,'cubic output bound failed')
        require(L>dimensions(n-1) if n>1 else L==4,'nonincreasing input size')
    # The two binary clock families have the same descriptor size up to order.
    d=encode_tm([(1,1,0)]*3,1)
    for h in (1,2,4,16,64,256,1024):
        big='1'+'0'*h
        a=(d,big,'1')
        b=(d,'1',big)
        A,B=pack(a),pack(b)
        require(len(A)==len(B) and unpack(A)==a and unpack(B)==b,
                'binary parameter encoding mismatch')
    C,P=pin_selectors()
    p=formula_only_fixture(d,1)
    require(type(p) is int and p==counterexample_fixture(d,1)[0],
            'formula-only fixture failed')
    x,_=recover(C,3,p)
    d2,T=writer(3,x)
    require(not valid(C,3,p,clocked(C,3,p,d,1,1)) and
            valid(C,3,p,clocked(C,3,p,d2,1,1)),
            'reconstructed witness not verified')
    try:
        recover(C,3,1<<len(C))
    except ValueError:
        pass
    else:
        raise ValueError('invalid selector accepted')
    return 4


def audit():
    result={'controls':controls(),'recovery':recovery()}
    print('F038_UNRESTRICTED_FORMULA_DISCOVERY_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
