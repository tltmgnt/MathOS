# F038 — nine-group algebraic reduction and exact-stage RAM audit

PNP_RESOLUTION_STATUS = OPEN. New mathematical reductions and finite reference checks. External algebraic running-time theorem is a recent preprint, not independently reviewed here. No compiled original-U solver, Lean proof, or new unrestricted lower bound.

Parent 25acf40d54dea60f014d83f00c3a4fa4a1bd22fc (recursive tiling). The available connector reported no combined statuses or PR-triggered runs for the parent; this does not establish push-triggered CI success.

## 1. Literature update and scope

Chan, Itakura, Ma, Yu, "The 3-Uniform Hyperclique Hypothesis is False", arXiv:2611.06813v1, November 4, 2026 (https://arxiv.org/html/2611.06813v1), Theorem 2.8, report deterministic O(N^3.957) time for 3-uniform 4-hyperclique and give counting and witness recovery (Section 2.1). Nick Fischer, "The Hyperclique Hypothesis is False", arXiv:2611.03880, November 2, 2026 (https://arxiv.org/abs/2611.03880), reports power savings for general fixed hyperclique sizes and uniformities. These are newly posted preprints; neither proof, including its matrix multiplication dependencies, has been independently checked by this project. We do not invoke the traditional unrestricted hyperclique hypothesis as a hardness premise. The following first reduction is unconditional as a mathematical equivalence; its advertised RAM exponent is contingent on the cited algorithm and its model/cost assumptions. The separate exact-stage RAM simulation in Section 3 does not use the preprints.

## 2. Exact four-supergroup reduction for nine groups

Retain the full parent family with r=9, n=19m-7, L=n+1+2n^2+8 binom(n,3)=Theta(m^3), fixed one-hot/OR/pin/guard clauses and arbitrary negative cross-group clauses of widths 1,2,3. Each surviving tuple a in [0,m)^9 has exactly one full assignment for the fixed input pins.

Fix the ninth digit d=a_8. Pair groups (0,1),(2,3),(4,5),(6,7) into four supergroups, each with domain [0,N), N=m^2; the index of a pair (x,y) is mx+y. There are four triples H of supergroups. A forbidden original cross clause has support G (a subset of the nine original groups of size 1..3) and selected digit vector. Ignore the clause if it specifies a ninth digit different from d. Otherwise remove the ninth coordinate, if present. The remaining support involves at most three supergroups. Assign the clause to the lexicographically first supergroup triple H containing that support, including the empty support. This assignment is deterministic and independent of the remaining digit values.

Construct four Boolean arrays A_H on [0,N)^3. An entry is one iff none of the clauses assigned to H forbids the specified supergroup values. An empty projected forbidden clause makes its owner table identically zero. Each remaining projected clause is evaluated in exactly one table; there are no constraints on any supergroup not in its owner table. Thus a supergroup tuple u is a 4-hyperclique iff the decoded eight digits plus d form a surviving outer tuple. Equivalently

    count(d) = sum_{u0,u1,u2,u3} product_{|H|=3} A_H[u_H].

Summing count(d) over all d gives the exact number of outer models. This is a parsimonious disjoint decomposition and handles unary, binary and ternary cross clauses, including repeated projection patterns, not just pure ternary masks.

On a word-RAM, parse the actual selector once to construct indexed forbidden tables, one for each original support G. For each fixed r there are only sum_{h=1}^3 binom(r,h) such supports (129 for r=9). Their total input size is O(m^3). Each supergroup table entry can be formed in O(1) word operations for fixed r by looking up the forbidden bit at the induced original digits, with ninth digit fixed to d, for each original support assigned to the owner H. This is a bounded number of indexed lookups; scanning the whole forbidden-clause list for every entry would not justify the bound. The four arrays occupy O(N^3)=O(m^6) entries per d, and the cost of building all d's arrays is O(m^7), including parsing. Invoke the cited deterministic 4-hyperclique counting/detection algorithm on each d's arrays. If positive, repeatedly restrict one supergroup's allowed domain to half and zero the entries involving disallowed vertices, using the same detector to choose a nonempty half. O(log m) calls suffice to recover the four indices. Reconstruct the original n-bit witness, not the supergroup indices alone; the pins come from the original selector. The original verifier is unchanged.

Using the preprint's reported 3.957 exponent in its standard indexed algebraic algorithm model, the resulting conditional-on-the-preprint time is

    O(m * (m^2)^3.957 polylog(m+2))
    = O(m^8.914 polylog(m+2))
    = O(L^(4457/1500) polylog(L+2)).

Here 4457/1500=2.971333...<3, with slack 43/1500. This is a RAM/algebraic-model transfer, NOT an original three-symbol single-tape runtime bound. In particular the O(m^6) array construction already uses a workspace larger than the original O(m^3) input. The cited rectangular multiplication operations are not free on the original tape. A generic quadratic tape simulation of a multitape algorithm, even if an appropriate multitape algorithm is supplied, cannot preserve this small exponent saving. We supply neither the cited algebraic algorithm's implementation nor a charged original-tape implementation here. The exact cubic cutoff for nine groups remains open.

## 3. Unconditional exact-stage decision simulation on RAM

For any fixed r>=3 in the full promised distributed family (not just nine), define A_s to be the boolean predicate that at least one actual description accepts at stage s of the original U. There is a deterministic word-RAM algorithm computing exactly A_s in

    O(Lm + (s+1)2^s)

word operations for fixed r, with O(L+2^s+s) words of space and words of O(s+log(L+2)) bits (constant factor sufficient for signed positions and sums). At the exact cubic stage s=3 ceil(log2 L) this is O(L^3 log L) time and O(L^3) words. It does not assume SAT coverage and is not a subcubic RAM theorem. It is a simulation of the full stage's acceptance predicate, not a new original-U stage or a claim that the simulation is itself eligible at that stage. It avoids the naive per-description O(L) verification surcharge and is useful for auditing precise resource-model claims.

Preprocess the original normalized input into the indexed forbidden tables and pin vector, as above. Let B(i) be its binary input bit for 0<=i<L, and blank 2 otherwise. Precompute prefix counts and first moments of ones on the input (the sum of their physical positions). Counts of zeros and blanks in any interval follow by clipping it to [0,L). Also precompute, for each possible starting position p in [1-m,L-1], the number M(p) of mismatches between B(p..p+m-1) and the m input pins; for any other p, M(p)=m because the interval is wholly blank. Direct precomputation costs O(Lm) time and O(L) words. Parse the canonical normalized pool and extract the pin bits from the positive-pin, negative-guard selectors. No expensive SAT computation is required.

Enumerate every binary description of length ell<=s, as in the actual descriptions(s), allocating t=2^(s-ell). Decode each actual table using the original syntax; invalid descriptions are ignored. Each code takes O(s+1) word operations to enumerate/decode. A word-RAM tape array of size O(L+2^s) covers every cell any simulated run can visit or read as output, because the head starts at 0, moves by at most one per transition and the output reads n consecutive cells. Initialize it once with B and blanks. For each run simulate its actual transitions up to t or halt, maintaining a log of distinct written positions (mark each on first write). Reads and writes are constant-time array accesses. At halt, the final tape differs from B only at logged positions; the log length is <=t, even if many writes target the same cell. After the run restore the logged cells to B and clear their markers in O(t) time. No O(L) reset per description. A timeout cannot accept.

The external verifier's acceptance on this promised family can be evaluated using only that log and constant-in-r range queries:

- For each original one-hot group, take the m-cell output interval starting at the halt head plus that group's output offset. Obtain its baseline number of ones, zeros, blanks and sum of one positions from the prefix data. For every logged cell in the interval subtract its B contribution and add its final contribution. Reject unless there is exactly one one and no blank. Its digit is the corrected sum of one positions minus the interval's left endpoint. This works also for negative head positions.
- For each OR auxiliary group, its expected zero-prefix length is max(0,a_g-1), followed by ones through the end. Check the corresponding zero and one counts using the same interval-correction procedure. This enforces every auxiliary bit, including the two choices a_g=0,1 with all-one OR groups.
- The pin interval starts at head+n-m-2. Start with M(p); for each distinct logged cell inside this interval adjust by the difference between final and initial mismatch indicators with the appropriate pin. Require zero final mismatches. Check the two guard cells are zero by an interval count. These tests exclude malformed outputs, including blanks outside the initial tape.
- For each of the finitely many original cross supports G of size 1..3, check the selected forbidden bit at the reconstructed digits a_G. Reject iff any such clause is selected. Because the fixed clauses have exactly the stated one-hot/OR/pin/guard extension, these tests are logically equivalent to valid(C,n,p,x) after a well-formed tape_run halt, including every fixed clause. They do not assume the proposed assignment is valid beforehand.

There are O_r(1) interval queries, each can scan the distinct-write log in O(t+1), and O_r(1) forbidden table lookups. Thus verification is O_r(t+1) even when t is much less than n. This is not merely an amortization over long machines. The RAM preprocessing charges the pin pattern's arbitrary bits once, not once per candidate.

The original short builtins returning integers <=3 (including the selector-dependent p%4) cannot satisfy r>=3 one-hot groups, and the out-of-range and empty builtins cannot accept. The exhaustive builtin is active only if its clock is at least 2^n. If active, enumerate the m^r tuples and check their forbidden tables, taking O_r(m^r)<=O(2^n)<=O(2^s) word time because m<=2^m and n>=rm; the stage acceptance predicate is then exactly the family SAT predicate. This simulates its accept/reject effect, not its literal Python list of all models. No need to return the first description's output, since A_s is boolean.

The sum of all allocated clocks, including invalid descriptions, is

    sum_{ell=0}^s 2^ell 2^(s-ell) = (s+1)2^s.

Enumeration/decode and simulation/verification/reset have the same asymptotic bound after adding the preprocessing. This proves the stated time and space and handles the exact original clocks and syntax. At cubic stage the preprint-derived RAM SAT bound in Section 2 is strictly faster asymptotically than this generic stage simulation, but the two predicates need not agree: A_s implies SAT, not conversely absent a stage-coverage theorem. A faster RAM SAT detector alone therefore neither establishes stage coverage nor disproves it.

## 4. Executed finite reference checks

A separate JavaScript implementation used actual canonical clause positions and the full fixed clause set in r=9 layouts m=2,3, with eight deterministic fixture modes per layout. It built the four tables via direct projected clauses and compared every decoded tuple with full clause truth. Totals: 16 selectors, 74,080 table entries, 16,621 retained projected clause occurrences, 161,560 tuple checks, 20,204 satisfying tuples, 8 SAT fixtures (4 unique). Sparse output-image verification was compared with direct selected-clause truth on 2,688 cases across seven head positions, including negative/outside-input positions, valid/malformed images and no-write cases; 235 accepted. A further 3,223 halted traces from 4,096 sampled one-state-table runs were checked (none accepted); eight explicit successful output images were also checked. Zero discrepancies. JS does not implement the external algebraic algorithm or execute the entire cubic schedule. Its direct table construction is a reference, not the optimized bound.

The Python regression checks the same finite semantics, with optimized owner-support indexed lookup and the original verifier on reconstructed witnesses. Its execution and exact-head CI are unconfirmed at writing. The exact-stage complexity proof is not inferred from finite tests.

## 5. Disposition

Do not use the historically stated 3-uniform hyperclique hypothesis as an unqualified lower-bound premise given the new preprints. The nine-group family admits a precise algebraic reduction with a reported subcubic indexed-model exponent; the missing original-machine locality/space transfer is now the target. Next investigate charged blockwise contraction or a different family/proof mechanism; no universal obligation closes. Finite cubic interval 52..233 and reported Lean census unchanged and not recounted. Promotion NONE.
