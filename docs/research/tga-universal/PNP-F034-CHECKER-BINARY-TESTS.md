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
