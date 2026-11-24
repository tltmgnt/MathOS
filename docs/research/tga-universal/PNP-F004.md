# PNP-F004 — Constructive original-row dual certificates over GF(2)

**MathOS | Specialist formal research | 24 November 2026 | Classical scoped result**

## 1. Exact result

For every finite row list A with right-hand sides b and declared assignment dimension n, either construct an n-bit satisfying assignment or construct original-row selection weights w such that the weighted XOR of right-hand sides is one and the weighted XOR of all original left sides is zero on every n-bit assignment. The selection vector is represented as a Boolean list, interpreted with zero padding/truncation against the original row list. For ordinary rectangular systems this is precisely the dual certificate lambda^T A=0 and lambda^T b=1: evaluate the universal left-side identity on each unit coordinate vector to obtain every zero column; conversely zero columns imply the identity by linearity. The formal statement uses the universal functional identity, not an independently formalized matrix-column representation.

PNP-F003 proved total decision and a constructive witness or nonexistence proof. The new result supplies explicit original-row weights in the failure branch. Both the primal and dual result are proof-carrying values in Lean, not merely a finite search over test systems. No literature novelty or general SAT solution is asserted.

## 2. Provenance invariant

Each current row r is tagged with an original-row weight list w and a proof that, for every full assignment x, the weighted original left-side values equal dot(r.coeff,shift(x)), and the weighted original right-hand-side values equal r.rhs. Initially shift is identity and the unit weight at row i represents row i. The tag construction prepends a zero to each tail unit vector. Missing trailing weight entries denote zero.

When adding a pivot row to another row, XOR their coefficient vectors and their provenance weights. The verified F002 linearity identity gives both invariants by equality transport. If the cleared first coefficient is zero, remove it from the coefficient list and compose shift with tail. The weighted original row remains unchanged; the zero coordinate has no effect. This proves that each reduced equation retains exact provenance without assuming an unverified matrix inverse.

## 3. Recursive certificate algorithm

At dimension zero, check right-hand sides. If any is true, return its stored weight list. For every full assignment whose shifted tail has length zero, its current dot product is zero, so the tag invariant gives a left-side zero and right-side one. If every right side is false, return the empty satisfying assignment.

For dimension n+1, scan the tagged rows. In the no-pivot branch all heads are zero; strip every row and recurse. In the pivot branch clear and strip every row with the pivot and recurse. The recursive call strictly decreases n. A dual result lifts unchanged, since every shift-output of length n+1 has tail length n. A primal result lifts by the F003 free-bit or pivot back-substitution argument, with the equality of raw transformed rows checked separately.

At the root, the initialized tagged rows are exactly the original row list and shift is identity. The returned Certified type therefore provides the original system witness or the dual weights with both exact properties.

## 4. Soundness and completeness

If x satisfied every original equation, the list of evaluated left sides would equal the list of original right sides. Taking the dot product with the same weight list would force zero equal to one for a dual certificate. Hence the formal dual_sound theorem proves impossibility from the original rows and certificate alone. Conversely, if no satisfying assignment exists, the total certify function cannot return its witness branch, so dual_complete extracts the weights and their exact properties. This yields the constructive GF(2) theorem of alternatives in the declared finite dimension.

The verifier audits certify, dual_sound and dual_complete, with all earlier projection, row calculus and total-solver theorems replayed under Lean 4.14.0 and the strict empty-axiom policy. Executable controls compare primal assignment enumeration, exhaustive original-row subset enumeration, and the existing F003 Python certificate generator. Include a three-row contradiction where no pair suffices: x=1, y=1, x+y=1. The unique nonzero contradiction selection uses all three equations.

## 5. Remaining formal boundary

The new formal solver constructs explicit weights, with proof-erased output containing either assignment bits or certificate weights. Its provenance uses Boolean lists, not the optimized Python integer masks, and the matrix-column equivalence above is explained mathematically rather than a separately checked theorem. The finite Python regression does not establish a code-level refinement theorem. The specialist graph can close the certificate-generation node only on successful strict replay; implementation refinement and total bit complexity remain open. No canonical Millennium obligation is changed. Independent review and educational outcomes are not established. Deterministic specialist replay is not live AI discovery.

## Reproduction

Pinned baseline 7b055251949a449be428d641d137d79a20e0f17b; prior sources formal/ProctorGF2.lean and formal/ProctorGF2Solver.lean. New source formal/ProctorGF2Certificate.lean. Run python -m unittest discover -s tests -p 'test_tga_proctor_gf2_certificate.py' -v and python -m mathos.research.tga_proctor_gf2_certificate --output-dir artifacts/gf2-certificate with Lean 4.14.0. The replay preserves the exact concatenated source, checker diagnostics, digests, prior results and a standalone DOCX. Acceptance is based on the actual report, not this planned gate.
