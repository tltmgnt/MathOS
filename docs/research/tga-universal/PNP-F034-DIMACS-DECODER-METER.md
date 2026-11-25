# PNP-F034 — Combined strict DIMACS decoder selected-charge bound

PNP_RESOLUTION_STATUS = OPEN.

Base is the merged lexer research parent
e30a40af7e3b2dbfdbacafb1fec9e27baf6a2f69 (PR #187). The exact
row candidate a086d24ba4047af05ad526c6be40cef250ef37a3 passed
mandatory preflight 45521685022 job 138894849064: all 13
declarations zero axioms; 73 files, 63 lexed, 56 parsed,
12 hand controls, selected=10549. Artifact 14981435078.
Initial failed run 45521309027 job 138893570455 is documented
verbatim in PNP-F034-DIMACS-ROW-METER.md. PR #188 opened after
successful preflight but is not yet merged. This branch starts
from the current merged research parent and carries its four
exact preflight-verified row files unchanged so that composition
can be checked without an unverified dependency. Do not open
the composition PR until #188 is merged and the exact new
candidate passes mandatory preflight.
https://github.com/tltmgnt/MathOS/actions/runs/45521685022/job/138894849064
https://github.com/tltmgnt/MathOS/pull/188

## Candidate theorem

decodeMeter binds the complete lexMeter to rowsStage, using
the returned token stream directly. It does not invoke the lexer
twice. A lex failure charges no row work. A successful lex
charges the declared-row-limit comparison and, if allowed, the
verified rowsMeter. Value correspondence covers all raw byte
lists, including rejected or oversized files. The exact charge
decomposition theorem equals the lexer ledger plus the separate
row-stage ledger. The candidate bound is
  decoderUnit(A) = lexUnit(A) + (rowsUnit(A)+1).
Constructive affine normalization proves equality to 34A+29
for all natural A, rather than relying on an external algebraic
expansion. The final decode_meaning pairs independent raw
grammar on a successful decode with that linear inequality.
These are selected charges (including structural reversal
credits), not a proof of complete runtime, allocation, bit
operations, stack space, IO or compiler refinement.

11 candidate gated declarations. All 73 existing DIMACS files,
including malformed and over-limit inputs, six hand controls.
Expected aggregate selected count 1641507+10549=1652056
from prior verified independent fixture ledgers; this aggregate
is a new candidate control, not measured until replay passes.
Marker F034_DIMACS_DECODER_METER_OK files=73 lexed=63 parsed=56 hand_controls=6.
No production changes. Existing gates preserved, main untouched.
No independent review, proof discovery or proof-size guarantee.
Next: combine decoded formula, proof decoder and verifier selected
charges on acceptance and rejection; extend control/reversal and
integer bit-cost accounting.
