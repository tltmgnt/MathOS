"""FAR-002: independent interpreter replay and conservative TGA evidence gate.

The input description comes from the fixed JavaScript compiler. This module
uses the original F038 decoder but a prepared block layout, not tape_run's
normalized selector input. It cannot promote the global P vs NP status.
"""
import itertools
import json
import sys
from pathlib import Path
from mathos.research.f038_unrestricted_universal_search import decode_tm, encode_tm
from mathos.research.tga_f038_far_001 import graph as far_graph
from mathos.proof_analysis.gap_analysis import Claim, analyze


def replay(description, stream, mask):
    decoded = decode_tm(description)
    assert decoded is not None
    q, table = decoded
    assert encode_tm(table, q) == description
    assert q == 2021 and len(description) == 92970
    alphabet = list(itertools.product("_01E", "_LR01", "_01"))
    def ternary(v):
        return "".join(str(v // (3 ** j) % 3) for j in (3, 2, 1, 0))
    codes = ["2222"] + [ternary(i) for i in range(59)]
    encode = dict(zip(alphabet, codes))
    decode = dict(zip(codes, alphabet))
    n, k = len(stream), len(mask)
    windows = n-k+1
    expected_steps = 11*(2*windows-1)*(2*k+3)-3*windows
    tape = {}
    for i in range(n+2):
        s = "_" if i == 0 else "E" if i == n+1 else stream[i-1]
        m = "L" if i == 0 else "R" if i == k+1 else mask[i-1] if i <= k else "_"
        for j, a in enumerate(encode[s,m,"_"]):
            if a != "2":
                tape[4*i+j] = int(a)
    state = head = 0
    low = high = 0
    for step in range(1, expected_steps+1):
        state, write, move = table[3*state+tape.get(head,2)]
        if write == 2:
            tape.pop(head, None)
        else:
            tape[head] = write
        head += move
        low, high = min(low,head), max(high,head)
        if state == q:
            break
    assert state == q and step == expected_steps
    assert head == 4*(n-k) and low == 0 and high == 4*(n+2)-1
    for i in range(n+2):
        s,m,o = decode["".join(str(tape.get(4*i+j,2)) for j in range(4))]
        assert s == ("_" if i == 0 else "E" if i == n+1 else stream[i-1])
        assert m == ("L" if i == n-k else "R" if i == n+1 else mask[i-(n-k)-1] if n-k<i<=n else "_")
        want = str(int(any(a == b == "1" for a,b in zip(mask,stream[i:i+k])))) if i<windows else "_"
        assert o == want
    return [n,k,step,high-low+1]


def report(audit, replays):
    assert audit["states"] == 2021 and audit["descriptionBits"] == 92970
    assert audit["tests"] == 10668 and audit["windows"] == 20052
    assert audit["transitions"] == 3409992 and audit["cutoffs"] == 21
    for n,k,w,physical,logical,span in audit["scaling"]:
        assert w == n-k+1 and logical == (2*w-1)*(2*k+3)
        assert physical == 11*logical-3*w and span == 4*(n+2)
    g = far_graph()
    for key,label,note in (
        ("PHYS-01","Fixed alphabet compiler and mask primitive review","Finite transition table and exact clock derivation; independent review outstanding"),
        ("PHYS-02","Nested mobile key/mask/record-list composition","Not implemented"),
        ("PHYS-03","Raw normalized-input preparation and output reconstruction","Not implemented for this primitive"),
        ("PHYS-04","Complete root/descendant movement ledger on same machine","Not implemented"),
    ):
        g[key] = Claim(label,"open",note=note)
    g["FAR-05"] = Claim("Physical implementation and cost","derived",
                         (("PHYS-01","PHYS-02","PHYS-03","PHYS-04"),),
                         "Refinement of FAR-05; all obligations still open.")
    r = {key:analyze(g,key) for key in ("FAR-05","restricted_evidence","uniform_recovery")}
    assert all(v["status"] == "BLOCKED" for v in r.values())
    assert r["FAR-05"]["minimal_completion_sets"] == [["PHYS-01","PHYS-02","PHYS-03","PHYS-04"]]
    return {"mission":"F038-FAR-002","scope":"PREPARED_BLOCK_PRIMITIVE_ONLY",
            "PNP_RESOLUTION_STATUS":"OPEN","PROMOTION":"NONE",
            "decision":"CONTINUE_ONLY_COMPOSITION_AUDIT",
            "rejected_inferences":["prepared layout implies normalized input integration",
                                    "one mask primitive implies full FAR-05",
                                    "finite exact clocks imply universal cubic coverage"],
            "replays":replays,**r}


if __name__ == "__main__":
    d = Path(sys.argv[1]).read_text().strip()
    audit = json.loads(Path(sys.argv[2]).read_text().split("F038_FAR_PHYSICAL_MASK_SCAN_OK ",1)[1])
    cases = [("0","0"),("1","1"),("010011001","101"),("101010101","010101010"),
             ("00110110","1"),("10000111","0000")]
    print(json.dumps(report(audit,[replay(d,s,m) for s,m in cases]),indent=2))
