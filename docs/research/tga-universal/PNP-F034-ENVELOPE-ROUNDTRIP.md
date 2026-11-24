# PNP-F034 — Proof-envelope token roundtrip and scanner converse

PNP_RESOLUTION_STATUS = OPEN. PR #169 merged at
daab64c66ee17258fc7b0066d15d8315f39aa4bd. Original CI run
45486235088 job 138772257233 failed the strict axiom gate:
'ProctorWireRoundtrip.items_roundtrip' depends on axioms: [propext]
strict axiom check failed: ProctorWireRoundtrip.items_roundtrip
Process completed with exit code 1.
Nine declarations transitively depended on propext. Repository
correction b9aec40caa04f81dd76fa65e5c2ab3f43413e68c replaced
library list identities with constructive local proofs. Final run
45487122441 job 138775363503 confirmed all 13 new declarations
zero axioms, 53 expected token fixtures, the prior 67 data-pair
fixtures and static CLI accept/reject controls. Artifact 14964697591.
https://github.com/tltmgnt/MathOS/actions/runs/45486235088/job/138772257233
https://github.com/tltmgnt/MathOS/actions/runs/45487122441/job/138775363503

## New candidate theorems

ProctorEnvelopeRoundtrip defines independent token encoders for
annotated references, groups, capacity certificates, sparse XOR
blocks, paired steps and batches, all terminal variants, proof
scope, and complete envelopes. Fits predicates express recursive
list count bounds; they do not assert semantic certificate validity.
Suffix-preserving roundtrip lemmas compose these encoders with the
existing parser. The byte roundtrip requires a Wire grammar witness
for the encoded tokens and a byte-limit premise; it does not prove
a decimal-printer algorithm.

ScanWitness is a partial-word invariant. On successful scanning
the input either ends at an empty token boundary or completes a
canonical decimal Word followed by a Wire suffix. The output equals
the reversed accumulator plus those tokens. The candidate converse
proves that accepted tokenization has a canonical grammar witness
and satisfies the byte bound. Combined with the prior constructive
grammar-to-tokenizer theorem this gives wire_iff. This concerns
lexical decimal grammar only, not the converse for every typed
count-prefixed parser. No claim of universal encoder completeness
for all arbitrary byte streams or uniqueness of decimal spelling
is made.

Thirteen candidate declarations enter strict zero-axiom checking.
The static test reopens all 53 prior syntactically representable
proof files, including semantically invalid certificates, and
compares their token lists with the independent envelope encoder.
Required marker F034_ENVELOPE_ROUNDTRIP_OK envelopes=53.
No generated Lean terms are needed for this test. Existing CI,
loader, and verifier remain unchanged. The new tests await CI;
no local Lean available.

Next: a strictly specified DIMACS input subset with explicit
conversion to expected data, adversarial input controls, and
formal correspondence to that subset. External parser/IO/compiler
refinement, full typed-parser converse, decimal printer proof,
machine-cost analysis and independent review remain open. No
original scratch port, unrestricted SAT result, or main change.
