"""Original F038 codec and dictionary-tape regression for RE-X-022B3."""
import json
import sys
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import (
    decode_tm, encode_tm, encoded, tape_run,
)
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed


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
    assert q == 65275 and len(desc) == 3981779
    assert encode_tm(table, q) == desc
    n, m, pins = 31, 2, (1, 0)
    clauses = pool(n)
    base = set(fixed(9, m, n, pins))
    cross = {(-1,), (-3,), (-5,), (-1, -3), (-1, -3, -5)}
    results = []
    for name, active, clock, output in (
        ("mixed", base | cross, 7649152, None),
        ("outside", base | {(-1, -17)}, 7687297, 1),
        ("outside_malformed", (base | {(-1, -17)}) - {(28, -30, -31)}, None, 0),
    ):
        p = sum(1 << j for j, c in enumerate(clauses) if c in active)
        raw = encoded(n, p, clauses)
        assert len(raw) == 37914
        t, head, tape = exact_run(q, table, raw, 10000000)
        if clock is not None:
            assert t == clock
        if output is not None:
            assert tape == {head: output}
        else:
            assert head == len(raw)-1 and head not in tape
            work = 15 + 5*m.bit_length()
            end = head-work-1
            start = end-len(clauses)
            assert end not in tape
            assert ''.join(str(tape[i]) for i in range(start, end)) == raw[n+1:]
            expected = [[] for _ in range(49)]
            for c in clauses:
                if not all(-9*m <= x < 0 for x in c):
                    continue
                groups = [(-x-1)//m for x in c]
                if len(set(groups)) != len(groups):
                    continue
                for j in range(7):
                    if all(j <= g <= j+2 for g in groups):
                        mask = sum(1 << (g-j) for g in groups)
                        expected[7*j+mask-1].append(int(c in active))
            expected.append(list(pins))
            cursor = start-1
            for block in expected:
                assert cursor not in tape
                cursor -= 1
                got = []
                while cursor in tape:
                    got.append(tape[cursor])
                    cursor -= 1
                assert got == block
            assert sum(map(len, expected)) == 184
            assert len(tape) == len(clauses)+work+184
            assert exact_run(q, table, raw, t-1) is None
        # Mask checkpoints and single-bit rejection results are not n-bit witnesses.
        assert tape_run(clauses, n, p, desc, t) is None
        results.append(dict(name=name, transitions=t, witness_refused=True))
    return dict(decoder_roundtrips=1, exact_replays=3, one_step_short=1,
                mask_blocks=49, mask_bits=182, witness_refusals=3, results=results)


if __name__ == '__main__':
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
