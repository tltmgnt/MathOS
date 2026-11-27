# F038-REX-024D5H — Conditional quadratic envelope and adaptive first-allowed witness controller

Parent c5fa9971cdfd4b740a294bff711423c9d5826105. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Prior physical closure

[D5G run 45938789950](https://github.com/tltmgnt/MathOS/actions/runs/45938789950) completed all seven jobs successfully, including exact quotient and one-step-short cutoff. In job 140308057290 the forced m4 raw selector halted after 10999810416 transitions with head 506166, span 512362, and the original valid 69-bit witness. Producer 6899458662, bridge 906416072, worker 3185014450, projection 8921232. This is a JS physical transition replay, not a new independent native ASCII decoder run. The previous general machine's native confirmation is [run 45934056192](https://github.com/tltmgnt/MathOS/actions/runs/45934056192). D5G m4 acceleration is about 27.27x (96.33% fewer transitions), compared to its confirmed 299944027294 transitions. D5G descriptor is 124696396 bits, slot 124696430, cubic stage 57.

## Uniform resource argument, accepted normalized inputs only

Use the unchanged producer and the D5E source-level macro ceilings as premises. The physical bridge skips the fixed 851-symbol header and copies the canonical contiguous D2C stream. Let m>=2, n=19m-7, L=n+1+2n^2+8 binom(n,3), H=ceil log2 L, b=ceil log2 m, B=9m+36m^2+84m^3, S=2(b+m+B+131). For genuine admitted checkpoints the stream has exactly S bits. The strict mode requires nine unary singleton domains. Adaptive mode selects the first allowed rank of every nonempty unary domain and checks all binary and ternary masks against that candidate. The same bounds apply on successful paths in either mode.

As D5F showed, L>=4096m^3. Since b<=m, S<=168m^3+72m^2+22m+262<=256m^3<=L/16. Also S>=1936 and n+1<=S.

Producer: the inherited accounting is P=256 L(131 L+2176)+2^40. Divide by L^2; the two decreasing terms are maximized at L=37914, where P/L^2<35000.

Bridge: the initial encoded prefix has 235 bits (G, fifteen empty tapes, final tape sentinel), the tail 10 bits. It copies S bits, each to a 5-bit block, using a temporary blank and two-way scans. Its source-to-destination interval is at most 1098+6S<=7S including source header and separators. There are S+2 append shuttles (initial and tail included); each fits 64S physical transitions, counting the source and return scans, writing and restoration. Thus I<=128 S^2. The producer's bridge-entry transition is already charged in the producer ledger.

Worker capacity: the 16 segmented tapes need 49 fixed blocks (one G, sixteen sentinel/spare-blank/separator triples). Additional data capacities are S for stream, 444 for the static scope table (36 pairs x3 plus 84 triples x4), 9m for domain words, 3m for reusable rank words, m for pins, n for output. Clears reuse existing cells and append at most one spare blank beyond maximum data length. Thus N<=S+32m+486<=2S, counting logical blocks.

Worker time: every charged IR primitive is a read, write or unit move. There are exactly 120 higher-arity scopes, 36m^2+84m^3 candidate mask rows. For each row there are at most 3 rank reads, 4 stream read/move primitives, at most 3 rank advances (2 primitives each); each rank word's rewind costs at most 2k+4 for length k>=1 and occurs once per k advances, amortized at most 6 per advance. Hence <=31 primitives per row including these amortized rewinds (use 32). Pair's third word has length one. Each scope's loading, scratch clearing/copying, dispatch, initial rank rewinds and delimiter handling fit 100(m+1) primitives: a clear costs <=7m+9 and a copy <=6m+5; even three clears/copies plus rewind and dispatch fit the allocation. Unary/pin/bound scans are linear, initialization of the fixed 444-symbol table takes fewer than 2000 primitives, and output translation is linear in m with at most nine one-hot copies, nine cumulative scans and one pin copy. Allow the extra 4000(m+1)+5000 primitives on top of the 12000(m+1) scope overhead for these operations and terminal handling. In particular use T<=32B+16000(m+1)+5000<=128S. This is source-level amortized accounting, not a machine-checked cost certificate.

By the existing five-bit segmented compiler inequality W<=(26N+16)T+8<=8192 S^2. Projection uses the tape-zero variant of the established mark/append/restore routine, giving O<=16(n+1)(5N+n+1)<=256 S^2. Thus

    t <= P+I+W+O <= 35000 L^2 + (128+8192+256) S^2
      <= 65536 L^2 = 2^16 L^2.

The latter constant is deliberately loose. This applies to successful supported computation, with normalization/planner correctness, D5E producer macro costs, valid stream shape and the existing physical compiler proof as premises. This is not a mechanically certified result or an unrestricted runtime theorem.

## Cubic admission thresholds

From L<=2^H, ceil log2 t<=16+2H. A sufficient condition for the original schedule is ell+16+2H<=3H, i.e. H>=ell+16. This gives:

| machine | ell | sufficient H |
|---|---:|---:|
| strict singleton |124696396|124696412|
| adaptive first allowed |124697764|124697780|

These are exact integer thresholds for this sufficient inequality, not earliest successful stages. They are dramatically below the conditional general width-three threshold 2785338274 but still astronomical. No measured input fits these descriptors at cubic stage.

## Adaptive controller

The strict and adaptive IR share one implementation with a compile-time flag. Instead of refusing on the second allowed unary bit, adaptive mode writes zero in that position, retaining a one-hot word for the first allowed rank. An empty domain refuses. Binary/ternary masks are checked exhaustively at the selected rank combination; a forbidden candidate refuses. No false witness is emitted. This is not propagation, search over alternatives, or complete coverage of partially forced SAT inputs. The validated producer still refuses outside its supported width-three graph family.

Adaptive quotient: 2244378 original states, 1640760 quotient states, 6733134 exact transition homomorphism checks, descriptor 124697764 bits. Only 18 quotient states and 1368 descriptor bits more than strict. Fresh whole-machine raw selector replay, exact quotient replay and one-step-short cutoff completed in a JS runtime:

| m2 case | t | head | span | result |
|---|---:|---:|---:|---|
| empty |289513684|53132|54161|valid witness |
| partially forced |289527574|53132|54162|valid witness |
| candidate conflict |155016220|40701|53970|blank refusal |

The conflict instance is SAT (another rank in group 1 works); blank refusal is intentional. Native independent descriptor replay is configured in new CI, not claimed until confirmation.

## Executed verification

10017 exact arithmetic domain evaluations (2..10000 and 18 large power neighbors), 6 threshold boundary checks, three inherited strict physical phase ledgers, 40 adaptive IR fixtures and the same 40 strict checks, 23 successful adaptive cases checked against original clause oracle and source-level worker resource envelopes, 17 adaptive refusals. Seven refusals were positively identified as satisfiable by the exhaustive rank oracle for m<=4; additional refusals are not claimed UNSAT. All expectations passed. Three fresh adaptive physical raw-selector cases with quotient/cutoff and all-transition checks passed. New CI independently runs these checks, original-format C++ native interpreter and Python original clause verification, and inherited governance gates.

Reproduce: node mathos/research/f038_rex_width_three_singleton_envelope.js ; node mathos/research/f038_rex_width_three_adaptive_audit.js

Next: confirm D5H CI/native replay, implement bounded alternate-candidate retries or unary/binary propagation with explicit resource budgets, and investigate smaller original-format controllers. No changes to main or PR #248.
