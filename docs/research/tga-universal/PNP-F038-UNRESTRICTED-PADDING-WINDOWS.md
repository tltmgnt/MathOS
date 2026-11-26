# F038 / unrestricted route — simultaneous residual transfer across polynomial length windows

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Parent 8059232a68660d3f147355b34b3cb05a040087da: https://github.com/tltmgnt/MathOS/actions/runs/45743460207 (success). Six parent workflows passed at inspection; TOPO-406 was still running.

## Objective and main result

The prior reduction gives an exact single-support ternary normal form at the one target size 3n+7. This cycle develops an injective seeded padding transfer across EVERY size in a polynomial-length interval, with one uniform source algorithm that searches all target sizes and seeds. It rules out a potential intermediate resolution in which a fixed polynomial stage has easy (or polynomially small residual) sizes at polynomially bounded gaps. The result is conditional on P!=NP when asserting unbounded hard windows. The transfer inequality itself is unconditional. No new unconditional cubic failure is claimed. Same U, exact complete selector representation, original verifier and length-weighted clocks.

Write D_h for ALL selectors at source size h consisting exclusively of width-three clauses with at most one selected clause on each support. Do not confuse D_h with the rigid previous image C_h at h=3n+7. Let L(n)=n+1+2n+4 binom(n,2)+8 binom(n,3) and B_k(n) be the satisfiable selectors missed by the exact stage k ceil(log2 L(n)).

For every fixed integer k>=1, a>=2, d>=1, there exist fixed integers K>=k and n0 such that for ALL n>=n0 and EVERY integer h in [4n+7,(4n+7)^a],

    |B_k(h) intersect D_h| >= h^d |B_K(n)|.

More strongly, the same single source p in B_K(n) forces every one of its h^d padded variants at every such h to fail stage k. Neither the source witness nor a successful target size is given to the search algorithm. K is an existential absorbed polynomial exponent, not k. This is an amplification of the earlier one-size injection and residual census.

## 1. Injective padding with exact model correspondence

Reuse the proven single-support normal form f_n(p) on h0=3n+7 variables: seven gadget variables pinned to zero; two equal polarity copies and one forced dummy per original variable; translated clauses supported on distinct triples. The first two gadget variables (numbered 1,2) are zero on every model. For h>=h0 and integer z in [0,2^(h-h0)), add for each new variable v=h0+1,...,h one clause

    (x_1 OR x_2 OR l_v),

where l_v is positive if bit v-h0-1 of z is one, negative otherwise. The clause is on a new support {1,2,v}; all these supports are different and none intersect the previous selected-support collection as equal sets. There are no selected units or binaries. Denote the complete h-variable selector by Q_(n,h,z)(p). Every model must assign the new bits exactly as z. Every old model has exactly one such extension. Thus projection onto the original u_i bits is a bijection of model sets, preserving exact count, SAT, UNSAT and uniqueness.

For fixed n,h the map (p,z)->Q is injective: recover p by the known translated-clause positions, and z by the sign chosen at each padding support. At each allowed h the new variables have precisely one pin clause each, so the support property holds for every seed including zero. There are no complete seven-of-eight supports; the n disjoint dummy triples from the original reduction remain irreducible. This is a normal-form construction for every integer h beyond the base, not only one arithmetic progression.

For the desired census use seeds 0<=z<h^d. Their binary length is at most ceil(d log2 h). With 4n+7<=h<=(4n+7)^a, the padding has h-h0>=n bits, whereas ceil(d log2 h)<=ceil(ad log2(4n+7)). Therefore for fixed a,d all seeds fit for every h in the window once n is sufficiently large. Choose n0 so this holds uniformly. The constructor does not require finding a model: generate the base normal form clauses, add the new pins, and emit the full normalized h-variable selector tape. Its bit cost is polynomial in L(n)+L(h)+log(z+1), by enumerating/sorting clause indices or sequential full pool generation. The target L(h)=O(L(n)^a) for fixed a; there is no compressed or free padding.

## 2. A uniform window search forces simultaneous rejection

Fix k,a,d. Define a SINGLE fixed deterministic algorithm A on an arbitrary valid original selector p. For each integer h in the stated finite window and every seed z<h^d, construct Q and run the original U stage at precisely s=k ceil(log2 L(h)). If it returns a verified witness, project to the original n variables, verify against p and return it. Otherwise move to the next pair; if none succeeds return FAIL (no UNSAT assertion). For n below the fixed capacity threshold, choose any bounded behavior, since the transfer only asserts n>=n0. The algorithm is total and polynomial time for fixed k,a,d: there are O((4n+7)^(a(d+1))) pairs, each target has polynomial complete length, and the previously established stage bound is polynomial in target length at fixed k. Charge all stage simulation, selector construction, arithmetic, output verification and repetition. Standard polynomial-overhead fixed multitape-to-three-symbol one-tape simulation and final positioning of n output bits give a fixed original general description of A. Hence some fixed integer K>=k covers every successful execution on the original p by stage K ceil(log2 L(n)), absorbing fixed description length, all polynomial overheads and finite exceptions. No explicit numerical K or compiled description is provided.

Suppose p belongs to B_K(n). Then p is SAT, so every Q in the window is SAT. If even ONE pair (h,z) succeeds at its own stage k, A would produce a verified model on p, contradicting its membership in B_K(n). Consequently every such Q belongs to B_k(h) intersect D_h. This conclusion is simultaneous in h and z for that same p; it does not require a different source failure at each target size. Distinct source selectors and seeds yield distinct Q at a fixed h. Counting gives the main inequality. The theorem transfers failure from a potentially stronger source stage to a weaker target stage, not conversely. In particular known unbounded stage-two failures do not imply unbounded stage-three failures.

## 3. Conditional density-one subsequences of hard sizes

Under P!=NP, the earlier exact-U equivalence gives B_K(n) nonempty for arbitrarily large n at every fixed K. Thus for EVERY fixed k,d and a>=2 there exist arbitrarily large m=4n+7 such that for EVERY integer h in [m,m^a],

    |B_k(h) intersect D_h| >= h^d.

No randomized hypothesis such as NP!=RP is needed for this implication. It is a consequence of deterministic polynomial search across all padding variants, not a new proof of P!=NP. At a=2, let T_{k,d}={h: |B_k(h) intersect D_h|>=h^d}. Taking H=m^2 along these windows, |T_{k,d} intersect [1,H]|/H >= (m^2-m+1)/m^2 tends to one. Hence T_{k,d} has upper asymptotic density one (limsup equals one). This is density of SOURCE SIZES, not of selector strings. It does not establish natural density one or lower density one, and it does not contradict the earlier planted-density upper bound for a different quantity.

In fact the following is exactly equivalent to P=NP:

    There exist fixed integers k>=1, a>=2, b>=0 and m0 such that
    for every integer m>=m0 there is some h in [m,m^a] with
    |B_k(h) intersect D_h| <= h^b.

The forward direction uses a fixed uniform U cutoff (empty residuals). For the converse, if P!=NP apply the window theorem at d=b+1 with the same k,a. Its arbitrarily large windows contain no such h, contradiction. This characterization does NOT require a computable rule identifying the sparse residual sizes, or supplying lists of their bad selectors. The proof is by contrapositive using the unconditional transfer and the earlier equivalence. In particular if a fixed stage is universally successful at even one size in every polynomial window eventually, then P=NP; the successful size set need not be computable. Infinitely many successful sizes with no polynomial gap restriction are not enough for this conclusion.

The argument also yields, under P!=NP, a sequence of windows with simultaneous bounds for every fixed k,d eventually along that sequence: at step j apply the theorem for k=d=j,a=2 and choose a start m_j increasing so windows are disjoint. For fixed k,d, j>=max(k,d) and monotonicity of stages in k give the desired count. No effective procedure for selecting m_j with efficient discovery or for finding the source witness is proved.

## 4. Validation and boundaries

Independent JavaScript generated the actual clause pools, cyclic gadget and polarity-copy mapping, then padded every selected formula at the six target sizes h=14,15,16 for n=1 and h=18,19,20 for n=2, with d=1 and every seed z<h. Used all four n=1 selectors and sixteen explicit n=2 masks. Verified full target support uniqueness, exact model correspondence, distinct target keys, and rejection after flipping any forced padding bit of a valid model. Independently predicted exact stage 0,1,2 outcomes on the two endpoint seeds: no general descriptions or exhaustive built-in are active, the gadget forces all low output bits zero, and stage succeeds precisely at s>=1 on seed zero when the source has witness zero. The submitted Python regression uses the actual parent normal-form helpers, original selector pool, original verifier, inverse mapping and actual stage calls at these small stages. It also replays a finite window search with the original stage at fixed s=0,1,2, not a full polynomial stage for these sizes. The independent finite expected wrapper call counts are 180,92,92; no input search is classified UNSAT from failure. Rows and all counts are recorded in the plan JSON. Independent JS did not execute Python. No arbitrary larger-stage run, explicit generic U compilation, numerical K, independent mathematical review or Lean formalization is supplied; new exact-head CI remains outstanding.

The finite fixture windows are intentionally small and test the seeded transformation and search logic, not the asymptotic interval theorem by computation. The latter is a mathematical consequence of a fixed polynomial-time wrapper. There is still no unconditional unbounded cubic counterexample theorem. The new result describes what must happen if the unrestricted lower bound is true: large simultaneous failure windows and polynomial residual multiplicity throughout them. It cannot be used in reverse to infer P!=NP merely from finite windows.

Forward TGA: BARRIER_IDENTIFIED. Next investigate whether the compact exact residual predicate has an unconditional nonempty solution at unbounded cubic lengths or prove a uniform cutoff, respecting the source/target exponent distinction. No universal obligation closes.
