# PNP-F027 — Syntactic affine backdoors and clause compression

Baseline: F026 merged into F025 research branch at
4b0265000e8913b9153012de31b1ab2a3cc034e1. F025 strict kernel replay
45423765660 and F026 replay 45423710340 succeeded. F026 has six
axiom-free interface-join declarations, 35 bounded controls (32 SAT,
3 UNSAT), 272 candidate entries, and 252 entries on the 64-variable
width-one chain. This base is not the main branch.

## Exact compression and syntactic backdoor

For signed 3-CNF with explicit n variables, remove repeated literals,
tautological clauses, and duplicate clauses. Keep original clause
indices for refutations. Build a simple graph by putting an edge
between every pair of distinct variables in each surviving clause.
A vertex cover B ensures that each clause has at most one distinct
unfixed variable after assigning B, because two unfixed variables
would form an uncovered edge. Each residual clause is then satisfied,
false, or a single signed literal (the affine equation x=b).
Solve the residual system by direct unit assignment and conflict
detection, a specialized affine solver. Unused coordinates are false.
This does not need F014 row elimination, because every residual row
has at most one nonzero coefficient.

The Lean local kernel proves exact three-slot classification, pair
coverage sufficiency, repeated-literal and tautology identities,
literal complement and opposite-unit inconsistency. It treats free
slots as separate Boolean coordinates after duplicate removal.
The graph construction, compression algorithm, and Python certificate
search are not formally refined to those lemmas in this milestone.

## Cover optimization and proof of the approximation guarantee

A deterministic greedy maximal matching M gives a cover consisting
of all its endpoints. Every vertex cover must intersect every
matching edge, which is vertex-disjoint from the others; hence
|M| <= OPT <= 2|M|. Maximality ensures no edge has both endpoints
outside this cover. Trim redundant vertices, try a second
highest-degree greedy cover with deterministic tie breaks, and
choose the smaller valid cover. The retained matching lower bound
and cover cardinality satisfy |M| <= OPT <= |B| <= 2|M| <= 2OPT.
OPT here is the minimum cover of this syntactic graph, not the
minimum possible semantic backdoor for SAT. The approximation argument
is mathematical, not kernel-verified graph code.

For k=|B| and m' retained clauses, at most 2^k branches and m' scans
per branch are needed. Preprocessing is polynomial in explicit input
size, plus sorting, graph construction, matching, degree-greedy
search, trimming, and witness initialization. All certificates may
be exponential in k. A supplied or constructed logarithmic cover
suffices for polynomial search, not for all unrestricted formulas.
Do not confuse the scan count with actual machine transitions.
The F024 gate-coordinate backdoor size is recorded only as a comparison:
different representations, not a performance ratio or proof of dominance.

## Certificate format

SAT contains the original n-bit witness. UNSAT contains a sorted unique
cover and one refutation for each of its Boolean assignments in lexical
order: an original clause that is false under the assignment, or two
original clauses with opposite unit residuals. The verifier checks the
original formula or reconstructs the cited residuals directly, and rejects
missing branches and corrupted indices. Soundness of this verifier does
not require trusting the cover heuristic, nor do its decisions depend on
the claimed scan counters or matching bound.

## Controls

103 bounded formulas compare with brute force and check the 2-approximation
against exact small-graph cover enumeration. A duplicate-heavy 64-variable
star has 63 graph edges and a one-variable cover. All positive triples on
12 variables produce a complete graph and a minimum cover of size 11,
despite the formula being trivially SAT. This is a barrier to universal
logarithmic covers for this method, not a lower bound on SAT algorithms.
Six tests cover malformed input, compression, false and opposing-unit
refutations, and empty/tautological formulas. Previous factor and tree
regressions are rerun. Actual report determines acceptance.

Run python -m unittest discover -s tests -p 'test_tga_proctor_affine_backdoor.py' -v
and python -m mathos.research.tga_proctor_affine_backdoor_audit --output-dir artifacts/pnp-affine-backdoor.
Seven Lean declarations must pass the strict no-axiom gate. No machine
refinement, independent review, universal polynomial time or prize solution
is claimed.

Next: F028 universal reduction falsification and representation-sensitive
barriers; formal graph-cover/refinement proof; compare with semantic
backdoors and treewidth rather than assuming a universal small parameter.
