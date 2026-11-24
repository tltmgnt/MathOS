# PNP-F034 — Bounded mixed inference and semantic composition

PNP_RESOLUTION_STATUS = OPEN. PR #161 merged at
0d4e487d1b63e31011016c7c5072d19a81eb9618. CI run 45466438787
job 138702483041 passed five tests, all 1600 random cases
UNKNOWN (there were no random mixed positives), all 12 guarded
PHP mixed refutations and six equal controls. At h=4 old dynamic
used 95/99 nodes; h=5 511/515; h=6,7 UNKNOWN at 1000; h=16,32
UNKNOWN at one node. At h=32 both seeds used 16929 paired
resolution steps, 103554 signatures and 1584 Hall edge scans.
Artifact 14955522068.
https://github.com/tltmgnt/MathOS/actions/runs/45466438787/job/138702483041

## Routing and certificate boundary

Try the existing combined nonbranching policy with the supplied
pair budget and zero search nodes. If UNKNOWN, perform one round
of paired equal-tail resolution. Stop at either signature or
distinct derived-clause limit; keep the sound prefix. Try capacity
one/two, signed Hall, positive Hall and XOR on the derived subset
and then on original clauses plus derived clauses. Return MIXED
only for a checked UNSAT result. A derived subset is entailed,
not equivalent, so no SAT witness from it may be promoted. If
neither scope refutes, invoke the existing hybrid on ORIGINAL
clauses with the remaining pair budget and supplied node budget.
Original fallback may repeat uncharged recognition; initial
BVE pair charges are not refunded. This is an explicit routing
choice rather than an optimized schedule. Existing entry points
are unchanged.

MIXED evidence is (original-parent steps, scope, inner route,
inner certificate). Replay exact normalized equal tails with
opposing pivots; verify the inner proof on the reconstructed
scope. Reject malformed parents, scope, route, UNKNOWN and SAT.
Counters are not evidence. All SAT decisions are from original
fallback and checked against original CNF. Zero signature or
step budget disables paired inference; zero pair and node budget
does not disable the ordinary nonbranching or mixed routes.

The four separately counted quantities are signatures, emitted
resolution steps, BVE pairs and dynamic nodes; matching edge
scans are additionally reported. They do not cap normalization,
tail length, arithmetic, discovery, proof replay or total time.
One round only, no saturation and no recursive mixed inference.
Default 200000 signatures and 100000 steps cover the tested
guarded PHP through 32 holes; not a universal sufficient budget.

## Formal candidate composition

ProctorMixedInference.lean proves signed paired resolution for
normalized lists with a pivot at the head, finite batch entailment,
UNSAT lifting for a derived subset, conjunction of formula models
under append, and UNSAT lifting for original plus derived.
These generic composition results apply to any sound inner refutation
and in particular the previously verified capacity theorem with
its supplied hypotheses. They do not formalize parent index parsing,
literal normalization, permutations or executable dispatch. The
new five declarations must pass strict Lean 4.14.0 warnings-as-errors
and zero-axiom checks; prior gates unchanged. No local Lean available.

## Controls and limitations

1000 small sparse random formulas at three budgets (3000 runs),
six guarded PHP and six guarded odd-charge cubic graph fixtures
through 80 vertices, original/derived versus augmented scope,
zero and prefix budgets, tamper, fallback SAT and pair accounting.
The mixed router is still heuristic and incomplete at bounded
budgets. No proof-complexity lower bound for mixed proof languages
or general SAT follows from the previous policy-specific result.
New tests and formal declarations await actual CI. No executable
refinement, machine-cost theorem, independent review or scratch
port. Main unchanged. Next: audit a multi-round obstruction and
the actual verifier-to-semantics gap before extending the policy.
