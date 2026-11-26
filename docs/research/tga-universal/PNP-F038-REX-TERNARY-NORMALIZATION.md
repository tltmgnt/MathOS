# F038-REX-022B2 — Fixed ternary normalization classifier and validated selector checkpoint

MRA-X 2.0 + RE-X; MRA-X Omega Phase III evidence. Parent REX-022B1 2cf45683aa6ecc9d8b5cba939d719f58e612a879. Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

## Scope

A new fixed ternary descriptor validates the original SEP-003 raw normalized selector family and tests placement in the fixed REX-022A seven-bag path. It reads raw input directly; n, m, clause coordinates, required-clause membership, sign checks and the structural refusal flag are computed by physical transitions. The descriptor is generated once with no input-dependent state construction. On accepted input it retains the exact selector payload and a small binary workspace in a canonical continuation layout on the same physical tape. This is not the full producer: no forbidden-mask records, bag records, worker handoff or Boolean witness are produced.

Three canonical halts: NORMALIZED_FIXED_PATH (head at blank, retained payload/workspace), OUTSIDE_NORMALIZED (single 0 at head), OUTSIDE_FIXED_PATH (single 1 at head). TIMEOUT is a separate simulation result. OUTSIDE_NORMALIZED has priority if any malformed clause occurs even after an unsupported cross scope. Neither structural acceptance nor structural refusal decides SAT. Binary input is required; nonbinary host strings are refused before execution.

## Physical invariants and exact classification theorem

A raw header is 1^n0. In finite control count 0..30 exactly, then represent 31+(n-31 mod 19) using states 31..49. Increment binary m at header lengths 12,31,50,... . Only state 31 accepts the terminator, enforcing n=19m-7 and m>=2. Subtract one and copy-minus-one to obtain M=m-1, Y=m-2.

The moving workspace consists of a binary column region (M,Y,A,B,C), least significant column nearest the right, and a 15-bit suffix encoding three 5-bit group words. A,B,C are zero-based local ranks. Groups 0..8 represent the nine X groups (size m); groups 9..17 represent Y groups (size m-1); group 18 is P (size m); groups 19,20 are the two singleton guards. These sizes sum to n. Group words are big-endian. A coordinate increments its rank unless it reaches the group's bound, then resets its rank and advances its group. The last guard overflows without advancing. Copying a coordinate copies both rank and group. Consequently this representation is order-isomorphic to the original variable index sequence. Unary, binary, ternary nested loops traverse every increasing support in lexicographic order, sign codes ascending with negative before positive.

The classifier reads group words using fixed decision DAGs (equivalent subtrees share states), then uses finite-state binary scans for rank equality, constant comparison and successor checks. Let r(x) be the local rank and X_g, Y_g the group. Required clauses:

* Within X_g, every binary all-negative support (at-most-one).
* For a binary support X_g,Y_g, sign (-,+) is required iff both ranks are zero or r(X)=r(Y)+1.
* For a binary support Y_g,Y_g, sign (-,+) is required iff the second rank is the first plus one.
* For a ternary support X_g,X_g,Y_g, sign (+,+,-) is required iff the ranks are (0,1,0).
* For a ternary support X_g,Y_g,Y_g, sign (+,+,-) is required iff the second Y rank is the first Y rank plus one and the X rank is the second Y rank plus one.
* The last Y of each group is a required positive unit; the two guard units are required negative.
* A support P,G1,G2 has eight signs. The first four must have identical bits b, the last four identical bits 1-b. This accepts exactly one polarity of four lifted pin clauses and enforces all lifts, including absent ones.
* An all-negative support in distinct X groups is optional. It is covered iff the difference between maximum and minimum group indices is at most two, equivalent to containment in some fixed triple (j,j+1,j+2), j=0..6. Selected optional supports outside this span set a persistent finite-control flag; unselected ones do not. Every other selector bit must be zero.

These cases are disjoint and exhaust the normalized grammar: the OR-chain rule for the first link uses (X0,X1,Y0), and for every later link uses (X_{j+1},Y_{j-1},Y_j) (with local rank indexing). The binary implications and final Y unit are exactly the remaining OR-chain clauses. Thus the required clauses, optional negative cross clauses, and lifted-pin selection are precisely those accepted by the strict inherited decoder. Address enumeration consumes every bit once, rejecting missing/extra bits. Therefore for any finite contiguous binary raw input the abstract machine accepts NORMALIZED_FIXED_PATH iff the strict normalization conditions and fixed-path support coverage hold. A normalized input with selected outside scopes returns OUTSIDE_FIXED_PATH; otherwise malformed input returns OUTSIDE_NORMALIZED. This is an informal constructive correctness proof, not mechanized certification.

At each consume step the raw bit is blanked, the contiguous workspace moves one cell right by a backwards copy, and the consumed bit is retained at the former left boundary (header bits are not retained). Inductively the untouched suffix, all counter bits, and the original-order payload prefix are preserved. At the accepted halt, M,Y have their bounds, A,B,C are zero, group words are (19,20,20), and the head is on the final separator at original position L-1. The tape has exactly [payload][blank][workspace][blank at head], with blanks elsewhere. The payload is the original selector sequence, not a generated factor table. On rejection, cleanup erases the raw suffix, workspace and preserved prefix before writing the single result bit. Internal BROKEN states denote violated workspace invariants; the canonical-halt audit guards against extraneous tape content.

## Resource bound for the emitted descriptor

Let L=n+1+2n^2+8*C(n,3) for valid shape. The active workspace contains exactly 5 bit_length(m)+15 bits after the header. Header increments and support enumeration use a bounded number of scans over the workspace per consumed bit; group word reads and decision DAG traversal have fixed maximum length. Each shift takes Theta(log(m+1)) transitions, as do the counter scans in the upper bound. Hence T=Theta(L log L) and active workspace O(log L) for valid pool-shaped inputs that traverse the entire pool. Malformed inputs can terminate early; for arbitrary finite binary raw input of length L, header processing, consumed-bit work and cleanup cost O(1+L log(L+2)). The total tape span is O(1+L+log(L+2)), including the original payload. Time for physical mask deposition, bag production, elimination and original witness reconstruction remains separate. No original cubic stage admission: the descriptor is fixed but much longer than tested stage indices and cannot output an original n-bit witness.

## Executed evidence

The compiler emitted 40333 nonhalt states and 2460317 descriptor bits. All primary runs used the serialized-and-decoded transition table. Every visited clause address was compared against the inherited pool generator, including physical bit position and raw bit; every bit's required/optional/forbidden/pin category was compared against the independent inherited fixed-clause list and cross-scope test. The read-only observer does not control physical execution. The entire retained payload and final workspace layout were checked.

| m | Raw bits | Addresses | Physical transitions | Work bits |
|---|---:|---:|---:|---:|
| 2 | 37914 | 37882 | 5139764 | 25 |
| 3 | 161851 | 161800 | 21419492 | 25 |
| 4 | 428744 | 428674 | 66390634 | 30 |
| 5 | 893465 | 893376 | 137672288 | 30 |

Four principal inputs: 1521974 raw bits, 1521732 addresses, 230622178 transitions. Four additional m=2 payloads exercise all pin patterns, empty constraints, contradictory unary constraints, and dense or partial dense in-path cross clauses: 151656 raw bits, 151528 addresses, 20559056 transitions. Two are known UNSAT yet correctly return NORMALIZED_FIXED_PATH. Combined eight runs: 1673630 raw bits, 1673260 per-address classification comparisons, 251181234 physical transitions, zero observed address/classification/payload disagreements. Classification counts across eight runs: 682 mandatory non-pin bits, 24222 optional cross bits (inside and outside scope), 1648180 forbidden bits, 176 lifted-pin bits. Counts describe bit positions visited, not distinct clauses or selected constraints.

Fifteen additional targeted controls: 13 malformed and two normalized fixed-path refusals. The all-zero valid-shape input rejects; missing mandatory one-hot/OR/guard/pin clauses and extra selected clauses reject; malformed later pin lifts override earlier structural refusal. Both a binary scope (0,8) and a ternary scope (0,1,8) are outside the fixed path, and explicit original Boolean witnesses verify their satisfiability. Seventy further mutation cases (123822076 transitions) remove each of 55 mandatory selected clauses at m=2 individually, add each of eight absent opposite-pin bits individually, select both full pin signs, or insert one of six illegal clauses. All rejected. Some mutations overlap targeted controls. Four cutoff checks plus an exact and one-step-short halt pair passed.

A separate JS sparse Map tape interpreter with independently written descriptor decoding and step loop replays one normalized UNSAT input and one satisfiable outside-path input: two completions, 10317439 transitions, payload/rejection equality and one-step-short timeout verified. Headline 261498673 transitions = eight dense-table runs plus two sparse replays; excludes mutations, targeted controls and timeout/exact-clock repeats. All counts are simulated physical transitions, not hardware timing. No elimination-worker runs in this cycle.

Development: the candidate compiler initially constructed movement states inside a transition callback; factored out that construction before testing to avoid duplicate definitions across flag variants. V8 tests used inherited source at the exact parent. Native Node and original Python decoder/interpreter regression are added as remote gates but not executed here (container GitHub DNS access failed); independent formal review and exact-head CI remain unconfirmed.

## Governance and next bounded mission

ADVANCE exact physical normalization and fixed-path structural recognition, validated payload checkpoint, and all-address semantic comparison. PRESERVE REX-022A charged multitape producer, REX-022B1 physical address descriptor, REX-020 worker and exact width-two theorem. DECOMPOSE physical mask deposition, bag serialization, same-machine worker handoff and witness translation. RETIRE treating shape or normalization as SAT, treating fixed-path coverage as general width-two coverage, or counting simulator observer operations as machine work. STOP after classifier audit. All four global routes and six formal Omega obligations remain open.

Next: F038-REX-022B3 — physically deposit local forbidden-tuple masks from the validated raw payload, with exact address/rank ordering and charged tape accesses. Require byte-for-byte mask equivalence with REX-022A, including zero bits, duplicate bag placement and rejection controls. No host-generated factor tables or uncharged storage operations.

Reproduce:
```sh
node mathos/research/f038_rex_ternary_normalization.js
node mathos/research/f038_rex_ternary_normalization.js --independent
node mathos/research/f038_rex_ternary_normalization.js --descriptor > /tmp/normalization.desc
python -m mathos.research.f038_rex_ternary_normalization_replay /tmp/normalization.desc
```

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
