# PNP-F034 — Selected front-end resource ledger

PNP_RESOLUTION_STATUS = OPEN.

Independent candidate on merged research head c6fcac63fd7ade7e6b4ce7d5df48608ae66f62a3.
Reuses the scanner padding/encoder, abstract token emission and amortized
token grammar theorems. Both decoder projections target the existing
fuel-free decoders on every byte list, including malformed input.
The grammar meter is an alternative instrumented parser; equality of
results is not a cost simulation of the fuel-free parser.

For a total byte length B across the expected-input and envelope streams,
the proposed seven-coordinate reservation is:
(5235*B,1046*B+16,20*B,1047*B,21*B,1536*B,64*B+6).
Coordinates are scanner gates, narrow/zero visits, byte prepass visits,
padding visits, selected digit encoder events, abstract token emission
events, and selected token grammar events. Successful tokenization
bounds token count by byte count via the exact wire consumption theorem;
grammar charge is zero if tokenization fails. Two independent stream
reservations compose coordinatewise, retaining the additive constants.
Not a single instrumented trace, full decoder cost, or whole-machine
complexity bound. Nat arithmetic, allocation and further structural
operations remain outside these coordinates.

12 candidate declarations and 209 control groups (156 short byte lists,
49 cross-pairs and 4 positive decode fixtures). Controls compare decode
success flags, seven resource bounds and pair budget arithmetic; exact
typed equality is the proposed kernel theorem, not the executable test.
Strict Lean 4.14.0 warnings-as-errors and explicit zero-axiom checks:
F034_FRONTEND_RESOURCE_LEDGER_OK small=156 pairs=49 positive=4.
Fresh exact-head replay required; no local Lean execution or certificate
completeness claim.
