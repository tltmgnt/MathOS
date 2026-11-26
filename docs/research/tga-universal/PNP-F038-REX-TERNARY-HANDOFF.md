# F038-REX-022B5 — Same-machine physical elimination handoff

MRA-X 2.0 + RE-X; MRA-X Omega Phase III. Parent REX-022B4 b9793ca3f619e2efe0df8f281c0001533d2e399f. Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

## Scope and interface

A single fixed original-format ternary descriptor now takes an original raw selector, executes the complete B4 producer, physically relocates its prepared word to an isolated region of the same tape, and directly executes the unchanged REX-020 worker. No host resets, input extraction, phase-dependent tape rewrites, or host-supplied coordinates are involved. Compilation combines finite transition tables; simulation uses only the serialized-and-decoded combined descriptor and the current physical symbol. The only edit to B4 is exporting its existing success-state index as compile-time metadata. Its reachable transitions and descriptor are unchanged. The worker transition table is copied with state renumbering and a common halt. Rejection halts in the producer still bypass the worker.

The composite has 254151 nonhalting states, 762453 transition entries and 17028121 description bits. Components: 127040 producer states, 116 bridge states, 126995 worker states. Ternary alphabet 0,1,blank; head moves left, stay, right. The worker's six-cell logical alphabet encoding is unchanged.

At halt on an accepted normalized fixed-path raw input, a nonblank worker head denotes SAT with the original REX-020 row-index certificate; a blank worker head denotes UNSAT. The producer's single-bit rejection convention remains separate; the host status observer records whether worker entry occurred. This is a restricted physical decision/row-certificate machine, not an original Boolean witness machine. UNSAT scratch remains as in REX-020. Host status labels are observational, not an extra physical output protocol. On SAT the complete producer-side data (pins, all 49 original masks, selector payload, rank bounds and group words) is retained, and the row certificate is on the same tape. Translating that certificate physically into exactly n original Boolean bits is still open.

## Physical isolation bridge

Let h be the B4 success separator and N the prepared word length. Initially the word occupies h+1..h+N with a blank on each side. The producer data is at positions strictly less than h. Set w=6 (worker block width), K=w+4=10 (fixed constant). The bridge maintains the following region to the right of the preserved separator:
[source prefix][blank][zero gap][blank][relocated suffix][blank].
After i source bits have been popped from right to left, the source prefix has N-i bits, the relocated suffix has i bits in their original order, and the zero gap has (K+1)i cells. The initial suffix and gap are empty.

Pop the last source bit into finite control; its cell becomes the new source separator. Write zero at the old separator, increasing the gap by one. Scan right to the gap delimiter. K times, move the delimiter one cell right by writing zero at its old cell and shifting the entire relocated suffix one cell right with a single-symbol carry. Finally prepend the held source bit by a carry sweep right through the suffix, increasing its length by one. Return left across suffix and gap to the new source separator. These scans never move left of h. Induction proves the invariant and exact suffix ordering. When the left neighbor of the source separator is blank, the prefix is empty, and this neighbor is h. Return right, erase the zero gap and enter the worker's start state at the first bit of the relocated word.

The resulting worker origin is
o=h+(K+1)N+3=h+11N+3.
The entire interval [h,o-1] is blank. The only nonblank cells to the right of h are the N prepared bits starting at o. This is established by actual transition rules, not by an artificial virtual tape origin.

For i=0..N-1 the pop/shift/prepend/return loop takes exactly 4(K+1)i+3K+9 transitions. Initialization costs N+2; final empty-prefix detection and gap erasure cost (K+1)N+4. Consequently the exact bridge clock is
T_bridge(N)=2(K+1)N^2+(2K+9)N+6=22N^2+29N+6.
This includes all relocation and blank erasure moves.

## Worker isolation argument

The REX-020 preparation codec visits only the raw word and a leftward product region of width wN, with at most constant-sized blank probes. The logical worker installs L immediately left of the first encoded input block and R immediately after the last. Compile-time checks exhaust all logical rules at L, R and blank: nonreject L rules never move left and preserve L except the final clean transition (which erases L and moves right); nonreject R rules never move right and preserve R; the only nonreject blank rules install L or R and move inward. The logical reject rules halt without moving and write blank. The aligned physical codec performs bounded-width read/write/move scans, so prior to projection the left extent is bounded by w(N+1)+O(1). The output projection erases the encoded region and writes H<=N row bits left of it. The inherited exact SAT output head is -wN-H-2 relative to the worker origin, and the projection's outermost blank probe is one cell further left. Hence a conservative bound for every accepted grammar (SAT or UNSAT) is worker head >= o-(w+2)(N+2). No dependence on observed input-specific maximum travel is used for isolation.

All B4 words have N>=77 (seven empty tables). For w=6, o-(w+2)(N+2) = h+3N-13>h. Therefore the worker never reads or modifies protected producer storage. Induction on worker transitions gives exact equivalence to execution on a fresh isolated tape, translated by o, including terminal head, certificate and rejecting scratch. The bridge and boundary argument constitute a constructive proof, not a mechanically verified theorem.

## Executed differential evidence

The actual combined serialized descriptor was replayed from original inputs. At the handoff observer, each prepared word matched the inherited producer byte-for-byte; worker entry word, exact origin and blank isolation were checked. At halt, every protected cell matched its prehandoff value, and the complete worker-side nonblank tape, translated head and exact worker transition count matched an isolated REX-020 reference replay. Exhaustive independent enumeration of m^9 latent assignments verified each decision. Three SAT certificates were decoded on the host into mutually consistent bag rows and original n-bit Boolean witnesses, then checked against every selected original clause. Neither the host exhaustive oracle nor the isolated worker replay influences the composite descriptor.

| Fixture | m | L | N | Producer | Bridge | Worker | Combined | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| forced |2|37914|245|41229674|1327661|1591842|44149177|SAT|
| multirow |2|37914|269|42067940|1599749|1897883|45565572|SAT|
| empty bag |2|37914|1229|57769910|33265349|21614082|112649341|UNSAT|
| inconsistent nonempty bags |2|37914|365|49848492|2941541|1609212|54399245|UNSAT|
| rank two |3|161851|308|515740005|2095946|2503920|520339871|SAT|

Five complete principal runs: 313507 original input bits, 2416 prepared bits, 706656021 producer transitions, 41230246 bridge transitions, 29216939 worker transitions, total 777103206. All five physical worker tapes, head positions and clocks matched the isolated worker. All five protected regions unchanged; no observed discrepancies. The minimum observed distance from worker head to protected separator was 1218 cells (forced fixture); the five margins were 1218,1337,6141,1821,1533. The inconsistent fixture has nonempty local tables [1,2,2,2,2,2,1] but contradictory endpoint requirements connected by equality constraints, hence UNSAT, not merely an empty-table rejection. SAT row certificates 1111111, 10111111, 1111111. Multirow fixture has two models; the selected ranks were [0,1,0,1,0,1,0]. The m=3 selected ranks were all two.

A separately written sparse dictionary-tape parser and interpreter replayed the entire forced input without a reset: 44149177 transitions, exact phases and 38091 protected nonblank cells preserved; seven-bit certificate matched. Combined headline 821252383 physical transitions (five principal plus one sparse replay). Excludes host reference computations, isolated worker comparison runs, cutoff repeats and smoke runs. Nine cutoff controls passed, including one-before/exact/one-after producer and worker phase boundaries, and one-before-halt; exact completion at 44149177. Three producer refusal controls passed without entering either bridge or worker. All tests executed in JavaScript V8 using retrieved sources at exact parent and research branch. The full m>=4 composite has not been executed. Native Node CI and the original Python replay are added as gates, not claimed executed in session.

## Resource composition

For accepted fixed-path normalized inputs let L denote original selector length, N the produced word length. B4 proves T_producer=O(L^2+N^2), N=O(L log L), and worst-case accepted time Theta(L^2 log^2 L). The new bridge is Theta(N^2) time and O(N) additional span, including the entire erased gap. REX-020 provides Theta(N^2) time for valid explicit words (quadratic preparation lower bound) and O(N) tape span. No extra simulation factor: state renumbering and bridge are directly in one fixed physical transition table. Therefore combined raw-to-row-certificate time is O(L^2+N^2)=O(L^2 log^2 L), worst-case Theta(L^2 log^2 L) on empty-constraint normalized inputs. Space O(L+N)=O(L log L). Malformed binary input inherits B3's O((L+1)^2) bound and never enters the bridge. This is asymptotically subcubic for the fixed-path family, not a finite original-selector clock guarantee, not a polynomial-time algorithm for unrestricted SAT. Physical original Boolean witness translation is excluded; the original interpreter expects n bits at the halt head, and the tested forced certificate has only seven. Some other row certificates may accidentally supply n bits, so no blanket original witness-interface refusal is asserted.

## Governance and next bounded mission

ADVANCE same-machine raw-to-row-certificate composition and isolation. PRESERVE exact B4 producer and REX-020 worker; retain producer data. DECOMPOSE physical certificate-to-rank recovery, pin recovery, original Boolean witness emission and clock audit. RETIRE treating the prepared grammar, row certificate, or asymptotic bound as original selector admission. STOP after these bounded integration tests. All four global routes and all six overarching Omega obligations remain open; no new original stage admission or P versus NP result.

Next F038-REX-022B6: implement physical original Boolean witness recovery, including traversal back across the blank isolation gap, mapping selected row bits to physical bag tuples using the preserved masks, consistency of overlapping variables, original X/Y/pin/guard layout, and canonical n-bit output on the same tape. Require an exact original verifier replay and full composed resource accounting. No promotion until the actual original witness contract and clock have been verified.

Reproduce:
```sh
for suite in small three controls; do
  node mathos/research/f038_rex_ternary_handoff_audit.js "$suite"
done
node mathos/research/f038_rex_ternary_handoff_replay.js
node mathos/research/f038_rex_ternary_handoff.js --descriptor > /tmp/handoff.desc
python -m mathos.research.f038_rex_ternary_handoff_codec /tmp/handoff.desc
```

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
