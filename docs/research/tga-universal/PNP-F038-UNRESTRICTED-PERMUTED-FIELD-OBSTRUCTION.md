# F038 — Permuted-field obstruction to local representation overflow certificates

PNP_RESOLUTION_STATUS = OPEN. Parent 2cdbeed1fb8dbb68f902b40fa076fab2326c7fb1 (shared quadrant DAGs). This cycle changes direction: a rigorous asymptotic obstruction to the sufficiency of vanishing average directed loss for the three latest direct representation certificates, rather than another conditional compressor. Executed finite host audit; no compiled original-U program, independent proof review or Lean formalization. Parent combined statuses and PR-triggered runs empty; push CI unconfirmed.

## 1. Statement and exact scope

Use the inherited normalized nine-group selector family n=19m-7, L=Theta(m^3), actual negative cross-support bits of width at most three, and original fixed one-hot/OR/pin/guard extension. For m=2^d, there exists a sequence of such selectors, with designated compressed group g=0 and context groups K={1,2,3}, on which the actual unpenalized full-average facility greedy maps satisfy

    beta=1/m, delta_n=0,
    delta_w=(1-1/m)*zeta*(1-zeta) -> 0,

where zeta=Theta(1/log(d+2)). For ANY contextual maps on the same configuration the wide loss is at least (1-beta)*zeta*(1-zeta). Thus under vanishing capacity the loss cannot be made polynomially or fixed-log-power small on this configuration.

Nevertheless for the sole wide support H={0,4,5}, and the DIRECT guard (equivalently the null-template candidate), every projected coarse root of side B=2^floor(2d/3) overflows simultaneously for all three preceding certificates, uniformly over every allowed dyadic capacity 1<=C<=m^(1/32), for sufficiently large d. Consequently

    omega_dense(C)=omega_run(C)=omega_DAG(C)=1,
    min(J_dense(Z),J_run(Z),J_DAG(Z))>=1.

The earlier all-target source-only union charge tends to one and the fixed positive log-power weighted exact charge does not vanish either. The conclusion is about the direct/null-template route on the designated actual generated maps. It refutes the implication from beta,delta_n,delta_w->0 to vanishing scores of those direct certificates, even if capacity can be chosen adaptively in the allowed range. It is NOT a separation from the full earlier approximate-radius portfolio, other compressed groups or generated policies, any general physical machine class, or efficient SAT. Indeed the examples have easy witnesses and their narrow constraints force a unique source digit for each context; a guard semijoin using these constraints could eliminate all actual exceptions. The representation certificates discussed here do not perform that semijoin. The obstruction concerns their unfiltered guard before original compatibility pruning.

The proof uses a probabilistic existence construction of input bits, not a randomized witness algorithm, supplied advice, or an algorithm for finding the best permutation. No SAT time lower bound is asserted. All probability estimates below concern finite input families. A suitable deterministic input exists at every sufficiently large d, so a sequence can be fixed (for example choose the lexicographically least successful subset and permutation).

## 2. Uniform directed loss despite arbitrary free-column rearrangement

Identify real digits with GF(m) in a fixed binary basis. Let p0=1/log2(d+2). Choose an auxiliary subset J of the field, to be fixed in Section 3, with

    (p0/2)*m <= |J| <= 2*p0*m.

Put zeta=|J|/m and p=zeta*(1-zeta). For an arbitrary bijection P from the m^2 physical free-coordinate pairs to the m^2 field pairs, define

    F_H(a,x,y)=1{a*u+v in J},   (u,v)=P(x,y).

This is a genuine ternary relation on the original digits, not a new higher-width constraint. The original input explicitly lists its selected forbidden triples. The common bijection is applied to every raw row. It need not be a product of permutations of x and y; it is only a choice of input support bits.

For distinct a,b the map (u,v)->(a*u+v,b*u+v) is bijective. Therefore for every ordered nonself pair

    |Z(a,b)| = |{(x,y): F_H(a)=0,F_H(b)=1}|
             = |J|*(m-|J|) = p*m^2 = D.

Self difference zero. This is exact, for every P and J, including pairs involving digit zero. Consequently summed wide loss to any fixed target is (m-1)*D.

Define q=m/2 and T=[q,m). For each context c=(c1,c2,c3), let f(c) be the high-bit-one digit whose d-1 lower output bits are interleaved from successive low input bits of c1 and c2. Forbid high-bit-zero source digits with one unary support on g. Use binary supports {g,1} and {g,2} forbidding any source whose corresponding output positions fail to match the respective input features. Together these three supports force exactly f(c) for fixed context. All narrow bits vanish at f(c). No further cross supports are needed. The family is SAT: choose a context, a=f(c), choose a free pair outside its forbidden row (there are m^2-|J|*m such pairs), and arbitrary remaining digits. The original one-hot/OR/pin/guard extension gives a normalized witness.

At every context, f(c) uniquely minimizes the first facility's summed weighted directed loss. Its narrow loss from every source is zero; every other target acquires at least one narrow violation from source f(c) (weighted m^2), and all targets have identical summed wide loss. After selecting f(c), an additional candidate b cannot improve any source a other than b: for a distinct from both f(c) and b the wide loss remains D and narrow loss nonnegative; source f(c) already has zero loss. Source b improves by at most D. Thus every second marginal <=D<m^2, the facility penalty. Further marginal gains cannot increase under the minimum-residual rule. The unique best positive greedy round is the singleton f(c), and p_c(a)=f(c) for every source. This is a statement about actual generated maps, not a prescribed adverse map.

It follows beta=1/m, delta_n=0, delta_w=(1-1/m)*p. For arbitrary maps with representative self ties or even without requiring those ties, a self assignment implies source membership in its representative set, so the self fraction is <=beta. All nonself pairs have wide loss D; hence delta_w>=(1-beta)*p. For the indicated p0, p tends to zero but p*(log m)^A diverges for every fixed A>0.

## 3. Choose J so that distinct directed-pair strings are separated

Uniform pair loss alone is not enough for a DAG obstruction: two different source/target pairs might have identical strings. We prove that a suitable J makes ALL distinct nonself ordered pair strings separated in relative Hamming distance by at least p0^2/4.

Choose each field element independently into J with probability p0. For each lambda in GF(m) excluding 0 and 1, define

    N1(lambda)=#{A,B: A notin J, B in J,
                         (1-lambda)A+lambda B in J},
    N0(lambda)=#{A,B: A notin J, B in J,
                         (1-lambda)A+lambda B notin J}.

For A!=B the three field values in the test are distinct, since both coefficients are nonzero. For A=B the first two membership requirements conflict. Thus

    E N1=(m^2-m)*(1-p0)*p0^2,
    E N0=(m^2-m)*(1-p0)^2*p0.

Changing one field membership bit can affect at most 3m ordered pairs in either count: at most m with A equal to the changed element, at most m with B equal, and at most m with the nonzero linear combination equal to it. This deterministic bounded-difference estimate does not assume the summands in N1 or N0 are independent. The bounded differences inequality for m independent membership bits gives, for a downward deviation h, probability at most exp(-2h^2/(9m^3)). Both means exceed p0^2*m^2/4 by at least a fixed positive multiple of p0^2*m^2 for large d. Hence probability that either count is below p0^2*m^2/4 is exp(-Omega(p0^4*m)) for each lambda. A union bound over 2(m-2) counts still tends to zero. Independently the binomial subset size lies in [(p0/2)m,2p0*m] with probability tending to one (e.g. by variance and Chebyshev). Therefore there is a J satisfying these size bounds and BOTH triple bounds simultaneously. No assumption of random J once the input is fixed.

For distinct field labels a,b,c, the bijective variables A=a*u+v, B=b*u+v give c*u+v=(1-lambda)A+lambda B with lambda=(c-a)/(b-a) not 0,1. The two counts just proved are precisely the numbers of columns where F(a)=0,F(b)=1,F(c)=1 or F(c)=0. They are invariant under the common column permutation.

Now consider two distinct nonself ordered pairs (a,b),(a',b'). If b=b', then a!=a' and the event F(a)=0,F(b)=1,F(a')=1 has at least p0^2*m^2/4 columns, at which the first Z is one and the second zero. If b!=b' and b'=a, every one of Z(a,b) is zero in Z(a',b') because the latter requires F(a)=1; there are D such columns, at least p0^2*m^2/4 for large d. If b' is distinct from a,b, the event F(a)=0,F(b)=1,F(b')=0 gives at least p0^2*m^2/4 differing columns. These cases exhaust all pairs, regardless of a'. Thus all m(m-1) directed-pair strings are distinct and their relative Hamming distances have the claimed uniform lower bound. Their common one density p lies in [p0/4,2p0] for sufficiently large d. The argument uses triple counts, not an independence assumption for four labels.

## 4. Choose P to destroy aligned submatrix sharing

Choose P uniformly over the permutations of the m^2 columns, after fixing J. Let s be the least dyadic integer with

    s^2 >= 1024*d/p0^2.

Then s^2=O(d/p0^2), s divides B and s<B for sufficiently large d. Partition the full physical free square into aligned s-by-s squares. Consider the ordered string of bits of Z(a,b) on each such square in a fixed lexicographic coordinate order. We show that P can be chosen so that ALL these strings over all nonself ordered pairs and all s-squares are nonzero and pairwise distinct. This includes comparisons across different free squares and across different sources, which are essential for the shared DAG certificate.

For one square and one pair, the bits are a sample without replacement of s^2 columns; probability of all zero is <=(1-p)^(s^2). For two distinct directed pairs on the SAME square, equality means sampling no column in their symmetric difference, probability <=(1-p0^2/4)^(s^2) by Section 3. The avoidance bound follows directly from the product of successive conditional avoidance probabilities, each at most one minus the original marked fraction.

For two DIFFERENT s-squares, reveal the entire permutation on the first square. Its string is then fixed. Reveal columns of the second square in matching position order; conditioned on previous revealed columns, the remaining placement is uniform without replacement. For the second directed pair the remaining number of columns of EACH bit value is at least min(p,1-p)*m^2-2s^2, which is at least (p0/8)*m^2 for sufficiently large d. Thus at each position the probability of the bit matching its fixed first-square value, conditional on the entire previous history, is at most 1-p0/8. Probability of matching all s^2 bits <=(1-p0/8)^(s^2). This argument also covers the same directed pair on different squares; it does not incorrectly assume independent square strings.

There are at most m^2*(m/s)^2<=m^4 candidate strings and at most m^8 comparisons, plus at most m^4 zero tests. Every failure probability is at most exp(-p0^2*s^2/4) for sufficiently small p0 (in the cross-square case p0/8>=p0^2/4). By the chosen s this is <=exp(-256d). Multiplying by m^8=exp(8d ln 2) tends to zero. Therefore with probability tending to one all nonself strings on all s-squares are simultaneously nonzero and pairwise distinct. This is a global event, not a separate choice of permutation for each root.

## 5. Also force high canonical run weight

With the same random permutation, we establish two further events simultaneously for EVERY nonself pair and EVERY aligned B-square. A pair's row on the B-square is a uniform ordered sample without replacement from a fixed population of m^2 bits with p*m^2 ones. Since B^2/m^2=O(m^(-2/3))=o(p), after at most B^2 exposures each bit value still has remaining count at least half its original count for sufficiently large d.

First, for each pair of adjacent x traces in that row, expose corresponding bits in successive y positions, two at a time. Conditional on any previous exposures and on the first bit of a pair, probability the second bit differs is at least p/2 (p<=1/2). The probability the complete two traces are equal is <=(1-p/2)^B. A union bound over at most m^2*(m/B)^2*B<=m^5 such tests tends to zero, since p*B grows exponentially in d. Thus every adjacent pair of x traces differs on every such B-row.

Second, across all x coordinates of one B-square, partition each y trace into disjoint adjacent y-pairs. There are B^2/2 pairs. For each expose its first then second bit. Conditional on previous pairs, probability of first zero is at least (1-p)/2, and, given that zero, probability second one is at least p/2. Hence probability of a 01 pair is at least p/8 (a conservative constant). The number of 01 pairs stochastically dominates a binomial with B^2/2 trials of probability p/8: use independent uniform variables to generate successive conditional Bernoulli successes, or apply the exponential-moment proof of the binomial lower-tail bound using the conditional probability lower bound. Therefore probability of fewer than p*B^2/32 successes is <=exp(-p*B^2/128). A union bound over at most m^4 pair/square combinations tends to zero.

Every 01 pair begins a distinct maximal y-run of ones within its x trace. Since adjacent x traces differ, every nonempty trace occupies its own maximal equal-trace slab; separated equal traces cannot be merged through an intervening different or empty trace. Consequently the preceding canonical run representation's weight for each nonself row on each B-square is at least p*B^2/32. No assumptions about a particular algorithm's chosen node IDs or run ordering.

The failure probabilities in Sections 4 and 5 sum to o(1). Fix ONE permutation P satisfying all events. This is the existence step for the selectors; the finite audit below does not claim to construct this asymptotic event or certify its constants by extrapolation.

## 6. Every coarse root overflows

Take the actual greedy maps from Section 2. In every aligned K context cube of side B, all q=m/2 target digits occur equally often: all input feature positions of f are below log2 B for sufficiently large d, so all required bits vary independently over their full range. This holds regardless of the high context bits. For any actual source a, at least q-1 distinct target digits are nonself, whether or not a belongs to T. Every projected coarse B-root has B sources (m is power of two, no padding), and uses the same q targets across its context intervals. Every corresponding nonself local row is nonzero, and distinct even across sources, by Section 4 applied to any constituent s-square. In particular, the following lower bounds apply also on source roots wholly inside the unary-allowed high-bit-one domain.

Dense-row quotient: each source has >=q-1 nonzero distinct rows. Its allowed cap C*B <=m^(1/32)*B=o(q). Hence every root overflows.

Run-coded quotient: at least B*(q-1) source-specific rows, each with weight >=p*B^2/32 by Section 5. Total

    W_run >= p*(q-1)*B^3/32.

The ratio to maximum C*B^4 is >=p*(q-1)/(32*m^(1/32)*B), diverging as m->infinity. Here B=Theta(m^(2/3)) and p=Theta(1/log d). Thus every root overflows, even though individual rows have vanishing one density.

Shared quadrant DAG: at level log2 s, each root row has (B/s)^2 aligned submatrices. Every submatrix over all B*(q-1) nonself pair rows and all constituent s-squares is nonzero and distinct by Section 4. All are reachable from actual row pointers because each target occurs in the context cube. The canonical ordered DAG MUST have a distinct node for each such distinct nonzero matrix at that level (by its own recursive equality definition). This is a representation-specific lower bound, not a bound on arbitrary program descriptions. Thus

    W_DAG >= B*(q-1)*(B/s)^2 = (q-1)*B^3/s^2.

Divide by the maximum cap m^(1/32)*B^4 to get >=(q-1)/(m^(1/32)*B*s^2), which diverges: s^2=O(d*(log d)^2), and the remaining positive polynomial exponent is 1-1/32-2/3=29/96. Hence every root overflows. Cross-source sharing, cross-row sharing, implicit zero and all reachable-node compaction are already accounted for. Merely counting distinct whole rows would not establish this DAG bound.

At each allowed capacity, all first-overflow cubes for each representation are the B-roots themselves. They partition the real projected domain exactly because M=m. Their normalized volume is exactly one, not just bounded away from zero. This proves the score obstruction in Section 1. Even selecting the representation independently at each root among these three at the same permitted maximum capacity cannot avoid this particular root obstruction. No claim about altering the root scale, unrestricted capacities, alternative encodings, or filtering with original constraints.

## 7. Other direct-route charges and implications

For the null-template candidate all centers equal the source, so missing-bit guard is exactly Z. For a field column with u!=0 the map b->b*u+v is bijective; some target forbids the column and some allows it. For u=0 all raw rows agree and no directed exception occurs. For each u!=0 there are m choices of v, and for each such column exactly m-|J| old source digits have a zero. Consequently the all-target source-only union has exact cardinality

    |U_H|=(m-1)*m*(m-|J|),
    eta_H=(1-1/m)*(1-zeta) -> 1.

The common permutation preserves that cardinality. Exact correction density kappa=delta_w has slow order Theta(1/log d). For every fixed positive D0 the prior log-weighted charge (1+ceil(log2 m))^D0*kappa diverges. Thus adding those two earlier correction choices to the THREE direct certificates cannot yield a vanishing score on the same null-template candidate.

The crucial distinction is that density counts ones with multiplicity across contexts, whereas these representations' capacities measure distinct strings/submatrices or run complexity. The field construction fixes all pair losses exactly and the common column permutation can change local representation complexity without changing any of those losses, the narrow bits, or the greedy facility optimization. Low average directed loss therefore cannot alone justify tight first-overflow volume for these certificates.

This is not an impossibility theorem for every future representation. For example, the full raw restricted cache on a coarse B-square has m B^2 bits, below B^4, and an alternative factorization retaining those raw bits and actual maps may be compact at the root. Its local physical transfer cost and descendant restrictions would need separate analysis. Likewise the original narrow constraints force f(c), so a semijoin that first conditions on original feasible source/context keys would remove every actual Z exception on this simple family. This illustrates why the certificate obstruction is not a SAT lower bound. The next useful direction is to incorporate original compatibility before evaluating representation complexity or exploit asymmetric factorizations that preserve the raw-field structure. No universal guarantee from the present example.

## 8. Executed finite host regression

Standalone JavaScript audit executed in the tool runtime and committed with identical Node entry point. An initial longer draft failed to parse; replaced it with the committed shorter audit and executed successfully. It uses deterministic seeded shuffles, not a cryptographic RNG or uniform probability experiment. At m=16,32,64 select the best of eight finite fixed-size subsets J (|J|=m/4) using the actual triple minima, then permute all free columns. Check finite field multiplication is bijective for each nonzero factor, all ordered nonself directed losses before and after permutation, affine-ratio triple formula, exact union cardinality, unique first greedy facility and every second marginal for each possible forced target, and target coverage in a finite coarse context cube. Record actual levelled distinct nonzero submatrix counts and exact per-source deduplicated run weights at three sampled coarse roots per domain.

Counts:

    5,264 ordered pair loss comparisons (each before and after permutation)
    848 finite affine-ratio triple partition checks
    768 direct triple formula comparisons
    56 unique first facility checks
    2,632 second marginal checks
    336 context feature evaluations
    552,212 submatrix occurrence comparisons
    1,987 canonical run-weight computations
    5,376 column union checks
    890 exact small-urn sampling inequality checks.

Field summaries [m,|J|,D,min N1,min N0,|U_H|]:

    [16,4,48,10,36,2880]
    [32,8,192,43,145,23808]
    [64,16,768,183,567,193536]

Greedy summaries [m,q,max second marginal,coarse target count]:

    [16,8,48,8]
    [32,16,192,16]
    [64,32,768,32]

Finite tile summaries [m,B,source offset,free x offset,free y offset,nonself row occurrences,min distinct nonzero rows per source,distinct node counts by increasing dyadic side,total DAG nodes,run weight,adjacent equal trace occurrences,disjoint 01 occurrences]:

    [16,4,0,0,0,32,8,[1,10,19],30,174,21,47]
    [16,4,12,4,0,28,6,[1,10,17],28,170,7,39]
    [16,4,0,12,12,32,8,[1,12,23],36,217,6,43]
    [32,8,0,0,0,128,16,[1,15,278,127],421,2360,38,731]
    [32,8,24,8,0,120,15,[1,15,231,119],366,1989,21,606]
    [32,8,0,24,24,128,16,[1,14,243,128],386,2104,51,520]
    [64,16,0,0,0,512,32,[1,15,1980,2014,512],4522,28619,19,10017]
    [64,16,48,16,0,496,31,[1,15,1842,1957,496],4311,27947,27,10024]
    [64,16,0,48,48,512,32,[1,15,1887,2021,512],4436,28840,19,10010]

These finite sizes do NOT satisfy the asymptotic s requirement, and the finite DAG counts are below B^4 in these examples. They do not demonstrate simultaneous actual overflow. Adjacent equal traces at finite sizes are expected. The finite B choice for m=32 is 8 (the production largest dyadic with B^3<=m^2), others likewise. Arithmetic-only controls [d,log2 B,log2 s,log2 maximum cap,log2 conservative DAG lower bound,log2 ratio] are:

    [128,85,12,344,357,13]
    [256,170,13,688,738,50]
    [512,341,13,1380,1507,127]
    [1024,682,14,2760,3040,280]

These evaluate the proven bound assuming the existence events, not actual enumeration at those domain sizes. The audit only asserts s<B; the positive ratios are recorded. Small urn tests directly enumerate samples without replacement and conditional remaining-bit probabilities, not the full asymptotic concentration argument.

All committed assertions passed. Host indexed arrays, field multiplication and explicit dense strings are used only for testing. No physical sorting/sweeps, original normalized encoder/verifier integration, compiled transitions, actual U stage, independent review, Lean formalization or exact-head CI confirmation. This cycle proves a conditional-scope negative mathematical result about scores; it does not extend the prior time upper bound to arbitrary low-loss maps.

## 9. Disposition

The three latest direct representation certificates (dense row, canonical run, shared quadrant DAG) can all fail maximally on the SAME actual full-average greedy maps with genuinely slow vanishing loss. This is a concrete obstruction to inferring their scores from average loss alone, not a barrier to all possible algorithms. The all-target union and fixed-log-weighted exact corrections fail on the same null-template candidate. Next investigate original-feasibility semijoins and asymmetric local factorization before representation certification; do not assume more lossless compression formats will resolve the unrestricted implication. General arbitrary-slow full-average recovery, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Previously reported finite interval 52..233 and Lean census 1603 unchanged, not recounted. Promotion NONE.
