"""Independent standard-library checker for original-factor partition proofs.

No elimination trace or solver import. Leaf 0 proves infeasibility; leaf 1
proves a lower bound; [variable, children] covers every value of that variable.
"""
import argparse
import hashlib
import json
from pathlib import Path

MAX_BYTES = 8_000_000
MAX_NODES = 250_000
MAX_ROWS = 10_000_000


def require(ok):
    if not ok:
        raise ValueError('partition proof rejected')


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def unique(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out)
        out[key] = value
    return out


def fields(x, names):
    require(type(x) is dict and set(x) == set(names.split()))


def integer(x):
    return type(x) is int and abs(x) <= 10**100


def problem(p):
    fields(p, 'domains factors')
    d, fs = p['domains'], p['factors']
    require(type(d) is dict and len(d) <= 128 and all(type(v) is str and 0 < len(v) <= 128 and type(n) is int and 1 <= n <= 4 for v,n in d.items()))
    require(type(fs) is list and len(fs) <= 1024)
    out = []
    rows = 0
    for f in fs:
        require(type(f) is list and len(f) == 2)
        scope, table = f
        require(type(scope) is list and all(type(v) is str and v in d for v in scope) and len(set(scope)) == len(scope) and type(table) is list)
        tab = {}
        for row in table:
            rows += 1; require(rows <= MAX_ROWS)
            require(type(row) is list and len(row) == 2)
            ar,cost = row
            require(type(ar) is list and len(ar) == len(scope) and all(type(x) is int and 0 <= x < d[v] for v,x in zip(scope,ar)) and integer(cost))
            key = tuple(ar); require(key not in tab); tab[key] = cost
        out.append((tuple(scope), tab))
    return d,out


def components(d, fs):
    """Connected components derived from original scopes, not supplied by prover."""
    adjacent = {v:set() for v in d}
    for scope,_ in fs:
        for v in scope: adjacent[v].update(scope)
    pending = set(d); groups = []
    while pending:
        todo = [min(pending)]; group = set(todo); pending -= group
        while todo:
            for u in sorted(adjacent[todo.pop()] & pending):
                pending.remove(u); group.add(u); todo.append(u)
        groups.append(tuple(sorted(group)))
    owner = {v:i for i,g in enumerate(groups) for v in g}
    buckets = [[] for _ in groups]; constants = []
    for f in fs:
        if not f[0]: constants.append(f)
        else: buckets[owner[f[0][0]]].append(f)
    return constants, list(zip(groups,buckets))


def score(fs, w):
    total = 0
    for scope,tab in fs:
        c = tab.get(tuple(w[v] for v in scope))
        if c is None: return None
        total += c
    return total


class Budget:
    def __init__(self): self.nodes = self.rows = 0
    def node(self):
        self.nodes += 1; require(self.nodes <= MAX_NODES)
    def bound(self, fs, partial):
        total = 0
        for scope,tab in fs:
            fixed = [(i,partial[v]) for i,v in enumerate(scope) if v in partial]
            best = None
            for row,cost in tab.items():
                self.rows += 1; require(self.rows <= MAX_ROWS)
                if all(row[i] == x for i,x in fixed) and (best is None or cost < best): best = cost
            if best is None: return None
            total += best
        return total


def tree_check(tree, d, group, fs, target, budget, partial):
    budget.node()
    if type(tree) is int:
        require(tree in (0,1))
        lower = budget.bound(fs,partial)
        if tree == 0: require(lower is None)
        else: require(target is not None and lower is not None and lower >= target)
        return
    require(type(tree) is list and len(tree) == 2)
    v, children = tree
    require(type(v) is str and v in group and v not in partial and type(children) is list and len(children) == d[v])
    for x, child in enumerate(children):
        partial[v] = x; tree_check(child,d,group,fs,target,budget,partial)
    del partial[v]


def check(doc, expected=None):
    fields(doc,'schema problem optimum witness proofs')
    require(type(doc['schema']) is int and doc['schema'] == 1)
    d,fs = problem(doc['problem']); identity = digest(doc['problem'])
    if expected is not None: require(type(expected) is str and identity == expected)
    c,groups = components(d,fs); const = score(c,{})
    optimum,w,proofs = doc['optimum'], doc['witness'], doc['proofs']; budget = Budget()
    require(type(proofs) is list)
    if optimum is None:
        require(w is None)
        if const is None: require(proofs == [])
        else:
            require(len(proofs) == 1 and type(proofs[0]) is list and len(proofs[0]) == 2)
            i,tree = proofs[0]; require(type(i) is int and 0 <= i < len(groups))
            g,terms = groups[i]; tree_check(tree,d,g,terms,None,budget,{})
    else:
        require(integer(optimum) and type(w) is dict and set(w) == set(d) and all(type(w[v]) is int and 0 <= w[v] < d[v] for v in d))
        require(const is not None and score(fs,w) == optimum and len(proofs) == len(groups))
        for i,((g,terms),entry) in enumerate(zip(groups,proofs)):
            require(type(entry) is list and len(entry) == 2 and type(entry[0]) is int and entry[0] == i)
            target = score(terms,w); require(target is not None)
            tree_check(entry[1],d,g,terms,target,budget,{})
    return dict(problem_sha256=identity,proof_sha256=digest(doc),optimum=optimum,variables=len(d),nodes=budget.nodes,row_checks=budget.rows)


def load(path):
    with Path(path).open('rb') as f: raw = f.read(MAX_BYTES+1)
    require(len(raw) <= MAX_BYTES)
    return json.loads(raw,object_pairs_hook=unique)


if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('proof'); p.add_argument('--expect-problem',required=True); args=p.parse_args()
    try: print(json.dumps(check(load(args.proof),args.expect_problem),sort_keys=True))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError,OSError) as e: p.exit(1,'rejected: '+str(e)+'\n')
