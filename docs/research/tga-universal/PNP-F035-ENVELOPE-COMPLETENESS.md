# PNP-F035/F038 — Valid input-bound envelope completeness

PNP_RESOLUTION_STATUS = OPEN.

Candidate builds on ordinary typed refutation completeness, whose 19
declarations passed the zero-axiom audit but executable harness failed
on a swapped argument. Parent repair 83ca79f4fe5d89e23230a93226ad2a29e87678c6
requires exact-head successful replay. New candidate retains validId
and validClause through finite splitting and the frontier-copy compiler.

For every finite f and n with validFormula n f = true, there exists an
envelope e with boundCheck n f e = true iff f is unsatisfiable. For n>0
use identifier 1 for weakening and copy steps; branch pivots come from
the original variable list. Preserve the identifier range of every
derived blocking clause and every step. For n=0 a valid UNSAT formula
must contain an empty clause, giving a proof with zero batches.
The original ordered formula and n are bound exactly.

This is ordinary typed envelope existence, not universal decimal byte
encoding completeness, machine-cost refinement or polynomial certificate
size. Finite splitting remains exponential. The executable finite
prototype is not a formally refined generator. 19 candidate declarations,
24 control groups, strict Lean 4.14.0 and explicit zero-axiom audit.
Marker F035_ENVELOPE_COMPLETENESS_OK pairs=16 singles=4 empty=2 sparse=1 zero=1.
Fresh exact-head CI required. Main unchanged.
