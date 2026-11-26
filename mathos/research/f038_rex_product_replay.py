"""Replay the actual fixed product descriptors using original U semantics."""
import json
import sys
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import (
    decode_tm, encode_tm, encoded, tape_run, valid,
)
from mathos.research.f038_universal_witness_layout import pool


def replay(prefix, grouped):
    for d, q in ((prefix, 371), (grouped, 607)):
        a = decode_tm(d)
        assert a is not None and a[0] == q
        assert encode_tm(a[1], q) == d
    counts = {"selector_inputs": 0, "prefix_valid": 0,
              "prefix_timeouts": 0, "group_valid": 0, "group_blank": 0}
    for n in (1, 2):
        C = pool(n)
        for p in range(1 << len(C)):
            raw = encoded(n, p, C)
            N = len(raw)
            clock = 10*N*N + 51*N + 63
            assert tape_run(C, n, p, prefix, clock-1) is None
            x = tape_run(C, n, p, prefix, clock)
            assert x == (1 << n)-1
            counts["prefix_timeouts"] += 1
            counts["prefix_valid"] += int(valid(C,n,p,x))
            # The original unary selector is NOT a membership-token input.
            # Among these small selectors only n=1,p=1 is valid grouped input.
            y = tape_run(C,n,p,grouped,clock)
            if n == 1 and p == 1:
                assert y == 0 and valid(C,n,p,y)
                counts["group_valid"] += 1
            else:
                assert y is None
                counts["group_blank"] += 1
            counts["selector_inputs"] += 1
    assert counts == {"selector_inputs":260,"prefix_valid":34,
                      "prefix_timeouts":260,"group_valid":1,"group_blank":259}
    return counts


if __name__ == "__main__":
    print(json.dumps(replay(*(Path(p).read_text().strip() for p in sys.argv[1:]))))
