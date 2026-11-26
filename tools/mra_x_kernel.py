"""Phase XXIII: standalone, bounded checker of finite-domain elimination certificates."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

MAX_BYTES=8_000_000
MAX_VISITS=1_000_000
MAX_LOOKUPS=5_000_000


def require(ok):
    if not ok: raise ValueError('certificate rejected')


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def unique(pairs):
    out={}
    for k,v in pairs:
        require(k not in out); out[k]=v
    return out


def load(path):
    with Path(path).open('rb') as f: raw=f.read(MAX_BYTES+1)
    require(len(raw)<=MAX_BYTES)
    return json.loads(raw,object_pairs_hook=unique)


def integer(x):
    return type(x) is int and abs(x)<=10**100


def fields(x,keys):
    require(type(x) is dict and set(x)==set(keys.split()))


def factor(d,f):
    require(type(f) is list and len(f)==2)
    s,rows=f; require(type(s) is list and all(type(v) is str and v in d for v in s) and len(set(s))==len(s))
    require(type(rows) is list); tab={}
    for item in rows:
        require(type(item) is list and len(item)==2); a,c=item
        require(type(a) is list and len(a)==len(s) and all(type(x) is int and 0<=x<d[v] for v,x in zip(s,a)) and integer(c))
        k=tuple(a); require(k not in tab); tab[k]=c
    return tuple(s),tab


def check(doc,expected=None):
    fields(doc,'schema problem result messages'); require(type(doc['schema']) is int and doc['schema']==1)
    problem=doc['problem']; fields(problem,'domains factors'); identity=digest(problem)
    if expected is not None: require(identity==expected)
    d=problem['domains']; require(type(d) is dict and len(d)<=128 and all(type(v) is str and 0<len(v)<=128 and type(k) is int and 1<=k<=4 for v,k in d.items()))
    fs=problem['factors']; require(type(fs) is list and len(fs)<=1024); original=[factor(d,f) for f in fs]
    r=doc['result']; fields(r,'order trace optimum witness induced_width assignments_evaluated')
    order=r['order']; trace=r['trace']; messages=doc['messages']
    require(type(order) is list and all(type(v) is str for v in order) and len(order)==len(d) and set(order)==set(d))
    require(type(trace) is list and type(messages) is list and len(trace)==len(messages)==len(d))
    visits=lookups=width=0; active=list(original); back=[]
    def cost(fs,a):
        nonlocal lookups
        total=0
        for s,tab in fs:
            lookups+=1; require(lookups<=MAX_LOOKUPS)
            c=tab.get(tuple(a[u] for u in s))
            if c is None: return None
            total+=c
        return total
    for i,v in enumerate(order):
        bucket=[f for f in active if v in f[0]]; active=[f for f in active if v not in f[0]]
        s=tuple(sorted({u for scope,_ in bucket for u in scope}-{v})); width=max(width,len(s))
        visits+=d[v]*math.prod(d[u] for u in s); require(visits<=MAX_VISITS)
        ms,tab=factor(d,messages[i]); require(ms==s)
        rec=trace[i]; require(type(rec) is list and len(rec)==3 and rec[:2]==[v,list(s)] and type(rec[2]) is list)
        args={}
        for row in rec[2]:
            require(type(row) is list and len(row)==2); a,x=row
            require(type(a) is list and len(a)==len(s) and all(type(y) is int and 0<=y<d[u] for u,y in zip(s,a)) and type(x) is int and 0<=x<d[v])
            k=tuple(a); require(k not in args); args[k]=x
        require(set(args)==set(tab))
        for row in itertools.product(*(range(d[u]) for u in s)):
            a=dict(zip(s,row)); claim=tab.get(row); attained=False
            for x in range(d[v]):
                a[v]=x; c=cost(bucket,a)
                if c is None: continue
                require(claim is not None and (c,x)>=(claim,args[row]))
                if (c,x)==(claim,args[row]): attained=True
            require(attained==(claim is not None))
        active.append((s,tab)); back.append((v,s,args))
    optimum=cost(active,{})
    require(r['optimum'] is None if optimum is None else integer(r['optimum']) and r['optimum']==optimum)
    require(type(r['induced_width']) is int and r['induced_width']==width and type(r['assignments_evaluated']) is int and r['assignments_evaluated']==visits)
    if optimum is None: require(r['witness'] is None)
    else:
        a={}
        for v,s,args in reversed(back): a[v]=args[tuple(a[u] for u in s)]
        require(type(r['witness']) is dict and all(type(x) is int for x in r['witness'].values()) and a==r['witness'] and cost(original,a)==optimum)
    return dict(problem_sha256=identity,certificate_sha256=digest(doc),optimum=optimum,variables=len(d),visits=visits,lookups=lookups)


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('certificate'); p.add_argument('--expect-problem'); a=p.parse_args()
    try: print(json.dumps(check(load(a.certificate),a.expect_problem),sort_keys=True))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError,OSError) as e: p.exit(1,'rejected: '+str(e)+'\n')
