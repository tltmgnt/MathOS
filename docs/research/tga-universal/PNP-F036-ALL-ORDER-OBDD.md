# F036 — All-order semantic representation barrier on hypercubes

PNP_RESOLUTION_STATUS = OPEN.

The previous hybrid invariant audit passed at 0fe5f1103be5d6a6555334f73aa9778b59cb0e01
(run 45685383735, job 139456494664). This note changes the proposed
global representation rather than adding another local inference rule.

## Exact compilation target and result

Suppose an algorithm attempts to compile every CNF into a
polynomial-size ordered binary decision diagram (OBDD), representing
its complete Boolean function. An OBDD is a deterministic branching
program that reads variables in a single chosen order, possibly
skipping variables; different paths can share nodes.

For d>=2 let n=2^d and let G be the d-dimensional hypercube, on
d-bit words with edges between words differing in exactly one bit.
Define the monotone 2-CNF

    F_d = AND_{uv in E(G)} (x_u OR x_v).

It has n variables and nd/2 binary clauses. For EVERY variable
order the exact OBDD has at least

    2^ceil(n/(4d(d+1)))

nodes (counting terminals). This is superpolynomial in the encoded
input length O(n d^2) under ordinary binary variable identifiers.
Unlike a blocked-order equality example, selecting a different
global variable order does not evade this bound.

## Proof

1. Every subset S of the cube has at least min(|S|, n-|S|)
   crossing edges. Induct on d. Split into two (d-1)-cubes of size M.
   Let a,b be their counts of S vertices. By induction the internal
   boundaries contribute min(a,M-a)+min(b,M-b). The perfect matching
   between halves contributes at least |a-b|. Their sum is at least
   min(a+b,2M-a-b): by symmetry suppose a<=b. If both counts are at
   most M/2, the internal sum is a+b; if both are at least M/2, it
   is 2M-a-b. In the mixed case the full sum is M. The dimension-zero
   base case has one vertex and zero boundary.

2. Given any chosen variable order, cut it after n/2 variables.
   There are at least n/2 crossing edges. Greedily select a crossing
   edge uv and delete all remaining crossing edges incident to any
   vertex in the closed neighborhoods of u or v. Each closed
   neighborhood has d+1 vertices, each incident to at most d edges.
   One step deletes at most 2d(d+1) edges, including the selected
   edge. Thus the selected induced matching has size
   t>=ceil(n/(4d(d+1))). Its endpoints induce exactly the selected
   edges. Write them (a_i,b_i) with a_i in the prefix and b_i in
   the suffix.

3. For every subset T of {1,...,t}, assign precisely the prefix
   variables a_i with i in T to zero, and all other prefix variables
   to one. To distinguish these restrictions, for each j set the
   suffix variable b_j to zero and every other suffix variable to
   one. The whole formula is true exactly when j is not in T.
   This follows because the selected endpoints form an induced
   matching: there are no prefix-prefix edges between selected
   zeros and no cross-edge from an a_i to b_j except i=j.
   Thus all 2^t restricted Boolean functions are distinct.

4. In an ordered decision diagram, after a prefix assignment,
   follow its decisions until reaching a terminal or the first
   node labeled by a suffix variable. Its subdiagram computes the
   restricted function. Equal reached nodes give equal functions,
   so the 2^t distinct functions require 2^t distinct reached
   nodes. This holds with skipped variables, arbitrary merging
   and any chosen order. The bound follows.

For n=2^d the exponent is Omega(n/log^2 n), while the logarithm
of encoded input length is O(log n). Consequently no fixed
polynomial can bound the exact compiled representation on all
these inputs. This is a self-contained specialization of known
induced-matching arguments, not a novelty claim. Related source:
Igor Razgon, Classification of OBDD Size for Monotone 2-CNFs,
IPEC 2021, https://doi.org/10.4230/LIPIcs.IPEC.2021.25 .
Only the abstract publication page was consulted for context.

## What this does and does not eliminate

A universally polynomial explicit compilation to a single exact
OBDD is impossible. This says nothing against a polynomial SAT
decision procedure that does not compile the complete function.
Indeed every F_d is trivially satisfiable by all ones and lies
in 2-SAT. It also does not rule out general branching programs,
arbitrary circuit representations, multiple diagrams, adaptive
variable orders, or lazy partial OBDDs used only to find a model.
The number of distinguishable residuals is not a lower bound on
the bit length of a single residual descriptor.

## Evidence

Independent JavaScript audit enumerated every balanced cut of
cubes of dimensions 2, 3 and 4, and 16 sampled cuts of each cube
of dimensions 5 through 8: 13010 cuts total. It tested the boundary
bound, induced matching construction and 372292 residual
witness evaluations, with at most eight selected matching edges
per cut for finite enumeration. All checks passed. The mathematical
argument applies to the full matching and all dimensions.
The separate Python implementation and CI replay are pending;
different random sampling can yield different witness counts.

## Decision

Exact global representations must not be treated as free
polynomial-size primitives. A decision-oriented route must avoid
unnecessary full truth-function compilation and produce a
uniform polynomial correctness and cost proof, rather than
only demonstrate more expressive representations. There is no
new general mechanism with that guarantee. No new Lean credit,
no unrestricted P vs NP conclusion, and no main-branch change.
