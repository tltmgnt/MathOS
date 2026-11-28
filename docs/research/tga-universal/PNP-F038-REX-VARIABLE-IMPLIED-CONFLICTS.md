# F038-REX-024D7I — Certified implication-path conflict recovery

Parent: D7H 75f4612f92e1a8239f8f8485594eaa0984a85281. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

For every original binary forbidden row, the clause (a or b) implies edges not a -> b and not b -> a. If a source path runs from literal x to not y, every original model satisfies (not x or not y), by induction along the path. The independent checker validates each edge against the forbidden row of its cited original factor, path continuity, distinct coordinates for each edge, literal bounds, and endpoint. No reachability routine or producer clause extractor is trusted by that checker.

The producer selects boundary coordinates occurring in both a binary and a nonbinary factor. It runs BFS from each of their signed literals and emits each reachable pairwise exclusion between distinct coordinates once, with a simple source path. It retains all original nonbinary factors, drops original binary factors, and adds only the path-certified exclusions. Every original model is a model of this relaxation (not necessarily conversely). Run D7H on that relaxed instance; independently reconstruct the relaxation from original nonbinary factor indices and source paths and check the D7H proof. A verified Hall contradiction transfers to the original. UNKNOWN invokes the unchanged D7H fallback on the original, preserving its witness convention. No SAT result is inferred from the relaxation.

For k coordinates and e binary implication edges, at most 2k BFS runs cost O(k(k+e)), candidate pair tests O(k^2), and explicit path serialization O(k^3) worst case. The work budget counts visits to graph edges, pair tests and path steps, not extraction, D7H search, verification or physical runtime. A budget cutoff returns UNKNOWN without relying on partial results. The graph and path storage are polynomial; D7H's documented polynomial structural search bounds apply to the derived formula. General SAT fallback and end-to-end physical accounting remain outside the bound. The boundary policy is incomplete (for example, pure binary formulas with no nonbinary boundary).

## Executed finite audit

The committed audit was loaded from the repository and executed in a JavaScript runtime with a small assert-compatible harness. Results:
- 256 deterministic small-instance exhaustive comparisons, 472 original models preserved in the reconstructed relaxation, 104 certified refutations, zero observed false refutations.
- Five corrupted path certificates rejected; zero-budget cutoff preserved UNKNOWN.
- Three split-exclusion pigeonhole fixtures, all independently checked.

|holes|coordinates|factors|certified paths|charged work|
|---:|---:|---:|---:|---:|
|3|30|40|18|384|
|6|189|280|126|4242|
|8|405|630|288|12024|

The D7H 189-coordinate raw obstruction is refuted by seven groups and six holes. This is a scoped result, not a general polynomial SAT claim. A dedicated Proctor is configured; remote execution and full inherited/physical replay are not asserted. Main and PR #248 are not modified by this branch.

## Next gates
- Actual predecessor residual and physical replay tests, wider signed and noisy path families, and independent review.
- Mechanized proof-to-checker correspondence, complexity and physical accounting.
- Explore boundary discovery without assuming all option coordinates occur in nonbinary factors.
