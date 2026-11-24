# PNP-F006 — Formal natural-number bitmask transport and local domain encoding

**MathOS | Specialist formal research | Classical scoped reduction**

## 1. Bitmask semantics

Define decodeAt(n,a,k) as the list of n Boolean bits of natural-number mask a beginning at position k, least significant first. The exact width is fixed by recursion on n. The formal statements relate Lean natural-number XOR, AND and right shift to the list calculus from F002. Pointwise XOR agrees with addVec on decoded lists; the dot product of two decoded lists agrees with the XOR-fold of the bitwise AND; shifting right by s agrees with starting decoding at offset s+k. The maskSat_iff theorem connects the exact same row equation under these two representations.

These results use core natural-number bitwise lemmas with explicit congruence and induction. The initial replay 45390051574 exposed an incomplete Boolean membership proof and reported propext and Quot.sound for the core bitwise lemmas. The corrected workflow separates the strict empty-axiom gate for the prior results and domain reduction from the library-backed mask check, which requires a successful compilation and only the recorded standard Lean dependencies (propext and Quot.sound, or none). The mask proofs are not classified as axiom-free when these dependencies occur. This scoped reporting decision does not relax prior acceptance gates. The parity fold equals popcount modulo two by elementary counting of set bits, but that specific count-parity identity and a complete encode/decode inverse are not separately formalized here. The Python integer runtime and highest-bit pivot implementation are not certified by these identities.

## 2. Local Boolean domain encoding

Let D be a finite list of allowed pairs and E its AND-output image. Define f and t as membership of false and true in E. Four cases exhaust the possibilities: neither is permitted (add the contradictory equation 0=1); only false is permitted (add the unit equation y=0); only true is permitted (add y=1); both are permitted (add no equation). Prove equivalence between satisfying these rows and membership in E, using explicit Boolean membership and cases. The contradictory-row convention differs from the optimized Python early empty-block return but has the same satisfiability semantics.

For a domain list ds, recursively append the first local constraints to the tail constraints padded with a zero coefficient. This shifts every tail equation to its correct coordinate. Induction proves AllSat(domainRows ds,ys) iff Projected(ds,ys) for every assignment of length ds.length. The proof covers empty domains, empty lists, duplicates and arbitrary finite lists of pairs.

## 3. Full scoped reduction and certificate transport

Append these domain equations after the original affine coupling rows rs. F001's disjoint-coordinate projection/lifting theorem, together with the domain equivalence, proves:

there exists a list of allowed original pairs satisfying rs on their AND outputs iff there exists a Boolean list ys of length ds.length satisfying rs ++ domainRows ds.

Using the F005 verified dual checker on the augmented equations therefore certifies impossibility of any original pair witness. This is the theorem encoded_unsat. A projected satisfying assignment lifts by F001. For nonempty domains the generated unit constraints coincide mathematically with the singleton equations in B006; the empty-domain branch is represented by a contradiction. No general overlapping-block SAT reduction is claimed.

## 4. Regression and verification

Exact Python controls compare every projected output set and the corresponding augmented affine solution set for all 16^3 local domain triples under the B006 two-row coupling, and compare actual B006 decisions with the set result. Bitmask controls enumerate all ordered mask pairs at widths zero through six and verify XOR, AND parity and coordinate shift against explicit lists. The Lean replay concatenates the exact prior source files with the new extension and audits the seven selected new results as well as all prior audited results.

## 5. Scope and reproducibility

Pinned baseline 1954faf0a196539f79ea209ef19f41d8a7369448 (F005 workflow 45389387556). Run python -m mathos.research.tga_proctor_pnp_encoding --output-dir artifacts/pnp-encoding using Lean 4.14.0. The report includes actual acceptance, axiom dependencies, source hashes and finite controls. The remaining implementation-refinement work includes a complete bitmask codec, popcount correspondence and formal semantics of the Python program; formal total bit complexity also remains open. Deterministic specialist replay, no literature novelty, live AI run, independent review or canonical Millennium promotion. No solution of P versus NP.
