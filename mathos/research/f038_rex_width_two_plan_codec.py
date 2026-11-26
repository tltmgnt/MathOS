"""Native original-format codec regression for REX-023B plan checkpoints."""
import json
import sys
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import (
    decode_tm, encode_tm, encoded, tape_run,
)
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed


def replay(desc):
    q, table = decode_tm(desc)
    assert q == 113660 and len(desc) == 7274244
    assert encode_tm(table, q) == desc
    n, m, pins = 31, 2, (0, 1)
    clauses = pool(n)
    active = set(fixed(9, m, n, pins)) | {(-1, -9, -17)}
    p = sum(1 << j for j, c in enumerate(clauses) if c in active)
    raw = encoded(n, p, clauses)
    tape = dict(enumerate(map(int, raw)))
    state = head = 0
    clock = 8080323
    for t in range(1, clock+1):
        state, w, d = table[3*state+tape.get(head, 2)]
        if w == 2:
            tape.pop(head, None)
        else:
            tape[head] = w
        head += d
        if state == q:
            break
    assert state == q and t == clock and head == len(raw)-1
    assert head not in tape
    plan = [(0,4,8),(1,9,9),(2,9,9),(3,9,9),(4,8,9),
            (5,9,9),(6,9,9),(7,9,9),(8,9,9)]
    expected = '0'*45+''.join(format(x,'04b') for r in plan for x in r)+'1'
    assert len(expected)==154
    assert ''.join(str(tape[head+1+i]) for i in range(154))==expected
    assert head+155 not in tape
    assert tape_run(clauses,n,p,desc,clock) is None
    return dict(states=q, descriptor_bits=len(desc), transitions=t,
                output_bits=154, plan_records=9, not_a_witness=True)


if __name__ == '__main__':
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
