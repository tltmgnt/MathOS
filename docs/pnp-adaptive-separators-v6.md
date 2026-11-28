# MathOS v6 — adaptive certified separator discovery

V5 selects the highest-occurrence variable in a connected residual CNF.
V6 adds a deterministic alternative that inspects both Boolean residuals
for every active variable. It ranks by worst largest residual component,
then total mass in components above the bounded leaf cap, then aggregate
active mass and variable ID. It recomputes after each recursive split.
It does not search for an optimal multi-variable separator.

The unchanged V5 verifier checks the actual signed witness or UNSAT tree.
A score is not a proof of satisfiability, contradiction or hardness.
The optional selector changes only the producer; the default V5 path
and certificate schema remain identical. The existing Lean logical
gate still runs on producer changes; no new Lean theorem is claimed.

Run:
    
    python -m unittest discover -s tests -p 'test_pnp_adaptive_separators.py' -v
    python -m mathos.research.pnp_adaptive_separators

The report compares frequency and adaptive selection at identical split
depth (one) on paired planted SAT/UNSAT block families and a dense
negative control. It records certificates, replay status, chosen
variables, component scores and cooperative work counters. Both SAT and
UNSAT controls are designed to have a low-occurrence separator whose
removal leaves six-variable components. The dense control remains
outside one-step recognition; unknown is not a lower bound on SAT.

For input size N and active-variable count V <= N, ranking performs
two conditioning and incidence-component passes for each of V candidates,
with sorting of at most V rows. This adds polynomial work to each
bounded recursive node of V5. With fixed depth and enumeration cap,
the combined search is polynomial under the same unit-cost operation
model as V5. No asymptotic speedup or hard process memory guarantee
is claimed. Resource exhaustion is propagated, not converted to UNSAT.

Next obligation: characterize and recognize multi-variable separators
or backdoor sets within a fixed search budget, and test where adaptive
single-variable greedy selection fails. P vs NP remains unresolved.
