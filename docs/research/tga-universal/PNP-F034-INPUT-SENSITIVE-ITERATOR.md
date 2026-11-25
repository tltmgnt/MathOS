# PNP-F034 — Input-sensitive selected iterator amortization

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base f2d4061c8468c027e21eef56350aa79299858ada (PR #204, includes #205). Independent of
open PR #206 (complete grammar meter; exact preflight 45539541503 passed).
The previous uniform list bound multiplies child budgets by listLimit.
Instead use a state potential: on success, charged cost+1 plus residual
potential is <= initial potential; on failure cost+1 <= initial
potential+D. Doubling preserves the success invariant and increases
failure allowance by only one, since a failed transition short-circuits.
Word dispatch <= potential+D+width, and joint ledger adds 2*width+1.
For the actual Nat-token list meter use potential 3*remaining tokens
and D=3. Candidate bound on every input, including malformed and
oversized headers: list cost <=3*input.length+56. This is a selected
source-level cost bound, not machine cost. This first specialization
is for Nat lists only; extending the potential to nested grammar
parsers and byte-level resources remains outstanding.

Seven candidate declarations; 1131 controls (1122 small, 8 boundaries,
1 empty), including large declared count with very short token tail.
Marker F034_INPUT_SENSITIVE_ITERATOR_OK small=1122 boundary=8 empty=1.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gate unchanged.
No local Lean execution. Exact preflight required before PR.
Independent review and resolution remain open.

## Initial replay and constructive repair

PR #206 merged at 9af7c618d8eeb467c3ee7d0d6a4a990b202b72af.
Exact candidate 2ac6250e88113ff93aba8ca88ec4bef08ccbf5ff failed
[45540163698 / job 138956456235](https://github.com/tltmgnt/MathOS/actions/runs/45540163698/job/138956456235), artifact 14988757964.
Three of seven named declarations (double_safe, word_bound,
joint_bound) printed no axioms. Two proof branches reached reflexive
Nat inequalities without discharging them: the empty word success
case and the successful Nat-token step. Add explicit Nat.le_refl
proofs. Four declarations had sorryAx dependencies from these errors.
No change to executable definitions, statements, fixtures or strict
gates. The executable marker was not reached. Require corrected
exact-SHA replay before PR.
