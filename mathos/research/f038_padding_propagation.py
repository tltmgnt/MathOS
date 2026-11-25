"""Padding propagation and shared-witness clock-counterexample finite audit."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_clock_counterexample import early_candidates, compile_miss
from mathos.research.f038_monotone_choice import sat, restrict

STAGES=(3,4,5,6,6,7,2,4)


def encode(mask,padding=0):
    n=len(ROWS)
    assert 0<=mask<1<<n and padding>=0
    return '1'*n+'0'+format(mask,f'0{n}b')+'0'*padding


def decode(data):
    n=data.find('0')
    assert n==len(ROWS) and len(data)>=2*n+1
    assert all(c in '01' for c in data)
    assert not any(c!='0' for c in data[2*n+1:])
    return int(data[n+1:2*n+1],2)


def pad(data,length):
    assert length>=len(data)
    return data+'0'*(length-len(data))


def candidates_at(offset):
    return tuple(sorted(w^offset for w in early_candidates(STAGES[offset])))


def sweep(f,sets):
    for early in sets:
        for w in early:
            if satisfies(f,w):
                return w
    return None


def audit():
    sets=tuple(candidates_at(i) for i in range(8))
    compilers={}
    unions={}
    for i in range(8):
        u=set()
        for j in range(i,8):
            u.update(sets[j])
            unions[i,j]=frozenset(u)
            compilers[i,j]=compile_miss(ROWS,sorted(u))
    n=len(ROWS)
    formulas=source_sat=padded=single_misses=intervals=misses=witnesses=checks=candidates=0
    per_length=[0]*8
    per_window={ij:0 for ij in unions}
    for mask in range(1<<n):
        f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
        models=tuple(w for w in range(8) if satisfies(f,w))
        base=encode(mask)
        hits=[]
        for i,early in enumerate(sets):
            data=pad(base,len(base)+i)
            assert data==encode(mask,i) and decode(data)==mask
            hit=sweep(f,(early,))
            assert (hit is not None)==any(w in models for w in early)
            if models and hit is None:
                per_length[i]+=1
                single_misses+=1
            hits.append(hit)
            padded+=1
        pins={i+1:bool(mask&(1<<i)) for i in range(n)}
        for (i,j),u in unions.items():
            hit=sweep(f,sets[i:j+1])
            assert hit==next((h for h in hits[i:j+1] if h is not None),None)
            joint=bool(models) and hit is None
            assert joint==(bool(models) and not any(w in models for w in u))
            if hit is not None:
                assert hit in models
                witnesses+=1
            if joint:
                misses+=1
                per_window[i,j]+=1
            k=compilers[i,j]
            for w in range(8):
                assert satisfies(k,mask|(w<<n))==(joint and w in models)
                checks+=1
            assert sat(restrict(k,pins))==joint
            intervals+=1
            candidates+=len(u)
        formulas+=1
        source_sat+=bool(models)
    good_lengths=sum(m==0 for m in per_length)
    good_windows=sum(m==0 for m in per_window.values())
    collective=sum(m==0 and all(per_length[t]>0 for t in range(i,j+1))
                   for (i,j),m in per_window.items())
    assert (formulas,source_sat,padded,single_misses,intervals,misses,witnesses,
            checks,candidates,good_lengths,good_windows,collective,per_length)==(
        4096,1360,32768,5532,147456,7752,41208,1179648,946176,1,23,5,
        [1232,736,480,516,224,0,1360,984])
    print(f'F038_PADDING_PROPAGATION_OK formulas={formulas} sat={source_sat} '
          f'padded_checks={padded} single_misses={single_misses} windows={intervals} '
          f'joint_misses={misses} sweep_witnesses={witnesses} certificate_checks={checks} '
          f'candidate_checks={candidates} good_lengths={good_lengths} '
          f'good_windows={good_windows} collective_only={collective} '
          f'length_misses={",".join(map(str,per_length))}')


if __name__=='__main__':
    audit()
