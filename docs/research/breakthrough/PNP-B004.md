# An exponential CNF projection barrier on contradictory parity chains

**MathOS PNP-B004 | Breakthrough cycle 4 | 24 November 2026 | Unreviewed technical note**

## Abstract

A family of unsatisfiable formulas with clauses of width at most three and a linear number of clauses forces a specified Davis–Putnam variable-elimination order to materialize exponentially many clauses. A parity-aware representation, by contrast, gives an immediate algebraic contradiction. This exposes a precise representation barrier for the P=NP algorithm route, not an unrestricted SAT lower bound.

## 1. Target and fixed algorithm

Registered claim PNP.sat_runtime, route PNP.equality. The algorithm maintains an explicit CNF. To eliminate a variable v it retains unaffected clauses and replaces clauses containing v or its negation by all non-tautological resolvents, removes duplicates, and may remove syntactically subsumed clauses. The fixed order first eliminates the auxiliaries of one chain, before eliminating any input or second-chain auxiliary. It does not run an XOR solver or arbitrary semantic simplification. Complexity is measured in total bit length, including intermediate representations.

## 2. Infinite family

For n≥3, use common Boolean inputs x₁,…,xₙ. Introduce n−2 fresh first-chain auxiliaries y₂,…,y_(n−1) and impose

y₂=x₁⊕x₂; y_j=y_(j−1)⊕x_j (3≤j≤n−1); y_(n−1)⊕xₙ=0.

A second chain with disjoint auxiliaries z₂,…,z_(n−1) has the same equations except its final parity is 1. Encode each three-variable XOR relation as the four clauses excluding its forbidden assignments; each final two-variable XOR uses two clauses. The combined formula has 3n−4 variables and 8n−12 clauses, with input encoding length O(n log n) under binary variable labels. Summing all the XOR equations in both chains over GF(2) cancels every variable, leaving 0=1. This is an explicit linear-size algebraic refutation using n-dependent but O(n) row additions; it is not a claim about arbitrary CNF.

## 3. Exact lower bound for the specified representation

Resolving all opposite occurrences when eliminating v is equivalent to existentially quantifying v: an assignment to the other variables extends to at least one value of v precisely when it satisfies the resolvents and unaffected clauses. Since the second chain has no first-chain auxiliary, it remains unchanged during elimination of y₂,…,y_(n−1). Every resolvent involving a first-chain auxiliary comes from the first chain. Its projection onto the input variables is exactly even parity.

Any non-tautological clause implied by even parity must involve all n inputs. Otherwise, after assigning the literals of that clause false, one unused input can be chosen to make the overall parity even, violating the clause on a satisfying input. A full-width non-tautological clause excludes exactly one assignment. There are 2^(n−1) odd-parity assignments, so every equivalent auxiliary-free CNF of even parity needs at least 2^(n−1) full-width clauses. This lower bound is attained by the clauses excluding each odd assignment.

At the end of first-chain elimination none of those clauses can be removed by syntactic subsumption from the second chain, since every second-chain clause contains a second-chain auxiliary. During the fixed order, the first-chain clauses may be shortened only through valid resolution and subsumption; no second-chain clause can subsume one of them. No empty clause is produced by resolving first-chain variables, because that chain by itself is satisfiable. Therefore even duplicate removal and syntactic subsumption cannot prevent the exponential intermediate representation.

The number of literal occurrences is at least n·2^(n−1), and hence the explicit representation needs Ω(n·2^n) bits even if a literal uses only one bit. With binary variable labels the cost is higher. This is superpolynomial in the original O(n log n) input length.

## 4. Executed evidence

The Python replay implements the actual variable elimination, not merely the closed-form count. For n=3 through 12 it compares the projected clause set exactly against all forbidden parity assignments and checks that the second chain is untouched. At n=12, 84 input clauses expand to 2,048 input-only clauses containing 24,576 literal occurrences, plus the untouched second chain. Ten sizes passed. The infinite-family result is justified by the proof above, not by extrapolation.

## 5. Boundary and next proof obligation

This is a counterexample to polynomial worst-case complexity for the fixed-order, explicit-CNF elimination strategy. It does not establish P≠NP, an exponential lower bound for every resolution refutation, or a lower bound for other elimination orders or algorithms. In particular GF(2) reasoning avoids this constructed blowup. The next investigation will test an explicitly defined hybrid XOR and CNF solver and determine which mixed constraints force a representation expansion that its compression cannot avoid. A proof of arbitrary-instance correctness and polynomial total bit complexity remains missing.

## 6. References and reproduction

M. Davis and H. Putnam, A Computing Procedure for Quantification Theory, J. ACM 7 (1960), 201–215, https://doi.org/10.1145/321033.321034 .

Standard parity CNF lower bound and variable elimination: https://algorithm.tamnd.com/boolean-quantifier-elimination/ . The general phenomenon is established prior art; no literature novelty is claimed for this reconstruction and adversarial family.

Pinned source: b4623c70d99ca05363681e709e9dc9191e93fd9d. Executed workflow: https://github.com/tltmgnt/MathOS/actions/runs/45371621490. Evidence: cycle4-evidence.json.

```sh
python -m unittest discover -s tests -p 'test_breakthrough_cycle4.py' -v
python -m mathos.research.breakthrough_cycle4
```

Independent specialist review and formal proof verification are outstanding. PNP.sat_runtime remains open.
