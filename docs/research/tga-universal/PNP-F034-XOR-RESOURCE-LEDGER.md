# PNP-F034 — XOR selected terminal resource ledger

PNP_RESOLUTION_STATUS = OPEN.

Based on merged research head 34ea00c74f8580d3335cf67c7f34eb25ebe38f8e
(PRs #229–232 merged). Independent of the pending unified checker.
Twenty-one candidate declarations compose selected reference lookup
visits, row comparison gates, signed-pattern membership gates and
sparse support toggle comparison gates into two separate coordinates.

The result projection targets xorBinary for arbitrary typed operands,
including failed encoding cases. The block reservation first checks the
existing length <=5 guard; an oversized block reserves no reference or
pattern operations. On other blocks it reserves both reference checks
and all signed-pattern branches. The sparse sum reservation follows the
actual binary support outputs, including duplicate and out-of-width
identifiers. Sum reservation is independent of block success.

The gate budget is the sum of guarded block reference/pattern budgets
and the support-combination budget; the lookup budget is the sum of
guarded reference visit budgets. Bounds reuse (w+1)*F per checked
reference lookup, literalBudget(w)=10*w+6 per literal comparison, and
eqBudget(w)=10*w+3 per inspected support identifier. Budgets are
recursive and data-dependent, not yet a closed polynomial in byte size.
This is an eager selected reservation, not actual short-circuit trace.
Structural enumeration, Boolean operations outside metered primitives,
encoding, padding, allocation and full machine runtime are excluded.

Strict Lean 4.14.0 warnings-as-errors, exact marker
F034_XOR_RESOURCE_LEDGER_OK blocks=252 pairs=441 terminals=6 positive=1 guards=1 malformed=1 wide=1
and explicit twenty-one zero-axiom checks. 703 control groups, some
containing multiple checks. Fresh exact-head replay required before PR.
No local Lean execution, polynomial certificate existence, or P vs NP
resolution claim.
