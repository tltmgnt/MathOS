# F038-REX-022B3 — Physical forbidden-mask and pin deposition

MRA-X 2.0 + RE-X; MRA-X Omega Phase III evidence. Parent REX-022B2 d074d5d68f68716adc640932bb1f30a3b5bf8304. Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

## Scope

A single fixed ternary descriptor now accepts original normalized raw selectors on the fixed seven-bag path and physically creates all 49 local forbidden-tuple masks and the pin string, retaining the raw selector payload. No host-supplied dimension, rank, scope, mask bit, predicate table or storage update is used in its execution. The previous normalization state machine is specialized with new scope dispatch and deposition transitions; the separate REX-022B2 machine is preserved. This is a fusion of validation and deposition, not an execution that feeds the halted B2 descriptor's checkpoint into a second machine. Tentative masks are erased on any rejection. No physical bag serialization or same-machine worker handoff is claimed.

The descriptor has 65275 nonhalt states, 195825 transitions and 3981779 serialized bits. It uses 0,1,2 (blank) and moves -1,0,+1. The transition table is generated once independent of m. Decoded transitions exclusively drive each physical read/write/move. Host inspection of output and oracle operations are not machine execution.

Outcomes: MASKS_PREPARED (blank-head checkpoint), OUTSIDE_NORMALIZED (single zero), OUTSIDE_FIXED_PATH (single one), TIMEOUT (not a halt). No outcome constitutes an original Boolean SAT witness. In particular the normalized all-forbidden fixture yields a complete mask checkpoint despite being UNSAT.

## Mask invariant and constructive correctness

For bag j=0..6 with scope (j,j+1,j+2), and nonempty bit mask h=1..7, let H be the selected subset. The output block ID is 7j+h-1. Its length is m^|H|. For each lexicographically ordered rank tuple z in [0,m-1]^|H|, its bit equals the original selector of the all-negative clause on the corresponding X variables. Zero bits are retained just as one bits are. Each optional negative support is copied to every containing bag, so overlapping unary and binary scopes deliberately produce duplicated bits. The output pin block ID 49 contains the original lifted-pin polarity in increasing pin-variable order.

The inherited address and clause validator traverses increasing supports and negative-before-positive sign patterns. When a support lies entirely in distinct X groups, a fixed decision DAG identifies all containing bags from the group words (not the variable ranks or host tables). The sign-zero state reads the raw bit and dispatches the finite sequence of depositions for those block IDs. All other signs retain their inherited validation rules. A P,G1,G2 first-sign bit b appends 1-b to the pin block, before all eight lifts are validated. Selected outside-path scopes set the inherited finite flag, and any invalid later bit takes precedence over the structural flag. Header processing and strict normalization follow REX-022B2.

Physical layout at each selector event, from left to right:
[blank][pins reversed][blank][mask 48 reversed][blank] ... [mask 0 reversed][blank][consumed selector prefix][blank][binary workspace][blank at head][unread raw suffix].
Empty blocks are represented by adjacent blank delimiters. The 50 conceptual empty blocks initially exist in the blank left region; no host initialization of data is needed. The workspace separator moves right one cell per consumed bit; the left boundary of the consumed selector prefix is fixed once the header is complete.

Each deposit executes a single-head shuttle:
1. From the separator, scan left across the workspace and consumed prefix to the rightmost mask delimiter. Count delimiters in fixed control to reach the left boundary of the target block.
2. Write the new bit in that boundary. Carry the old blank left, shifting every cell of the farther-left suffix by one cell. The carry is always a ternary symbol; finite control counts the remaining delimiters. Once the far-left separator is reached, extend by one blank.
3. Scan right through exactly 50 delimiters, then through the prefix and workspace, returning to the original separator. The current raw bit remains unchanged until the inherited consume operation.

Induction on depositions proves that the target block appends exactly one bit when read right-to-left, all other blocks retain their exact sequence, and workspace/prefix/raw cursor are unchanged. For a fixed subset H the filtered original support order is exactly lexicographic rank order, since groups are ordered and distinct. Therefore each output mask equals the REX-022A reference mask, including all absent clauses. At accepted halt every required bit has been appended exactly once per containing bag. The pin order is similarly exact. Rejection cleanup erases the raw suffix, workspace, consumed prefix and all 50 blocks, even if only partly populated, and leaves one result bit. This is an informal constructive proof; mechanized proof remains open.

## Resource accounting

For a valid normalized dimension, L=Theta(m^3), and the total mask bits are
B(m)=7 sum_{k=1}^3 C(3,k)m^k = 7((m+1)^3-1).
There are exactly B(m)+m depositions (pins included), irrespective of which constraints are selected. Each shuttle costs O(L+B(m)+log m+1)=O(L) transitions, including any shifted suffix, the consumed-prefix traversal and the return path. The inherited normalization costs O(L log L), so the fused machine costs O(L^2). A matching Omega(L^2) bound on accepted inputs follows because Theta(m^3) ternary deposits for the last bag occur after a prefix of length Omega(m^3), and every deposition traverses that prefix. Hence accepted input time is Theta(L^2), without invoking a generic multitape simulation. Arbitrary finite binary inputs of length L also have O((L+1)^2) time: at most three mask depositions per consumed selector bit and at most one pin deposition per pin event; accumulated storage is O(L+1), including partial blocks, and cleanup is linear. Space is O(L+1) visited cells, including the retained selector and masks; active counters remain O(log(m+1)) bits, plus fixed finite control. This replaces the earlier projected O(L^(7/3) log L) bound for the producer *only for the normalization+mask stage*. Bag row enumeration, serialization, worker, and original witness translation are not included.

The decision to use a quadratic shuttle instead of faster indexed storage favors an actual fixed descriptor and straightforward tape invariants. It does not claim optimality. The mask checkpoint provides local relations but no physical join/elimination computation.

## Executed evidence

All principal inputs were made by the exact inherited encoder. Output masks were compared byte-for-byte with (1) a direct independent selector-pool oracle and (2) the REX-022A charged producer instrumented only in the test harness to expose its mask tape contents immediately before row output. Pin strings, retained original selector, all mask lengths, boundaries and absence of extraneous nonblank cells were verified. A host-only serializer consumed the actual extracted physical masks and matched the existing REX-022A prepared grammar byte-for-byte. This last step is an integration oracle, not a physical serializer.

| m | Fixture | Raw bits | Mask bits | Selected cross clauses | Mask ones | Physical transitions |
|---:|---|---:|---:|---:|---:|---:|
|2|empty|37914|182|0|0|7649152|
|2|forced|37914|182|9|21|7649152|
|2|dense|37914|182|134|182|7649152|
|2|seeded mixed|37914|182|47|68|7649152|
|3|seeded mixed|161851|441|125|152|52759428|
|4|seeded mixed|428744|868|278|332|252350946|
|5|seeded mixed|893465|1505|536|627|872353008|
|3|forced|161851|441|18|42|52759428|

Eight completions: 1797567 original bits, 392 mask blocks, 3983 mask bits, 23 pin bits, 3616 host-serialized prepared bits, 1260819418 charged physical transitions. Zero observed mismatches. All four m=2 pin patterns tested. Dense fixture: 134 distinct selected optional clauses, 182 deposited one bits (48 additional overlapping bag placements); no optional zero bit survives in this particular fixture, whereas the empty fixture has 182 zeros. All 49 blocks exist for every accepted fixture.

Eleven targeted rejection controls passed: malformed empty/header/mandatory, first-sign-only and partial ternary truncations, late pin failure, last-bit truncation, extra suffix, binary and ternary outside scopes, and outside scope followed by malformed lift. Canonical cleanup verified. Four timeout controls including one-step-short and an exact halt budget at 7649152 transitions passed.

Independent JS sparse Map tape simulation (separate table parsing and stepping) replayed a normalized input and a normalized outside-path input, verifying payload, masks, pin layout, rejection cleanup and one-step-short timeout. Two completions, 15336449 transitions; 182 mask bits independently replayed. Headline 1276155867 transitions across eight principal and two independent deposition-machine completions; controls and repeated cutoff runs excluded.

Two *additional* inherited REX-020 physical worker runs used the host-serialized masks: forced m=3 SAT row certificate 1111111, 2503920 transitions; dense m=2 UNSAT, 78018 transitions. The SAT row certificate maps to all nine rank-2 values; the original Boolean witness with pins 101 was constructed and validated by the inherited verifier. Witness reconstruction was host-side, as was serialization and the handoff. Combined worker transitions 2581938, separate from headline. No new unrestricted SAT evidence.

Development: the first compile attempt encountered impossible non-increasing group assignments in the static DAG enumeration; added an internal BROKEN target for these unreachable assignments before successful physical tests. V8 executed retrieved exact-parent modules. Native Node and original Python replay are regression gates, not claimed executed in this session; exact-head CI unconfirmed. The descriptor's large fixed description also prevents any inference of original selector admission at the tested stage indices. No mechanized certification.

## Governance and next mission

ADVANCE physical all-mask and pin deposition; PRESERVE exact normalization and REX-020 worker; DECOMPOSE physical mask odometer and bag record serialization, same-machine worker handoff, Boolean witness translation; RETIRE any inference from MASKS_PREPARED to SAT; STOP after this bounded producer stage. All four global P versus NP routes and six formal Omega obligations remain open.

Next F038-REX-022B4: physically serialize the 49 local masks into the REX-020 nested-bag grammar, including rank-width encoding, zero-row bags and separator/carry behavior. Prove a resource bound and compare the exact physical prepared payload with the inherited worker grammar. Then address the same-machine handoff; no original selector promotion.

Reproduce:
```sh
node mathos/research/f038_rex_ternary_masks.js
node mathos/research/f038_rex_ternary_masks.js --independent
node mathos/research/f038_rex_ternary_masks.js --descriptor > /tmp/masks.desc
python -m mathos.research.f038_rex_ternary_masks_replay /tmp/masks.desc
```

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
