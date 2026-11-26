# F038 / negative route — MRA-X: degree-filtered multi-output rank and Boolean derivatives

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Verified parent 07cce6d4a5bf8c876cc16c3d941459a2c4fec941: https://github.com/tltmgnt/MathOS/actions/runs/45731282868 (success). At inspection the TOPO-406 workflow was still running. No claim of all parent workflows completed.

## Backward gap analysis

The previous affine cover theorem gives an exact exponential representation lower bound but no general physical gate bound. Seek a measure directly charged to shared nonlinear gates. Use multi-output XOR-AND normal forms and degree-filtered linear rank, then test whether derivative families of the fixed universal SAT selector transfer hardness to the single decision output. This is an application of elementary Boolean polynomial algebra and linear algebra; no claim of literature novelty. MRA-X stages are authored local records, not independent agents.

## Constructive theorem: degree-filtered output rank

Work in the Boolean ring R_N=GF(2)[x_1,...,x_N]/(x_i^2-x_i). Every element has a unique multilinear representative. Let V_<d denote the vector space of functions of degree strictly less than d, including zero, for 2<=d<=N. Let a multi-output Boolean function have coordinate functions f_1,...,f_t, and define rho_d as the dimension of the span of their images in R_N / V_<d.

A circuit with affine operations free and k binary AND gates computes each output as an affine combination of input bits and the k AND outputs y_1,...,y_k in topological order. Each y_j is the product of two affine forms in inputs and earlier AND outputs. This normal form also applies to the 16 binary gate basis by replacing each nonaffine gate with one AND and affine operations, without assuming formula structure. The previous degree lemma applies to each prefix: deg(y_j)<=j+1. For completeness, reverse-substitute its j AND definitions into an affine output expression, multilinearizing after every substitution in all Boolean variables; each substitution increases degree by at most one even with repeated uses. Therefore y_1,...,y_(d-2) have zero image in the quotient. All output images are spanned by the remaining AND outputs, so whenever rho_d>0,

    k >= (d-2) + rho_d.

The positive-rank premise is required: a constant or affine output does not force d-2 gates for large d. Taking the maximum of these lower bounds over d yields a physical nonlinear-gate bound for arbitrary shared multi-output DAGs. Rank at d=2 is ordinary linear independence modulo affine functions. Rank at higher thresholds charges the initial degree-building gates separately. This is a genuine circuit measure, not an unfolded formula or affine-region count. It is bounded by the number of outputs plus N-2, hence cannot give a superpolynomial lower bound for one output by itself.

## Application: all coordinate Boolean derivatives of a full-degree function

Define Delta_i f(x)=f(x)+f(x+e_i) over GF(2) and Delta_I=product of these commuting operators for I a subset of [N], with Delta_empty the identity. On a multilinear monomial, Delta_I gives zero if I is not contained in its support, otherwise deletes I. Suppose f has degree N, i.e. its full monomial coefficient is one. Then Delta_I f has degree exactly N-|I|, with unique top monomial product_{j not in I} x_j. These 2^N derivative functions, including f, form a basis of R_N: in any nonempty linear combination take the highest degree present, whose distinct top monomials cannot cancel.

Let D_r(f) consist of all derivatives Delta_I f of orders |I|<=r, for 0<=r<=N-2. Its t_r=sum_{j=0}^r binom(N,j) output functions are independent modulo degree <N-r, by the same leading-term proof. Apply the filtered rank theorem with d=N-r:

    MC(D_r(f)) >= t_r+N-r-2,

where MC counts AND gates with arbitrary affine operations free, and all outputs must be explicitly available as Boolean wires at the same input. In particular for N>=3 the batch of f and all first derivatives needs at least 2N-2 AND gates; at r=0 we recover N-1. At r=N-2 the lower bound is exactly 2^N-N-1. It is attained: compute every monomial of size at least two with one AND per monomial, in increasing support size, reusing a previously computed submonomial and one input. All derivative outputs are affine combinations of these monomials and the original inputs. Thus for every full-degree f,

    MC(D_(N-2)(f)) = 2^N-N-1.

The same exact bound holds if all orders up to N are requested, since the additional derivatives are affine. This is an exact exponential multi-output gate complexity theorem for full-degree functions, regardless of fan-out and sharing. It applies to the universal SAT selector f on N inputs, whose full degree was proved by sign symmetry in the earlier F038 selector-degree-symmetry cycle. It also applies to AND_N; the output task is exponentially larger than a single decision.

These gate counts are in the multiplicative complexity model, not total bit cost. The upper construction may require exponentially many affine wire incidences and XORs to express all outputs. The lower bound is valid for ordinary binary circuits as well because their nonaffine gate count dominates MC. The exact upper bound concerns AND counts only.

## Alternative track: charge the derivative transfer, reject free Boolean differentiation

If a single-output circuit for f uses k AND gates, independently evaluate it on x+e_J for every |J|<=r, where e_J flips those coordinates. Each shifted copy uses k ANDs (input flips are affine). Then Delta_I f is the XOR of the shifted evaluations indexed by J subset I. Hence MC(D_r(f))<=t_r*k, with t_r copies; the affine output combination cost is at most sum_{j<=r} binom(N,j) 2^j wire occurrences, in addition to the copied circuits and shifts. This gives the valid transfer k>=ceil((t_r+N-r-2)/t_r), not an exponential single-output lower bound. The prior N-1 degree lower bound is stronger except at r=0 where equal. No efficient simultaneous derivative compiler with dramatically smaller cost is assumed. Explicit output enumeration itself costs at least t_r wire labels in a normal representation.

A tempting alternative is ordinary formal automatic differentiation of the arithmetic gate DAG, treating shared gates as differentiable polynomials. Boolean finite differences do NOT obey the ordinary Leibniz rule. Exactly,

    Delta_i(uv) = u Delta_i(v) + v Delta_i(u) + Delta_i(u) Delta_i(v).

This follows by expanding the shifted product. The extra term matters: u=v=x_i gives uv=x_i in the Boolean ring, Delta_i(uv)=1, whereas the ordinary two-term rule gives zero. The usual formal derivative does not descend to R_N since the derivative of x_i^2-x_i is 1 in GF(2), though the relation equals zero as a Boolean function. A straight-line polynomial circuit may compute a nonmultilinear polynomial with the correct Boolean evaluations but incorrect formal derivatives on the cube. Multilinearization before differentiation repairs the semantic issue but its cost is not free; no polynomial conversion for arbitrary Boolean circuits is proved here. This is not a claim that every efficient Boolean derivative algorithm is impossible.

For a fixed full-degree function there is an especially simple adversarial counterexample: AND_N has one output and exactly N-1 AND gates, but its order-(N-2) derivative batch has the exact exponential MC above. Thus an unconditional generic transformation with polynomial AND overhead in N and single-output gate count, independent of the batch size, is impossible for explicit derivative outputs. Even first-order rank bounds do not rule out a polynomial overhead or a compact programmable derivative evaluator taking I as additional input; the latter is a single-output function and the multi-output rank proof cannot charge it as if every derivative were separately available. This isolates the exact difference between an explicit vector output and implicit access to its entries.

Topology: coordinate restrictions and translations induce commuting finite differences; their leading monomials distinguish graded output classes. The filtered quotient is a linear-algebraic invariant of the output vector, not an unrestricted topological invariant of a single SAT decision circuit.

## Evidence and resource ledger

Independent JS used direct truth-table finite differences and rank elimination on truth-table bit vectors modulo the span of low-degree monomial tables. For every full-degree truth table on N=2,3 and 256 deterministic full-degree fixtures on N=4 (first and last 128 odd-parity truth tables in numeric order), rows [N,functions,order-family tests,sum quotient ranks,sum degree-filtered bounds,sum full-batch exact bounds]:
[2,8,8,8,8,8], [3,128,256,640,768,512], [4,256,768,4352,5120,2816].
Independently enumerated all pairs of Boolean functions on N=1,2,3 and every coordinate/input for product finite differences. Rows [N,function pairs,checks,ordinary Leibniz failures,nonzero cross terms,nonzero differences]:
[1,16,32,8,8,12], [2,256,2048,512,512,768], [3,65536,1572864,393216,393216,589824].
For full universal selector pools on one and two source variables, rows [source n,selector N,truth-table length,full derivative basis rank,ranks for orders 0..N-2]:
[1,2,4,4,[1]], [2,8,256,256,[1,9,37,93,163,219,247]].
The Python regression uses coefficient-vector elimination, actual SAT truth tables, independent finite-difference replay, and constructs every monomial by an actual sequence of AND operations then reconstructs every derivative output by affine combinations. It also checks malformed dimensions, low-degree rank-zero cases, and the Boolean product-rule counterexample. Independent JS did not execute Python. Complete truth tables, derivative batches and rank checks are exponential in N and finite regression only. Asymptotic claims rely on the mathematical proofs, not extrapolation. No general fast simultaneous derivative compiler, SAT minimizer or unrestricted lower-bound solver implemented. Exact-head CI required.

Forward TGA: BARRIER_IDENTIFIED. A degree-filtered physical nonlinear-gate bound and exact exponential batch complexity are proved, but explicit-output enlargement prevents transferring that exponential bound to the original SAT decision circuit. Next investigate a single-output, resource-charged structural transformation (e.g. programmable restricted evaluations or a gate-elimination recurrence for a hard restriction), and abandon explicit output-count amplification unless it gives a noncircular single-output bound. Independent mathematical review and Lean formalization outstanding. No universal obligation closes.
