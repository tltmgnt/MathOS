"""REX-023A native original scheduler / quotient interpreter gate."""
import json
import sys
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import (
    valid, stage, universal, controls, decode_tm, encode_tm, tape_run,
)
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed


def small_schedule():
    C = pool(2)
    hist, solved, bad = [0]*7, [0]*7, [0]*7
    descs = natives = 0
    for p in range(256):
        models = [x for x in range(4) if valid(C, 2, p, x)]
        first = None
        for s in range(7):
            w, c, native = stage(C, 2, p, s)
            descs += c
            natives += native
            if w is not None:
                assert w in models
                solved[s] += 1
                if first is None:
                    first = s
                    hist[s] += 1
            elif models:
                bad[s] += 1
        assert bool(models) == (first is not None)
        if models:
            assert universal(2, p)[1] == first
    assert hist == [0,32,46,0,17,0,0]
    assert solved == [0,32,78,78,95,95,95]
    assert bad == [95,63,17,17,0,0,0]
    assert descs == 63232 and natives == 11008
    return dict(stage_tests=1792, descriptions=descs, builtin_launches=natives,
                solved=solved, bad=bad, histogram=hist, controls=controls())


def quotient_replay(desc):
    q, table = decode_tm(desc)
    assert q == 103393 and len(desc) == 6617156
    assert encode_tm(table, q) == desc
    n, m, pins = 31, 2, (1,0)
    C = pool(n)
    base = set(fixed(9,m,n,pins))
    active = base | {(-1-2*g,) for g in range(9)}
    p = sum(1 << j for j,c in enumerate(C) if c in active)
    t = 44654867
    x = tape_run(C,n,p,desc,t)
    assert x == 268348074 and valid(C,n,p,x)
    assert tape_run(C,n,p,desc,t-1) is None
    assert tape_run(pool(1),1,0,desc,1000) is None
    s = len(desc)+(t-1).bit_length()
    assert s == 6617182
    assert (1 << (s-len(desc)-1)) < t <= (1 << (s-len(desc)))
    return dict(states=q, bits=len(desc), sat_clock=t, witness=x,
                original_valid=True, one_step_short=True, min_slot=s,
                full_stage_enumerated=False)


def family_schedule():
    result = []
    for m in range(2, 101):
        n = 19*m-7
        L = n+1+2*n*n+8*n*(n-1)*(n-2)//6
        b = (L-1).bit_length()
        result.append(dict(m=m,n=n,L=L,logL=b,stage3=3*b,
                           exhaustive_slot=n+3,
                           exhaustive_budget_eligible=n+3<=3*b))
    assert [r["m"] for r in result if r["exhaustive_budget_eligible"]] == [2,3]
    return result


if __name__ == '__main__':
    result = dict(small=small_schedule(), family=family_schedule())
    if len(sys.argv)>1:
        result["quotient"] = quotient_replay(Path(sys.argv[1]).read_text().strip())
    print(json.dumps(result))
