# PNP-F034 — Encoder-aware byte checker selected resources

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base 5c8992c083c5ee0f5760338a3e0e0c4d23a5c01e (PR #216). Four files copied byte-identically
from verified PR #217 head 258b092514fa4a6753496038e308018a5fe49f59, exact preflight 45553494229/job
138999922531/artifact 14995076418, 43 zero-axiom declarations and
131 controls. Require #217 merge and successful exact-head replay
before opening PR.

Decode using checked binary tokenizer result and complete encoder-aware
grammar, charging grammar selected events plus one final-consumption
test only on successful tokenization. The token wire-length theorem
lifts the 512*m+3 grammar bound to 512*b+4 per input byte stream.
Both inputs decoded; charge typed checker only when both succeed.
Exact result projection to original byte checker and fuel-free
decoder, with accepted-input UNSAT soundness. Pair selected grammar
and checker bound is (512*a.length+4)+(512*b.length+4)+globalUnit(byteCap a b).
Four separate scanner coordinates per input, bounded respectively by
5235*b, 1046*b+8, 20*b, 21*b. Combined resource theorem keeps these
coordinates separate from the grammar/checker ledger. No summed
machine instructions, fused execution or claim of bit-cost refinement.
The grammar is a header accounting wrapper, not recursively substituted
encoder execution. Nat projection, storage, allocation, byte
classification and other operations remain unaccounted.

Eleven candidate declarations and 125 executable control groups
(8 expected, 12 envelope, 96 pairs, 8 malformed, 1 positive);
scanner ceilings also tested on expected, envelope and malformed
fixtures. Marker F034_ENCODER_BYTE_CHECKER_OK expected=8 envelope=12 pairs=96 malformed=8 positive=1.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
No local Lean execution. Independent review and resolution remain open.
