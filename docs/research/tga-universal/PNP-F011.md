# PNP-F011 — End-to-end certified disjoint AND-block SAT

**MathOS | Specialist formal research | Restricted classical algorithm**

## Input and exact theorem

An instance is a finite list ds of local Boolean-pair domains, together with a finite list rs of affine coupling rows on the AND outputs. Each row is a nonnegative mask less than 2^n, where n is the number of domains, and a Boolean right-hand side. The original solution is a list of pairs, one from each domain, whose AND outputs satisfy every coupling equation. Disjointness is by construction; this is not general SAT.

The executable Lean solver returns original satisfying pairs, or a selection mask for an XOR contradiction of a deterministic augmented row list. Its result theorem proves the original solution valid in the SAT branch, and refutes every original solution in the UNSAT branch. The dual mask has at most as many bits as augmented rows. Unsatisfiability completeness follows by eliminating the impossible SAT case.

## Reduction and executable lifting

F006 generates local constraints: empty output domain gives 0=1; singleton output gives a unit equation; both outputs give no row. Fit each coefficient list to the declared width by zero padding or truncation. For every length-n assignment, dot product is unchanged by fitting; the F007 codec converts these lists to in-width natural-number masks. Append the generated rows to the original coupling list. The augmented-satisfaction equivalence identifies the original affine constraints and projected domain membership. Each domain contributes at most one row, so the augmented count M is at most m+n.

Run F010's costed proof-carrying highest-bit solver on the augmented masks. A SAT result gives the projected output vector. The executable pick function searches each domain for a pair with that output; its result type carries membership and output proofs. liftExec recursively constructs the entire pair list. This is a computational witness, not an extraction of data from a proof-only existential. If the solver returns UNSAT, its provenance certifies contradiction on augmented rows. Any original witness would project to a satisfying augmented vector, contradicting that certificate.

## Integrated cost contract

The returned charge is the F010 abstract affine-phase bit charge. Monotonicity of its polynomial in row count gives charge <= polynomial(n,m+n), namely (6n(m+n)+10(m+n)+10n+1)(m+2n+1). For m and n of comparable size it is cubic. The encoding creates at most n additional rows. This is not a machine-checked total primitive-operation bound including preprocessing, list allocation and pair searches; those phases and a concrete runtime cost refinement remain open. A mathematical implementation can scan local domains and build unit masks with polynomial effort in the explicit input size, but the present charge does not account for that execution. The original Python B006 solver has a separate empty-domain early return; F011 encodes that case as a contradictory augmented row. Exact certificate equality with Python is not asserted.

## Evidence and limitations

The replay audits the preceding 69 declarations and eleven new declarations with Lean 4.14.0, preserving the earlier strict empty-axiom audit and the separate allowlist for standard library-dependent proofs. Finite controls enumerate all 4096 ordered triples of local domains under the B006 coupling, all ordered two-row systems on zero through two unrestricted blocks, and an empty instance. A Python model constructs the actual expected pair witness or augmented-row contradiction and charge, checks the original B006 decisions, and compares exact output and charge against the Lean executable solver. No general SAT solution, literature novelty, live AI research, independent review, or canonical Millennium promotion is asserted.

Reproduction: baseline e30855f2674ef047064b5e85ce9e2e5e7c9c5021; successful F010 workflow 45394764867. Run python -m mathos.research.tga_proctor_pnp_end_to_end --output-dir artifacts/pnp-end-to-end. The report records actual kernel, axiom and cross-language results.
