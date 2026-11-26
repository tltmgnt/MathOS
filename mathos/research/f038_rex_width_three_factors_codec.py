"""REX-024C1 native original-format structural checkpoint, not witness admission."""
import json
import sys
from itertools import combinations, product
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import decode_tm, encode_tm, encoded, tape_run
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed


def replay(desc):
    q, table = decode_tm(desc)
    assert q == 485080 and len(desc) == 33955604
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
    clock = 26957865
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
        if v != 9:
            ns = sorted(G[v])
            parent = next((x for x in order[i+1:] if x in ns), 9)
            a,b,c = ns+[9]*(3-len(ns))
            word += ''.join(format(x,'04b') for x in (a,b,c,parent))
            word += ''.join(str(int(x)) for x in (True,a!=9,b!=9,c!=9,b!=9,c!=9,c!=9))+'0'
        else:
            word += '0'*24
        h = head+85*i
        assert h not in tape and ''.join(str(tape[h+1+j]) for j in range(84)) == word
        if v != 9:
            ns = sorted(G[v])
            for a,b in combinations(ns,2):
                G[a].add(b)
                G[b].add(a)
            for a in ns:
                G[a].remove(v)
            G[v].clear()
            remaining.remove(v)
    assert head+850 not in tape
    end=head-26
    start=end-(len(raw)-32)
    assert ''.join(str(tape[i]) for i in range(start,end))==raw[32:]
    cursor=start-1
    blocks = ['1' if e in graph else '' for e in edges]+['01']
    for k in range(1,4):
        for scope in combinations(range(9),k):
            blocks.append(''.join(str(int(k==2 and scope in graph and not any(z)))
                                  for z in product(range(2),repeat=k)))
    for expected in blocks:
        assert cursor not in tape
        cursor-=1
        got=[]
        while cursor in tape:
            got.append(str(tape[cursor]))
            cursor-=1
        assert ''.join(got)==expected
    assert len(tape)==len(raw)-32+25+14+2+834+840
    assert tape_run(clauses,n,p,desc,clock) is None
    return dict(states=q, descriptor_bits=len(desc), transitions=t,
                frames=10, order=order, mask_blocks=129, mask_bits=834, not_a_witness=True)


if __name__ == '__main__':
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
