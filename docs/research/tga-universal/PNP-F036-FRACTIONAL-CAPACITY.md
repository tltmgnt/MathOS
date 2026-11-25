# F036 — Fractional capacities across overlapping groups

PNP_RESOLUTION_STATUS = OPEN.

## Certificate and discovery

Let D be a collection of nonempty pairwise literal-disjoint original
clauses. Let U be the union of their signed literals. Each group G
has original binary clauses (-u OR -v) for all distinct u,v in G.
Singleton groups require no evidence. Assign positive integer weights
w_G and a positive integer scale Q. An exact contradiction certificate
satisfies

    sum_{G containing l} w_G >= Q       for each l in U,
    sum_G w_G < Q |D|.

In a satisfying assignment at least |D| distinct literals in U are
true. Summing the first inequalities over true literals, and using
the capacity-one property of every group, gives

    Q |D| <= sum_G w_G * (# true literals in G) <= sum_G w_G,

a contradiction. No disjointness of groups is assumed. Opposite
signed literals may occur in different demands: they cannot both
be selected as true. The integer checker validates all conditions
independently of the search, including binary clause evidence.

The new discovery implementation greedily selects disjoint original
clauses of length at least three, enumerates all signed conflict
cliques of sizes one through four on U, and minimizes total
nonnegative fractional weight subject to covering each literal by
weight at least one. The explicit LP has at most O(|U|^4) variables
and |U| constraints. Rational linear programming is a polynomial-time
problem for this explicitly bounded input, unlike separation over
arbitrary-size cliques. The implemented SciPy/HiGHS solver is a
floating-point candidate generator, NOT a certified polynomial-time
rational LP algorithm. Round weights upward to an integer grid of
scale 10^6, repair undercoverage with singleton weights, and check
the resulting integer certificate exactly. This can miss small
deficits or fail to discover an existing certificate, but it cannot
turn an invalid certificate into a sound UNSAT answer. None means
UNKNOWN, never SAT.

## Strict separation from unweighted capacity certificates

In one block, use nine variables on a cycle. The three demands are
the consecutive disjoint triples. Include negative binary clauses
for pairs at cyclic distance at most three. Each set of four
consecutive positions is a capacity-one group. Use all nine cyclic
quadruples with unit weight and Q=4. Each position is covered four
times, and total weight is 9 < 4*3=12. The formula is UNSAT.

The complement of this conflict graph is a nine-cycle (distance-four
edges). Consequently any clique has at most four vertices. An
unweighted cover of all nine variables needs at least three groups,
which cannot exhibit a strict Hall deficit for these three demands.
The fractional certificate has total normalized weight 9/4 instead.
Even a proper subset of the three designated triple demands cannot
have a strict unweighted deficit: covering 3j vertices with size-four
groups requires ceil(3j/4)=j for j=1,2,3. Replicate t blocks to get
9t variables and 30t clauses. No group with two vertices can span
blocks. Thus no unweighted capacity-one certificate covering a
subset of these designated demands suffices, but weighted coverage
gives a strict deficit 9t/4 < 3t. This is a separation for these
original demands and this capacity vocabulary, not a lower bound
against arbitrary resolution, other derived demands, or counting
systems. The block family itself is easy; the point is a strictly
stronger certifying primitive, not a hard SAT benchmark.

The same certificates exist after consistent variable polarity flips
and renamings. No group map or weights are supplied to discovery.

## Executed local tests

Python 3 with SciPy 1.17.0: 36 transformed UNSAT cases across t=1..12,
12 transformed satisfiable controls, 256 random signed CNFs,
three corrupted-certificate rejections, one known UNKNOWN case.
The random controls yielded zero accepted certificates: these are
limited negative controls, not evidence of broad discovery power.
The base nine-variable instance was independently brute-force
checked, as was a supplied explicit weighted certificate. The
repository exact-head replay remains separate.

Prior signed counting exact-head replay passed: fe9bf2fb,
run 45681852113, job 139444157737, 31 independently brute-force-checked
accepted certificates in 512 random small formulas.

## Remaining obstruction

Greedy demand selection, fixed clique size, numerical LP discovery
and fixed integer grid are incomplete. Even complete rational LP
solution over the selected inequalities would only decide that
relaxation, not integer satisfiability. A universal completeness
or polynomial decision theorem is absent. No new Lean credit.
Main unchanged.
