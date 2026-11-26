"""Finite cubic gap closure by sound zero-block language overapproximation."""
import json
import subprocess
import tempfile
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_unrestricted_quadratic_stage import length,count
from mathos.research.f038_unrestricted_kraft_crossing import shapes
from mathos.research.f038_unrestricted_cubic_crossing_census import ceil,trace,table

PLAN='docs/research/tga-universal/f038-unrestricted-block-language.json'
CPP=Path('mathos/research/f038_unrestricted_block_language.cpp')


def run(exe,n,cap,c,S):
    rows=[list(map(int,s.split())) for s in subprocess.check_output(
        [str(exe),str(n),str(cap),str(c)],text=True,timeout=120).splitlines()]
    R,V,*J=rows
    H=S['matrix']
    total=(H[1][2],H[2][1],H[2][2])[c]
    require(R[:3]==[n,cap,c] and R[-1]==total and sum(R[3:7])==total
            and sum(V[:4])==R[5],'weighted partition')
    require(all(len(row)==4 and 0<=row[0]<=257 for row in J)
            and [sum(row[i] for row in J) for i in (1,2,3)]==V[1:4],
            'rate partition')
    return [R,V,J]


def charge(K,h,d):
    return K if d==0 else min(K,K-K//d+h-1)


def weight(K,h,d):
    k,r=divmod(charge(K,h,d),h)
    return Fraction(1<<(k+1),2*h-r)


def bound(n,m,records,S):
    L=n+1+2*n*n+8*comb(n,3)
    s=3*(L-1).bit_length()
    g=8*(comb(n-1,3)-comb(n-m,3))-15
    h=g-n
    require(3<=m<=n-3 and h>0 and s==72 and s-3<n and length(4)>s
            and (1<<(s-length(3)))+n<=n+1+2*n*n
            and 2048+n<=n+1+2*n*n,'geometry')
    t=1<<(s-length(2))
    A,B=1<<m,1<<(n-m)
    f,x,y,z,cl,cr,ml,mr=(sum(row[1][i] for row in records) for i in range(8))
    C=cl*A+cr*B
    for l in range(3):
        for rr in range(3):
            if l==0 or rr==0 or l==rr==1:
                C+=S['matrix'][l][rr]*(A+(0 if rr==0 else 2 if rr==2 and l==0 else 1)*B)
    F=count(1)+count(3)+4+S['initial']+S['high']-f-x-y-z
    require(F>=0,'negative fixed count')
    u=Fraction(g*C,h)+g*(ml*A+mr*B)+F
    for _,_,J in records:
        for d,x,y,z in J:
            u+=g*((x*B+z*(A+B))*weight((t+g)//2,h,d)+y*A*weight(t//2,h,d))
    u/=1<<n
    return u,[n,m,g,str(ceil(10**9*u)),str(ceil((1-u)*(1<<n)))]


def alphabets(T):
    L={a for a,w,m in T if a<2 and m==-1}
    R={a for a,w,m in T if a<2 and m==1}
    for _ in range(4):
        states=[(0,a) for a in R]
        seen=set(states)
        l,r=set(),set()
        for s,a in states:
            b,w,m=T[3*a+s]
            if b==2:
                continue
            if m==-1:
                l.add(b)
            if m==1:
                r.add(b)
            for z in R if m==-1 else L if m==1 else (b,):
                if (w,z) not in seen:
                    states.append((w,z))
                    seen.add((w,z))
        L,R=l,r
    return L,R


def accepts(T,L,R,b,d,word):
    """Independent tuple-valued nondeterministic word replay; no DFA graph."""
    saved={(0,)*b}
    for i,a0 in enumerate(word):
        incoming=R if i==0 or d==-1 else L
        h0=0 if i==0 or d==-1 else b-1
        states=[(S,h0,a) for S in saved for a in incoming]
        seen=set(states)
        next_saved=set()
        for S,h,a in states:
            z,w,m=T[3*a+S[h]]
            if z==2:
                continue
            V=S[:h]+(w,)+S[h+1:]
            j=h+m
            if 0<=j<b:
                choices=((V,j,z),)
            elif m==d:
                if z==a0:
                    next_saved.add(V)
                choices=()
            else:
                choices=((V,0 if d==1 else b-1,x) for x in (R if d==1 else L))
            for v in choices:
                if v not in seen:
                    seen.add(v)
                    states.append(v)
        saved=next_saved
        if not saved:
            return False
    return True


def reference():
    st=[0]*6
    for seed in range(256):
        T=table(seed)
        L,R=alphabets(T)
        memo={}
        st[0]+=1
        for a,b in product(range(4),repeat=2):
            S=[1,1,1,1,0,a&1,a>>1]+[0]*24+[b&1,b>>1]
            E=[(x,y,z) for x,y,z in trace(S,4,T,128)[3] if z<2]
            st[1]+=1
            for x,y,z in E:
                if 11<=x<=26 and x!=y:
                    require(z in (L if y<x else R),'actual alphabet violation')
                    st[4]+=1
            for c in range(15,24):
                for d in (-1,1):
                    word=tuple(z for x,y,z in E if (x,y)==((c-1,c) if d==1 else (c,c-1)))
                    if not word:
                        continue
                    st[2]+=1
                    st[5]+=len(word)
                    for b0 in (1,2,3):
                        key=b0,d,word
                        if key not in memo:
                            memo[key]=accepts(T,L,R,b0,d,word)
                        require(memo[key],'actual word outside abstraction')
                        st[3]+=1
    return st


def controls():
    for h in range(1,5):
        for J in product(range(6),repeat=h):
            K=sum(J)
            for d in (2,3,4):
                require(sum(j-j//d for j in J)<=charge(K,h,d),'branch charge')
    require(weight(8,3,0)==Fraction(2,1) and weight(0,3,0)==Fraction(1,3),
            'discrete convexity reciprocal')
    require([length(q) for q in (1,2,3,4)]==[20,42,61,92],'actual lengths')
    return 3


def audit():
    S=shapes()
    with tempfile.TemporaryDirectory() as tmp:
        exe=Path(tmp)/'audit'
        subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-Werror',str(CPP),'-o',str(exe)],check=True)
        short=[run(exe,186,8,c,S)[0] for c in range(3)]
        census=[run(exe,n,2048,c,S) for n in range(186,189) for c in range(3)]
    short=[[r[3],sum(r[4:7])] for r in short]
    require(short==[[9688563,14788341],[13790259,10686645],[2770335,3239541]],
            'prior independent short replay')
    bounds=[]
    for n in range(186,189):
        records=[r for r in census if r[0][0]==n]
        u,row=min((bound(n,m,records,S) for m in range(2*n//5,(13*n+19)//20+1)),
                  key=lambda a:a[0])
        require(u<1,'nonempty residual not established')
        bounds.append(row)
    result={'bounds':bounds,'census':census,'controls':controls(),'reference':reference(),'short':short}
    print('F038_UNRESTRICTED_BLOCK_LANGUAGE_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
