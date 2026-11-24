# PNP-F034 — Encoded-size selected-charge polynomial

PNP_RESOLUTION_STATUS = OPEN. PR #179 merged at
9c0aa409237184afa272ab80ff0459911fd98064. Initial run
45505543106 job 138839679676 failed, including:
artifacts/pnp-f030/f034-terminal-polynomial-combined.lean:3639:32: error: unknown identifier 'wordsBudget'
artifacts/pnp-f030/f034-terminal-polynomial-combined.lean:3706:21: error: type mismatch
artifacts/pnp-f030/f034-terminal-polynomial-combined.lean:3782:2: error: index in target's type is not a variable (consider using the `cases` tactic instead)
artifacts/pnp-f030/f034-terminal-polynomial-combined.lean:3901:5: error: unknown identifier 'nc!'
Process completed with exit code 1.
Correction 73288af4e3a43f90cdcd62fadae1064b4672dce3
resolved imports, arithmetic, induction and spacing. Final run
45507232877 job 138845457428 passed all 24 zero-axiom declarations
and 24 capacity, 21 XOR controls. Artifact 14974760482.
https://github.com/tltmgnt/MathOS/actions/runs/45505543106/job/138839679676
https://github.com/tltmgnt/MathOS/actions/runs/45507232877/job/138845457428

## Candidate global theorem

S = length(encExpected n f) + length(encEnvelope e) is the exact
natural-token count of the canonical typed encoders, not the
numeric variable bound. B = 2S+1 accommodates an augmented target
which may duplicate the original. The bridge proves that explicit
formula, chain, reference, group, block and support masses are
dominated by B; binding and range budgets are dominated by four
times the relevant encoder length. No input validity hypothesis
is needed for the typed bounds.

globalUnit B = 1 + 3*(4B) + B*stepUnit B +
  (B + capacityUnit B + xorUnit B).
The parent and terminal units were defined in previous verified
modules. This is a polynomial of degree at most four after
expanding the fixed-depth binary recurrence, as an elementary
algebraic observation. The candidate Lean global_budget and
global_meter declarations prove the explicit inequality against
that expression. global_sound pairs it with semantic UNSAT
soundness on an accepted typed verdict. No claim of a formally
defined asymptotic complexity class or optimized constant.

The theorem is in canonical encoded token length. It does not
yet prove that every accepted arbitrary external byte stream
has canonical encoding length at most its byte length; that
requires a typed-parser converse or consumption-size theorem.
The 53 existing fixture tests check that inequality empirically
for those files, plus the global bound and verdict equivalence.

20 candidate zero-axiom declarations, new CI pending.
Required marker F034_ENCODED_SIZE_OK cases=53 accepted=19 rejected=34.
No local Lean; existing strict gates unchanged. No parser cost,
allocator, arithmetic bit cost, compiler/IO refinement, actual
production trace, independent review or proof-discovery bound.
No original scratch port, main change or unrestricted SAT claim.
Next: typed parser consumption bridge for arbitrary accepted data
and explicit bit-cost accounting, keeping proof-size and search
separate from verification.
