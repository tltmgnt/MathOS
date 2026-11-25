# PNP-F034 — Raw-pair end-to-end selected-resource composition

PNP_RESOLUTION_STATUS = OPEN. Current merged research base
ef496ba3c66cda84416ef9afa12253fa34be6ac1 includes PR #188.
Combined decoder candidate b0767f7e94a8a5813035e196a015480a3e881caf
passed exact-SHA preflight 45522764251 job 138898488686:
11 zero-axiom declarations, 73 fixtures, 63 lexed, 56 parsed,
6 hand controls and 1652056 selected charges. Artifact 14980512652.
Initial failure 45522077278 job 138896175071 is documented in
PNP-F034-DIMACS-DECODER-METER.md. PR #189 was opened after
successful preflight but is not yet merged. This branch starts
from the verified merged base and includes the four exact
preflight-verified decoder files unchanged. Do not open this
PR until #189 merges and this candidate passes exact-SHA preflight.
https://github.com/tltmgnt/MathOS/actions/runs/45522764251/job/138898488686
https://github.com/tltmgnt/MathOS/pull/189

## Candidate composition

The raw-pair meter evaluates both decoders, then enters the
typed checker only if both return values. It charges both
decoder ledgers even when one fails, plus the eager selected
typed verifier ledger when both succeed (even if verification
fails). No extra charge for the final dispatch is defined.
No production changes. Functional projection is to checkBytes
or checkDimacs respectively. The generic pair_bound uses a
conditional verifier bound only when both decodes succeed;
all malformed inputs have a bound as well.

Let A be expected file bytes, D proof file bytes, P=globalUnit
(the prior explicit degree-at-most-four polynomial), and
Q(X)=((X+1)+(X+1)+X)+(X+1)+1 = 4X+4, the prior typed decoder
selected scanner/token-read budget. Candidate inequalities:
custom: C <= Q(A)+Q(D)+P(2(A+D)+1).
DIMACS: C <= 34A+29+Q(D)+P(4A+2D+7).
The formal budget definitions use the exact existing
decodeBudget and byteCap definitions. Soundness additionally
gives UNSAT on acceptance, with independent RawMeaning for
DIMACS. These are polynomial selected-charge bounds in the
combined supplied file length, not in formula length alone.
They are not complete parser/verification instruction counts
and not bounds on required certificate size or proof discovery.

12 gated candidate declarations. Static fixture runner covers
67 custom pairs (19 expected acceptances), 73 DIMACS pairs
(22 expected acceptances), and eight hand controls, checking
verdict correspondence, budget and exact ledger decomposition
including failed decoding. Marker:
F034_END_TO_END_METER_OK custom=67 accepted=19 dimacs=73 accepted=22 hand_controls=8.
New CI pending; local Lean unavailable. Strict Lean 4.14.0
zero-axiom, warning and fixture gates unchanged. Main untouched.
Uncharged parser control/reversal work, integer bit cost,
memory/stack, allocation, compiler and IO refinement and
independent review remain open. No P vs NP resolution claim.
