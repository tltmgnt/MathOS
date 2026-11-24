# PNP-F012 — Integrated polynomial cost accounting for certified disjoint-block SAT

**MathOS | Specialist formal research | Explicit abstract cost model**

## Input and scope

The F011 solver was verified in workflow 45395547151, including 4,181 cross-language cases. An input consists of n independent Boolean-pair domains, m affine mask equations of width n, and q total pair entries in the domains. Duplicates are permitted in the formal list representation. F012 implements a new proof-carrying version of the F011 algorithm that counts domain preprocessing and original witness lifting, in addition to F010's affine-phase charge. The result is a valid original pair assignment or an augmented-row contradiction certificate. This is not unrestricted SAT.

## Measured structural events

The executable containsCount returns Boolean membership and the actual visited list length, bounded by the input list length. buildLocal maps AND over a domain and performs two membership searches. It charges one visit for each mapped pair and each comparison. Its output equals the original localRows and the scan count is at most three times the domain length. buildDomains combines local rows with recursively padded tail rows. Every padding event accounts for one shifted row; the tail has at most its number of domains in rows. Induction bounds total pair scan visits S by 3q, padding events P by n squared, and generated rows G by n. Each row converted to a mask uses n fit positions and n encode positions. Appending the original affine rows is charged by m. The counted witness search returns a member pair matching the projected output, counting every visited pair. Across the disjoint domains Lifting visits H are at most q. The UNSAT branch makes no lifting calls.

## Integrated proof and cost contract

The counted domain builder is provably equal to domainRows, so its augmented masks are exactly the F011 augmented rows in deterministic order. Their count is at most m+n. The costed affine solver constructs a proof-carrying result; the SAT branch lifts to original pairs by the counted search, and the UNSAT branch retains bounded original augmented-row provenance. Proof fields are erased at execution. No certificate rechecking is required to transport the logical refutation; its returned mask is charged as an output payload, not as a separate independently executed verifier.

Let W=n+m+q+1 and let A denote the F010 abstract elimination charge on the actual augmented system. Define total abstract charge

T = A + (8S+4P+(4n+4)G+8H+8n+4m+4)W.

The extra charges are an explicit model of structural list visits and fixed-width payload operations. The fixed conversion and input/output terms account for fitting/encoding, headers, original row assembly, decoding and serializing the returned payload; these are analytical charges, not counters for each host instruction. Substitution of the verified event bounds yields

T <= polynomial(n,m+n) + (32q+8n*n+12n+4m+4)(n+m+q+1).

The bound is polynomial (at most cubic in n+m+q+1). It is a formal bound for the specified charge function. It does not establish exact bit-level execution costs of the Lean runtime or CPython, peak allocated storage, or a simulation of the model by a Turing machine. In particular, list allocation and object overhead are not measured. The original Python dictionary algorithm and its early empty-domain return are not claimed to be universally execution-equivalent to the Lean solver.

## Evidence and reproduction

Replay all 80 preceding audited declarations and ten new ones under Lean 4.14.0, retaining the earlier strict empty-axiom gate and the separate allowed standard library dependencies. Compare full original witness/certificate and all six reported count/charge values against the Python mirror for the 4,181 prior fixtures and three additional duplicate-domain controls. These are finite controls, not a proof of source-language refinement. The report records actual verification status. No literature novelty, independent review, live AI execution or canonical Millennium promotion is claimed.

Baseline dc893b402520e614857519c73e7415ac588e4942; run python -m mathos.research.tga_proctor_pnp_full_cost --output-dir artifacts/pnp-full-cost. See report.json and cross-language.txt. Remaining work: concrete bit-machine refinement, full Python source-language correspondence, and independent review.
