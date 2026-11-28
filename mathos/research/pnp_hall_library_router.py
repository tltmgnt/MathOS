"""Bounded multi-record Hall lookup with cold UNSAT-only fallback."""
import time
from collections import Counter
from .pnp_bounded_matching import Meter, Limit, normalize
from .pnp_hall_rectangular_embedding import solve as rectangular
from .pnp_signed_hall_subsystem import solve as cold


def profile(record,b):
    # Hints only: search independently validates the chosen record.
    c=record['certificate'];gs,bs=c['groups'],c['buckets'];r,s=len(gs),len(bs)
    b.tick(1+r+s+sum(map(len,gs))+sum(map(len,bs)))
    if not 1<=s<r or record['n']!=r*s or r*s>128 or any(len(g)!=s for g in gs) or any(len(g)!=r for g in bs):return None
    col={x:j for j,q in enumerate(bs) for x in q}
    if any(len({col.get(x,-1) for x in g})!=s or any(x not in col for x in g) for g in gs):return None
    return r,s


def candidates(n,f,records,b):
    known=normalize(n,f,b);degree=Counter();width=Counter()
    for q in known:
        b.tick(1+len(q));width[len(q)]+=1
        if len(q)==2:
            for x in q:degree[-x]+=1
    active=len({abs(x) for q in known for x in q});b.tick(1+sum(map(len,known)))
    out=[]
    for i,record in enumerate(records):
        p=profile(record,b)
        if p is None:continue
        r,s=p
        if r*s>active or width[s]<r or width[2]<s*r*(r-1)//2:continue
        count=0
        for q in known:
            b.tick()
            if len(q)==s:
                b.tick(s)
                if all(degree[x]>=r-1 for x in q):count+=1
        if count>=r:out.append((count-r,r*s,i))
    b.tick(1+len(out)*max(1,len(out).bit_length()))
    return [i for _,_,i in sorted(out)]


def solve(n,f,records,*,steps=25000,seconds=1.25,indexed=True):
    if not isinstance(records,(list,tuple)) or len(records)>32 or type(indexed) is not bool or steps<5:raise ValueError('library envelope')
    deadline=time.monotonic()+seconds;cap=steps*4//5
    b=Meter(cap,seconds*4/5);attempts=[];decision='unknown';cert=None
    try:
        if indexed:ids=candidates(n,f,records,b)
        else:b.tick(1+len(records));ids=list(range(len(records)))
        selection=b.used
    except Limit:
        ids=[];selection=cap
    used=selection
    for i in ids[:4]:
        left=min(deadline-time.monotonic(),b.deadline-time.monotonic());q=cap-used
        if q<1 or left<=0:break
        r=rectangular(n,f,records[i],steps=q,seconds=left)
        attempts.append({'record':i,'quota':q,'report':r});used+=r['work_steps']
        if r['decision']=='unsat':decision='unsat';cert=r['certificate'];break
    fb=None;left=deadline-time.monotonic()
    if decision=='unknown' and left>0 and used<steps:
        fb=cold(n,f,steps=steps-used,seconds=left);used+=fb['work_steps'];decision=fb['decision'];cert=fb['certificate']
    return {'decision':decision,'certificate':cert,'work_steps':used,'selection_work':selection,'candidates':ids,'attempts':attempts,'fallback':fb,'indexed':indexed}
