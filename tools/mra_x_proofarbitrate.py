"""Phase XLII: bounded proof synthesis and format arbitration.
The unchanged standalone checkers are the acceptance boundary.
"""
import copy
import mra_x_boundproof as p
import mra_x_kernel as k


class Exhausted(ValueError): pass
class Counterexample(ValueError): pass


class Search:
    def __init__(self, nodes=12000, work=300000, entries=24000):
        p.require(type(nodes) is int and 1<=nodes<=p.MAX_NODES and type(work) is int and 1<=work<=p.MAX_ROWS and type(entries) is int and 1<=entries<=100000)
        self.limits=nodes,work,entries
        self.nodes=self.work=self.scans=self.hits=0
        self.cache={}; self.started=False

    def charge(self):
        if self.work>=self.limits[1]: raise Exhausted('search work')
        self.work+=1

    def node(self):
        if self.nodes>=self.limits[0]: raise Exhausted('search nodes')
        self.nodes+=1

    def minimum(self, i, scope, rows, partial):
        self.charge()
        fixed=tuple((j,partial[v]) for j,v in enumerate(scope) if v in partial)
        key=i,fixed
        if key in self.cache:
            self.hits+=1; return self.cache[key]
        best=None
        for row,cost in rows:
            self.charge(); self.scans+=1
            if all(row[j]==x for j,x in fixed):
                best=(row,cost); break
        if len(self.cache)<self.limits[2]: self.cache[key]=best
        return best

    def stats(self):
        return dict(nodes=self.nodes,work=self.work,row_scans=self.scans,cache_hits=self.hits,cache_entries=len(self.cache))


def generate(doc, search, *, adaptive=True):
    p.require(not search.started); search.started=True
    problem=copy.deepcopy(doc['problem']); d,fs=p.problem(problem)
    constants,groups=p.components(d,fs); optimum=doc['result']['optimum']; w=copy.deepcopy(doc['result']['witness'])
    proofs=[]; serial=0
    for i,(group,terms) in enumerate(groups):
        if optimum is None and p.score(constants,{}) is None: break
        # Unique occurrence IDs, including duplicate mathematical factors.
        indexed=[]
        for scope,tab in terms:
            indexed.append((serial,scope,sorted(tab.items(),key=lambda x:(x[1],x[0])))); serial+=1
        degree={v:sum(v in scope for scope,_ in terms) for v in group}
        target=None if optimum is None else p.score(terms,w)
        if optimum is not None: p.require(target is not None)
        def build(partial):
            search.node(); total=0; votes={}
            for j,scope,rows in indexed:
                m=search.minimum(j,scope,rows,partial)
                if m is None: return 0
                row,cost=m; total+=cost
                if adaptive:
                    for v,x in zip(scope,row):
                        if v not in partial: votes.setdefault(v,set()).add(x)
            if target is not None and total>=target: return 1
            rest=set(group)-set(partial)
            if not rest: raise Counterexample('claimed bound is false')
            # Prioritize inconsistent minimizing rows, then original degree.
            v=min(rest,key=lambda v:(-len(votes.get(v,())) if adaptive else 0,-degree[v],d[v],v))
            children=[]
            try:
                for x in range(d[v]):
                    partial[v]=x; children.append(build(partial))
            finally: del partial[v]
            return [v,children]
        try: tree=build({})
        except Counterexample:
            if optimum is not None: raise
            continue
        proofs.append([i,tree])
        if optimum is None: break
    if optimum is None and p.score(constants,{}) is not None and not proofs: raise Counterexample('no dead component')
    out=dict(schema=1,problem=problem,optimum=optimum,witness=w,proofs=proofs)
    if len(p.canonical(out))>p.MAX_BYTES: raise Exhausted('proof bytes')
    return out


def select(doc, expected, *, reads=4, nodes=12000, work=300000, entries=24000):
    """Choose a checked proof, attempting partition search for repeated retrieval.
    Size-based policy, not a prediction of wall-clock savings. Failed work is charged.
    """
    p.require(type(expected) is str and len(expected)==64 and p.digest(doc['problem'])==expected)
    p.require(type(reads) is int and 0<=reads<=10000)
    size=len(k.canonical(doc)); p.require(size<=k.MAX_BYTES)
    search=Search(nodes,work,entries); reason='single_read'
    if reads>=2:
        try:
            proof=generate(doc,search)
        except (Exhausted,Counterexample): reason='search_refused'
        else:
            try: receipt=p.check(proof,expected)
            except ValueError: reason='checker_refused'
            else:
                if len(p.canonical(proof))<size:
                    return dict(kind='partition',proof=proof,receipt=receipt,reason='smaller',search=search.stats())
                reason='not_smaller'
    receipt=k.check(doc,expected)
    return dict(kind='elimination',proof=doc,receipt=receipt,reason=reason,search=search.stats())
