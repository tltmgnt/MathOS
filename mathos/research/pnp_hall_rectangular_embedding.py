"""Symmetry-reduced exact signed embedding for rectangular Hall witnesses."""
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
        known=normalize(n,f,b);graph=defaultdict(set);rows=[]
        for q in known:
            b.tick(1+len(q))
            if len(q)==2:
                x,y=q;graph[-x].add(-y);graph[-y].add(-x)
            if len(q)==s:rows.append(order(q,b))
        # Every image literal has at least r-1 conflict neighbors.
        candidates=[]
        for q in rows:
            b.tick(1+s)
            if all(len(graph.get(x,()))>=r-1 for x in q):candidates.append(q)
        b.tick(1+len(candidates)*s*max(1,len(candidates).bit_length()));candidates.sort()
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
        return {'decision':'unsat','status':'verified','work_steps':b.used,'embedding':e,'certificate':target}
    except Limit:
        return unknown('resource_exhausted')
