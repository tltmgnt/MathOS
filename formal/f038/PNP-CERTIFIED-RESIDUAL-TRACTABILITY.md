# Certified residual tractability — FV-11 follow-on

Status: research only; PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## Implemented conditional theorem (mathematical argument, not Lean formalization)

Encode arbitrary 3-CNF as Boolean tables with at most three coordinates and at most eight allowed tuples (seven for an ordinary distinct-literal clause). Renumber occurring identifiers, retain empty clauses, and directly validate the returned original assignment. The encoded size measure N is 1 + k + sum over factors of (1 + arity + row count * (arity + 1)); k denotes explicitly represented variables. It is polynomial in the source representation.

First run the actual FV-11 D7A semijoin producer and independent exact replay checker. Accepted deletion logs preserve the entire model set. Then choose a minimum-current-neighborhood variable deterministically, with ties by coordinate index. Join all its incident tables and existentially project that variable. The new factor over the remaining incident coordinates is true exactly when at least one bit extension satisfies every old incident table. Factors outside the bucket are unchanged. Therefore this step preserves satisfiability by existential quantification, and reversing the sequence reconstructs a witness. Empty table implies UNSAT; eliminating all variables without an empty table implies SAT. The separate checker independently reconstructs each projected table using both bit extensions and direct row matching; it also checks the original SAT witness. This is an executable certificate checker, not a new Lean theorem.

The fixed policy permits neighborhood width w <= floor(log2 N). Each bucket examines at most 2^(w+1) <= 2N candidate assignments, with at most k buckets and at most O(N) active factors (one new factor per step). Generated tables and replay certificates therefore have polynomial size. Pairwise semijoin closure deletes at most O(N) rows, with polynomially many bounded-arity pair comparisons; deterministic selection, joins, independent replay, certificate size and reconstruction all have polynomial abstract operation/bit bounds in explicit input length. The table-candidate counter charges only producer enumeration, not wall time or total instructions; its default 1,000,000 cap can refuse earlier. No exponential fallback. UNKNOWN is not a SAT/UNSAT certificate and proves neither hardness nor failure of every elimination order.

**Sufficient route to P=NP:** a universal polynomial-time, polynomial-size, satisfiability-preserving reduction of every 3-SAT input to a certified terminal result or a residual with a polynomially discoverable logarithmic-width elimination order (and compatible resource policy) would yield polynomial-time SAT. This implementation does not establish that universal reduction or order discovery. Min-neighborhood selection can refuse even when another order succeeds. The wider connected SAT control is deliberately returned UNKNOWN; it refutes a universal claim about this specific policy, not P=NP or P!=NP. The logarithmic width criterion is a different sufficient condition from logarithmically many total free variables; it handles arbitrarily long low-width chains.

## Executed audit (connector JS, actual inherited modules)

```json
{
  "small": 512,
  "sat": 138,
  "unsat": 374,
  "unknown": 2,
  "tamperRejected": 6,
  "structured": [
    {
      "name": "empty formula",
      "k": 0,
      "status": "SAT",
      "reason": null,
      "rows": 0,
      "width": 0,
      "eliminated": 0
    },
    {
      "name": "empty clause",
      "k": 0,
      "status": "UNSAT",
      "reason": null,
      "rows": 0,
      "width": 0,
      "eliminated": 0
    },
    {
      "name": "large literal IDs",
      "k": 1,
      "status": "UNSAT",
      "reason": null,
      "rows": 0,
      "width": 0,
      "eliminated": 0
    },
    {
      "name": "tautology and repeated literal",
      "k": 2,
      "status": "SAT",
      "reason": null,
      "rows": 4,
      "width": 0,
      "eliminated": 2
    },
    {
      "name": "odd cycle",
      "k": 101,
      "status": "UNSAT",
      "reason": null,
      "rows": 796,
      "width": 2,
      "eliminated": 100
    },
    {
      "name": "long chain",
      "k": 512,
      "status": "SAT",
      "reason": null,
      "rows": 2046,
      "width": 1,
      "eliminated": 512
    },
    {
      "name": "disjoint blocks",
      "k": 512,
      "status": "SAT",
      "reason": null,
      "rows": 1536,
      "width": 1,
      "eliminated": 512
    },
    {
      "name": "connected wide obstruction",
      "k": 32,
      "status": "UNKNOWN",
      "reason": "width",
      "rows": 0,
      "width": 0,
      "eliminated": 0
    }
  ]
}
```

Run `node mathos/research/pnp_certified_residual_audit.js` to reproduce. No full general SAT theorem, new Lean proof, independent human review, physical compiler/resource accounting, production integration, or promotion is claimed. Established variable/bucket elimination is used as a reference tractable mechanism, not a novelty claim.
