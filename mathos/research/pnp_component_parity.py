"""Component parity recognition and certificates for bounded-arity graph CNFs."""
from collections import defaultdict
from itertools import product
from .pnp_structural_kernel import normalize
from .pnp_unified_portfolio import fingerprint

ARITY=8


def _decode(n,clauses,b):
    nn,f,m=normalize(n,clauses)
    groups=defaultdict(list)
    for c in f:
        b.tick(1+len(c))
        if not 1<=len(c)<=ARITY:
            return None
        groups[tuple(sorted(abs(x) for x in c))].append(c)
    rows=[]
    for vs,block in sorted(groups.items()):
        # Every full-scope clause forbids exactly one assignment.
        masks={tuple(x<0 for x in sorted(c,key=abs)) for c in block}
        b.tick(1+len(vs)*len(block))
        if len(masks)!=1<<(len(vs)-1):
            return None
        parities={sum(bits)%2 for bits in masks}
        if len(parities)!=1:
            return None
        rows.append((vs,1-parities.pop()))
    incidence=defaultdict(list)
    for i,(vs,_) in enumerate(rows):
        for v in vs:
            incidence[v].append(i)
            b.tick()
    if set(incidence)!=set(range(1,nn+1)) or any(len(a)!=2 for a in incidence.values()):
        return None
    return nn,f,m,rows,incidence


def _components(rows,incidence,b):
    g=[[] for _ in rows]
    for v,(i,j) in incidence.items():
        g[i].append((j,v))
        g[j].append((i,v))
    seen=set()
    parts=[]
    for root in range(len(rows)):
        if root in seen:
            continue
        order=[root]
        parent={root:None}
        seen.add(root)
        for i in order:
            for j,v in g[i]:
                b.tick()
                if j not in seen:
                    seen.add(j)
                    parent[j]=(i,v)
                    order.append(j)
        parts.append((order,parent))
    return parts


def propose(n,clauses,b):
    decoded=_decode(n,clauses,b)
    if decoded is None:
        return None
    nn,f,m,rows,incidence=decoded
    parts=_components(rows,incidence,b)
    components=[sorted(order) for order,_ in parts]
    bits=[False]*nn
    residual=[rhs for _,rhs in rows]
    conflict=None
    for order,parent in parts:
        if sum(residual[i] for i in order)%2:
            conflict=sorted(order)
            break
        for i in reversed(order[1:]):
            j,v=parent[i]
            bits[v-1]=bool(residual[i])
            residual[j]^=residual[i]
            b.tick()
        if residual[order[0]]:
            raise AssertionError("even component has nonzero residual")
    proof={"kind":"xor_conflict","rows":conflict} if conflict is not None else {"kind":"sat_witness","assignment":bits}
    return {"schema":"mathos-pnp-component-parity/1","input_sha256":fingerprint(n,clauses),
            "normalized_n":nn,"new_to_old":m,"rows":rows,"components":components,
            "global_rhs":sum(rhs for _,rhs in rows)%2,
            "decision":"unsat" if conflict is not None else "sat","proof":proof}


def verify(n,clauses,r,b):
    """Independent local truth tables, partition, XOR identity or original model."""
    nn,f,m=normalize(n,clauses)
    if (r["schema"]!="mathos-pnp-component-parity/1" or r["input_sha256"]!=fingerprint(n,clauses)
            or r["normalized_n"]!=nn or tuple(r["new_to_old"])!=m):
        raise ValueError("invalid input binding")
    groups=defaultdict(list)
    for c in f:
        b.tick(1+len(c))
        if not 1<=len(c)<=ARITY:
            raise ValueError("invalid scope width")
        groups[tuple(sorted(abs(x) for x in c))].append(c)
    rows=[]
    covered=set()
    owners=defaultdict(list)
    for i,(raw,rhs) in enumerate(r["rows"]):
        vs=tuple(raw)
        if (vs not in groups or vs in covered or any(type(v) is not int for v in vs)
                or type(rhs) is not int or rhs not in (0,1)):
            raise ValueError("invalid row")
        covered.add(vs)
        for bits in product((False,True),repeat=len(vs)):
            b.tick(1+len(vs)*len(groups[vs]))
            a=dict(zip(vs,bits))
            holds=all(any(a[abs(x)]==(x>0) for x in c) for c in groups[vs])
            if holds!=(sum(bits)%2==rhs):
                raise ValueError("parity equivalence rejected")
        for v in vs:
            owners[v].append(i)
        rows.append((vs,rhs))
    if covered!=set(groups) or set(owners)!=set(range(1,nn+1)) or any(len(a)!=2 for a in owners.values()):
        raise ValueError("incomplete graph incidence")
    # Independent component reconstruction via union-find.
    parents=list(range(len(rows)))
    def find(i):
        while parents[i]!=i:
            b.tick()
            parents[i]=parents[parents[i]]
            i=parents[i]
        return i
    for i,j in owners.values():
        b.tick()
        parents[find(i)]=find(j)
    components=defaultdict(list)
    for i in range(len(rows)):
        components[find(i)].append(i)
    actual=sorted(components.values())
    if r["components"]!=actual or r["global_rhs"]!=sum(rhs for _,rhs in rows)%2:
        raise ValueError("incorrect component partition")
    odd=[c for c in actual if sum(rows[i][1] for i in c)%2]
    p=r["proof"]
    if p["kind"]=="xor_conflict":
        ids=p["rows"]
        if ids not in odd or any(type(i) is not int for i in ids):
            raise ValueError("not an odd component")
        support=set()
        parity=0
        for i in ids:
            vs,rhs=rows[i]
            b.tick(1+len(vs))
            support.symmetric_difference_update(vs)
            parity^=rhs
        if support or parity!=1 or r["decision"]!="unsat":
            raise ValueError("invalid conflict")
    elif p["kind"]=="sat_witness":
        bits=p["assignment"]
        if len(bits)!=nn or any(type(x) is not bool for x in bits) or odd or r["decision"]!="sat":
            raise ValueError("invalid assignment")
        for c in f:
            b.tick(1+len(c))
            if not any(bits[abs(x)-1]==(x>0) for x in c):
                raise ValueError("input rejects assignment")
    else:
        raise ValueError("unknown proof")
    return True
