# PNP-F001 — Formal projection and lifting for disjoint AND blocks

**MathOS | Specialist research milestone | PNP-B006 correctness dependency**

## Mathematical result

Let D=(D_1,...,D_n) be an arbitrary finite list of local domains of Boolean pairs. Each block has its own two coordinates. Write g(a,b)=a AND b and E_i=g(D_i). For any output predicate C on Boolean lists, the original block system is satisfiable if and only if there exists y with y_i in E_i and C(y). This includes the affine GF(2) output equations of PNP-B006. It does not require the coupling predicate itself to be efficiently decidable.

Proof. Forward, apply g to each admissible pair. Reverse, for each projected output, membership in the image domain supplies an original pair producing that output. Induct on the domain list: the empty list lifts to the empty list; lift the tail and prepend the selected head pair. The resulting list is admissible and has the prescribed output list. Transport C along that equality. Empty local domains are automatically excluded by the membership premise. The proof handles arbitrary finite length, not a fixed number of tested blocks.

## Verified scope and library

The Lean module uses core Init List membership and map, two inductive relations for pointwise admissibility and projected admissibility, and a general predicate C. The formal theorem is ProctorPNP.projection_iff; the witness construction is ProctorPNP.lift. These exact relations encode disjoint coordinates by construction. This is a formal reconstruction of the correctness reduction already stated in PNP-B006, not literature novelty. Gaussian elimination implementation, affine encoding correspondence and total bit complexity are not verified by this theorem.

## Essential boundary

Take singleton local domains {(true,false)} and {(false,true)}. Both project to false, so the projected output (false,false) exists. If their first coordinates refer to the same input variable, the original constraints require that variable to be both true and false. The shared-variable claim is impossible. The formal negative control proves the conflict from the two pair equalities, and proves the projected list is admissible. The projection theorem cannot be extrapolated to overlapping blocks without further constraints.

## Agentic process extension

Freeze the source-aligned theorem contract and digest of the curated Lean module. The specialist controller validates the contract, evaluates the finite local image domains and negative control, attempts a deliberately insufficient strategy, then checks the curated constructive proof through the actual kernel. The planner is deterministic in the offline fixture. This is a limited verified proof strategy, not live AI discovery of arbitrary Lean code. A checked proof report retains actual axioms and source hashes; acceptance affects only a separate scoped specialist graph. All canonical Millennium obligations remain unchanged. The next specialist dependency is an exact formal GF(2) encoding and verified elimination with certificate and bit-cost proof. No unrestricted SAT or P versus NP solution is asserted.

## Reproduction

Source: docs/research/breakthrough/PNP-B006.md at baseline f9d09c67852b57c6d6f2108eaa5befbac6fab070. Run Lean 4.14.0 on formal/ProctorPNPProjection.lean. Run python -m mathos.research.tga_proctor_pnp --output-dir artifacts/pnp-formal. The CI workflow logs kernel dependencies and exact controls; its result determines status. Independent review not performed, educational validation not performed.
