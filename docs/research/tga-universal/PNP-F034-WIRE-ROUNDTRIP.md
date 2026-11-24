# PNP-F034 — Expected-CNF wire grammar and bounded file loading

PNP_RESOLUTION_STATUS = OPEN. PR #168 merged at
4e864309d68100cda91ff9e8e10262f8116046dd. Initial run
45483960988 job 138764245013 failed:
 /home/runner/.elan/toolchains/leanprover--lean4---v4.14.0/bin/lean: unrecognized option '--fixtures'
Process completed with exit code 1.
Repository correction 52ad4954daacc24252c3bbe278451f737b3b1f1c
inserted the CLI argument separator --. Final run 45484937080
job 138767683375 passed three Python tests, all three data
acceptance theorems zero axioms, and
F034_DATA_REPLAY_OK cases=67 accepted=19 rejected=48.
Artifact 14964127932.
https://github.com/tltmgnt/MathOS/actions/runs/45483960988/job/138764245013
https://github.com/tltmgnt/MathOS/actions/runs/45484937080/job/138767683375

## Candidate grammar correspondence

ProctorWireRoundtrip independently specifies the expected-CNF
token encoder (natural and Boolean tokens, count-prefixed
lists, literals, clauses, formula, expected magic and bound).
RoundTrip is a suffix-preserving decoder equation. FitsList
requires the explicit count bound and element premises.
The generic accumulator proof covers arbitrary bounded lists.
Word is an inductive decimal digit grammar with explicit
numeric accumulation, nonzero leading digit for multi-digit
tokens, digit count and ASCII constraints; Wire concatenates
words with one LF per token. The scanner theorem relates these
grammar witnesses to tokenization, and the expected byte
roundtrip composes this with the expected-CNF token encoder.
Thirteen candidate declarations, not yet kernel-confirmed.
The theorem is grammar-to-decoder only; no converse, unique
encoding theorem, general decimal printer correctness or
universal proof-envelope encoder theorem is claimed. The
numeric grammar is not DIMACS. Prior byte-input UNSAT theorem
still uses the decoded expected formula semantics.

## Bounded loader and source distribution

The production CLI now opens a binary handle and reads chunks
of at most 65536 bytes, never intentionally requesting beyond
byteLimit+1 cumulative bytes. It probes EOF at the exact limit,
continues on nonempty short reads and rejects over-limit data
without reading the remainder. Fuel is byteLimit+1 reads.
The pure decoder's existing length check is retained. The
fixture-mode verdict file is trusted CI metadata, not a proof
input. File handles, runtime read semantics, memory allocation,
compiler and IO are not formally refined. No total time or
memory bound is claimed; certificate checking can still be
expensive. A blocking stream is not time-bounded.

A static bundle builder concatenates only repository-owned
Lean sources; no generated fixture code or proof file enters
the source bundle. Build:
    bash scripts/build_proctor_data_checker.sh checker.lean
Run with pinned Lean 4.14.0:
    lean -DwarningAsError=true --run checker.lean -- expected.cnfdata certificate.proofdata
The source bundle preserves kernel printouts and requires
Lean; this is not a native standalone binary distribution.
The CLI's final verdict is CERTIFIED_UNSAT (exit 0) or
REJECTED (exit 1); rejection does not mean SAT.

## Validation

Keep the prior 67 byte-pair fixtures and all strict gates.
CI uses the source bundle builder for a separate CLI positive
and negative check, and compares all 53 previous expected-CNF
files with the independent token encoder. Marker:
F034_WIRE_ROUNDTRIP_OK expected=53. New results await CI.
No local Lean, external DIMACS correspondence, full proof
encoder theorem, machine-cost bound or independent review.
No main change; inherited PR trigger policy unchanged.
Next: universal proof-envelope token encoder theorem and
converse grammar proof, then independently sourced DIMACS
input conversion and proof-certificate interchange.
