# F038 / negative route — MRA-X: local existential certification of circuit range avoidance

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivations and finite checks, not Lean. Verified parent c3f568862e9bd27385a8d13606c9814a2aed08ac: https://github.com/tltmgnt/MathOS/actions/runs/45726384203 (success).

## Backward gap analysis

The previous cycle constructed a single language outside P/poly by sparse truth-table prefix avoidance, but did not place it in NP. Investigate existential certificates for absence from the circuit range. Distinguish an explicit m-bit input word from the original n-bit input length of the constructed language. A polynomial in m is not necessarily a polynomial in n. All seven MRA-X records are authored locally, not independent live agents.

## Constructive track: finite sample interpolation

Use the previous circuit basis: n input wires, free constants, all 16 binary Boolean gates, repetitions permitted. Let Q be any set of q distinct inputs and specify an arbitrary bit at each. If q=0 or 1, a constant works. For q>=2 there is a circuit of at most 2q-3 gates matching all specified bits.

Proof: recursively split any nonconstant labeled sample by a coordinate on which its points differ. Such a coordinate exists because the points are distinct. Stop when all labels at a node coincide. This yields a full binary decision tree with at most q leaves. Compile bottom-up. A node whose children are both leaves, or one leaf and one subtree, needs at most one binary gate (any Boolean function of the tested bit and the subtree value is available); a node with two nonleaf children needs at most three (two conditional AND gates and OR). For a nontrivial tree let a,b,c count internal nodes having 0,1,2 internal children. Then a=c+1, a+b+c=ell-1 for ell leaves, and c<=(ell-2)/2. The total gate count is at most a+b+3c<=2ell-3<=2q-3. A constant tree uses zero gates. Construction by explicit partitioning and tree compilation is polynomial in n+q plus sample encoding length. The circuit is not required to agree outside the sample.

Let R_{n,s,m} be the set of first m output bits of <=s-gate circuits on binary ordered inputs, where 1<=m<=2^n and s>=0. Define K(s)=floor((s+3)/2). Any partial assignment on at most K(s) prefix positions extends to a word in R by interpolation. This holds even for arbitrary, adaptively selected positions, not merely a consecutive prefix.

## Local existential certificate obstruction

Define a verifier V^{y}(n,s,m,w) accessing the unknown m-bit word y only by individual bit queries. Its purported certificate w can be arbitrary, and computation can be adaptive; fix w and any internal deterministic execution. Soundness means no w is accepted for ANY y in R; completeness means each missing word (or at least one missing word in the weaker version) has an accepting certificate.

For any accepted word y, consider the distinct queried positions Q on the accepting transcript. If |Q|<=K(s), interpolate a <=s-gate circuit matching their values and let y' be its prefix. With the same w and public parameters the verifier on y' has exactly the same transcript, inductively including its adaptive query choices, and accepts. This contradicts soundness. Thus EVERY accepting transcript must query more than K(s) distinct bits, regardless of certificate length or computational power. The bound includes perfect-soundness randomized verifiers by fixing an accepting random tape. When m<=K(s), there are no missing words at all.

This is an unconditional lower bound for a particular oracle-access certification model. In the growing budget s(n)=n^ceil(log2 n), K(s) exceeds all fixed polynomials in n, and the preceding counting prefix m exists eventually. No polynomial-in-n query verifier of this form can certify even one missing word, even with a long auxiliary certificate. The same result does not exclude a polynomial-in-m verifier of explicit missing words. It also does not rule out an NP bit-membership verifier for the constructed language, which need not certify global absence from R on an arbitrary oracle word. The latter distinction is essential.

## Alternative track: bounded randomness and exact certificate complexity

Suppose a verifier uses r unbiased random bits, at most q distinct queries per tape, and has completeness probability alpha and soundness probability beta with alpha>beta for each fixed supplied certificate. Pick a certificate for an accepted hard word. There are at least ceil(alpha*2^r) accepting tapes. Select t=floor(beta*2^r)+1 of them, possible by alpha>beta. Their union contains at most q*t queried positions. If q*t<=K(s), interpolate one easy word matching the union. The same certificate accepts that easy word on all selected tapes, with probability at least t/2^r>beta. Hence q*(floor(beta*2^r)+1)>K(s) is necessary. This also handles beta=0. A randomized verifier with q=poly(n) and r=O(log n) cannot meet this condition for the growing superpolynomial budget. No claim is made for polynomially many random bits with unrestricted soundness error; the union argument alone does not cover that case.

For fixed explicit parameters and absent word y define c(y)=min{|Q| : no word v in R agrees with y on Q}. This is exactly the minimum deterministic accepting transcript query count achievable by a sound oracle verifier with no resource bound (lower bound above, upper bound by storing Q and exhaustively checking compatibility). It is finite, at most m. The exhaustive finite implementation computes it by projecting every circuit-range word to every subset of positions. Interpolation gives c(y)>K(s); some small examples have a substantially stronger exact value. Computing a partial labeling's nonextendibility is a coNP predicate for explicit unary gate budget and explicit samples: its complement is witnessed by a circuit with polynomial-size gate description. No coNP-hardness is asserted for this circuit-minimization-like decision problem. In particular an efficient existential certificate system for arbitrary explicit nonextendibility, or an NP membership theorem for the previous hard language, has not been constructed.

Topology: projection of a circuit range onto small subsets is surjective, despite non-surjectivity of the full projection. Thus all sufficiently small local assignments have extensions to bounded circuits, while some global words do not. The interpolation circuit may change with the subset; no globally consistent family is asserted. This is a finite projection obstruction, not a SAT homology invariant.

## Evidence, costs and forward disposition

Independent JS scalar gate enumeration and projection checks, per [n,s,m,range size,absent-word/subset tests,tests with <=K(s) positions,histogram of minimum certificate size from 0 to m]:
[2,0,4,4,192,60,[0,0,10,2,0]]
[3,1,8,38,55808,8066,[0,0,0,0,218,0,0,0,0]]
[3,2,8,152,26624,3848,[0,0,0,0,0,0,80,24,0]]
[4,2,10,238,804864,44016,[0,0,0,0,0,544,218,24,0,0,0]]
[3,2,5,32,0,0,[0,0,0,0,0,0]].
Independent JS separately compiled and checked every nonempty partial labeling for n=1,2,3: [n,labelings,point checks,max gates,total gates] = [1,8,12,1,2], [2,80,216,5,90], [3,6560,34992,13,25530]. Python uses prior bit-parallel range enumeration, exact subset projection histograms, and actual circuit compilation/evaluation, plus malformed-sample and randomized-bound controls. Independent JS is not execution of Python. The circuit compilation cost is polynomial in explicit sample length; exact histogram computation is exponential in m and only finite regression. The query bound is independent of actual running time and does not claim a general time lower bound for algorithms not in the oracle model.

Gap disposition BARRIER_IDENTIFIED. The local existential certification proposal fails at superpolynomial gate budgets; alternative bit-membership certification is untouched. Next examine whether a succinct globally consistent bit-witness relation can place a fixed hard language in NP (and distinguish NP from NP intersect coNP and shared advice); alternatively establish a stronger explicit-model barrier. No promotion, independent mathematical review or Lean proof.
