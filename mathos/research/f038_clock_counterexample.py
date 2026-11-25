"""Exact finite deadline counterexample compiler; logical delay reduction audit."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_universal_clock import descriptions, candidate, stage, verify
from mathos.research.f038_monotone_choice import sat, restrict


def early_candidates(s):
    return tuple(sorted({w for p,b in descriptions(s)
                         if (w:=candidate(p,b)) is not None
                         and type(w) is int and 0<=w<8}))


def compile_miss(rows,early):
    n=len(rows)
    clauses=[(-i-1,)+tuple((n+abs(l))*(1 if l>0 else -1) for l in c)
             for i,c in enumerate(rows)]
    clauses.extend(tuple(i+1 for i,c in enumerate(rows) if not satisfies((c,),w))
                   for w in early)
    return tuple(clauses)


def audit():
    stages=cases=misses=nonmisses=candidates=wchecks=clause_sum=max_v=max_c=0
    counts=[]
    previous=set()
    for s in range(8):
        early=early_candidates(s)
        assert previous<=set(early)
        previous=set(early)
        k=compile_miss(ROWS,early)
        local=0
        for mask in range(1<<len(ROWS)):
            f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
            hit,_,_=stage(f,s)
            assert (hit is not None)==any(verify(f,w) for w in early)
            pins={i+1:bool(mask&(1<<i)) for i in range(len(ROWS))}
            restricted=restrict(k,pins)
            found=None
            for w in range(8):
                got=satisfies(k,mask|(w<<len(ROWS)))
                want=satisfies(f,w) and hit is None
                assert got==want
                if got:
                    found=w
                wchecks+=1
            assert sat(restricted)==(found is not None)
            if found is not None:
                assert verify(f,found) and hit is None
                local+=1
                misses+=1
            else:
                nonmisses+=1
            cases+=1
        counts.append(local)
        stages+=1
        candidates+=len(early)
        clause_sum+=len(k)
        max_v=max(max_v,len(ROWS)+3)
        max_c=max(max_c,len(k))
    assert (stages,cases,misses,nonmisses,candidates,wchecks,clause_sum,max_v,max_c,counts)==(
        8,32768,7844,24924,19,262144,115,15,20,[1360,1360,1360,1232,984,924,624,0])
    print(f'F038_CLOCK_COUNTEREXAMPLE_OK stages={stages} pinned_cases={cases} '
          f'misses={misses} nonmisses={nonmisses} early_candidates={candidates} '
          f'witness_checks={wchecks} clauses_sum={clause_sum} max_variables={max_v} '
          f'max_clauses={max_c} counts={",".join(map(str,counts))}')


def delay_audit():
    cases=params=misses=hard=units_checked=0
    n=len(ROWS)
    for mask in range(1<<n):
        f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
        found=False
        for x in range(8):
            data=mask|(x<<n)
            units=tuple((i+1 if data&(1<<i) else -i-1,) for i in range(n+3))
            decoded=sum(1<<(c[0]-1) for c in units if c[0]>0)
            assert decoded==data and satisfies(units,decoded)
            d=tuple(c for i,c in enumerate(ROWS) if decoded&(1<<i))
            delayed=satisfies(d,decoded>>n)
            assert delayed==satisfies(f,x)
            found|=delayed
            misses+=delayed
            units_checked+=len(units)
            params+=1
        assert found==any(satisfies(f,x) for x in range(8))
        hard+=found
        cases+=1
    assert (cases,params,misses,hard,units_checked)==(4096,32768,2304,1360,491520)
    print(f'F038_CLOCK_DELAY_REDUCTION_OK cases={cases} parameters={params} '
          f'delayed={misses} source_sat={hard} unit_checks={units_checked}')


if __name__=='__main__':
    audit()
    delay_audit()
