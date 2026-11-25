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
