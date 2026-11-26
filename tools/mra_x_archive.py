"""Phase XXIV: standalone content-addressed archive and incremental certificate replay."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

MAX_BYTES=8_000_000
MAX_STATES=128
MAX_OBJECTS=32768
MAX_VISITS=1_000_000
MAX_LOOKUPS=5_000_000
MAX_ARCHIVE_VISITS=8_000_000


def require(ok):
    if not ok: raise ValueError('archive rejected')


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')


def digest(x): return hashlib.sha256(canonical(x)).hexdigest()


def unique(pairs):
    out={}
    for k,v in pairs:
        require(k not in out); out[k]=v
    return out


def load(path):
    with Path(path).open('rb') as f: raw=f.read(MAX_BYTES+1)
    require(len(raw)<=MAX_BYTES)
    return json.loads(raw,object_pairs_hook=unique)


def fields(x,keys): require(type(x) is dict and set(x)==set(keys.split()))


def integer(x): return type(x) is int and abs(x)<=10**100


def factor(d,f):
    require(type(f) is list and len(f)==2)
    s,rows=f; require(type(s) is list and all(type(v) is str and v in d for v in s) and len(set(s))==len(s))
    require(type(rows) is list); tab={}
    for item in rows:
        require(type(item) is list and len(item)==2); a,c=item
        require(type(a) is list and len(a)==len(s) and all(type(x) is int and 0<=x<d[v] for v,x in zip(s,a)) and integer(c))
        k=tuple(a); require(k not in tab); tab[k]=c
    return tuple(s),tab


def pack(docs):
    objects=[]; index={}; states=[]
    def add(value):
        h=digest(value)
        if h in index:
            require(canonical(objects[index[h]][1])==canonical(value)); return index[h]
        i=len(objects); index[h]=i; objects.append([h,value]); return i
    for doc in docs:
        r=dict(doc['result']); trace=r.pop('trace'); p=doc['problem']
        states.append(dict(domains=p['domains'],factors=[add(f) for f in p['factors']],proofs=[add([m,w]) for m,w in zip(doc['messages'],trace)],result=r,problem_sha256=digest(p)))
    return dict(schema=1,objects=objects,states=states)


def check(archive,expected=None):
    fields(archive,'schema objects states'); require(type(archive['schema']) is int and archive['schema']==1)
    identity=digest(archive)
    if expected is not None: require(identity==expected)
    objects=archive['objects']; states=archive['states']
    require(type(objects) is list and len(objects)<=MAX_OBJECTS and type(states) is list and 1<=len(states)<=MAX_STATES)
    seen=set(); used=set()
    for entry in objects:
        require(type(entry) is list and len(entry)==2); h,obj=entry
        require(type(h) is str and h not in seen and digest(obj)==h); seen.add(h)
    def get(i):
        require(type(i) is int and 0<=i<len(objects)); used.add(i); return objects[i][1]
    receipts={}; results=[]; cumulative=0
    for state in states:
        result,receipts=verify_state(state,get,receipts,MAX_ARCHIVE_VISITS-cumulative)
        cumulative+=result['visits']; results.append(result)
    require(len(used)==len(objects))
    return dict(archive_sha256=identity,states=results)


def verify_state(state,get,receipts,remaining):
    fields(state,'domains factors proofs result problem_sha256'); d=state['domains']
    require(type(d) is dict and len(d)<=128 and all(type(v) is str and 0<len(v)<=128 and type(n) is int and 1<=n<=4 for v,n in d.items()))
    ids=state['factors']; proofs=state['proofs']; require(type(ids) is list and len(ids)<=1024 and type(proofs) is list and len(proofs)==len(d))
    fs=[get(i) for i in ids]; problem=dict(domains=d,factors=fs); require(digest(problem)==state['problem_sha256'])
    original=[factor(d,f) for f in fs]; active=list(original); r=state['result']; fields(r,'order optimum witness induced_width assignments_evaluated')
    order=r['order']; require(type(order) is list and all(type(v) is str for v in order) and len(order)==len(d) and set(order)==set(d))
    visits=fresh=lookups=width=hits=0; back=[]; staged={}
    def cost(fs,a):
        nonlocal lookups
        total=0
        for s,tab in fs:
            lookups+=1; require(lookups<=MAX_LOOKUPS)
            c=tab.get(tuple(a[u] for u in s))
            if c is None: return None
            total+=c
        return total
    for v,pid in zip(order,proofs):
        bucket=[f for f in active if v in f[0]]; active=[f for f in active if v not in f[0]]
        s=tuple(sorted({u for scope,_ in bucket for u in scope}-{v})); width=max(width,len(s))
        n=d[v]*math.prod(d[u] for u in s); visits+=n
        require(visits<=MAX_VISITS and visits<=remaining)
        proof=get(pid); require(type(proof) is list and len(proof)==2); message,rec=proof
        ms,tab=factor(d,message); require(ms==s)
        require(type(rec) is list and len(rec)==3 and rec[:2]==[v,list(s)] and type(rec[2]) is list)
        args={}
        for row in rec[2]:
            require(type(row) is list and len(row)==2); a,x=row
            require(type(a) is list and len(a)==len(s) and all(type(y) is int and 0<=y<d[u] for u,y in zip(s,a)) and type(x) is int and 0<=x<d[v])
            key=tuple(a); require(key not in args); args[key]=x
        require(set(args)==set(tab))
        # Exact, immutable equality; object hashes alone never authorize reuse.
        key=(tuple((u,d[u]) for u in (v,)+s),tuple(sorted((scope,tuple(sorted(table.items()))) for scope,table in bucket)),tuple(sorted(tab.items())),tuple(sorted(args.items())))
        if receipts.get(v)==key: hits+=1
        else:
            fresh+=n
            for row in itertools.product(*(range(d[u]) for u in s)):
                a=dict(zip(s,row)); claim=tab.get(row); attained=False
                for x in range(d[v]):
                    a[v]=x; c=cost(bucket,a)
                    if c is None: continue
                    require(claim is not None and (c,x)>=(claim,args[row]))
                    if (c,x)==(claim,args[row]): attained=True
                require(attained==(claim is not None))
        staged[v]=key; active.append((s,tab)); back.append((v,s,args))
    optimum=cost(active,{})
    require(r['optimum'] is None if optimum is None else integer(r['optimum']) and r['optimum']==optimum)
    require(type(r['induced_width']) is int and r['induced_width']==width and type(r['assignments_evaluated']) is int and r['assignments_evaluated']==visits)
    if optimum is None: require(r['witness'] is None)
    else:
        a={}
        for v,s,args in reversed(back): a[v]=args[tuple(a[u] for u in s)]
        require(type(r['witness']) is dict and all(type(x) is int for x in r['witness'].values()) and a==r['witness'] and cost(original,a)==optimum)
    return dict(problem_sha256=state['problem_sha256'],optimum=optimum,variables=len(d),visits=visits,fresh=fresh,lookups=lookups,hits=hits),staged


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('archive'); p.add_argument('--expect-archive'); a=p.parse_args()
    try: print(json.dumps(check(load(a.archive),a.expect_archive),sort_keys=True))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError,OSError) as e: p.exit(1,'rejected: '+str(e)+'\n')
