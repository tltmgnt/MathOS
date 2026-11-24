# PNP-F029 — Constructive renamable-Horn deletion discovery

Baseline: F028 at a3fd8a71e567062f710102df7d069a83a4a8281d, with
successful strict CI run 45427176592. F028's Horn/dual-Horn approach
is limited to a single global sign. F029 generalizes to individual
variable complements and retains all inherited code and tests.
**P versus NP remains open.** New results are not claimed novel.

## Exact recognition, constructive but nonoptimal deletion

After F027 compression, let f_v denote whether variable v is
complemented. A positive original literal remains positive iff f_v
is false; a negative literal becomes positive iff f_v is true.
For each pair of distinct surviving literals a,b in a clause,
the condition that they are not both positive is the 2-CNF clause
(a OR b) over flip bits (signed literal IDs retain their original signs).
Thus the conjunction of these pair constraints is satisfiable iff
the clause-deleted residual is renamable Horn. Deletion here means
removing all occurrences of the selected variable, not removing clauses.
Tautologies are discarded first and duplicates collapsed.

The implication graph contains edges not-a -> b and not-b -> a.
The standard SCC criterion for 2-SAT is exact: a variable and its
negation in the same SCC rule out any solution. Otherwise the later
of the two components in a topological order can be set true, yielding
a satisfying assignment. The implementation uses iterative Kosaraju
and checks the resulting flip assignment against every pair.

When recognition fails, remove a deterministically chosen contradictory
variable and repeat, at most n deletions. Greedily restore removable
variables, then compare against the inherited F028 global-polarity cover.
The selected plan is valid and no larger than the F028 candidate; there
is no approximation claim relative to the minimum renamable-Horn
deletion set. The greedy candidate before comparison is inclusion-minimal,
not necessarily minimum cardinality. The fallback need not be inclusion-minimal.

Fix any assignment to the deleted variables. Satisfied clauses vanish;
otherwise their fixed literals vanish. No clause can acquire a second
positive literal in the fixed orientation. Apply F028 Horn closure to
each branch. Original witnesses are unflipped and checked. For UNSAT,
the original clauses are flipped and the inherited F028 verifier checks
all branch traces. Budget exhaustion is UNKNOWN, not a SAT decision.

## Cost and encoding

For n explicit variables and m clauses, each recognition uses at most
2n graph vertices and 6m implication edges, with O(n+m) DFS work after
pair construction. Deduplication and sorting are polynomial. There are
at most 2n+1 recognition calls including greedy restoration, plus F028
fallback planning and checks. These are abstract operation bounds, not
a formally refined bit machine. With k selected deletions and budget L,
at most min(2^k,L) branches are processed; each uses at most n+1 scans of
m clauses plus witness work. UNSAT trace size can be exponential in k.

A separate sparse_input routine compacts occurring variable IDs to
1..r with r <= 3m, even if the declared n is huge and binary encoded.
It returns the reverse map, and preserves every literal evaluation
under assignment restriction and extension; omitted variables can be
set false. This is a polynomial-size normalization in standard bit
encoding, not a full bit-string parser or formally verified bit-time
implementation. Call solve on the compact formula and r, not the
potentially huge original n. A polynomial per-branch cost still does
not imply a polynomial bound on all branches.

## Track B: obstruction and progress

F028's connected positive/negative clique family becomes renamable Horn
without deleting any variable: complement the positive block, keep the
negative block (the shared variable may be complemented). This removes
the prior syntactic obstruction for this family.

New connected family: t disjoint pairs (a_i,b_i), shared variable c,
and all four clauses (±a_i, ±b_i, c) per pair. Setting c true satisfies
the formula. For any deletion set missing both a_i and b_i, all four
signed pair constraints remain, and no flip assignment satisfies them.
Thus at least one variable of every pair must be deleted, so k >= t.
Conversely delete all a_i and complement c: at most one positive
literal remains per clause, proving the exact syntactic deletion minimum t.
There are 2t+1 variables and 4t clauses, O(t log t) encoded bits, so the
minimum is not O(log input length). This is not a lower bound for semantic
strong backdoors with propagation, adaptive orientations or SAT generally.
In particular a satisfying assignment can be found without exploring all
branches. It rules out only this deletion-based uniform orientation target.

## Evidence and next gates

The four new local Lean declarations check pair encoding, exact
three-slot positivity counting, deletion monotonicity, and flip
involution. They do not formally certify the SCC implementation, greedy
algorithm, entire formula reduction, certificate replay or bit complexity.
CI runs F028 regressions, F029 tests and controls, and strict zero-axiom
Lean replay (4.14.0). All new checks are pending until actual CI evidence.
The controls compare 4,162 formulas against brute force and 16,645
deletion/recognition cases against exhaustive orientations; separate
tests cover 256 three-variable sign-subsets and small exact minima.

F029 closes the constructive *candidate discovery* design, not universal
small-parameter discovery. F030 should pursue propagation-aware or
adaptive residual classes and classify whether counterfamilies survive
preprocessing. F031 must refine total bit complexity and recursive
cost. F032 barrier analysis, F033 unconditional universal bound or
general lower bound, F034 end-to-end formal refinement, F035 external
review and F036 resolution remain open. Do not promote a scoped
algorithm, counterexample or passing CI into a P versus NP result.

Reproduce:

    python -m unittest discover -s tests -p 'test_tga_proctor_renamable_horn.py' -v
    python -m mathos.research.tga_proctor_renamable_horn
    lean -DwarningAsError=true formal/ProctorRenamableHorn.lean
