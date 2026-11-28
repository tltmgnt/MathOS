# MathOS v18 integration candidate — release admission evidence

2026-11-28. This is a research candidate; no universal decision or complexity claim. PR #280 (baseline audit only) was observed merged at the start of this continuation; the integration is staged separately on main snapshot 6d6eb6bd2efea00a225f9802b60cce8787ca759a. No merge performed by this continuation.

## Upstream verified results

Adaptive v16 original commit 229bf872e243bf41b05962810b064d2454fce7a7 passed run https://github.com/tltmgnt/MathOS/actions/runs/46132714203. The v17 branch's final formal repair 873e6df6c451ae0ee5adb80dc3c3c5968b35729c passed both evidence and formal jobs in https://github.com/tltmgnt/MathOS/actions/runs/46133376858, with adaptive regression rerun https://github.com/tltmgnt/MathOS/actions/runs/46133376947. Both adaptive and library are now on main. The v17 workflow now includes a separate report audit; this supersedes the initial static audit's missing-audit observation. Lean logs show both adaptive abstract theorems and all six library abstract theorems are axiom-free. They do not prove the Python implementation.

Adaptive regression gate passed. Original development: v12 18/24, v14 15/24, v16 24/24. Prior unresolved: 0/2, 2/2, 2/2. Fresh public seed 16028: v12 15/24, v14 16/24, v16 24/24; v16 16 SAT, 8 UNSAT, zero unknown. All 50 v16 decisions were from the first search route alone. This is a significant diagnostic: no evidence yet that later routes caused this gain. Heldout reported steps 1,310,246 / 988,095 / 57,030; counters are implementation-specific.

v17 public seed 17003: 8/10 reference UNSAT certified (2/4 random3, 6/6 random2); 8/32 overall, versus v15 0/32. 3 of 8 positive cases used multiple transfers. Discovery 2/3 UNSAT; retrospective 0/5. 30 retained fragments, 14 heldout transfer limits, 10 not found. Expanded library plus algorithm changes confound attribution; this is not a complete decision solver. Work 3,313,885 vs old 8,416 steps across heldout; new retrieval is far more expensive in these counters, so do not run it blindly before inexpensive constructive search.

## Independent execution on downloaded release artifacts

Actual ZIP bytes downloaded and SHA-256 checked against GitHub metadata:
- adaptive artifact 15258388176, 344780 bytes, 08d5be130c94bd9b9f032ebf57067ea6b329fdf6372ff9ea8c2b05c13e829bf1;
- library artifact 15257734225, 180925 bytes, 91296051843d486f424d872e677658de16ca86117fb083768f7a27c49e4986d2.

Independent standard-library-only Python checker executed locally; no MathOS imports. ZIP CRC and canonical upstream artifact hashes matched. All 50 adaptive references recomputed by truth table; 34 SAT assignments and 16 complete UNSAT trees replayed, 548 tree nodes. All 64 library evaluation references recomputed; 45 retained/original fragments independently checked by reverse unit propagation. All ten credited v17 transfers (2 discovery, 8 heldout) checked signed injections and guards, rebuilt flattened proofs and replayed 427 explicit additions against original formulas. Three negative controls rejected (unjustified leaf, non-RUP empty clause, missing guard). Separate baseline probe reran with unchanged 512 formulas and zero false positives. No discrepancies. This independent checker did not replay the v12/v14 baseline certificates or reconstruct training provenance from upstream source; the upstream audit did the latter for v17. Work/timing/unknown search traces are not authenticated by these positive replays.

## Candidate staged

Small active support (<=16) attempts adaptive search/portfolio first with 75% of available cooperative allowance; larger inputs try library first with 25%. Remaining allowance is handed to the other route. The final result is checked against the original CNF with route-specific replay. Library frozen by digest; no retrieval miss means SAT. An exhausted proof earns no credit. This split is a chosen heuristic, not a guaranteed improvement.

Offline abstraction converts a verified UNSAT split tree to guarded RUP blockers: each leaf falsifies an original clause under its path; the two child blockers force conflicting pivot assignments under the parent path. Postorder ends at empty. Replay guards and source before admission, cap support/steps, content-address duplicate rejection. A new snapshot is returned separately; evaluation never calls admission. Abstract Lean lemmas check the implication argument, not implementation refinement.

The development experiment compares seven arms under the same process wall timeout, one core affinity, 512 MiB address-space limit, five cooperative seconds and 100000 reported steps. Offline training/build excluded. v15 is operationalized as old-template retrieval plus v12 fallback; v17 as new library retrieval plus v12 fallback. v18-no-retrieval ablates retrieval. Includes new public seed random2/random3 and six analytic chain twins; this is explicitly not a blind independent holdout or external benchmark. All references checked separately, every credited route replayed, complete manifest and summary audited, JSON artifacts hashed. Reported work excludes some legacy replay and bookkeeping; hard process envelope rather than counter units provides common upper resource boundary. Address-space cap is not RSS; RSS is measured separately. Work and time observations are not authenticated by proof replay.

## Obligation updates

- V18-05: release admission positive certificates verified independently for actual v16/v17 artifact outputs, as scoped above. Full code-to-semantics and provenance replication not discharged.
- V18-06: integration candidate implemented, improvement conjecture unresolved; no v18 result asserted before execution.
- V18-07: new code, tests, and Lean staged; end-to-end refinement remains unresolved. New CI must pass, then inspect downloaded artifacts and real failures. Public seeded suites are not blinded evidence.
- V18-08: offline tree blocker construction proved at abstract level by the paper argument; new Lean checks pending; no novel theorem claim.
- P versus NP unresolved. Do not merge until actual candidate CI, replay, review and independent held-out evaluation satisfy the original gate. Do not relax upstream gates, or tune on held-out evidence.
