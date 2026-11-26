"""Finite reference for explicit-table geometry, local replay, and exact clock slack."""
import json
from itertools import product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_crossing_adversary import true
from mathos.research.f038_unrestricted_universal_search import (
    encoded, valid, encode_tm, decode_tm)
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed, witness


def length(m):
    n=19*m-7
    return n+1+2*n*n+8*comb(n,3)


def tables():
    rows=[]
    for m in (2,3):
        n=19*m-7
        N=m*m
        M=m**3
        Q=N**3
        C=pool(n)
        pos={c:i for i,c in enumerate(C)}
        F=fixed(9,m,n,(0,)*m)
        clauses=tuple((-(m+a+1),-(3*m+b+1),-(5*m+c+1))
                      for a,b,c in product(range(m),repeat=3))
        require(len(set(F+clauses))==len(F)+M,'fixed/variable overlap')
        slots=[pos[c] for c in clauses]
        base=bytearray(len(C))
        for c in F:
            base[pos[c]]=1
        masks=range(256) if m==2 else (
            [0,(1<<M)-1]+[1<<i for i in range(M)]+[0x5555555,0x2aaaaaa,0x1234567])
        entries=reads=sat=0
        for mask in masks:
            raw=base[:]
            for j,i in enumerate(slots):
                raw[i]=mask>>j&1
            A=[]
            for u,v,w in product(range(N),repeat=3):
                j=((u%m)*m+v%m)*m+w%m
                bit=1-raw[slots[j]]
                require(bit==1-(mask>>j&1),'table entry')
                A.append(bit)
                entries+=1
            first=last=0
            for j,(a,b,c) in enumerate(product(range(m),repeat=3)):
                p=(a*N+b)*N+c
                q=(((m-1)*m+a)*N+b)*N+c
                require(p<m*N*N and q>=Q-m*N*N,'recovery position')
                first|=(1-A[p])<<j
                last|=(1-A[q])<<j
                reads+=2
            require(first==last==mask,'mask recovery')
            if mask!=(1<<M)-1:
                j=next(j for j in range(M) if not (mask>>j&1))
                a=[0]*9
                a[1],a[3],a[5]=j//(m*m),j//m%m,j%m
                w=witness(9,m,n,(0,)*m,a)
                require(all(true(c,w) for c in F),'fixed witness')
                require(all(true(c,w) for i,c in enumerate(clauses) if mask>>i&1),
                        'cross witness')
                if mask in (0,1):
                    p=sum(1<<i for i,v in enumerate(raw) if v)
                    require(encoded(n,p,C)=='1'*n+'0'+''.join(map(str,raw)),
                            'original normalized input')
                    require(valid(C,n,p,w),'original verifier')
                sat+=1
        rows.append([m,len(masks),entries,reads,sat])
    require(rows==[[2,256,16384,4096,255],[3,32,23328,1728,31]],'table totals')
    return rows


def exterior(c,h):
    return h<c if c<=0 else h>=c


def run(T,q,S,t,c):
    tape=dict(enumerate(S))
    h=state=steps=0
    seq=[]
    for _ in range(t):
        if state==q:
            break
        old=h
        a,w,d=T[3*state+tape.get(h,2)]
        steps+=exterior(c,h)
        if w==2:
            tape.pop(h,None)
        else:
            tape[h]=w
        h+=d
        state=a
        if exterior(c,old)!=exterior(c,h):
            seq.append(state)
    return seq,steps,{p:v for p,v in tape.items() if exterior(c,p)},state


def replay(T,q,c,seq,steps):
    tape={}
    used=0
    for j in range(0,len(seq),2):
        h=c-1 if c<=0 else c
        state=seq[j]
        while j+1<len(seq) or used<steps:
            require(state!=q and used<steps and exterior(c,h),'replay budget')
            a,w,d=T[3*state+tape.get(h,2)]
            if w==2:
                tape.pop(h,None)
            else:
                tape[h]=w
            h+=d
            state=a
            used+=1
            if not exterior(c,h):
                require(j+1<len(seq) and state==seq[j+1],'exit record')
                break
        require(exterior(c,h)==(j+1==len(seq)),'visit endpoint')
    require(used==steps,'exterior time')
    return tape


def replay_checks():
    seed=192837
    def rand(n):
        nonlocal seed
        seed=(1664525*seed+1013904223)&0xffffffff
        return seed%n
    rows=[]
    for q in (1,2,3):
        size=5832 if q==1 else 256
        row=[q,size,0,0,0,0,0,0]
        for k in range(size):
            T=[]
            v=k
            for _ in range(3*q):
                if q==1:
                    a=v%18
                    v//=18
                    T.append((a//9,a//3%3,a%3-1))
                else:
                    T.append((rand(q+1),rand(3),rand(3)-1))
            require(decode_tm(encode_tm(T,q))==(q,T),'table syntax')
            for S,t,c in product(((0,1,0),(1,0,1)),(1,4,8),(-1,0,3,4)):
                seq,steps,out,state=run(T,q,S,t,c)
                require(replay(T,q,c,seq,steps)==out,'exterior reconstruction')
                row[2]+=1
                row[3]+=bool(seq)
                row[4]+=len(seq)>=2
                row[5]+=bool(seq) and seq[-1]==q
                row[6]+=len(seq)%2==1 and state!=q
                row[7]+=steps
        rows.append(row)
    require(rows==[[1,5832,139968,16832,1950,8196,6160,18438],
                   [2,256,6144,794,128,277,333,1086],
                   [3,256,6144,880,194,290,439,1490]],'replay totals')
    return rows


def arithmetic():
    geom=dyad=syntax=0
    for m in (256,512,1024):
        L=length(m)
        Q=m**6
        J=Q//3
        P=m**5
        require(6*(L+P)<=Q,'geometry margin')
        for h in (-2*Q,-Q,-Q//2,-1,0,L//2,L,L+Q,L+2*Q,
                  L+Q//2-Q,L+Q//2-Q-1):
            e=h+Q
            right=2*(e-L)>=Q-L
            for i in (1,J//2,J):
                c=L+i if right else -i
                require(e-P>=c if right else h+P<=c,'exterior block')
                geom+=1
    for j in range(32,129,8):
        cap=1<<j
        lo=hi=2
        while length(hi)<=cap:
            hi*=2
        while hi-lo>1:
            mid=(lo+hi)//2
            if length(mid)<=cap:
                lo=mid
            else:
                hi=mid
        require(length(lo)<=cap<length(lo+1),'dyadic maximum')
        if lo>=100:
            require(20*cap<=21*length(lo),'near dyadic')
            dyad+=1
    for q in range(2,129):
        b=(q-1).bit_length()
        ell=4+q+3*q*(q.bit_length()+4)
        require((1<<ell)>=(1<<42)*b,'weighted bits')
        syntax+=1
    require(40*21**3*9146**3<9*20**3*2**42,'strict slack')
    require((geom,dyad,syntax)==(99,12,127),'arithmetic totals')
    return [geom,dyad,syntax]


def audit():
    result={'tables':tables(),'replay':replay_checks(),'arithmetic':arithmetic()}
    print('F038_UNRESTRICTED_EXPLICIT_TABLE_BARRIER_OK '+
          json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
