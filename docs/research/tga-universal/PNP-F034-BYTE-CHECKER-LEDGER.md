# PNP-F034 — Combined selected byte checker ledger

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base ad6e7199da2f5f288fa2b5dc12ce992599aa9a34 (PR #208). Four files copied byte-identically
from verified PR #209 head 2ff41e0e5452bae6967765c5b34a30d1b6bca79c, exact preflight 45543238197/job
138966558418/artifact 14989594988, twenty zero-axiom declarations and
131 controls. Require #209 merge and exact candidate replay before PR.

Compose original Nat scanner's selected meter, unchanged binary-iterator
grammar meter, one final parse remainder test charge, and typed
boundMeter. Token length <= byte length for successful tokenization.
Per decoder selected bound tokenBudget(bytes)+64*bytes.length+4,
algebraically 67*bytes.length+6. The combined selected checker bound
is decodeBudget(a)+decodeBudget(b)+globalUnit(byteCap(a,b)), using the
existing canonical encoding size bridge for both successful decodes,
regardless of checker acceptance. Both decoders are evaluated;
checker charged only if both succeed. Result equivalence with original
byte checker and fuel-free binary decoder; inherited UNSAT soundness.
This is a mixed abstract ledger, NOT a bit-machine refinement.
Scanner charges are the original Nat scanner's abstract visit/guard/
reversal charges, NOT the checked binary scanner's primitive gates.
Typed checker charges do not bound actual Nat bit operations,
allocation, stack, encoding or full runtime. No production substitution.

Ten candidate declarations; 125 executable controls (8 expected,
12 envelope, 96 pairs, 8 malformed bytes, 1 positive UNSAT).
Marker F034_BYTE_CHECKER_LEDGER_OK expected=8 envelope=12 pairs=96 malformed=8 positive=1.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
No local Lean execution. Independent review and resolution remain open.
