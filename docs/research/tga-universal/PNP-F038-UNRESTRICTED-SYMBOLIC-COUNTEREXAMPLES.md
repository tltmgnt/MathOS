# F038 / direct unrestricted route — symbolic counterexample compiler and exact residual NP-completeness

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Parent 216203d8c872d240283216bdc88cf6dc4c117a21: https://github.com/tltmgnt/MathOS/actions/runs/45735702198 (success). All seven parent workflows passed.

## Goal and outcome

The preceding cycle derives counterexamples for the exact quadratic stage of the original universal witness-search machine U. Attack the higher-stage problem on the SAME machine, not another restricted representation. In particular, replace the old truth-table failure-formula fixture with an actual uniform bounded computation CNF compiler that leaves the candidate input and satisfying witness symbolic. The new compiler and exact residual-hardness theorem below do not establish satisfiability at exponent three. They give a concrete executable counterexample search target and explain why moving the problem into that target is not itself an unconditional lower bound. No novelty claim for bounded computation encodings or the residual-hardness argument. MRA-X roles are locally authored records, not independent agents.

## 1. The exact higher-exponent counterexample language

Use the original unary source-count and full normalized width-at-most-three selector input p of length L, the original U descriptions and the original stage s_k(n)=k ceil(log2 L). Define

    B_k = { valid encoded p : F(p)=1 and S_(s_k(n))(p)=0 }.

For every fixed positive integer k, the stage predicate S is deterministic polynomial-time computable in L by the earlier universal schedule bound. Therefore B_k belongs to NP: guess and check a satisfying assignment and replay the actual deterministic stage to confirm failure. Neither a witness of failure of an arbitrary unknown program nor an UNSAT proof is required; the bounded computation is total.

**Exact dichotomy:** for each fixed k, either B_k is empty or B_k is NP-complete under polynomial-time many-one reductions.

If B_k is empty, S at this cutoff is a correct total SAT decider; hence P=NP. If B_k is nonempty, choose one fixed encoded b_k in B_k. Given ordinary 3SAT, normalize it into p (handle malformed or trivially contradictory cases by a fixed no instance). Compute S at its cutoff. If it succeeds, output b_k. Otherwise output p. Sound verification implies every successful input is satisfiable; every unsuccessful input belongs to B_k exactly when it is satisfiable. Thus the transformation preserves yes and no cases. Its fixed constant b_k may be hardcoded for this one language and this one k. No efficient uniform procedure to find b_k given k is asserted. For a uniform search reduction, run the stage; if it succeeds return the verified witness, otherwise ask a solver for B_k witness search on the original p. This version requires no hardcoded bad instance.

If B_k is finite, membership in it can be decided by a finite hardcoded list, so the decomposition SAT(p)=S(p) OR B_k(p) again gives P=NP. Conversely if P=NP, the earlier universal-search equivalence gives some k with B_k empty. Thus P!=NP iff every B_k is infinite, and under that assumption each is NP-complete. The languages are nested B_(k+1) subset B_k. This is an exact residual-decision theorem, not a proof that any particular higher B_k is nonempty. The quadratic proof and nesting establish nonemptiness for k=1,2 only. Even NP-completeness of a nonempty B_k does not imply P!=NP. The quantifier over fixed k must not be silently exchanged for a uniform polynomial bound in k.

## 2. Symbolic simulation of the actual U

The former finite fixture blocked each already-solved selector by a separate clause chain, requiring enumeration of all 2^N selectors. The new implementation never enumerates input selectors during compilation. It constructs a Boolean circuit with the N selector bits and n proposed witness bits as free inputs, then emits exact Tseitin width-three CNF. All gates are binary AND with complemented wires and a forced true constant; OR and NOT follow by De Morgan and complementation. Each gate is constrained in both directions; every base assignment has a unique extension to the gate wires.

For a valid general program with q running states, halt state q, and allotted clock t>=1, retain tape cells indexed -t through t+n-1. The head starts at zero and moves by at most one each step. Every visited cell and every output cell read from the terminal head are in this interval. Initial tape symbols use the actual unary header, the symbolic selector bits, and blank outside the encoded input. Each cell has three one-hot symbol wires and q+1 one-hot head/state wires (all zero when the head is elsewhere). The initial state is zero at cell zero.

At each step form an event for each running head/state and read-symbol combination at each cell. It is exactly the conjunction of that head wire and symbol wire. The new symbol at a cell is the old symbol if there is no running head there, or the symbol written by its unique event. The next head/state wires are ORs of incoming events according to the decoded transition, plus the retained halt-head wire. The halt state is absorbing and no further writes occur after halt. Determinism gives exactly one head and exactly one symbol per cell at each step. Induction on time proves equality to the parent's concrete interpreter through its clock, with halting configurations frozen. The finite boundary cannot discard a real head transition because the maximum displacement at step i is i<=t.

At the final layer, for each of the n output offsets, OR the conjunction of a halt-head wire and the corresponding cell's zero or one symbol. Require every output offset to have a binary symbol. This handles timeouts (no halt head), malformed output (a blank), and halts at either tape boundary. Decode the one-symbol wires as the proposed assignment. Apply the actual verifier: for each clause, either its selector is zero or some literal of that proposal is true. Only a well-formed verified proposal contributes to stage success.

The original short built-ins are compiled too, not replaced with a hypothetical solver. The null and invalid proposals are rejected; fixed proposals obey their exact costs. The p mod 4 proposal reads the first two selector bits (and is rejected if outside n bits), and its cost 2+p mod 3 is checked by a three-state residue circuit scanning selector bits. The exhaustive built-in is inactive unless its original clock permits all 2^n assignments. If active, its success is exactly F(p); enumerate those assignments in the circuit only in that case, when 2^n<=2^(s-3). The other programs can then be omitted because verification means no proposal can succeed on an unsatisfiable selection.

Enumerate all valid general descriptions with e(q)<=s by their actual independent transition choices, rather than wasting launches on invalid strings. The parent decoder is used to verify those descriptions. For each description d, use exactly t=2^(s-|d|) steps. OR all verified success wires. This is exactly S_s(p). AND its negation with the independent witness verifier on x. Force that output true in the CNF. Denote the resulting symbolic formula by H_(n,s). For every p,x,

    exists gate assignment satisfying H_(n,s)
       iff x satisfies F_p and S_s(p)=0.

The extension to all gate wires, if accepted, is unique. Hence H is SAT iff a genuine counterexample exists at precisely that stage. In particular H_(n,3 ceil(log2 L)) is now an implemented construction, rather than merely a reference to Cook-Levin. Its large instances are not claimed to have been generated or solved in this cycle.

## 3. Explicit construction costs

A t-step program uses at most 2t+n cells, O(q) wires per cell per layer, and O(q) event and incoming-update gates per cell per step using bounded fan-in OR reductions. A loose uniform bound including output extraction and verification is poly(L+s)*(t+1)^2 gates and constructor operations up to polynomial bit overhead. Here n<=L and q<=s. There are at most 2^ell valid descriptions of length ell. Thus

    sum_(ell<=s) 2^ell (2^(s-ell))^2
       < 2^(2s+1).

Since t>=1, replacing t^2 by (t+1)^2 changes only a constant. The exhaustive built-in expansion, if active, uses O(L 2^n) gates with 2^n<=2^(s-3). The other built-ins are polynomial. Therefore the explicit circuit and CNF have O(poly(L+s) 4^s) gates/clauses. Their encoded bit size includes logarithmic wire indices; the total constructor time and storage are polynomial in L+2^s, including explicit descriptions, transition generation, gates, and integer arithmetic. For fixed k, s=k ceil(log2 L), so construction is polynomial in L with an exponent depending on k. The bound does not say construction is polynomial uniformly in binary s or in k. The prototype uses exact Boolean simplification and a gate cache, which can only reduce circuit size; even if dictionary operations are implemented with deterministic linear scans the polynomial bit bound remains valid.

No call to a SAT oracle occurs in the compiler. Deciding the resulting H is still an existential search. A SAT algorithm polynomial in its expanded size need not run within the original stage clock on p. In particular feeding H to U cannot force U to contradict itself at that stage: H is a different input of potentially much greater length and its witnesses refer to p. A polynomial-size fixed-k construction is not a proof of the all-exponent condition.

## 4. Validation and exact remaining gap

Independent scalar JavaScript replayed deterministic tape transitions on every selector of the one- and two-variable pools for 32 deterministic descriptions of each q=1,2,3 and clocks 1,2,4. Description generation uses x=seed+1, x=(1664525*x+1013904223) mod 2^32, and option=(x>>16) mod (9(q+1)), indexing next state, write symbol, and move. Rows [q,program/size/clock configurations,selector tests,well-formed emissions,verified emissions,sum emitted assignment integers,timeout or malformed]:
[1,192,24960,7552,956,15432,17408], [2,192,24960,6374,834,11245,18586], [3,192,24960,4188,538,7340,20772].
Independent JS also computed all built-in stage outcomes for source sizes one and two and stages zero through six. Python constructs the actual symbolic circuits, compares each program's output against the parent's interpreter and verifies each compiled counterexample CNF on every base selector/witness combination at those small stages. It checks a real stage containing general descriptions with exhaustive fallback enabled and individual generic-program compilation even where the fallback would subsume them. Boundary controls cover halt, invalid output, timeout, and inactive versus active exhaustive search. Independent JS did not execute Python. Finite tests are not asymptotic counterexamples. New exact-head CI, independent mathematical review and Lean formalization are outstanding.

Forward TGA: NARROWED_RESTRICTED_CASE_ONLY (implementation gap closed, no new exponent established). The exact higher-exponent Bad predicate is now executable as a symbolic CNF with polynomial fixed-k construction rather than an exponential selector truth table. The residual language dichotomy shows that no simplification of the target into an easier decision problem has been proved. Next pursue an actual satisfying-witness construction for H at k=3 and unbounded lengths, or prove a uniform polynomial success cutoff for the same U. Do not present the compiler, finite evidence or a restricted-model result as the missing existence proof. No universal obligation closes.
