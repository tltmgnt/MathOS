# F038-REX-024D5I — Bounded repair and direct normalized mask producer

Parent b534e74407d8cbb91312a7a7b53a424fe03e960e. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE. No global or Omega obligation closure.

## Parent native verification

D5H exact-head Proctor [45940110751](https://github.com/tltmgnt/MathOS/actions/runs/45940110751), job 140312235407, completed successfully. Independent C++ decoded 1640760 states / 124697764 descriptor bits; verified exact physical halt, output and cutoff for empty, partial and satisfiable conflict refusal. Python original clause verifier and governance passed.

## New machine

The first trial chooses the first allowed unary rank in all nine groups. If a selected binary/ternary mask row forbids the candidate, shift a single marker in a ten-bit attempt word, rewind the mask stream, rebuild nine one-hot rank words and test the next candidate. Trial g+1 uses the second allowed unary rank only in group g, first allowed in all other groups. Missing second rank skips that trial; empty unary domain refuses. No output is produced until all masks pass. At most ten attempts, with no host decisions. This is a bounded neighborhood search, not arc consistency or general propagation. A SAT instance requiring two simultaneous changes or a third allowed rank can still refuse.

The new producer keeps the inherited normalized selector validation, optional negative mask deposit and pin extraction. It omits graph-edge flag updates, width-three DFS and unused 851-cell planner header, and loads the canonical stream immediately right of the validated root separator. This is a deliberate change of admission family: a partial witness machine does not need an elimination order to verify a candidate. The old width-three planner is retained as unreachable source, not emitted into the reachable descriptor. Do not substitute the new producer for the general forest solver, which needs the planner metadata. The 17-tape worker and direct bridge are composed with original ternary transition rows. All acceptance claims are witness claims; refusal never means general UNSAT.

## Conditional resource bound

Retain D5H notation: L selector length, H=ceil log2 L, S=2(b+m+9m+36m^2+84m^3+131), S>=1936 and S<=L/16. N<=S+32m+499<=2S (three fixed logical blocks and ten attempt bits beyond D5H). Use D5H's source-level 128S primitive accounting for one full candidate pass. On every additional attempt, rewinding Q costs at most 2S+2, clearing all group words at most 9(7m+9), resetting A and dispatching at most a fixed 100 primitives, plus repeat of bound/pin field skipping and table rewind; these fit an additional 12S per attempt (table rewind already included in the single-pass accounting). Thus T<=1400S for successful paths, including partial scans and skipped trials. This uses inherited macro accounting, not a mechanically checked proof. The compiler bound gives W<=(26N+16)T+8<=131072 S^2. Bridge and projector bounds remain 128S^2 and 256S^2: added fifteen encoded prefix bits are covered by the prior slack, and no planner frames are traversed. Producer bound P<=35000L^2 is conditional on the inherited normalization/deposit/loader macro ceilings applying to arbitrary normalized scopes, now without graph maintenance or planner; no new mechanized proof is claimed. The aggregate is <=(35000+(128+131072+256)/256)L^2 <=2^16 L^2. This retains a sufficient cubic admission threshold H>=ell+16, namely 122349684, still astronomical and not a practical finite-stage result.

## Measured results

Compiled 2640 IR instructions, 2404901 physical states (producer 230467, bridge 297, worker 2174010, projection 126, blank halt 1), quotient 1609864 states and 122349668 bits, 7214703 exact transition homomorphism checks. Producer state count reduced from 577884 by 347417; whole descriptor smaller than adaptive D5H despite repair.

| case | clock | head | span | result |
|---|---:|---:|---:|---|
| empty m2 |288362787|52347|53376|valid |
| D5H SAT conflict m2 |292851589|52347|53376|valid repaired |
| K5 safe m2 |288362787|52347|53376|valid outside width-three graph family |
| K5 previous refusal m2 |191269332|39851|53184|blank refusal |
| m3 forced |2142202580|197888|200703|valid |

All five rows physically replayed using the compiled table; repaired row also checked exact quotient replay and one-step-short cutoff interactively. The m4 repair machine and full native verification are configured in the new workflow, not claimed complete. Original D5H conflict witness recovered as 0101101010101010101111111110000.

Producer clocks m2 empty 100021617 vs old 104551138; m3 forced 1174779533 vs old 1191370586. The large selector/deposit cost remains, so the producer state reduction is not proportional to clock reduction.

Tests executed: 45 independently constructed single-coordinate conflict cases (domains 2..6, all nine positions) verified original witnesses and exact worker cost accounting. Five original fixtures compared actual direct producer stream bit-for-bit against host canonical mask oracle (including K5); 48 accepted, two refused among 50 IR cases. Three malformed selector variants refused. These are finite tests, not a proof of all normalized inputs. New CI runs all six physical cases, quotient cutoff, four m2 independent native replays, original witness verification and inherited governance.

Next: confirm D5I current-head CI and m4 physical replay; investigate bounded multi-coordinate repair and genuine unary/binary propagation, plus a shared smaller normalization controller. No changes to main or PR #248.
