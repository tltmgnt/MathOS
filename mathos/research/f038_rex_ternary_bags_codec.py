"""Original F038 descriptor codec and witness-interface regression for B4."""
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
    assert q == 127040 and len(desc) == 8130564
    assert encode_tm(table, q) == desc
    n, m, pins = 31, 2, (1, 0)
    clauses = pool(n)
    selected = set(fixed(9, m, n, pins)) | {(-1-2*g,) for g in range(9)}
    p = sum(1 << j for j, c in enumerate(clauses) if c in selected)
    raw = encoded(n, p, clauses)
    tape = dict(enumerate(map(int, raw)))
    state = head = 0
    clock = 41229674
    for t in range(1, clock+1):
        state, w, d = table[3*state+tape.get(head, 2)]
        if w == 2:
            tape.pop(head, None)
        else:
            tape[head] = w
        head += d
        if state == q:
            break
    assert t == clock and state == q and head == len(raw)-1
    assert head not in tape
    row = '011' + '001010'*3 + '101'
    expected = '11111'+row+'110'+('11110'+row+'110')*6+'010'*7
    assert len(expected) == 245
    assert ''.join(str(tape[head+1+i]) for i in range(len(expected))) == expected
    assert head+1+len(expected) not in tape
    assert tape_run(clauses, n, p, desc, clock) is None
    return dict(states=q, descriptor_bits=len(desc), prepared_bits=len(expected),
                transitions=t, original_witness_refused=True)


if __name__ == '__main__':
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
