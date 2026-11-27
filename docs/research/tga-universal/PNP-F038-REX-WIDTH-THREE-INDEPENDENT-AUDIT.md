# F038-REX-024D5F — Independent arithmetic audit, sharper conditional envelope and finite-format obstruction

Parent 9858fc4e420444ce2e2fb13f3c18f64c92dfb3b0. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE. Global routes 0/4, Omega obligations 0/6.

## Proctor evidence

D5E exact-head [run 45936696550](https://github.com/tltmgnt/MathOS/actions/runs/45936696550), job 140301433591, completed SUCCESS; both the explicit phase/threshold regression and governance steps passed. The parent native m4 [run 45934056192](https://github.com/tltmgnt/MathOS/actions/runs/45934056192), job 140293064394, still reports step 8 (native exact halt and cutoff) in progress when inspected. Compilation, worker regression and governance passed; no native m4 exact halt/cutoff claim. The 299944027294 clock remains the direct-phase prediction until native confirmation. No new physical machine is synthesized.

## Independent resource arithmetic

Retain the four D5E numerical phase inequalities P=2^21 L^2, I=2^16 L^2, W=2^39(b+1)^3 m^8 and O=2^20(b+1)m^5. The source-level macro counts, legitimate normalized layout, previous worker capacity/time argument, compiler simulation and physical composition remain premises.

The D5E producer accounting gives 256 L(131 L+2176)+2^40; dividing by L^2, the resulting expression is decreasing for positive L and at L=37914 is below 2^21. The bridge expression (5L+2)128L is below 2^16 L^2 for L>=1. For projection, n+1<=19m and N<=512(b+1)m^4 give

16(n+1)(5N+n+1) <= 778240(b+1)m^5 + 5776m^2 <= 2^20(b+1)m^5.

The ordered partial-path count for the nine-vertex DFS is exactly 986410 < 2^20. These numerical checks do not certify 128 charges per input bit, the 16D transition ceiling, the 1024 by 1024 DFS macro ceilings, bridge shuttles, or the worker's IR scan/capacity invariants. Those remain source-level proof obligations. The numerical inequalities do not replace an all-input physical cost proof.

## Sharpen the global simplification without changing the machine

For m>=2, n=19m-7 gives n>=31m/2, n-1>=15m, n-2>=29m/2. Thus the ternary selector block alone gives

L >= (4/3)n(n-1)(n-2) >= 4495m^3 >= 2^12 m^3.

Since log2(m)>b-1, H>=3b+10, so 3(b+1)<=H+1. Also L>=2^15 and H>=16. Normalize all four phase bounds by X=(H+1)^3 L^(8/3):

- W/X <= 2^39 * 2^(-32) / 27 = 128/27.
- P/X <= 2^21 / (2^10 * 2^12) = 1/2.
- I/X <= 1/64.
- O/X <= 1/4096, using m^5<=m^8 and b+1<=H+1.

Their sum is strictly below 8. Consequently, subject to precisely the inherited phase premises,

t(L) <= 2^3 (H+1)^3 L^(8/3).

The coefficient improves by a factor 2^37; this is tighter accounting only, not a physical speedup.

## Exact integer stage threshold

For a coefficient 2^c and fixed ell=928445994, L<=2^H yields a sufficient condition by cubing both sides of the time-budget inequality:

2^(3ell+3c) (H+1)^9 <= 2^H,

equivalently H>=3ell+3c+ceilLog2((H+1)^9). This avoids floating logarithms and materializing 2^H. For H>=16, (H+2)/(H+1)<=18/17 and (18/17)^9<2, so the ceiling-log RHS grows by at most one per integer increment and the margin never decreases. H<3ell+3c is impossible. Checking the boundary and predecessor establishes eventual validity and first satisfaction of this sufficient inequality.

For the original c=40 envelope, the first threshold is 2785338385, five lower than D5E. For c=3 it is 2785338274, 116 lower than D5E's published 2785338390. Equivalently L>2^2785338273. This is not a necessary or optimal admission threshold; it remains astronomically large.

## Exact original-format finite tradeoff

The 111 table encoding of q>=1 nonhalting states has ell(q)=4+q+3q(bit_length(q)+4), so ell(1)=20, ell(2)=42, ell(3)=61. At every recorded SAT fixture's clock, the cubic-stage descriptor allowance is already smaller than 20:

| fixture | L | cubic stage | ceilLog2(t) | allowed ell | one-state budget | two-state budget |
|---|---:|---:|---:|---:|---:|---:|
| empty m2 |37914|48|30|18|268435456|64|
| edge SAT m2 |37914|48|31|17|268435456|64|
| forced m3 |161851|54|37|17|17179869184|4096|
| forced m4 (predicted clock) |428744|57|39|18|137438953472|32768|

Thus descriptor-only reduction, even hypothetically down to one state, cannot admit the unchanged physical clocks. Three-state and larger 111 tables are not listed at any of these cubic stages. A two-state table cannot both fit and perform a full left-to-right scan of the original selector (L-1 moves from its start). This is a format-specific resource barrier, not a lower bound for every algorithm, not a claim that a one-state table can solve a fixture, and not an exclusion of other original program types or earlier universal successes. The quotient's exact arbitrary-read-symbol Mealy refinement has already exhausted that clock-preserving equivalence class; further reductions require different semantics-preserving design or exploiting reachable tape invariants.

## Host singleton shortcut

For legitimate normalized inputs, selected optional negative unary clauses delete ranks in the nine domains. If any domain empties, no normalized witness exists. If every domain is a singleton, their unique tuple is forced; validate all remaining optional clauses against it. Otherwise return FALLBACK to the existing worker. No search over m^9 tuples, planner, or bag joins are needed for the forced case, once the normalized factors have been decoded. This is a host prototype, not a compiled physical machine, and does not bypass required validation or certify width-three admission. An independent exhaustive rank oracle checked 12 synthetic cases (four each at m=2,3,4), including the prior forced m4 rank pattern, a contradictory binary clause, an empty unary domain, and a fallback; 1129356 tuples visited, no discrepancy. No end-to-end physical cost reduction has been measured.

## Executed checks and scope

The independent JS function bodies were executed in a JS runtime before repository writes: 10000 original phase-arithmetic domain checks, 196 original-envelope threshold boundary checks, 10018 stronger-envelope arithmetic domain checks (including large power neighbors), 195 stronger threshold boundary checks, four finite SAT clock tradeoffs, 12 host shortcut cases and 1129356 rank-oracle visits. All passed. The new branch's workflow is separate; its status must be confirmed independently. The source-level macro/counting premises and native m4 replay remain unresolved. Main and PR #248 are not modified by this mission.

Reproduce:
```sh
node mathos/research/f038_rex_width_three_independent_audit.js
```

Next: confirm native exact m4 replay and one-step-short cutoff; design and measure a validated singleton fast path in physical transitions, and investigate a compact algorithmic controller rather than further clock-preserving row interning. Preserve all existing gates.
