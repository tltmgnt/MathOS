"""Bounded, topology-specialized, one-tape elimination machine (not original RE-X).
Finite alphabet and control; input costs never used by compiler. Standard library.
"""
import argparse
import hashlib
import itertools
import json
import math
import random
from pathlib import Path
import mra_x_topology as ref


class Machine:
    def __init__(self, domains, scopes, order, cost_cap=10):
        self.domains = dict(domains)
        self.scopes = tuple(tuple(s) for s in scopes)
        self.order = tuple(order)
        if not 1 <= cost_cap <= 16 or len(domains)>8 or len(scopes)>32:
            raise ValueError('outside bounded compilation envelope')
        if any(type(d) is not int or not 1<=d<=4 for d in domains.values()):
            raise ValueError('domain outside envelope')
        ref.validate(domains, [(s,{}) for s in self.scopes])
        if len(order)!=len(domains) or set(order)!=set(domains):
            raise ValueError('bad order')
        self.cap=cost_cap
        self.bound=max(4, len(scopes)*cost_cap)
        self.size=0; self.code=[]; self.inputs=[]; self.records=[]
        def cell():
            if self.size>=20000: raise ValueError('tape layout budget')
            self.size+=1; return self.size-1
        def table(scope):
            return {a:cell() for a in ref.assignments(domains,scope)}
        def emit(op, pos=None, literal=None):
            if len(self.code)>=200000: raise ValueError('control program budget')
            self.code.append((op,pos,literal))
        active=[]
        for scope in self.scopes:
            t=table(scope); active.append((scope,t)); self.inputs.append(t)
        self.optimum_cell=cell(); self.witness_cells={v:cell() for v in domains}
        for v in order:
            bucket=[(s,t) for s,t in active if v in s]
            active=[(s,t) for s,t in active if v not in s]
            boundary=tuple(sorted({u for s,_ in bucket for u in s if u!=v}))
            projected=table(boundary); back=table(boundary)
            for row in projected:
                a=dict(zip(boundary,row)); emit('best_reset')
                for x in range(domains[v]):
                    a[v]=x; emit('sum_reset')
                    for s,t in bucket: emit('add',t[tuple(a[u] for u in s)])
                    emit('consider',literal=x)
                emit('best_write',projected[row]); emit('arg_write',back[row])
            active.append((boundary,projected)); self.records.append((v,boundary,back))
        emit('sum_reset')
        for s,t in active:
            if s: raise ValueError('nonconstant terminal factor')
            emit('add',t[()])
        emit('sum_write',self.optimum_cell)
        for v,boundary,back in reversed(self.records):
            emit('selected_reset')
            for row,p in back.items():
                emit('match_reset')
                for u,x in zip(boundary,row): emit('match',self.witness_cells[u],x)
                emit('take',p)
            emit('selected_write',self.witness_cells[v])
        self.code=tuple(self.code)

    def input(self, factors):
        if tuple(tuple(s) for s,_ in factors)!=self.scopes: raise ValueError('scope mismatch')
        ref.validate(self.domains,factors)
        tape=[None]*self.size
        for (_,t),layout in zip(factors,self.inputs):
            for row,c in t.items():
                if abs(c)>self.cap: raise ValueError('cost outside alphabet envelope')
                tape[layout[row]]=c
        return tape

    def transition(self,state,symbol):
        """One deterministic transition: bounded state, one symbol, move -1/0/+1."""
        pc,pos,acc,best,arg,match,selected=state
        op,target,literal=self.code[pc]
        if target is not None and target!=pos:
            move=1 if target>pos else -1
            return (pc,pos+move,acc,best,arg,match,selected),symbol,move
        out=symbol
        if op=='best_reset': best=arg=None
        elif op=='sum_reset': acc=0
        elif op=='add':
            acc=None if acc is None or symbol is None else acc+symbol
            if acc is not None and abs(acc)>self.bound: raise ValueError('finite control bound exceeded')
        elif op=='consider':
            if acc is not None and (best is None or acc<best): best,arg=acc,literal
        elif op=='best_write': out=best
        elif op=='arg_write': out=arg
        elif op=='sum_write': out=acc
        elif op=='selected_reset': selected=None
        elif op=='match_reset': match=True
        elif op=='match': match=match and symbol==literal
        elif op=='take':
            if match: selected=symbol
        elif op=='selected_write': out=selected if acc is not None else None
        else: raise ValueError('invalid control instruction')
        return (pc+1,pos,acc,best,arg,match,selected),out,0

    def run(self,tape,state=None,limit=20_000_000):
        """One tape, no random reads/writes in execution; resume from a saved configuration."""
        tape=list(tape)
        if len(tape)!=self.size or any(x is not None and (type(x) is not int or abs(x)>self.bound) for x in tape):
            raise ValueError('invalid tape')
        state=(0,0,0,None,None,False,None) if state is None else tuple(state)
        steps=moves=0
        while state[0]<len(self.code) and steps<limit:
            pos=state[1]
            state,out,move=self.transition(state,tape[pos]); tape[pos]=out
            if state[1]!=pos+move: raise ValueError('head motion mismatch')
            steps+=1; moves+=bool(move)
        return {'state':state,'tape':tape,'halted':state[0]==len(self.code),'transitions':steps,'head_moves':moves}

    def decode(self,result):
        if not result['halted']: raise ValueError('machine did not halt')
        t=result['tape']; optimum=t[self.optimum_cell]
        witness=None if optimum is None else {v:t[p] for v,p in self.witness_cells.items()}
        trace=[[v,list(s),[[list(row),t[p]] for row,p in back.items() if t[p] is not None]] for v,s,back in self.records]
        return {'optimum':optimum,'witness':witness,'trace':trace}


def require(ok):
    if not ok: raise ValueError('differential check failed')


def audit():
    rng=random.Random(38020)
    families={
        'isolated':(3,[(0,), (1,)]), 'chain':(4,[(0,1),(1,2),(2,3)]),
        'star':(4,[(0,1),(0,2),(0,3)]), 'joint':(4,[(0,1,2),(0,1,3)]),
        'wide':(5,[(0,1,2,3,4)]), 'nested':(5,[(0,1,2),(1,2,3),(3,4)]),
        'cycle':(4,[(0,1),(1,2),(2,3),(3,0)]),
        'grid':(6,[(0,1),(1,2),(3,4),(4,5),(0,3),(1,4),(2,5)]),
        'dense':(4,list(itertools.combinations(range(4),2))),
        'hypergraph':(5,[(0,1,2),(1,3,4),(0,4)]),
        'dynamic':(4,[(0,1),(1,2),(2,3),(0,3)])}
    stats={}; totals=dict(cases=0,feasible=0,infeasible=0,transitions=0,head_moves=0,max_tape_cells=0,max_program_instructions=0,max_induced_width=0)
    def check(name,m,fs,resume=False):
        tape=m.input(fs); result=m.run(tape)
        got=m.decode(result); expected=ref.solve(m.domains,fs,m.order)
        require(got=={k:expected[k] for k in got} and got['optimum']==ref.brute(m.domains,fs))
        if got['witness'] is not None: require(ref.score(fs,got['witness'])==got['optimum'])
        if resume:
            part=m.run(tape,limit=max(1,result['transitions']//2))
            snap=json.loads(json.dumps(part)); rest=m.run(snap['tape'],snap['state'])
            require(rest['tape']==result['tape'] and rest['state']==result['state'] and part['transitions']+rest['transitions']==result['transitions'])
        s=stats.setdefault(name,dict(cases=0,transitions=0,feasible=0,infeasible=0,max_induced_width=0))
        for a in (s,totals):
            a['cases']+=1; a['transitions']+=result['transitions']; a['feasible' if got['optimum'] is not None else 'infeasible']+=1
            a['max_induced_width']=max(a['max_induced_width'],expected['induced_width'])
        totals['head_moves']+=result['head_moves']; totals['max_tape_cells']=max(totals['max_tape_cells'],m.size); totals['max_program_instructions']=max(totals['max_program_instructions'],len(m.code))
    for name,(n,scopes) in families.items():
        d={str(i):2+(i==0) for i in range(n)}; scopes=[tuple(map(str,s)) for s in scopes]
        if name=='dynamic': variants=[scopes[:-1],scopes,scopes[1:]]
        else: variants=[scopes]
        for ss in variants:
            order=ref.min_fill(d,[(s,{}) for s in ss]); m=Machine(d,ss,order)
            for trial in range(4):
                target={v:rng.randrange(k) for v,k in d.items()}
                fs=[]
                for s in ss:
                    t={a:rng.randint(-4,8) for a in ref.assignments(d,s) if rng.random()<.75}
                    t.setdefault(tuple(target[v] for v in s),0); fs.append((s,t))
                if trial==0: fs[0]=(ss[0],{})
                check(name,m,fs,resume=trial==1)
    d={'a':2,'b':2}; s=('a','b'); m=Machine(d,[s],['a','b'],1)
    for values in itertools.product((None,-1,0,1),repeat=4):
        fs=[(s,{a:c for a,c in zip(ref.assignments(d,s),values) if c is not None})]
        check('exhaustive_binary_factor',m,fs)
    for d,fs in [({},[]),({},[((),{})]),({},[((),{():-3})]),({'x':1},[]),({'x':2},[(('x',),{(0,):0}),(('x',),{(1,):0})])]:
        check('boundary',Machine(d,[s for s,_ in fs],list(d)),fs)
    out={'totals':totals,'families':stats,'resume_checks':13,'scope':'bounded topology-specialized finite-alphabet one-tape simulator; no original RE-X integration, uniform machine, bit-level bounds or mechanized proof','source_sha256':{Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (__file__,ref.__file__)}}
    out['evidence_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps(r,indent=2))
