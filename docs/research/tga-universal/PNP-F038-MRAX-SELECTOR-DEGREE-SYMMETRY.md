# F038 / negative route — MRA-X: selector degree by symmetry and nonlinear gate complexity

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivations and finite regression, not Lean.
Verified parent 9521903cfd5f9084e76abd262e0d0dde71c3fd2f: https://github.com/tltmgnt/MathOS/actions/runs/45728449215 (success).

## Backward gap analysis

Fixed-partition rank can be exponential for a linear-size circuit. Investigate a compositional measure that genuinely bounds arbitrary fan-in-two Boolean circuits, including nonlinear gates and reuse. Use the previous fixed universal clause selector family. This applies classical multilinear degree and elementary finite group orbit counting; no claim of literature novelty. Target universal_lower_bound, machine_cost, discovery, short_proofs. MRA-X stages are authored local records, not independent live agents.

## Constructive theorem: full selector degree via sign symmetry

For n>=1 let U_n be all nonempty, non-tautological normalized Boolean clauses of widths 1 through min(3,n), and N=|U_n|. Let f(p)=1 iff the selected clauses are satisfiable. Regard f as its unique multilinear polynomial over GF(2) on the N Boolean selector bits. Its full monomial coefficient is the parity of the number of satisfying SELECTOR vectors (not the number of source assignments). This follows from the Boolean cube Möbius transform: the full coefficient is sum_{S subset U_n} f(1_S) in GF(2).

The group GF(2)^n acts by independently flipping the sign of every occurrence of each source variable. It permutes the clause pool, hence acts on its subsets, and preserves satisfiability by the corresponding translation of source assignments. Every orbit has size a power of two. All non-singleton orbits contribute zero to the parity. The only invariant satisfiable subset is the empty subset: an invariant subset containing a clause must contain every sign pattern on that clause's support, and their conjunction is unsatisfiable (each assignment falsifies one of them). Thus the number of satisfying selector vectors is odd. Consequently

    deg_GF2(f)=N=sum_{j=1}^min(3,n) 2^j binom(n,j).

This proof applies to any nonempty sign-flip-invariant pool of nonempty non-tautological clauses, even with omitted support sizes or arbitrary clause width. Symmetry of the entire pool is essential; arbitrary selected subpools do not inherit the theorem.

### Transfer to arbitrary fan-in-two circuits

In the 16 binary Boolean gate basis with free constants, every gate has the algebraic form a+b u+c v+d uv over GF(2). An affine gate has d=0; every nonaffine gate needs at most one AND when XOR, negation and constants are free. A circuit with k nonaffine gates can therefore be written in normal form with k AND outputs y_i, each equal to a product of two affine forms in original inputs and earlier AND outputs. The final output is affine in those variables. Start from that affine output and substitute AND definitions in reverse topological order, multilinearizing after each substitution (all input and temporary gate variables have Boolean values). Every multilinear monomial contains the substituted y_i at most once, so replacing it by a degree-at-most-two polynomial increases degree by at most one. The invariant is an algebraic expression with the same values after substituting remaining gate definitions. After all k substitutions the degree is at most k+1. This accounts for fan-out and reuse; no formula unfolding bound is assumed.

It follows that every fan-in-two Boolean circuit for f, even nonuniform and with unrestricted depth and reuse, needs at least N-1 nonaffine gates. In particular the XOR-AND multiplicative complexity is at least N-1. Degree doubling at each nonlinear level also gives nonlinear depth >=ceil(log2 N), with nonlinear depth defined as the maximum number of nonaffine gates along a directed input-to-output path. These bounds concern Boolean circuits over a fixed binary basis; unbounded fan-in gates are not counted as single binary gates. For a polynomial-size circuit lower-bound separation, this result is still only linear in N, the actual selector input length, and logarithmic in depth. It does not prove P!=NP, NP not subset P/poly, or any superpolynomial circuit bound.

An exact alternative coefficient formula is useful for finite checks. Write q_C=1+p_C. For each source assignment x let A_x be the set of clauses falsified by x. Its witness acceptance indicator is product_{C in A_x} q_C. OR over assignments equals XOR over all nonempty products of these indicators in characteristic two. Thus the multilinear polynomial in q is obtained by toggling the monomial indexed by union_{x in T} A_x for every nonempty subset T of assignments. Distinct unions may cancel; this is an exponential-in-2^n symbolic audit, not a proposed efficient solver. Translation q=1+p preserves degree and the full coefficient. The code checks the complete union parity polynomial for n<=4, and direct truth-table Möbius transforms for n<=2.

## Alternative track: prime-domain symmetry and compositional limits

Let p be a prime, source variables take values in GF(p), and let a finite nonempty pool of constraints be invariant under coordinatewise translations of GF(p)^n. Require that no constraint is identically true on all assignments. A constraint may otherwise be any relation on the whole source space, and translations may permute equal syntactic labels provided the action is well-defined. Select constraints by Boolean bits. A nonempty translation-invariant subset of the pool is unsatisfiable: if it contains any constraint C that excludes some assignment, translating C across the full group excludes every assignment in at least one translated constraint. The empty subset is satisfiable. Satisfiability is preserved under translation, and all nonsingleton subset orbits have size divisible by p.

The unique multilinear polynomial over GF(p) for the Boolean selector function has full coefficient sum_{S} (-1)^(N-|S|) f(1_S). The sign is constant on each orbit, so nonsingleton orbits vanish modulo p, and the only contributing singleton is the empty subset. Hence the full coefficient is (-1)^N, nonzero, and degree equals N. This is an exact extension to prime-domain translation-symmetric CSP pools. The finite fixtures use all unary and binary forbidden tuples on up to two source variables, with p=2,3,5 as specified. The GF(2) nonaffine-gate argument above is not silently applied to odd characteristic: for Boolean inputs over GF(p), each binary Boolean gate still has a degree-at-most-two multilinear representation, so the same reverse-substitution argument bounds degree by total binary gates plus one; no claim about XOR being affine in odd characteristic.

### Adversarial scope

Full degree is the maximum possible for N Boolean inputs, yet the AND of all N inputs has exactly the same degree and a binary circuit of N-1 AND gates. Thus even a maximally large degree value cannot by itself force a superlinear circuit-size lower bound. This is a quantitative obstruction to using raw algebraic degree alone, not an impossibility theorem for every algebraic circuit measure. Degree respects nonlinear composition and shared computations, unlike the earlier fixed-partition rank-to-circuit intuition, but its range is too small for the required universal separation. A proof of superpolynomial hardness would need a different measure, a stronger multi-invariant argument, or a new structural simulation theorem. No extrapolation from the finite coefficient counts is used in the proof.

Topology: source translations act on selected constraint complexes and preserve global witness existence. The top multilinear coefficient is an orbit-weighted sum on the selector cube, not a claimed unrestricted SAT homology invariant. The nonzero coefficient follows from the unique satisfiable invariant subset.

## Evidence, bit cost and forward disposition

Independent scalar JS enumerated the nonempty assignment subsets and union parity monomials for n=1..4. Rows [n,N,assignment subsets,distinct unions,odd unions,max degree,full coefficient]:
[1,2,3,3,3,2,1], [2,8,15,15,15,8,1], [3,26,255,255,255,26,1], [4,64,65535,43145,34953,64,1].
Independent prime-domain selector enumeration rows [p,n,k,N,selector vectors,source assignment checks,SAT selectors,full coefficient mod p]:
[2,1,1,2,4,8,3,1], [2,2,2,8,256,1024,95,1], [3,1,1,3,8,24,7,2], [3,2,2,15,32768,294912,19759,2], [5,1,1,5,32,160,31,4].
Independent circuit enumeration and Möbius degree histogram rows [n,s,distinct functions,histogram degrees 0..n, with zero function assigned degree zero]:
[2,0,4,[2,2,0]], [2,1,16,[2,6,8]], [3,1,38,[2,12,24,0]], [3,2,152,[2,14,72,64]], [4,1,70,[2,20,48,0,0]].
The submitted Python checks the actual parity-polynomial calculation, Möbius cross-check, source translation permutations and closure of forbidden-tuple pools, exact signed coefficients, circuit degree histograms, and AND witnesses attaining the degree bound. Independent JS did not execute Python. Enumeration cost is explicitly exponential in the number of source assignments or selector bits, as applicable; the symmetry proof itself does not enumerate them. The mathematical nonlinear-gate and prime-domain claims are not inferred from the finite experiments. CI required.

Forward TGA: BARRIER_IDENTIFIED. A maximum-degree theorem and unconditional linear nonaffine-gate lower bound apply to general fan-in-two circuits for the fixed SAT family, with an exact prime-domain extension; neither yields a superpolynomial separation. Next investigate whether an independently justified stronger algebraic measure (e.g. restriction-sensitive circuit decomposition or gate-elimination recurrence) can exceed the degree ceiling, including the counterexamples to a proposed compositional inequality. No universal obligation closes. Independent review and Lean formalization outstanding.
