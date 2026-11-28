# MathOS P vs NP outcome engine v2 — scoped research implementation

This additive research module implements the first executable slice of the reverse-engineered specification. The repository's existing MathOS core is a package, not the standalone mathos.py described by the audit. Existing interfaces, formal results and PNP overlap research are unchanged. P versus NP remains open.

## Run

From the repository root (Python 3.11+, standard library only):

    python -m mathos.research.pnp_outcome_engine --objective E12 --checkpoint artifacts/pnp.json
    python -m mathos.research.pnp_outcome_engine --objective E06 --input cnf.json --c 1
    python -m mathos.research.pnp_outcome_engine --resume artifacts/pnp.json --seconds 30
    python -m unittest discover -s tests -p 'test_pnp_outcome_engine.py' -v

Input JSON: {"n":3,"clauses":[[1,-2],[2,3],[-3]]}. Empty conjunction is true; empty clause is false. Literal zero, out-of-range indices and booleans are rejected. E12 runs the exact built-in duplication counterexample, independent of input.

## Architecture and acceptance

The outcome registry records E01–E20, their responsible agent roles and acceptance conditions. Backward decomposition expands O01–O12 in dependency order. The forward engine normalizes, measures, replays certificates, chooses an exact solver, and independently cross-checks small decisions by exhaustive search. It records resource exhaustion, diagnostic mismatches, finite limitations or unresolved obligations. Only E12 currently has an objective-specific acceptance route. Other objectives are explicitly unresolved; their labels do not imply agents exist. No AI or external verifier result is accepted as a theorem. The existing Lean graph bridge checks Boolean graph entailment, not arbitrary mathematical labels.

## Mathematical contract

Normalization removes duplicate literals/clauses, tautologies and unused declared variables, with dense variable mapping. A satisfying assignment can be lifted by mapping active variables back and assigning unused variables arbitrarily. Removing syntactic redundancy is truth-preserving under this projection; it does not canonicalize arbitrary equivalence, subsumption or renaming.

The primal graph forgets signs; signed incidence retains them. Graph Betti numbers are beta0 = components and beta1 = edges - vertices + components. Euler characteristic is vertices - edges. Higher homology and spectral criteria are not implemented.

For raw and normalized encodings, N = max(2,n+m+literal occurrences); gap = certified induced width - floor(c log2 N). The integer threshold is computed exactly as bit_length(N**c)-1. c is a fixed integer 1..16, not fitted to each instance. Minimum degree and minimum fill heuristics produce replayed upper bounds on treewidth; neither establishes optimality. Duplicating all 28 positive pair clauses on 8 variables changes N from 92 to 176, width stays 7, and gap changes from +1 to 0 at c=1. Normalized metrics coincide. The raw gap remains a valid sufficient encoding-dependent condition, not a semantic hardness invariant.

The portfolio recognizes 2-CNF, Horn CNF and certified logarithmic width. Exact 2-SAT uses implication reachability, Horn SAT uses least-model closure, and general CNF uses Boolean factor elimination with a certified ordering. Eliminating a variable existentially quantifies the conjunction of its incident factors, preserving satisfiability. At width w, the largest bucket has at most w+1 variables, giving a 2^O(w) factor with polynomial overhead. The engine may attempt elimination outside the sufficient criterion under a budget; exhaustion is not UNSAT, a lower bound on all algorithms, or evidence of P != NP. Graph analysis and explicit replay are polynomial but may themselves hit the research budget. The implementation is a decision engine, not a witness/proof-producing SAT solver.

## Resource policy

Cooperative wall-clock and work-step budgets, input dimension caps (512 variables, 20k clauses, 100k occurrences), and live Boolean factor cell limits are enforced. These are not hard RSS/OS limits. Python operations between checks can overrun a deadline. CLI JSON input is limited to 2 MB. A checkpoint atomically stores input, plan, partial completed stage evidence and outcome; resume restarts from input with a fresh budget rather than resuming an interrupted factor table. Invalid input or filesystem errors fail explicitly. A resource-exhausted result may include a previously completed decision, but never fabricates one.

## Roadmap and boundaries

- P0: normalization, explicit obligations, cooperative budgets/checkpoints implemented; formal proofs of implementation and hard process isolation still open.
- P1: signed incidence, two ordering strategies, 2-SAT and Horn portfolio implemented.
- P2: spectral/higher homology and counterexample minimization remain research work; the existing finite counterexample is not a statistical study.
- P3: independent formal proof construction and checking of the actual CNF implementation, proof obligation closure, automated lemma decomposition remain open.
- P4: universal transformation and algorithm-independent obstruction remain unsolved. No conditional or unconditional separation/equality claimed.

The constructive pathway requires a polynomial-time, polynomial-output, SAT-preserving transformation with efficiently certified logarithmic induced width for all inputs. The separation pathway requires ruling out every deterministic polynomial-time SAT algorithm, not just elimination. Failure to find counterexamples cannot discharge either proof pathway.
