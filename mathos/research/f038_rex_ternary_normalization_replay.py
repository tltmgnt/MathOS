"""Original descriptor-codec and independent sparse-tape regression for RE-X-022B2."""
import json
import sys
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import (
    decode_tm, encode_tm, encoded, tape_run, valid,
)
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed, witness


def exact_run(q, table, raw, budget):
    tape = dict(enumerate(map(int, raw)))
    state = head = 0
    for t in range(1, budget + 1):
        state, write, move = table[3 * state + tape.get(head, 2)]
        if write == 2:
            tape.pop(head, None)
        else:
            tape[head] = write
        head += move
        if state == q:
            return t, head, tape
    return None


def replay(desc):
    decoded = decode_tm(desc)
    assert decoded is not None
    q, table = decoded
    assert q == 40333 and len(desc) == 2460317
    assert encode_tm(table, q) == desc
    n, m, pins = 31, 2, (1, 0)
    clauses = pool(n)
    base = set(fixed(9, m, n, pins))
    results = []
    for name, active, clock, output in (
        ("normalized_unsat", base | {(-1,), (-2,)}, 5139764, None),
        ("outside_sat", base | {(-1, -17)}, 5177675, 1),
        ("missing_pin", base - {(28, -30, -31)}, None, 0),
    ):
        assert active != base or name != "missing_pin"
        p = sum(1 << j for j, c in enumerate(clauses) if c in active)
        raw = encoded(n, p, clauses)
        assert len(raw) == 37914
        t, head, tape = exact_run(q, table, raw, 10000000)
        if clock is not None:
            assert t == clock
        if output is not None:
            assert tape == {head: output}
        else:
            assert head == len(raw) - 1 and head not in tape
            work = 15 + 5 * m.bit_length()
            end = head - work - 1
            start = end - len(clauses)
            assert end not in tape
            assert ''.join(str(tape[i]) for i in range(start, end)) == raw[n+1:]
            assert len(tape) == len(clauses) + work
            groups = []
            for g in range(3):
                groups.append(int(''.join(str(tape[head-15+5*g+j])
                                          for j in range(5)), 2))
            assert groups == [19, 20, 20]
            vals = [0] * 5
            for col in range(m.bit_length()):
                for lane in range(5):
                    vals[lane] |= tape[head-15-5*(col+1)+lane] << col
            assert vals == [1, 0, 0, 0, 0]
            assert exact_run(q, table, raw, t-1) is None
        assert tape_run(clauses, n, p, desc, t) is None
        if name == "outside_sat":
            assert valid(clauses, n, p, witness(9, m, n, pins, (1,)*9))
        results.append(dict(name=name, transitions=t, witness_refused=True))
    return dict(decoder_roundtrips=1, exact_replays=3, one_step_short=1,
                witness_refusals=3, results=results)


if __name__ == '__main__':
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
