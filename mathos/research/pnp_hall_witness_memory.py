"""Guarded Hall witness reuse; only explicit embeddings, never untrusted SAT.
No automatic isomorphism search or global mutable cache.
"""
from itertools import combinations
from .pnp_bounded_matching import Meter, Limit, normalize, order, check


def guards(c, b):
    out = set()
    for g in c['groups']:
        b.tick(1 + len(g)); out.add(frozenset(g))
    for bucket in c['buckets']:
        for x,y in combinations(bucket,2):
            b.tick(); out.add(frozenset((-x,-y)))
    return out


def transport(c, embedding, b):
    def mapped(x):
        b.tick(); v = embedding[abs(x)-1]
        return v if x > 0 else -v
    return {'decision':'unsat', **{k:[[mapped(x) for x in g] for g in c[k]]
                                   for k in ('groups','buckets')}}


def admit(n, f, certificate, *, steps=100_000, seconds=5):
    """Verify original proof, abstract to dense labels, recheck guard-only proof."""
    b = Meter(steps, seconds)
    if certificate['decision'] != 'unsat':
        raise ValueError('Hall contradiction required')
    check(n,f,certificate,b)
    active = order({abs(x) for g in certificate['groups'] for x in g},b)
    dense = {v:i+1 for i,v in enumerate(active)}
    b.tick(1+n); mapping = [dense.get(v,0) for v in range(1,n+1)]
    c = transport(certificate,mapping,b)
    g = [order(q,b) for q in guards(c,b)]
    b.tick(1+sum(map(len,g))*max(1,len(g).bit_length())); g.sort()
    check(len(active),g,c,b)
    return {'schema':'mathos-hall-memory/1','n':len(active),'guards':g,
            'certificate':c,'source_embedding':active}


def transfer(n,f,record,embedding,*,steps=25_000,seconds=1.25):
    """Explicit signed injection, verified on guards and on the original target."""
    b = Meter(steps,seconds)
    def unknown(status):
        return {'decision':'unknown','status':status,'work_steps':steps if status=='resource_exhausted' else b.used,'certificate':None}
    try:
        if set(record) != {'schema','n','guards','certificate','source_embedding'} or record['schema']!='mathos-hall-memory/1':
            raise ValueError('record schema')
        k = record['n']
        if type(k) is not int or not 1<=k<=512 or not isinstance(embedding,(list,tuple)) or len(embedding)!=k:
            raise ValueError('embedding shape')
        b.tick(1+k)
        if any(type(x) is not int or not 0<abs(x)<=n for x in embedding) or len({abs(x) for x in embedding})!=k:
            raise ValueError('embedding not a signed injection')
        c = record['certificate']
        if c['decision']!='unsat': raise ValueError('not Hall certificate')
        # Never trust a saved record or a claimed source provenance.
        check(k,record['guards'],c,b)
        expected=guards(c,b)
        if normalize(k,record['guards'],b)!=expected:
            raise ValueError('guard set differs from witness premises')
        known=normalize(n,f,b)
        for q in expected:
            b.tick(1+len(q))
            mapped=frozenset(embedding[abs(x)-1]*(1 if x>0 else -1) for x in q)
            if mapped not in known:return unknown('guard_miss')
        target=transport(c,embedding,b)
        check(n,f,target,b)
        return {'decision':'unsat','status':'verified','work_steps':b.used,'certificate':target}
    except Limit:
        return unknown('resource_exhausted')
