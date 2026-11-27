# F038-REX-024D6E — Automatic scope-graph decomposition and complete connected fallback

Parent D6D 675ffcef61686b51ec235e399d69354390984406. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D6D exact-head verification
[Proctor 46028751351](https://github.com/tltmgnt/MathOS/actions/runs/46028751351) at 675ffce completed successfully, all 15 jobs: 12 physical original/quotient/cutoff, two native, one audit/governance. Includes crossing cutoffs and m3 SAT in both modes.

## Controller construction and correctness (genuine normalized canonical stream)
D6E replaces the fixed three-triple admission and refusal with discovery of the active scope graph. The producer, original witness projector, GAC and direct row-extension rules are retained. After sound GAC, reuse support scratch V0 for an edge list. Scan the genuine run-coded stream once with the fixed scope directory D. For a nonuniversal pair append its two IDs, and for a nonuniversal triple append its first-to-second and first-to-third IDs. The universal 10 field contributes no edge. Each ID uses four bits; at most 36+2*84=204 edge records, 1632 bits. A positions 7..15 store 0=unseen, 1=current, x=solved; the blank at 6 preserves the bounded GAC budget format. No host graph certificate or partition is provided.

Choose the smallest unseen coordinate and mark it current. Repeatedly scan only the compact edge list, adding the other endpoint whenever one endpoint is current. Stop when no new coordinate was added. The stored edges induce the same connected components as the active scope hypergraph. Each nonfinal sweep grows the current set by at least one vertex. It is contained in the seed's component throughout and is edge-closed at the fixed point, hence exactly the component. At most s sweeps for a component of size s (including the final unchanged sweep); at most nine sweeps in total. A solved vertex cannot be adjacent to an unseen/current vertex, by closure of its component. The component list may be discovered in any normalized instance; connected inputs simply select all nine coordinates. No specialized outside-class refusal remains for genuine normalized inputs. Invalid or out-of-family normalization may still use the inherited blank halt; no all-input status theorem.

For a singleton component, GAC's first surviving unary rank already satisfies all its constraints, so no candidate scan is needed. For a nontrivial component, scan the prefix-ordered directory/stream, testing only factors whose first coordinate is current. Other active fields are skipped without evaluating their rows. On conflict, inherited direct extension and suffix reset/carry operate only on current coordinates. Search advances in local lexicographic order without skipping satisfying tuples: factors are wholly local; the failed last-coordinate row and all skipped disallowed last ranks for its fixed earlier prefix cannot satisfy that factor; suffix resets and carry preserve the next possible local tuple. Exhaustion is genuine normalized UNSAT. Sound GAC cannot remove a satisfying assignment. After a component succeeds, mark it solved and preserve its selected ranks. Cartesian product factorization yields the original lexicographically first global satisfying assignment. Connected inputs use the same complete direct extension logic as D6C, with no special refusal. This is a source-level argument under the genuine stream and lowering preconditions; physical replay is finite evidence.

## Adaptive maximum-component theorem
For actual component sizes s_i, k=max_i s_i, and domain size m, the candidate bound is
C <= sum_{i:s_i>=2} m^(s_i) <= 9 m^k.
Singletons have zero complete candidate visits. The stronger D6C first-active-factor functionality charge, applied separately in each local prefix order, gives C_i <= min(m^(s_i),1+3 s_i m^(r_i)) for a nontrivial component with r_i certified functional roots, subject to the inherited certificate argument. Thus the exponent depends on the largest component or maximum certified root count rather than the sum.

Under inherited physical macro assumptions, graph building and discovery add O(S) primitives for fixed nine variables, dynamic membership tests add O(1) per scope and per carry/reset, and the scratch graph adds at most 1632 bits. The unchanged GAC and candidate macros therefore give O(S(C+m+1)) primitives, O(S+m+1) segmented span and conditional O(L^2(C+m+1)) total, using S=O(L), L>=4096 m^3. Consequently O(L^(2+k/3)) for k>=2: k=2 gives O(L^(8/3)), k=3 O(L^3), and k=9 O(L^5). For all singleton components the unchanged GAC has one no-change pass, zero candidates, giving conditional O(L^2). No new explicit 512 L^3 constant, mechanically proven macro bound, universal cubic admission, or unrestricted SAT reduction is asserted. General connected constraints remain unresolved.

## Independent audit
Executed 510 fixtures, 1020 modes, 896 SAT and 124 UNSAT; of these 860 SAT and 116 UNSAT cross the old fixed partition. 26 fully connected mode executions. Independently decoded clique graph/BFS component discovery and relation-level propagation/direct-extension traces matched 5904 discoveries and edge-list comparisons, 4858 singleton bypasses, 2372 candidate visits and 1338 conflicts. Tested every pair and triple scope (120), every ternary mask on a crossing triple (256), every integer partition size pattern of nine (30; one interleaved labeling each, not every labeled set partition), 12 functional fixtures and 90 seeded random fixtures plus two base fixtures. Exact original witness or blank UNSAT matched the independent exhaustive oracle. All candidate ceilings checked. No correctness mismatch in executed audit. This is not exhaustive all-input verification.

Selected exact source-accounted SAT worker clocks (pins zero):
| fixture | D6C | D6D | D6E |
|---|---:|---:|---:|
| empty m2 | 183311146 | 419632682 | 341343496 |
| crossing pair m2 | 194910862 | outside class | 433535020 |
| connected one-root m2 | 609609700 | outside class | 872189768 |
| equality triples m2 | 1149574156 | 921521072 | 1227210254 |
| equality triples m3 | 4598984028 | 1629504332 | 2046556678 |

D6E avoids repeated original-stream scans during closure and avoids all singleton candidate scans. It still traverses the full source stream for each nontrivial candidate and may be slower than D6C/D6D. Empty fixture improves over D6D, not D6C. D6E m3 triples beat D6C by approximately 2.25x in worker clocks but lag D6D. No uniform performance gain.

## Lowering and observed original-selector replay
Initial adjacency-bit implementation generated 19830 bounded IR instructions. Compact scratch edge list reduces to 10548 (full 10547), but the quotient exceeds the previous 21-bit threshold. Original table and exact reachable quotient constructed in both modes.

| mode | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|
| bounded | 3925504 | 2826496 | 223293188 | 11776512 |
| full | 3923224 | 2824773 | 223157071 | 11769672 |

20 tapes, four-bit segmented encoding, 22-bit state numbers; bounded descriptor grows approximately 42.9% from D6D. This cost is not a proof of any budget slot.

| fixture / mode | original transitions | head | span | result | quotient + exact cutoff |
|---|---:|---:|---:|---|---|
| cross-sat bounded | 466373694 | 45712 | 46503 | SAT | matched, cutoff 466373693 |
| empty-domain full | 71580968 | 38219 | 46117 | UNSAT | matched, cutoff 71580967 |
| triple-2-sat bounded | 1262785614 | 46422 | 47235 | SAT | original only observed interactively |

Crossing SAT witness 1001101010101010101111111110000; worker 433535020. Triple SAT witness 0101010101010101011111111110000; worker 1227210254. Both worker clocks match actual raw-selector phase clocks. The combined full connected-UNSAT/triple-SAT replay timed out interactively; do not claim its results. CI registers twelve original/quotient/cutoff jobs, two native descriptor jobs and an independent audit/governance job. D6E CI completion not yet established at this checkpoint.

## Next D6F
Reduce dynamic controller descriptor below the 21-bit threshold; index component-local factor traversal to avoid repeated whole-stream scans; verify connected UNSAT, multi-component quotient/cutoffs and native exact-head CI; derive independently checked physical macro bounds and investigate connected separators. Keep D6C as general-purpose baseline until benchmarks justify switching. Main and PR #248 unchanged. No promotion.
