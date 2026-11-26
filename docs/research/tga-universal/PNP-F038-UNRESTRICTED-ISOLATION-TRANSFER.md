# F038 / direct unrestricted route — exact unique-witness isolation and residual mass

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Parent b851e6a7927d00c156fae43ec6ab26d39214756f: https://github.com/tltmgnt/MathOS/actions/runs/45738606088 (success). Six parent workflows succeeded at inspection; TOPO-406 was still running.

## Scope and outcome

Keep the identical universal scheduler U, normalized universal selector input, general tape machine descriptions, built-ins, verifier and stage clocks. The previous finite cubic counterexample is now replayed by exact-head CI. The remaining goal is bad inputs at unbounded lengths for k=3 and ultimately every k, or a universal polynomial success bound. This cycle investigates whether the remaining failure can be concentrated on uniquely satisfiable inputs, thereby eliminating witness multiplicity as a source of ambiguity. It gives an exact randomized transfer and a deterministic conditional route, NOT an unconditional new exponent. The isolation argument is classical pairwise-independent hashing (Valiant-Vazirani style), specialized here to the same U with an injective selector construction. No novelty claim. Seven MRA-X roles are authored local records, not independent agents.

## 1. Uniform injective isolation encoding

Let F_p be the selected formula on n>=1 source variables. Choose r in {1,...,n+1}. A seed consists of (n+1)^2 independent bits, encoding n+1 rows of n coefficients a_ij and an independent offset b_i per row. For each row i allocate n+1 fresh variables y_i0,...,y_in, distinct from the original variables and every other row. Force y_i0=b_i by a unit. For j>=1 force

    y_ij = y_i,j-1 XOR (a_ij AND x_j).

For a_ij=0 use the two binary equivalence clauses. For a_ij=1 use the four ternary clauses of the XOR truth table. Force y_in=0 for exactly the first r rows by negative units. All rows, including the unconstrained final rows, have their entire chain of definitions. No free auxiliary variables are introduced. Let Q(p,r,seed) denote the selector of this conjunction, including all original clauses, on exactly h=n+(n+1)^2 source variables. L(h)=Theta(n^6)=Theta(L(n)^2). The full universal pool and selector bits are generated and charged.

For every original x there is exactly one extension to all row variables that satisfies the definitions, by induction in j. It is a model of Q exactly when x satisfies F_p and the first r affine hash equations vanish. Thus the projected model count is preserved exactly, not just equisatisfiability. Every verified witness for Q yields a verified witness of F_p by dropping the fresh variables. In particular a single surviving original model gives a uniquely satisfiable full selector (including all auxiliary variables).

The map (p,r,seed) -> Q is injective at each fixed n. Restrict to original-only clauses to recover p. The start units recover offsets. At each chain step the coefficient is zero iff the defining clauses are binary; otherwise the four ternary clauses mention x_j. The end units recover exactly r. These groups cannot collide: fresh row-variable supports are distinct, and none coincide with original-only clauses. Fixed h is a strictly increasing function of n. The constructor and decoder are polynomial in L(n), including the explicit selector length, and do not search for models.

## 2. Exact isolation probability

Let M>=1 be the number of original satisfying assignments (unknown to the algorithm). Choose r*=ceil(log2 M)+1, which belongs to the allowed range. For a uniformly sampled seed, a fixed x has independent fair hash bits across rows, hence probability 2^-r to pass the first r rows. For distinct x,x', one coordinate differs; the random coefficient on that coordinate and the independent offset imply that the pair of row outputs is uniform on {0,1}^2. Rows are independent. Thus the survival indicators are pairwise independent.

Let Z be the number of surviving original models. Put lambda=M/2^r*. Then 1/4<lambda<=1/2. We have E Z=lambda, E[Z(Z-1)]=M(M-1)2^(-2r*)<=lambda^2. For every integer z>=0, indicator(z=1)>=z-z(z-1) (equality for z=0,1,2). Taking expectations,

    Pr[Q(p,r*,seed) has exactly one full model]
      >= lambda-lambda^2 >= 3/16.

The algorithm does not need M or r*. It tries every r from 1 through n+1, with independently sampled seeds. This costs only a polynomial factor. Model count is used in the proof only. No promise about the input model count is needed.

## 3. Same-U stage transfer and quantitative unique residual census

Fix integer k>=1 and write A_k(p,r) for the probability (over a uniform seed) that the actual U succeeds on Q at its own exact stage k ceil(log2 L(h)). A trial constructs the full selector, calls the original bounded stage, and projects and verifies any returned witness. It never accepts an unsatisfiable original input. Its cost is polynomial in L(n) for fixed k, using the previously charged stage bound and the polynomial encoding blowup. Random bits are charged explicitly.

For any fixed positive integer d, suppose for every satisfiable p of sufficiently large source size there is some r with A_k(p,r)>=L(n)^(-d). Then a randomized polynomial witness algorithm tries all r, with ceil(2 L(n)^d) independent trials per r. The failure probability for that r is at most exp(-2)<1/2. On no instances no verified witness is possible. A finite number of smaller sizes can be handled by exhaustive search. This gives SAT in RP and hence NP=RP. The implication holds for arbitrary underlying deterministic algorithms in U; it does not establish P=NP. The exponential inequality is used only for the randomized analysis.

Taking the contrapositive: under NP!=RP, for every fixed k,d there are satisfiable p at unbounded n with A_k(p,r)<L(n)^(-d) for EVERY r. At the correct r* for those p, subtract the probability of any stage success from the isolation probability. For all sufficiently large such n,

    Pr[Q has one model AND belongs to B_k(h)]
      >= 3/16 - L(n)^(-d) >= 1/8.

Write B_k^uniq(h) for the uniquely satisfiable members of the exact residual B_k(h). Injectivity then proves

    |B_k^uniq(n+(n+1)^2)| >= 2^((n+1)^2-3)

for unbounded n, for EVERY fixed k, under NP!=RP. In terms of the actual enlarged encoded length this is exp(Omega(L(h)^(1/3))) on that subsequence. At k=3 this is a conditional exponential census of uniquely satisfiable cubic failures, not an unconditional unbounded cubic result. The assumption NP!=RP is strictly no weaker than P!=NP (P subset RP subset NP); it must not be replaced by P!=NP. This is a witness-preserving transfer with no free sampling oracle or adaptive SAT calls.

## 4. Deterministic route and exact unresolved discovery obligation

For a fixed k, if B_k^uniq(h) is empty at all sufficiently large h, the randomized construction above works with success probability at least 3/16 at r*, so NP=RP. If additionally there is a deterministic polynomial-time procedure on input p that outputs a polynomial-size list of pairs (r,seed) including an isolating pair for every satisfiable p, then the same construction becomes deterministic: test every pair by the actual U stage and verify any witness. With finite small-size exceptions handled exhaustively this implies P=NP. The list generator itself is an additional hypothesis. It may not use the unknown M or a satisfying assignment for free. No deterministic isolation theorem is proved here.

For comparison, existence of a small NONUNIFORM list is elementary. If U succeeds on all sufficiently large unique queries, sample independent complete seed lists (one seed per r per trial). Each satisfiable p has failure probability at most (13/16)^t across t trials. There are 2^N original selectors at n, so t=4(N+1) trials suffice for the union bound to be <1: (13/16)^4<1/2. Some common list therefore succeeds on every satisfiable p at that size. Its total bits are polynomial. This supplies polynomial advice, not a uniform deterministic algorithm; it cannot be treated as a proved efficient list discovery procedure. More generally, if a polynomial-time method provides lists with the required coverage and the actual stage succeeds on every unique query, the deterministic route closes. An unconditional proof of either the stage property plus discovery, or of unbounded failures for every exponent, remains absent.

## 5. Evidence

Independent JS exhaustively enumerated original selectors of n=1,2, every row count and every seed, computing the number of surviving original assignments from the affine hash itself. Metrics [n,source formulas,SAT formulas,queries,zero survivors,unique survivors,multiple survivors,sum survivors,unique survivors at r*]:
[1,4,3,128,85,38,5,48,22], [2,256,95,393216,342081,45364,5771,57344,22388].
The minimum number of isolating seeds at r* was 6 of 16 for n=1 and 147 of 512 for n=2. The reference also constructed actual normalized clause lists and verified injectivity, extension truth and single-auxiliary-bit flips, using all seeds for n=1 and eight seeds (0,1,7,85,170,255,256,511) for n=2. Rows [n,queries,selected clauses summed,canonical extension tests,accepted extensions,auxiliary flip checks,full assignment checks]:
[1,128,1344,256,48,1024,4096], [2,6144,158208,24576,1472,221184,0].
The full assignment tests for n=1 compare the entire model set to the canonical extensions. Single flips alone would not prove uniqueness at n=2; the general chain induction proves it, and the finite tests are regression. The reference also computed exact built-in stage outcomes at stages 0..8 on the 128 n=1 isolation selectors (enlarged size five). Python calls the original stage on those actual selector masks, checks projection, and compares the independent counts. General tape descriptions are not active at these small stages; the mathematical transfer includes all programs through the actual stage bound. JS did not execute Python. The finite queries do not demonstrate the asymptotic cubic failure claim. Exact-head CI, independent mathematical review and Lean formalization remain outstanding.

Forward TGA: BARRIER_IDENTIFIED, with exact unique-witness and randomized transfer. The next mathematical obligation is an unconditional unbounded B_3 construction or a resource-preserving deterministic cutoff. The isolation transfer exposes the distinction between randomized and deterministic discovery; no hypothesis or finite computation closes a universal obligation.
