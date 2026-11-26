"""Original U interpreter negative acceptance replay for retained join descriptor."""
import json
import sys
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import decode_tm, encode_tm, tape_run
from mathos.research.f038_universal_witness_layout import pool


def replay(d):
    a = decode_tm(d)
    assert a is not None and a[0] == 15686 and len(d) == 862734
    assert encode_tm(a[1], a[0]) == d
    count = 0
    for n in (1, 2):
        C = pool(n)
        for p in range(1 << len(C)):
            assert tape_run(C, n, p, d, 10000) is None
            count += 1
    assert count == 260
    return {"selector_inputs": count, "no_candidate": count}


if __name__ == "__main__":
    print(json.dumps(replay(Path(sys.argv[1]).read_text().strip())))
