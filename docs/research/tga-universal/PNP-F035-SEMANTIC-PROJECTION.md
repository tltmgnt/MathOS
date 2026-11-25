# F035 — Exact existential projection

PNP_RESOLUTION_STATUS = OPEN.

The projection candidate computes a CNF representation of the
disjunction of the two Shannon residuals, by taking every pair of
clauses and concatenating them. It preserves the Boolean function on
the surviving variables, eliminates the selected variable, and
preserves valid IDs. The exact clause count is the product of the
residual clause counts, before simplification.

A stronger representational barrier than syntactic cache collisions:
even parity of k visible bits has a linear-size 3-CNF encoding with
auxiliary prefix parity variables (4k+2 clauses). Existentially
eliminating those auxiliaries gives even parity. Any CNF representing
even parity on the visible bits alone must have at least 2^(k-1)
non-tautological clauses. A falsifying assignment of a non-tautological
clause fixes the bits mentioned by that clause; if any bit is absent,
flipping it changes parity without changing falsification. Thus each
non-tautological clause in an exact representation can exclude at
most one odd assignment. There are 2^(k-1) odd assignments.
The candidate parity_pattern_unique formalizes the singleton
falsification-pattern lemma; the full parity CNF lower bound is
a mathematical argument here, not yet an audited Lean theorem.

The Python stress test resolves the prefix parity auxiliaries in
order, deduplicates and removes tautologies, and checks exact odd
assignment exclusion for k=1..12. This is a representation lower
bound for auxiliary-free CNF projection, not for SAT decision,
arbitrary circuit representations, or all elimination orders.
Keeping the auxiliary XOR representation or solving parity directly
avoids this blow-up. A universal polynomial exact representation
with efficient operations remains unproved.

16 public theorem candidates; 12288 projection cases and 98304
pointwise assignment checks on 4096 formulas. Strict replay required.
