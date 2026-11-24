# PNP-F031 — Dynamic resolution boundary and cubic Tseitin controls

PNP_RESOLUTION_STATUS = OPEN. Baseline PR #148 merged into the bit-cost
branch at f587c3e3697eb76d74130255eeab7c0f726a4e8c. Its actual CI
run 45441330118, job 138612954555, passed all six dynamic tests:
800 brute-force comparisons (354 SAT, 446 UNSAT), 800 zero-budget
checks, eight dynamic visits for the guarded family at t=1,2,4,8,16,32.
Evidence: https://github.com/tltmgnt/MathOS/actions/runs/45441330118/job/138612954555
Artifact 14943058397. PR #147 merged into F030 separately; #148 was
merged into its research parent branch, not automatically into F030.

## Explicit conversion to ordinary resolution

For a verified dynamic refutation with V certificate nodes, m input
clauses and r occurring variables, derive an ordinary resolution proof
with at most m + V(mr+1) lines. No weakening, extension or oracle rule.

Maintain a residual clause C with a line deriving D=C union A, where A
is a subset of the literals falsified by **binary decisions** along
the current path. Initially D=C is an original clause (duplicates of
literals are interpreted as sets and tautologies are omitted).

- Binary decision l=true: discard satisfied residual clauses; remove
  -l from each other residual clause. Keep its derived line unchanged,
  since -l is now a permitted falsified decision literal.
- Forced unit l: its reason is a residual singleton, so its derived
  line is {l} union A. For each surviving residual clause containing
  -l, resolve its derived line with that reason on l. This removes
  -l and unions only permitted decision literals. Other surviving
  clauses need no new line.
- Pure literal l: no residual contains -l; discard those containing l.
  No new derived line is needed. Derived lines contain no pure-assignment
  complements, because the invariant tracks only binary decisions.
- Subset: keep only the named residual clauses and their derived lines.
  Independence is unnecessary for UNSAT lifting.
- Conflict: the residual is empty, so its derived line consists only
  of falsified decision literals.
- Binary join: the two conclusions contain only complements of the
  shared ancestor decisions and possibly opposite split literals.
  If either conclusion omits its split literal, reuse it. Otherwise
  resolve them once, removing the split variable.

Induction on the finite certificate tree proves the invariant and that
the root conclusion is empty. Each node has at most r unit events, each
requiring at most m resolutions, and at most one binary join; the
m initial axioms cover every retained clause. Therefore the stated
polynomial overhead follows. The extractor is iterative and starts
by checking the dynamic proof. The ordinary resolution checker derives
every line from original CNF or two earlier lines and verifies a named
empty conclusion; it does not call the dynamic verifier or solver.
This is a same-author paper proof and executable audit, not a
kernel-refined theorem or independent implementation review.

## Actual asymptotic obstruction for dynamic decomposition

Apply the above argument to odd-charge Tseitin formulas on an infinite
family of connected simple 3-regular expanders. There are r=3q/2 edge
variables and m=4q width-three clauses for q vertices. Every vertex
enforces XOR of its incident edge bits equal to its charge. Summing
the equations over GF(2) gives 0=1 because each edge occurs twice.
The primal graph is connected (the line graph of the connected cubic
graph).

The classical general-resolution lower bound is 2^Omega(q) for these
formulas. See Urquhart 1987, and Ben-Sasson/Wigderson 2001 (connected
3-regular expander corollary). Since the dynamic solver emits a proof
with V no greater than its visited-node count N, and the conversion
has at most 4q+N(6q^2+1) lines, the lower bound implies
N=2^Omega(q) for completed UNSAT search on that family. For budget
below the required node count the solver must return UNKNOWN.
Input length is O(q log(q+1)) bits with compact labels, so this is
superpolynomial in input length. This is a consequence of an existing
proof-system lower bound and the local conversion argument, not a
new resolution lower bound. It applies to this dynamic solver's
certificate language, not all SAT algorithms or stronger proof
systems. GF(2) elimination can solve the original parity systems in
polynomial time. No universal SAT complexity result follows.

Primary references:
- A. Urquhart, Hard Examples for Resolution, JACM 34(1), 209–219 (1987),
  https://doi.org/10.1145/7531.8928
- E. Ben-Sasson and A. Wigderson, Short Proofs Are Narrow—Resolution
  Made Simple, JACM 48(2), 149–169 (2001),
  https://eccc.weizmann.ac.il/eccc-reports/1999/TR99-022/index.html

## Finite controls and limitations

Generate connected cubic graphs as a cycle plus a seeded disjoint
perfect matching; do not claim a uniform random sample or certify
expansion. Odd-charge controls: q=4,6,8,10,12,14,16, seeds 11 and 29.
Record dynamic visits and actual extracted resolution lines. These
finite controls do not prove the asymptotic lower bound. The proof
uses the established expander theorem, not these samples. Even-charge
and full truth-table controls check the encoding on K4. Extract
resolution from 600 seeded random sparse CNFs whenever UNSAT; reject
malformed axioms, pivots, references and conclusions. Actual CI must
report success before counting these new tests as passed.

No dynamic machine-cost refinement has been proved; the older root-only
bit-cost model is not automatically transferred. The original six
scratch modules are still missing. Next: native XOR detection and
GF(2) certificates, with negative controls and explicit proof-system
scope.
