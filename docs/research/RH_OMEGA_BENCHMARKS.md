# RH-Ω software benchmarks and acceptance protocol

Run:

    python -m unittest discover -s tests -p 'test_rh_omega.py' -v
    python scripts/rh_omega_benchmark.py --repetitions 2 --output artifacts/rh-omega/benchmark.json

The benchmark checks eight stage outputs, ten role records, identical
packet hashes across repeated runs, the open canonical G1-G6 plus G5P
firewall, correct finite/uncertified scopes and no proof-registry writes.
It records minimum, median and maximum runtime for environment-specific
regression checks, not mathematical performance superiority.

GitHub Actions independently compiles existing Lean RHTransferLogic.lean
and Coq RHOmegaFinitePrefix.v. These establish limited **logical**
statements and do not formally prove a theorem about actual zeta zeros.

| Proposal metric | Present benchmark | Limitation |
|---|---|---|
| Mathematical correctness | Exact synthetic arithmetic and scoped code-contract checks | Not full analytical correctness |
| Theorem reconstruction | Existing literature-aligned source pointers | Complete mathematical reconstruction open |
| Proof completeness | G1-G6 and G5P remain unresolved | No RH theorem discharged |
| Counterexample detection | Four explicit unjustified-inference controls | Not independently calibrated detection |
| Formal verification | Lean/Coq bounded logical kernel checks | No RH formalization |
| Reproducibility | Same-CI-environment fingerprints and runtime | Not independent external replication |
| Novelty | No automatic novelty score or certificate | Not established |

A green action is a software result. The source PDF's principle remains:
discovery, verification and proof are three different categories.
