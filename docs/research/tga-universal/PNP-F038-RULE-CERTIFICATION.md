# F038 — Quantifier barrier for global selector-rule certification

PNP_RESOLUTION_STATUS = OPEN. Scoped derivation, not a Lean declaration.
Verified base b321dde8811dc812ecbb5f3e7c0fc6ba1e430063: https://github.com/tltmgnt/MathOS/actions/runs/45700994492 (success).

## Certification problem

An input consists of a Boolean circuit C mapping a polynomial number of parameter bits x to a 3-CNF presence vector in an explicitly declared polynomial-size variable universe, and a total Boolean circuit A mapping that presence vector to a selector bit. Decide whether for every x, whenever F_x=C(x) is satisfiable, F_x restricted to z=A(C(x)) is satisfiable. This is checking a supplied rule over a supplied succinct family, not the existence of a universal efficient selector. Equivalently, for every x and assignment w there exists an assignment v such that
not F_x(w) OR (F_x(v) AND v_z=A(C(x))).
The predicate is polynomial-time, hence the problem lies in Pi_2^P. All input lengths and universe sizes are explicit or polynomially bounded by the input description.

## Hardness, even with a constant rule and always-satisfiable formulas

Reduce the standard Pi_2^P-complete problem forall x exists y R(x,y), where R is width-at-most-three CNF. See Arora and Barak, Computational Complexity: A Modern Approach, chapter 5, https://theory.cs.princeton.edu/complexity/phchap.pdf ; and the restricted quantified 3-SAT result https://arxiv.org/abs/1908.05361.

Introduce fresh z, form (z OR c) for every clause c of R, and split each width-four guarded clause (z OR l1 OR l2 OR l3) into (z OR l1 OR u) AND (not u OR l2 OR l3) with a private fresh u. The split is existentially equivalent to the original clause: if the first two literals are both false then u must be true, requiring a remaining literal; otherwise u=false works. Empty/short clauses are allowed. Append unit pins for the x bits. These pins are the only nonconstant coordinates of a public clause-presence template (normalization of fixed clauses does not affect satisfiability); each pair of signed pin slots is locally determined by a source bit. The family generator is polynomial-time and has linear gate/guard overhead in the matrix's explicit size, apart from any chosen universal presence-vector padding.

For each x, branch 1 is satisfiable independently of R (take all private u=false); branch 0 is satisfiable iff exists y R(x,y). The constant selector A=0 is safe on all family members iff forall x exists y R(x,y). Therefore certification is Pi_2^P-complete even with constant A and a family whose every input is satisfiable. This does not prove that verifying a circuit on the *entire* universal CNF domain is Pi_2^P-hard, since the family generator is part of this problem's input.

Counterexample existence is Sigma_2^P-complete; an x by itself does not generically certify that the selected branch is unsatisfiable. In particular a deterministic polynomial-time certification decision algorithm would imply P=NP. A sound and complete polynomial-time verifier with polynomial-length certificates for every correct family-rule pair would imply Pi_2^P subseteq NP, hence NP=coNP and PH=NP. These are conditional consequences, not unconditional impossibility results.

## Constructive sufficient invariant

A supplied witness-repair circuit W(x,w) that satisfies the implication above gives a concrete constructive certificate of safety (a witness transformer). Checking the implication for all x,w is in coNP: a violating pair is an efficiently checkable counterexample. For the guarded family and constant zero, a Skolem circuit Y(x) satisfying R(x,Y(x)) for every x is sufficient: use Y(x), the x pins, z=0, and choose each private u from its clause's first literals (u=true precisely when z OR l1 is false). Conversely any repair circuit for this family yields a Skolem circuit by feeding the canonical branch-one witness (x pins, zero y and u, z=1) and extracting y. Thus polynomial-size repair circuits are equivalent, up to polynomial overhead, to polynomial-size Skolem circuits for this family, not implied by the mere existence of an arbitrary truth-table repair. A truth table always exists for a true quantified sentence, but can be exponential in the number of universal bits.

A uniform polynomial-time procedure that always produces such a repair circuit on every true quantified instance of this family would solve SAT in polynomial time if its runtime is bounded on all inputs: use no universal bits (or one unused bit), generate the circuit and evaluate it at zero, then verify the resulting assignment against R. On false instances no assignment can pass. This is a constructive-route obligation, not a new SAT algorithm. Checking a given repair is a different problem from synthesizing one, and a certificate checked by a coNP oracle is not an NP certificate.

## Finite regression

Exhaust 4096 subsets of a fixed mixed-width three-variable matrix family; use both splits of one and two universal bits. For every parameter assignment compare the two guarded CNF branches via the existing exact finite SAT oracle against direct matrix evaluation; enumerate every candidate Skolem truth table and compare existence to constant-rule safety. Expected: 8192 family/split pairs, 356 safe, 7836 unsafe, 24576 instances, 49152 branch checks, 20912 unsafe instance outputs, 131072 candidate truth tables, 356 families with a repair, max 8 variables and 18 clauses. Finite enumeration is validation only; the asymptotic completeness proof is the reduction.

Next: investigate efficient witness transformers on a specified nontrivial structural domain and test whether their composition preserves polynomial size and covers the universal domain. A universal coverage proof, rather than a finite certification rate, is essential. No new Lean declaration or P versus NP resolution.
