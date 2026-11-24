# PNP-F008 — Highest-bit Gaussian elimination invariants

**MathOS | Specialist formal research | Classical scoped result**

## 1. Source-aligned objective

B006 solve_blocks processes each affine row in order, selects p=bit_length(mask)-1, inserts at an unused pivot or XORs the existing row with the current row and its provenance. After processing it visits pivots in increasing order, setting each pivot bit when the current parity disagrees with the right side. We formalize the local mathematical invariants of this exact strategy, not the Python dictionary and control-flow semantics.

## 2. Highest-pivot descent

Define Highest(a,p) by 2^p ≤ a < 2^(p+1). This is the mathematical characterization of a nonzero mask's highest bit. Prove the bit at p is true. If two masks have the same highest pivot, their XOR is below 2^p: bit p cancels, all higher bits are zero. Hence the new mask is strictly smaller, and its next nonzero pivot is strictly lower. These theorems justify at most n collisions in any n-bit row-reduction chain; the full loop count and bit-cost theorem are separate.

## 3. Row and provenance invariants

The F006 decode-XOR theorem identifies integer row addition with the F002 list row operation. Conditional on satisfying the retained pivot, replacement of the other row preserves satisfaction. For provenance define an invariant between each current row and its original-row selection mask: every Boolean assignment evaluates to the weighted original left side and the current right side is the weighted original right side. XORing both the row and the provenance preserves this invariant. If the current mask is zero and the right side true, the invariant yields an independently valid dual contradiction, refuting every n-bit assignment. Initialization and maintenance of an entire basis and the original source-language execution trace are not implied by this local proof.

## 4. Back substitution

For p<n the decoded unit mask 2^p has dot product with any decoded mask a equal to bit p of a. Dot-product linearity therefore shows that toggling coordinate p changes the row value by that coefficient. For a highest-pivot row the bit is true, so the operation that toggles p only when parity disagrees satisfies that row. For any row with mask below 2^p the operation leaves satisfaction unchanged. If the assignment has no bits at or above p, OR with the unit mask agrees with XOR. This supplies the local mathematical justification for the increasing-pivot reconstruction in B006. A global proof of the sorted basis traversal and freshness invariant remains to be integrated.

## 5. Evidence and boundaries

The Lean replay audits twelve new theorem statements alongside the forty previously audited results. Strict earlier axiom-free gates remain intact; the library-backed results accept only explicitly recorded propext and Quot.sound dependencies. The Python trace mirror checks pivot descent, exact original-row provenance and lower-row preservation and compares its exact output masks and row-XOR counts with the actual B006 solver on all ordered systems up to three variables and three rows, using unrestricted local domains. This is a finite implementation control, not a universal Python refinement proof. The formal results concern the affine core; the domain reduction is the earlier F006 theorem.

Remaining: formal basis initialization/insertion and global loop refinement, source-language execution correspondence, and total polynomial bit complexity. No live AI execution, independent review, literature novelty or canonical Millennium promotion is claimed.

Reproduction: baseline 90581a1d0f7125a5f12399e3fb9f709136f6d6b4; F007 workflow 45390922328. Run python -m mathos.research.tga_proctor_gf2_highest --output-dir artifacts/gf2-highest with Lean 4.14.0. Actual result and dependencies recorded in report.json.
