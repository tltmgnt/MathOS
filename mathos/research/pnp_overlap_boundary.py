"""PNP-OVL-001: two-block overlap, exact projection and parameterized solving.

Bit 2*x+a selects a local domain element (x,a). Output bit 0 is u=x&a,
bit 1 is v=x&b. Each component has its own three private input variables.
Only affine equations on outputs couple components. Not unrestricted SAT.
"""
from collections import Counter
from itertools import product
import json

def project(left, right):
    if not all(isinstance(d, int) and 0 <= d < 16 for d in (left, right)):
        raise ValueError("domain masks must be in 0..15")
    out = {}
    for x, a, b in product(range(2), repeat=3):
        if left & (1 << (2*x+a)) and right & (1 << (2*x+b)):
            out.setdefault((x & a) | ((x & b) << 1), (x,a,b))
    return out

def affine_rows(relation):
    """Exact affine description on two output bits; reject non-affine triples."""
    r = set(relation)
    if not r:
        return [(0,1)]
    if len(r) == 3:
        raise ValueError("non-affine")
    return [(m, (next(iter(r)) & m).bit_count() % 2)
            for m in (1,2,3)
            if len({(v&m).bit_count()%2 for v in r}) == 1]

def affine_solve(width, rows):
    pivots = {}
    for mask, rhs in rows:
        if not (isinstance(mask,int) and 0 <= mask < (1 << width) and rhs in (0,1)):
            raise ValueError("invalid affine row")
        while mask:
            p = mask.bit_length()-1
            if p not in pivots:
                pivots[p] = (mask,rhs)
                break
            a,b = pivots[p]
            mask ^= a
            rhs ^= b
        if not mask and rhs:
            return None
    result = 0
    for p,(mask,rhs) in sorted(pivots.items()):
        if ((mask & result).bit_count()%2) != rhs:
            result |= 1 << p
    return result

def verify(domains, rows, witness):
    if witness is None or len(witness) != len(domains):
        return False
    output = 0
    for i,((left,right),(x,a,b)) in enumerate(zip(domains,witness)):
        if any(v not in (0,1) for v in (x,a,b)):
            return False
        if not (left & (1 << (2*x+a)) and right & (1 << (2*x+b))):
            return False
        output |= ((x&a) | ((x&b)<<1)) << (2*i)
    return all((output&m).bit_count()%2 == rhs for m,rhs in rows)

def solve(domains, rows):
    """Return a checked input witness or None. At most 2**k affine leaves."""
    domains,rows = tuple(domains),tuple(rows)
    width=2*len(domains)
    if any(not isinstance(m,int) or not 0 <= m < (1<<width) or b not in (0,1)
           for m,b in rows):
        raise ValueError("invalid affine row")
    relations = [project(*d) for d in domains]
    if any(not r for r in relations):
        return None
    fixed=list(rows)
    branches=[]
    for i,r in enumerate(relations):
        if len(r)==3:
            # Split on u. Each nonempty slice has at most two points.
            branches.append([[(m<<(2*i),b) for m,b in affine_rows(
                {v for v in r if v&1 == bit})] for bit in (0,1)])
        else:
            fixed.extend((m<<(2*i),b) for m,b in affine_rows(r))
    for chosen in product(*branches):
        ans=affine_solve(width, fixed+[row for block in chosen for row in block])
        if ans is not None:
            witness=tuple(r[(ans>>(2*i))&3] for i,r in enumerate(relations))
            if not verify(domains,rows,witness):
                raise AssertionError("invalid lifted witness")
            return witness
    return None


def independent_coordinates(width, rows, coordinates):
    """Greedy basis of coordinate rows modulo the affine coefficient row space.

    Returned coordinate indices are independent modulo that space.
    RHS values play no role in rank; consistency must be checked separately.
    """
    pivots = {}
    def insert(mask):
        while mask:
            p=mask.bit_length()-1
            if p not in pivots:
                pivots[p]=mask
                return True
            mask ^= pivots[p]
        return False
    for m,b in rows:
        if not isinstance(m,int) or not 0 <= m < (1<<width) or b not in (0,1):
            raise ValueError("invalid affine row")
        insert(m)
    basis=[]
    for j in coordinates:
        if not isinstance(j,int) or not 0 <= j < width:
            raise ValueError("invalid coordinate")
        if insert(1<<j):
            basis.append(j)
    return tuple(basis)


def minimum_rank_coordinates(width, rows, pairs):
    """Exact minimum rank increase selecting one coordinate per pair.

    Iterative deepening over the extra dimension, not over the number of
    pairs. A depth-first stack stores at most one sibling per level.
    """
    rows,pairs=tuple(rows),tuple(tuple(p) for p in pairs)
    if not isinstance(width,int) or width<0:
        raise ValueError("invalid width")
    if any(len(p)!=2 or any(not isinstance(j,int) or not 0<=j<width for j in p)
           for p in pairs):
        raise ValueError("invalid coordinate pair")

    def residual(mask, pivots):
        while mask:
            p=mask.bit_length()-1
            if p not in pivots:
                break
            mask ^= pivots[p]
        return mask

    initial={}
    for m,b in rows:
        if not isinstance(m,int) or not 0<=m<(1<<width) or b not in (0,1):
            raise ValueError("invalid affine row")
        v=residual(m,initial)
        if v:
            initial[v.bit_length()-1]=v

    nodes=0
    for budget in range(len(pairs)+1):
        stack=[(initial,0)]
        while stack:
            pivots,depth=stack.pop()
            nodes+=1
            choice=[]
            uncovered=None
            for a,b in pairs:
                u,v=residual(1<<a,pivots),residual(1<<b,pivots)
                if not u:
                    choice.append(a)
                elif not v:
                    choice.append(b)
                else:
                    uncovered=(u,v)
                    break
            if uncovered is None:
                # Minimum budget certifies optimality by exhaustive failure
                # of all preceding budgets; this is not a succinct certificate.
                actual=len(independent_coordinates(width,rows,choice))
                if actual!=budget:
                    raise AssertionError("rank search invariant")
                return {"coordinates":tuple(choice),"d":actual,"search_nodes":nodes}
            if depth==budget:
                continue
            # Each uncovered alternative increases the rank by exactly one.
            # Duplicate residuals may describe the same extension, but need
            # not be deduplicated for correctness or the binary-tree bound.
            for v in reversed(uncovered):
                child=pivots.copy()
                child[v.bit_length()-1]=v
                stack.append((child,depth+1))
    raise AssertionError("choosing every first endpoint is always possible")

def graph_rank_instance(edges):
    """Embed vertex cover: one component per edge, equality rows per vertex."""
    edges=tuple(tuple(e) for e in edges)
    reps={}
    rows=[]
    for i,e in enumerate(edges):
        if len(e)!=2 or e[0]==e[1]:
            raise ValueError("expected loop-free graph edges")
        for j,v in enumerate(e):
            coord=2*i+j
            if v in reps:
                rows.append(((1<<coord)|(1<<reps[v]),0))
            else:
                reps[v]=coord
    return [(10,15)]*len(edges),rows

def optimum_demo(k=21):
    if k<1:
        raise ValueError("expected positive edge count")
    ds,rows=graph_rank_instance((i+1,0) for i in range(k))
    fixed,optimized={},{}
    assert solve_ranked(ds,rows,stats=fixed) is not None
    assert solve_ranked(ds,rows,stats=optimized,optimize=True) is not None
    return {"k":k,"fixed_d":fixed["d"],"optimal_d":optimized["d"],
            "fixed_patterns":fixed["affine_feasible_patterns"],
            "optimal_patterns":optimized["affine_feasible_patterns"],
            "optimizer_nodes":optimized["optimizer_nodes"],
            "fixed_visited":fixed["visited"],"optimal_visited":optimized["visited"],
            "scope":"star-graph structured SAT control; pattern count, not runtime"}

def solve_ranked(domains, rows, *, stats=None, optimize=False):
    """Solve by enumerating only affine-feasible split patterns.

    For consistent affine relaxation, the number of patterns is exactly 2**d
    where d is the rank increase from adding all chosen split coordinates.
    stats, if supplied, receives counters; an early SAT exit may visit fewer.
    """
    domains, rows = tuple(domains), tuple(rows)
    width=2*len(domains)
    if any(not isinstance(m,int) or not 0 <= m < (1<<width) or b not in (0,1)
           for m,b in rows):
        raise ValueError("invalid affine row")
    relations=[project(*d) for d in domains]
    triple=[i for i,r in enumerate(relations) if len(r)==3]
    report={"k":len(triple),"d":None,"affine_feasible_patterns":0,"visited":0}
    if stats is not None:
        stats.clear()
        stats.update(report)
        report=stats
    if any(not r for r in relations):
        return None
    fixed=list(rows)
    for i,r in enumerate(relations):
        if len(r)!=3:
            fixed.extend((m<<(2*i),b) for m,b in affine_rows(r))
    if affine_solve(width,fixed) is None:
        return None
    if optimize:
        opt=minimum_rank_coordinates(width,fixed,[(2*i,2*i+1) for i in triple])
        coords=opt["coordinates"]
        report["optimizer_nodes"]=opt["search_nodes"]
    else:
        coords=tuple(2*i for i in triple)
    report["split_coordinates"]=coords
    basis=independent_coordinates(width,fixed,coords)
    report["d"]=len(basis)
    report["affine_feasible_patterns"]=1<<len(basis)
    for bits in product(range(2),repeat=len(basis)):
        branch=fixed+[(1<<j,b) for j,b in zip(basis,bits)]
        representative=affine_solve(width,branch)
        if representative is None:
            raise AssertionError("independent coordinate assignment infeasible")
        report["visited"]+=1
        for i,j in zip(triple,coords):
            bit=(representative>>j)&1
            local=j-2*i
            branch.extend((m<<(2*i),b) for m,b in affine_rows(
                {v for v in relations[i] if ((v>>local)&1) == bit}))
        ans=affine_solve(width,branch)
        if ans is not None:
            witness=tuple(r[(ans>>(2*i))&3] for i,r in enumerate(relations))
            if not verify(domains,rows,witness):
                raise AssertionError("invalid lifted witness")
            return witness
    return None

def rank_demo(k=21):
    """Structured UNSAT family: all u equal; both global u choices fail."""
    if k<2:
        raise ValueError("k must be at least two")
    ds=[(10,15),(15,10)]+[(10,15)]*(k-2)
    # First relation v implies u; second u implies v.
    # Set v0=1, v1=0, forcing conflicting u values, while all u are equal.
    rows=[(2,1),(8,0)]+[(1|(1<<(2*i)),0) for i in range(1,k)]
    stats={}
    assert solve_ranked(ds,rows,stats=stats) is None
    return {**stats,"unfiltered_patterns":1<<k,"result":"UNSAT",
            "scope":"structured control, not an unrestricted SAT benchmark"}

def reduce_3sat(clauses):
    """Signed nonzero literal IDs; exactly three literals per clause.
    One isolated two-block component per occurrence. u is literal truth,
    v is its selector. Couple only outputs, never input variables.
    """
    domains,rows,representatives=[],[],{}
    for clause in clauses:
        if len(clause)!=3 or any(not isinstance(l,int) or l==0 for l in clause):
            raise ValueError("expected three nonzero signed integer literals")
        parity=0
        for lit in clause:
            i=len(domains)
            u,v=2*i,2*i+1
            domains.append((0b1010,0b1111)) # force a=1, b free
            parity |= 1<<v
            var,neg=abs(lit),int(lit<0)
            if var in representatives:
                j,oldneg=representatives[var]
                rows.append(((1<<u)|(1<<j),neg^oldneg))
            else:
                representatives[var]=(u,neg)
        rows.append((parity,1))
    return tuple(domains),tuple(rows)

def audit():
    sizes,missing=Counter(),Counter()
    for a,b in product(range(16),repeat=2):
        r=project(a,b)
        sizes[len(r)]+=1
        if len(r)==3:
            missing[next(v for v in range(4) if v not in r)]+=1
    return {"domain_pairs":256,"relation_sizes":dict(sorted(sizes.items())),
            "triple_missing_output":dict(sorted(missing.items())),
            "status":"FINITE_CONTROLS_ONLY","novelty":"NOT_ESTABLISHED",
            "independent_review":"NOT_PERFORMED","global_promotion":"NONE"}

if __name__=="__main__":
    print(json.dumps({**audit(), 'rank_demo': rank_demo(), 'optimum_demo': optimum_demo()},indent=2,sort_keys=True))
