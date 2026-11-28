# MathOS v11 — reproducible evidence benchmark

This is a finite evidence audit of the existing v10 portfolio, not a new
algorithm or a complexity separation. Default manifest: 11 structured
controls and 24 seeded random formulas split into development and holdout
groups. Every case has at most ten active variables; independent exhaustive
truth evaluation supplies the reference decision. No planted label is used
as ground truth.

## Run

    python -m mathos.research.pnp_evidence_benchmark --checkpoint artifacts/pnp-v11.json
    python -m mathos.research.pnp_evidence_benchmark --audit artifacts/pnp-v11.json
    python -m unittest discover -s tests -p 'test_pnp_evidence_benchmark.py' -v

Every one of the 14 default plans is run separately on each input with
the same work-step quota, time limit and logical cell cap. The report
stores exact input, manifest SHA-256, configuration, reference decision,
proof, search work, elapsed nanoseconds, replay work and status. A fresh
budget independently replays every plan's evidence. Results with no
certificate remain unknown. Exhausted and unrecognized plans are distinct.
The reported portfolio union counts cases decided by at least one plan
in these isolated runs; it is NOT an end-to-end timed v10 portfolio run.
Search timings include the plan's internal replay but not the external
audit. Timings are machine-dependent and not certified. Work steps are
implementation-specific proxies and not machine-independent complexity.

Per-plan totals include SAT, UNSAT, unknown, exhausted, unique decisions,
coverage with that plan omitted, work, external replay steps and compact
JSON certificate bytes (including partial unknown trees when present).
Unique contribution is observed on this manifest at these quotas; it is
not a proof that a route is necessary in general. The holdout labels
denote a separate deterministic seed, not a blind secret test set;
the suite is intentionally small and does not represent SAT distributions.
No performance superiority or generalization claim is inferred.

The audit reconstructs the manifest and reference decisions, validates
the fixed plan sequence and per-plan configuration, replays all credited
proofs, checks replay work and recomputes aggregate counts. It does not
authenticate observed wall time or search work; rerun the benchmark to
measure these independently. It permits partial prefixes only when
explicitly marked incomplete. It rejects a modified reference, omitted
case on a complete report, unsupported universal claim or inconsistent
aggregate. Exact equality of observed time across runs is not expected.
Checkpoint writes are atomic per completed case; restart is a fresh run.

No Lean changes are required because this is an empirical measurement
layer on the existing proof routes. The underlying proofs remain scoped.
O10/O11/O12 and P versus NP remain unresolved.
