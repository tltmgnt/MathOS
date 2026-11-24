# Full-target attack: unrestricted SAT and horizontal BSD finiteness

**MathOS | 24 November 2026 | Universal proof not obtained**

## 1. Why the previous completion is not a solution

Cycle 6 completed two defined use cases. The 14 canonical mathematical obligations remain open. Independent review is nonblocking for internal research, but the exact universal statement must still be proved. This note attacks the step from the scoped AND/XOR decision procedure to arbitrary SAT and the step from one primary Sha calculation to full finiteness.

## 2. Unrestricted AND/affine SAT

Let A x=b be an arbitrary affine system over GF(2) in N Boolean variables, together with any finite collection of gates y=a AND b. Gate variables may overlap without restriction. Every 3-CNF formula reduces in polynomial time to this system. For each clause introduce three fresh variables equal to the negations of its literals, enforce those equalities by affine rows, and two AND gates computing their product. Set the last output to zero. The clause holds exactly when this product is zero. There are five new variables, four affine rows and two gates per clause. Thus a polynomial solver for this system would prove P=NP; deciding its satisfiability is NP-complete by the reduction and direct polynomial witness verification.

## 3. A complete rank-adaptive decision algorithm

First solve the affine equations by Gaussian elimination. If consistent their solution space is x0+V, with V a linear subspace. Select the first operand of each gate and let P be the coordinate projection onto the distinct selected variables. Compute a basis of P(V) and let r be its dimension. Enumerate precisely the 2^r possible values of P(x) in P(x0)+P(V). In each branch add affine equations fixing the chosen operands. Every gate becomes affine: if its fixed operand is zero enforce y=0, and if one enforce y=b. Solve the augmented affine system. Any resulting witness satisfies the original gate equations and rows. Conversely any solution has a projected value in the enumeration and satisfies the corresponding linearized equations. Exhaustion with no witness proves unsatisfiability. Repeated or overlapping gate variables do not invalidate the argument.

Each branch costs polynomial total bit operations, including the projection-basis calculation, enumeration and Gaussian elimination. Therefore runtime is O(2^r poly(L)), where L is explicit input bit length. This is polynomial on subfamilies with r=O(log L), and a complete decision procedure for general inputs, but not a polynomial bound for all inputs.

## 4. The exact obstruction

For k gates on disjoint triples (a_i,b_i,y_i), impose a_i+b_i=1, y_i=1, and y_i=a_i AND b_i. The affine system permits every assignment of the selected a_i, so r=k; however every nonlinear branch is inconsistent because a_i and b_i are complementary. The stated implementation visits all 2^k branches. A different solver could reject this family immediately. This is a worst-case lower bound for the declared enumeration implementation, not all SAT algorithms and not P≠NP. The hoped-for universal logarithmic rank bound is false. A proof of P=NP would need a different mechanism or a polynomial guarantee avoiding this enumeration on arbitrary instances. A proof of P≠NP requires an unrestricted lower bound, not this restricted example.

## 5. BSD: the missing all-prime theorem

Cycle 6 gives 5-primary triviality of Sha(E/Q) for E:y²=x³−1681x under its cited classical inputs. Together with the earlier 2-descent it says nothing decisive about infinitely many other primes. For an elliptic curve over Q, each fixed finite-level group Sha[N] is finite by the finite Selmer exact sequence. Full finiteness is therefore equivalent to the existence of one nonzero integer N annihilating Sha. Equivalently it requires both finiteness of every primary component and vanishing of all but finitely many primary components. The group direct sum over primes of Z/pZ shows why primary finiteness by itself cannot logically imply full finiteness for torsion groups. This is an abstract countermodel to the inference, not an example of infinite Sha for an elliptic curve.

Banwait's September 2026 preprint, arXiv:2609.08431, introduction sections 1.1–1.3, develops new prime-by-prime criteria for rank-two CM curves and explicitly distinguishes these from the unresolved uniform all-prime statement. Its criterion cannot simply be used as a universal nonvanishing theorem. To finish even the selected curve's full Sha use case, obtain an independently justified finite prime support bound and verify all remaining primary components, or prove a uniform annihilator theorem directly. General BSD additionally requires analytic rank equality on every elliptic curve and, for the refined MathOS target, the leading-term formula. No such theorem is derived here.

## 6. Outcome

The unrestricted SAT correctness step has a direct proof for the stated representation, but the general polynomial-time step fails for the tested algorithm. The all-prime BSD step remains open. This is a research attempt, not a complete solution, new complexity-class separation, or prize claim. No canonical obligation is promoted.

Replay: python -m mathos.research.breakthrough_full_target

Tests: python -m unittest discover -s tests -p 'test_breakthrough_full_target.py' -v

Source: MathOS cycle-six papers PNP-B006 and BSD-B006. B. S. Banwait, Second derivatives of p-adic L-functions and the Shafarevich–Tate group of rank-two CM elliptic curves (8 September 2026), https://arxiv.org/abs/2609.08431 . Clay Mathematics Institute, official problem status and rules: https://www.claymath.org/millennium-problems/ . The algorithm and reduction use elementary Boolean algebra and Gaussian elimination; no literature priority is claimed.
