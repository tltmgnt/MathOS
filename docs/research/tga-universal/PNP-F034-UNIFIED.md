# PNP-F034 — Unified typed UNSAT replay and input binding

PNP_RESOLUTION_STATUS = OPEN. PR #166 merged at
7881db126b9276c8ff433b12597962cbded6f49f. Original run
45478518440 job 138745070561 failed:
artifacts/pnp-f030/f034-xor-replay-combined.lean:1202:10: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
artifacts/pnp-f030/f034-xor-replay-combined.lean:1205:10: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
Process completed with exit code 1.
Repository correction 2a2e5b9fe5991053b0b30be6486b75fc33981e06
removed redundant rewrites. Final PR run 45479430046 job
138748273347 passed three Python tests, all twelve XOR declarations
with zero axioms, and exact F034_XOR_REPLAY_OK cases=18.
Artifact 14960668022. The same correction restricted adaptive
push CI to main to avoid duplicate runs on research PRs;
pull_request and workflow_dispatch remained available. This
change is inherited, not introduced by the present PR.
https://github.com/tltmgnt/MathOS/actions/runs/45478518440/job/138745070561
https://github.com/tltmgnt/MathOS/actions/runs/45479430046/job/138748273347

## Typed dispatcher and theorem

ProctorUnifiedReplay combines checked paired batches with exactly
one terminal: empty clause, capacity or sparse XOR. The scope
flag selects the final frontier or original plus frontier;
each is entailed by the input if the chain is checked.
The typed Proof is not allowed to assert SAT or UNKNOWN.
Six candidate declarations prove terminal dispatch soundness,
target entailment, unified checking, input-bound soundness,
exact binding and original literal-range soundness.

The boundCheck entry point takes an independently supplied
expected typed ordered formula and variable bound, plus a
producer envelope with its claimed original and bound.
It compares exact list equality (including row order and
duplicates) and numeric bound equality. It validates every
original literal, pivot and tail label, group literal, parity
support and annotated reference literal against 1..n. It then
checks the proof against the EXPECTED formula, not the envelope.
Parent and row indices are independently validated by previous
checkers. The theorem bound_sound concludes UNSAT of expected
from boundCheck=true, not UNSAT of some proof-supplied formula.

The equality check is stricter than semantic equivalence;
permutations of equivalent input may be rejected. This is
intentional to make index binding unambiguous. No digest is
trusted as proof of equality. The Boolean range check is
enforced for proof labels; only original-label range soundness
has a separate theorem. The old Python checkers and routing
are unchanged. Not all their certificate types are supported
by this typed dispatcher (in particular dynamic search and
BVE projection). It is not a complete SAT decision system.

## Input trust boundary

A successful check against a formula provided solely by a
proof producer proves only that formula UNSAT. It does not
establish that the formula represents the user's intended
problem. This PR requires a distinct caller-supplied typed
expected input. The CI exporter constructs both from fixtures,
not from an independent external DIMACS file, and remains
trusted for translation. No external parser, byte binding,
untrusted source-code loader, cryptographic authenticity or
production CLI is verified. A next step is a bounded data-only
parser with a theorem connecting accepted bytes to typed data
and an independently supplied expected input.

## Validation

Reuse all 17 capacity and 18 XOR fixtures plus direct and
chained empty terminals, an actual augmented-only XOR proof
and wrong-scope rejection, seven substituted-input/variable
bound cases and six invalid label controls. Total 53 fixtures
(19 expected acceptances, 34 expected rejections), with
deterministic chunked typed export and exact marker
F034_UNIFIED_REPLAY_OK cases=53. New results pending CI.
All existing strict gates preserved; new six exact zero-axiom
checks and Lean 4.14.0 warnings-as-errors. Same-author mirror
is not independent review. No full Python refinement, total
machine-cost theorem, original scratch port or main change.
