# F038-REX-024D4A — Direct physical initialization and composed constructive worker

Parent acc9a5073ce4c4e881e10bce4a317b0039acfa81. Research branch only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE. [D3B2 exact-head Proctor 45920732360](https://github.com/tltmgnt/MathOS/actions/runs/45920732360) passed.

## Interface

The new packed single-tape transition table begins on the original raw selector. It preserves the direct D2C producer, appends a charged physical initialization region, and enters the previously tested compiled 61-tape witness worker on the same physical tape. The only runtime interpreter operation is a packed transition read, cell write, head move and state change. The phase clocks and terminal tape extraction are observer-only. There is no host-mediated copying, reinitialization, command stream or input-dependent compilation in the composed computation.

At accepted D2C completion h is the blank checkpoint root separator, ten 84-bit frame words occupy the following 850 cells, and the contiguous 131-field mask stream follows. Let b be the blank immediately after that stream. The initializer writes a contiguous binary segmented worker encoding starting at b+1, leaving all original cells unchanged. The two input virtual tapes contain the literal 851-symbol header suffix (H at h and b for each frame delimiter), and the literal encoded mask stream. All other virtual tapes initially contain a marked left sentinel and an unmarked virtual blank. The fixed five-bit codebook agrees with the witness worker. The physical head arrives at the first bit of its global sentinel G.

## Charged bridge construction

Append G and the first 19 empty segments, followed by the header segment's marked left sentinel and encoded H. For each of ten frames, copy its bits left to right. Temporarily blank one bit and retain its value in finite control. Cross the remaining original frame separators and contiguous stream to b, scan the growing encoding, append that bit's unmarked-symbol code, and return across the stream and known number of frame separators. Scan left from the current frame's right delimiter to the temporary blank, restore the bit, and move right to the next source bit. The marker is inside the frame, hence not confused with the counted separators. At each frame end append an encoded b; the last also closes the header segment and opens the stream segment. For the stream, repeat the temporary marker copy and restore, returning from the original stream-end blank. Finish by appending the stream's virtual blank and separator and the remaining 40 empty segments, ending with E. Rewind the contiguous encoding to b and step right to G. Each copy is charged. The procedure relies on genuine admitted producer output and does not authenticate arbitrary forged checkpoints.

Induction over copied symbols proves exact initialization and preservation. All source separators are restored; the boundary blank b remains outside the worker encoding. The worker's global sentinel is its left boundary, so moving its entire initialization region by a fixed physical offset changes neither its transition sequence nor its virtual computation. The original left checkpoint is outside the worker's visited region. This is not a full original output interface: on accepted completion the physical head is at encoded G, not at the first unencoded Boolean bit. UNSAT leaves the virtual output empty but the physical head is not blank. Inherited normalization refusal behavior is also not yet an original witness-safe interface.

## Composition

Fork the direct loader compiler only to distinguish its successful completion state from the shared structural refusal halt. Its dedicated bridgeReady transition is replaced by a stationary move to the new bridge start. Relocate packed successor state IDs for the producer, initializer and worker; all other actions are unchanged. Separate initializer success and error exits; only success enters the worker. Producer structural refusal bypasses the bridge. The actual joined table is generated before any selector is supplied.

| Component | Nonhalting states |
|---|---:|
| Producer with dedicated exit |577884|
| Physical initializer |1768|
| Constructive worker |10767877|
| Composed table |11347529|

There are 34042587 packed transition entries. The calculated original-format bit length is 964539969; the full composed descriptor has not been serialized or independently decoded. This is not a quotient or finite-stage admission result.

## Executed verification

The bridge-only table has 579652 states. Two m=2 original-selector instances (empty and nontrivial triples) physically generate exactly the 14855-bit initialization, compared to an independent encoder; source preservation agrees with the baseline D2C observer after normalizing one extra leading blank in its snapshot. Each bridge takes 48370247 transitions. The structural K5 refusal preserves its exact 27879500 transition clock and bypasses the initializer. Six budget controls (0,1,100,104551137,104551138,152921384) return TIMEOUT without publishing a configuration; exact budget completes. These bridge-only executions predate the separate success/error-exit correction, which preserves the successful transition path; the final joined table was subsequently tested on three fixtures.

| Fixture | Producer | Bridge | Worker | Total | Physical span |
|---|---:|---:|---:|---:|---:|
| Empty |104551138|48370247|672161844|825083229|58929|
| Nonempty-child edge SAT |104556548|48370247|1144561610|1297488405|59875|
| Empty-child edge UNSAT |104556548|48370247|512737138|665663933|58905|

All three composed runs start on their original raw selectors; total 2788235567 charged single-tape transitions, including 145110741 initialization transitions. The worker clocks equal the independently executed and CI-passed D3B2 clocks exactly. The two 31-bit SAT outputs (1010101010101010101111111110000 and 0110101010101010101111111110100) pass the original Boolean verifier after terminal decoding; the UNSAT case emits no virtual witness. The preserved source and worker input tapes agree with baseline D2C. All three halt at physical position 40701 relative to the raw input origin. The attempted combined SAT plus standalone-worker differential replay exceeded the interactive timeout; all three composed cases were then executed separately with the exact prior clocks, output and source assertions. Full 61-tape/head comparison via fresh standalone replay is included in the native workflow but not claimed completed here. No observed disagreement on the completed tests. Current executions used JS V8. Domain-three bridge, full serialized descriptor and native codec checks remain open; current-head CI unconfirmed.

## Resource argument

The preserved producer uses O(L^2) transitions and O(L) space. Source and initialization sizes are O(L) because the mask stream has O(m^3) bits and fixed frame/tape counts, with L=Theta(m^3). Each source-symbol shuttle moves O(L) cells and appends O(1) bits. Thus the added physical initializer costs O(L^2) time and O(L) span. The already single-tape worker is not re-simulated: it has O(L^(8/3) log^3 L) time and O(L^(4/3) log L) space under the fixed-tape resource argument. Therefore the composed restricted computation through encoded witness output has derived time O(L^(8/3) log^3 L); output projection and witness-safe rejection must still be implemented and audited before original interpreter admission. No numerical finite cubic threshold or unrestricted SAT complexity claim follows.

Next 024D4B: add charged physical unencoded witness projection and blank refusal/UNSAT exits. Verify original halt-head semantics and independently decode the original descriptor. Main and PR #248 unchanged. All four global routes and six Omega obligations remain open.

Reproduce:
```sh
for suite in bridge empty sat unsat; do
  node --max-old-space-size=6144 mathos/research/f038_rex_width_three_physical_bridge_audit.js "$suite"
done
```
