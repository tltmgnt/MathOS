# F035/F040 — Deterministic exhaustive certificate discovery baseline

PNP_RESOLUTION_STATUS = OPEN.

Based on verified input-bound envelope completeness head
4fd3a57c03bf081e586c21307725dc2c0faea314 (PR #241, run
45637419634/job 139286528382, 19 zero-axiom declarations, 24 controls).
Ordinary typed completeness PR #240 merged. This branch is independent
of the pending unbounded wire encoder repair.

Candidate actual deterministic generator, not just a Prop existence
argument. At each leaf search the accumulated frontier for a row whose
literals are all contained in the blocking path. At an internal node
generate both children, search for their exact blocking clauses and
resolve them. Trace n f ss g links the exact returned steps to the
frontier and identifier-validity invariant. Build_complete proves
successful construction on every UNSAT original formula under the
coverage/validity hypotheses. Generate_complete compiles the actual
trace, proves original input binding and validity, and handles n=0
separately. Decide_iff is an unconditional UNSAT equivalence on valid
finite typed formulas, not conditional on a supplied complete generator.
It verifies the generated proof and therefore inherits soundness even
if generation fails. No assertion of correctness on invalid formulas.

This is an ordinary decidability baseline: the generator recursively
splits over the list of literal variable occurrences, including duplicate
identifiers. Worst-case complete traversal can be exponential, with
additional explicit frontier copying and row search overhead. No
polynomial bound on proof size, search, or total bit cost is asserted.
This does not discharge F040 polynomial discovery. No new complexity
class theorem follows from ordinary decidability of SAT.

15 candidate declarations, 25 finite control groups: 16 subsets of
four 2-variable clauses, 4 one-variable subsets, 2 zero-variable
cases, one sparse wide variable case and 2 duplicate/tautology cases.
The controls call the actual candidate generator and decision function.
Strict Lean 4.14.0 warnings-as-errors and explicit zero-axiom checks.
Marker F035_EXECUTABLE_DISCOVERY_OK pairs=16 singles=4 empty=2 sparse=1 duplicates=2.
Fresh exact-head CI required. Main unchanged.
