"""F034: conservative structural work ledger for typed certificate replay.

No stopwatch, solver discovery, machine instruction or bit-step claim.
Counts are upper estimates of selected list operations, including
paths that can be skipped by the actual short-circuit checker.
"""
from collections import Counter
from . import tga_proctor_data_fixtures as wire
from . import tga_proctor_unified_bridge as unified
from . import tga_proctor_capacity as capacity
from . import tga_proctor_capacity_bridge as capbridge
from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_xor_bridge as xorbridge
from . import tga_proctor_dynamic_resolution as graphs


def _refs(count, target, refs):
    for i,row in refs:
        count["reference_lookup_cells"] += min(i+1,len(target))
        if i<len(target):
            count["reference_equality_cells"] += min(len(row),len(target[i]))+1


def ledger(n,expected,env):
    """Typed, finite, serialization-representable input (including rejects)."""
    a,b=wire.encode_expected(n,expected),wire.encode_envelope(env)
    s=a.count(b"\n")+b.count(b"\n")
    _,original,(batches,aug,tag,payload)=env
    c=Counter()
    # Token-sized proxy for simple traversals, list lengths, validation,
    # ordered input equality, frontier construction and scope append.
    c["simple_structure_proxy"]=s
    current=expected
    for batch in batches:
        for left,right,pivot,tail in batch:
            for i in (left,right):
                c["parent_lookup_cells"]+=min(i+1,len(current))
                if i<len(current):
                    c["parent_shape_comparisons"]+=len(current[i])*(1+len(tail))
        current=tuple(tail for _,_,_,tail in batch)
    target=expected+current if aug else current
    if tag=="EMPTY":
        c["empty_scan_cells"]=len(target)
    elif tag=="CAPACITY":
        ds,gs,rs=payload
        _refs(c,target,ds+rs)
        d=len(ds)
        dl=sum(len(row) for _,row in ds)
        gl=sum(len(vs) for vs,_ in gs)
        rl=sum(len(row) for _,row in rs)
        c["demand_pair_tests"]=d*d
        # Conservative: re-fetch the inner demand per outer literal,
        # even if a runtime closure shares the result.
        c["demand_index_cells"]=(d*d+d*dl)*(d+1)
        c["demand_index_list_cells"]=d*(d+1)
        c["demand_literal_comparisons"]=dl*dl
        c["coverage_group_visits"]=dl*len(gs)
        c["coverage_literal_comparisons"]=dl*gl
        for vs,k in gs:
            g=len(vs)
            if k>2:
                continue
            width=k+1
            leaves=g**width
            c["group_distinct_comparisons"]+=g*(g-1)//2
            c["capacity_word_nodes"]+=sum(g**j for j in range(width+1))
            c["capacity_tuple_leaves"]+=leaves
            c["tuple_distinct_comparisons"]+=leaves*width*(width-1)//2
            c["conflict_ref_visits"]+=leaves*len(rs)
            c["conflict_literal_visits"]+=leaves*rl
            c["conflict_literal_comparisons"]+=leaves*width*rl
    elif tag=="XOR":
        support=sum(len(vs) for vs,_,_ in payload)
        c["sparse_toggle_comparisons"]=support*support
        for vs,rhs,rs in payload:
            k=len(vs)
            if k>5:
                continue
            _refs(c,target,rs)
            leaves=2**k
            rl=sum(len(row) for _,row in rs)
            c["xor_pattern_nodes"]+=2*leaves-1
            c["xor_pattern_leaves"]+=leaves
            c["xor_pattern_parity_terms"]+=leaves*k
            c["xor_pattern_ref_visits"]+=leaves*len(rs)
            c["xor_pattern_literal_visits"]+=leaves*rl
            c["xor_pattern_literal_comparisons"]+=leaves*k*rl
    else:
        raise ValueError("unknown terminal")
    # Width proxy, not an instruction-cost multiplier or measured bit cost.
    max_bits=max((int(t).bit_length() for t in (a+b).splitlines()),default=0)
    return dict(terminal=tag,input_bytes=len(a),certificate_bytes=len(b),
                natural_tokens=s,max_encoded_natural_bits=max_bits,
                counts=dict(sorted(c.items())),abstract_sum=sum(c.values()),
                scope="SELECTED_STRUCTURAL_UPPER_ESTIMATES_NOT_MACHINE_STEPS")


def controls():
    rows=[]
    for n,f,env,ok in unified.cases():
        r=ledger(n,f,env)
        if r["abstract_sum"]>256*(r["natural_tokens"]+1)**4:
            raise AssertionError("coarse ledger envelope exceeded")
        rows.append(dict(expected_accept=ok,**r))
    families=[]
    for h in (2,3,4,8):
        n,cs=capacity.php(h,1)
        p=capbridge.annotate(n,cs,capacity.solve(n,cs,1))
        r=ledger(n,cs,(n,cs,((),False,"CAPACITY",p)))
        families.append(dict(family="PHP",size=h,**r))
    for q in (4,8,16,32,64):
        n,cs=graphs.tseitin(q,graphs.cubic_graph(q,11),(True,)+(False,)*(q-1))
        p=xorbridge.annotate(n,cs,xor.solve(n,cs))
        r=ledger(n,cs,(n,cs,((),False,"XOR",p)))
        families.append(dict(family="TSEITIN",size=q,**r))
    return dict(fixture_count=len(rows),accepted_expectation=sum(r["expected_accept"] for r in rows),
                fixtures=rows,families=families,polynomial_ledger_exponent=4,
                total_machine_refinement=False,independent_review=False,
                resolution_status="OPEN")


if __name__=="__main__":
    import json
    print(json.dumps(controls(),indent=2))
