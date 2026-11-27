# F038-REX-024D3A2 — Compiled canonical mask routing and local relation generation

Parent fd0496a7b2ce4af9f796e0f5aea1c18b85c0c5a4. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Prior exact-head [D3A1 Proctor run 45912592731](https://github.com/tltmgnt/MathOS/actions/runs/45912592731) passed.

## Implemented boundary

A single finite instruction program now combines the one-bag D3A1 cursor with a router consuming three literal input tapes: the 851-symbol C1 header suffix (H and ten 84-bit frames separated by b), the complete 131-field encoded D2C stream, and a unary bag ordinal (0..8). The original 19 cursor tapes start empty. No host-derived scope IDs, coordinate masks, domain bound, bag arity, mask routing, rank counters or tuple lists are inputs. The audit transfers the actual suffix and stream from the observed D2C physical tape, mapping physical blanks in the suffix to b, and initializes the encoded virtual tape layout. This is still a host-mediated *literal tape transfer* and external bag selection, not an original raw-selector-to-worker bridge. The program handles one bag per invocation, and the input precondition remains a genuine admitted D2C checkpoint. It is not an arbitrary forged-checkpoint verifier.

Read the first D2C field by decoding 00/01 as bits and 10 as the field terminator, writing the bound to M. Test the accepted root-status bit, then skip 85 cells per unary ordinal and read the selected header's owner, neighbors, parent and seven presence flags into scratch W. Build a nine-bit bag bitmap B by bounded owner/neighbor ID walks (sentinel 9 is absent). Scan B to write one arity symbol per member. A seven-symbol slot-dispatch word identifies each owned scope. For each present slot, form its nine-bit scope bitmap S from the owner and corresponding neighbor nibbles. Scan B and S together in increasing group-ID order to append its four-bit projection mask (zero-pad unused coordinates). The same fixed canonical scope universe as C1/D2A is encoded in a shared finite decision tree. It resolves S to an eight-bit LSB-first mask ID on a scratch tape N. This is fixed finite control, not a host runtime lookup. Absent slots append 0000 and leave their mask tape empty.

For each present slot, rewind the literal D2C stream, skip bound and pin fields, then skip exactly ID mask fields using a physical binary countdown. Each skip parses the self-delimiting token grammar. Once the countdown is zero, decode the next field onto the selected slot's mask tape. Input suffix and stream remain unchanged. After all seven slots, clear W,B,S,N and the dispatch tape (temporarily reusing five cursor scratch tapes), then enter the unmodified D3A1 cursor IR. It generates the binary rank counters and unary domains, enumerates all local tuples and emits locally allowed rows. This is a single compiled router/cursor computation, not a host-mediated exchange of derived mask streams between two programs. There is no retained-relation controller or original Boolean witness in this stage.

Correctness for genuine D2C output: its frame/ownership invariant identifies exactly the seven potential owned scopes, and each present scope is a subset of the bag. Its mask stream is ordered by scope arity then lexicographic group IDs. The bitmap decoder therefore selects exactly the intended field. The joint bitmap scan projects the same sorted coordinates as the field's canonical rank order. The countdown invariant proves exact stream selection, and the previously tested cursor invariant proves the local allowed relation. All source cells are preserved. Malformed controls are limited; rank/mask length and header validity rely on the genuine-checkpoint precondition.

## Compiler locality revision

The unchanged D1A string-state compiler exceeded the JavaScript Map maximum size on the composed IR. The new compiler preserves the segmented virtual tape representation and logical transition definitions, but skips the rewrite sweep when a decoded logical symbol is unchanged. At the last bit of an aligned width-w block, a right logical move needs one physical right step; a stationary logical move needs w-1 left steps; a left logical move needs 2w-1 left steps. Shared finite movement tails perform exactly these distances, then enter the next block decoder. Changed symbols retain the original rewrite traversal. This is a semantics-preserving lowering by induction on logical transitions, with a different physical clock, not an exact clock-preserving state quotient. Its effect on the whole old compiler family has not been exhaustively audited. It allowed the composed machine to compile and execute:

| Metric | Value |
|---|---:|
| Generated IR instructions |11941|
| Reachable non-jump instructions |10120|
| Compact instructions |5217|
| Refinement rounds |612|
| IR homomorphism checks |10120|
| Logical state definitions |155490|
| Ternary nonhalting states |11765353|
| Packed physical entries |35296059|
| Calculated descriptor bits |1000055009|

The descriptor bit count is calculated from the original syntax. The entire 1.000055009-billion-bit descriptor was NOT serialized or independently decoded. All packed transition fields were range-checked; native Python decoding and full physical state quotient remain open. This remains a major finite-description burden. No numerical old/new clock speedup is claimed because the old compilation failed.

## Executed verification

Three genuine D2C selectors completed separately (104728446, 104759830 and 1191953378 producer transitions; total 1401441654). All 27 bag invocations were executed in both raw and compact finite IR, comparing exact primitive counts, all 22 terminal tapes and heads. The independent oracle derives expected configurations from the original selected factors and C1 frame metadata, and tests expected allowed rows directly against original clauses. All 485 routed mask bits, 273 candidate tuples and 190 emitted local rows agreed. Total 362684 charged virtual primitives. Five malformed IR controls rejected. Four of the same bag invocations were replayed in the actual compiled ternary table:

| Fixture / ordinal | m | Owner | Arity | Routed mask bits | Candidates / allowed | IR primitives | Ternary transitions |
|---|---:|---:|---:|---:|---:|---:|---:|
| four-bag triples / 0 |2|0|4|38|16/1|20969|158315656|
| four-bag triples / 8 |2|8|1|2|2/2|3588|18903682|
| greedy trap / 3 |2|5|4|38|16/12|34835|446806226|
| mixed / 0 |3|0|4|111|81/48|63710|479586556|

The greedy trap includes canonical ID 127 and an owner in a nonfirst sorted coordinate. All 22 terminal virtual tapes and heads agreed with the compact IR. Principal physical totals: 115 candidates, 63 allowed rows, 189 routed mask bits, 123102 virtual primitives and 1103612120 ternary transitions. Other 23 bags were IR-only. The independent sparse packed-table interpreter reproduced the ordinal-eight case at 18903682 transitions, span 14810, exact config and output 0;1;. Compared all terminal tapes and heads with the dense exact-budget run. Four physical cutoff controls (0,1,100,18903681) withheld completion; exact budget completed. Three physical malformed controls rejected. Combined principal and sparse replay transitions: 1122515802, excluding controls, smoke and separate D2C producer runs. All current tests executed in JS V8. No observed disagreements. Current-head CI unconfirmed.

## Resource audit and remaining composition

For fixed nine vertices and seven slots, the suffix/ordinal/bitmap work is constant in m. Stream length is O(m^3); at most seven scans skip at most 129 fields plus bound/pins, and the countdown has fixed eight-bit width. Thus routing costs O(m^3) virtual operations and cells. The cursor adds O(m^4 log m) time and space, including the O(m^3) source. The segmented simulator charges O((T+1)(S+1)) physical transitions for fixed alphabet and tape count, giving O(m^8 log^2 m) for the combined one-bag router/cursor. This excludes initializing the encoded tapes from the raw selector. It is not a measured whole-forest clock or an original witness admission theorem.

Next 024D3B: replace external bag selection with a fixed finite forest loop, retain each generated local relation in owner-indexed tape storage, then route actual joint separator masks and run the compiled semijoin on retained tapes. Preserve literal input and eliminate the remaining physical raw-selector transfer boundary before claiming original-format Boolean witness execution. Large-descriptor overhead and finite cubic-stage admission remain open. Main unchanged; all four global routes and six Omega obligations remain open.

Reproduce:
```sh
for suite in ir physical physical3 physicalTrap; do
  node --max-old-space-size=6144 mathos/research/f038_rex_width_three_mask_router_audit.js "$suite"
done
node --max-old-space-size=6144 mathos/research/f038_rex_width_three_mask_router_replay.js
```
