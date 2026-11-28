"""Shared per-query target index for bounded rectangular Hall library search."""
from collections import defaultdict
import time
from .pnp_hall_library_router import profile
from .pnp_signed_hall_subsystem import solve as cold
from .pnp_bounded_matching import Meter, Limit, normalize, order, check
from .pnp_hall_witness_memory import guards, transport


def _attempt(n, f, record, index, b):
    start=b.used;steps=b.limit-start
    def unknown(status):
        return {'decision':'unknown','status':status,'work_steps':steps if status=='resource_exhausted' else b.used-start,
                'embedding':None,'certificate':None}
    try:
        if set(record)!={'schema','n','guards','certificate','source_embedding'} or record['schema']!='mathos-hall-memory/1':
            raise ValueError('record schema')
        k=record['n'];c=record['certificate']
        if type(k) is not int or not 1<=k<=512 or c['decision']!='unsat':raise ValueError('record scope')
        check(k,record['guards'],c,b)
        if normalize(k,record['guards'],b)!=guards(c,b):raise ValueError('guard mismatch')
        gs,bs=c['groups'],c['buckets'];r,s=len(gs),len(bs)
        b.tick(1+k+r+s)
        if {abs(x) for g in gs for x in g}!=set(range(1,k+1)):raise ValueError('not dense')
        if k>128 or k>n:return unknown('support_limit')
        if not s or k!=r*s or any(len(g)!=s for g in gs) or any(len(q)!=r for q in bs):return unknown('nonrectangular')
        col={x:j for j,q in enumerate(bs) for x in q}
        source=[]
        for g in gs:
            b.tick(1+s*max(1,s.bit_length()))
            if len({col[x] for x in g})!=s:return unknown('nonrectangular')
            source.append(sorted(g,key=col.__getitem__))
        graph,candidates=index.graph,index.eligible(r,s,b)
        if len(candidates)<r:return unknown('not_found')
        # Row and column automorphisms let us order image rows and fix the
        # first image row's column ordering. All remaining bijections are searched.
        used=set(); chosen=[]
        def visit(start,domains):
            b.tick(); i=len(chosen)
            if i==r:return True
            for j in range(start,len(candidates)-(r-i)+1):
                q=candidates[j];b.tick(1+s)
                if any(abs(x) in used for x in q):continue
                if i==0:
                    picks=[q]
                else:
                    opts=[];qset=set(q)
                    for d in domains:
                        b.tick(1+min(len(qset),len(d)))
                        opts.append(order(qset&d,b))
                    if any(not a for a in opts):continue
                    # MRV enumeration of each complete column bijection.
                    b.tick(1+s*max(1,s.bit_length()));idx=sorted(range(s),key=lambda z:(len(opts[z]),z))
                    def assignments(pos,partial,taken):
                        b.tick()
                        if pos==s:
                            yield tuple(partial);return
                        z=idx[pos]
                        for x in opts[z]:
                            b.tick()
                            if x in taken:continue
                            partial[z]=x;taken.add(x)
                            yield from assignments(pos+1,partial,taken)
                            taken.remove(x)
                    picks=assignments(0,[0]*s,set())
                for a in picks:
                    b.tick(1+s);chosen.append(a);used.update(abs(x) for x in a)
                    if i+1==r:return True
                    ds=[]
                    for z,x in enumerate(a):
                        adj=graph.get(x,set())
                        if i==0:
                            b.tick(1+len(adj));ds.append(set(adj))
                        else:
                            b.tick(1+min(len(domains[z]),len(adj)));ds.append(domains[z]&adj)
                    if visit(j+1,ds):return True
                    chosen.pop();used.difference_update(abs(x) for x in a)
            return False
        if not visit(0,[]):return unknown('not_found')
        b.tick(1+k);e=[0]*k
        for g,q in zip(source,chosen):
            for x,y in zip(g,q):e[abs(x)-1]=y if x>0 else -y
        target=transport(c,e,b);check(n,f,target,b)
        return {'decision':'unsat','status':'verified','work_steps':b.used-start,'embedding':e,'certificate':target}
    except Limit:
        return unknown('resource_exhausted')


class _TargetIndex:
    def __init__(self,n,f,b,widths):
        known=normalize(n,f,b);self.graph=defaultdict(set);self.rows=defaultdict(list)
        self.count=defaultdict(int);active=set()
        for q in known:
            b.tick(1+len(q));active.update(map(abs,q));self.count[len(q)]+=1
            if len(q)==2:
                x,y=q;self.graph[-x].add(-y);self.graph[-y].add(-x)
            if len(q) in widths:self.rows[len(q)].append(q)
        self.active=len(active);self.cache={}

    def eligible(self,r,s,b):
        key=(r,s)
        if key not in self.cache:
            out=[]
            for q in self.rows[s]:
                b.tick(1+s)
                if all(len(self.graph.get(x,()))>=r-1 for x in q):out.append(order(q,b))
            b.tick(1+len(out)*s*max(1,len(out).bit_length()));out.sort()
            self.cache[key]=out
        b.tick()
        return self.cache[key]


def solve(n,f,records,*,steps=25000,seconds=1.25):
    if not isinstance(records,(list,tuple)) or len(records)>32 or type(steps) is not int or steps<5:
        raise ValueError('library envelope')
    deadline=time.monotonic()+seconds;cap=steps*4//5
    b=Meter(cap,seconds*4/5);attempts=[];decision='unknown';cert=None
    try:
        ps=[profile(rec,b) for rec in records]
        index=_TargetIndex(n,f,b,{p[1] for p in ps if p is not None})
        ranked=[]
        for i,p in enumerate(ps):
            b.tick()
            if p is None:continue
            r,s=p
            if r*s>index.active or index.count[s]<r or index.count[2]<s*r*(r-1)//2:continue
            k=len(index.eligible(r,s,b))
            if k>=r:ranked.append((k-r,r*s,i))
        b.tick(1+len(ranked)*max(1,len(ranked).bit_length()));ids=[i for _,_,i in sorted(ranked)]
        selection=b.used
    except Limit:
        ids=[];selection=cap
    used=selection
    for i in ids[:4]:
        q=cap-used
        if q<1 or time.monotonic()>=b.deadline:break
        r=_attempt(n,f,records[i],index,b)
        attempts.append({'record':i,'quota':q,'report':r});used+=r['work_steps']
        if r['decision']=='unsat':decision='unsat';cert=r['certificate'];break
        if r['status']=='resource_exhausted':break
    fb=None;left=deadline-time.monotonic()
    if decision=='unknown' and left>0 and used<steps:
        fb=cold(n,f,steps=steps-used,seconds=left);used+=fb['work_steps'];decision=fb['decision'];cert=fb['certificate']
    return {'decision':decision,'certificate':cert,'work_steps':used,'selection_work':selection,'candidates':ids,'attempts':attempts,'fallback':fb,'indexed':True}
