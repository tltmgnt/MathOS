# F038 — MRA-X: polynomial compatible-type recognition by bounded relational width

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation with an external theorem dependency and finite regression, not a Lean declaration.
Verified base fead4da57c93cab22e208323c7538535c5c132b9, https://github.com/tltmgnt/MathOS/actions/runs/45721840186 (success).

## Backward gap analysis and strategy decision

Target F040 discovery, F037 machine_cost, F038 ordinary_complete, F039 short_proofs. Previous exact orientation discovery still enumerates algebraic family assignments. Instead of increasing search budgets, study the algebra on the four operation labels themselves. The constructive track proves a common bounded-width identity for every local compatibility relation. The alternative track implements (2,3)-minimality and pinned witness reconstruction rather than enumerating families. MRA-X uses seven authored local records and TECT-X pre/post checks; no live independent agents or proof promotion.

## Constructive theorem: a common algebra on operation labels

Let D={0,1,2,3} denote ternary Boolean AND, OR, majority and minority respectively; write f_p for the corresponding operation. The four operations are exactly the symmetric idempotent ternary Boolean operations: their two values on inputs of Hamming weight one and two determine them. For every Boolean relation R of any arity, define L(R) subset D^arity as all coordinate type tuples preserving R.

Define a ternary operation t on D by composition:
 f_{t(p,q,r)}(x,y,z)=f_p(f_q(x,y,z),f_r(x,y,z),f_r(x,y,z)).
The right side is symmetric and idempotent, hence uniquely in D. Composition of polymorphisms proves that every L(R) is closed under coordinatewise t, regardless of R or arity. Define
 u=t(p,q,p), v=t(p,p,q), s(p,q)=t(u,u,v).
The following exact table (row p, column q) is obtained from the two weight values:
 0 0 0 0
 1 1 1 1
 0 1 2 3
 0 1 3 3
Thus s selects a higher priority label in the ordered classes {0,1} > {3} > {2}; it selects the first argument on a tie. Every L(R) is closed under s.

For each k>=3 define a_i(x_0,...,x_{k-1}) as the left-associated s-fold of the cyclic list starting at x_i, wrapping through all k inputs. Define w_k=t(a_0,a_1,a_2). These are terms in t, hence common polymorphisms of all L(R). They are idempotent. To check the weak near-unanimity identities on inputs consisting of k-1 copies of x and one y, distinguish:
* If x,y have different priorities, every cyclic fold gives the higher-priority label, so w_k returns it regardless of the outlier position.
* If x,y share priority and differ, they must be 0 and 1. Every cyclic fold returns its first argument. On these two labels t is ordinary Boolean majority, so w_k returns the repeated label x (at most one of the first three differs).
* If x=y idempotence applies.
This proves WNU terms of every arity k>=3, and in particular w_3(y,x,x)=w_4(y,x,x,x). The identities are exact, not a conjecture inferred from finite testing.

Use the established finite-domain bounded-width theorem (Barto and Kozik, Constraint Satisfaction Problems of Bounded Width, FOCS 2009, https://www.karlin.mff.cuni.cz/~barto/Articles/SDBW.pdf) and Barto's relational-width collapse (The collapse of the bounded width hierarchy, J. Logic Comput. 26(3), 923-943, https://doi.org/10.1093/logcom/exu070). In the form used here, a finite relational language on a finite domain, including all singleton unary relations, with WNU polymorphisms of all sufficiently large arities has bounded relational width and hence relational width (2,3). The constants are preserved by idempotence. This is an explicit external theorem dependency, not a new proof of the bounded-width theorem. The argument applies to the finite set of relations actually occurring in any given instance, including arbitrary arities. No hidden language-specific algorithm or bound is invoked: the width (2,3) algorithm is uniform and described below.

**Conclusion:** given explicit local type tables L(R), existence of a common compatible type tuple is decidable in uniform polynomial time in their total explicit length and number of variables. The same applies with arbitrary unary allowed-label sets, since w_k is conservative: all folds select an input, and t on the three selected labels is conservative for these folds, because folds all have the same maximal priority, so they are either identical or all in {0,1}; t returns one of them. Thus every unary subset is w_k-closed. Singleton restrictions alone suffice for reconstruction. The theorem does not require fixed families, orientation guesses, a bound on ambiguity or disconnected components.

## Alternative implementation: exact local consistency and reconstruction

Keep every original table (do not replace a high-arity table by its pair projections). Add a full relation on every scope of size 1,2,3. Repeatedly compute for each unary/binary scope S the intersection of the projections onto S of every table containing S. Delete from every table any row whose restriction to some such S is absent from that intersection. An empty table is a sound contradiction. At a nonempty fixed point, every <=3 variable subset is contained in some table and all projections onto shared subsets of size <=2 agree. This is exactly (2,3)-minimality. The operations preserve solutions; by the invoked theorem the nonempty fixed point implies existence of a type assignment.

Let P denote total initial table rows after adding O(n^3) scopes of at most 64 rows. At most P strict row deletions, hence at most P+1 sweeps. Each sweep is polynomial in explicit encoding length (projection over at most quadratically many subscopes per table; finite domain size four). Record sweep counts, recheck via deterministic replay. To reconstruct a type assignment, add singleton pins one coordinate at a time, checking the four options with the exact decision algorithm. At most 4n+1 decision calls; the invariant is a feasible extension. Verify every original local type table and, when constructed from Boolean tables, every original Boolean closure condition. This is polynomial constructive recognition. No external SAT oracle. The prototype repeats full sweeps and is not optimized for large instances; proof certificate is replay, not formal Lean.

For supplied private-block interface with scope at most h, the explicit Boolean tables and local type enumeration each cost 2^O(h) poly(L), including all ordered triples of Boolean rows and all 4^h local type choices. Thus entire compatible-type discovery, earlier mixed solver and witness gluing cost 2^O(h) poly(L), with no ambiguity exponent. For h=O(log L), this is polynomial, conditional on supplied interface and existence of compatible typing. If no typing, return NO_TYPING, never UNSAT for the Boolean source. The topological aspect is an exact gluing theorem for local unary/pair projections of type constraints under bounded-width hypotheses, not a homology criterion for arbitrary Boolean SAT.

## TECT-X adversarial boundary and route disposition

The label algebra does not imply every Boolean relation has a typing. NAE is nonempty and untypable. Moreover exact compatibility cannot simply be reduced to pair projections of original tables: for R={0,...,6} on three bits, the type tuples (2,2,0),(2,0,2),(0,2,2) are valid, but (2,2,2) is not. Every pair of the all-2 tuple occurs in an allowed type tuple, so pair projections alone admit it incorrectly. Our algorithm retains the original tables. All local type constraints may be feasible yet globally incompatible: pin H type labels on a triangle of equality/equality/disequality Boolean relations; individual unary domains survive arc consistency but (2,3)-minimality detects the contradiction. These facts distinguish compatibility search from source solving and justify the exact consistency algorithm.

The previous discovery bottleneck is fully discharged within this four-operation table class. No claim that these terms are new in general CSP theory. Universal existence of a useful interface/typing is still unproved and false for arbitrary fixed table representations. Therefore do not continue optimizing recognition in isolation: redirect to representation transformations that preserve SAT and produce typable relations, or a barrier for such transformations. A uniform polynomial-time transformation of arbitrary 3-CNF to polynomial explicit typable tables preserving satisfiability (and, for the selector route, efficiently lifting witnesses or using SAT self-reduction) would imply P=NP by this theorem and the prior typed solver. Conversely P=NP gives such a transformation by deciding SAT and emitting a constant true or false table; for witness lifting use polynomial self-reduction. This is an equivalence of unrestricted transformation existence, not a circular proposal for an algorithm.

## Evidence and complexity ledger

Independent JS: 528 WNU outlier-position tests for arities 3..8; 256 Boolean ternary relations, 4650 compatible local type rows, 8955210 t-composition checks; 256 four-variable global fixtures, 120 typable and 136 untypable, 4096 singleton-pinned decisions with 1080 feasible. The independent reference used pairwise semijoins with added scopes and compared to exhaustive label assignments; it did not execute the submitted Python. Submitted Python independently runs the consistency implementation, tests the same finite counts, reconstructs witnesses, tests prior typed solving, pair-projection counterexample, unary restrictions and cap-free component example. No mathematical acceptance, independent expert review or Lean declaration. Exact-head replay required.

All input construction, table enumeration, sweeps, reconstruction calls, bit arithmetic and certificate replay included. Explicit local tables polynomial; original compact encodings of arbitrary high-arity relations not covered. F037-F040 universal obligations and both resolution routes remain open. Forward gap disposition: restricted discovery gap closed mathematically subject to established theorem; global universal gap unchanged. Next target: evaluate representation transformation coverage (including an actual obstruction to a specified transformation policy), rather than extend the now-polynomial type-recognition mechanism.
