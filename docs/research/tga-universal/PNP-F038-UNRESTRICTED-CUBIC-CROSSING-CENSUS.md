# F038 / unrestricted route — cubic crossing census on 93 additional source sizes

PNP_RESOLUTION_STATUS = OPEN. Mathematical finite-length existence derivation and finite regression; not Lean or independent mathematical review.

Parent e70a6ed0e40a4fab632aa10164035d976981654b: six exact-head workflows passed. The stage-63 Proctor failed at compilation: https://github.com/tltmgnt/MathOS/actions/runs/45745443011 . GCC 15 emitted -Warray-bounds at vector push_back on the initial 93-byte tape. This commit replaces the constructor with an already-sized zero vector, fills the unary prefix and reserves the final length, without suppressing warnings or changing input bits. The repaired prior workflow is a separate replay; it has not yet passed at the new head. Its partial census and attempted full-clock simulation are NOT premises of the theorem below.

## 1. Result and significance

The earlier stage-63 fixed pattern has unresolved two-state computations. Instead of attempting to certify that particular pattern, construct a different family of uniquely satisfiable inputs and prove by exact crossing-sequence counting that many members defeat ALL programs at their actual cubic clocks.

For every integer n in [93,185], on the unchanged U and exact stage s=3 ceil(log2 L(n)),

    |B_3^uniq(n)| >= 2^(n-7).

At n=93 a stronger exact integer lower bound is 618634502047598618803566102. Combined with the earlier finite interval result this gives unconditional finite existence at every source size 52..185, 134 consecutive sizes. These are existence counts, not enumeration of that many selectors, and not a verified particular assignment pattern at n=93. Neither this theorem nor the prior 52..92 result establishes an asymptotic exponent-three lower bound. All prior one-state suffix arguments remain subject to review. No novelty claim for classical crossing-sequence reasoning.

## 2. Two independent data blocks in the actual selector

Set m=floor((n+1)/2), A=m-2, B=n-m-2. For every a in [0,2^A) and b in [0,2^B), force x_3,...,x_m to the bits of a and x_(m+1),...,x_(n-2) to the bits of b, in increasing variable order. A pin for x_i uses all four ternary clauses (l_i OR +/-x_g OR +/-x_h), where l_i is the desired signed literal and g,h are distinct other variables. For the left block choose g=1,h=2; for the right block choose g=n-1,h=n. Additionally force x_1,x_2 to zero with guards 3,4 and x_(n-1),x_n to zero with guards 1,2. The four signs of the two guards force the pinned literal regardless of those guard values, so the formula has the unique model w= (a shifted by 2) OR (b shifted by m). All 4n clauses are distinct: the four additional pin supports are distinct from each other and from the varying block supports; each pin has four different signed clauses. No other selector is chosen. Different (a,b) give different selectors because the models are different. There are precisely 2^(n-4) members of this family. The output includes all n bits, including the fixed zero guards.

The actual normalized input is 1^n 0 followed by all selector bits, with unit/binary clauses first and lexicographic ternary supports then signs. Its length is L=n+1+2n^2+8 binom(n,3). Varying left clauses have least variable 1; varying right clauses have least variable at least m+1. Put

    P = L - 8 binom(n-1,3),
    Q = L - 8 binom(n-m,3),
    g = Q-P+1.

For each integer c in [P,Q], cut the tape between c-1 and c. The initial left half-line is determined by a and fixed constants, and the initial right half-line by b and fixed constants. All such cuts are strictly to the right of the starting head. All cells in the common intervening region are independent of the two data blocks. Some fixed pin clauses may lie in that region; it is not necessary that the region be all zero. Blanks outside the input are fixed. This is an exact property of the COMPLETE selector encoding, not of a compressed clause list.

## 3. Two-state crossing lemma with exact original clock

Fix any one of the 27^6 valid two-running-state descriptions. Its allocated clock at stage s is t=2^(s-42). Let M be the set of pin pairs on which it halts within t original transitions and emits the verified model. For an execution in M and a cut c, record the running state immediately after each crossing of c. Ignore cuts crossed by the halting transition (at most one cut) and cuts strictly inside the final n-cell output window (at most n-1 cuts). Every remaining transcript is a binary string. Head starts on the left, hence an even transcript length has final head on the left and an odd length on the right. The entire output window lies on that side.

The crucial deterministic replay fact: given the initial tape on one side and the complete crossing sequence, the final output, when the execution halts wholly on that side at a noncrossing transition, is determined. Between crossings the machine evolves using only that side's cells. For the initial side, its first local segment starts at the original head/state; for the other side it starts at the boundary with the first incoming state. Each subsequent incoming crossing supplies exactly a boundary head and running state. Induction over local segments proves that two actual halting executions with equal side input and equal transcript have identical local evolution on that side, including its tape edits and the terminal head and output if they halt there. No remote time is communicated to the machine; its transition rule has no clock input. The external clock only discards some executions. We only compare executions known to halt within their actual clocks, never infer a halt by extending the clock. A halting transition across the cut is deliberately discarded so a terminal halt symbol is not needed. No rejection transcript, output offset, time or clause index is transmitted in this proof.

Fix r>=1. Let E_r=sum of 2^j over even j in [0,r], and O_r=sum of 2^j over odd j in [0,r]. For any fixed cut, the number of successful pin pairs with at most r crossings and with no discarded condition is at most

    E_r 2^A + O_r 2^B.

Indeed on the left side, fix a and any even transcript of length at most r. The verified output determines the entire b, so at most one b is possible. The right-side case fixes b and an odd transcript and determines a. This applies to every table, irrespective of its computational behavior on the rest of the family.

On each successful execution, each transition crosses at most one cut, so the sum of crossing counts over these g cuts is at most t. At most t/(r+1) cuts have more than r crossings. Discard also at most n cuts for straddling and halting-crossing. Therefore every successful pair has at least g-n-t/(r+1) good cuts. Double-counting good (pair,cut) incidences gives

    |M| * (g-n-t/(r+1)) <= g (E_r 2^A + O_r 2^B).

For positive denominator D=(r+1)(g-n)-t, the fraction of the entire family solved by this fixed two-state table is bounded by

    (E_r/2^B + O_r/2^A) (r+1)g / D.

This averaging avoids an extra factor g in the union bound. It charges all t original transitions, including any repeated crossings, and does not depend on a partial simulation or guessed termination. It is a success-count theorem, not a restriction on eligible two-state machines.

## 4. Exhaustion of all eligible descriptions and exact integer bound

At these sizes s is 63,66 or 69. The description lengths for one, two, three, four running states are 20,42,61,92. The actual decoder gives 18^3,27^6,36^9 valid descriptions respectively for q=1,2,3; no q>=4 description is eligible. The earlier all-clock one-running-state prefix theorem applies since all selectors are ternary-only, so each one-state description emits the same optional well-formed proposal on every member of the family. Consequently each can solve at most one member. The three-state clock is 2^(s-61), at most 256 here; its accessed cells and final output window lie before the first ternary selector bit because t_3+n <= n+1+2n^2. Thus each three-state description likewise solves at most one. Invalid descriptions cannot produce proposals. The exhaustive built-in is inactive since s-3<n. All other built-ins have absent, invalid or at-most-3 proposals; the first two output bits are forced zero, hence they can collectively solve at most the all-zero model's family member (including the selector-dependent residue built-in). No change to the built-ins or the original stage.

Let D2=27^6 and D0=18^3+36^9+1. The fraction of the entire family solved by ANY scheduled description is at most the rational

    U(n,r) = [D2 (E_r 2^A + O_r 2^B) (r+1)g + D0 D] / [2^(n-4) D].

All quantities are integers and every denominator used is strictly positive. For each n=93,...,185 choose the r in 1..256 minimizing U among positive denominators (smallest r on ties). The independent BigInt computation and the Python exact Fraction regression check, for each of the 93 sizes, the strict inequality 8 U < 7, plus the original stage eligibility and prefix bounds. The maximum is at n=148, where U<0.830928636. Therefore more than 1/8 of the family remains, giving at least 2^(n-7) distinct uniquely satisfiable selectors in B_3(n). At n=93, r=3, g=883201, s=63, and U<=0.000542058; the exact ceiling of 2^89 (1-U) is 618634502047598618803566102. This is a union bound on all eligible programs, not a count of distinct two-state outputs on a single input. It proves nonemptiness without computing which pair is missed. The previous fixed-pattern candidate may or may not be missed; no full-clock claim about it follows.

For reproducibility the plan contains integer upper ceilings of 10^9 U at endpoints, sums over all sizes, the exact maximum size and exact n=93 lower count. The interval's stage distribution is 24 sizes at stage 63, 31 at 66, 38 at 69. At n=186, stage 72 raises the two-state clock by a factor of eight and this bound with the chosen balanced split fails. That does not imply absence of cubic failures there. Even though the construction is parameterized, at unbounded n more descriptions activate and t/g grows; this finite calculation cannot prove an infinite sequence. Future work needs an asymptotically new argument or a uniform polynomial cutoff.

## 5. Evidence and audit limits

Independent JavaScript enumerated all pin pairs and all assignments at n=8,9,10 (112 uniquely satisfiable selectors; 86016 full assignment tests). It also ran 256 deterministic two-state tables on 16 binary input pairs at each clock 8,16,32 (12288 executions), comparing local transcript/output consistency across both data blocks, parity, discarded cuts, per-cut counts, and double counting. The small trace tapes are abstract separated-data tapes, not actual large cubic instances. The Python regression additionally verifies original clause-pool positions on the small pin selectors, checks the actual parent decoder and interpreter on a real selector, and includes a dedicated halting-crossing control. Exact arithmetic checks all 93 sizes and the next size 186; no enumeration of the 387420489 two-state tables is needed for the theorem. Independent JS did not execute the new Python. No actual large missed pin pair has been identified; the previous C++ full-clock attempt remains incomplete. The prior failed compilation is repaired in the same branch, not reported as passed. The new proof is independent of those partial execution counts. Exact-head CI, mathematical review and Lean formalization remain outstanding. MRA-X stages are locally authored records, not independent agents.

Forward TGA: NARROWED_RESTRICTED_CASE_ONLY. Finite unconditional cubic failure interval enlarged to 52..185 by counting the successful programs rather than simulating them. No universal obligation closes.
