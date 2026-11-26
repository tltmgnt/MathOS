"""Exact original F038 decoder, tape_run and valid regression for B6."""
import json
import sys
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import (
    decode_tm, encode_tm, encoded, tape_run, valid,
)
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed


def replay(desc):
    q, table = decode_tm(desc)
    assert q == 278200 and len(desc) == 19474004
    assert encode_tm(table, q) == desc
    n, m, pins = 31, 2, (1, 0)
    clauses = pool(n)
    base = set(fixed(9, m, n, pins))
    sat = base | {(-1-2*g,) for g in range(9)}
    p = sum(1 << j for j, c in enumerate(clauses) if c in sat)
    clock = 44654867
    x = tape_run(clauses, n, p, desc, clock)
    assert x == 268348074 and valid(clauses, n, p, x)
    assert ''.join(str(x >> i & 1) for i in range(n)) == '0101010101010101011111111111000'
    assert tape_run(clauses, n, p, desc, clock-1) is None
    unsat = base | {(-2,), (-17,)}
    for g in range(8):
        unsat.update({(-(2*g+1), -(2*(g+1)+2)),
                      (-(2*g+2), -(2*(g+1)+1))})
    p = sum(1 << j for j, c in enumerate(clauses) if c in unsat)
    # Exact physical halt on UNSAT, not just a timeout from tape_run.
    tape = dict(enumerate(map(int, encoded(n, p, clauses))))
    state = head = 0
    for t in range(1, 54399245+1):
        state, w, d = table[3*state+tape.get(head, 2)]
        if w == 2:
            tape.pop(head, None)
        else:
            tape[head] = w
        head += d
        if state == q:
            break
    assert t == 54399245 and state == q and head == 39926 and head not in tape
    assert tape_run(clauses, n, p, desc, t) is None
    # Small original n=1 refusal must not look like an original witness.
    assert tape_run(pool(1), 1, 0, desc, 1000) is None
    # Per-description slot arithmetic; do not enumerate the whole stage.
    s = len(desc)+(clock-1).bit_length()
    assert s == 19474030
    assert 1 << (s-len(desc)) >= clock > 1 << (s-len(desc)-1)
    return dict(states=q, descriptor_bits=len(desc), sat_clock=clock,
                unsat_clock=t, witness=x, original_valid=True,
                one_step_short=True, blank_unsat=True, original_n1_refused=True,
                per_description_stage=s, stage_enumerated=False)


if __name__ == '__main__':
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
