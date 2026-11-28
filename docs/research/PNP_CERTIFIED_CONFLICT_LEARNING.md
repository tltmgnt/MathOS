# Certified conflict learning — isolated research candidate

## Verified predecessor

PR #288's run 46135333996 passed both evidence and formal jobs.
Hall-first achieved 73/73 against v16 64/73, no paired losses.
The three previously unresolved pigeon instances and six new scaled
pigeon instances were recovered. New pigeon group: v16 1/7,
Hall-first 7/7, counted work 527419 versus 38187. Mixed group:
both 12/12 SAT; Hall-first added work (18148 versus 15354).
This group had no UNSAT controls; it does not establish generalization
to mixed UNSAT formulas. No claim of third-party blinded validation.

## Mechanism

The existing Hall and v16 paths remain unchanged. New iterative
watched-literal propagation and first-UIP conflict analysis resolves
false clauses with implication reasons until one current-level literal
remains. Backtrack to the maximum level of other literals, append the
asserting clause, and continue. Nonchronological jumps and conflicts
are observed statistics. A root conflict yields an explicit empty
clause addition. All UNSAT additions independently replay using v17
RUP on the original CNF. SAT is a direct model checked on original CNF;
intermediate internal learned clauses on SAT runs are not exported
as mathematical certificates. Exhaustion, including replay exhaustion,
is UNKNOWN. No proof reuse, external solver, clause deletion, restart
or asymptotic improvement is claimed.

A new route is eligible only for more than 16 active variables with
no Hall gate match, and receives 60% of configured budget. Hall/v16
receives unused resources; on ineligible inputs it gets its full
budget. This is an experimental heuristic, not a dominance theorem.
Counters are route-specific cooperative measures; allocation,
validation, external replay and Python overhead are not fully
charged. CDCL proof replay uses a slower independent scan algorithm,
so replay can itself obstruct coverage.

## Frozen protocol

129 cases: existing 73 Hall cases, archived 24 v16 seed 16028 cases,
24 new random 3-CNFs (18/20 variables, densities 3.8–4.9, seed 191903),
and eight even 3-XOR cycle encodings (19–49 variables; both labels).
Small random reference uses independent exhaustive bitset evaluation
up to 20 variables. Parity reference sums all equations modulo 2
(every variable occurs evenly), or gives the all-zero witness.
Compare Hall, standalone full-budget CDCL, and candidate under
100000 steps / 5 cooperative seconds. Rotate order and separately
replay all credited results. Retain all old coverage, no paired Hall
loss, require strict new coverage gain. Expose unresolved IDs and
standalone-only wins. Public synthetic development set, not blind
external evidence. The 129-case gate is new, not a substitute for
the v18 integration gates.

Lean verifies only elementary resolution soundness and assumption
discharge, not the Python checker or implementation. New tests
include 512 exhaustive two-variable CNFs, 1600 seeded randomized
CNFs, forged proofs, depth and budget controls, and portfolio
binding. No new measured outcomes are asserted before execution.
Do not merge before integrated results and review.
