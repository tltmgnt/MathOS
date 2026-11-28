"""Rollback Gaussian state with checked native explanations."""
from collections import defaultdict
from . import pnp_native_xor_conflict as native


def indices(mask):
    while mask:
        bit=mask & -mask
        yield bit.bit_length()
        mask ^= bit


class Incremental:
    def __init__(self,masks,b):
        self.basis={}
        self.columns=defaultdict(set)
        self.units=set()
        self.frames=[]
        self.trail=[]
        self.true=self.assigned=0
        self.bad=None
        self.log_size=self.incidence=0
        for i,(m,r) in enumerate(masks):
            b.tick()
            row=(m,r,m,1<<i)
            # Eliminate existing pivot columns; reduced rows contain
            # no other pivot, so this loop needs no new pivots.
            for v in list(indices(m)):
                b.tick()
                if v in self.basis:
                    row=self.combine(row,self.basis[v])
            self.insert(row,None,b)
            if self.bad is not None:
                break
        self.cap(b)

    @staticmethod
    def combine(a,c):
        return tuple(x^y for x,y in zip(a,c))

    def cap(self,b):
        b.cells(4*(len(self.basis)+self.log_size)+self.incidence+len(self.frames))

    def replace(self,p,row,changes,b):
        old=self.basis.get(p)
        if old==row:
            return
        b.tick()
        if changes is not None:
            changes.append((p,old))
            self.log_size+=1
        before=old[0] if old is not None else 0
        after=row[0] if row is not None else 0
        self.incidence+=after.bit_count()-before.bit_count()
        for v in indices(before^after):
            b.tick()
            if before>>(v-1)&1:
                self.columns[v].remove(p)
                if not self.columns[v]:
                    del self.columns[v]
            else:
                self.columns[v].add(p)
        self.units.discard(p)
        if row is None:
            del self.basis[p]
        else:
            self.basis[p]=row
            if after.bit_count()==1:
                self.units.add(p)

    def insert(self,row,changes,b):
        m,r,full,prov=row
        if not m:
            if r:
                self.bad=row
            return
        p=m.bit_length()
        if p in self.basis:
            raise AssertionError('uneliminated pivot')
        for q in sorted(self.columns.get(p,())):
            b.tick()
            self.replace(q,self.combine(self.basis[q],row),changes,b)
        self.replace(p,row,changes,b)

    def push(self,x,b):
        v=abs(x)
        bit=1<<(v-1)
        if self.assigned & bit:
            raise ValueError('repeated trail variable')
        changes=[]
        oldbad=self.bad
        self.assigned |= bit
        if x>0:
            self.true |= bit
        for p in sorted(self.columns.get(v,())):
            b.tick()
            m,r,full,prov=self.basis[p]
            row=(m^bit,r^int(x>0),full,prov)
            if p==v:
                self.replace(p,None,changes,b)
                self.insert(row,changes,b)
            else:
                self.replace(p,row,changes,b)
        self.trail.append(x)
        self.frames.append((changes,oldbad))
        self.cap(b)

    def pop(self,b):
        x=self.trail.pop()
        changes,self.bad=self.frames.pop()
        self.assigned ^= 1<<(abs(x)-1)
        if x>0:
            self.true ^= 1<<(x-1)
        for p,old in reversed(changes):
            self.replace(p,old,None,b)
            self.log_size-=1
        self.cap(b)

    def explain(self,row,lit,b):
        _,_,full,prov=row
        b.tick(1+full.bit_count()+prov.bit_count())
        c=[lit if lit is not None and v==abs(lit)
           else -v if self.true>>(v-1)&1 else v for v in indices(full)]
        return {'kind':'xor','clause':sorted(c),'rows':[i-1 for i in indices(prov)]},lit

    def sync(self,trail,b):
        common=0
        for a,c in zip(self.trail,trail):
            b.tick()
            if a!=c:
                break
            common+=1
        while len(self.trail)>common:
            self.pop(b)
        for x in trail[common:]:
            if self.bad is not None:
                break
            b.tick()
            self.push(x,b)
        if self.bad is not None:
            return [self.explain(self.bad,None,b)]
        out=[]
        for p in sorted(self.units):
            b.tick()
            row=self.basis[p]
            out.append(self.explain(row,p if row[1] else -p,b))
        return out


def compress(result,b):
    """Prune unused source rows, preserving event order and clause content."""
    if result['decision']!='unsat':
        return result
    p=result['certificate']
    used=set()
    for e in p['events']:
        b.tick(1+len(e.get('rows',())))
        if e['kind']=='xor':
            used.update(e['rows'])
    # Native verifier requires at least one source row even for RUP-only proofs.
    keep=sorted(used or {0})
    index={old:new for new,old in enumerate(keep)}
    events=[]
    for e in p['events']:
        b.tick(1+len(e.get('rows',())))
        events.append(dict(e,rows=[index[i] for i in e['rows']]) if e['kind']=='xor' else e)
    b.tick(len(keep))
    return dict(result,certificate={'rows':[p['rows'][i] for i in keep],'events':events})


def attempt(n,clauses,total,seconds,*,prune=True):
    return native.attempt(n,clauses,total,seconds,state_factory=Incremental,
                          transform=compress if prune else None)
