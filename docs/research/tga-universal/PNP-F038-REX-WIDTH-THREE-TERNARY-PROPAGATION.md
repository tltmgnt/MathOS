# F038-REX-024D5K — Bounded ternary support propagation and four-bit lowering

Parent 452032322ff2c0091e0f224374864727baae45aa. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Previous native verification

D5J exact-head [Proctor run 45943058160](https://github.com/tltmgnt/MathOS/actions/runs/45943058160), job 140321489115, completed successfully. All five original raw-selector replays, quotient/cutoff checks, independent C++ original-format replays of the binary propagation chain (425690086 transitions) and two-coordinate repair (401408188 transitions), Python original clause verifier and inherited governance passed. The radius-three SAT refusal was physically confirmed at 735673214 transitions, with blank halt.

## New physical construction

D5K extends the support projection to every binary and ternary scope, using three copied domain words and three support vectors. For a pair the third rank word is the one-symbol word 1. For each allowed tuple whose coordinates lie in the current domains, set the corresponding support bits. After scanning that scope, replace its participating domains with the support projections. Every update is a subset operation preserving all globally satisfying assignments. Empty domain is a sound contradiction. A complete unchanged sweep establishes generalized arc consistency (GAC) for all represented factors; changed sweeps do not certify a fixed point. Each sweep follows the canonical 36 binary and 84 ternary scope order.

A four-sweep cap deliberately preserves the quadratic resource envelope. The physical change flag and four budget cells stop earlier on a no-change sweep, otherwise continue to the candidate controller at the fourth sweep. This replaces D5J's unbounded binary fixed-point loop: D5K no longer guarantees even binary fixed-point completion on all inputs. A reverse-chain fixture demonstrates the cap can bind. The unchanged radius-two neighborhood has at most 46 actual candidate checks. All candidates are checked against every original mask, including after a capped propagation phase. Blank refusal is not general UNSAT. The existing direct normalized producer is unchanged.

The binary-only and bounded ternary machines are separate descriptors; neither is asserted to dominate the other on all instances.

## Compression

Replace nine individual scope-name symbols with four-bit fixed binary IDs in the scope table; read each ID in finite control. Logical alphabet is now [L,0,_,1,x], with five symbols rather than eleven. Its 13 nonphysical-blank codewords fit in four binary cells instead of five. The order makes u0/h0 and u1/h1 share the first bit, preserving the inherited physical projection marker invariant. The unchanged generic compiler, bridge and projector work at width four. The static scope table grows from 444 to 1416 cells (36*9+84*13), a storage/time tradeoff.

| metric | D5J | D5K |
|---|---:|---:|
| logical tapes |19|20|
| logical alphabet size |11|5|
| bits per encoded logical cell |5|4|
| IR instructions |4049|6940|
| original physical states |3481614|2455137|
| quotient states |2099611|1841457|
| original-format quotient bits |165869273|139950736|

D5K total states: producer 230467, bridge 279, worker 2224316, projector 74, blank halt 1. Quotient all-transition check count 7365411. Its state count lies 255695 below 2^21, so the original descriptor state-number field is again 21 bits rather than 22. This is not compression of a semantically equivalent D5J solver; the algorithms differ. Shared normalization compression remains unimplemented.

## Conditional quadratic envelope

Retain L,n,m,H,S from D5H/D5I, with S>=1936, S<=L/16 and S>=168m^3. Twenty tapes use 61 fixed logical blocks. Data capacities: stream S, scope table 1416, counter 9, domains 9m, rank words 3m, support vectors 3m, pins m, output n=19m-7. Hence N<=S+35m+1479<=2S. The five-cell propagation budget is replaced by the nine-cell counter, not added to it.

Conservative source-level macro accounting: each scope of arity r consumes at most 64m^r+512(m+1)+64 primitives (mask read, at most three support writes and rank/support advances, amortized rewinds, copying and resetting scratch words, domain writeback and ID decoding). Per sweep additional stream rewind, table rewind and skip/init overhead fit 16S. Thus the sweep ceiling 64(36m^2+84m^3)+120(512(m+1)+64)+16S<=256S. At most four sweeps cost <=1024S. Use 256S per actual candidate attempt (previous D5J per-trial 140S with slack for the larger table/ID reading/rewinds); 46 attempts cost <=11776S. The counter traversal has at most 512 increments/checks, and initial unary/pin/table setup and output emission are covered with the remaining slack. Use T<=16384S. The source-level macro ceilings are not mechanically certified.

The generic four-bit segmented compiler gives W<=(20N+12)T+6<=1048576S^2. Inherited producer P<=35000L^2, bridge I<=128S^2 and projection O<=256S^2 remain conditional premises; shorter encoding covers bridge/projector growth in scratch count. Thus t<=35000L^2+1048960S^2<=2^16 L^2 on successful supported paths. For ell=139950736 the sufficient cubic admission threshold H>=ell+16=139950752. No measured fixture is admitted at cubic stage.

If the cap were removed, at most 9(m-1)+1 nonempty GAC passes yield O(m^4) IR work, O(m^7)=O(L^(7/3)) physical work under analogous macro premises, rather than the same quadratic bound. This is a source-level asymptotic observation, not an implementation or mechanically checked full-GAC theorem.

## Executed evidence

Independent sequential bounded GAC oracle and candidate oracle matched all 68 cases (8 named, 60 seeded); 40 accepted, 28 refused; 27 empty-domain contradictions independently exhaustively verified, one known SAT radius-three refusal. Two newly supported witnesses versus D5J, zero lost witnesses in this particular sample. One reverse-chain case hit the four-sweep budget with further propagation possible. All nonempty terminal domain words matched the oracle, including capped/refused cases. All successful IR fixtures validated the original witness and exact source-level clock accounting. 10017 exact arithmetic resource checks, including large power neighbors.

New gains: ternary-three-rank m3 requires a rank originally third; ternary-chain m2 requires three unsupported values to be removed using ternary factors. Both D5J refusals became valid D5K witnesses. Physical original raw-selector replay for ternary-chain, pins [0,0]:

  t=2235614856, head=53792, span=54821,
  producer=100021617, bridge=19693963, worker=2115023998, projection=875278,
  witness=0101010101101010101111111110000.

Exact physical worker clock matched source accounting; original clause validation passed. The quotient replay matched exact clock/head/span/witness; cutoff at 2235614855 was TIMEOUT with no witness. The new CI registers five physical replays and independent native descriptor replay. Only the above D5K physical replay and quotient/cutoff were executed interactively; do not claim new CI/native completion without evidence.

Full ternary sweeps are substantially more expensive in measured worker transitions than binary-only passes; e.g. empty m2 D5K worker 1229603364 vs D5J 227037108 for pins [0,1]. Descriptor compression is not a runtime speedup. Next: confirm D5K CI/native replay, investigate sparse-mask/active-scope skipping and a selector-preserving shared normalization controller; consider a separate full-GAC subcubic branch with a proved envelope. No main or PR #248 edits.
