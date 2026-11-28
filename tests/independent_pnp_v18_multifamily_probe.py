"""Archived regression and fresh synthetic development controls, equal process envelopes."""
import json, random, sys, time, os, signal, resource, multiprocessing as mp
from collections import Counter
from itertools import product
from mathos.research.pnp_hall_shared_index import solve as hall
from mathos.research.pnp_v18_multifamily import solve, _attempt, propagation

STEPS=25000
SECONDS=1.25
WALL=3
MEMORY=512*1024*1024


def truth(n,f):
    # Bitsets over all 2^n assignments, independent from the solver.
    m=1<<n;mask=(1<<m)-1;pos=[]
    for v in range(n):
        block=(1<<(1<<v))-1;bits=0
        for i in range(1<<v,m,1<<(v+1)):bits|=block<<i
        pos.append(bits)
    a=mask
    for q in f:
        b=0
        for x in q:b|=pos[abs(x)-1] if x>0 else mask^pos[abs(x)-1]
        a&=b
        if not a:break
    return bool(a)


def scramble(n,f,rng):
    p=list(range(1,n+1));rng.shuffle(p);p=[x if rng.randrange(2) else -x for x in p]
    order=list(range(len(f)));rng.shuffle(order);ix={j:i for i,j in enumerate(order)}
    out=[[p[abs(x)-1]*(1 if x>0 else -1) for x in f[j]] for j in order]
    for q in out:rng.shuffle(q)
    return out,p,ix


def rename_model(a,p):
    out=[False]*len(p)
    for i,x in enumerate(p):out[abs(x)-1]=a[i]==(x>0)
    return out


def fresh():
    rng=random.Random(190207);rows=[]
    for k in (3,5,8,12,16,20,24,32,40,64):
        n=k+3
        for sat in (False,True):
            f=[[1]]+[[-i,i+1] for i in range(1,k)]+[[k if sat else -k],[-k-1,-k-2,-k-3],[-k-1,k+3]]
            g,p,ix=scramble(n,f,rng)
            rows.append({'n':n,'clauses':g,'kind':'signed_horn','reference':'sat' if sat else 'unsat',
                         'model':rename_model([True]*k+[False]*3,p) if sat else None,
                         'reference_certificate':None if sat else {'trace':[ix[j] for j in range(k+1)]}})
    for h in range(3,11):
        edges=[(i*h+j,i*h+(j+1)%h) for i in range(2) for j in range(h)]+[(j,h+j) for j in range(h)]
        scopes=[[i+1 for i,e in enumerate(edges) if v in e] for v in range(2*h)]
        n=len(edges);a=[bool(rng.randrange(2)) for _ in edges];rhs=[sum(a[x-1] for x in q)%2 for q in scopes]
        for sat in (False,True):
            f=[];cert=[]
            for i,q in enumerate(scopes):
                value=rhs[i]^(int(not sat and i==0));ids=[]
                for bits in product((False,True),repeat=len(q)):
                    if sum(bits)%2!=value:
                        ids.append(len(f));f.append([-x if b else x for x,b in zip(q,bits)])
                cert.append({'scope':q,'rhs':value,'sources':ids})
            if h%2==0:
                f.append([x if a[x-1] else -x for x in rng.sample(range(1,n+1),5)])
            g,p,ix=scramble(n,f,rng)
            dual=[{'scope':sorted(abs(p[x-1]) for x in q['scope']),
                   'rhs':q['rhs']^(sum(p[x-1]<0 for x in q['scope'])%2),'sources':[ix[i] for i in q['sources']]} for q in cert]
            rows.append({'n':n,'clauses':g,'kind':'affine','reference':'sat' if sat else 'unsat',
                         'model':rename_model(a,p) if sat else None,'reference_certificate':None if sat else {'dual':dual}})
    for n in (8,10,12):
        counts=Counter();seen=set()
        while min(counts[False],counts[True])<4:
            f=set()
            while len(f)<5*n:
                f.add(tuple(sorted(x if rng.randrange(2) else -x for x in rng.sample(range(1,n+1),3))))
            f=sorted(f);key=tuple(f)
            if key in seen:continue
            seen.add(key);sat=truth(n,f)
            if counts[sat]>=4:continue
            counts[sat]+=1
            rows.append({'n':n,'clauses':[list(q) for q in f],'kind':'random3','reference':'sat' if sat else 'unsat','model':None,'reference_certificate':None})
    assert len(rows)==60
    return rows


def worker(conn,arm,n,f,lib):
    try:
        resource.setrlimit(resource.RLIMIT_AS,(MEMORY,MEMORY));resource.setrlimit(resource.RLIMIT_CPU,(WALL,WALL))
        os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
        r=hall(n,f,lib,steps=STEPS,seconds=SECONDS) if arm=='hall' else solve(n,f,lib,steps=STEPS,seconds=SECONDS,use_hall=(arm=='multi'))
        conn.send(('result',r))
    except MemoryError:conn.send(('resource','memory'))
    except Exception as e:conn.send(('error',repr(e)))
    finally:conn.close()


def isolated(arm,n,f,lib):
    ctx=mp.get_context('fork');recv,send=ctx.Pipe(False);p=ctx.Process(target=worker,args=(send,arm,n,f,lib));start=time.monotonic();p.start();send.close()
    response=None
    try:
        if recv.poll(WALL):
            try:response=recv.recv()
            except EOFError:pass
    finally:
        recv.close()
        if response is None and p.is_alive():p.kill()
        p.join()
    wall=time.monotonic()-start
    if response is None:
        if p.exitcode not in (-signal.SIGKILL,-signal.SIGXCPU):raise RuntimeError(f'worker exit {p.exitcode}')
        r={'decision':'unknown','certificate':None,'work_steps':STEPS,'process_resource':'timeout_or_cpu_limit'}
    elif response[0]=='resource':r={'decision':'unknown','certificate':None,'work_steps':STEPS,'process_resource':response[1]}
    elif response[0]=='error':raise RuntimeError(response[1])
    else:
        if p.exitcode!=0:raise RuntimeError(f'worker exit {p.exitcode}')
        r=response[1]
    return {'result':r,'wall_seconds':wall}


def horn_controls():
    rng=random.Random(120920);counts=Counter()
    for _ in range(700):
        n=rng.randint(1,8);signs=[rng.choice([-1,1]) for _ in range(n)];f=[]
        for j in range(rng.randrange(25)):
            vs=rng.sample(range(1,n+1),rng.randrange(n+1));q=[-v for v in vs]
            if q and rng.randrange(2):q[0]=-q[0]
            f.append([x*signs[abs(x)-1] for x in q])
        r=_attempt(propagation,n,f,STEPS,SECONDS);assert r['decision']==('sat' if truth(n,f) else 'unsat');counts[r['decision']]+=1
    return dict(counts)


def probe(prior):
    lib=prior['library'];rows=[];counts=Counter();strata={};routes=Counter();sources=[]
    for i,row in enumerate(prior['rows']):sources.append({k:row[k] for k in ('n','clauses','kind','reference','model')}|{'archive_index':i,'reference_certificate':None})
    sources+=fresh()
    for i,row in enumerate(sources):
        n,f=row['n'],row['clauses'];arms={}
        names=['hall','multi','no_hall'];names=names[i%3:]+names[:i%3]
        for arm in names:
            a=isolated(arm,n,f,lib);r=a['result'];d=r['decision'];assert d in ('unknown',row['reference']) and 0<=r['work_steps']<=STEPS
            arms[arm]=a
            for c in (counts,strata.setdefault(row['kind'],Counter())):
                c[arm+'_'+d]+=1;c[arm+'_work']+=r['work_steps']
                if 'process_resource' in r:c[arm+'_process_resource']+=1
            if d!='unknown' and arm!='hall':routes[arm+'_'+r['attempts'][-1]['route']+'_'+d]+=1
        rows.append(dict(row,arms=arms))
    return {'library':lib,'rows':rows,'counts':dict(counts),'strata':{k:dict(v) for k,v in strata.items()},'routes':dict(routes),
            'horn_controls':horn_controls(),'envelope':{'work_steps':STEPS,'cooperative_seconds':SECONDS,'process_wall_seconds':WALL,'address_space_bytes':MEMORY,'cpu_cores':1},
            'scope':'archived and fresh synthetic development; fixed library; no external blinded holdout'}

if __name__=='__main__':print(json.dumps(probe(json.load(open(sys.argv[1]))),sort_keys=True))
