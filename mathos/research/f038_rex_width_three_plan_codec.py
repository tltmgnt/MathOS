"""REX-024B native original-format structural checkpoint, not witness admission."""
import json
import sys
from itertools import combinations
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import decode_tm, encode_tm, encoded, tape_run
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed


def replay(desc):
    q, table = decode_tm(desc)
    assert q == 124438 and len(desc) == 7964036
    assert encode_tm(table, q) == desc
    n, m, pins = 31, 2, (0,1)
    clauses = pool(n)
    edges = list(combinations(range(9),2))
    graph = {(0,1),(0,2),(0,6),(1,3),(1,8),(2,5),(2,7),(3,6),
             (3,7),(3,8),(4,6),(5,8),(6,7),(7,8)}
    active = set(fixed(9,m,n,pins)) | {(-(2*a+1),-(2*b+1)) for a,b in graph}
    p = sum(1 << j for j,c in enumerate(clauses) if c in active)
    raw = encoded(n,p,clauses)
    tape = dict(enumerate(map(int,raw)))
    state = head = 0
    clock = 8277570
    for t in range(1,clock+1):
        state,w,d = table[3*state+tape.get(head,2)]
        if w == 2:
            tape.pop(head,None)
        else:
            tape[head] = w
        head += d
        if state == q:
            break
    assert state == q and t == clock and head == len(raw)-1 and head not in tape
    order = [1,2,4,5,6,0,3,7,8]
    G = [set() for _ in range(9)]
    for a,b in graph:
        G[a].add(b)
        G[b].add(a)
    remaining = set(range(9))
    for i,v in enumerate(order+[9]):
        tried = {x for x in remaining if x<=v and len(G[x])<=3}
        word = ''.join(str(int(b in G[a])) for a,b in edges)
        word += ''.join(str(int(x in remaining)) for x in range(9))
        word += ''.join(str(int(x in tried)) for x in range(9))
        word += format(v,'04b')+str(int(i==0))*2
        h = head+61*i
        assert h not in tape and ''.join(str(tape[h+1+j]) for j in range(60)) == word
        if v != 9:
            ns = sorted(G[v])
            for a,b in combinations(ns,2):
                G[a].add(b)
                G[b].add(a)
            for a in ns:
                G[a].remove(v)
            G[v].clear()
            remaining.remove(v)
    assert head+610 not in tape
    end=head-26
    start=end-(len(raw)-32)
    assert ''.join(str(tape[i]) for i in range(start,end))==raw[32:]
    cursor=start-1
    for expected in ['1' if e in graph else '' for e in edges]+['01']:
        assert cursor not in tape
        cursor-=1
        got=[]
        while cursor in tape:
            got.append(str(tape[cursor]))
            cursor-=1
        assert ''.join(got)==expected
    assert len(tape)==len(raw)-32+25+14+2+600
    assert tape_run(clauses,n,p,desc,clock) is None
    return dict(states=q, descriptor_bits=len(desc), transitions=t,
                frames=10, order=order, not_a_witness=True)


if __name__ == '__main__':
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
