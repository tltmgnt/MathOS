# Native XOR explanations during conflict learning

## Verified predecessor

PR #303, run 46139267316: both evidence and Lean jobs passed.
Projected portfolio and frozen XOR portfolio both decided 171/171.
All three standalone XOR mixed-SAT misses were recovered by projection;
the predecessor portfolio already solved them by fallback, so this is
a route improvement, not a portfolio coverage gain. On 12 affine-lifted
random CNFs the projected portfolio credited ten SAT and two projected
RUP proofs, with 108972 vs 174473 counted work, 49.528 vs 89.551 ms
observed solver-call time, and 12665 vs 4346 stored certificate bytes.
On archived mixed graphs work 49278 vs 53509. Nested-wrapper overhead
increased observed time on several unchanged families. Synthetic data,
not third-party blind validation.

## Native mechanism

Keep original coordinates and all original CNF clauses. After ordinary
watched-literal propagation, Gaussian elimination on extracted implied
rows restricted to the current partial assignment derives contradictions
or forced literals. Each derived row records the XOR of original source
rows. Its explanation clause contains exactly one literal per variable
of that combined row, with a falsifying assignment of incorrect parity.
Thus it is entailed by the original CNF. Use these clauses as implication
reasons in first-UIP analysis; they are not inserted into ordinary
watch lists, so elimination rederives relevant native reasons after a
backjump. Ordinary learned clauses are watched as before.

UNSAT certificates contain source row witnesses and chronological
events, either XOR explanations or ordinary RUP additions, ending with
an empty RUP addition. The checker independently truth-table checks
each source row using the existing local verifier; checks provenance
by set symmetric difference, exact explanation support and wrong
parity of its falsifying assignment; then replays each RUP step
against original clauses plus earlier checked explanations/additions.
SAT is direct original witness replay. Intermediate native events on
SAT runs are not exported as certificates; counts are observational.
No new variables or auxiliary XOR gates are introduced. The search
is a separate adaptation of frozen CDCL; duplicated code is a
maintenance cost, and default predecessor behavior is not modified.
Gaussian elimination is recomputed at each Boolean fixpoint, not
incrementally maintained; expensive scans or RUP replay can erase
any gains. Explanation size can grow with row support and provenance.
Resource exhaustion is UNKNOWN.

## Evaluation

191 cases: 171 archived plus 12 new random base CNFs (16/18 variables)
masked through two latent bits per copied coordinate, and eight
explicit native equality/inequality controls. Base reference is
exhaustive bitset evaluation; the constructed controls follow
elementary parity and residual-clause arguments. Public synthetic
development set, not a blind industrial comparison. Seed 192208.
Four matched arms at 100000 counted steps and five cooperative
seconds: frozen projected portfolio, standalone projection, native
standalone and native-first portfolio. The probe receives 20% of
configured budget only on larger eligible mixed parity instances
without Hall eligibility; unused resources pass to unchanged fallback.
No proof of equal-budget dominance; measured timing includes nested
replay overhead, and feature scans and some Python overhead are not
charged. Require 171 archived decisions, no paired baseline losses,
and at least one integrated native XOR explanation refutation on the
new controls. Report all unknowns and gains, even if the gate fails;
a pass alone does not establish speed or coverage superiority.

Tests include exhaustive partial-trail semantic checks, mixed-proof
forgeries, 600 small mixed CNFs against exhaustive reference, budget
and serialized certificate replay. Lean checks local two-bit parity
explanation, XOR combination, and entailment transfer only, not full
finite Gaussian or Python checker correctness. No changes to existing
solver or tests. No P versus NP claim. New results pending CI; do not
merge before verification and review.
