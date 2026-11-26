"""Replay RE-X descriptors through the original decoder and witness-only interpreter."""
import json
import sys
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import (
    decode_tm, encode_tm, encoded, tape_run, valid,
)
from mathos.research.f038_universal_witness_layout import pool


def replay(expand, pack, roundtrip):
    for d, q in ((expand, 18), (pack, 18), (roundtrip, 36)):
        decoded = decode_tm(d)
        assert decoded is not None and decoded[0] == q
        assert encode_tm(decoded[1], q) == d
    cases = 0
    accepted = 0
    for n in (1, 2):
        C = pool(n)
        for p in range(1 << len(C)):
            L = len(encoded(n, p, C))
            clock = 10*L*(L+1) + 13*L + 6
            assert tape_run(C, n, p, roundtrip, clock-1) is None
            x = tape_run(C, n, p, roundtrip, clock)
            assert x == (1 << n)-1
            accepted += int(valid(C, n, p, x))
            cases += 1
    # A satisfiable input requiring x1=0: the identity codec is NOT a solver.
    C = pool(2)
    assert valid(C, 2, 1, 0)
    L = len(encoded(2, 1, C))
    x = tape_run(C, 2, 1, roundtrip, 10*L*(L+1)+13*L+6)
    assert x == 3 and not valid(C, 2, 1, x)
    assert cases == 260 and accepted == 34
    return {'decoder_roundtrips': 3, 'selector_replays': cases,
            'one_step_short_timeouts': cases, 'valid_witnesses': accepted,
            'identity_is_not_solver': True}


if __name__ == '__main__':
    print(json.dumps(replay(*(Path(p).read_text().strip() for p in sys.argv[1:]))))
