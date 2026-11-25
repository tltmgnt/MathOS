"""Free-suffix success mass and polynomial-window hitting-list finite audit."""
from fractions import Fraction
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_clock_counterexample import early_candidates, compile_miss
from mathos.research.f038_monotone_choice import sat, restrict

STAGES=(3,4,5,6,2)


def encode(mask,suffix=''):
    n=len(ROWS)
    assert 0<=mask<1<<n and all(c in '01' for c in suffix)
    return '1'*n+'0'+format(mask,f'0{n}b')+suffix


def decode(data):
    n=data.find('0')
    assert n==len(ROWS) and len(data)>=2*n+1
    assert all(c in '01' for c in data)
    return int(data[n+1:2*n+1],2)


def candidate_sets(j):
    return tuple(tuple(sorted(w^(v&7)^j for w in early_candidates(STAGES[j])))
                 for v in range(1<<j))


def audit():
    sets=tuple(candidate_sets(j) for j in range(len(STAGES)))
    n=len(ROWS)
    compilers={}
    unions={}
    for i in range(len(sets)):
        u=set()
        for j in range(i,len(sets)):
            for candidates in sets[j]:
                u.update(candidates)
            unions[i,j]=frozenset(u)
            compilers[i,j]=compile_miss(ROWS,sorted(u))
    formulas=yes=no=variants=accepted=missed=unsat_checks=mass_checks=0
    windows=all_miss=positive=det_miss=det_hit=random_only=checks=0
    good_half=zero=one=0
    counts=[0]*len(sets)
    for mask in range(1<<n):
        f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
        models=tuple(w for w in range(8) if satisfies(f,w))
        masses=[]
        heads=[]
        pins={i+1:bool(mask&(1<<i)) for i in range(n)}
        for j,alternatives in enumerate(sets):
            hits=0
            head=False
            for v,candidates in enumerate(alternatives):
                suffix=format(v,f'0{j}b') if j else ''
                data=encode(mask)+suffix
                assert data==encode(mask,suffix) and decode(data)==mask
                assert len(data)==2*n+1+j
                w=next((w for w in candidates if satisfies(f,w)),None)
                expect=any(w in models for w in candidates)
                assert (w is not None)==expect
                if expect:
                    assert w in models
                    hits+=1
                    counts[j]+=1
                    accepted+=1
                    head|=v<2
                elif models:
                    missed+=1
                else:
                    unsat_checks+=1
                variants+=1
            p=Fraction(hits,len(alternatives))
            assert 0<=p<=1
            if models:
                good_half+=p>=Fraction(1,2)
                zero+=p==0
                one+=p==1
            masses.append(p)
            heads.append(head)
            mass_checks+=1
        for i in range(len(sets)):
            failure=Fraction(1)
            hit=False
            for j in range(i,len(sets)):
                failure*=1-masses[j]
                hit|=heads[j]
                pos=failure<1
                u=unions[i,j]
                assert pos==any(w in models for w in u)
                # The list is a subset of the randomized support.
                assert not hit or pos
                if models:
                    all_miss+=not pos
                    positive+=pos
                    det_miss+=not hit
                    det_hit+=hit
                    random_only+=pos and not hit
                k=compilers[i,j]
                for w in range(8):
                    assert satisfies(k,mask|(w<<n))==(not pos and w in models)
                    checks+=1
                assert sat(restrict(k,pins))==(bool(models) and not pos)
                windows+=1
        formulas+=1
        yes+=bool(models)
        no+=not models
    assert (formulas,yes,no,variants,accepted,missed,unsat_checks,mass_checks,
            windows,all_miss,positive,det_miss,det_hit,random_only,checks,
            good_half,zero,one,counts)==(
        4096,1360,2736,126976,11944,30216,84816,20480,61440,3656,16744,
        4952,15448,1296,491520,3180,3124,764,[128,1000,2748,8068,0])
    print(f'F038_RANDOM_PADDING_OK formulas={formulas} sat={yes} unsat={no} '
          f'variant_checks={variants} accepted={accepted} missed={missed} '
          f'unsat_checks={unsat_checks} mass_checks={mass_checks} windows={windows} '
          f'all_miss={all_miss} positive={positive} det_miss={det_miss} '
          f'det_hit={det_hit} random_only={random_only} certificate_checks={checks} '
          f'good_half={good_half} zero={zero} one={one} '
          f'accepted_by_length={",".join(map(str,counts))}')


if __name__=='__main__':
    audit()
