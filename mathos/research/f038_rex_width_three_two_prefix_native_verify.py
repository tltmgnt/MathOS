"""Verify the native interpreter's original halt-head output with the original pool and verifier."""
import json
import sys
from mathos.research.f038_unrestricted_universal_search import valid
from mathos.research.f038_universal_witness_layout import pool


def audit(fixtures, result, mode):
    records = {}
    with open(fixtures) as f:
        for line in f:
            name, n, budget, raw, expected, head, span = line.split()
            records[name] = (int(n), int(budget), raw, expected, head, span)
    rows = []
    with open(result) as f:
        tag, q, ell, entries = f.readline().split()
        q, ell, entries = map(int, (q, ell, entries))
        assert mode in ("bounded", "full")
        assert (tag, q, ell, entries) == (("CODEC", 3516288, 277786756, 10548864) if mode == "bounded" else ("CODEC", 3514565, 277650639, 10543695))
        for line in f:
            tag, name, t, h, span, word, cell, after = line.split()
            t, h, span, cell, after = map(int, (t, h, span, cell, after))
            assert tag == "RUN"
            n, budget, raw, expected, old_h, old_span = records[name]
            C = pool(n)
            assert raw[:n+1] == "1"*n+"0" and len(raw) == n+1+len(C)
            p = int(raw[n+1:][::-1], 2)
            assert 0 < t <= budget and word == expected
            if old_h != "-":
                assert (t, h, span) == (budget, int(old_h), int(old_span))
            slot = None
            if word != "-":
                assert len(word) == n and valid(C, n, p, int(word[::-1], 2)) and after == 2
                b = (len(raw)-1).bit_length()
                stage = ell+(t-1).bit_length()
                slot = dict(stage=stage, min_k=(stage+b-1)//b, s3=3*b)
            else:
                assert cell == 2
            rows.append(dict(classification="UNSAT" if word=="-" else "SAT", name=name, t=t, head=h, span=span, witness=None if word=="-" else word, slot=slot))
    assert len(rows) == len({r["name"] for r in rows}) == len(records)
    return dict(q=q, bits=ell, entries=entries, rows=rows)


if __name__ == "__main__":
    print("F038_REX_TWO_PREFIX_NATIVE_OK " + json.dumps(audit(sys.argv[1], sys.argv[2], sys.argv[3]), separators=(",", ":")))
