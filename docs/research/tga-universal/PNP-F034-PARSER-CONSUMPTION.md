# PNP-F034 — Successful parser consumption and byte-size bound

PNP_RESOLUTION_STATUS = OPEN. PR #180 merged at
20418ae4d45d31a935bbf914ca5e7e9ad8610ef1. Initial run 45508946038
job 138851359993 failed:
artifacts/pnp-f030/f034-encoded-size-combined.lean:4637:17: error: unsolved goals
artifacts/pnp-f030/f034-encoded-size-combined.lean:4743:63: error: expected type must not contain free or meta variables
artifacts/pnp-f030/f034-encoded-size-combined.lean:4756:2: error: type mismatch
artifacts/pnp-f030/f034-encoded-size-combined.lean:4767:56: error: expected type must not contain free or meta variables
Process completed with exit code 1.
Repository correction 1817fe6c0fffe1a0f2b81f1e8c864d1809fe8058
resolved associativity, explicit binder type and closed numeral goals.
Final run 45510177344 job 138855571352 passed all twenty zero-axiom
declarations and 53 data-pair controls (19 accepted,34 rejected).
Artifact 14974849199.
https://github.com/tltmgnt/MathOS/actions/runs/45508946038/job/138851359993
https://github.com/tltmgnt/MathOS/actions/runs/45510177344/job/138855571352

## New scope

Consumes p enc means every successful parse p ts = some(a,rest)
has ts = enc a ++ rest. Prove it for all typed custom-data parsers,
including the accumulator invariant of manyAux, length-prefixed
lists, terminal tags and both magic headers. This is the missing
successful-decode converse, not just an encoder round-trip test.
Together with the previous independent Wire grammar, wire_length
shows one token requires at least one byte. Thus for successfully
decoded custom-data file pairs (including semantically rejected
proofs), canonical token size S <= A = sum of input byte lengths.

global_mono proves monotonicity of the explicit prior resource
polynomial using constructive arithmetic. byte_budget composes
the verified global_meter with the candidate size bridge:
selected boundMeter charges <= globalUnit(2A+1).
accepted_byte_sound also concludes UNSAT on checkBytes acceptance.

23 candidate declarations, no production checker changes. The
static runner reuses all 67 data fixtures (including malformed
inputs), tests exact canonical token equality on each successful
decode, byte budget on every successfully decoded pair and exact
19 certificate acceptances. New CI pending. No local Lean.
Required marker F034_PARSER_CONSUMPTION_OK cases=67 accepted=19.

This is the custom decimal data format only. The separate DIMACS
expected-file path needs its own size bridge. Parser runtime,
integer bit cost, compiler, IO, complete machine-time accounting
and independent review remain outside the theorem. No bound on
proof discovery or required proof size; no P vs NP claim.
Existing strict zero-axiom gates retained; main unchanged.
Next: DIMACS size bridge and explicit parser/bit-cost accounting.
