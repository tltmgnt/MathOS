# F038-REX-024D5A — Exact whole-machine quotient and admission ledger

Parent 09c481480dde16acdd3bddfdd70923a2ab374e8c. Research branch only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE. [D4B exact-head Proctor 45926266236](https://github.com/tltmgnt/MathOS/actions/runs/45926266236) passed, including the original halt-head and full original-format JS codec checks.

## Exact physical quotient

Apply the established typed-array refiner to the *entire* D4B raw-selector-to-unencoded-witness machine, including producer, bridge, worker, projector and blank rejection exit. Partition by each read symbol's write/move action, distinguish halt, refine by successors using inverse adjacency and smaller-half splitting. Every graph-reachable nonhalting state is included. Check the mapping f for every original state and read symbol: Q(f(s),a)=(f(t),w,d) whenever T(s,a)=(t,w,d), with f(0)=0 and f(halt)=halt. Induction preserves the complete physical tape, head, halting status and exact clock at every finite budget, including malformed inputs and blank refusal. Quotient states do not uniquely identify original phases.

| Metric | D4B | Quotient |
|---|---:|---:|
| Nonhalting states |11349426|10922894|
| Transition entries |34048278|32768682|
| State-address width |24|24|
| Original-format descriptor bits |964701214|928445994|

Removed 426532 states and 36255220 descriptor bits (3.758181235%). Initial blocks 71, splits 10922824, processed splitters 32768685, predecessor visits 158682584. All 34048278 transition homomorphism checks passed. All original states graph-reachable and halt reached in the abstract transition graph. The earlier numeric row interning already shares many continuations; the smaller improvement is not a clock speedup. The compressed table's bit count is calculated from its original-format grammar, not a claim that its full serialized stream has already been read natively.

The direct quotient K5-refusal replay completed at exactly 27879501 physical transitions, head 37913, span 39346, blank head, and no witness. The attempted combined quotient build and empty SAT replay exceeded the interactive execution timeout. The two SAT and one UNSAT clocks below therefore transfer from the independently CI-verified D4B machine via the *executed exact all-transition homomorphism*, not fresh completed quotient SAT replays in the interactive environment. No new complete domain-three original-selector run is claimed.

## Native compatible interpreter

Implement a C++17 original ASCII descriptor reader with 1 MiB read buffer, exact unary state header, fixed-width rule fields, range and end-of-file validation, and one packed uint32 per transition. A dynamically growing two-sided tape is initialized with the original raw selector and otherwise blank. Each iteration performs one actual original transition; halt reads n consecutive symbols from the actual head (blank makes the result absent), and an insufficient budget returns no word. Expected output, original clock, and span are checked only after execution. Replay at exactly one step short. Independent Python verification imports the original pool and valid(), interprets the selector and witness in the original little-endian integer convention, and calculates exact witness slot budgets. This is not a call to the original Python tape_run on the large descriptor. The native regression workflow builds the quotient, streams the actual original-format descriptor, runs native cases including a uniquely forced domain-three fixture, and verifies them; full native execution is unconfirmed at this commit. A small original Python tape_run cross-check is included in CI. No complete native large replay or native decoder success claimed before confirmation.

## Exact stage arithmetic

The original schedule has L=n+1+2n^2+8*binom(n,3), b=ceil(log2 L), s_k=k*b. For a particular fixed descriptor of length ell and verified SAT clock t>=1, its minimum *sufficient allotted-budget stage* is s_d=ell+ceil(log2 t), and its minimum coefficient k_d=ceil(s_d/b). This does not identify the earliest universal success, which can come from another description.

| m | Fixture | L | s3 | t | Quotient s_d | k_d |
|---:|---|---:|---:|---:|---:|---:|
|2|empty SAT|37914|48|825112955|928446024|58027877|
|2|edge SAT|37914|48|1297519076|928446025|58027877|
|2|edge UNSAT|37914|48|665681141|no witness slot|--|
|2|K5 refusal|37914|48|27879501|no witness slot|--|
|3|forced (physical unmeasured)|161851|54|unmeasured|unmeasured|--|
|4|unmeasured|428744|57|unmeasured|unmeasured|--|

Before quotient the empty SAT slot was 964701244 (k=60293828). All measured SAT witnesses are from the restricted family. The quotient descriptor is not listed at s3 on any measured dimension. Listing alone requires b>=309481998, hence L>2^309481997. The actual original built-in 000 has length 3 and charged exhaustive clock 2^n, so all SAT inputs at m=2,3 (n=31,50) are guaranteed a witness by s>=34,53, respectively, within s3=48,54. This is an arithmetic implication, not execution of the exponential built-in. At m=4 it needs s>=72 versus s3=57. Exclusion of either the built-in or this fixed description does not establish universal-stage failure.

Conditional on the previously derived uniform resource bound t(L)<=C L^(8/3)(log2 L)^3 for supported SAT inputs of sufficiently large L, the fixed quotient has eventual restricted-family cubic-stage admission: for b=ceil(log2 L), log2 t <= log2 C+(8/3)b+3log2 b. It suffices that b/3 >= ell+log2 C+3log2 b. For example b>=max(256,6*(ell+ceil(log2 max(C,1)))) implies this inequality (for b>=256, 3log2 b<=b/6). Also require L in the range of the inherited bound. C and the start of that range have not been made explicit. This is a symbolic sufficient condition, not a numerical threshold or finite coverage proof. A sufficiently large fixed k may absorb finite exceptions in the supported family; unrestricted SAT and global routes remain open.

Next 024D5B: confirm the native compatible interpreter's actual full descriptor and forced domain-three executions, extend physical domain coverage, derive explicit resource constants or improve the asymptotic and description overhead. Main and PR #248 unchanged; all four global routes and six Omega obligations open.

Reproduce:
```sh
p=mathos/research/f038_rex_width_three
node --max-old-space-size=6144 "${p}_admission.js" K5-refusal
node --max-old-space-size=6144 "${p}_admission.js" descriptor > /tmp/w3.desc
node "${p}_admission.js" fixtures > /tmp/w3.fixtures
g++ -std=c++17 -O3 "${p}_native.cpp" -o /tmp/w3-native
/tmp/w3-native /tmp/w3.desc /tmp/w3.fixtures > /tmp/w3-native.txt
python -m mathos.research.f038_rex_width_three_native_verify /tmp/w3.fixtures /tmp/w3-native.txt
```
