"""Independent dictionary-tape replay using the original F038 descriptor codec."""
import json
import sys
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import (
    decode_tm, encode_tm, encoded, tape_run,
)
from mathos.research.f038_universal_witness_layout import pool


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


def replay(address, checkpoint):
    n = 31
    clauses = pool(n)
    # A deterministic nontrivial pool-shaped input, not asserted normalized.
    p = sum(1 << j for j in range(0, len(clauses), 97))
    raw = encoded(n, p, clauses)
    assert len(raw) == 37914
    results = []
    for desc, states, bits, clock, preserve in (
        (address, 11499, 632449, 3938318, False),
        (checkpoint, 11609, 638499, 3938295, True),
    ):
        decoded = decode_tm(desc)
        assert decoded is not None
        q, table = decoded
        assert q == states and len(desc) == bits
        assert encode_tm(table, q) == desc
        assert exact_run(q, table, raw, clock - 1) is None
        t, head, tape = exact_run(q, table, raw, clock)
        assert t == clock
        if not preserve:
            assert tape == {head: 1}
        else:
            assert head == len(raw) - 1 and head not in tape
            work = 4 * n.bit_length()
            sep = head - work - 1
            assert sep not in tape
            start = sep - len(clauses)
            assert ''.join(str(tape[i]) for i in range(start, sep)) == raw[n+1:]
            vals = [0] * 4
            for col in range(n.bit_length()):
                for lane in range(4):
                    vals[lane] |= tape[head - 4 * (col + 1) + lane] << col
            assert vals == [n, n-1, n, n]
            assert len(tape) == len(clauses) + work
        # Original witness-only API must not interpret either result as a witness.
        assert tape_run(clauses, n, p, desc, clock) is None
        results.append(dict(states=q, descriptor_bits=bits, transitions=t,
                            checkpoint=preserve, original_witness_refused=True))
    return dict(decoder_roundtrips=2, exact_replays=2, one_step_short=2,
                witness_refusals=2, results=results)


if __name__ == '__main__':
    print(json.dumps(replay(*(Path(p).read_text().strip() for p in sys.argv[1:]))))
