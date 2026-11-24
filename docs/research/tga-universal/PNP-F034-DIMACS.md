# PNP-F034 — Strict DIMACS expected-input subset

PNP_RESOLUTION_STATUS = OPEN. PR #170 merged at
c5ff88c321fb6385680f51d307d4ae1e0147eb05. Initial CI run
45488695711 job 138780876670 failed (representative exact message):
artifacts/pnp-f030/f034-envelope-combined.lean:1988:33: error: invalid constructor ⟨...⟩, expected type must be an inductive type 
Process completed with exit code 1.
Repository correction e17beec31198256ed890994c40bb17d0fd322e6a
used explicit structure constructors. Final PR run 45489480704 job
138783615174 passed all thirteen zero-axiom declarations and
F034_ENVELOPE_ROUNDTRIP_OK envelopes=53. Artifact 14966610622.
https://github.com/tltmgnt/MathOS/actions/runs/45488695711/job/138780876670
https://github.com/tltmgnt/MathOS/actions/runs/45489480704/job/138783615174

## Accepted subset and trust boundary

New static Lean parser accepts a first-line header beginning exactly
with ASCII "p cnf " followed by two canonical natural tokens n m and
LF (CRLF is accepted). The header suffix and body accept space, tab,
LF and CR as whitespace. Body tokens are canonical decimal naturals,
optionally preceded by a single minus for nonzero literals. Positive
zero terminates each clause; the body must contain exactly m terminated
clauses and no other tokens. Literals must lie in 1..n. Empty clauses,
duplicates, and clauses spanning lines are retained. No comments,
leading zeros, plus signs, additional headers or other DIMACS
extensions are accepted. This is explicitly a subset, not a general
DIMACS implementation. File limit 1,000,000 bytes, digit limit 128,
clause and per-clause literal count limit 100,000.

The expected file is now read directly by the Lean checker as DIMACS
bytes; no Python conversion of expected input is trusted at runtime.
The existing proof envelope is still the custom data format, not
DRAT/LRAT. The decoded expected formula and n must exactly equal
the claimed formula and n in the certificate; order and duplicates
are significant. The new CLI uses the existing bounded chunk-reading
algorithm; no proof-supplied source is evaluated. Reject is not SAT.
Build with bash scripts/build_proctor_dimacs_checker.sh checker.lean
and run lean -DwarningAsError=true --run checker.lean -- expected.cnf certificate.proofdata
using pinned Lean 4.14.0. This is a source bundle, not a native binary.

## Formal scope

Row and Rows are independent inductive zero-terminated token
grammars. Four candidate theorems prove both directions between
the row/body parsers and these grammars, preserving order and
clause count. Meaning uses the explicit byte lexer and independent
token grammar. Two candidate theorems connect decodeDimacs and
Meaning in both directions; three more connect checker acceptance
to successful decoding, exact binding and UNSAT of that meaning.
The byte lexer itself is not proved equivalent to an independently
specified raw DIMACS grammar. I/O, compiler and Python export
remain outside the refinement boundary; no standard-wide parser
completeness, total resource or machine-cost theorem is claimed.

## Validation

53 prior unified fixture inputs, including two invalid literal-range
cases; 20 handwritten cases (five parse-positive, fifteen malformed)
cover multiline/CRLF/EOF whitespace, duplicates, empty clauses,
zero-clause SAT, count mismatch, missing zero, negative zero, plus,
leading zero, comments, invalid range, extra tokens, and size limits.
Expected 73 file pairs: 56 parse, 22 certificate accept, 51 reject.
For each valid parse compare exact ordered typed formula and n to a
separately serialized expected-data fixture. This is a same-author
differential check, not independent review. New nine declarations
and exact execution marker F034_DIMACS_REPLAY_OK cases=73 parsed=56 accepted=22 rejected=51
are subject to strict CI. No local Lean; outcomes pending.
Existing strict gates and inherited PR trigger policy unchanged.
Main unchanged. No scratch port or unrestricted SAT result.
Next: independent DIMACS byte lexical grammar and correctness,
then resource accounting and additional proof-format interoperability.
