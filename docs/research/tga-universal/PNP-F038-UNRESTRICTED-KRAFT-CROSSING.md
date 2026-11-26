# F038 — prefix-free incoming crossing transcripts and finite cubic residuals

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation with finite regression; not independent mathematical review or Lean.

Parent f63f83d39b12adb186c0d7be6b77fd06480bf836: both exact-head Proctor replays passed: https://github.com/tltmgnt/MathOS/actions/runs/45746300784 and https://github.com/tltmgnt/MathOS/actions/runs/45746300815 . Seven workflows passed at inspection; TOPO-406 still running.

## Result

For every integer n=191,...,233, the exact original cubic stage has at least 2^(n-3) uniquely satisfiable residual selectors. Together with the previous results this proves finite existence at 177 sizes: 52..185 and 191..233. Sizes 186..190 are NOT covered. At 234 the bound again exceeds one. No unbounded-length theorem is asserted. The improvement uses prefix-free incoming transcripts rather than counting full crossing strings up to a selected threshold. This is an elementary application of the classical Kraft inequality and crossing-sequence argument, not a novelty claim.

## 1. All n bits independent, separated input

Choose 3<=m<=n-3. Divide variables into 1..m and m+1..n. For any assignment w=(a,b) select the seven satisfied signed clauses on support {1,2,3}, and on {n-2,n-1,n}. These force the respective triples. For i=4..m select the four guard-sign lifts of its desired signed literal using guards 1,2; for i=m+1..n-3 use guards n-1,n. All 4n-10 clauses are distinct, ternary-only, and their conjunction uniquely forces w. There are exactly 2^n distinct selectors, since each has a different unique model. Left varying clauses have minimum variable 1 and right varying clauses minimum at least m+1. Thus in the actual lexicographic support pool, for every cut c in [P,Q] where P=L-8 binom(n-1,3), Q=L-8 binom(n-m,3), g=Q-P+1, the left initial tape depends only on a and the right only on b. Here L=n+1+2n^2+8 binom(n,3). Common cells and exterior blanks are fixed. Head starts left of all cuts.

## 2. Incoming prefix-free lemma

Fix a deterministic general tape program and its actual allocated clock t. Consider successful executions on this family. Discard cuts strictly inside the final output window (at most n-1) and the cut, if any, crossed by the halting transition. At each remaining cut the final output is wholly on a side and the halt transition is noncrossing. Record ONLY the sequence of running states arriving INTO that final side (not outgoing states). Given the initial tape on that side and the incoming sequence, deterministically replay its local segments: for the left side begin at the initial head/state; for the right begin at the first incoming boundary state. Whenever the head exits, suspend until the next incoming state supplies the boundary head and state. The clock is not supplied to the program as input. Compare only actual executions known to halt on that side, not artificially extended runs.

For fixed side, cut, side input and program, incoming sequences of actual noncrossing halts on that side are prefix-free, even if the allowed output is not verified. Indeed, if a shorter sequence ends in a local halt, the same local evolution with those incoming states must halt before any further departure. It cannot consume additional arrivals. Equal sequences have equal outputs. On successful pin executions that output fixes the missing opposite-side data, so each sequence corresponds to at most one successful pair. If the incoming state alphabet has cardinality q>=1, Kraft's inequality gives sum q^(-j)<=1 over those distinct sequences of lengths j (for q=1 this just says at most one word). An empty alphabet permits only the empty sequence. The claim uses actual determinism and the original head movement, not the absence of writes. For binary states the inequality follows by associating each sequence with its disjoint cylinder in infinite binary strings.

Let h=g-n>0. Each successful execution has at least h retained cuts. Across those cuts the number of incoming states is at most floor((t+g)/2): at any cut crossings alternate; an even number ends on the left with half incoming, an odd number ends on the right with one additional incoming. Summed crossings <=t because each transition crosses at most one cut. Choose any h retained cuts per execution and put K=floor((t+g)/2)=kh+r, 0<=r<h. For nonnegative integral incoming lengths j_i with sum<=K,

    sum_i 2^(-j_i) >= (h-r)2^(-k)+r 2^(-k-1) = (2h-r)/2^(k+1).

Proof: increasing a length decreases the sum, so a minimum occurs at sum K. Replacing lengths x,y with x+1,y-1 when y>=x+2 decreases the sum; repeat to make lengths differ by at most one. This is the discrete convexity inequality, avoiding floating-point estimates.

Summing over all successful pairs and cuts, the prefix-free bound at each cut is <=2^m+2^(n-m), so any two-state program solves at most

    g(2^m+2^(n-m)) 2^(k+1)/(2h-r)

members. This improves the previous full transcript threshold bound and is valid at the original clock, regardless of the actual program's runtime distribution.

## 3. Exact directional alphabet census

A two-running-state transition is (next state in {0,1,halt}, write in {0,1,blank}, move in {-1,0,+1}). Enumerate all 9^6 shapes of next-state/move pairs and multiply by 3^6 for writes. If the initial state reading 1 halts, the proposal is independent of w (the first step and entire output window precede any varying selector bit), so that table solves at most one member. There are 129140163 such tables. Otherwise compute the running-state graph reachable from initial state 0, over all possible read symbols. If no reachable transition halts, no successful execution is possible: 44109603 tables. These classes are disjoint, and the graph is an overapproximation of actual reachable states, so it never discards a possible halt.

For all remaining tables let l,r' be the numbers of distinct running states entered by reachable nonhalting left-moving and right-moving transitions respectively. These bound the respective incoming alphabets. The exact matrix, rows l=0,1,2 and columns r'=0,1,2, is

    [[11029041,30967920,14217687],
     [30967920,57806784,24476904],
     [14217687,24476904,6009876]].

Together the classes sum to 27^6. The high class (l,r')=(1,2),(2,1),(2,2) has 54963684 tables; apply the binary Kraft bound. For l=r'=1, prefix-freeness on a unary alphabet bounds successful pairs per retained cut by 2^m+2^(n-m). For l=0, a retained cut has at most one nonhalting crossing, so at most 2^m+r' 2^(n-m) successful pairs; for r'=0 there can be no crossing and only the 2^m term. Define low contribution C by summing these per-cut bounds times their exact matrix counts. Every success has h retained cuts, hence at most gC/h successes across low tables. No assumptions about actual reachability or halting beyond the sound graph exclusion are made.

## 4. Exact stage accounting

At 191..233, s=72, t=2^(s-42), and description lengths 20,42,61,92. The one-state prefix theorem from the previous cubic interval applies (all unit and binary selectors zero), so each one-state table solves at most one. The three-state clock t3=2^(s-61) satisfies t3+n<=n+1+2n^2, so each three-state table's optional output is independent of w. No four-state description is eligible. The exhaustive builtin is inactive (s-3<n), and remaining builtins together can solve at most the four assignments with values 0..3, even the selector-dependent residue proposal. Invalid strings cannot emit a proposal.

With H=54963684, F=18^3+36^9+4+129140163, the union-bound fraction of all family members solved is at most

    U = [ H*g*(2^m+2^(n-m))*2^(k+1)/(2h-r) + g*C/h + F ] / 2^n.

All computations use integers or exact rationals. For each n in 186..234 choose the m minimizing U over floor(2n/5)..ceil(13n/20) (first on ties). At 191..233 all geometry constraints hold and 8U<7. The largest U is at 191, below 0.824878034. At 191 the exact ceiling of 2^191(1-U) is 549629200504464154840598534802029203673962019961848562590. In particular every size 191..233 has >=2^(n-3) unique failures. The bound does not establish actual failure at 186..190 or 234. These are symbolic counts, not explicitly located missed patterns. This improves the finite frontier from 185 to 233, not the asymptotic exponent. At unbounded lengths the two-state clock/g grows like L^2 and higher descriptions activate; the argument gives no unbounded cubic theorem. The previously proved all-exponent target remains open.

## 5. Evidence

Independent JS enumerated all 531441 shapes with write multiplicity, computed the rational bounds using integer cross-products, exhaustively verified 448 pin selectors and 86016 assignment tests at n=6,7,8, and ran 12288 small abstract separated-tape executions checking incoming word prefix-freeness and consistency. Python uses actual pool and verifier for the pin geometry, previous trace helper for finite local replay, exact Fraction arithmetic, and independent controls for discrete convexity. JS did not execute Python. Exact-head CI, independent mathematical review, Lean formalization, and an explicit missed pattern remain outstanding. The previous stage-63 partial candidate is still not fully certified, despite its repaired partial replay passing. No universal obligation closes. MRA-X roles are locally authored records.
