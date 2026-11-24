# An exact exponential projection barrier for mixed CNF and XOR constraints

**MathOS PNP-B005 | Breakthrough cycle 5 | 24 November 2026 | Unreviewed technical note**

## 1. Target and theorem

Registered target PNP.sat_runtime. Cycle 4 established an exponential projection barrier for explicit CNF on parity chains; pure parity could be retained cheaply as a single XOR row. Here we test the stronger hybrid representation consisting of a conjunction of explicit clauses and affine GF(2) equations.

For n≥2 let a_i,b_i,y_i be Boolean variables. Define y_i=a_i AND b_i for every i and impose Σ_i y_i=0 over GF(2). Each AND gate has three CNF clauses (¬y_i∨a_i), (¬y_i∨b_i), (y_i∨¬a_i∨¬b_i), and the parity equation is one row. The representation has O(n log n) input bits under standard binary labels. The projected relation R on the 2n visible input bits accepts precisely when an even number of pairs equal 11.

**Theorem.** Every exact representation of R as a conjunction of explicit clauses and affine GF(2) equations using only the visible variables has at least (3^n−1)/2 clauses. This bound is attained. No extra variables, branching representation, arbitrary nonlinear constraints, or circuit representation are permitted in the target model.

## 2. Why affine compression cannot help

R contains the all-zero vector and each of the 2n coordinate unit vectors: none of these inputs contains a pair equal to 11. If an affine equation is satisfied by every member of R, evaluating at zero gives its right-hand side zero, and evaluating at each unit vector makes each coefficient zero. Consequently any affine equation valid on R is a tautology. In any conjunctive hybrid representation of R, every individual equation must hold on R, so all such equations are redundant.

## 3. Exact CNF lower bound

A non-tautological clause is falsified on a nonempty subcube of visible assignments, determined by fixing its literals false. If the clause is valid on R, every assignment in that cube must have odd AND parity. Each pair's AND output must therefore be fixed throughout the cube: otherwise, because the cube fixes coordinates independently, changing only that pair could switch parity while staying within the cube.

To force a pair output to one requires fixing both bits to one; to force it to zero requires at least one bit fixed to zero. The maximal subcubes contained in the rejected set are thus exactly those that fix both bits to one on some odd subset S of the n pairs and fix one chosen coordinate to zero in each pair outside S, leaving its other coordinate free. There are 2^(n−|S|) choices for each S.

Each maximal rejected cube has a private witness: assign 11 to the pairs in S and, outside S, assign its specified zero coordinate to zero and the other coordinate to one. Any other maximal rejected cube containing that witness would need exactly the same active subset S and the same zero choices. Every smaller rejected cube lies inside one of these maximal cubes, so no valid clause can exclude two private witnesses belonging to different maximal cubes. Since a CNF equivalent to R must exclude every private witness, it needs at least one clause per maximal cube. Conversely, one clause excluding each maximal cube suffices.

The exact minimum is therefore

Σ_(k odd) binom(n,k)2^(n−k) = [(2+1)^n−(2−1)^n]/2 = (3^n−1)/2.

Thus any algorithm required to materialize this auxiliary-free conjunction on these inputs has superpolynomial output size and total bit complexity. A compact AND/XOR circuit or the original representation with auxiliary variables avoids this expansion. The theorem is a representation result, not a SAT decision lower bound or P≠NP proof.

## 4. Executed finite controls

The replay constructs the maximal rejected cubes for each n from 2 to 7, explicitly enumerates their assignments, and checks exact agreement with the rejected parity set obtained independently by exhaustive pair-state enumeration. It counts unique witnesses and checks zero and all coordinate unit vectors.

n=2: 4 maximal cubes and private witnesses; 6 rejected assignments.

n=3: 13 maximal cubes and private witnesses; 28 rejected assignments.

n=4: 40 maximal cubes and private witnesses; 120 rejected assignments.

n=5: 121 maximal cubes and private witnesses; 496 rejected assignments.

n=6: 364 maximal cubes and private witnesses; 2016 rejected assignments.

n=7: 1093 maximal cubes and private witnesses; 8128 rejected assignments.

The general lower bound follows from the analytical argument, not extrapolation from these six cases.

## 5. Next proof obligation

Exact auxiliary-free projection is now ruled out as a universal efficient CNF+XOR representation strategy. The next attempt should retain nonlinear gate structure or auxiliary variables and specify a decision procedure, proving correctness and accounting for actual branch complexity and intermediate bit lengths. The present result places no lower bound on such a procedure. PNP.sat_runtime remains open.

## References and reproducibility

MathOS PNP-B004, previous parity-chain projection result. M. Davis and H. Putnam, A Computing Procedure for Quantification Theory, J. ACM 7 (1960), 201–215, https://doi.org/10.1145/321033.321034 . The present proof uses elementary Boolean function representation arguments; no comprehensive prior-art or novelty assessment is claimed.

Pinned code: fb4c9faa5cf8a32c286996e80ce443d6ad0b48fe. Executed workflow: https://github.com/tltmgnt/MathOS/actions/runs/45372843485. Evidence: cycle5-evidence.json.

Run: python -m unittest discover -s tests -p 'test_breakthrough_cycle5.py' -v

Run: python -m mathos.research.breakthrough_cycle5

Independent mathematical review and formal proof verification are outstanding. No global solution or proof promotion.
