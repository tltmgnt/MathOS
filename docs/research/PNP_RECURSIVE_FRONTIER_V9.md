# MathOS v9 — recursive separator and proof composition

Extends v8's static independent-component backdoors with recursive
AND/OR decomposition on connected formulas. No unrestricted SAT claim.

## Run

    python -m mathos.research.pnp_recursive_frontier --checkpoint artifacts/pnp-v9.json
    python -m mathos.research.pnp_recursive_frontier --input cnf.json --depth 6
    python -m mathos.research.pnp_recursive_frontier --resume artifacts/pnp-v9.json
    python -m unittest discover -s tests -p 'test_pnp_recursive_separators.py' -v

Input is JSON n and signed integer clauses; normalized labels are used in
the proof and a new-to-old map is included. The frontier report preserves
unknown and unresolved universal obligations. Resume restarts the input.

## Constructive recursion

At each node, check terminal empty conjunction/empty clause, partition
by shared variables, then try the v7 direct affine/bijunctive algebra.
If neither applies, score up to 32 variables by largest remaining
primal component after deletion, then sum of squared component sizes,
occurrences and label. Select one variable, check both assignments,
and recursively rediscover independent components. A non-separator
fallback split is allowed. No optimal separator claim. The depth cap
counts splits, not AND nodes. Node cap is at most 4096, depth at most
12. Exhaustion raises a resource status, not a mathematical decision.

The independent verifier checks the original signed clauses at every node:
complete and disjoint variable partition for AND, both restrictions in
fixed false/true order for OR, terminal premises or replayed algebra
certificates at leaves. Unknown permits either actual truth value.
An AND is UNSAT if any child is certified UNSAT, SAT if all are SAT.
An OR is SAT if any branch is certified SAT, UNSAT if both are UNSAT.
Otherwise propagate unknown. The verifier reconstructs graph components
by DFS for separator accounting, independently of the union-find finder.
It checks node and split-depth counts, terminal/algebra/unknown leaves,
separator/fallback split counts, and literal-visit proxy. It verifies
soundness, not the heuristic choice or optimality of the tree.

## Connected obstruction and constructive escape

For every m>=2 let h be a hub, and let disjoint triples a_i,b_i,c_i
form the clauses (a_i OR b_i OR c_i) and (h OR a_i). The primal graph
is connected. Every ternary support is exclusive: no other clause
contains its full set of variables. If a global static strong backdoor
into the v7 direct algebra misses that support, assignments outside it
cannot change its ternary clause or produce another clause with exactly
that support. The seven allowed patterns of a signed OR are neither
majority-closed nor ternary-XOR-closed (v8 witnesses). Hence the residual
cannot compile into either direct mode. Each of the m disjoint supports
must be hit. Choosing all a_i suffices, since every residual is 2-CNF.
Therefore the global static strong backdoor size is exactly m.
The verifier checks the disjoint/exclusive support premises; the counting
and closure argument is mathematical, not machine formalized.

The recursive method instead selects h, whose deletion separates all
m triples, then chooses one variable per component in each branch.
The family has 3m+1 variables and 2m clauses. Both hub assignments are
processed, each with m components and two local leaves. Thus the proof
tree uses 4m leaves and split depth two, vs 2^m assignments in full
global enumeration of a minimum static backdoor. The finite probes
verify these counts up to m=64. This is a comparison of specified
enumeration schemes, not a runtime lower bound or claim that other
algorithms cannot solve this easy family.

## Complexity accounting

With n active variables and split depth d, at a fixed split depth the
total active-variable count across nodes is at most a constant times
n*2^d: AND partitions disjointly and each split duplicates remaining
variables at most twice. There are no consecutive AND nodes in the
generated tree; empty leaves arise only from a split or the empty root.
Charging nonempty nodes and empty children to active variables gives
O(n*2^d) nodes across all split depths. This is a conservative
combinatorial bound for generated trees, not an optimal bound.
Per-node selection, restriction, partition, algebra decision and
certificate replay have polynomial overhead for fixed v7 relation arity.
Consequently a fixed or logarithmic successful split-depth bound would
give polynomial total overhead, but there is no guarantee of finding
such a tree for arbitrary input, and the current implementation caps
depth, nodes and resources. Work steps and literal-visit proxies are
not measured CPU time or a hard RSS bound. Complexity arguments are
not yet verified in a formal machine model.

## Formal verification

Lean checks three-valued AND/OR soundness and its extension to arbitrary
finite binary trees with valid leaves. Known SAT or UNSAT is sound
under any completion of unknown leaves. This abstracts disjoint AND
and exhaustive OR composition; it does not formalize the CNF
partitioner, algebra checker, separator heuristic, or complexity proof.
Separate CI enforces axiom-free theorem checks. O08/O09/O10/O11/O12
remain unresolved in the executable report; no P versus NP conclusion
is inferred from the finite results.
