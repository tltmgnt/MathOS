# PNP-F034 — Parser list counter refinement

PNP_RESOLUTION_STATUS = OPEN.

Verified merged research base 9662fc2772432f20ebcb4d11a36fff4fb9a8002f (PR #196).
Independent of pending byte-prepass candidate 839a9c115f8970d62d40b352df1c48d6f1542810.
The generic list parser uses checked 17-bit remaining-item words
after the original Nat list-limit guard and checked boundary encoding.
Each successful item parse consumes one checked decrement; a zero word
terminates the loop. An explicit Nat structural recursion fuel, initialized
to listLimit, remains in the executable definition. The proposed refinement
assumes fuel >= decoded remaining count; no claim that the Nat fuel is
erased or that all counter operations are binary. No production change.

Candidate equality covers any element parser, success/rejection, remaining
tokens, output ordering, and arbitrary initial accumulators. A successful
decrement preserves 17-bit width; selected bit visits <=17 per attempt.
No composed list-cost, guard/encoding cost, full nested envelope substitution,
allocation or machine semantics claim.

Six candidate declarations, 612 small Nat/Bool list controls, six malformed
cases, three real list-limit boundaries and six nested-list controls.
Marker F034_PARSER_COUNTERS_OK small=612 malformed=6 boundary=3 nested=6.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates preserved.
No local Lean verification; exact-SHA preflight required before PR.
No independent review or resolution claim.
