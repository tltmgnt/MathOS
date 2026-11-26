# F038 — Product-domain isolation on the unrestricted nine-group family

PNP_RESOLUTION_STATUS = OPEN. Mathematical isolation and model-preserving reduction, finite reference checks, not a compiled original-U solver or Lean proof. Parent ef2dd3fa3ad4714e21e293badf5335a650058f33 (cyclic semantic boxes); available connector reported no statuses or PR-triggered runs for parent. Push-triggered CI unconfirmed.

## 1. Result and motivation

The preceding cyclic family had only four latent digits. Return to the full nine-group family of the distributed-hyperclique note: all negative cross-group clauses of widths 1..3 are independently selectable, with NO equality reductions, and the inherited one-hot/OR/pin/guard clauses fixed for each pin pattern. The following reduction isolates a unique witness within the same normalized layout without new variables, longer clauses or hashing constraints that require auxiliary encodings.

For any fixed r>=3, m>=2, let D=ceil(log2 m)+2, and p=(3/(16D))^r. An efficiently sampled product of r domain subsets isolates exactly one satisfying tuple with probability >=p for EVERY nonempty solution set, regardless of its size or correlations. The restriction is implemented by setting existing negative unary selector bits, and L and n are unchanged.

For each m there exists a nonadaptive list of O_r(m^3 log^r(m+2)) product restrictions isolating every nonempty solution set of the full distributed family. Any such universal list has at least m^3 members, even if unrestricted subsets of the tuple universe are allowed instead of product sets. This list is a nonuniform existence result, NOT a uniform efficient deterministic algorithm. In particular a constant-size universal restriction list is impossible.

Combining with the earlier exact-stage RAM audit gives a conditional transfer: if every uniquely satisfiable member of the full r=9 family is accepted at the exact cubic stage for all sufficiently large m, then there is a uniform randomized word-RAM witness finder for that full family with bounded error, time O(L^3 log^10(L+2)), and O(L^3) words of space. This implication is not a claim of original-tape cubic coverage, a strictly subcubic RAM solver, or a proof that the hypothesis holds.

## 2. Exact restriction in the original normalized pool

Use the existing layout n=(2r+1)m-r+2, X_g[a]=gm+a+1 for 0<=g<r and 0<=a<m. Every surviving tuple a in [0,m)^r extends to a unique assignment using the fixed OR auxiliary groups, actual m pins and zero guards. Let V be its set of surviving tuples.

Given domain subsets D_g of [0,m), set the selector bit for the negative unit (-X_g[a],) to one whenever a is not in D_g. This is a bitwise OR with the original selector: it does not turn off any original clause, including preexisting negative units. All these positions belong to the actual canonical width-one pool, and none is a fixed clause. Every original variable, pin and auxiliary rule is unchanged, including n and raw input length L=n+1+2n^2+8 binom(n,3).

The resulting tuple set is exactly V intersect (D_0 x ... x D_(r-1)); the full assignments themselves are unchanged on surviving tuples. Thus every valid restricted output is already a valid original output without any witness translation. Empty boxes are allowed, and unsatisfiable originals remain unsatisfiable. The family is closed under the operation, since width-one cross clauses are allowed. In particular this does not reduce to the earlier easier aligned or cyclic subfamilies.

## 3. Random product isolation lemma

Choose each coordinate's level k independently and uniformly in {0,...,D-1}. Conditional on that level, include each digit independently with probability 2^(-k). The bits can be sampled exactly by k fair coin flips per digit (include iff all are zero), and a uniform level by rejection from the smallest enclosing binary range. Empty and full subsets are included in the distribution.

For any nonempty W subset [0,m) of size h, there is a level k in the range with 1/4 < h*2^(-k) <= 1/2: take k=ceil(log2(2h)). Write q=2^(-k). Conditional on this level, the probability of selecting exactly one member of W is

    h*q*(1-q)^(h-1) >= h*q*(1-(h-1)*q)
                     >= h*q*(1-h*q) >= 3/16.

Averaging over the D levels gives at least 3/(16D). To isolate an arbitrary nonempty V subset [0,m)^r, expose the coordinate restrictions one at a time. Conditional on success at every previous coordinate, the surviving V is nonempty and has exactly one allowed digit in each exposed coordinate. Its projection onto the next coordinate is a nonempty W of size at most m. With conditional probability >=3/(16D), the next restriction selects precisely one digit of W, leaving at least one tuple and fixing another coordinate. The next random subset is independent of all previous restrictions, even though W depends on them. After all r successes there is precisely one surviving tuple. Multiplying the conditional lower bounds proves p. The event used is sufficient but not necessary for final uniqueness; no independence of coordinates in V is assumed.

Sampling needs O_r(m log(m+2)) expected random bits and word operations, including level rejection sampling; a bounded-time variant can sample levels by taking the next power-of-two number of levels and allowing the extra levels to mean an immediate failed trial. This changes the bound only by a constant factor for fixed r. In this note the algorithm uses uniform levels with rejection and expected sampling time; alternatively use the bounded variant for worst-case time, with p replaced by (3/(32D))^r and the same big-O bounds. Generating the restricted raw selector by sequential copying and updating its unary section costs O(L polylog L) bit work on fixed multitape storage; on RAM it takes O(L) word operations. No SAT queries are used to choose the random restrictions.

## 4. Nonadaptive universal list and a size lower bound

The number of arbitrary variable cross selector positions for fixed r,m is

    H=sum_{k=1}^3 binom(r,k) m^k = Theta_r(m^3).

There are at most 2^H distinct tuple sets; pin choices do not change tuple feasibility. For r=9, H=9m+36m^2+84m^3. Sample K independent product boxes from the above distribution. A particular nonempty tuple set has probability at most (1-p)^K<=exp(-p*K) of never being isolated. A union bound over at most 2^H tuple sets shows that K=ceil((H ln 2+1)/p) suffices for a positive probability of simultaneous coverage. Hence a nonuniform universal list exists with O_r(m^3 log^r(m+2)) members. It can be stored with O_r(K m) bits plus overhead, but this proof does not construct it uniformly in polynomial time or provide a short uniform seed.

For the lower bound, restrict all groups after the first three to digit zero using negative unary clauses, and use the arbitrary ternary mask on the first three groups to realize EVERY subset of the M=m^3 tuples with this fixed suffix. For any list of subsets R_1,...,R_K of the full tuple universe that isolates every such nonempty subset (not necessarily product boxes), begin with all M tuples. Choose a list member intersecting this set in exactly one tuple; delete that tuple. Repeat with the remaining set until empty. A previously chosen member cannot be reused because it has empty intersection with every subsequent remaining set. Thus at least M different list members are needed. This peeling proof does not assume a particular enumeration or that the list is efficient. It also does not bound adaptive algorithms, which may choose different restrictions based on the input, or the number of programs capable of generating many restrictions.

For r=9 the bounds differ by at most a fixed ninth power of a logarithm. The universal list lower bound cautions against simply encoding a separate restriction identifier in each fixed-clock program description and assuming that the description penalty is constant. It is not a lower bound on the original weighted clock, and it does not preclude a succinct adaptive or randomized strategy.

## 5. Conditional unique-to-general transfer with exact stage accounting

Assume the following specific hypothesis U_r: for all sufficiently large m, every uniquely satisfiable selector in the full promised r-group family is accepted by the actual U at s=3 ceil(log2 L). This includes all restricted selectors constructed in Section 2 because the restriction does not change L or leave the family. We make no claim that U_9 has been established.

The earlier algebraic-transfer note gave an exact boolean stage simulation on word RAM in O(Lm+(s+1)2^s) word operations and O(L+2^s+s) words of space on the full promised family, by restoring sparse writes between original descriptions and using a sparse exact verifier for the fixed clauses and indexed variable supports. That simulation can also return any accepting witness: after its first acceptance, read the n output bits from the simulated tape (O(n) extra time), or reconstruct the fixed extension of the accepted tuple. For the exhaustive builtin, if eligible, a direct enumeration of the m^r tuples suffices to return a valid model in O_r(m^r+n)<=O_r(2^s+n) word work; the other builtins do not accept for r>=3. This is a boolean-or-witness stage audit, not an original machine running free RAM operations.

For each independent restriction trial, construct the modified selector and run this exact simulation. On acceptance return the original witness, which is valid by the subset property. On UNSAT no trial can ever accept, since the original verifier is sound. On SAT, under U_r a trial succeeds at least whenever it isolates a unique model, hence with probability >=p. With ceil(ln(1/eta)/p) independent trials the chance of failing to return a witness is at most eta in (0,1). Trials reuse the simulation workspace. The same guarantee holds using the bounded-time sampler and its correspondingly halved per-coordinate probability bound.

For fixed r and fixed eta (e.g. 1/3), the resulting RAM time is

    O_r((Lm+(s+1)2^s) log^r(L+2))
      = O_r(L^3 log^(r+1)(L+2)),

at the cubic stage. For r=9 this is O(L^3 log^10(L+2)); the word space is O(L^3) with word width O(log L). If U_r only starts beyond an unknown finite cutoff, uniform asymptotic existence follows by incorporating that finite threshold and direct exhaustive handling of smaller m into the machine; no numerical threshold is asserted. A positive result on unique coverage would transfer to this randomized indexed-model search, but not directly to original tape coverage. The probability and repetitions are not a free extra resource in the deterministic original schedule; the simulation overhead and code-length penalties must be charged for any original-machine claim. Conversely, failure of U_r would directly give unbounded unique SAT misses because the hypothesis quantifies over all sufficiently large sizes. This implication is logical, not evidence of such failures.

## 6. Executed finite reference validation

Separate JavaScript enumerated every nonempty tuple set at (m,r)=(2,1),(2,2),(2,3),(3,1),(3,2), and every possible product box, using the exact dyadic-mixture integer weights for the distribution (converted to a floating ratio only for reporting/checking the loose bound). Totals: 791 nonempty tuple sets, 156 product boxes across layouts, 49,332 set/box checks. All probability lower-bound checks passed. The Python regression uses integer arithmetic for the bound.

A separate JS reference built actual normalized clause positions for r=9,m=2,3 with eight deterministic full-family fixture modes each, and 32 boxes per fixture (including full, empty, and a known-singleton box if a model exists, plus deterministic pseudorandom samples). It compared all restricted tuples to filtering the original tuple set, and checked the original fixed clauses and restricted cross clauses on a surviving reconstructed witness for each SAT restriction. Totals: 16 selectors, 512 restrictions, 3,429 newly set unit bits, 35,171 restricted models counting repetitions, 17 unique restrictions, 82 SAT restrictions, zero discrepancies. The sampled fixtures are semantic tests, not statistical evidence for the isolation probability; some boxes intentionally depend on an already known witness for positive controls. Python regression uses the actual pool/normalized selector and original verifier on witnesses. Python execution and exact-head CI unconfirmed at writing. The asymptotic probability lemma is mathematical, not inferred from these tests.

## 7. Disposition

Unique-SAT isolation can be performed within the full nine-group family and without changing the exact clock length. Uniform randomized isolation is polylogarithmically lossy for fixed r; nonadaptive universal deterministic lists need at least linear-in-L size and exist within a polylog factor of that. This neither establishes U_9 nor yields a deterministic original-tape subcubic algorithm. Next investigate resource-aware deterministic isolation or an obstruction to unique witness generation, including the cost of adaptive restriction evaluation on the actual tape. The earlier finite cubic interval 52..233 and reported Lean census are unchanged and not recounted. No universal obligation closes. Promotion NONE.
