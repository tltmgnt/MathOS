# PNP-F012 — End-to-end polynomial abstract cost accounting

**MathOS | Specialist formal research | Restricted classical algorithm**

## Scope

F011 proves total correctness of the disjoint AND-block solver, including executable original-pair witnesses and augmented-row dual certificates. Its corrected workflow 45395547151 passed 4,181 cross-language controls. F012 adds explicit computational counters for preprocessing and witness reconstruction. This is a model of operation events, not a proof of the runtime of Python, Lean's VM, or a particular machine.

## Preprocessing

Let n be the number of domains, m the number of coupling rows and s the total number of listed allowed pairs, including duplicates. A counted scan searches the projected Boolean list for a requested bit and returns the same result as containsBit, with at most the length of the list visits. Each block maps its pairs to output bits, searches for both bits, creates at most one local equation, pads each tail row and appends its local row. The counted recursion returns exactly domainRows. Its work recurrence adds the tail work, the domain length, both search counts, two control events, the tail row count and the local row count. Since the tail row count is bounded by the number of remaining domains, induction gives work <= 3s+n(n+3). The count charges each pad/map/append event at the later fixed-width rate; it does not count host allocations.

The mask conversion visits each generated row and charges two width-n passes (fit, encode) plus one event; there are at most n such rows. Appending the original m rows charges m events. The resulting list is exactly F011's augmented list, with preprocessing count P <= 3s+n(n+3)+n(2n+1)+m. A proof of representation equality transports all existing affine theorems.

## Lifting and certificates

A counted executable pair search returns a membership and gate-output proof with at most the local domain length visits. The recursive lifting returns an actual original-variable witness and a total search count H <= s. For contradiction output H=0; no witness reconstruction is needed. The dual provenance is already an augmented-row mask and its certificate transport to original unsatisfiability is a proof, erased at runtime. Output copying is included in the abstract overhead, not a separate checker run.

## Total charge

The affine phase charge A is bounded by polynomial(n,m+n) from F010/F011. Use a declared common fixed-width charge L=n+m+s+1 for additional events. Define T=A+(P+H+4n+2m+1)L. The overhead is a chosen abstract charge for dimensions, decoding and copying the answer. The theorem proves

T <= polynomial(n,m+n)+(4s+n(n+3)+n(2n+1)+3m+4n+1)(n+m+s+1).

This is polynomial in explicit n,m,s (at most cubic in their sum plus one). The bound concerns the defined event charges. It is not a primitive bit-machine refinement, a bound on persistent-list copying or allocator use, or an independently verified worst-case complexity of CPython. A concrete implementation realizing the chosen charges requires further work. In particular, the original B006 empty-domain early return differs from the deterministic augmented-row model. No general SAT decision algorithm is claimed.

## Evidence

Replays 80 prior audited declarations and ten new declarations with Lean 4.14.0, using prior empty-axiom policy and separately reported standard library dependencies. Exact finite cross-language controls compare original pair outputs, dual masks, preprocessing counts, affine charges, lift visits and total charges with the Python model. Two extra repeated-domain controls exercise s independent of n. The report records actual verification and source hashes. The paper does not assert acceptance until the replay passes. No literature novelty, live AI discovery, independent review or canonical Millennium promotion.

Reproduction: source baseline dc893b402520e614857519c73e7415ac588e4942; run python -m mathos.research.tga_proctor_pnp_total_cost --output-dir artifacts/pnp-total-cost.