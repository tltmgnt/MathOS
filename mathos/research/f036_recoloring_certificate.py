"""Polynomial-size recoloring certificates from graph structure.

A graph-level UNSAT fragment for the standard 3-coloring CNF encoding.
The discovery procedure is independent of any supplied Mycielski labels.
None means UNKNOWN. No general SAT completeness claim.
"""
from collections import deque
from dataclasses import dataclass
from itertools import combinations
from random import Random
from mathos.research.f036_coloring_gap import colorable


@dataclass(frozen=True)
class Certificate:
    apex: int
    walk: tuple
    witnesses: tuple


def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for u,v in edges:
        if not (0 <= u < n and 0 <= v < n and u != v):
            raise ValueError("not a simple undirected graph")
        adj[u].add(v)
        adj[v].add(u)
    return adj


def check(n, edges, cert):
    adj = adjacency(n, edges)
    walk, ws = cert.walk, cert.witnesses
    k = len(walk)
    if (k < 3 or k%2 == 0 or len(ws) != k
            or not 0 <= cert.apex < n
            or any(not 0 <= v < n for v in (*walk,*ws))):
        return False
    return all(walk[(i+1)%k] in adj[v]
               and ws[i] in adj[cert.apex]
               and ws[i] in adj[walk[i-1]]
               and ws[i] in adj[walk[(i+1)%k]]
               for i,v in enumerate(walk))


def discover(n, edges):
    adj = adjacency(n, edges)
    states = [(u,v) for u in range(n) for v in sorted(adj[u])]
    index = {s:i for i,s in enumerate(states)}
    for w in range(n):
        transitions = [[] for _ in states]
        for i,(u,v) in enumerate(states):
            for z in sorted(adj[v]):
                candidates = adj[w] & adj[u] & adj[z]
                if candidates:
                    transitions[i].append((index[v,z],min(candidates)))
        for i in range(len(states)):
            start, goal = 2*i, 2*i+1
            queue = deque([start])
            parent = {start:None}
            while queue and goal not in parent:
                a = queue.popleft()
                for j,s in transitions[a//2]:
                    b = 2*j+1-(a%2)
                    if b not in parent:
                        parent[b] = (a,s)
                        queue.append(b)
            if goal in parent:
                walk, ws = [], []
                b = goal
                while b != start:
                    a,s = parent[b]
                    walk.append(states[a//2][1])
                    ws.append(s)
                    b = a
                cert = Certificate(w,tuple(reversed(walk)),tuple(reversed(ws)))
                assert check(n,edges,cert)
                return cert
    return None


def mycielski(n, base):
    return list(base)+[(a,n+b) for a,b in base]+[(b,n+a) for a,b in base]+[(n+i,2*n) for i in range(n)]


def run():
    rng = Random(3604)
    positives = negatives = extra = accepted = 0
    for k in range(5,32,2):
        base = [(i,(i+1)%k) for i in range(k)]
        n,edges = 2*k+1,mycielski(k,base)
        for j in range(3):
            perm = list(range(n))
            rng.shuffle(perm)
            g = [(perm[a],perm[b]) for a,b in edges]
            if j == 2:
                g.append((perm[k],perm[k+1]))
                extra += 1
            rng.shuffle(g)
            cert = discover(n,g)
            assert cert is not None and check(n,g,cert)
            positives += 1
        b = [(i,(i+1)%(k+1)) for i in range(k+1)]
        assert discover(2*k+3,mycielski(k+1,b)) is None
        negatives += 1
    for _ in range(256):
        n = 7
        edges = [(u,v) for u,v in combinations(range(n),2) if rng.random()<0.45]
        cert = discover(n,edges)
        if cert is not None:
            assert check(n,edges,cert) and not colorable(n,edges,3)
            accepted += 1
    edges = mycielski(5,[(i,(i+1)%5) for i in range(5)])
    cert = discover(11,edges)
    assert cert is not None
    assert not check(11,edges,Certificate(cert.apex,cert.walk[:-1],cert.witnesses[:-1]))
    assert not check(11,edges,Certificate(cert.apex,cert.walk,(cert.apex,)+cert.witnesses[1:]))
    assert not check(11,[],cert)
    print(f"random accepted={accepted}")
    print(f"F036_RECOLORING_OK unsat={positives} sat={negatives} extra={extra} random=256 rejection=3")


if __name__=="__main__":
    run()
