# PNP-F034 — Unified typed certificate metering

PNP_RESOLUTION_STATUS = OPEN. Both terminal branches are merged.
PR #175 final run 45500649175 job 138822703599: 24 zero-axiom
declarations, 24 capacity cases, six hand controls, selected
count=1668002, terminal_accept=11. Artifact 14969934881.
PR #176 final run 45500645438 job 138822688303: 20 zero-axiom
declarations, 21 XOR cases, six hand controls, selected
count=26495, terminal_accept=10. Artifact 14970976767.
The original capacity run 45499880801 job 138820033867 failed:
artifacts/pnp-f030/f034-capacity-meter-combined.lean:2258:2: error: unsolved goals
Process completed with exit code 1.
The original XOR run 45500289835 job 138821445897 failed:
artifacts/f034-xor-meter/combined.lean:2213:2: error: unsolved goals
Process completed with exit code 1.
Repository corrections 1d5b4c2292f085ff6ac4459005757050a34928a8
and bb65525f64dec2eb6948928c08671c9eff0046e5 respectively closed
the false guard cases with reflexivity. Both merges are ancestors
of base 386a983f285012663b35b88928bf19b32b8ad771.
https://github.com/tltmgnt/MathOS/actions/runs/45499880801/job/138820033867
https://github.com/tltmgnt/MathOS/actions/runs/45500289835/job/138821445897
https://github.com/tltmgnt/MathOS/actions/runs/45500649175/job/138822703599
https://github.com/tltmgnt/MathOS/actions/runs/45500645438/job/138822688303

## Unified selected charge semantics

New ProctorUnifiedMeter composes existing chain, capacity and XOR
meters with an empty-clause row scan, ordered formula equality,
declared bound comparison, original label and proof label checks.
The candidate bound_value equates the Boolean projection to the
production boundCheck, bound_cost bounds the selected count by an
explicit structural budget, and bound_sound links an accepted
metered verdict to UNSAT of the independently supplied typed formula.
Neither terminal recognition nor proof discovery is performed.

The formula equality meter visits both lists simultaneously until
either ends, charges a row-list comparison per pair or end marker,
and uses the earlier row equality meter on each pair even if a prior
pair failed. Range checks charge two comparisons per label and one
per enclosing traversal element. Empty terminal counts visited
formula rows. Bound comparison costs one. All conjunction operands
are evaluated eagerly, even on a binding mismatch. Target construction
is reused verbatim and not charged. Existing terminal meter charges,
including hoisted demand lookup, remain unchanged. Generic folds are
reused from capacity for this new layer; the independently verified
XOR folds remain intact to avoid changing their verified implementation.

## Analytical polynomial envelope (not kernel-proved)

Let S be total natural tokens in the canonical expected and envelope
data files, including all explicit annotations and intermediate
tails. Each row, label, step, group, block, reference and batch count
is at most S, and the sums of their encoded occurrence counts are
bounded by S. An augmented target may contain two copies of the
original (if the chain is empty), so its row and literal totals
are bounded by 2S. Formula binding and ranges have linear selected
budgets. Each step's two lookup scans and parent shape budgets are
O((S+1)^2), with at most S steps. Reference equality and lookup
budgets across each terminal are O((S+1)^2). Capacity groups have
sum of cubes at most S^3; each tuple budget scans at most S
conflict references/literals with width at most three, giving
O((S+1)^4) including internal enumeration visits and distinctness.
Demand-pair indexed lookups are cubic at worst, with pairwise
literal comparisons quadratic; coverage is quadratic. XOR patterns
have at most 32 leaves per guarded block with at most five
literals per pattern; total reference/pattern budgets are at most
quadratic. Sparse support summation has at most S toggles on lists
of length at most S, including over-width rejected blocks.
Thus the selected additive budget is analytically O((S+1)^4),
not a formal global polynomial theorem. The fixed test envelope
256*(A+1)^4 uses A total custom wire bytes, not a proved constant.
It is tested on fixtures only. No allocation, arithmetic bit cost,
parsing, file IO, constructor/closure overhead, or actual
short-circuit machine trace is bounded by these claims.

## Validation

22 candidate declarations, strict Lean 4.14.0 zero-axiom gate.
Static runner reuses 53 typed file pairs; expected 19 accepted,
34 rejected. Compare full meter result to boundCheck and fixture
verdict, compare charges to recursive budget, test loose quartic
byte envelope and four direct hand counts. Exact marker:
F034_UNIFIED_METER_OK cases=53 accepted=19 rejected=34 hand_controls=4.
New CI pending; no local Lean. Prior gates preserved. No total
machine complexity, independent review, original scratch port,
unrestricted SAT result or main change. Next: formalize the
polynomial bound for the selected abstract budget using encoded
structural size; keep parser and machine refinements separate.
