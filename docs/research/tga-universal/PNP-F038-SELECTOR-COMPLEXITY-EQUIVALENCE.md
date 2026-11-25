# F038 — Universal existential selector complexity equivalence

PNP_RESOLUTION_STATUS = OPEN. Mathematical reduction, not a verified Lean declaration.
Verified base e0d2741f435c3d8e8488d413255f05654f773945: https://github.com/tltmgnt/MathOS/actions/runs/45700589388 (success).

## Universal input model

For n variables use a fixed public presence vector over all normalized clauses of width at most three (including empty, excluding tautologies). Its length M(n)=sum_{j=0}^3 2^j binom(n,j)=O(n^3). Repeated clauses, literal order, and tautologies can be normalized in polynomial time. A selector A_n(F) outputs one bit, referring to variable 1, and on every satisfiable F must choose b with SAT(F AND (x_1=b)). It is arbitrary on unsatisfiable F, but is total (time/circuit bound holds also there). This is the universal domain, not a special local projection family. It includes formulas with both branches satisfiable. An unmentioned variable is still allowed in the declared universe. Relabeling variables is a fixed permutation of vector coordinates.

## Witness extraction with no off-promise assumptions

Start G=F. For i=1,...,n, swap variables 1 and i in G, query A_n on the renamed formula, and append the unit (x_i=b) to G in the original variable naming. Finally verify the resulting full assignment against F; accept iff it satisfies F.

If F is satisfiable, induction preserves satisfiability of G at every step, so the next query is always on-promise and the assignment is a model. If F is unsatisfiable, no assignment passes verification, regardless of answers. Prefix clauses remain within width three and the original n-variable universe. This uses n selector calls without recognizing which input was on-promise, and works with any choices where both branches are satisfiable.

Conversely a total SAT decision procedure gives a selector by testing SAT(F AND (not x_1)); choose zero if true, one otherwise. Thus deterministic uniform polynomial-time selectors exist iff P=NP. More explicitly, input normalization, relabeling, appending units and checking the witness have polynomial cost. No selector correctness outside the satisfiable promise is required.

## Nonuniform and quantitative equivalence

Let S(n) be the size of a total Boolean circuit selector for the n-variable presence representation, and D(n) the minimum decision circuit size for that representation. The converse uses a fixed input wire set to one and a negation, so S(n)<=D(n)+O(1). In the forward construction unroll n selector copies; permutation is wiring, and updating each unit pair after choosing a bit uses O(1) gates per step with fanout allowed. Verification checks each original clause against the output assignment using O(M(n)) bounded-fan-in Boolean gates. Hence D(n)<=n S(n)+O(M(n)+n). The polynomial-size circuit existence equivalence is NP subseteq P/poly iff universal polynomial-size nonuniform selectors exist. For the forward implication from presence SAT to arbitrary encoded NP inputs, reduce to 3-SAT, relabel and pad to a polynomially bounded common n, and compute the presence vector in polynomial time; the reverse follows by compiling NP decision circuits for the presence language. Circuit existence by itself does not imply uniform polynomial-time construction or evaluation from n. Polynomial-time constructible selector circuits do give P=NP.

A useful intermediate: a uniform polynomial-time evaluator with a common correct advice string of length O(log n) for each n already implies P=NP. Enumerate every possible advice string (padding to the known length bound), run the entire witness extraction under each, and accept only a verified witness. Polynomially many candidate strings suffice and false positives are impossible. More generally any polynomial-time constructible polynomial-size list containing a globally valid selector for that universe suffices; it is not necessary to recognize which member is valid. This is not a claim that an arbitrary polynomial-size nonuniform circuit family can be enumerated in polynomial time.

## Randomized equivalence and a narrower promise

For a total randomized uniform polynomial-time selector with worst-case error at most a fixed epsilon<1/2 on every satisfiable formula, amplify each query independently to error <=1/(3n). Condition on a correct prefix: the next formula is satisfiable and fresh coins give the same bound. A union bound gives probability >=2/3 of finding a model on satisfiable inputs. Verification rejects all unsatisfiable inputs. Thus NP=RP. Conversely if NP=RP, a one-sided SAT test with success probability >=2/3 on satisfiable inputs gives a selector by testing the zero branch; its only possible error on satisfiable formulas is choosing one when only zero is viable. All calls must obey polynomial time even off-promise.

Even a selector guaranteed only for formulas with exactly one satisfying assignment suffices to obtain NP=RP if it is total and uniform polynomial time with exact or fixed bounded-error on-promise behavior. The same extraction preserves uniqueness, and final verification checks all other cases without assuming correct behavior. Apply the Valiant-Vazirani randomized isolation theorem followed by a parsimonious 3-CNF gate encoding of the isolating XOR constraints (full equivalences uniquely extend source assignments). Inverse-polynomial isolation success times constant conditional extraction success is amplified with independent trials. Conversely NP=RP yields the broader randomized selector above. This does not establish that a deterministic unique-promise selector implies P=NP.

References: Valiant and Vazirani, NP is as easy as detecting unique solutions, TCS 47 (1986), https://doi.org/10.1016/0304-3975(86)90135-0 ; Trevisan complexity notes, https://theory.stanford.edu/~trevisan/notes/complexitynotes02.pdf .

## Total forced-choice reduction barrier

Suppose a deterministic polynomial-time many-one construction maps every SAT instance F to a formula H(F) such that exactly one branch is satisfiable, and SAT(F) iff branch 1 of H(F) is satisfiable. Then UNSAT(F) iff branch 0 is satisfiable. The latter is an NP predicate, so coNP subseteq NP and NP=coNP. This also holds when each H has exactly one satisfying assignment, but uniqueness of the model is not needed. Therefore earlier all-promise forced-choice reductions of easy explicit source functions cannot simply be replaced by a deterministic total forced-choice reduction of SAT without confronting NP vs coNP. This is a conditional implication, not a separation or impossibility theorem. The adaptive extraction above avoids this requirement.

## Finite regression

Enumerate all normalized width<=2 clause subsets on one and two variables (including empty clause), and 4096 subsets of a fixed mixed-width three-variable family. Enumerate every reachable prefix under all safe on-promise choices and both arbitrary off-promise outputs. Check the renamed branch truth against the original model restriction, check the prefix invariant, and verify all completed assignments. Expected 4616 formulas (1458 satisfiable, 3158 unsatisfiable), 51644 reachable states, 51284 branch checks, 26002 completed assignments (2436 verified, 23566 rejected), 20408 off-promise internal states. Finite oracles enumerate assignments only to validate the reductions; no efficient SAT selector is inferred.

## Boundary

This identifies the exact remaining uniform/nonuniform and randomized obligations. None of the earlier restricted architecture lower bounds is an unrestricted superpolynomial circuit lower bound. NP not subseteq P/poly would imply P!=NP but is stronger than the needed separation and its converse is not known. NP=RP is not known to imply P=NP. No new Lean declaration or P versus NP resolution. Next: investigate uniform algorithmic structure with an explicit cost and correctness model, or a genuine unrestricted lower-bound approach, rather than treating further restricted transfers as a resolution.
