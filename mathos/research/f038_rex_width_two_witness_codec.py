"""Native original-format codec, exact-clock interpreter and witness verifier."""
import json
import sys
from pathlib import Path
from itertools import product
from mathos.research.f038_unrestricted_universal_search import (
    decode_tm, encode_tm, encoded, tape_run, valid,
)
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed


def replay(desc):
    q, table = decode_tm(desc)
    assert q == 809925 and len(desc) == 59124529
    assert encode_tm(table, q) == desc
    n, m, pins = 31, 2, (1,0)
    clauses = pool(n)
    base = set(fixed(9,m,n,pins))
    active = base | {(-1,-9,-17)}
    p = sum(1 << j for j,c in enumerate(clauses) if c in active)
    clock = 34911962
    x = tape_run(clauses,n,p,desc,clock)
    assert x == 268260694 and valid(clauses,n,p,x)
    assert ''.join(str((x>>i)&1) for i in range(n)) == '0110101010101010101111111111000'
    assert tape_run(clauses,n,p,desc,clock-1) is None
    B = {tuple(-(2*g+b+1) for g,b in zip((0,4,8),z))
         for z in product(range(2),repeat=3) if z[1]!=z[2]}
    B.update({(-9,-17),(-10,-18)})
    active = base | B
    p = sum(1 << j for j,c in enumerate(clauses) if c in active)
    raw = encoded(n,p,clauses)
    tape = dict(enumerate(map(int,raw)))
    state = head = 0
    for t in range(1,34465372+1):
        state,w,d = table[3*state+tape.get(head,2)]
        if w == 2:
            tape.pop(head,None)
        else:
            tape[head] = w
        head += d
        if state == q:
            break
    assert t==34465372 and state==q and head==37913 and head not in tape
    assert tape_run(clauses,n,p,desc,t) is None
    assert tape_run(pool(1),1,0,desc,1000) is None
    return dict(states=q, descriptor_bits=len(desc), sat_clock=clock,
                witness=x, original_valid=True, one_step_short=True,
                unsat_clock=t, blank_unsat=True, n1_refused=True,
                per_description_slot=len(desc)+(clock-1).bit_length())


if __name__ == '__main__':
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
