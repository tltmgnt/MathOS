# F038 — sharp product-isolation query bound and larger shattered selector universe

PNP_RESOLUTION_STATUS = OPEN. Mathematical black-box oracle bounds and same-layout normalized construction, finite reference checks; not an original-U runtime lower bound, compiled machine, Lean proof, or independent review. Parent 72b50abb2ebc3a6a0669380296dfffffc2e1d30d (product isolation). Available connector returned no statuses or PR-triggered workflow runs for parent; push-triggered CI unconfirmed.

## 1. Result

The previous product-isolation upper bound O_r(log^r(m+2)) independent random trials is asymptotically optimal in a precisely specified black-box model, even allowing adaptive product restrictions and witness-returning answers. For fixed r>=3, bounded-error randomized one-sided search requires Omega_r(log^r m) queries in the worst case. This holds even when the hidden original solution set is a Cartesian product of nonempty coordinate subsets, hence comes from the full distributed family using unary clauses alone. It is NOT a lower bound on reading the actual SAT input, which exposes these unary bits.

For deterministic black-box isolation, enlarge the previous shattered universe from m^3 tuples to

    N=27(m-1)^3

in the full r=9 normalized family. Every subset of these N tuples is realized, with exactly one full assignment per retained tuple, fixed n=19m-7 and fixed pins. Consequently even adaptive deterministic black-box isolation with arbitrary subset queries (not just product restrictions) needs at least N queries in the worst case. The same N lower bound holds for a nonadaptive universal isolation list. This improves the earlier m^3 lower bound by an asymptotic factor of 27, without changing the normalized length or weighted clocks.

## 2. Oracle model and its limitations

The unknown object is V subset [0,m)^r, a surviving tuple set of a promised-family selector. An isolation query chooses a product box B=product D_g (or an arbitrary subset in the separately stated stronger deterministic lower bound). A response is the unique tuple in V intersect B if that intersection has size one, and a single symbol NO otherwise. NO conflates an empty intersection with an intersection of size at least two. The algorithm may adapt its next query to earlier answers and may use randomness, but has no access to the original clause bits or other information about V. It must never output a witness on the empty set and must return a valid witness with probability >=2/3 for each nonempty V (deterministic search must always be correct). It may stop at the first positive answer. For one-sided algorithms on the all-NO transcript no witness may be output: that transcript is identical on V=empty, up to any termination, including for each random seed outside a probability-zero exceptional set.

The oracle is the weakest witness interface consistent with the earlier conditional unique-coverage hypothesis U_r: it guarantees a witness on unique restrictions and no false witness, but provides no assistance on multi-model restrictions. Actual U can accept multi-model inputs, and algorithms can read the explicit selector, use rejection certificates, or interleave partial machine executions. Therefore a black-box bound here does not establish an actual stage lower bound or refute U_r.

## 3. Optimal randomized product-query count

Let k0=floor(log2 m)+1. Define a hard distribution for a single coordinate W: choose j uniformly in 0..k0-1; include each of the m digits independently with probability p_j=2^(-j); condition the resulting W on being nonempty. Before conditioning, nonemptiness has probability >=1-(1-1/m)^m>=1-e^(-1)>1/2, since p_j>=1/m for every j.

For a fixed query subset D of size a>=1, the unconditional probability of exactly one selected member at level j is

    f_a(p_j)=a p_j (1-p_j)^(a-1).

For every 0<p<=1, including a=1,

    f_a(p) <= 2[(1-p/2)^a - (1-p)^a].

Indeed the difference of powers is the integral of a(1-u)^(a-1) from p/2 to p, whose integrand is at least a(1-p)^(a-1). Sum over the dyadic levels; the right sides telescope to at most 2. Therefore the mixture probability is <=2/k0 and after conditioning on W nonempty it is <=4/k0. For a=0 the probability is zero. This is an elementary bound uniform over all query subsets, not a heuristic about random instances.

Choose r such W_g independently (each individually conditioned to be nonempty). Put V=product W_g. V is always nonempty and is realizable in the full selector family by forbidding digits outside W_g with existing negative units and selecting no other cross clauses. A product query B=product D_g isolates a unique tuple iff |W_g intersect D_g|=1 for EVERY g. By independence the probability for any fixed query is at most (4/k0)^r.

For a deterministic adaptive algorithm, list its first q queries on the all-NO path, or fewer if it terminates earlier. A positive answer in the first q queries on any input can occur only at one of these fixed queries (up to the first positive, the actual path equals the all-NO path). A union bound yields probability at most q(4/k0)^r over the hard distribution. For a randomized algorithm condition on the random seed, apply the same bound to its fixed all-NO path, then average. Since a one-sided witness search needs a positive answer, worst-case query budget q and success probability >=2/3 for all nonempty V imply

    q >= (2/3)(k0/4)^r.

The lower bound also holds in order of magnitude for worst-case expected query count: truncate after ceil(3E) queries if E bounds the expectation on every input; by Markov the probability of truncation before termination is at most 1/3, so success is >=1/3 on every nonempty input, and the same argument applies with 1/3. The previous note's independent product sampling with probability >=(3/(16(ceil(log2 m)+2)))^r gives a matching O_r(log^r(m+2)) upper bound for worst-case query budget (or expected trials). For fixed r, the optimal bounded-error one-sided product-query complexity is thus Theta_r(log^r(m+2)), including r=9. This statement counts queries, not random bits, CPU operations, original-tape transitions or description penalties. Arbitrary non-product queries need not obey the r-fold lower bound.

## 4. Enlarged exact shattered universe in the original selector

Use n=19m-7 and the inherited nine one-hot groups X_g[a]=gm+a+1, zero pins, OR auxiliaries and guard clauses. Here digit zero denotes inactive and digits 1..m-1 active. Partition the nine groups into three disjoint triples of consecutive groups, indexed h=0,1,2, with group numbers 3h,3h+1,3h+2.

For each cluster add:
* negative binary clauses forbidding any simultaneous active choices in two of its groups, for all pairs of nonzero digits;
* the one negative ternary clause selecting the three zero digits in that cluster, forbidding all three groups inactive.

These 9(m-1)^2+3 distinct fixed cross clauses enforce exactly one active group and a nonzero digit per cluster. There are D=3(m-1) choices of active (group,digit) per cluster, and exactly N=D^3 surviving structural tuples. This is an equality-free construction in the full family; no extra variables or width-four clauses.

For each triple of active (group,digit) choices, one from each cluster, choose its cross negative ternary clause independently. In the structural universe this clause is violated by exactly the corresponding tuple: the active digits fix the one active group in every cluster, and the other groups are forced to zero. Conversely each structural tuple violates exactly one of these N distinguished clauses. They are distinct canonical positions, disjoint from the structural and inherited fixed clauses (the structural ternaries are contained within one cluster and use only zero digits). Selecting a subset of the distinguished clauses deletes precisely its corresponding tuples.

Thus the family realizes EVERY subset of the structural universe, including empty and singleton, with exactly one full assignment per retained tuple by the inherited fixed extension. There are 2^N distinct normalized inputs in this subfamily, fixed n, L=n+1+2n^2+8 binom(n,3), pins and clocks. In particular N/m^3 tends to 27. This is not a claim that all V of this cardinality are hard to solve: this structural subfamily has a direct sequential mask scan and a fixed O(L^2 polylog L) original solver by the same construction as the earlier independent-mask families. The actual selector makes the allowed active triples explicit.

## 5. Deterministic adaptive lower bound

For any list of fewer than N subset queries R_i, restrict them to the structural universe W of N tuples; they need not be products. Begin with W and repeatedly find a query intersecting the current set in exactly one element, then delete that element. Each query used this way becomes disjoint from all subsequent sets and cannot be used again. After at most the list length deletions the remaining set V is nonempty, and the process stops only when no query isolates it. Since every subset V is realizable, all the list's queries return NO on this nonempty instance.

Apply this to the list of queries on a deterministic adaptive algorithm's all-NO path. If the algorithm terminates on the empty input in fewer than N queries, the same path is taken on the nonempty adversarial V. Its output must be no witness on the empty input, so it fails there. Thus it must make at least N queries on the empty input, and with the same argument for the first N-1 queries it must also make at least N queries on some nonempty input. This applies to decision as well as witness search with zero error, since the two transcripts are identical. For a nonadaptive universal isolation list the same adversary proves length >=N. On just the shattered subfamily, N singleton product queries achieve the bound, so the deterministic black-box count is exact there. For the full nine-group family, N is a lower bound only; the previous nonuniform upper O(m^3 log^9 m) for universal product lists and the trivial uniform m^9 singleton query upper remain valid.

This rules out a black-box deterministic constant-query reduction under the unique-only guarantee, even if it adapts and has access to arbitrary subset restrictions. It does not rule out input-aware deterministic isolation: on the shattered subfamily that is particularly cheap. It also does not charge a separate complete stage simulation for each query automatically. If a method chooses to use a full enumeration of descriptions for every black-box query, each such enumeration costs Theta(2^s)=Theta(L^3) descriptions at cubic s, so N such enumerations would already cost Omega(L^4) operations. That is only a cost warning about this implementation/interface, not a lower bound on actual U evaluation or all deterministic algorithms.

## 6. Executed finite validation

Separate JavaScript built the actual normalized pools at m=2,3,4, structural clauses and all private ternary positions, checked structural membership of every nine-group tuple and exactly one private violation per structural survivor. It tested eight allowed-mask fixtures per size, including all, empty, singleton, periodic and deterministic sparse subsets. Totals: 24 selector fixtures, 282339 structural tuple checks, 578826 private-clause checks, 7776 structural survivor/mask comparisons, 2978 surviving models counting repetitions, zero discrepancies. For reduced universe sizes N=1..4 it enumerated all unordered query lists of size <N, checked the deletion adversary, and tested that singleton queries cover every nonempty set: 740 lists, 744 deletions. It also checked 803 dyadic telescoping inequalities for m=2,3,4,8,16,32,64. Python regression repeats the checks with integer arithmetic and actual original verifier calls for SAT controls. Python execution and exact-head CI unconfirmed at writing. Finite enumeration is not the proof of the asymptotic lower bound.

## 7. Disposition

Randomized product isolation has a tight black-box query exponent, and the larger explicit shattered universe strengthens the deterministic bound even against adaptation. Both results identify limits of the isolation interface, not limits of actual input-aware algorithms. No general nine-group cubic cutoff, unique cubic coverage, unbounded SAT residuals or P versus NP resolution established. Next target an input-aware restriction generator or a semantic certificate that exploits full constraint structure beyond this oracle model. Finite cubic interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
