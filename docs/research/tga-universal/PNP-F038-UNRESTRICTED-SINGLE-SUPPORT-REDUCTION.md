# F038 / unrestricted route — exact single-support normal form and all-exponent transfer

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Parent 71a680abb12e5bc3fe59574d5524661476c5adc4: https://github.com/tltmgnt/MathOS/actions/runs/45743031920 (success). Six parent workflows passed at inspection; TOPO-406 was still running.

## Objective

The previous quadratic adversary has a subcubic witness algorithm. Two earlier necessary conditions for unbounded cubic failure concern variables uncovered by complete ternary supports and the hitting number of locally non-bijunctive supports. Rather than continue that exhausted adversary or merely add further exclusion tests, construct a linear-variable, exact model-preserving normal form that meets both necessary conditions maximally or linearly. Prove that investigating all-exponent failures on this normal form is equivalent to the original unrestricted problem, with an explicit transfer direction between stages. This is a reduction and a test of the value of the earlier filters, not a new lower bound. Same U, actual complete selector representation, actual verifier and weighted clocks. No novelty claim for elementary SAT gadget reductions.

## 1. A constant forcing gadget with at most one clause per support

Index seven variables z_0,...,z_6 cyclically modulo seven. For each i select the three clauses

    (not z_i OR z_(i+1) OR z_(i+2)),
    (not z_i OR z_(i+3) OR z_(i+5)),
    (not z_i OR z_(i+4) OR z_(i+6)).

These occupy 21 distinct supports: the three base triples have different unordered cyclic gap multisets {1,1,5}, {2,2,3}, {1,2,4}, and each has seven distinct rotations. On each of the other 14 supports choose the all-negative clause. Every one of the 35 supports now has exactly one selected clause. The all-zero assignment satisfies every clause. If any bit is one, its three disjoint pair constraints force at least three more ones. Every four-element subset contains a triple outside the 21 supports of the implication clauses. For a short exact verification, identify a subset by its seven-bit mask (z_0 low bit). The five cyclic orbits of four-subsets have minimum-mask representatives 15,23,27,29,43; respectively spare triple masks 11,19,25,25,11 are contained in those representatives. The representatives can be checked by listing all seven rotations of each: the five disjoint orbits have 35 elements, exhausting the 35 four-subsets. Rotation preserves spare supports. Thus an assignment with four or more ones falsifies one selected all-negative clause. The gadget has the unique model zero. No unit or binary clauses, repeated variables, or repeated supports are used.

## 2. Parsimonious injective transformation

Given an arbitrary original selector p on n variables, use h=3n+7 variables. Reserve the first seven for the gadget, now numbered 1..7. For original variable i=1..n let u_i=8+3(i-1), v_i=u_i+1, d_i=u_i+2. For each i include

    (not u_i OR v_i OR z_0),
    (u_i OR not v_i OR z_1),
    (not d_i OR z_0 OR z_1),
    (u_i OR v_i OR not d_i).

With the gadget's constants zero, these force u_i=v_i and d_i=0; the fourth clause is redundant but has a disjoint triple support for each i. Translate each selected original literal -i to -u_i and +i to +v_i. Translate each selected original clause by this substitution, padding a width-two clause with positive z_0 and a unit with positive z_0,z_1. Normalize literals by absolute variable index, select these and only the fixed and mapped clauses in the full h-variable selector pool. Call the resulting selector f_n(p).

Every translated support is distinct for distinct original clauses: its non-gadget variable indices recover both the original indices and the original signs, and the number of those indices recovers clause width. Each translated clause uses at most one of the u_i,v_i,d_i of an original variable and never a dummy d_i; the fixed equality clauses use both copies, dummy pins use a dummy, and the last fixed clause uses all three. The gadget clauses use only gadget variables. Therefore none of the fixed and translated supports collide. Every selected clause has width exactly three and every support contains at most one selected clause. The fixed clauses have 2^n models, exactly the extensions of the original assignments obtained by setting both copies equal to the corresponding source bit and setting all seven constants and every dummy to zero. A translated clause is true on such an extension iff the original clause is true. Hence the model sets correspond bijectively. In particular the transformation preserves UNSAT, SAT, uniqueness and the exact number of models. Project by reading the u_i bits. Removing the fixed clauses and inverting the translated indices recovers p; even easier, query the selected bit at each known translated clause position. Thus f_n is injective, also across source sizes since h increases strictly.

The output is the COMPLETE original selector tape at size h, not a compact clause list. Its length is L(h)=Theta(L(n)); in fact L(h)/L(n) tends to 27. A fixed multitape bit algorithm can enumerate the original pool, extract selected clauses, translate their indices with binary counters, append fixed clause records, sort by width/support/sign with sequential merge passes, then enumerate the h-pool and emit the output selector bits in order. Both pools contain O(L(n)) clauses, and all explicit records have O(log L) bits. This costs O(L polylog L) sequential multitape bit time and space, or O(L^2 polylog L) by ordinary quadratic fixed one-tape simulation including output conversion. Inversion and witness projection have polynomial bit cost. The Python implementation is an exact finite prototype, not a compiled one-tape program or a benchmark of that bound.

## 3. The previous two necessary filters are jointly insufficient

Every selector in the image has no complete seven-of-eight support at all, so the uncovered-variable count u(f_n(p)) equals h. Every selected triple block is non-bijunctive: a single width-three clause forbids one of eight local assignments, but all four projections onto any variable pair occur among the seven allowed assignments, hence its binary-clause closure is the full cube. The n fixed dummy triples (u_i,v_i,d_i) are disjoint, so the hitting number tau(f_n(p)) is at least n. These properties hold whether the original p is SAT or UNSAT. In particular the image of an arbitrary easy or hard SAT instance passes BOTH previous necessary asymptotic cubic-failure filters, with linear rather than logarithmic hitting number. They do not identify a tractable remainder and cannot by themselves establish a lower bound.

## 4. Transfer of actual residual failure and exact remaining problem

Let C_h denote the image of f_n at h=3n+7 (empty at other sizes). For each fixed positive integer k there exists a fixed integer K>=k such that, for EVERY n,

    f_n(B_K(n)) subset B_k(3n+7) intersect C_(3n+7).

Proof: consider the fixed algorithm on arbitrary original p which constructs the transformed selector, runs the actual U stage k ceil(log2 L(h)) on that selector, and projects any verified witness. That algorithm is total, with polynomial bit runtime in L(n) for fixed k by the earlier stage bound and the linear-length reduction. Failure yields no verified witness, not an UNSAT inference. Its successful execution has a fixed general U tape implementation of polynomial runtime in L(n), using standard polynomial-overhead tape simulation and exact output positioning. Its description length is fixed. Hence some integer K>=k covers this successful computation in the original stage K ceil(log2 L(n)) on every valid input, including the finite small sizes after increasing K. If a satisfiable p belongs to B_K(n), the algorithm cannot succeed, yet f_n(p) is satisfiable; its actual stage-k must fail. Injection yields the exact census transfer

    |B_k(3n+7) intersect C_(3n+7)| >= |B_K(n)|.

The K here depends on k and the fixed implementation; it is not identified with k and is not a numerical bound. A near-linear input translation does not make executing an entire U stage cost the same as one simulated program. No same-exponent transfer is claimed.

Consequently P!=NP iff, for EVERY fixed k>=1, there exist arbitrarily large h and satisfiable selectors in C_h that defeat the unchanged exact stage k ceil(log2 L(h)). The forward direction uses the previous all-exponent equivalence and transfer. The reverse follows because C_h is a subset of the original input domain. The same equivalence holds for the larger class of all ternary-only selectors with at most one selected clause per support; the image suffices for the forward direction. If a fixed stage succeeds on all sufficiently large satisfiable members of that larger class, projection and finite exceptions yield P=NP. This is an exact equivalent reformulation of the unrestricted target, not a proof of either side. In particular the known unbounded B_2 failures do NOT establish unbounded B_3 failures in the image: the transfer needs failure at K, which may be larger than three. The proof does not assume a hard source formula or a freely supplied source witness.

## 5. Evidence and scope

Independent JavaScript constructed the 35-clause cyclic gadget, enumerated all 128 gadget assignments, and verified the five orbit representatives. It constructed the complete source and target clause pools for n=1,2,3,4, enumerated every assignment to the fixed target constraints (1024,8192,65536,524288 assignments respectively), and found exactly 2^n fixed models with the prescribed copy and dummy values. It tested all 4 and 256 selectors for n=1,2, and 130 deterministic fixtures for each of n=3,4 (empty, full and 128 seeded clause masks). It compared the truth of each original formula and its target on every source assignment, checked support uniqueness across all possible mapped clauses, and compared distinct selector keys. Rows in the plan record [n,h,target pool length,fixed assignment tests,fixed model count,source fixtures,SAT fixtures,source assignment tests,total models,selected target clauses summed,distinct transformed selectors]. The Python regression checks the actual target selector bits, reverses the mapping, verifies with the actual parent verifier, and independently audits gadget orbits and local irreducibility. JS did not execute the submitted Python module. The finite fixtures verify semantics, not the existence of unbounded cubic counterexamples or the numerical simulation constants. No generic source-to-U compiler is implemented. New exact-head CI, independent mathematical review and Lean formalization remain outstanding.

Forward TGA: BARRIER_IDENTIFIED. The two earlier exclusion criteria are compatible with a parsimonious, linear-variable embedding of arbitrary SAT. Unrestricted all-exponent failure is equivalent to failure on the single-support normal form; the exact cubic existence theorem remains open. Next seek a genuinely resource-sensitive adversary within this form or a universal polynomial cutoff, rather than treating the structural filters as evidence of hardness. No universal obligation closes.
