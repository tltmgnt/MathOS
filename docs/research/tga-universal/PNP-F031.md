# PNP-F031 — Component complexity (partial handoff; not accepted)

**PNP_RESOLUTION_STATUS = OPEN.** This is not a resolution of P versus NP
and is not evidence of progress toward either resolution.

## Provenance and baseline

The handoff identified F030 commit b5ab1ae6d9c0e2fd0cae0ea6e13b69ac53689ab6.
The actual F030 branch tip at inspection was f3ae2c137e826e38fa80f48590826325eaf7772f,
a merge of PR #144 with the requested commit as first parent. This draft
uses that descendant; the comparison showed only the five TGA gap-closure
files changed in between. No changes to main or existing history.

Claude supplied a textual summary, not the six Python sources, scratch
logs or test fixtures. No faithful port can be claimed. The reported
measurements below are unreplicated handoff data, not repository evidence.

## Implemented in this draft

- Four candidate semantic declarations extend the existing F025
  ProctorFactorDecomposition namespace: finite witness selection by
  constructive induction, explicit owner-based witness union, finite
  component SAT equivalence and UNSAT lifting. The existing component_iff
  (empty separator) already establishes the family-witness equivalence.
  The new equivalence assumes supplied valid partition labels and a finite
  bound on clause component labels. Empty components are vacuously SAT;
  an empty clause cannot be satisfied. UNSAT lifting requires no partition.
- The existing F025 audit is extended, not weakened, to require axiom-free
  output for all four declarations in addition to the seven prior ones.
  The existing workflow pins Lean 4.14.0 and treats warnings as errors.
- No Python solver implementation or scratch test has been imported.
  Reuse F025 partition and F030 solve/verify after the originals arrive.
  F025 uses width-three padded clauses and dense witnesses; F030 uses
  sparse normalization, so arbitrary widths, empty clauses and sparse IDs
  need explicit compatibility tests. F026 handles supplied tree decompositions;
  it is not a general component solver.

## Tested

No new Python solver tests were run or ported in this draft. The scratch
handoff reports the following, without source or raw artifacts:

| Scratch module | Reported evidence (not reproduced) |
| --- | --- |
| pnp_f031_component.py | 600 brute-force comparisons, sparse IDs near 1e9, corrupt certificate rejection; disjoint F030-style family 6 component nodes vs 17–12,281 plain nodes (t=1–10) |
| pnp_f031_connected.py | **Negative result:** 21–129 nodes for t=1–8, no component advantage, core-first policy 5 nodes; no demonstrated exponential connected adversary |
| pnp_f032_lab.py | PHP(n+1,n): 12–51,776 nodes n=2–7; random 3-regular Tseitin 111–25,599 nodes n=6–20 |
| pnp_f032_xor.py | syntactic width <=5 detector, GF(2) UNSAT certificate, negative controls, 3000 formula fuzz cases; reported n<=400 in <=7.3 ms |
| pnp_f032_obfuscate.py | one gate-hiding scheme/seed; detection fails and bounded elimination repairs it; 1500 fuzz cases |
| pnp_f032_bvecert.py | resolution log verifier, n<=80, four tamper cases, 1500 fuzz cases |

## Formally verified

The four new declarations passed the pinned Lean replay and strict axiom
 gate in PR #145: run 45436519279, job 138595697242, artifact 14939909674.
Lean 4.14.0 returned exit code 0 with all eleven declarations axiom-free.
The 74 inherited F025 controls also passed. The local execution environment had no Lean
or elan and could not resolve github.com for a git checkout. No local
kernel output is claimed. Evidence: https://github.com/tltmgnt/MathOS/actions/runs/45436519279/job/138595697242 . No executable partition, certificate
checker, search algorithm or machine-cost refinement is formally proved
by these semantic declarations.

## Independently verified

None. The scratch verifier shares helper code with the solver; same-author
replay and a kernel proof do not constitute independent implementation
review. No independent review of this draft is claimed.

## Cost and scope

The scratch literal-touch counter is an **abstract work measure**, not a
Turing-machine or word-RAM bound. A binary input must charge signed ID
length, normalization, component construction, restriction, branching,
assignment/certificate storage, serialization and replay; a dense array
indexed by the maximum variable ID is not a polynomial-space operation
in the sparse binary input length. A node limit is not a total work limit;
budget exhaustion must produce UNKNOWN, never UNSAT. Explicit proof size
can be exponential. F031 total bit-complexity remains unmet.

Resolution lower bounds concern particular proof systems, not unrestricted
SAT algorithms. Haken's pigeonhole lower bound and Urquhart's expander
Tseitin lower bound are for resolution; ordinary tree-like DPLL without
stronger inference inherits applicable resolution bounds. Tseitin parity
systems themselves are solvable by polynomial GF(2) elimination.
The scratch syntactic XOR detector is incomplete; the BVE claim requires
checking the actual resolution derivation and elimination log. Finite
node counts alone establish no asymptotic lower or upper bound.

Primary publication references:
- A. Haken, The intractability of resolution, TCS 39 (1985), 297–308.
  https://doi.org/10.1016/0304-3975(85)90144-6
- A. Urquhart, Hard examples for resolution, JACM 34(1) (1987), 209–219.
  https://doi.org/10.1145/7531.8928

## Unresolved / next acceptance gate

Obtain the six original sources and exact fixtures; compare with F025/F026/
F030, port with relative imports, and preserve behavior rather than silently
reimplementing the experiments. Test sparse IDs, empty CNF/clause, SAT
witness union, UNSAT lifting with tampered evidence, budgets and deterministic
component ordering. Reproduce the disconnected measurements and negative
connected result. A connected family forcing exponential search under
the stated component-aware policy has not been constructed. F032 remains
a separate incomplete experimental track. Require pinned zero-axiom Lean
and actual CI run IDs, then explicit bit-cost analysis and independent
review before accepting F031. No global promotion.

## Native follow-up (not the scratch port)

PR #145 was merged into the F030 branch at e7e593fc53a3045a5ea43de700e52f221f161ebd.
This follow-up deliberately implements a separate adapter using repository
sources, since the six scratch modules remain unavailable. It does root-only
decomposition using F025 partition and F030 sparse normalization and solve.
It accepts signed CNF of width 0–3, pads nonempty short clauses by repeating
their final literal, and treats empty clauses as direct refutations.
Wider clauses are rejected. Smallest components are tried first; the global
F030 search-node budget is decremented across calls. An empty formula may
return SAT without a search node; a zero budget always yields UNKNOWN.

SAT witnesses are checked against the original clauses. UNSAT evidence is
either an original empty-clause index or a sorted set of original clause
indices and the F030 refutation of that subset. The outer verifier does not
reconstruct the partition: a refuted subset suffices by monotonicity.
It reuses F030's verifier and the input normalizer, so independent code
review and kernel refinement of the executable remain open.

New controls: 600 deterministic random sparse formulas compared with brute
force, 600 zero-budget checks, direct tamper tests, and F030's existing
disjoint UNSAT and connected SAT families at t=1,2,4,6,8. The connected
SAT control checks that root splitting gives no gain when there is one
component; it is not Claude's missing connected adversary. PR #146 CI run 45438210589, job 138601729422, completed successfully:
all five component-search tests passed, including the seeded 600-formula
and budget controls; evidence artifact 14942193124.
https://github.com/tltmgnt/MathOS/actions/runs/45438210589/job/138601729422
The native follow-up was merged into F030 at 5249246d80cb8c9baebb369cfc9f28b19a77c905.

Cost accounting: nodes are explicitly abstract search nodes, not bit steps.
For a supplied root partition with component variable counts r_j, complete
search needs at most sum_j (2^(r_j+1)-1) nodes, since each F030 search
splits on a previously unassigned variable. A global node limit also bounds
their sum. This is a schedule bound only. Sparse normalization, partition,
sort, propagation, recognition, Horn closure, stack and certificate storage,
replay and serialization are additional costs. No total machine-model
complexity theorem or general connected search bound is claimed.

## Next native gate: connected root obstruction and explicit machine model

The follow-up supplies a connected obstruction for **this root-only policy**.
Start with F030's disjoint mixed-sign gadgets and fixed UNSAT core, with
4t+3 variables and 24t+8 clauses. Introduce fresh g=4t+4 and its unit clause
(g,g,g). Let a_i=4i+1 for i=0,...,t (the last representative belongs to
the UNSAT core). Append (g,a_i,a_{i+1}) for i=0,...,t-1.
All clauses are non-tautological. The primal graph is connected: every
original gadget and the core is internally connected, and the added
clauses connect their representatives to g. Root F025 partition therefore
returns just one component. Its F030 solver forces g=true before any
branch, removing precisely the added clauses. The residual is the
original F030 obstruction, with unchanged compact IDs and original clause
indices. F030's later decisions are unchanged: g is fixed and excluded
from recognition, counts and branch choices; all original rows, ties
and assignments are preserved. Hence the visited-node count is exactly
the count of the original F030 search, at least 2^t by the F030 argument.
The guarded family has 4t+4 variables, 25t+9 clauses and O(t log(t+1))
encoded bits. This is superpolynomial for the current root-only search
policy, not a lower bound for all SAT algorithms or for dynamic splitting
after propagation. The latter would immediately expose the original
components. The new controls check equality of node counts at five
sizes and budget exhaustion at three sizes; actual CI is required.

A conservative deterministic multitape Turing-machine time bound for a
specified list-based realization of the native algorithm is given in
[PNP-F031-BIT-COST.md](PNP-F031-BIT-COST.md). It charges preprocessing,
per-node work, proof replay, output and sparse-ID bit lengths. It is a
paper analysis, not a kernel-checked or measured CPython transition
bound. The literal-touch/node counters remain abstract. The scratch
code is still unavailable; the old connected negative result has not
been reproduced and this new family does not settle it.
