# PNP-F034 — Fuel-free nested decoder composition

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base cc33fe0873b0511b5d9d4f7ff32511baf3613848 (PR #198).
Eight files copied byte-identically from exact verified heads:
- PR #199 c0079273a472b7875b9fa24af32ab7b7444c190c, preflight 45531466656/job 138927564359,
  artifact 14985407107, 5 zero-axiom declarations, 2160 controls.
- PR #200 7d217e942aa8af00c4c4a19f4930ab5a1c5322fe, preflight 45533326956/job 138933790535,
  artifact 14985931282, 18 zero-axiom declarations, 117 controls.
Both PRs are open at candidate creation. Do not open this PR until
both merge and the exact candidate SHA passes mandatory replay.

Specialize the abstract nested ListBuilder contract to listWord.
Compose the existing binary byte-length prepass and decimal scanner
with fuel-free binary list iteration at every nested parser level.
Candidate exact equality of expected decoder, envelope decoder and
checker against the original; equality with the structural-fuel
variant; inherited soundness. No original checker or production
implementation changes. Boundary Nat list-limit guard, checked
encoding, Nat byte classification and emitted token conversion,
and typed Nat checker operations remain. Transition doubling is
not a logarithmic-time parser: the underlying element transitions
still execute in sequence. Closure allocation, dispatch, calls,
memory access, and total cost are not established.

Six candidate declarations. Retain all 117 nested decoder controls
and additionally compare the fuel-free checker to the structural-fuel
checker on the same 96 pairs. Required marker:
F034_FUEL_FREE_DECODER_OK expected=8 envelope=12 checker=96 positive=1
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gate unchanged.
No local Lean execution; no independent review or resolution claim.
