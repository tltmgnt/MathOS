"""Bounded automatic signed Hall guard embedding, for a single saved witness."""
from collections import defaultdict
from .pnp_bounded_matching import Meter, Limit, normalize, order, check
from .pnp_hall_witness_memory import guards, transport


def solve(n, f, record, *, steps=25000, seconds=1.25):
    b=Meter(steps,seconds)
    def unknown(status):
        return {'decision':'unknown','status':status,'work_steps':steps if status=='resource_exhausted' else b.used,
                'embedding':None,'certificate':None}
    try:
        if set(record)!={'schema','n','guards','certificate','source_embedding'} or record['schema']!='mathos-hall-memory/1':
            raise ValueError('record schema')
        k=record['n'];c=record['certificate']
        if type(k) is not int or not 1<=k<=512 or c['decision']!='unsat':
            raise ValueError('record scope')
        check(k,record['guards'],c,b)
        expected=guards(c,b)
        if normalize(k,record['guards'],b)!=expected:
            raise ValueError('guard set differs from witness premises')
        active={abs(x) for g in c['groups'] for x in g}
        b.tick(1+k)
        if active!=set(range(1,k+1)):
            raise ValueError('not dense')
        if k>128 or k>n:
            return unknown('support_limit')
        known=normalize(n,f,b)
        bywidth=defaultdict(list);graph=defaultdict(set)
        for q in known:
            b.tick(1+len(q))
            bywidth[len(q)].append(order(q,b))
            if len(q)==2:
                x,y=q;graph[-x].add(-y);graph[-y].add(-x)
        for qs in bywidth.values():
            b.tick(1+sum(map(len,qs))*max(1,len(qs).bit_length()));qs.sort()
        neighbors={}
        for bucket in c['buckets']:
            for x in bucket:
                b.tick(1+len(bucket));neighbors[x]=set(bucket)-{x}
        groups=[order(g,b) for g in c['groups']]
        b.tick(1+k*max(1,len(groups).bit_length()))
        groups.sort(key=lambda g:(len(bywidth[len(g)]),-len(g),g))
        if any(not bywidth[len(g)] for g in groups):return unknown('not_found')
        mapping={};used=set()

        def group(i):
            b.tick()
            if i==len(groups):return True
            g=groups[i]
            for q in bywidth[len(g)]:
                b.tick(1+len(q))
                if any(abs(y) in used for y in q):continue
                # Most already-bound conflict neighbors first; recomputed per group.
                b.tick(1+sum(len(neighbors[x]) for x in g)+len(g)*max(1,len(g).bit_length()))
                xs=sorted(g,key=lambda x:(-sum(z in mapping for z in neighbors[x]),-len(neighbors[x]),x))
                if literals(i,xs,q,0):return True
            return False

        def literals(i,xs,q,j):
            b.tick()
            if j==len(xs):return group(i+1)
            x=xs[j];ns=neighbors[x]
            for y in q:
                b.tick(1+len(ns))
                if abs(y) in used or len(graph.get(y,()))<len(ns):continue
                if any(z in mapping and mapping[z] not in graph.get(y,()) for z in ns):continue
                mapping[x]=y;used.add(abs(y))
                if literals(i,xs,q,j+1):return True
                used.remove(abs(y));del mapping[x]
            return False

        if not group(0):return unknown('not_found')
        b.tick(1+k)
        e=[0]*k
        for x,y in mapping.items():e[abs(x)-1]=y if x>0 else -y
        target=transport(c,e,b)
        check(n,f,target,b)
        return {'decision':'unsat','status':'verified','work_steps':b.used,'embedding':e,'certificate':target}
    except Limit:
        return unknown('resource_exhausted')


def replay(n,f,record,r,*,steps=25000):
    if set(r)!={'decision','status','work_steps','embedding','certificate'}:
        raise ValueError('report fields')
    w,e,c=r['work_steps'],r['embedding'],r['certificate']
    if type(w) is not int or not 0<=w<=steps:raise ValueError('work envelope')
    if r['status']=='verified':
        from .pnp_hall_witness_memory import transfer
        if r['decision']!='unsat' or not isinstance(c,dict):raise ValueError('decision mismatch')
        t=transfer(n,f,record,e,steps=max(1,w),seconds=15)
        if t['decision']!='unsat' or t['certificate']!=c:raise ValueError('transport mismatch or replay exhausted')
    elif (r['status'] not in ('not_found','support_limit','resource_exhausted') or r['decision']!='unknown'
          or e is not None or c is not None or (r['status']=='resource_exhausted' and w!=steps)):
        raise ValueError('uncredited report')
    return True
