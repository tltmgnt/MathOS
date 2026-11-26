# F038-REX-023C1 — Physical all-scope factors and elimination forest headers

Parent REX-023B 3c0c1372b4749305600619be9ed300bef0244ec6. Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

## Scope

Previous exact-head REX-023B Proctor run 45895460512 is confirmed successful, including its native original-codec checkpoint gate. This cycle implements the first bounded part of REX-023C: all local forbidden masks and the actual elimination-forest parent indices, directly from the original selector. The arbitrary-bag row serializer and variable-separator worker remain open. The earlier fixed-path B6 witness descriptor and its quotient remain unchanged.

The new fixed ternary machine has 421642 nonhalt states, 1264926 transitions and 29514944 serialized bits. No host-supplied scopes, factors, ranks, parent indices or graph enter the computation. The compiler uses the nine constant vertex IDs, and the physical simulator executes the serialized table. The observed output is not a Boolean witness.

## All-scope factor invariant

Use 166 blank-separated blocks to the left of the moving selector workspace, read right-to-left: 36 deduplicated edge flags (lexicographic pairs), one pin block, then 129 mask blocks. The latter are indexed by arity 1,2,3 and lexicographic increasing group tuples within arity. For every optional all-negative support of distinct X groups, regardless of its selector bit, deposit that bit into its corresponding mask. For selected supports additionally perform inherited edge deduplication. The exact physical clause address enumeration filters to each scope in lexicographic rank-tuple order. Every mask thus has exactly m^k bits for a k-variable scope; absent constraints and absent clauses are represented by zeros. No per-bag duplication is required. The total mask length is

    B(m) = 9m + 36m^2 + 84m^3.

All mandatory clause and pin validation remains inherited from 023B. A malformed input erases tentative graph, mask and pin storage with canonical single-zero refusal. For valid normalized input all original selector bits and masks are retained, even if the structure is outside width two. The initial graph, filled graph and elimination records are computed by the inherited greedy planner.

## Physical parent construction

The successful planner emits a 154-bit word: residual edge flags (36), active flags (9), nine elimination records (12 bits each), and acceptance bit 1. Each record is (v,a,b) with 4-bit IDs and sentinel 9. In elimination order, read the two neighbor fields of each record. If a=b=9, append parent sentinel 9. Otherwise scan subsequent records in increasing index, compare each vertex ID to a,b in finite control, and append the first matching record index as a four-bit word. The scan skips exactly eight bits after each unmatched vertex. All reads, comparisons, walks and writes are fixed physical transitions. The resulting 190-bit word contains the original 154-bit plan plus nine parent indices (36 bits). The root sentinel denotes a disconnected component, not a fake separator. On a structurally refused plan, no parent section is emitted.

Correctness: the later-neighbor pair is a clique after fill. Its earliest eliminated vertex has a bag containing the entire separator, so the parent index strictly exceeds the child index and the edge separator is precisely the child's later neighbors. The induced forest is acyclic and has running intersection: each occurrence of a variable before its own elimination has a parent containing it, until the variable's own bag. Every original selected factor scope is contained in the bag of its earliest-eliminated variable. Thus each factor can be owned exactly once by that bag, even when the bag order (v,a,b) is not sorted by group ID. A bag of arity r owns at most 2^(r-1) possible scope masks (all subsets containing v); r<=3. Absent scopes contribute all-zero masks. This supplies a well-defined input to the next physical relation builder.

The audit enumerates bag candidates using the actual emitted physical masks and parent records, comparing against independently decoded selected factors. This row computation is HOST-ONLY verification; no physical row words are emitted in C1. The old worker requires a different grammar, and was not executed on these checkpoints.

## Resource accounting

For L=Theta(m^3) on normalized dimensions, there are B(m)=Theta(L) mask depositions, each costing O(L) transitions for a physical shuttle including suffix shifts. There are at most three additional edge queries/insertions per selected optional clause, each O(L), and m pin depositions. Inherited normalization O(L log L), graph copy O(L), elimination and parent selection O(1) in m (nine vertices, fixed-size plan word). Total worst-case Theta(L^2) time, O(L) visited space and O(log L) binary counter workspace. Late ternary mask depositions alone force the quadratic lower bound on normalized inputs. Malformed finite binary inputs also cost O((L+1)^2) and O(L+1) space, because each consumed bit creates at most a constant number of depositions. This bound excludes actual bag row generation and the general solver.

## Executed evidence

Nine principal completions from original raw bits, comparing every physical mask to a direct independently decoded factor oracle, every graph flag and record to a host graph replay, every physical parent to the earliest-later-neighbor rule, and checking full factor coverage and running intersection for accepted plans. All four m=2 pin patterns; zero and dense masks; unary contradiction; nonconsecutive ternary scope; unsorted bag coordinates on star; cyclic fill; disconnected forest; K4 and dense structural refusal.

| Fixture | m | Mask bits | Mask ones | Parent records | Physical transitions | Outcome |
|---|---:|---:|---:|---:|---:|---|
| empty |2|834|0|9|26645129|forest |
| outside triple |2|834|1|9|26693134|forest |
| star |2|834|8|9|26666515|forest |
| cycle |2|834|9|9|26690876|forest |
| two triangles |2|834|2|9|26815807|forest |
| K4 |2|834|6|0|26655850|structural refusal |
| unary UNSAT |2|834|2|9|26645129|forest |
| dense all scopes |2|834|834|0|79393089|structural refusal |
| seeded mixed scopes |3|2619|41|9|282875190|forest |

Total 465163 raw bits, 1161 mask blocks, 9291 mask bits, 903 one bits, 63 physical parent indices, 549080719 charged physical transitions. Seven complete forests, two structural refusals. Host-only comparison of all 313 candidate tuples in 63 owned-factor bag relations agreed exactly with independent factor filtering, including zero-row unary bag. No observed mask, graph, parent or relation-oracle disagreements.

Separate sparse tape interpreter independently parsed and replayed the outside-triple descriptor for 26693134 physical transitions, checking all 129 masks (834 bits), raw selector, pins, original graph and exact 190-bit word. Total 575773853 transitions across principal and independent completed runs (excludes smoke runs, controls and repeats). Seven malformed controls, four budget cutoffs including one step before halt, and exact budget 26693134 verified. The current full tests execute in JS V8. Native regression and CI are committed but not asserted executed until verified.

## Decisions and next mission

Chose all-scope masks to avoid an input-dependent second raw enumeration and allow exact-once factor ownership. This deliberately increases fixed description size and storage constant relative to the 49-mask fixed-path producer. Parent indices are computed physically from the constant-size elimination word, rather than supplied by the host. The remaining actual bag row serialization was decomposed into a separate milestone C2; the relation oracle in C1 is not that serializer. No original-selector admission or general width-two witness result is claimed.

Next REX-023C2: consume this factor-forest checkpoint physically, derive owned scope IDs, enumerate and serialize each variable-arity bag's relation in the recorded coordinate order, explicitly encode parent/overlap and disconnected roots, then compare every emitted relation against the C1 oracle. Preserve physical masks or prove destructive use safe. All four global P vs NP routes and six Omega formal obligations remain open.

Reproduce:
```sh
for suite in small larger controls; do
  node mathos/research/f038_rex_width_two_factors_audit.js "$suite"
done
node mathos/research/f038_rex_width_two_factors_replay.js
node mathos/research/f038_rex_width_two_factors.js --descriptor > /tmp/factors.desc
python -m mathos.research.f038_rex_width_two_factors_codec /tmp/factors.desc
```
