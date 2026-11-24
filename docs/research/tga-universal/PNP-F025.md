# PNP-F025 — Separator-conditioned factor-graph decomposition

Baseline: F024 PR #137 head a92936c913a60e4c5d212e68b795152e6eb40f1c,
scope replay 45421468050 succeeded (8 strict declarations, 26 formulas,
88 affine branches, 153266 structural steps). F025 is stacked on that
head while the parent PR remains open.

## Mathematical result

For a finite list of clauses, label each nonseparator variable with a
component owner and each clause with a component. Require each literal
to be on a separator variable or a variable owned by its clause's component.
Fix a common separator assignment sigma. A global witness restricts to
a family of local witnesses, and conversely a family of witnesses can be
glued by choosing sigma for shared variables and the owner's assignment
elsewhere. The Lean statement uses a total family of Boolean assignments,
so no choice principle or arbitrary existential witness selection is needed.
The empty-separator theorem is the disconnected-component special case.
This is a conditional gluing theorem, not a proof that arbitrary graphs
have small separators.

## Executable decomposition

Given signed 3-CNF and an optional supplied separator, enumerate its
assignments in lexicographic order. Drop satisfied clauses, delete false
fixed literals, reject any empty residual clause immediately. Build
connected components by unioning variables of each remaining clause.
Rename each component's used variables to compact indices; pad residual
one- or two-literal clauses with repeats. Solve each local formula with
F024's exact affine-backdoor reference, then glue SAT witnesses and check
the original formula. Unused variables can be false.

UNSAT evidence contains one entry per separator assignment: an original
clause index that is already false, or an index into the canonical residual
component list plus a complete F024 branch-dual certificate for that component.
The verifier reconstructs the partitions, checks all separator assignments
and verifies each selected contradiction; SAT verification uses only the
original CNF. Truncated, reordered or corrupted evidence is tested.

## Complexity and remaining gap

Let s be separator size, k_{sigma,j} the F024 backdoor size of component j
under sigma, and L_{sigma,j} its materialized affine problem dimensions.
The number of affine calls is at most sum_sigma sum_j 2^k_{sigma,j}.
The affine structural charge is at most
sum_sigma sum_j 2^k_{sigma,j} B_j, with B_j the F014 affine structural
bound for that branch's width and row count. Partition construction,
enumeration, certificate checking and allocation are additional costs.
For a common bound k, at most 2^(s+k) times a polynomial in explicit input
size suffices as an abstract schedule. This is a parameterized bound, not
a machine trace theorem. Disconnected components avoid a Cartesian product
of independent branch searches. No universal logarithmic s+k is established,
and UNSAT evidence can still be exponential. The Python recursion and
machine refinement gaps remain. No proof of P = NP or P != NP.

## Validation

Run python -m unittest discover -s tests -p 'test_tga_proctor_factor_decomposition.py' -v
and python -m mathos.research.tga_proctor_factor_decomposition_audit --output-dir artifacts/pnp-factor-decomposition.
Seven new declarations are audited with Lean 4.14.0 and no axioms.
The 74 finite fixtures cover all ordered pairs from four clauses with
four separator choices, empty formulas, split and connected instances,
and direct separator contradictions. The report records actual control
counts. Python partition/conditioning implementation is not formally refined
to the gluing relation. F024 regression tests are rerun separately.
No independent review or global promotion is claimed.

Next: formal residual conditioning and partition-construction correctness,
then supplied tree decomposition dynamic programming / affine backdoor
optimization with explicit worst-case accounting.
