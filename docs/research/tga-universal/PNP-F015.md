# PNP-F015 — End-to-end Boolean-tape domain integration

**MathOS | Specialist formal research | Disjoint AND-block restricted domain**

## Scope

F014's merged commit a2527d3f87a29534c447aeb54b938f3a27427868 is the baseline. The F014 corrected kernel and cross-language workflow concluded successfully. F015 connects rectangular Boolean coupling rows, domain-generated rows, full-width provenance, constructive witness lifting, and the F013 output wire format without coefficient or certificate integer masks.

## Construction

Given n disjoint pair domains and r rectangular coupling rows, append at most one row per domain. A domain with no allowed pair contributes the contradiction 0 = 1; a domain allowing exactly one AND output contributes its coordinate unit row with that output as RHS; a domain allowing both outputs contributes no row. Lean uses the existing domainRows construction and fit to materialize rectangular rows. The Python mirror directly constructs equivalent explicit unit and zero rows. Row ordering is original coupling rows followed by domain rows in domain order.

Initialize full-width provenance and execute F014's coordinate-order solveTape. A satisfying output y has a constructive lift to a list of original pairs using the first allowed pair with AND output y. Serialize a true tag followed by the two bits of each pair. On contradiction, serialize a false tag followed by the full-width original augmented-row provenance tape. No natural-number mask is used in these steps. A dual wire is tied to the deterministic augmented row order. The F014 legacy mask fixture adapter is retained.

## Formal obligations

Eight new audited declarations establish rectangularity, satisfaction preservation, augmentation size, dual refutation and proof-carrying wire validity. The result type carries an affine charge bound and exact output-copy charge. The SAT result must parse to an allowed original-variable witness satisfying all coupling rows. The UNSAT result must have exactly the augmented row count in selection bits and pass the dual checker, implying that no original witness exists.

For M augmented rows, M <= r+n. F014 provides the structural affine bound

4M^2 + 6M + n[M(4(n+M+1)+6)+4n+4].

The output copy charges exactly twice the wire length. These are separate model charges, not a total preprocessing/lifting/runtime bound. Domain enumeration, fitting, witness search, pair serialization construction, input parsing, counters and allocation have not been fully charged in a finite-state model. The wire length bound is tested in Python, not claimed as a new Lean theorem.

## Replay and limitations

Use Lean 4.14.0 to audit all prior declarations and the eight new declarations. Compare exact wire tapes, affine charges and output-copy charges on 4,181 ordered fixtures (4,096 triples of finite pair-domain subsets with fixed couplings, 84 small two-row systems, and the empty instance). Verify certificates independently against original pair enumeration or weighted augmented rows; reject truncated and extended wires and non-Boolean tags. Run the F014 regression suite again after extracting its native cell entry point.

Run python -m mathos.research.tga_proctor_pnp_tape_integration --output-dir artifacts/pnp-tape-integration. Actual report.json determines acceptance. No claim of unrestricted SAT, P versus NP resolution, finite-state simulation, exact highest-bit trace refinement, Python semantics refinement, independent review, live AI discovery, or canonical promotion.
