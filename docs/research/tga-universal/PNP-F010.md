# PNP-F010 — Machine-checked polynomial operation bounds for highest-bit elimination

**MathOS | Specialist formal research | Explicit abstract cost model**

## Exact scope
The F009 proof-carrying algorithm accepts finite in-width mask rows over GF(2). F010 implements a separately proof-carrying instrumented version of the same dense-slot algorithm. Its returned result includes original mathematical correctness and quantitative bounds. It does not assert the execution cost of Lean's compiler or CPython, or prove the instruction-level equivalence of the Python dictionary algorithm.

## Counting recurrence
For n variables, m rows, let V count insertion invocations (including the terminal zero case), C count joint coefficient/provenance XOR collisions, K count original rows processed, B count back-substitution slots visited and D count pivot evaluations. A single insertion descends at most n slots and can visit one terminal case. In each occupied collision it consumes one slot and adds one to the XOR count. Induction gives V per row <= n+1 and C per row <= n. Summing by structural recursion over input rows, including early contradiction, proves V <= m(n+1), C <= mn, K <= m. Reconstruction visits exactly n slots when called and evaluates at most n pivots, so B,D <= n. The counters are incremented inside the executable recursions, not assigned the upper bounds.

## Width and storage
Each original provenance unit is below 2^m, and XOR preserves this bound. The instrumented basis invariant preserves the bound at every insertion, including the contradiction branch. Coefficients in occupied slots are below 2^n by their highest-bit proof. At most n slots are occupied. A fixed-width basis representation with one occupancy bit per slot, n coefficient bits, one rhs bit and m provenance bits per occupied slot has payload <= n+n(n+1+m). This is logical payload storage, not peak allocation or stack space of a persistent implementation.

## Explicit abstract bit-cost model
Let L=n+m+1. Charge 4L per insertion invocation, 2L per collision, 4L per input row, 2L per reconstruction slot and 6L per pivot evaluation, plus (2n+2m+1)L for initialization and output. This model counts fixed-width scans, copying, XOR and parity at conservative linear charges; it assumes mutable fixed-width slots, preallocated storage and indexed access. The machine-checked numerical bound is

T = (4V+2C+4K+2B+6D+2n+2m+1)L
<= (4m(n+1)+2mn+6m+10n+1)L.

The displayed polynomial is O((m+1)(n+1)(m+n+1)); for square systems it is cubic. The theorem is a formal bound on the defined charge, not a verified compiler implementation of the charge model. It excludes host object overhead, allocation, proof elaboration, Python big integer internals, and original domain assembly/reading costs. Dimension n,m are explicit parameters, not logarithmic encodings of dimensions; input encoding and bit-cost refinement require separate justification.

## Validation and remaining boundary
The replay checks prior declarations plus ten new definitions/theorems, separating the earlier strict empty-axiom audit from standard library-backed results. Exact regression compares the costed Lean outputs and all five counters against a dense Python trace mirror, and the F009 fixtures use the B006 witness/certificate semantics. The finite cross-language comparison is not a universal program refinement. The output specification includes the bound on dual provenance width and mathematical validity for every finite in-width system. No unrestricted SAT result or P versus NP solution, no live AI research or independent review is asserted.

Reproduction: base a63a41efd079c73e963cac2d767340a91df40978; F009 corrected run 45393354385. Run python -m mathos.research.tga_proctor_gf2_cost --output-dir artifacts/gf2-cost using Lean 4.14.0. Actual verification results are recorded in report.json.
