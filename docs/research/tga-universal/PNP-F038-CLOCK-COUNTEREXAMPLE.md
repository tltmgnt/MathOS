# F038 — Bounded clock counterexample compiler

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not a Lean declaration.
Verified base d534a2fbf638993d38b4803f5fb39d2357ea7fb1: https://github.com/tltmgnt/MathOS/actions/runs/45705736723 (success).

## Exact bounded-counterexample reduction

Fix a deterministic explicit-input witness search machine U, with acceptance only after verification of a satisfying assignment, as in the previous universal clock note. Fix a standard CNF encoding in which syntactic validity and assignment verification are polynomial-time and the number of distinct variables is at most polynomial in the bit length. For integers N,T>=1, construct a Boolean circuit on N formula bits f and polynomially many witness bits w, computing

ValidCNF(f) AND Satisfies(f,w) AND NOT AcceptBy(U,f,T).

AcceptBy is deterministic bounded computation, with acceptance made absorbing. It can be compiled uniformly by unrolling the transition relation for T steps on the O(N+T) reachable tape cells of a fixed single-tape machine. One-hot state/head markers and local updates give a polynomial-size circuit (O(T(N+T)) for a fixed local encoding, plus input/output handling). Alternative machine models can first be fixed with their simulation overhead charged. A standard circuit gate encoding, using private extension variables and asserting the output, yields a width-at-most-three CNF K_U(N,T) of size polynomial in N+T, constructible in that time from unary N,T. Tseitin equivalences enforce gate values in both directions; the projected relation on f,w is exact.

K_U(N,T) is satisfiable iff there exists a satisfiable length-N CNF not accepted by U within T actual machine steps. A satisfying assignment provides both the missed input and an independently checkable satisfying witness. UNSAT is exactly the absence of such a counterexample at that length and deadline. Syntax validation avoids falsely counting arbitrary bit strings; verification of the source witness avoids treating genuinely unsatisfiable formulas as missed deadlines. This is a bounded statement, not a test of eventual termination. The compiler is independent of any restricted SAT proof system.

With unary N,T, bounded-counterexample existence is in NP. With binary T, the polynomial bound is in its VALUE, not its encoded length; no NP claim is made for that succinct formulation.

## Unrestricted clock obligation

For the fixed universal U from the preceding note,

P=NP iff exists integer k>=1, N0>=1 such that for every N>=N0, K_U(N,(N+1)^k) is UNSAT.

Indeed the absence of a counterexample is precisely the uniform polynomial clock bound on satisfiable inputs, and finite shorter inputs do not affect polynomial-time decidability. For each fixed k the circuit compiler is polynomial in N, but its polynomial exponent depends on k and on the simulation encoding. If P!=NP, for every fixed k the sequence contains satisfiable formulas at arbitrarily large N. Conversely, proving eventual UNSAT for a single fixed k would resolve P=NP. No finite prefix of UNSAT checks establishes this universal quantifier without an additional proved invariant.

Running U on the generated counterexample formula does not produce a contradiction to the clock bound being tested. Its input length is the length of K, not N; its time bound is measured against that enlarged length. Nor does failure to find a witness establish UNSAT of K. These two distinctions prevent a circular proof from bounded simulation or from applying the hypothesized clock to its own counterexample compiler.

## Candidate-specific clock certification can be NP-hard even on unit inputs

This separate result concerns a fixed, deliberately constructed correct witness solver A, not the specific universal U above. Use a polynomial-time decodable unit-CNF template: each distinct variable has exactly one unit clause pinning one bit of a self-delimiting encoded pair (D,x), with D a 3-CNF and x an assignment to its declared variables. All formulas in the template are satisfiable and have an immediate witness. For a fixed D, the template fixes the D-bit signs and leaves the x-bit signs free; use fixed-width variable identifiers or a length convention in which sign changes do not alter bit length.

A parses the template, evaluates D(x), and constructs the pinned witness. If D(x) is false it outputs immediately. If D(x) is true it first performs a deterministic delay exceeding a fixed polynomial deadline T(N), then outputs the very same valid witness. A polynomial T can be chosen to bound the fast path on all valid template inputs, since parsing, evaluation and output are polynomial-time. Implement the delay by a counter of T(N)+1 increments, with each increment taking at least one machine step; this is still polynomial-time. A can handle other inputs by a complete exhaustive algorithm, but no polynomial bound there is asserted. It is a correct polynomial-time witness solver on the template domain.

Given D, generate its partially pinned template and the unary deadline T(N) in polynomial time. A missed satisfiable formula exists in that template iff some x satisfies D. This proves NP-completeness of bounded missed-deadline existence for this fixed A with supplied partial unit template and unary clock (membership by guessing the remaining signs and simulating A). The result is not a lower bound for finding a witness, nor an NP-hardness claim for the specific fixed universal U. It establishes that even when witness construction is easy, finding a counterexample to a candidate runtime assertion can encode arbitrary SAT.

## Finite audit

Use the previous toy stage scheduler as a transparent bounded-computation fixture, not as an implementation of U. For a twelve-row template with presence bits p_i and three witness bits w, require (not p_i OR C_i(w)) for each template clause. For every valid candidate a returned by some simulated program within stage s, add a clause OR_{i:C_i(a)=false} p_i. An empty such clause means a is valid for every template formula and no missed input exists. This direct encoding is exact: the first group certifies satisfiability and the second excludes every early candidate. Stages restart with increasing budgets; the sets of returning valid-format candidates are nested. The resulting formula may contain long clauses; the general width-three circuit reduction above is separate.

Exhaust all 4096 presence masks and eight stages, all eight source assignments, and compare the compiler's projected relation with the independently evaluated stage. Expected: 32768 pinned cases, 7844 missed satisfiable deadlines, 24924 nonmisses, 19 distinct-per-stage candidate counts summed, 262144 witness checks, 115 clauses summed across stages, maximum 15 variables and 20 clauses. Counterexample counts by stage: 1360,1360,1360,1232,984,924,624,0. Repository additionally checks each pinned formula with the finite SAT oracle and extracts concrete missed-input witnesses.

A second finite fixture uses 15 unit pins encoding the template source mask and three-bit assignment. Compare the simulated delayed-path predicate with direct source satisfiability. Expected: 4096 source formulas, 32768 parameter cases, 2304 delayed paths, 1360 source formulas admitting a delayed path, 491520 unit checks. This tests the reduction's logical condition, not actual machine-step timing.

Next: a proved inductive or amortized invariant across lengths that discharges the eventual UNSAT obligation, or a genuine unrestricted lower bound. No such invariant is supplied here; no new Lean declaration or P versus NP resolution.
