"""Phase XLIV: mandatory problem binding and deterministic proof-work guard.
Work units are explicit heterogeneous operation counts, not time or CPU bounds.
"""
import mra_x_boundproof as p
import mra_x_kernel as k
import mra_x_proofarbitrate as q


def anchor(expected):
    p.require(type(expected) is str and len(expected)==64 and all(c in '0123456789abcdef' for c in expected))


def common_units(doc):
    return len(doc['problem']['domains'])+len(doc['problem']['factors'])+sum(len(f[1]) for f in doc['problem']['factors'])+1


def elimination_units(doc,receipt):
    return common_units(doc)+receipt['visits']+receipt['lookups']+sum(len(f[1]) for f in doc['messages'])+sum(len(r[2]) for r in doc['result']['trace'])


def partition_units(doc,receipt):
    return common_units(doc)+receipt['nodes']+receipt['row_checks']


def structural_bound(doc,limit):
    """Conservative FULL tree bounds: at each depth <= product of domain sizes.
    Only original problem structure; no trust in proposed search tree.
    Returns None when the prospective full-tree budget exceeds limit.
    """
    d,fs=p.problem(doc['problem']); const,groups=p.components(d,fs)
    if p.score(const,{}) is None: return (0,0)
    nodes=work=0
    for group,terms in groups:
        leaves=1
        for v in group:
            leaves*=d[v]
            if leaves>limit: return None
        n=(len(group)+1)*leaves
        nodes+=n; work+=n*(len(terms)+sum(len(t) for _,t in terms))
        if nodes+work>limit: return None
    return nodes,work


def root_proof(doc):
    """Produce a zero-branch proof when independent original minima suffice."""
    d,fs=p.problem(doc['problem']); const,groups=p.components(d,fs)
    opt=doc['result']['optimum']; w=doc['result']['witness']; proofs=[]
    if opt is None and p.score(const,{}) is None: return dict(schema=1,problem=doc['problem'],optimum=None,witness=None,proofs=[])
    for i,(_,terms) in enumerate(groups):
        dead=any(not t for _,t in terms)
        if opt is None:
            if dead: return dict(schema=1,problem=doc['problem'],optimum=None,witness=None,proofs=[[i,0]])
        else:
            if dead or sum(min(t.values()) for _,t in terms)!=p.score(terms,w): return None
            proofs.append([i,1])
    if opt is None: return None
    return dict(schema=1,problem=doc['problem'],optimum=opt,witness=w,proofs=proofs)


def replay_upper(proof):
    """Upper bound on counted checker units, before replay (generated trees only)."""
    d,fs=p.problem(proof['problem']); _,groups=p.components(d,fs)
    total=common_units(proof); nodes=0
    for i,tree in proof['proofs']:
        row_count=sum(len(tab) for _,tab in groups[i][1]); stack=[tree]
        while stack:
            node=stack.pop(); total+=1; nodes+=1
            if type(node) is int: total+=row_count
            else: stack.extend(node[1])
    return total,nodes


def select(doc,expected,*,reads=4):
    """Return a checked proof for remaining reads, always first verify elimination.
    checks_used=2 only on accepted conversion (one of each). Rejected conversion
    work is charged separately; original proof is already independently checked.
    """
    anchor(expected); p.require(type(reads) is int and 1<=reads<=10000)
    base=k.check(doc,expected); b=elimination_units(doc,base)
    out=dict(kind='elimination',proof=doc,receipt=base,reason='direct',checks_used=1,attempted=False,
             baseline_units=b,extra_units=0,projected_units=reads*b,search_nodes=0,search_work=0)
    if reads<4 or base['visits']<64: return out
    # Risk cap: screening/producer work budget is 1/8 of the planned baseline proxy.
    budget=min(300000,reads*b//8); common=common_units(doc)
    if 4*common>budget: return out
    out.update(attempted=True,extra_units=common,reason='root_not_tight')
    proof=root_proof(doc)
    if proof is None:
        out['extra_units']+=common
        remaining=budget-out['extra_units']-2*common
        bound=structural_bound(doc,remaining)
        if bound is None or remaining<4:
            out['reason']='structure_guard'; out['projected_units']=reads*b+out['extra_units']; return out
        search=q.Search(nodes=min(12000,max(1,remaining//4)),work=min(300000,max(1,remaining//2)),entries=min(24000,max(1,remaining//2)))
        try: proof=q.generate(doc,search)
        except (q.Exhausted,q.Counterexample): proof=None
        out['search_nodes']=search.nodes; out['search_work']=search.work
        out['extra_units']+=common+search.nodes+search.work
        if proof is None:
            out['reason']='search_refused'; out['projected_units']=reads*b+out['extra_units']; return out
    # Count a conservative replay preflight proxy (common parse + generated nodes).
    upper,nodes=replay_upper(proof)
    out['extra_units']+=common+nodes
    p.require(out['extra_units']<=budget)
    predicted=b+out['extra_units']+(reads-1)*upper
    if 10*predicted>9*reads*b or len(p.canonical(proof))>p.MAX_BYTES:
        out['reason']='cost_guard'; out['projected_units']=reads*b+out['extra_units']; return out
    receipt=p.check(proof,expected)
    p.require(receipt['optimum']==base['optimum'])
    units=partition_units(proof,receipt); p.require(units<=upper)
    out.update(kind='partition',proof=proof,receipt=receipt,reason='converted',checks_used=2,projected_units=b+out['extra_units']+(reads-1)*units)
    return out
