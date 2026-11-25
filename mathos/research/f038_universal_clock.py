"""Finite audit of universal-search scheduling and witness-only clocks.

This toy interpreter exercises the schedule, not a universal Turing machine.
"""
from mathos.research.f038_rule_certification import ROWS, satisfies


def descriptions(s):
    for l in range(s+1):
        for p in range(1<<l):
            yield (format(p,f'0{l}b') if l else '',1<<(s-l))


def candidate(p,budget):
    if p=='':
        return -1
    if p=='00':
        return 8
    if p=='01' and budget>=2:
        return 7
    if len(p)==4 and p[0]=='1':
        w=int(p[1:],2)
        if budget>=w+1:
            return w
    return None


def verify(f,w):
    return type(w) is int and 0<=w<8 and satisfies(f,w)


def stage(f,s,run=candidate):
    proposals=rejected=0
    for p,budget in descriptions(s):
        w=run(p,budget)
        if w is None:
            continue
        proposals+=1
        if verify(f,w):
            return w,proposals,rejected
        rejected+=1
    return None,proposals,rejected


def audit():
    formulas=yes=no=checks=accept=miss=unsat_deadlines=proposals=rejected=0
    bounds=max_first=budget_checks=0
    firsts=[0]*8
    for s in range(8):
        ds=tuple(descriptions(s))
        assert len(ds)==(1<<(s+1))-1
        assert len({p for p,_ in ds})==len(ds)
        assert all(len(p)<=s and b==1<<(s-len(p)) for p,b in ds)
        assert sum(b for _,b in ds)==(s+1)*(1<<s)
        budget_checks+=1
    for mask in range(1<<len(ROWS)):
        f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
        models=tuple(w for w in range(8) if satisfies(f,w))
        first=None
        for s in range(8):
            w,p,r=stage(f,s)
            proposals+=p
            rejected+=r
            checks+=1
            if w is not None:
                assert w in models
                if first is None:
                    first=s
                accept+=1
            elif models:
                miss+=1
            else:
                unsat_deadlines+=1
            if first is not None:
                assert w is not None
        if models:
            assert first is not None
            for w in models:
                # ceil(log2(w+1)) == w.bit_length().
                assert first<=4+w.bit_length()
                bounds+=1
            firsts[first]+=1
            max_first=max(max_first,first)
        else:
            assert first is None
        formulas+=1
        yes+=bool(models)
        no+=not models
    assert (formulas,yes,no,checks,accept,miss,unsat_deadlines,proposals,
            rejected,bounds,max_first,budget_checks,firsts)==(
        4096,1360,2736,32768,3036,7844,21888,131364,128328,2304,7,8,
        [0,0,0,128,248,60,300,624])
    print(f'F038_UNIVERSAL_WITNESS_CLOCK_OK formulas={formulas} sat={yes} '
          f'unsat={no} stage_checks={checks} accepting={accept} missed_sat={miss} '
          f'unsat_deadlines={unsat_deadlines} proposals={proposals} rejected={rejected} '
          f'deadline_bounds={bounds} max_first={max_first} budget_checks={budget_checks} '
          f'first_stages={",".join(map(str,firsts))}')


if __name__=='__main__':
    audit()
