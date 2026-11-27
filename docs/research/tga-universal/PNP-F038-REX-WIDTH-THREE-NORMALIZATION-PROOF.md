# F038-REX-024D5S — FIFO normalization, compiled classifier verification, and sparse reference storage

Parent c03ff740c931dcb1158802ad4112aa2d55f0eeff. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5R closure and architecture decision

Exact-head [Proctor 45992258144](https://github.com/tltmgnt/MathOS/actions/runs/45992258144) completed successfully. Other exact-head workflows also succeeded. D5R's adaptive packed-prefix representation prevents multiplicative expansion but regressed against D5Q joint on every comparative producer benchmark. D5S deliberately uses D5Q joint as the physical performance baseline, not D5R adaptive storage. It preserves joint's original packed constraint code and thus does not inherit D5R's additive-two-cell storage guarantee.

## Single-pass FIFO workspace relocation

The prior batch controller validates a mandatory selector word and moves each workspace bit right by k cells using a k-step forward/backward shuttle. Here k is fixed (2,3,4,7,8). The new batch controller validates the entire word first, returns to the current right workspace delimiter, scans left to the consumed-prefix separator, then traverses right once. At the old left delimiter write the first validated bit; during the first k workspace cells write the remaining k-1 validated bits followed by a blank separator while retaining their displaced bits in finite control. The FIFO now contains exactly k displaced binary symbols. For each remaining workspace cell, write the oldest symbol and append the original symbol to the queue. At the old right delimiter, flush the remaining symbols into the validated selector positions and write a new right delimiter. Return to the next coordinate controller at that delimiter. The earlier single-cell shift remains for k=1 and optional bits.

For workspace width w>=k, the invariant after each write is that the already emitted tape equals the desired shifted workspace prefix, the unread workspace is unchanged, and the queue contains the next k old workspace symbols in order. The flush finishes the exact relocation. The retained prefix and raw tail are unchanged except for the validated word being moved into the prefix; no raw selector grammar change. Invalid words return to the old head in the inherited rejection cleanup state without any writes. On a valid entry, the transition count is 2w+3k+4 (one initial move, k validation reads, k back moves, one left entry, w left scan moves, one separator write/move, w right scan moves, one old-right-delimiter flush, k-1 remaining flush moves, one terminal write; count verified by compiled tests). The conservative bound 2w+3k+8 covers the path. With k<=8, this is a constant-factor linear relocation in workspace width, rather than repeated per-bit k-cell shuttles. The physical producer still traverses the retained selector prefix for deposits and preserves the entire selector; no prefix elimination.

## Compiled-transition macro verification

The independent auditor uses the actual ternary transition table and diagnostic state names. All twelve reachable multi-bit mandatory batch entry paths (lengths 2,3,4,7,8) tested across five workspace widths and 64 patterns each: 3840 valid relocations. Verify exact full tape, head, unchanged prefix/tail, and bound. Another 580 invalid suffix cases (wrong bit or blank at each position, five widths) enter clean0 with original tape/head intact. Maximum observed excess over 2w: 28. These are local tests, not an exhaustive all-width proof. The FIFO invariant gives the source-level generalization.

For m=2,3,4, independently derive each variable's group/rank from the normalized clause pool and fixed clause set. For every combination of one, two, or three variables, run the actual compiled classifier at class1/2/3, verify required/none/optional/pin dispatch against independent fixed clauses and group membership, unchanged tape/head. Then run the compiled advance1/2/3 path on the same layout and compare the next lexicographic combination (including arity changes and done), checking bound lanes and boundary preservation. Results: 80675 classifier cases and 80675 advance cases; maxima 222 and 1146 transitions respectively. These test actual transitions for all combinations at three domain sizes, not all domain sizes or every possible malformed layout. Inherited arithmetic and all-input macro premises still conditional.

## Forbidden-position gap reference (host only)

A separate executable reference codec stores only increasing forbidden positions through positive gaps from previous position -1. Encode each positive gap g with Elias gamma: floor(log2 g) zero bits followed by binary g. Given mask length n and an externally known field boundary, compare the concatenated gamma payload length G with n; choose a sparse mode bit 1 followed by G bits if G<=n, otherwise mode bit 0 followed by n literal bits. Empty forbidden set has just the sparse mode bit. Decode cumulatively, rejecting truncated gamma codes or positions outside n. For each mask, encoded length = 1+min(G,n) <=n+1. This excludes the external length and boundary metadata; a physical implementation must supply them. No online physical gap counter, producer insertion, dense conversion or worker decoder is implemented here. The host model does not contribute to physical performance or resource claims.

8191 exhaustive binary masks lengths 0..12 and 24 seeded density/length examples (8215 total) round-tripped; 3569 sparse, 4646 dense, 2125 strictly shorter than n+1, seven malformed code examples rejected. Sample n=1024 with 12 forbidden entries used 135 bits, with 51 used 386, with 248 used 909, and with 496 used literal fallback 1025. These examples illustrate density-dependent encoding, not universal savings or a physical resource theorem.

## Architecture and performance

| metric | D5Q joint bounded | D5S FIFO bounded | D5S FIFO full |
|---|---:|---:|---:|
| producer states |285286|287874|287874|
| original physical states |2584418|2587006|2584726|
| quotient states |1900328|1901324|1899601|
| descriptor bits |144424932|144500628|144369680|
| transition checks |7753254|7761018|7754178|

Both quotients remain below 2^21. Unchanged 20-tape four-bit worker, bridge/projector and canonical run stream. The producer is slightly larger; no descriptor compression achieved.

Seven canonical selectors (21 actual producer comparisons), all streams match independent canonical encoding; five malformed inputs refused. FIFO improves all seven measured producer cases over both compact batch and joint.

| fixture | compact batch | joint | FIFO |
|---|---:|---:|---:|
| empty m2 |33762697|33551661|31570963|
| chain m2 |34691771|34484571|32503873|
| third-rank m3 |309040159|307377783|298878185|
| all-active m2 |59280361|59344113|57363415|

## Conditional resource accounting

Retain D5Q joint allowances N<=S+35m+1479<=2S, T<=49152S bounded or 49152mS full, W<=(20N+12)T+6, P'=4P+32L with P=256L(131L+2176)+2^40. The FIFO relocation preserves workspace extent and decreases local shifting cost, with inherited macro slack; the deposit and stream paths are unchanged. Total conditional t<=2^18 L^2 bounded, t<=2^14 L^(7/3) full. Sufficient cubic admission thresholds 144500646 and 216554541; 20034 arithmetic evaluations passed. No practical measured cubic admission or complete all-input proof. Full GAC and radius-two repair are incomplete SAT search.

## Exact physical evidence

Original raw selectors, pins [0,0]:

| fixture | D5Q joint | D5S FIFO |
|---|---:|---:|
| bounded chain |337754112|335773414|
| full all-active |1170974756|1168994058|

Chain: producer 32503873, bridge 723079, worker 302074888, projection 471574, head 45782, span 46577, witness 0101010101101010101111111110000. All-active: producer 57363415, bridge 10958635, worker 1099923738, projection 748270, head 51272, span 52301, witness 1010101010101010101111111110000. Both original and quotient replays validated witnesses, head/span and clocks; both exact one-short cutoffs 335773413 and 1168994057 TIMEOUT without witness. Registered 12 physical jobs, two independent native descriptors, independent macro/reference audit and governance; current-head success not claimed until confirmed.

Next: physically implement a bounded gap-count deposition/decoding prototype with dense fallback and account for all delimiters/counters; independently verify complete header and normalization composition costs; confirm D5S native/physical matrix. No main or PR #248 edits.
