# F038-REX-024D5F — Static producer macro resource certificates

Parent 9858fc4e420444ce2e2fb13f3c18f64c92dfb3b0. Research branch only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## Verification boundary

[Exact-parent Proctor run 45936696550](https://github.com/tltmgnt/MathOS/actions/runs/45936696550), job 140301433591, completed successfully, including all five phase-envelope regressions and governance gates. The separate [native m4 run 45934056192](https://github.com/tltmgnt/MathOS/actions/runs/45934056192) still had its native domain-four step in progress when checked. No completed native m4 execution claimed. The D5E eventual threshold is unchanged and conditional on the earlier source-level resource premises.

## Static certificate construction

The previous source-level proof charged at most 16D transitions to each producer scan/deposit/query/shift macro, conditional on its visited span D<=16L, and at most 128 macro/control charges per selector bit. This audit independently checks a large portion of those ceilings on the actual finite transition graph.

Instrument only the compiler, not the machine or raw input. Wrap scan, groupRead, groupSet, classify, shift, deposit, queryBlock, emit, blanks, streamEnd and back helper calls with unique macro-owner IDs. Definitions generated lazily while evaluating a transition inherit the owning macro ID; nested helper construction inherits the active outer ID. Each original graph-reachable state carries its definition's owner. Compile both original and annotated source and require byte-for-byte equality of their entire original-format descriptors before auditing packed rows. The production compiler and descriptor remain unchanged. An owner region is a set of finite control states, not a claim of runtime call-stack structure; a visit is any consecutive path within that region. Leaving and reentering counts as a new visit.

For each nonempty owner region, form the internal directed graph with an edge for each read-symbol transition and displacement d in {-1,0,1}. Compute strongly connected components (SCCs). For each cyclic SCC, find a sign sigma in {-1,+1} and integer potential phi satisfying, on every internal edge u->v,

    1 <= 4*sigma*d + phi(v)-phi(u).

Construct phi by longest-path relaxation with edge weight 1-4*sigma*d. Reject a sign if relaxation still improves after |SCC| passes. Then independently verify every potential inequality. A nonpositive drift cycle cannot satisfy this inequality in its chosen direction; summing around a cycle gives a strictly positive signed total displacement. All-symbol edges are included, even those not realizable for a particular tape.

For a path restricted to the SCC, telescope to get a bound 4(D-1)+range(phi) on transitions when its head positions lie in an interval of D cells. Acyclic components charge one exit step. Sum component bounds along the acyclic condensation graph. This first conservative calculation yields a coefficient as high as 1344, because counted delimiter scans may span many components.

Improve the certificate by assigning directions to acyclic components and lifting local potentials across same-direction condensation edges in topological order. Recheck every lifted inequality. A maximal same-direction path run now telescopes across component boundaries; the number of direction changes is bounded by a longest-path calculation on the condensation DAG. Charge each crossing and final exit separately. If r is the maximum number of directional runs and R the maximum same-sign potential range, this yields a second valid affine envelope 4rD+r(R+1). Combine the smaller coefficient and larger intercept of the two valid affine envelopes. The resulting global bound on a consecutive visit to any tagged region is 12D+503, hence <=16D for D>=126. This validates the earlier macro allowance for those regions under the already stated span premise.

## Executed all-symbol checks

| Quantity | Result |
|---|---:|
| Producer nonhalting states |577884|
| Tagged states |439429|
| Untagged states |138455|
| Nonempty owner regions |2354|
| Tagged transition entries inspected |1318287|
| Internal edges |1296436|
| Cyclic SCCs |294400|
| Local and lifted potential inequalities checked |2034648|

| Macro family | Regions | Max coefficient | Max intercept |
|---|---:|---:|---:|
| Shift |118|8|12|
| Workspace scan |76|12|84|
| Group read |33|8|34|
| Group set |2|4|17|
| Classify |3|4|17|
| Deposit |548|8|503|
| Query block |324|8|77|
| Emit |74|8|87|
| Stream end |392|8|27|
| Count blanks |783|4|169|
| Return scan |1|4|1|

Coefficients/intercepts are independently maximized across regions. A synthetic three-state cycle with moves +1,-1,-1 passes; a stationary self-loop and a zero-net-displacement two-state cycle both reject. These controls establish that mere SCC enumeration is not treated as a drift proof.

## Selector scanner cut graph

Collapse each tagged macro to one graph node; retain each untagged state as a separate node. Use the union of all outgoing edges of each owner (an overapproximation, not a new executable machine). Stop at SUCCESS, BROKEN or cleanup entry; treat actual named raw-read states (header hRaw, bits Raw, covered Raw, pin Raw, doneRaw) as cuts. From state zero, 2094 collapsed nodes are graph-reachable, with 240 distinct raw cut states. Verify no cycle remains between cuts; longest path charges one per visited macro or singleton state. Startup before the first raw cut is at most 24 visits. The maximum from a raw cut through the next cut/exit is 31 visits including the first cut. The dynamic program checks 1851 noncut/nonexit reachable nodes. An initial failure detected the standalone setupReturn scan, which was untagged; tagging the back helper then certified it without modifying the machine.

Thus the original 128 macro/control allowance per consumed input bit has ample static slack. The semantic invariant that successive raw cuts on a legitimate admitted path correspond to distinct consumed input bits, and the overall D=16L span premise, still require the earlier layout/selector proof; this checker does not prove those facts. The planner, loader outer-loop operation counts, bridge, projector, and all virtual worker resource arguments are not mechanically certified by this audit. In particular, the 138455 untagged producer states are not covered by the signed displacement certificate; some are included as singleton scanner nodes. No whole-machine certification or descriptor reduction is claimed. The fixed quotient remains 928445994 bits; eventual threshold and finite-stage gates are unchanged.

## Reproduction

Executed in JS V8, no observed disagreement. New exact-head CI remains unconfirmed at commit.

```sh
node --max-old-space-size=6144 mathos/research/f038_rex_width_three_macro_certificate.js
python -m mathos.research.tga_f038_rex_024d5f
```

Next D5G: extend the static certificates to loader outer-loop cuts, bridge and projector shuttles; formalize span/consumption invariants and examine a genuinely smaller descriptor architecture. Confirm the native m4 run when its exact-head result is available. Main and PR #248 unchanged; all four global routes and six Omega obligations remain open.
