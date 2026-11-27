# F038-REX-024D6C — Direct conflict-row extension and first-factor functional certificates

Parent 749a4747436947e4f98f859d593e08be2a9d7ba0. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Verification checkpoints

D6B exact-head [Proctor 46017461932](https://github.com/tltmgnt/MathOS/actions/runs/46017461932): all fifteen jobs passed, including the previously outstanding two-root physical executions. D6C executable checkpoint 6215456fbcb047cb4dff5646e9f2422bf8023c8d [Proctor 46022026974](https://github.com/tltmgnt/MathOS/actions/runs/46022026974): all fifteen jobs passed (audit/governance, twelve physical replays and two independent native descriptor jobs). This documentation commit does not alter the executable checkpoint; do not assume its own exact-head CI has finished.

## Physical direct extension

Retain D6B prefix-ordered producer, 20-tape worker, GAC and complete candidate validation. When selected row is forbidden, Q points immediately after the literal forbidden token; D identifies the current scope, whose last coordinate is g. Reset selected suffix domains after g. In domain g restore the current x to 1 and advance to the next rank. For this fixed earlier-coordinate tuple, the remaining rows of the factor's last-coordinate slice are consecutive in Q. Scan the remaining slice synchronously with the domain: forbidden literals advance without selecting; allowed literals or virtual allowed rows of a four-zero run select the first rank whose surviving domain bit is 1. Domain zero is never selected. At the domain blank, stop scanning even if the run crosses the slice boundary. If none qualifies, reset domain g to its first surviving value and carry to the previous coordinate. Restart complete candidate validation after either extension or carry. The physical machine does not require a host certificate, functional lookup table, or external rank hint. It is a sequential row-slice scan, not constant-time indexed functional evaluation.

Soundness on genuine canonical streams: a failed factor depends only on coordinates through g. All suffixes of the current prefix fail. Every skipped last-coordinate rank is either absent from the surviving domain or has a forbidden row in this same factor with earlier scope coordinates unchanged. Each of those prefixes therefore has no satisfying extension. Resetting the suffix and choosing the first surviving allowed rank, or carrying when none exists, preserves lexicographic search coverage. With sound GAC and the inherited exact validation, the machine retains restricted-family SAT/UNSAT completeness and returns the lexicographically first witness. No all-input mechanized proof of producer/lowering or arbitrary malformed-stream theorem is claimed.

## Stronger structural certificate and candidate bound

This certificate is intentionally stronger than D6B's existence of any functional factor: for each coordinate j, its first active higher-arity factor in prefix order must be functional in j (at most one allowed rank for each earlier tuple), or its unary domain must have at most one allowed rank. Other coordinates are roots; let r count them. The certificate is checked by a separate host audit of actual relations, not a runtime admission mechanism. A later functional factor alone does not qualify, because an earlier nonfunctional failure may block the direct jump.

Let P_j be the number of consistent prefixes of length j (all factors whose maximum index is less than j hold). By functional uniqueness, P_j <= m^(number of roots among the first j coordinates). Each failed complete candidate is charged to its first inconsistent prefix, at depth j+1, with preceding consistent prefix fixed; there is at most one successful complete candidate. For a root coordinate there are at most m failures for each such preceding prefix, hence at most m^r failures at that coordinate. For a determined coordinate with a functional first factor, at most two failures of the first factor can occur for each fixed consistent preceding prefix: before its unique allowed rank, direct extension jumps to that rank (or exhausts); after that rank, direct extension exhausts the slice. A failure of a later factor can occur only at the unique first-factor-compatible rank and at most once with the same preceding prefix. If no rank is allowed or survives GAC, the first failure exhausts the slice. For singleton unary domains, at most one failure is possible. Strict lexicographic increase ensures these charges cannot repeat. Thus at most three failures per determined coordinate per consistent preceding prefix, and

    C <= min(m^9, 1 + 27 m^r).

This is a source-level counting proof for the certificate class. It counts complete candidate attempts, not row scans. The machine may still scan O(m) ranks on a conflict, which is covered by the inherited conservative per-attempt macro allowance. Without the stronger certificate, retain C<=m^9; no general improvement in the worst-case exponent is claimed. Zero roots are included in the at-most-one-root resource class.

The 18 certificate fixtures span m=2,3,4 and one/two/three roots, SAT and UNSAT. Three-root family: three independent equality triples (j,j+3,j+6) for j=0,1,2, with binary equalities from j to each of the other two and ternary exclusion of equal diagonals except rank m-1; UNSAT variant forbids the last diagonal in the third triple too. All local domains remain full under GAC since every value has off-diagonal support in each ternary factor and equal support in each binary factor. Each SAT instance has exactly one rank assignment; each UNSAT instance has none. This is a decomposition-friendly test class, not an implementation of component decomposition.

## Conditional resources

Retain S<=L/16, L>=4096m^3, N<=S+35m+1479<=2S, inherited producer 4P+32L, bridge 128S^2 and projector 256S^2. The new slice scan takes O(m) primitives (one forward domain scan, paired token traversal, finite-control virtual rows, reset and carry), within the enlarged conservative per-attempt allowance 131072 S, conditional on inherited macro estimates. With C the certificate ceiling and T<=131072 S(C+(full?m:1)), W<=(20N+12)T+6. For r>=1, C+m<=29m^r and (20N+12)<=41S; the worker contribution is <=41*131072*29 S^2 m^r+6, leaving slack within total<=2^21 m^r L^2 after inherited allowances. For arbitrary fixed-nine use C=m^9, total<=2^21 m^9 L^2. Arithmetic checks cover m=2..10000 and very large BigInt boundaries, both modes, four envelopes (1,2,3,9 roots), 80136 evaluations. This verifies arithmetic, not the macro premises.

| class | D6C conditional total bound |
|---|---|
| at most one certified root | 131072 L^(7/3) |
| at most two certified roots | 8192 L^(8/3) |
| at most three certified roots | 512 L^3 |
| arbitrary normalized nine-group input | O(L^5) |

D6B's two-root conditional cubic class had a weaker certificate; the new three-root cubic class is not an unconditional superset of it. No actual cubic admission, unrestricted reduction, or general P versus NP resolution.

## Audits and performance

385 fixtures, 770 logical mode executions, 666 valid SAT witnesses and 104 correct UNSAT refusals. Independent relation-based direct-extension oracle matches all 7200 candidate vectors and 6534 failed scopes. Independent exact host search agrees with all outputs. Across the suite 5650004 candidate positions skipped (including both modes), 3104 direct leaps beyond the old immediate successor of the failed prefix. Compared to D6B, 106 mode executions use fewer complete candidates, none use more; among 666 paired successful worker clock comparisons, 86 improve, 382 tie, 198 regress. The initial three-root fixtures were too easy due to GAC deleting ranks, so replaced with the GAC-stable independent equality triples and reran the complete audit.

| fixture (alternating pins) | m | D6B trials | D6C trials | D6B worker clock | D6C worker clock |
|---|---:|---:|---:|---:|---:|
| cert-1 SAT |4|100|52|3965588240|2301453506|
| cert-2 SAT |4|347|179|21836978940|12218903080|
| cert-3 SAT |4|892|478|24216433876|13935099340|
| cert-3 SAT |2|46|46|1144677682|1149574474|
| third-rank-barrier |3|15|11|931914070|754593052|

These are exact worker source-accounted clocks, not complete physical replays of m4 examples. D6C is not uniformly faster: binary-domain conflicts often pay scanning overhead without skipping additional ranks. D6B remains a valid baseline.

## Physical and independent native evidence

Original raw selectors, zero pins. The bounded m3 one-root SAT original/quotient/cutoff were directly executed; full original also directly executed, with full quotient/cutoff confirmed by CI. Both modes of one-root m2 UNSAT original/quotient/cutoff directly executed. The executable checkpoint's CI confirms both modes and all twelve physical matrix jobs; bounded native includes SAT and UNSAT exact ledgers, full native includes the pinned UNSAT ledger (the full SAT ledger was not pinned in its native fixture generation). Full-mode logs independently confirm the following physical clocks:

| fixture | transitions | halt head | span | result |
|---|---:|---:|---:|---|
| cert-1-m3-sat |1595479077|170613|172882|SAT |
| cert-1-unsat m2 |633731654|38293|46646|UNSAT |
| cert-2-sat m2 |1025603114|46176|47006|SAT |
| cert-3-sat m2 |1185123308|46006|46819|SAT |
| cert-3-unsat m2 |1178755230|38297|46664|UNSAT |

m3 SAT ranks all 2, witness 00100100100100100100100100101010101010101010100000; worker 1270611344 transitions, 127800 primitives, N=2068. Original and quotient clocks match; cutoff 1595479076 TIMEOUT without witness. m2 UNSAT blank halt at 633731654, cutoff 633731653 TIMEOUT without witness. Other table entries are from full-mode CI logs, not newly repeated interactive runs.

## Descriptor

| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |7860|2746530|2010186|152774140|8239590|
| full |7859|2744250|2008463|152643192|8232750|

Producer 287874, bridge 279, projector 74, blank halt 1; worker 2458302/2456022. Four-bit segmented lowering and 20 tapes. Both quotients remain below 2^21; descriptor grew compared to D6B. Online sparse deposition remains outstanding.

Next D6D: implement independent component decomposition (start with host reference and a physical component-specific controller), verify component-wise witness reconstruction and attempt max-component rather than total-root bounds. Investigate actual certified admission and mechanically discharge macro allowances; no unrestricted promotion. Main and PR #248 unchanged.
