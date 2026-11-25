# PNP-F034 — Unified checker selected resource ledger

PNP_RESOLUTION_STATUS = OPEN.

Based on merged research head c6fcac63fd7ade7e6b4ce7d5df48608ae66f62a3
(PRs #233–234 merged), with the four unmodified pending capacity ledger
files from d86135b16fd3b74d150441ff50d6bdea7b3464ae incorporated on
this separate integration branch. Capacity preflight not yet confirmed
at integration time; fresh integrated replay is required.

Candidate composes the independent binding, proof-range, resolution
chain and terminal meters in a single Bool × Nat × Nat (result, selected
lookup visits, selected comparison gates). Empty clause structural scan
is uncharged in these coordinates. Proposed projection equals the
verified unified binary checker on arbitrary typed operands and the
original checker on all byte pairs. Conditional UNSAT soundness is
inherited. Failed decoding returns (false,0,0), meaning no checker
reservation, not that decoding costs nothing.

The selected visit budget is chainVisitBudget + terminalVisitBudget;
the selected gate budget is partialGateBudget + terminalGateBudget.
Terminal budgets dispatch over empty/capacity/XOR. Capacity demand
lookups are the hoisted alternative implementation in its meter.
This remains an eager conservative reservation, not a trace of the
short-circuit checker. It excludes scanner/decoder resources, structural
traversal, arithmetic, Boolean combining, encoding, padding, allocation,
and other machine costs. Data-dependent budgets are not closed
polynomial bounds in serialized length.

Eight candidate declarations, 218 control groups (196 cross-pairs
checking value and both resource bounds, 6 positive, 5 negative,
11 typed ledgers). Strict Lean 4.14.0 warnings-as-errors, exact marker
F034_UNIFIED_RESOURCE_LEDGER_OK pairs=196 positive=6 negative=5 ledgers=11
and eight explicit zero-axiom checks. No local Lean execution.
No certificate completeness or P vs NP resolution claim.
