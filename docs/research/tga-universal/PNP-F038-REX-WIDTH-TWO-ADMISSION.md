# F038-REX-024A — Exact quotient of the general width-two witness and original stage admission

Parent befcb8e24319c9aaa201af61f651b30ccb957097 (REX-023D3). Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

D3 implemented raw-selector-to-original-Boolean-witness computation for the normalized nine-group width-two family. This cycle records its full physical resource argument, reduces its descriptor using an exact clock-preserving quotient, and audits the original universal schedule. No unrestricted SAT coverage is claimed. The D2 exact-head native run 45898896321 passed; D3 had no dedicated native workflow at its parent head, so native D3 and quotient gates are both added here and remain unconfirmed until run.

## D3 reconstruction resource argument

The D2 successful checkpoint contains a constant 202-bit header/scratch, N serialized relation bits, a decision bit, and R=27(w+1) rank bits, w=ceil(log2 m). D3 physically consumes the header, nine sections, and decision by shifting the binary column workspace and its delimiter right one cell per bit, retaining consumed bits in the existing prefix. The charged shift traverses O(log m) workspace bits, not the whole prefix. Thus this preparation costs O((N+R+1)log m). Consume each rank token 00b into binary A=2A+b and 010 as end-field. For each group, B=0..m-1: emit X iff A=B, emit Y iff A<=B for B>0. Physical output appends traverse remaining rank tokens and O(m) output bits; X insertion shifts the Y block by one. Cost O(m(R+m+log m)+R log m). Read the m pins from physical block 36 using delimiter-counted traversal of preserved prefix and masks, rotate once per pin and restore original cyclic order after m rotations. Charge O(m(L+N+R+log m)). Emit two guard zeros and join the X and Y/pin/guard blocks by shifting the latter left one cell. Halt on first original bit, with exactly 19m-7 contiguous output bits. Scratch elsewhere is allowed by the original tape_run contract. Normalization/structural refusal and admitted UNSAT halt on blank; neither emits a witness. D3 changes inherited malformed refusal to blank even for n=1.

For L=Theta(m^3), N=O(L log L), the reconstruction upper bound is O((N+R+1)log m+m(L+N+R+m+log m)), below D1/D2's conservative O(L^(8/3) log^2 L) bound. Total visited span O(L+N)=O(L log L). This is a constructive informal resource argument dependent on the inherited invariants, not a mechanized proof or numerical uniform clock constant.

## Exact parent table and quotient

The former compiler's large intermediate row arrays and previous quotient implementation exceeded the interactive tool resource limit in three attempts (generic RPC errors; precise cause not independently measured). A packed compile option now stores each transition as a 32-bit integer (state<<4)|(write<<2)|(move+1). It retains the old state enumeration and default serialized grammar. Chunked encoding avoids a large array of temporary strings. A separate comparison against the exact D3 parent compiled/decoded table verified ALL 2429775 packed entries and all four entry state IDs, with no changes. This is a compiler storage change, not a change to the machine algorithm or physical runtime.

Use graph reachability on all three read symbols (not semantic tape reachability), including halt as a separate class. The compact partition-refinement implementation represents blocks as contiguous intervals in a permutation of states, with inverse positions and typed-array predecessor lists. Initial blocks distinguish the three write/move pairs and halt. For each queued (block,symbol), snapshot its preimage, partition touched blocks, keep the larger part's class ID and label only the smaller part with a new ID. Existing pending splitters remain pending; enqueue the new smaller part for each symbol. The standard smaller-half refinement argument applies: when a previous splitter is pending both halves will be processed, otherwise the complement of the smaller part within the former stable splitter is already accounted for. Each split is forced by an observable finite read-sequence distinction. Termination yields the coarsest stable partition over graph-reachable states. Linear storage in q and constant-alphabet inverse adjacency; predecessor work and smaller-side relabeling admit the usual O(q log q) bound. Do not infer global minimum tape-program size from this partition.

For original transition T(s,a)=(t,w,d), the compiler verifies for every reachable s and symbol a that Q(f(s),a)=(f(t),w,d); initial maps to 0, halt maps to the unique last state. Induction over charged transitions preserves tape contents, head and halting clock for every input and cutoff. All original states happen to be graph reachable. No decoder or runtime interpretation layer is added to the resulting original-format descriptor.

| Metric | D3 | Quotient |
|---|---:|---:|
| Nonhalting states |809925|428414|
| Entries |2429775|1285242|
| State address width |20|19|
| Description bits |59124529|29988984|

Removed 381511 states (47.10%), 29135545 bits (49.28%). 58 initial blocks including halt, 428357 splits, 1285245 processed splitter-symbol pairs, 7902325 predecessor visits, 2429775 homomorphism checks. Original and quotient entry mapping [533704->424086,585083->257521,781408->740,787007->1732] is diagnostic only: a quotient class may include multiple original states; it is not a reliable phase observation. The quotient is encoded and decoded entry-for-entry. Differential control suite compared the complete class partitions (up to renumbering) of 256 deterministic seeded small machines against the earlier 023A reference implementation, including unreachable states/halt, immediate halts and equivalent loops. No disagreement.

## Executed physical verification

Original D3 principal evidence (from the prior mission's executed source) and compressed-machine replay use the same 12 fixtures. All compressed replays matched exact inherited clocks, halt heads, visited spans and expected output bits; all seven SAT witnesses passed the original JS verifier. Four admitted UNSAT halts and one SAT width-three structural refusal remained blank. A separate original D3 sparse replay checked 69377334 transitions and original integer witness 268260694. The new quotient controls checked four cutoffs including one step before the outside-triple halt and nine malformed/unsupported-input blank refusals with exact inherited clocks. No full universal stage was enumerated.

| Fixture | m | Quotient transitions | Result |
|---|---:|---:|---|
| empty |2|30003260|witness|
| outside triple |2|34911962|witness|
| nonmonotone star |2|40288500|witness|
| nonfirst chain |2|31626203|witness|
| middle-owner joint |2|58956884|witness|
| nonempty inconsistent |2|30968165|blank|
| joint-pair inconsistent |2|34465372|blank|
| disconnected contradiction |2|35143066|blank|
| unary contradiction |2|29496152|blank|
| K4 SAT refusal |2|26655850|blank|
| seeded mixed |3|483345064|witness|
| forced mixed ranks |3|338108760|witness|

Principal compressed completions total 1173969238 transitions, 702842 input bits, 255 original witness bits. Additional m=4 forced mixed-rank fixture (428744 bits) ran exactly 300000000 transitions, returned TIMEOUT at head 100653, span 107722. This is only a bounded execution, not a full domain-four halt or algorithm failure. Current total principal plus bounded 1473969238 transitions, excluding controls/repeated runs. Current physical tests ran in JS V8. Full domain-four and larger complete replays remain unmeasured. Native original-format regression for both original and quotient is committed but not asserted executed until confirmed.

## Original schedule admission

Original scheduler enumerates every binary description of length ell<=s with budget 2^(s-ell) and validates its output. Minimum sufficient stage for a particular successful witness execution is ell+ceil(log2 t), not the earliest successful universal stage. For blank halts the same arithmetic is only a halt slot, not witness admission. For s_k=k ceil(log2 L), minimum sufficient integer coefficient for that particular run is ceil((ell+ceil(log2 t))/ceil(log2 L)). Compression reduces every such slot by exactly 29135545 without changing t.

| Fixture | L | s3 | Original witness slot | Quotient witness slot | Quotient min k |
|---|---:|---:|---:|---:|---:|
| outside triple |37914|48|59124555|29989010|1874314|
| m3 mixed |161851|54|59124558|29989013|1666057|

At m=2 and m=3 the quotient is not even listed by s3; listing alone requires ceil(log2 L)>=9996328, hence L>2^9996327. This does not imply stage failure. The original exhaustive built-in '000' has length 3 and requires charged clock 2^n; for n=31 and 50 its sufficient stages 34 and 53 are already within s3=48 and 54, respectively. This proves budget eligibility and universal success on every SAT selector at those dimensions, not an executed exhaustive search. For m>=4, n+3 exceeds s3 (see exact inequality in 023A). No failure of a universal stage follows, since other programs may succeed.

With inherited resource bound t(L)<=C L^(8/3)(log2 L)^2 for a fixed C and sufficiently large supported SAT inputs, the compressed program is eligible and has enough time at s3 once L^(1/3) >= C 2^ell (log2 L)^2, where ell=29988984. The ratio L^(1/3)/(log2 L)^2 tends to infinity, so eventually this holds uniformly over the supported family. This conclusion is conditional on the constructive resource proof and requires no assumption about the first successful description. It yields eventual restricted-family cubic-stage admission, not a numerical threshold. The finite intermediate dimensions have not been covered at k=3. Some larger fixed k can absorb the finite exceptions because the restricted witness machine terminates on all supported SAT inputs and each finite length has finitely many selectors. This existence argument does not give a numeric k, nor cover nonnormalized or width-three-and-higher selectors. In particular it does not prove any unrestricted polynomial-time cutoff.

## Governance and next milestone

ADVANCE exact compression, packed compiler equality and original stage accounting. PRESERVE fixed-path B6 and D3's general physical witness computation. DECOMPOSE native confirmation, finite clock constants and intermediate cubic coverage, and structural scope beyond width two. RETIRE claims that a missing descriptor means universal failure or that quotient minimization minimizes all possible tape programs. STOP at restricted witness evidence. All four global routes and six Omega formal obligations remain open.

Next REX-024B: investigate structure-sensitive fallback for normalized width-three graphs, first by physically validating a bounded-width-three elimination plan (degree-three greedy is not automatically sound/complete as in width two; use an exact bounded nine-vertex order search or another proved method). Audit the resulting relation and separator complexity before making any subcubic-stage claim. Alternatively finish explicit D3 finite resource constants and domain-four complete replays. No unrestricted promotion.

Reproduce:
```sh
p=mathos/research/f038_rex_width_two_admission_audit.js
for suite in controls small larger ranktwo four-bounded; do node "$p" "$suite"; done
node "$p" --original-descriptor > /tmp/original.desc
node "$p" --descriptor > /tmp/quotient.desc
python -m mathos.research.f038_rex_width_two_witness_codec /tmp/original.desc
python -m mathos.research.f038_rex_width_two_admission_codec /tmp/quotient.desc
```
