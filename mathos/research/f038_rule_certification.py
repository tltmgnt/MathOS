"""Quantified selector-rule certification and repair; exact finite regression."""
from mathos.research.f038_monotone_choice import sat, restrict

ROWS = ((-1,), (1,), (-2,), (2,), (-3,), (3,), (-1,-2), (2,3),
        (-1,-2,-3), (-1,2,3), (1,-2,3), (1,2,-3))


def satisfies(f, mask):
    return all(any(bool(mask & (1 << (abs(l)-1))) == (l > 0)
                   for l in c) for c in f)


def guard(f, n):
    top = n+1
    fixed = []
    for c in f:
        row = (1,) + tuple((abs(l)+1) * (1 if l > 0 else -1) for l in c)
        while len(row) > 3:
            top += 1
            fixed.append((row[0], row[1], top))
            row = (-top, *row[2:])
        fixed.append(row)
    return top, tuple(fixed)


def instantiate(fixed, a, x):
    return fixed + tuple((i+2 if x & (1<<i) else -i-2,)
                         for i in range(a))


def audit():
    matrices = families = good = bad = instances = checks = failures = 0
    repairs = repair_exists = max_v = max_c = 0
    for mask in range(1<<len(ROWS)):
        f = tuple(c for i,c in enumerate(ROWS) if mask & (1<<i))
        top,fixed = guard(f,3)
        matrices += 1
        for a in (1,2):
            families += 1
            allowed = []
            for x in range(1<<a):
                h = instantiate(fixed,a,x)
                assert all(1 <= len(c) <= 3 for c in h)
                ys = {y for y in range(1<<(3-a)) if satisfies(f,x | (y<<a))}
                allowed.append(ys)
                z0 = sat(restrict(h,{1:False}))
                z1 = sat(restrict(h,{1:True}))
                assert (z0,z1) == (bool(ys),True)
                # Explicitly check the canonical branch-one witness.
                w = 1 | (x<<1)
                assert satisfies(h,w)
                # Every satisfying y gives an explicit repaired assignment.
                for y in ys:
                    v = (x | (y<<a)) << 1
                    for c in fixed:
                        if len(c)==3 and c[0]==1 and c[2]>4:
                            if not satisfies((c[:2],),v):
                                v |= 1 << (c[2]-1)
                    assert satisfies(h,v) and not (v&1)
                instances += 1
                checks += 2
                failures += not z0
                max_v = max(max_v,top)
                max_c = max(max_c,len(h))
            valid = all(allowed)
            good += valid
            bad += not valid
            found = False
            width = 3-a
            for table in range(1<<(width*(1<<a))):
                works = all(((table>>(width*x)) & ((1<<width)-1)) in ys
                            for x,ys in enumerate(allowed))
                found |= works
                repairs += 1
            assert found == valid
            repair_exists += found
    assert (matrices,families,good,bad,instances,checks,failures,repairs,
            repair_exists,max_v,max_c) == (
        4096,8192,356,7836,24576,49152,20912,131072,356,8,18)
    print(f'F038_RULE_CERTIFICATION_OK matrices={matrices} families={families} '
          f'safe={good} unsafe={bad} instances={instances} branch_checks={checks} '
          f'unsafe_outputs={failures} repair_tables={repairs} '
          f'repair_families={repair_exists} max_variables={max_v} max_clauses={max_c}')


if __name__ == '__main__':
    audit()
