"""Independent scope replay, exhaustive order oracle, and reference validation."""
import json
import random
import sys
from dataclasses import asdict, replace
from itertools import combinations, permutations, product
from math import prod
from pathlib import Path

if __package__:
    from .finite_relational_elimination import Factor, Solver
    from .f038_rex_width_planner import Planner
    from .validate_finite_relational_elimination import oracle
else:
    from finite_relational_elimination import Factor, Solver
    from f038_rex_width_planner import Planner
    from validate_finite_relational_elimination import oracle


def scope_replay(solver, state, order, cap, limits):
    # Independent hyperedge replay, not a graph or subset-DP recurrence.
    scopes = [set(f.scope) for f in state.factors]
    steps = []
    for v in order:
        bucket = [s for s in scopes if v in s]
        bag = {v}.union(*bucket)
        out = bag - {v}
        c = prod(len(solver.domains[w]) for w in bag)
        u = prod(len(solver.domains[w]) for w in out)
        if any(l is not None and x > l for x, l in zip((len(bag), u, c), limits)):
            return None
        steps.append((v, tuple(w for w in state.order if w in bag),
                      tuple(w for w in state.order if w in out), c, u, (c+cap-1)//cap))
        scopes = [s for s in scopes if v not in s] + [out]
    return steps


def objective(solver, state, order, cap, limits):
    steps = scope_replay(solver, state, order, cap, limits)
    if steps is None:
        return None
    return (max((s[3] for s in steps), default=0), sum(s[3] for s in steps),
            tuple(state.order.index(v) for v in order))


def audit():
    rng = random.Random(0x52455809)
    counts = dict(plans=0, orders=0, admitted=0, rejected=0, stages=0,
                  candidate_rows=0, greedy_worse=0, greedy_blocked=0)
    greedy_example = None

    def check(s, st, retain=(), cap=3, limits=(None,None,None), execute=True):
        nonlocal greedy_example
        p = Planner(s, st, retain=retain, cap=cap, max_width=limits[0],
                    max_outgoing=limits[1], max_candidates=limits[2])
        plan = p.exact()
        objs = []
        for order in permutations(v for v in st.order if v not in retain):
            counts['orders'] += 1
            obj = objective(s, st, order, cap, limits)
            if obj is not None:
                objs.append(obj)
        counts['plans'] += 1
        if not objs:
            assert plan is None
            counts['rejected'] += 1
            return
        best = min(objs)
        assert plan is not None
        assert (plan.peak_candidates, plan.total_candidates,
                tuple(st.order.index(v) for v in plan.order)) == best
        expected = scope_replay(s, st, plan.order, cap, limits)
        assert [tuple(asdict(x).values()) for x in plan.steps] == expected
        counts['admitted'] += 1
        g = p.greedy()
        if g is None:
            counts['greedy_blocked'] += 1
        elif (g.peak_candidates,g.total_candidates) > best[:2]:
            counts['greedy_worse'] += 1
            if greedy_example is None:
                greedy_example = dict(sizes={v:len(s.domains[v]) for v in st.order},
                                      scopes=[f.scope for f in st.factors],
                                      retain=retain, limits=limits, greedy=asdict(g), exact=asdict(plan))
        if execute:
            final, traces = p.execute(plan)
            final_order = final.order
            projected = tuple(sorted({tuple(dict(zip(st.order,row))[v] for v in final_order)
                                      for row in oracle(s.domains,st)}))
            assert s.relation(final).rows == projected
            counts['stages'] += len(traces)
            counts['candidate_rows'] += sum(t.candidate_count for t in traces)

    names = tuple('abcd')
    edges = tuple(combinations(names,2))
    for mask in range(1<<len(edges)):
        for sizes in ((2,2,2,2),(1,2,3,4),(0,2,1,3)):
            s = Solver(dict(zip(names,map(range,sizes))))
            st = s.initial_state([Factor(e,tuple(product(*(s.domains[v] for v in e))))
                                  for j,e in enumerate(edges) if mask>>j&1])
            check(s,st)
            check(s,st,retain=('d',),limits=(3,8,16))
    for _ in range(100):
        names = tuple('abcde')
        s = Solver({v:range(rng.randrange(1,5)) for v in names})
        fs = []
        for _ in range(rng.randrange(1,9)):
            scope = tuple(rng.sample(names,rng.randrange(4)))
            fs.append(Factor(scope,tuple(row for row in product(*(s.domains[v] for v in scope)) if rng.randrange(2))))
        st = s.initial_state(fs,rng.sample(names,len(names)))
        check(s,st,retain=tuple(rng.sample(names,rng.randrange(3))))
        check(s,st,limits=(rng.randrange(2,6),rng.randrange(2,20),rng.randrange(3,50)))
    assert greedy_example is not None
    # Explicit materialization obstruction from REX-008 vs structural planning.
    stars=[]
    for n in (2,4,8,12):
        s=Solver({'a':[0,1],**{f'b{i}':[0,1] for i in range(n)}})
        st=s.initial_state([Factor(('a',f'b{i}'),((0,0),(0,1),(1,0))) for i in range(n)])
        p=Planner(s,st,cap=3)
        center=p.certificate(st.order)
        leaf=p.greedy()
        assert leaf.peak_candidates==4 and leaf.total_candidates==4*n+2
        if n<=8:
            assert p.exact().peak_candidates==4
        final,_=p.execute(leaf)
        assert s.relation(final).rows==((),)
        stars.append([n,center.peak_candidates,center.peak_outgoing_bound,leaf.peak_candidates,leaf.peak_outgoing_bound,leaf.total_candidates])
    # Fixed nine-group admission control, without materializing m^9 tuples.
    nine=[]
    for m in (2,3,8,32):
        names=tuple(str(i) for i in range(9))
        s=Solver({v:range(m) for v in names})
        for label,edges in [('path',zip(names,names[1:])),('clique5',combinations(names[:5],2))]:
            # Empty factors preserve structural scopes; admission is not a SAT verdict.
            st=s.initial_state([Factor(tuple(e),()) for e in edges])
            p=Planner(s,st,cap=m**3,max_width=4,max_outgoing=m**3,max_candidates=m**4)
            plan=p.exact()
            assert (plan is not None)==(label=='path')
            if plan:
                assert plan.peak_candidates==m*m and plan.batches<=9
            nine.append([m,label,None if plan is None else [plan.peak_bag_width,plan.peak_candidates,plan.batches]])
    # All-retained plan, empty active set and tampered certificate.
    s=Solver({'a':[0,1]});st=s.initial_state([])
    p=Planner(s,st,retain=('a',));assert p.exact().order==() and p.execute(p.exact())[0]==st
    p=Planner(s,st);plan=p.exact()
    try:p.execute(replace(plan,total_candidates=0))
    except ValueError:pass
    else:raise AssertionError('tampered certificate accepted')
    try:p.exact(max_eliminated=0)
    except ValueError:pass
    else:raise AssertionError('search limit ignored')
    # Physical bridge fixture: exact plan determines order; worker results feed next stage.
    domains={'a':[-3,7],'b':[2,9],'c':[-5,4]}
    fs=[Factor(('a','b'),((-3,9),)),Factor(('b','c'),((9,4),))]
    s=Solver(domains,batch_size=2);st=s.initial_state(fs)
    p=Planner(s,st,cap=2,max_width=2);plan=p.exact();final,traces=p.execute(plan)
    assert plan.order==('a','b','c') and s.relation(final).rows==((),)
    fixture={'domains':domains,'factors':[asdict(f) for f in fs],'plan':asdict(plan),
             'outgoing':[t.outgoing_rows for t in traces]}
    return dict(counts=counts,greedy_example=greedy_example,stars=stars,nine=nine,fixture=fixture)


if __name__=='__main__':
    result=audit()
    if len(sys.argv)>1:
        evidence=json.loads(Path(sys.argv[1]).read_text())
        assert evidence['plan']==json.loads(json.dumps(result['fixture']['plan']))
        assert evidence['outgoing']==json.loads(json.dumps(result['fixture']['outgoing']))
        assert evidence['stats']['physical']['physicalBatches']>0
        print('REX_WIDTH_PHYSICAL_BRIDGE_OK')
    print('REX_WIDTH_PLANNER_OK '+json.dumps(result,separators=(',',':')))
