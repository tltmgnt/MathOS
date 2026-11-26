# F038 / direct unrestricted route — one universal SAT witness machine and exact counterexample targets

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Parent 731f4dfeb426fa1d41d21834b60f7aca54406ca1: https://github.com/tltmgnt/MathOS/actions/runs/45733029874 (success). All seven parent workflows completed successfully.

## Research priority

The user explicitly redirected the work from repeated restricted-model bounds to unrestricted deterministic SAT complexity. This cycle targets every polynomial-time algorithm, including arbitrary representations, nonlinear sharing, memory and adaptive computations. The proof uses classical universal search, SAT self-reducibility and uniform bounded computation encoding. No novelty claim or resolution claim. The seven MRA-X records are locally authored, not independently running agents.

## Constructive track: a single universal witness search machine

Use the full normalized nonempty width-at-most-three clause pool U_n on n>=1 variables, with N selector bits. Encode input as n unary ones, a zero delimiter, then the N selector bits; L=n+1+N. Any ordinary 3CNF can be normalized, variables renamed and encoded in polynomial time. Handle empty clauses separately, and add a dummy variable when necessary. A satisfying assignment of the resulting selection recovers a witness of the original formula. The universal selector is therefore NP-complete as a uniform encoded decision problem, and its witness verification is polynomial in L.

Choose a fixed effective binary encoding of arbitrary deterministic Turing machines, with a polynomial-overhead universal interpreter and a convention for emitting n source bits at halt. The encoding may include a finite number of special-purpose built-in programs with their actual costs charged. It need not be prefix-free because the scheduler explicitly enumerates each length separately. Every polynomial-time deterministic witness algorithm on the chosen input encoding has an encoding of some fixed length ell and a polynomial simulation bound; arbitrary ordinary multi-tape computations can be simulated by a single-tape machine with polynomial overhead. Invalid programs or malformed outputs are ignored. Never trust a program's claimed SAT/UNSAT decision; verify an emitted assignment directly.

At integer stage s>=0, run every binary description d of length ell<=s from scratch for at most 2^(s-ell) simulated steps on the input. Accept only a verified model. Stage s enumerates exactly 2^(s+1)-1 strings and charges at most

    sum_{ell=0}^s 2^ell * 2^(s-ell) = (s+1)2^s

simulated steps. Charge parsing, tape handling, counters, input copies, output verification and loop overhead as well. There is a fixed polynomial bound in L+2^s for all operations through stage s, independent of the programs being simulated: each tape grows at most with input length and the simulated step limit, each transition can be found in its explicit description, and there are fewer than 2^(s+2) launches through stage s. The same bound holds with a fixed ordinary deterministic bit-machine implementation, not a model with free oracles or arbitrary-precision unit-cost arithmetic.

If any program of length ell produces a verified model in t>=1 simulated steps, it succeeds by stage ell+ceil(log2 t). Thus the fixed universal search U (run successive stages and return a verified model when one is found) has runtime bounded by a fixed polynomial in L+2^ell*t for that input. There is no restriction on the code of a competing algorithm. On every satisfiable input U eventually returns: exhaustive assignment search is an available program (also a charged built-in in the prototype). On unsatisfiable input U never returns a model and need not halt. The stage-success predicate S_s(p) is total, and monotone in s, since deterministic simulations are restarted with a nondecreasing step allotment and the same verifier.

### Exact unrestricted equivalence

If P=NP, ordinary SAT self-reducibility gives a deterministic polynomial-time witness algorithm: on a satisfiable formula, successively pin each variable, query the residual SAT problem and retain a satisfiable branch. This takes polynomially many polynomial-length queries; the emitted model is verifiable. A fixed encoding of that algorithm is included in U's search, so U succeeds in polynomial total bit time on every satisfiable input, with one uniform polynomial bound.

Conversely, if U has a uniform polynomial success-time bound on all satisfiable encoded inputs, simulate U for that bound. Return SAT if a verified model is found, otherwise UNSAT. On a satisfiable input the bound guarantees success; on an unsatisfiable input verification prevents false success. Normalization transfers this to all ordinary SAT inputs. Therefore

    P=NP iff the single fixed U has polynomially bounded success time on SAT inputs.

Equivalently P=NP iff there exists an integer k>=1 such that, for every n>=1 and every satisfiable selector p, S_{k ceil(log2 L)}(p)=1. For the forward direction absorb the fixed description length, polynomial constants, simulation overhead and finitely many small inputs into k (L>=2). For the backward direction the stage runtime bound is polynomial because 2^(k ceil(log2 L))<=(2L)^k. This removes the quantifier over all candidate algorithms without restricting the computational model. It does not establish either side of the equivalence.

## Direct adversarial target: bounded universal counterexample formulas

For each source n and stage s, define a Boolean predicate in p and an n-bit witness x:

    Bad_(n,s)(p,x) = [x satisfies every selected clause of p] AND NOT S_s(p).

Construct a width-three CNF H_(n,s) satisfiable exactly when there is such a pair. In the mathematical construction, take a fixed deterministic bounded-stage simulator, evaluate it on the symbolic p input with n and s fixed, and compile its bounded computation to a uniform Boolean circuit. A time-T machine computation can be represented by a circuit of size polynomial in T+L (e.g. explicitly update each cell of a bounded tape and head/state information for each step), with a deterministic uniform constructor taking polynomial time in the same bound. Encode every gate's equivalence and the forced final accepting bit by width-three clauses with fresh auxiliary variables. Include the witness verification predicate. For every p,x the extension is satisfiable iff Bad is true. All encoding and construction costs are polynomial in L+2^s, not necessarily polynomial in the binary representation of s. This is the standard bounded computation encoding, not an implemented general efficient compiler in the finite prototype. The source p and witness x remain actual free inputs until existentially quantified in H.

Set s_k(n)=k ceil(log2 L(n)). The direct, unrestricted negative goal is now the explicit family of statements

    for every integer k>=1, infinitely many n have H_(n,s_k(n)) satisfiable.

This is equivalent to P!=NP. If the family holds, no polynomial bound for U exists. If P!=NP and there were some k for which only finitely many n had a bad input, all sufficiently large source sizes would be decided by the stage cutoff. The finitely many smaller sizes can be handled by brute force, or k increased to absorb their finite maximum success stages; this would give P=NP. Equivalently the positive goal is existence of k such that every H_(n,s_k(n)) is unsatisfiable. For fixed k each H has polynomial size and a uniform polynomial-time constructor in L; the exponent depends on k. This does not claim a uniform polynomial in both variable k and L.

There is an exact finite counterexample generator: for fixed n,s enumerate all p and all source witnesses, test bounded-stage success, return the first bad pair or NONE. This always halts and can be verified without a SAT oracle, but costs exponential in selector length in general. A more compact existential counterexample formula H can be searched via SAT self-reduction; that does not provide a polynomial algorithm without an assumed SAT decider. If P!=NP, the equivalence gives a total computable sequence of increasingly large bad instances for k=1,2,... by searching n larger than the previous n until finding a bad pair. Its termination for each k is conditional on the unproved negative result; no polynomial hard-instance generator is asserted. Any generator that, from unary n, outputs these formulas AND witnesses in polynomial time on their indexed lengths would itself provide a polynomial witness procedure on its generated inputs (compare the input selector to the generated one). It could not beat U's fixed polynomial simulation overhead for unbounded k. This emphasizes that producing hard instances with efficiently recoverable witnesses is not a free diagonalization tool.

## Alternative track: the direct diagonalization gap

The construction of H is a real search for failures of unrestricted computation, but it does not force H to be satisfiable. A machine can correctly process its own bounded-counterexample formula: if H is satisfiable, solving it returns a hard instance of a DIFFERENT source length, not necessarily a failure on H itself. If H is unsatisfiable, there may simply be no counterexample at the given size and cutoff. A reduction can enlarge the input from L to poly(L+2^s), so a bound polynomial in the new input length need not fit within the original cutoff. Invoking the recursion theorem for program descriptions does not by itself supply a fixed point in explicit CNF length or a smaller bounded simulation. Likewise time hierarchy can separate fixed clock classes via predicates with larger verification exponent; it does not automatically give one NP-complete problem outside every polynomial clock. The missing mathematical step is a construction or structural theorem ensuring the family above has satisfying witnesses for every k, without assuming the result. No restricted proof-system lower bound, black-box oracle lower bound or nonuniform gate-count lower bound is substituted for it. Stop any proposed diagonalization that changes the input, clock or quantifier without an explicit charged preservation proof.

## Evidence and cost

The prototype implements the actual binary-description schedule, verification on the normalized selector encoding, a finite set of cheap built-ins and a general explicitly encoded deterministic tape machine interpreter (three tape symbols, finite states, moves left/stay/right, halt/output convention). The mathematical quantification over arbitrary algorithms uses this general machine family, not the finite built-ins. The built-ins have simple bounded semantics; exhaustive search only runs when its clock permits it. Their Python implementation costs polynomial per simulated step in input length. The interpreter and input format are specified in the code. For small stages the general tape descriptions are too long to be enumerated; separate interpreter controls test the actual generic simulation, its clock, and invalid code rejection.

Independent scalar JS calculated the schedule outcomes on all 256 selections of the two-variable full pool and all seven stages 0..6 using the eight short built-ins, with explicit witness validation and the equivalent minimum-length-plus-log-time criterion. Rows [selectors,SAT selectors,stage tests,eligible built-in launches,successful stage tests,bad SAT stage tests,source models] = [256,95,1792,11008,473,192,128]. First success stage histogram [0,32,46,0,17,0,0]. Bad selector counts [95,63,17,17,0,0,0]. A second reference independently computed the projected failure-predicate and explicit finite CNF sizes, rows [stage,scheduled binary descriptions,solved selectors,bad SAT selectors,bad (selector,witness) pairs,variables,clauses,base pair tests]:
[0,1,0,95,128,10,8,1024],
[1,3,32,63,76,234,712,1024],
[2,7,78,17,17,556,1724,1024],
[3,15,78,17,17,556,1724,1024],
[4,31,95,0,0,675,2098,1024],
[5,63,95,0,0,675,2098,1024],
[6,127,95,0,0,675,2098,1024].
Python additionally enumerates all binary descriptions at these stages, compares successful witnesses, constructs width-three finite counterexample CNFs by blocking solved selectors using OR-gate equivalences, and checks every base input with its uniquely determined auxiliary gate values. This deliberately exponential truth-table compiler is ONLY a bounded regression fixture, not the uniform polynomial bounded computation compiler in the theorem. Its actual costs are not hidden. Independent JS did not execute Python. Small stages where all satisfiable fixtures are solved illustrate why bounded counterexample existence is not automatic. Exact-head CI, independent mathematical review and Lean formalization outstanding.

Forward TGA: BARRIER_IDENTIFIED, direct unrestricted route. The exact universal negative obligation is now satisfiability of H_(n,s_k(n)) for arbitrarily large n for each k. Next target a concrete witness-producing adversarial construction for that exact predicate or a proof of its universal UNSAT cutoff. Require the same U, encoding and clock throughout. Do not redirect to unrelated restricted-model representation counts. No universal obligation closes.
