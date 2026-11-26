"""Native original-format codec regression for REX-023C1."""
import json
import sys
from pathlib import Path
from itertools import combinations
from mathos.research.f038_unrestricted_universal_search import (
    decode_tm, encode_tm, encoded, tape_run,
)
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed


def replay(desc):
    q, table = decode_tm(desc)
    assert q == 421642 and len(desc) == 29514944
    assert encode_tm(table, q) == desc
    n, m, pins = 31, 2, (1,0)
    clauses = pool(n)
    active = set(fixed(9,m,n,pins)) | {(-1,-9,-17)}
    p = sum(1 << j for j,c in enumerate(clauses) if c in active)
    raw = encoded(n,p,clauses)
    tape = dict(enumerate(map(int,raw)))
    state = head = 0
    clock = 26693134
    for t in range(1,clock+1):
        state,w,d = table[3*state+tape.get(head,2)]
        if w == 2:
            tape.pop(head,None)
        else:
            tape[head] = w
        head += d
        if state == q:
            break
    assert state == q and t == clock and head == len(raw)-1
    assert head not in tape
    plan = [(0,4,8),(1,9,9),(2,9,9),(3,9,9),(4,8,9),
            (5,9,9),(6,9,9),(7,9,9),(8,9,9)]
    parents = [4,9,9,9,8,9,9,9,9]
    word = '0'*45+''.join(format(x,'04b') for r in plan for x in r)+'1'+''.join(format(x,'04b') for x in parents)
    assert len(word)==190
    assert ''.join(str(tape[head+1+i]) for i in range(190))==word
    end=head-26
    start=end-(len(raw)-32)
    assert ''.join(str(tape[i]) for i in range(start,end))==raw[32:]
    blocks = ['1' if h in [(0,4),(0,8),(4,8)] else '' for h in combinations(range(9),2)]
    blocks.append('10')
    for k in range(1,4):
        blocks.extend('10000000' if h==(0,4,8) else '0'*(2**k) for h in combinations(range(9),k))
    cursor=start-1
    for expected in blocks:
        assert cursor not in tape
        cursor-=1
        got=[]
        while cursor in tape:
            got.append(str(tape[cursor]))
            cursor-=1
        assert ''.join(got)==expected
    assert len(tape)==len(raw)-32+25+3+2+834+190
    assert tape_run(clauses,n,p,desc,clock) is None
    return dict(states=q, descriptor_bits=len(desc), transitions=t,
                output_bits=190, parent_records=9, mask_blocks=129,
                mask_bits=834, not_a_witness=True)


if __name__ == '__main__':
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
