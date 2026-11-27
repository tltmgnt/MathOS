# F038-REX-024D5E — Explicit whole-machine source-level envelope and eventual restricted cubic threshold

Parent ffacc50caae015ff47d0b2939234729e2f87854a. Research branch only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## Native and prior evidence

[Parent Proctor run 45934056192](https://github.com/tltmgnt/MathOS/actions/runs/45934056192), job 140293064394: explicit worker envelope, governance gates, exact quotient generation and native interpreter compilation steps passed. The native domain-four halt and cutoff step is still running at the time of this audit. No native m4 completion claimed; do not mark the entire parent workflow passed. The exact D5C direct physical preparation CI and D5D source-level audit establish the existing predicted m4 clock 299944027294, head 568801, span 574997 and 69-bit witness. No new machine is synthesized here; the existing exact clock-preserving quotient has fixed descriptor length ell=928445994.

## Source-level resource argument

Scope: legitimate normalized selectors with m>=2, nine groups, and an admitted width-three primal graph. The established C1/D2C producer invariants, worker correctness, D5C storage and D5D virtual-time arguments are premises. The following conservative numerical accounting extends those source-level arguments; it is not a machine-checked bound or certification of all individual executions.

Let n=19m-7, L=n+1+2n^2+8*binom(n,3), b=ceil(log2 m), H=ceil(log2 L), B=9m+36m^2+84m^3 and S=2(b+m+B+131). Then m^3<=L, b<=H, L>=37914, and S<=4L: each of the B mask positions and m pin positions corresponds to a distinct selector slot, hence B+m<=L-n-1; b<=n and 131 is constant. These estimates use the legitimate normalized layout, not arbitrary malformed inputs.

### Producer (including mask loader)

The physical selector/workspace separator advances from the input left boundary to L-1. The five binary lanes plus fixed group suffix occupy 5*bit_length(m)+15 cells (at most L). The accumulated prefix has at most L cells. The blank-separated blocks contain at most B+m+36 data bits plus 166 delimiters and constant boundary cells (at most 2L). Deposits move their farther-left suffix by one cell, with no growing duplicate copy. The planner uses ten frames (850 cells), and the loader appends at most S bits. During shuttles only a temporary blank marker is inserted and restored. Even allowing setup and guards, the entire producer visited interval is at most D=16L.

For the accepted path, use the following coarse charging scheme, derived from the actual producer source rather than a measured fit:
- A workspace column scan reads one column, optionally rewrites it, and rewinds; each traversed column contributes at most three passes plus a constant extension. A group read/set/classification is a bounded walk of at most 15 bits with a return. A shift traverses the workspace, moves it one cell and returns. A deposit traverses the workspace/prefix/blocks, shifts the suffix, and returns by counting delimiters; a query traverses a prefix and returns. Each such macro fits 16D transitions, including fixed control entries/exits.
- Header scanning consumes one bit per shift and increments one binary lane at the fixed count positions. For clause scanning, each sign bit is consumed once, and at most one support advance or width transition is charged to each bit. A support advance performs at most a fixed sequence of nextCoord (group read, rank comparison, increment or clear and group set), copyCoord (one rank copy and bounded group copy), and classification tests (at most four rank comparisons). The longest advance-three overflow resets the suffix coordinates and performs only a fixed number of these calls. The first optional bit can deposit one mask and query/set at most three edges; a pin first bit deposits one pin. Including sign shifts, startup, final scan, and all fixed dispatch paths, 128 macro charges per input bit plus one extra iteration are conservative.
- Copy the 36 graph flags, then run the exact finite DFS. At most sum_{j=0}^9 9!/(9-j)! = 986410 < 2^20 distinct partial ordered paths are visited. Each successful push visits a new partial path; each failed return resumes its parent's search without retrying an already tried vertex. Across the tree there are at most twice this many search sweeps (initial plus return). A search sweep tests at most nine active flags, nine tried flags and 72 incident edge flags, plus choice writes. A push copies 45 graph/active bits via fixed walks, fills at most 28 edges with two tests and one write each, deletes at most eight edges and deactivates the vertex. Pop erases 84 cells. Counting two searches, push/pop and ascent per node gives fewer than 1024 addressed macro calls per node; each fixed-frame call (including the cross-frame copy of one bit) takes fewer than 1024 transitions. Thus the DFS costs less than 2^40 transitions independently of m. Root success header completion visits nine records, each reads eight possible neighbors, writes a fixed extension and scans at most nine later records then returns. Graph copy, header completion and fixed overhead together fit 2048 charges of 16D.
- Direct loader visits one workspace lane bit at a time, trims high zeros, and copies the B+m mask/pin bits and 130 field delimiters. The number of bit/field operations including trim and finalization is at most 3L. Each operation makes only a fixed number of counted-blank or contiguous scans and writes at most two output bits (fit 16D). All source scans and restore paths stay in D.

The sum 16D*(128(L+1)+2048+3L)+2^40 is bounded by P=2^21 L^2 using L>=37914. These intentionally loose macro ceilings rely on the admitted-path control-flow/layout invariants; no automated all-state macro-count certificate is claimed. Malformed input runtime is not included.

### Physical initialization bridge

Its literal source has 851+S<=5L symbols. The initial segmented encoding has 5*(1+3*61+851+S)<=30L bits. This is the complete fixed 61-tape initial layout, including left sentinels, spare blanks and separators. There are 840 frame-bit copies, ten frame-delimiter copies, S stream-bit copies, and fixed initial/final append operations (at most 5L+2 append shuttles). Each shuttle makes one outward and one return scan over the source and growing encoding, with bounded extra dispatch/write steps (including the two longer fixed-word appends); fewer than 128L transitions per shuttle. Hence I=2^16 L^2 bounds the bridge. No host transfer is counted as physical execution.

### Worker and physical projection

Use the D5D source-level bound N<=512(b+1)m^4 logical blocks and W=2^39(b+1)^3 m^8 transitions. The encoded worker span is at most 5N. At output projection, the scan from G through the witness segment, the temporary-mark/append/restore round trips and final rewind operate on a contiguous encoded region plus at most n unencoded output bits. Each copied bit takes a bounded decode/mark/restore path and at most two round trips over 5N+n cells; initial/final scans fit another such charge. A conservative total 16(n+1)(5N+n+1) is <= O=2^20(b+1)m^5, since n+1<=19m. The UNSAT case merely scans and halts blank. Here O denotes a numerical phase bound, not big-O notation.

The total bound U=P+I+W+O and visited-span envelope 16L+5N+n+4 include the preserved producer checkpoint, worker region and output. The quotient preserves the original physical clock. Since m^3<=L, b<=H, L>=1, the entire numerical upper envelope satisfies

```
t <= U <= 2^40 (H+1)^3 L^(8/3).
```

This is an explicit conservative *source-level* resource conclusion conditional on the stated invariants and previous worker derivation, not a verified bound for unrestricted SAT or all raw strings. No acceleration of the machine is claimed.

## Exact eventual stage arithmetic

The original stage s3=3H lists this fixed descriptor and allots t_budget=2^(3H-ell), provided 3H>=ell. From L<=2^H, it suffices that

```
ell+40+3*ceil(log2(H+1)) <= H/3.
```

Set H0=3*(ell+40+96)=2785338390. This lies between 2^31 and 2^32-1, so ceil(log2(H+1))=32 throughout [H0,2^32-1]; the inequality holds there. On each subsequent interval [2^k,2^(k+1)-1], k>=32, the ceiling logarithm is k+1, and it suffices to check its left endpoint. At 2^32 the inequality holds; each successive left endpoint increases by 2^k while the required RHS for 3*(ell+40+3*ceil(log2(H+1))) increases by only 9. Therefore all H>=H0 satisfy the sufficient inequality. No huge integer 2^H is materialized.

Thus, subject to the source-level resource premises, all supported SAT inputs with ceil(log2 L)>=2785338390 (equivalently L>2^2785338389) admit the fixed quotient at the cubic stage. This is the first integer H satisfying this particular coarse sufficient inequality in the threshold's dyadic interval, not an optimal admission threshold and not a guarantee of practical coverage. The enormous fixed description is the dominant obstruction. The proof does not cover finite exceptions below H0, structural refusals, unrestricted formulas, or the earliest successful universal stage. The exact listing-only threshold is H>=309481998. The original built-in independently suffices for m2,m3 by its exhaustive bound; it does not cover all m4 inputs at stage 57 by that argument.

## Executed arithmetic and phase regression

New BigInt auditor performs the simplified envelope comparison by cubing both sides, avoiding fractional arithmetic and floating logs. Tested 10017 domain sizes (all m=2..10000 plus three neighbors of six powers from 2^20 to 2^1024) and 195 threshold boundary values (H0 neighbors and neighbors of 64 dyadic boundaries). All passed; arithmetic tests are not executions at huge input lengths. Independently reexecuted four prior phase audits (three m2 cases and forced m3) with exact original-clock/head/span/witness checks and four phase-envelope assertions per case. The m4 bounds were checked against the actual D5C CI direct-phase ledger, not a fresh full native execution. All five rows pass:

| m | Entire numerical clock envelope | Phase-accounted principal clock(s) |
|---:|---:|---:|
|2|4234702112423936|825112955;1297519076;665681141|
|3|154040819887177728|72540199790|
|4|1370325896581349376|299944027294|

The bound is deliberately very loose. No observed discrepancies. The new regression workflow runs fresh phase audits and direct m4 preparation plus governance checks, without duplicating the still-running long parent native replay. Current-head CI is unconfirmed.

Next D5F: confirm native m4 full replay and cutoff, independently scrutinize/automate source-level macro ceilings and the worker capacity/time derivation, and investigate description or algorithm reductions for the finite regime. Main and PR #248 unchanged; global routes 0/4, Omega obligations 0/6.

Reproduce:
```sh
p=mathos/research/f038_rex_width_three_cubic_bound_audit.js
node "$p" arithmetic
for case in empty edge-SAT edge-UNSAT m3-forced; do node "$p" "$case"; done
node mathos/research/f038_rex_width_three_domain_four.js direct
```
