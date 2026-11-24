# PNP-F005 — Verified certificate interface for optimized disjoint-block SAT

**MathOS | Specialist formal research | Classical scoped result**

## 1. Objective and boundary

PNP-F004 constructs original-row dual weights with checked universal functional identities. This milestone develops an executable checker for arbitrary returned primal or dual certificates and tests actual outputs of the optimized PNP-B006 Python solver through that checker. This is certifying-interface refinement: an accepted result satisfies the formal projected affine specification. It is not a proof of correspondence between every Python instruction and the Lean program, and it does not prove unrestricted SAT correctness.

## 2. Weighted row theorem

Given a finite original row list R and selection bits w, form weightedRow by XOR-adding each selected row; missing weights denote zero and surplus weights are ignored. Induction on the row list, using the F002 dot-product linearity identity, proves that the dot product of its coefficient list with every assignment equals the weighted XOR of the original left-side evaluations. The right-side bit equals the weighted XOR of the original right sides.

For declared dimension n, zeroCheck checks only the first n coefficient positions, padding missing positions with zeros. Induction proves its equivalence to the functional identity dot(a,x)=0 for every list x of length n. In the reverse implication a nonzero head contradicts the test assignment consisting of true followed by n-1 zeros; a zero head reduces to the tail theorem. Thus checking a single combined row's coefficients replaces exhaustive testing of all 2^n assignments.

## 3. Formal acceptance contract

dualCheck accepts exactly when the combined right side is true and the combined coefficient prefix is zero. By weightedRow and zeroCheck this is equivalent to F004's dual conditions. primalCheck accepts exactly when the returned list has length n and every original affine row holds. The unified checkOutput_sound theorem proves that an accepted witness satisfies every row, or an accepted dual certificate rules out all n-bit witnesses. generated_accepted establishes that every result of the F004 constructive reference solver passes this checker.

The proof handles arbitrary finite dimensions and row lists under the existing zero-padding/truncation semantics. The checker is executable and has no dependency on external model judgments.

## 4. Actual optimized implementation interface

The B006 Python solver uses highest-bit pivots and returns either original local pair assignments, an empty-domain witness, or an XOR certificate indexed into an augmented row list. The adapter maps mask bit j to list coordinate j (least significant first), adds singleton output equations in the same order as B006, and projects valid local witnesses to AND outputs. Its independent Python precheck verifies original block membership or XOR provenance. The translated affine results are then evaluated by the formally verified Lean checker, in bounded batches of 64. Empty-domain results are separately verified using the original Python checker. The fixed test suite covers all 16^3 local domain triples with the B006 two-row coupling, all ordered two-row systems on two unrestricted blocks, and two zero-block cases. Invalid witness and invalid dual controls must be rejected by Lean.

The theorem certifies the mathematical checker for any input; the cross-language run tests the adapter and actual B006 outputs on the supplied instances. The finite run does not prove adapter correctness for all inputs, correspondence of highest-bit versus low-bit elimination, or total Python bit complexity. In particular, the formal equivalence between the Python mask codec and list semantics and the full singleton-domain reduction still require independent proof. No specialist implementation-refinement node is declared closed.

## 5. Reproduction and status

Base: F004 commit d9035af93d52a89a3cc7bfc82f2e84901b77462a, strict prior replay 45388700252. Sources: formal/ProctorGF2.lean, ProctorGF2Solver.lean, ProctorGF2Certificate.lean and ProctorGF2Checker.lean; actual Python solver mathos/research/breakthrough_cycle6.py. Run python -m mathos.research.tga_proctor_gf2_checker --output-dir artifacts/gf2-checker with Lean 4.14.0. The workflow rechecks prior projection and solver/certificate definitions, requires empty transitive axiom dependencies for six new theorems, and records actual cross-language output, fixtures, source hashes, and negative controls. Acceptance depends on the actual report. Deterministic specialist replay only; no literature novelty, independent review, educational validation or canonical Millennium promotion. Remaining: formal bitmask and domain encoding, full program refinement, and formal total bit-cost bound.
