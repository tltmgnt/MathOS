# Certification scope and reproducible audit

This package does not certify any new Millennium Prize proof. Its graph edges
are authored sufficient-route hypotheses; their mathematical sufficiency has
not been formally established. Small blocker counts do not imply proximity to
a solution. The earlier qualitative 1-to-5 ratings were not calibrated measurements.

The repository module adds result-contract records, an output-directory CLI,
four integration tests, and a Python-version CI matrix to the standalone prototype.

## Implemented assurance

- An obligation-set generator with AND/OR dependencies and cycle rejection.
- A separately implemented truth-table checker that validates completion sets
  on every open-leaf assignment for each supplied finite graph.
- Inclusion-minimality checks; missing routes, false empty certificates, and
  unknown assumptions are rejected. Exponential work is capped at 16 open leaves.
- Deterministic cross-checks on 1,000 generated acyclic graphs, with seed 173.
- Mutation tests that reject deliberately incorrect completion sets.
- Content hashes for input graphs, implementation files and results. These
  identify content; they are neither signatures nor correctness proofs.
- Exact integer polynomial expansion checks through m=8, plus the general
  informal SAT monomial-count proof in results.json.

## Exact mathematical statement of the SAT subresult

For every nonnegative integer m, in the polynomial ring over the integers in
2m distinct indeterminates x_1,y_1,...,x_m,y_m, the product
PRODUCT_i (x_i + y_i - x_i*y_i) has exactly 3^m nonzero monomials.

Proof: choose one of the three terms from each factor. The resulting exponent
pattern on the i-th variable pair is respectively (1,0), (0,1), or (1,1).
Consequently distinct choice sequences yield distinct monomials. Each has
coefficient +1 or -1, so no cancellation occurs. There are 3^m choice sequences.
This includes m=0, with empty product 1. This is an informal mathematical proof;
the finite computation is not a formal verification of the universal statement.

This disproves a polynomial bound on explicit expansion size for this route.
It establishes neither a SAT lower bound for arbitrary algorithms nor P != NP.

## Unmet requirements for formal and audited mathematical certification

1. Complete formal statements of the intended Millennium theorems and all bridges.
2. Proof objects covering every dependency, with axioms and imports enumerated.
3. Successful replay in a specified proof-assistant kernel without unproved gaps.
4. Independent mathematical assessment that the formal statements match the
   intended problems; formal checking alone does not establish that correspondence.
5. Independent audit of proof coverage, provenance and trusted components.

No Lean, Coq, Isabelle, or Z3 executable was found on PATH in this run. No proof
assistant check or external audit is claimed. A second local implementation is
a software cross-check, not an independent external audit.

## Reproduction

Python 3.10+; standard library only. Run from the MathOS repository root:

```sh
python -m unittest discover -s tests -p "test_proof_*.py" -v
python -m mathos.proof_analysis --run-tests --output-dir artifacts/proof-analysis
```

Inspect certification_audit.json for separate gates. Any unmet mathematical gate
keeps overall certification at NOT_CERTIFIED. The exhaustive checker validates
the Boolean abstraction only; it does not parse or establish mathematical truth.
