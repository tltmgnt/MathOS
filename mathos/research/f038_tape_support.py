"""Low-degree support rank criterion and dense-circuit hardness fixtures."""
from mathos.research.f038_low_degree_tape import sparse_points, evaluate


def evaluation_vector(monomials,x):
    return sum(1<<i for i,m in enumerate(monomials) if x&m==m)


def insert(basis,v):
    while v:
        k=v.bit_length()-1
        if k not in basis:
            basis[k]=v
            return True
        v^=basis[k]
    return False


def null_vector(basis,D):
    if len(basis)==D:
        return None
    # Highest-bit pivots, so compute dependent coordinates from low to high.
    free=next(i for i in range(D) if i not in basis)
    p=1<<free
    for k,row in sorted(basis.items()):
        if (row&p).bit_count()&1:
            p|=1<<k
    assert p and all(not (v&p).bit_count()%2 for v in basis.values())
    return p


def audit():
    functions=degree_cases=checks=full=support=counts=zero_rows=0
    for r in range(1,4):
        N=1<<r
        for f in range(1<<N):
            functions+=1
            for d in range(min(2,r)+1):
                ms=tuple(sparse_points(r,d))
                D=len(ms)
                vectors=tuple(evaluation_vector(ms,x) for x in range(N))
                basis={}
                certificate=[]
                for x,v in enumerate(vectors):
                    if not f&(1<<x):
                        zero_rows+=1
                        if insert(basis,v):
                            certificate.append(x)
                rank=len(basis)
                count=0
                for p in range(1,1<<D):
                    good=True
                    for x,v in enumerate(vectors):
                        y=evaluate(ms,p,x)
                        assert y==((v&p).bit_count()&1)
                        if y and not f&(1<<x):
                            good=False
                        checks+=1
                    count+=good
                assert count==(1<<(D-rank))-1
                p=null_vector(basis,D)
                if p is None:
                    assert rank==len(certificate)==D
                    verify={}
                    for x in certificate:
                        assert not f&(1<<x) and insert(verify,vectors[x])
                    assert len(verify)==D
                    full+=1
                else:
                    assert all(not evaluate(ms,p,x) or f&(1<<x) for x in range(N))
                    assert count
                    support+=1
                degree_cases+=1
                counts+=count
    assert (functions,degree_cases,checks,full,support,counts,zero_rows)==(
        276,824,294368,438,386,3348,3176)
    print(f'F038_TAPE_SUPPORT_RANK_OK functions={functions} degree_cases={degree_cases} '
          f'evaluation_checks={checks} full_rank={full} support_exists={support} '
          f'nonzero_supports={counts} zero_rows={zero_rows}')


def dense_audit():
    cases=checks=full=0
    min_num,min_den=1,1
    for d in range(3):
        g=(4*(d+1)-1).bit_length()
        b=2+g
        r=b*(d+1)
        N=1<<r
        ms=tuple(sparse_points(r,d))
        D=len(ms)
        mask=(1<<b)-1
        for f in range(16):
            zeros=0
            basis={}
            cert=[]
            for x in range(N):
                good=True
                for i in range(d+1):
                    v=(x>>(i*b))&mask
                    if v<4 and not f&(1<<v):
                        good=False
                        break
                if not good:
                    zeros+=1
                    if len(basis)<D:
                        if insert(basis,evaluation_vector(ms,x)):
                            cert.append(x)
                checks+=1
            assert 4*zeros<=N
            assert (len(basis)==D)==(f!=15)
            if len(basis)==D:
                verify={}
                for x in cert:
                    assert any((v:=((x>>(i*b))&mask))<4 and not f&(1<<v)
                               for i in range(d+1))
                    assert insert(verify,evaluation_vector(ms,x))
                assert len(verify)==D
                full+=1
            else:
                assert f==15 and not basis
                assert null_vector(basis,D)==1
            cases+=1
            if (N-zeros)*min_den<min_num*N:
                min_num,min_den=N-zeros,N
    assert (cases,checks,full)==(48,4210944,45)
    assert 4*min_num==3*min_den
    print(f'F038_DENSE_TAPE_SUPPORT_BARRIER_OK cases={cases} '
          f'tape_checks={checks} full_rank={full} min_mass=3/4')


if __name__=='__main__':
    audit()
    dense_audit()
