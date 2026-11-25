# PNP-F034 — Binary checker equality and identifier range tests

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base ee03c935217ac0488fe35c0809164fcd9df224be (PR #217). Independent of pending
encoder-aware byte checker and value projection candidates.

Use existing zero-padded borrow circuit twice for unsigned value
equality (two NOT and one AND) and for the checker identifier
predicate 0<v<=n (one NOT and one AND). Prove exact Boolean result
and gate ceilings 10*w+3 and 10*w+2 for both operands of width
at most w. Distinct representations of the same value (including
leading zero padding) compare equal. Checked Nat adapters encode
both operands, return none on failed encoding, and refine the
original predicates under the representability hypothesis. Gate
bounds apply even on rejected inputs. At 512 bits: 5123 and 5122.
Encoder events, operand widths for all derived checker arithmetic,
padding allocation, storage and complete checker substitution
are not established by this stage. No claim of full machine cost.

Ten candidate declarations and 2618 control groups
(961 word pairs, 1641 checked adapters, 16 wide pairs).
Marker F034_CHECKER_BINARY_TESTS_OK pairs=961 adapters=1641 wide=16. Strict Lean 4.14.0 warnings-as-errors
and zero-axiom gates unchanged. No local Lean execution.
Require exact replay before PR. Independent review and resolution
remain open.

## Initial replay repair

Exact head 6956c97c54157bf30879e25d5474dcfd3bdad3b8 failed [45555814873 / job 139007462688](https://github.com/tltmgnt/MathOS/actions/runs/45555814873/job/139007462688), artifact 14994979054. Lean parsed the unparenthesized Boolean negation in the private not_less_test statement as negation of a decidable equality, rather than equality of the negated Boolean. Parenthesize the complete negated Boolean on the left side. Two direct value proofs and two dependent adapter projections failed elaboration; six independent declarations printed no axioms. The executable marker was not reached. No public theorem statements, executable definitions, fixtures or gate requirements changed. Require fresh successful exact-head replay before PR.
