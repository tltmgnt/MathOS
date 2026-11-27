# F038-REX-024D5V — Persistent sparse local support projection

Parent 626c776159e88da02e95867ba480e20e9a6ffc7d. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5U closure

Exact-head [Proctor 45998880289](https://github.com/tltmgnt/MathOS/actions/runs/45998880289) completed all 15 jobs successfully, including two independent native original-format descriptors, twelve physical replays and audit/governance. The other exact-head workflows also succeeded. D5U remains a roundtrip integration checkpoint, not persistent sparse deposition.

## Direct persistent field projection

Implement a standalone nine-tape support projector. Three domain bit words A/B/C determine an independent Cartesian row budget (for binary scope use C=1). Let n=|A||B||C| and r=|A|+|B|+|C|. Input field Q consists of a mode bit followed by dense literal bits or gamma-coded positive forbidden-position gaps, with one blank field boundary. Domain lengths supply n; no separately trusted encoded length. On a sparse row, if no pending gap and Q is blank, all remaining rows are allowed. Otherwise parse the next gamma code into an LSB-first binary countdown when necessary; decrement once for each row, and classify that row as forbidden iff the counter becomes zero. On an allowed row whose three domain bits are 1, mark support on each of three support words. The rank odometer and support heads advance together and terminate at Cartesian exhaustion, not a gap-supplied output length. Require no pending gap and Q blank at that point; truncated gaps, extra payload, and gaps extending beyond the domain product refuse. A dense field reads exactly one bit per row. The input domains and coded field are read-only. No dense reconstructed mask is emitted. Support words have the same lengths as input domains. Output concatenates the support words with a 1 after each (not self-delimiting; known domain lengths required).

Proof invariant for genuine fields: after processing j rows, the payload cursor has consumed exactly the gap codes whose first row has been reached; a positive counter stores the distance remaining to the next forbidden row, zero means no pending code. For the current gap, decrements produce g-1 allowed rows then one forbidden row. If no gaps remain, the suffix is allowed. Dense path is immediate. Thus after each row support bits mark exactly the projection of allowed domain-compatible rows already visited. At exhaustion this yields the exact local supports, including empty support words on contradictory domains. This is a local support theorem by source-level induction; finite compiled audit below. No all-constraints fixed-point or global satisfiability completeness follows.

An early attempted full-worker rewrite had a syntax error and was not committed. The standalone prototype initially had a sentinel output-head error and a borrow-trimming error (decrementing a power of two incorrectly reported zero); both corrected before committing, with exhaustive retesting. In particular the countdown now explicitly tests emptiness after trimming the highest bit.

## Physical composition

Compose the D5T encoder (headerless variant; remove length counter work and header emission) with the support projector. Dense raw mask on tape 9, code on tape 8; reuse support tapes 4/5/6 as encoder scratch then clear them and the dense input before projection. The code is retained read-only through projection, rather than reconstructed as in D5U. Encoder compares gamma payload and original literal length physically and chooses mode. Emitted field length is 1+min(n,G) <= n+1 bits, plus blank. This bound assumes separately supplied domain lengths and a field boundary. Dense raw input and candidate coexist during encoding, and high-water physical allocation does not shrink merely because cells are cleared. Harness supplies segmented initial domains and mask; this composition does not yet start from the original raw selector, replace producer storage, or integrate multi-scope GAC/candidate repair. It still visits all n Cartesian rows, rather than skipping long allowed intervals algebraically. No true online forbidden-only deposition or retained-prefix elimination.

## Executed evidence

Independent Cartesian oracle tests all 256 domain-two ternary masks against all 64 combinations of three domain bit words, plus all 16 binary masks against all 16 pairs of domains, 90 seeded m=3,4,5 cases, and six named fixtures. Total 16736 direct support checks (8638 sparse, 8098 literal). 624 physical-encoder/logical-projector composition IR checks match the direct path exactly, including code and scratch cleanup. Eight malformed payloads refuse at IR level. Twelve actual compiled ternary replays (six direct, six composed) match independent exact clocks, halt head and full terminal physical tape. Direct IR 552 instructions, 111644 compiled states; composed IR 862 instructions, 153098 compiled states. These are standalone compiled machines, not original-format solver descriptors.

| field | forbidden | coded bits | direct clock | composed clock | direct N | composed N |
|---|---:|---:|---:|---:|---:|---:|
| n=8 all allowed |0|1|133268|251456|50|63|
| n=8 last forbidden |1|8|220266|484632|61|79|
| n=8 alternating |4|9|116632|435254|58|79|
| n=8 all forbidden |8|9|217580|515570|59|76|
| n=64 last forbidden |1|14|1493542|3226646|88|167|
| n=64 alternating |32|65|682782|6749504|132|291|

Direct clocks depend on both payload mode and supported rows. No comparable whole-machine performance improvement is asserted. Sparse countdown overhead may outweigh storage savings; composition still pays conversion cost. D5S stays preferred whole-solver baseline.

## Conditional local resource accounting

For genuine fields, b=ceil(log2(n+2)). Countdown and gamma operations have O(b) cost, rank/support odometer rewinds amortize to O(n+r) since each rank word of length d is reset at most O(n/d) times. Initialization/output O(r); encoder scans n positions, with total gamma candidate length <=2n. A conservative source-level allowance for either local machine is N<=8(n+r+1)+32(b+1), including high-water input, scratch, support words and segment boundaries, T<=512(n+r+1)(b+1), and inherited width-four lowering W<=(20N+12)T+6. All tested IR primitive counts and all twelve physical replay clocks/regions satisfy these allowances. They are conditional macro estimates, not mechanized universal bounds. For positive domain lengths r<=n+2, local physical complexity O(n^2 log(n+2)) (genuine fields); arbitrary malformed inputs not covered. Whole-selector conditional bounds and admission status unchanged. No complete SAT solver.

Registered new standalone local audit/governance workflow; exact-head completion unconfirmed at commit. Next D5W: integrate direct persistent field reader into actual FIFO original-selector worker with multi-scope propagation and candidate validation; supply physical framing, track counter reset across sweeps, verify both modes and original witnesses/cutoffs, benchmark before adopting; continue online deposition and all-input resource proof. No main or PR #248 edits.
