# F038 / unrestricted route — formula-only diagonal discovery and the cost of recovering a witness

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Parent 3b48c50cec7a6bea2677dacfc65b38d4909c9ae9 exact-head Proctor: https://github.com/tltmgnt/MathOS/actions/runs/45740509040 (success). Six parent workflows succeeded at inspection; TOPO-406 was still running.

## Objective and scope

The previous discovery obstruction required the adversary to output both a formula and a witness. Remove that requirement: the adversary now outputs ONLY a complete original selector encoding, guaranteed satisfiable and guaranteed to defeat the specified clocked program. Does omission of a witness make a uniform efficient adversary possible? This cycle proves that it does not when the clock exponent is given in binary. It also gives an unconditional resource constraint for the linear-clock domain and characterizes the remaining uniform formula-family route for the exact U. These are discovery results, not new SAT runtime lower bounds. No new unbounded cubic-stage counterexample is asserted. Seven MRA-X roles are authored local records, not independent agents.

## 1. Formula-only generator, exact clock and output cost

Keep the original general three-symbol tape-machine descriptions d, unary-n selector encoding p, assignment output convention and verifier. As in the preceding cycle, an external analysis clock for an individual program is c(L+1)^e, where c,e>=1 are binary integers and L=L(n)=n+1+2n+4 binom(n,2)+8 binom(n,3). The actual universal machine U and its stage clocks are unchanged. A formula-only generator G on valid triples (d,c,e) is total and returns a complete, explicitly encoded selector p such that F_p is satisfiable but d fails to emit a verified model within that clock. G need not output any model; its internal computation is unrestricted. It cannot return a compressed formula instead of its complete selector tape.

A total computable formula-only generator exists iff the previous witnessed generator exists: one direction discards the witness; the other exhaustively tests all n-bit assignments on the returned satisfiable formula, finds one, and appends it. Both are computable transformations, not polynomial-time equivalences. Thus existence on all clocked polynomial programs is equivalent to P!=NP by the previous proof. On the linear-clock domain e=1 existence is unconditional, using the previously derived unbounded exact quadratic-stage failures of U. Each fixed linear-clock description is covered by U's stage-two schedule at sufficiently large lengths, so enumerating actual failures terminates. The remaining issue is discovery time.

Charge G's running time T in bit-machine steps with explicit output; in the chosen model at most one output bit is emitted per step, so T>=L. Equivalently a different fixed output convention changes only a constant. The exact selector length satisfies L>=n^3/2 for every n>=1, directly from its polynomial and the finitely many small sizes. Hence n<=(2T)^(1/3).

## 2. Parameterized formula-only self-description

Reuse the preceding mathematical compiler C(s,z) from a fixed source bit-machine language with constant data z into the actual three-symbol one-tape syntax. A finite-state literal loader plus fixed interpreter gives description length O(b log(b+2)) for b bits of source and data. Computation and input/output conversion have fixed polynomial simulation overhead. This is the same mathematical simulation hypothesis justified by ordinary tape block encoding in the previous note, not a new implemented compiler. Classical background: Kleene's recursion theorem (Stanford Encyclopedia of Philosophy, https://plato.stanford.edu/archives/fall2025/entries/recursive-functions/ ) and the standard polynomial-overhead one-tape simulation (Sipser, Introduction to the Theory of Computation, theorem 7.8). No novelty claim for self-reference.

Fix G. Let Q be a fixed source program which receives z=(s,h), reconstructs d=C(s,(s,h)), builds the clock parameters described below, and runs G on the resulting triple. It reads the returned explicit formula, enumerates assignments in increasing integer order until a verified model is found, and emits that model with the actual U halt-head convention. Set d_h=C(Q,(Q,h)). The literal source-as-data construction ensures d_h is exactly the description reconstructed by Q. The data h is binary, so |d_h|=O(log(h+2) log log(h+3)). The coefficient or exponent 2^h is explicitly written as h+1 bits; no operation on an exponentially long unary clock is needed. The input tuple uses the previous self-delimiting lengths. Its total length m_h=h+o(h).

On the target selector p_h output by G, let n_h be its source size, L_h its full selector length, T_h the time used by G. Enumerating all assignments with direct verification takes at most poly(L_h+1) 2^n_h bit steps, because each selected clause has width at most three and indices and verification scans can be charged polynomially. Include setup, compiler invocation, clock writing, G's entire run, input copying, all witness verification, and final output copying. By fixed polynomial overhead there are constants C0>=1 and integer a>=1 independent of h such that the actual d_h runs on p_h in at most

    C0 (h+T_h+L_h+1)^a 2^(a n_h)

steps. This is a bound on the unclocked computation; if it fits inside the given external clock, the actual clocked interpreter must accept the returned verified witness. Correctness of G requires it not to fit. Thus the necessary inequality is

    a n_h + a log2(h+T_h+L_h+1) + log2 C0
        > log2 c_h + e_h log2(L_h+1).

No assumption that G reveals its witness is used.

### Linear-clock domain: unconditional cubic discovery cost

Take c_h=2^h, e_h=1, so the right side is h+log2(L_h+1). Suppose T_h<=delta h^3 for arbitrarily large h, with delta>0 chosen so that a(2 delta)^(1/3)<=1/4. Then a n_h<=h/4 and the logarithmic term on the left is O(log h), hence the entire left side is less than h for all sufficiently large such h. This contradicts the necessary inequality. Therefore every total correct formula-only linear-clock generator satisfies T_h>delta h^3 for all sufficiently large h along its own self-description family. As m_h=h+o(h), this proves the unconditional nonvacuous lower bound Omega(m_h^3). Unlike the earlier exponential witnessed-discovery bound, this is only a cubic lower bound on formula-only discovery for linear clocks.

A sharper tradeoff: if log2 T_h=o(h) along a subsequence, then the necessary inequality yields n_h >= h/a-o(h). In particular any polynomial-time formula-only linear-clock generator, if one exists, must output formulas with at least linearly many source variables along this family, and explicit selector length Omega(h^3). This is not a proof that no such polynomial-time linear-domain generator exists.

### All polynomial clocks: exponential discovery cost without a supplied witness

Take c_h=1, e_h=2^h instead. The input descriptor still has m_h=h+o(h) bits; each individual clock is polynomial in L, with a fixed (possibly huge) exponent for that individual triple. The right side is 2^h log2(L_h+1), at least 2^h.

Suppose T_h<=delta 2^(3h) for arbitrarily large h, with the same choice of delta. Then a n_h<=2^h/4 and the logarithmic overhead term is O(h), so the entire left side is less than 2^h for all sufficiently large such h. Contradiction. Thus every total correct formula-only generator on all binary polynomial clocks, IF ONE EXISTS, satisfies

    T_h > delta 2^(3h) = 2^((3-o(1)) m_h)

in the sense of a lower bound along its self-description family (equivalently liminf log2(T_h)/m_h >= 3). In particular no polynomial-time or subexponential-time generator on this domain exists. The quantitative exponent three reflects the cubic complete selector encoding; it is not a cubic SAT decision lower bound. Output length itself has no corresponding unconditional exponential lower bound, because G can spend a very long time computing a short formula.

The all-clock existence premise is equivalent to P!=NP, so this latter resource result is conditional on existence and does not settle that premise. The linear-clock theorem is nonvacuous from the earlier quadratic-stage derivation. Both bounds depend essentially on binary clocks, the explicit output tape, and the chosen polynomial-overhead simulation. They do not apply to a generator receiving only one fixed exponent and coefficient, a succinct-output generator, or an expensive existence proof. The all-clock theorem does not directly refute polynomial formula-only generation of B_3 instances.

## 3. Exact residual-family characterization without a supplied witness

Let F be a fixed deterministic polynomial-time constructor on unary 1^n that outputs one complete satisfiable selector p_n on exactly n variables, with no witness. Its totality and satisfiability guarantee are hypotheses; no algorithm to prove them is assumed. Define its unary search relation R_F(1^n,x) iff x is an n-bit satisfying assignment of F_(p_n). The relation is polynomial-time verifiable and total on unary inputs.

The following two statements are equivalent:

(A) For every fixed positive integer k, p_n belongs to the exact B_k(n) at infinitely many n.

(B) No deterministic polynomial-time algorithm on unary 1^n returns a witness of R_F at every n.

If (A) fails, for some fixed k the stage-k search succeeds for all but finitely many n on the generated p_n. A unary polynomial-time witness algorithm computes the constructor, executes that original stage, and uses a fixed finite lookup table for the exceptional n. The time is polynomial in n for fixed k, including the complete selector length and original universal stage simulation. This contradicts (B).

If (B) fails, compile one fixed program that reads n from its actual input, computes the unary witness finder, and writes its n-bit output at the required halt position. Its runtime is polynomial in L and its description length is fixed. On each p_n the output is verified; the original length-weighted scheduler therefore includes it by some uniform exponent K (absorbing constants and finite sizes). This contradicts (A). Neither direction changes U or makes witness search free.

This identifies the exact remaining difficulty of a single polynomial-time, formula-only adversarial family that works at every exponent: it would exhibit a total polynomially verifiable search relation on unary inputs with no polynomial-time witness algorithm. Merely exhibiting a formula-only constructor of satisfiable instances, or computing their selector census, does not establish that search hardness. An existence proof of the all-exponent residual property need not supply such a uniformly constructible family. The equivalence is about a given total constructor; it does not assert that such a hard family exists, even under P!=NP. A separate constructor for each fixed k is not excluded.

## 4. Evidence and accounting

Independent scalar JavaScript generated the normalized pools for n=1,2,3, computed the first model solely from the explicit selected clauses, and compared to independently enumerated complete model sets. All selectors at n=1,2 and 258 deterministic fixtures at n=3 (empty, full and 256 masks from multiplication by 2654435761 modulo 2^N) were included. Rows [n,selectors,SAT,UNSAT,assignment-verifier calls until first model or exhaustion,sum first models,writer transitions required on SAT fixtures,total model count] are [1,4,3,1,6,1,6,4], [2,256,95,161,858,119,380,128], [3,258,16,242,2012,60,96,25]. The new Python regression reconstructs each witness using the original verifier, encodes and executes the concrete prior witness writer at 2n and 2n-1 transitions, and checks input-length bounds and exact descriptor packing. It also distinguishes a formula-only output from a witness-bearing output in a concrete clocked fixture. The small concrete writer is not a general source-to-tape compiler. Neither the exponential theorem nor the unary-family characterization is inferred from the finite regression. The general compiler, self-referential G executions, and unbounded cubic counterexample construction remain unimplemented. Independent JS did not execute the new Python module. Independent mathematical review, Lean formalization and new exact-head CI remain outstanding.

Forward TGA: BARRIER_IDENTIFIED. A uniform cheap formula-only adversary for arbitrary binary polynomial clocks is obstructed as well as witnessed discovery; fixed-stage formula-only and nonuniform/existential routes remain open. Next attack the actual B_3(n) nonemptiness at unbounded lengths with a same-clock existence argument or a direct uniform polynomial cutoff. Do not promote a discovery-cost theorem to a SAT decision lower bound. No universal obligation closes.
