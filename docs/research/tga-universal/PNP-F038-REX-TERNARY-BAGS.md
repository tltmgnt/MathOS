# F038-REX-022B4 — Fixed ternary nested-bag serializer

MRA-X 2.0 + RE-X; MRA-X Omega Phase III evidence. Parent REX-022B3 8aeafd2a0478682baf713abc32772b872e4561ab. Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

## Scope and machine interface

A fixed descriptor now starts from original raw selector bits, validates normalization and the fixed seven-bag path, deposits all 49 local forbidden masks and pins, and emits the exact nested-bag grammar on the same physical tape. No host-supplied dimension, clause, mask, rank, predicate table or prepared payload is used during this computation. The new serializer is fused into the inherited B3 success transition; B3 itself is unchanged. There are 127040 nonhalt states, 381120 transition rules, and 8130564 serialized bits, using the original alphabet 0,1,2 (blank) and moves -1,0,+1. The abstract machine is fixed independently of the input size.

Canonical outcomes: BAGS_PREPARED, OUTSIDE_NORMALIZED, OUTSIDE_FIXED_PATH and a distinct simulated TIMEOUT. On success the head is at the original final workspace separator (blank); the contiguous prepared word begins one cell right. To the left lie the complete restored B3 masks, pin block, selector payload and binary workspace. On rejection, inherited cleanup writes a single status bit, without starting serialization. The finite simulator decodes the descriptor before running; the optional phase observer merely records the step count at entry to bag0Start. These are simulated physical transitions, not elapsed time. The original worker has not yet been composed into this descriptor; the checkpoint is not an isolated worker tape or an original Boolean witness.

## Physical serializer invariant

After the B3 phase, mask h in bag j, ID 7j+h-1 for h=1..7, contains the lexicographically ordered forbidden bits for the nonempty subset of the bag selected by h. The mask is physically read from right to left. Let z=(a,b,c) be the current candidate tuple, represented in the inherited binary rank lanes. Each rank ranges from zero to M=m-1. Initially all ranks and all mask rotation offsets are zero. For every mask, the first bit in its cyclic physical representation is the bit at the lexicographic projected rank of z. Querying the first bit of each of the seven masks decides whether to emit the row; a forbidden bit short-circuits the remaining queries but not the odometer updates.

A mask shuttle counts fixed blank delimiters from the workspace separator. A forward rotation carries the first bit to the far end, then sweeps right with a one-symbol carry, preserving length and all other blocks. A reverse rotation temporarily replaces the first bit with a blank, sweeps left with the first bit as carry, and writes the last bit in the temporary blank on return. In either case all delimiters, raw selector, pins and workspace are unchanged. The mask query returns the first bit in finite control, without modifying any cells.

The candidate odometer increments the rightmost nonmaximal rank c (coordinate 0,1,2), after setting all lower ranks to zero. For a mask containing c, the projected rank increases by one, regardless of which lower coordinates it contains. For a mask excluding c but containing k lower coordinates, the projected rank decreases by m^k-1; if k=0 it is unchanged. The serializer applies the corresponding forward rotation or sequence of reverse rotations to every mask. The zeroed lower lanes count the reverse steps, with one- or two-dimensional loops for k=1 or k=2, then return to zero. In the two-dimensional loop there are m groups of m-1 moves and m-1 extra cross moves, giving m^2-1 exactly. Thus the invariant holds inductively for every candidate. At the last tuple, each projection is at its final index. After clearing the odometer, a forward rotation of each mask restores its original representation exactly. This ensures the physical checkpoint preserves the mask oracle and not merely the generated rows.

The prepared word starts with root token 11111, each subsequent bag starts with 11110, and every bag's row list ends with 110. Each allowed row is 011 followed by three rank fields (each binary digit b encoded 00b, MSB first, followed by 010), then 101. The seven nested closes are 010 repeated seven times. Zero-row bags are emitted with their header and row-list terminator, not omitted.

Rank width is w=bit_length(m-1), whereas the inherited binary workspace has bit_length(m) columns. At the high column, test the M bit; skip that column iff it is zero. There can be at most one excess leading zero, since m>=2. Read the selected rank lane MSB first. For each digit, mark its cell temporarily blank and keep its old value in finite control; append 00b to the output word by scanning to its end; return to the fixed separator, locate the marked digit and restore it. A fixed-distance lookahead determines whether another column remains. Group words are unchanged. This yields exactly w digits for each of the three fields, including leading zeros of the rank. Token append operations similarly return to the same separator. No output address is supplied by the simulator.

Together with B3, these invariants give an informal constructive proof that the accepted raw input produces precisely the inherited REX-022A prepared grammar. The proof is not mechanized.

## Resource argument

For valid dimensions, L=Theta(m^3), masks plus pins occupy Theta(L), and there are 7*m^3 candidates. Let N be the serialized output length; N<=77+7*m^3*(15+9w)=O(L log L). Query and rotation shuttles cost O(L) each because they cross the retained selector and masks. The total rotation count is O(m^3): for a carry at coordinate c there are O(m^(c+1)) carries, and at most m^(2-c)-1 reverse steps for any mask excluding c, so the products are O(m^3); the number of masks and bags is fixed. There are O(m^3) queries and rank/odometer counter operations apart from digit emission. Counter operations cost O(log m). The serializer's output append cost is O(N^2+N log L), since each emitted token or digit traverses the current output prefix plus at most logarithmic workspace. Thus total raw-to-prepared time is O(L^2+N^2)=O(L^2 log^2 L), below cubic asymptotically. The lower bound Omega(L^2) holds for every accepted input because every candidate queries at least one mask across the retained selector; for empty constraints N=Theta(L log L) and appends force Omega(N^2). Hence worst-case accepted time is Theta(L^2 log^2 L). Total visited space is O(L+N)=O(L log L); binary counter workspace is O(log L). Invalid raw input never starts serialization and inherits B3's O((L+1)^2) bound.

No resource claim is made for same-machine worker handoff or Boolean witness translation. The inherited worker's bound in its own input length must be composed carefully with N=O(L log L), not silently treated as O(L) for all inputs. The descriptor length is fixed but huge compared with tested original stage indices. Original selector admission is open.

## Executed differential evidence

The principal audit used two grammar oracles: exact charged REX-022A producer output and independent rank-tuple filtering with the original REX-020 encoder. It also compared all restored masks against the instrumented REX-022A mask checkpoint, pins and entire original selector payload, plus final rank reset. Output inspection is host-side, but generation is entirely by physical transitions.

| m | Fixture | Raw bits | Prepared bits | Allowed rows | Physical transitions | Serialization transitions |
|---:|---|---:|---:|---:|---:|---:|
|2|empty|37914|1421|56|61579486|53930334|
|2|forced|37914|245|7|41229674|33580522|
|2|dense|37914|77|0|35356646|27707494|
|2|mixed|37914|77|0|38398540|30749388|
|3|empty|161851|6314|189|855731937|802972509|
|3|mixed|161851|143|2|535507485|482748057|
|4|mixed|428744|737|20|3556516463|3304165517|

Seven completed principal fixtures: 904102 original bits, 9014 physically emitted bits, 274 allowed rows, 343 restored mask blocks (2478 bits), 5,124,320,231 physical transitions (4,735,853,821 serialization transitions). No observed byte, mask, pin or rank-reset disagreements. All four m=2 pin patterns, zero-row bags, mixed empty/nonempty bag lists, full rows and rank widths 1 and 2 were tested. The read-only phase entry clocks 7649152, 52759428, 252350946 agree with separately measured B3 halt clocks. Eight targeted rejection controls, seven budget cutoffs (including serialization entry -1, entry, entry +1 and one-before-halt), and exact-budget completion at 61579486 passed. An additional m=5 bounded raw run consumed exactly 900000000 transitions and returned TIMEOUT; no full m=5 serialization result claimed.

An independently written sparse Map interpreter parses the emitted transition descriptor and replays the forced m=2 fixture for 41229674 steps, verifying physical output, restored mask blocks and absence of stray tape symbols. One independent completion. Headline 5,165,549,905 transitions = seven principal completions plus that sparse replay; excludes the dense repeat in the replay harness, larger-domain timeout, controls and repeated exact-budget runs.

Two additional inherited REX-020 worker runs on the host-extracted *physically emitted* words: SAT forced fixture (1591842 transitions, row certificate 1111111, original host-translated witness verified) and UNSAT dense fixture (78018 transitions). Total worker 1669860 transitions, reported separately. The host moves the word to a fresh worker tape; same-machine handoff and physical witness translation remain open.

Development choices: preserve all B3 data and restore masks; use cyclic in-place rotations rather than an indexed lookup table; use output append shuttles rather than compaction. A combined audit call hit the tool wall-clock limit, so the tests were split into independently executed suites; m=5 completion deferred and replaced with a verified bounded cutoff. Source cleanup removed unused compile-only movement definitions; reachable descriptor sizes unchanged. All successful tests executed in JavaScript V8 on retrieved exact-parent modules. Native Node workflow, Python original codec replay and mechanized certification are not confirmed in-session.

## Governance

ADVANCE fixed raw-to-nested-bag physical producer. PRESERVE B3 masks and pins and REX-020 worker. DECOMPOSE same-machine isolated worker handoff, worker exit preservation, physical original witness translation and combined clock analysis. RETIRE treating BAGS_PREPARED as SAT or host transfer as physical composition. STOP after serializer evidence. All four global routes and six formal Omega obligations remain open.

Next F038-REX-022B5: implement and verify same-machine worker handoff. The worker needs its expected isolated tape layout; preserve necessary pins and witness recovery information via an explicit physical encoding or prove the worker never touches protected storage. Recompute the composite descriptor and phase ledger, exercise SAT and UNSAT without host resetting the tape. No original selector promotion.

Reproduce:
```sh
for suite in small three four five controls; do
  node mathos/research/f038_rex_ternary_bags_audit.js "$suite"
done
node mathos/research/f038_rex_ternary_bags_replay.js
node mathos/research/f038_rex_ternary_bags.js --descriptor > /tmp/bags.desc
python -m mathos.research.f038_rex_ternary_bags_codec /tmp/bags.desc
```

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
