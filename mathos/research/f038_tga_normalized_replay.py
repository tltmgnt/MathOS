"""Replay emitted raw fixtures using the original MathOS pool and verifier."""
import json
import sys
from itertools import product
from pathlib import Path
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed, witness, cross


def replay(fixtures):
    rows = []
    for f in fixtures:
        raw, bits, status = f["raw"], f["bits"], f["status"]
        n = raw.index("0")
        m = (n + 7) // 19
        assert n == 19*m-7 and m == 2
        C = pool(n)
        selected = [j for j, b in enumerate(raw[n+1:]) if b == "1"]
        p = sum(1 << j for j in selected)
        assert encoded(n,p,C) == raw
        active = {C[j] for j in selected}
        pins = [int((n-m-1+i,1-n,-n) in active) for i in range(m)]
        base = set(fixed(9,m,n,pins))
        assert base <= active and all(cross(c,9,m) for c in active-base)
        # All latent assignments; fixed normalized clauses give unique extension.
        def sat(w):
            return all(any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c) for c in active)
        models = sum(sat(witness(9,m,n,pins,a)) for a in product(range(m),repeat=9))
        if status == "SAT":
            assert bits is not None and len(bits)==n and valid(C,n,p,int(bits[::-1],2)) and models>0
        elif status == "UNSAT":
            assert bits is None and models==0
        elif status == "INELIGIBLE":
            assert bits is None and models>0
        else:
            raise AssertionError(status)
        rows.append([status,models])
    assert rows == [["SAT",11],["UNSAT",0],["SAT",2],["INELIGIBLE",10],
                    ["SAT",512],["SAT",103],["SAT",188]]
    return rows


if __name__ == "__main__":
    print(json.dumps(replay(json.loads(Path(sys.argv[1]).read_text()))))
