# PNP-F013 — Sequential bit-cell primitives and certified output packets

**MathOS | Specialist formal research | Explicit cell-operation model**

## Objective and scope

The F012 abstract cost contract passed in run 45397087933 (4,184 cross-language cases). The next step is a local refinement into actual operations on materialized Boolean cells. This paper does not claim an entire bit-machine simulation of the solver.

## Explicit primitives

XOR consumes one cell from each of two equal-width tapes, evaluates one XOR gate and writes one output cell. The counted recursion proves equality with addVec and exactly four cell operations per coordinate. Dot product reads two cells and performs one AND and one XOR per coordinate, with a Boolean accumulator; its counted recursion proves equality with dot and exactly four operations per coordinate. The F006 natural-number mask representation connects both primitives to integer XOR and truncated AND parity. A joint tagged-row XOR acts on n coefficient bits, one rhs bit and M provenance bits, so its charge is exactly 4(n+M+1). These counts start with materialized input cells; decoding a host integer is not free in a concrete implementation.

Sequential read and write visit an explicit prefix of length i before accessing the target cell. The read returns the original target in i+1 visits; the write returns the identical prefix and suffix with the target replaced, in 2(i+1) modeled cell operations. The write models a copied prefix, not in-place allocation. These are local sequential-access primitives rather than a unit-cost random-access assumption.

## Arithmetic schedule bound

Using F010's actual collision count C and pivot evaluation count D, the local arithmetic events have charge 4C(n+M+1)+4Dn. Since C <= Mn and D <= n, the formal bound is 4Mn(n+M+1)+4n squared. This is a budget for replacing the arithmetic events, not a proved cost of the original solver's complete memory-access and control schedule. It is not a proof that F012's old charge dominates every concrete machine operation.

## Output wire contract

For a known input instance, emit one tag bit: true for SAT, false for UNSAT. SAT is followed by the two bits of each original witness pair in order; parsing is a proved inverse on serialized pair lists. UNSAT is followed by exactly M original augmented-row selection bits, least significant first. The prior codec reconstructs the exact bounded selection mask. The wire_valid theorem establishes that the emitted packet parses to an original satisfying assignment or decodes to an original augmented-row contradiction and refutation of all original witnesses. Length is at most 2n+m+1, where m is the original equation count. The explicit copy pass has exactly two operations per emitted bit and at most 2(2n+m+1) operations. This copy charge excludes construction of pairBits and the integer decoder; it is not a total serializer cost theorem. Dimensions and input instance are supplied out of band. No claim of an untrusted-input parser or network protocol.

## Evidence and boundaries

The replay checks all 90 preceding audited declarations and 13 new declarations on Lean 4.14.0, preserving the earlier strict axiom gate and standard library allowlist. Executable fixtures compare all 4,184 prior solver output packets and their copy counts, all ordered width-zero-through-four mask pairs, and all valid sequential read/write locations for those small masks. The whole solver-to-bit-machine simulation, concrete runtime/control costs, source-language Python refinement and peak allocator storage remain open. This is a classical restricted SAT result, not general SAT or a Millennium proof. No independent review or live AI discovery asserted.

Baseline f2ab1a7bbcfd56c53f74473b12ea3dd8d3c1dd72. Reproduction: python -m mathos.research.tga_proctor_bit_cells --output-dir artifacts/pnp-bit-cells. Actual report.json determines acceptance.
