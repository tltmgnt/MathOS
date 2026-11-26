"""Original F038 descriptor codec and independent dictionary-tape replay for B5."""
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
    assert q == 254151 and len(desc) == 17028121
    assert encode_tm(table, q) == desc
    n, m, pins = 31, 2, (1, 0)
    clauses = pool(n)
    selected = set(fixed(9, m, n, pins)) | {(-1-2*g,) for g in range(9)}
    p = sum(1 << j for j, c in enumerate(clauses) if c in selected)
    raw = encoded(n, p, clauses)
    tape = dict(enumerate(map(int, raw)))
    state = head = 0
    clock = 44149177
    producer = bridge = None
    protected = None
    row = '011' + '001010'*3 + '101'
    expected = '11111'+row+'110'+('11110'+row+'110')*6+'010'*7
    assert len(expected) == 245
    for t in range(clock):
        if state == 127040 and producer is None:
            producer = t
            assert head == len(raw)-1
            protected = {i: v for i, v in tape.items() if i < head}
            assert len(protected) == 38091
            assert ''.join(str(tape[head+1+i]) for i in range(245)) == expected
        if state == 127156 and bridge is None:
            bridge = t
            assert head == 40611
            assert {i:v for i,v in tape.items() if i >= len(raw)-1} == {
                head+i:int(v) for i,v in enumerate(expected)}
        state, w, d = table[3*state+tape.get(head, 2)]
        if w == 2:
            tape.pop(head, None)
        else:
            tape[head] = w
        head += d
        if state == q:
            break
    assert state == q and t+1 == clock
    assert producer == 41229674 and bridge == 42557335
    assert {i:v for i,v in tape.items() if i < len(raw)-1} == protected
    assert {i:v for i,v in tape.items() if i >= len(raw)-1} == {
        head+i:1 for i in range(7)}
    assert tape_run(clauses, n, p, desc, clock) is None
    return dict(states=q, descriptor_bits=len(desc), transitions=t+1,
                producer=producer, bridge=bridge-producer,
                worker=t+1-bridge, certificate="1111111",
                protected_cells=len(protected), tested_witness_refused=True)


if __name__ == '__main__':
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
