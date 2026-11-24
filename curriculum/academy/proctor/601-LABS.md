# Proctor 601 — specialist laboratory and answer guide

Use these public practice problems; an assessor must choose unseen equivalent variants for actual grading. Each exercise combines exact reasoning with the stated proof boundary.

## RH: Hankel form
Given moments (1,0,−1), construct the 2×2 Hankel matrix and evaluate q=(0,1). Answer: −1, so this matrix is not PSD. It is synthetic data, not actual xi moments. Extend by deriving q^T H q = Σ_i Σ_j q_i q_j m_(i+j). Lean rh_finite_observation formalizes only the implication from a universal property to one instance; the converse is not proved.

## P versus NP: reductions
Check CNF (x) AND (not x). Both assignments fail. Prove that satisfiability-preserving reductions compose by chaining two biconditionals (Lean pnp_compose). Add complexity hypotheses: both maps and the terminal decision algorithm must have polynomial total bit complexity. This single CNF is not a lower bound or universal algorithm.

## Navier–Stokes: conditional continuation
For scalar amplitude ratio 1/2 the squared ratio is 1/4. This is not a PDE solution. Independently derive the enstrophy estimate from U001 using Hölder, Sobolev interpolation and Young, explicitly preserving smoothness and boundary assumptions. Lean ns_continuation only formalizes the final contradiction given the continuation implication and bound.

## Yang–Mills: regulator dependence
For q=1/2,1/4,1/8,1/16 and eigenvalue ratio r=(1−q)/(1+q), calculate 1−r=2/3,2/5,2/9,2/17. Show r→1, hence −log r→0. A positive gap at every finite regulator is insufficient. Lean ym_single_channel_not_all supplies a two-channel logical countermodel, not a field theory.

## Hodge: algebraic class scope
Compute det([[2,1],[1,2]])=3; prove a determinant is nonzero iff the pairing matrix is invertible in this finite case. Explain why a matrix calculation does not establish a geometric cycle. Derive the additive closure of represented classes (Lean hodge_sum), then identify the primitive representative missing in U001 and the square-root obstruction in U002.

## BSD: finite support
For proposed annihilators 6,30,210 use summands Z/5,Z/7,Z/11 respectively; residues 1,2,1 are nonzero. Show in the abstract direct sum over all primes that every finite integer fails to annihilate some summand. This is not a counterexample elliptic curve. Lean bsd_zero_defect proves the elementary arithmetic implication given comparison and defect identities, not those identities for all curves.

## Poincaré: hypotheses
Identify a missing hypothesis in a two-condition implication: homology alone does not supply simple connectivity. Inspect Lean poincare_extra_hypothesis, a propositional abstraction with the implication explicitly assumed. Read a source for the established Perelman theorem, list its actual hypotheses, and explain why a sphere-homology probe is insufficient.

## Formal evidence record
For each of the eight formal lemmas record the exact statement, which hypotheses are assumed, command, toolchain, exit status and axiom report. A kernel-checked conditional proof cannot establish its antecedent. The negative-control theorem must be in a separate file so successful modules remain compilable. No claim of novelty.
