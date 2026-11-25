# F038 — Unate interface certification and polarity-discovery barrier

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivations and finite regression, not a Lean declaration.
Verified base b6fbe4ee2fe1da6d8cad5a3b38bca39b910141eb: https://github.com/tltmgnt/MathOS/actions/runs/45703110225 (success).

## Syntactic mixed-polarity parameter kernel

Let F(x,y) be an explicit normalized CNF; x are the universally quantified parameters and y the existential witnesses. Let H be the subset of x occurring with both signs in the formula and h=|H|. For each assignment a to H define the worst parameter assignment w(a) by pinning H to a, setting every positive-only parameter to zero, every negative-only parameter to one, and absent parameters arbitrarily (say zero).

For any extension x of a, and any y satisfying F(w(a),y), the same y satisfies F(x,y): changing a positive-only parameter away from zero can only make its literals true, and changing a negative-only parameter away from one likewise. Absent parameters are irrelevant. Hence
forall x exists y F(x,y) iff for all a in {0,1}^h, exists y F(w(a),y).
The reverse implication preserves the actual witness, not just feasibility. Each failed seed supplies a concrete counterexample. If all seeds succeed, a lookup circuit indexed by H outputs the stored existential witness for any parameter assignment. This gives a witness circuit of O((h+q+1)2^h) gates/wires for q witness bits (a shared binary multiplexer implementation can use O((q+1)2^h) gates). The algorithm needs 2^h pinned SAT/model queries, not 2^|x|.

When a tree decomposition of maximum bag size b is supplied, use the previously verified fixed-input witness algorithm for the seed calls. Total construction and certification cost is 2^O(b+h) poly(L) in the explicit input length L. This is fixed-parameter tractable in b+h. In particular b+h=O(log L) suffices for uniform polynomial time, in contrast to the previous generic double-exponential-in-b certification algorithm. Computing the syntactic kernel is a linear scan of the literals. The bound does not assume any polarity restriction on the existential variables.

A semantic variant: if the projected feasibility function C_F(x)=exists y F(x,y) has a supplied valid unate orientation outside H, the same extreme-point tests certify totality; the witness reuse conclusion above does not follow from semantic monotonicity alone. A per-input solver may still be required. E.g. y=x has constant true projection but no constant witness. A supplied semantic orientation is a promise or proof obligation, not a syntactically certified fact.

## Semantic polarity recognition is coNP-complete at logarithmic width

A Boolean function is unate in parameter t if it is nondecreasing or nonincreasing in t (one orientation must work over all assignments of other parameters). A non-unate function has one rising edge and one falling edge in the same coordinate. On a supplied logarithmic-bag-size decomposition, pinned feasibility is polynomial time, so a pair of such edges is a polynomially checkable certificate of non-unateness. This gives coNP membership for testing a specified coordinate, and for testing whether all coordinates are unate.

For hardness, start with arbitrary 3-CNF D(x), m clauses, and introduce two fresh universal bits t,r. Use the preceding clause-address reduction: k=max(1,ceil(log2(max(1,m)))) existential address bits p, mismatch clause M_j(p) false exactly at p=j. Add (r OR t). For every invalid address j add (not r OR not t OR M_j(p)); for every literal l of a valid clause D_j add (not r OR not t OR M_j(p) OR not l). Split long clauses into width at most three using private existential chain variables. This yields F(x,t,r,p,u) with projection
C(x,t,r)=(r OR t) AND (not r OR not t OR not D(x)).
At r=0 it equals t, guaranteeing rising edges in t. At r=1 it equals not t OR not D(x), yielding a falling edge iff D(x)=1 for some x. Therefore C is unate in t iff D is unsatisfiable. If D is unsatisfiable, C=r OR t, which is unate in all coordinates; if satisfiable, t is non-unate. This proves both hardness claims.

A supplied decomposition uses a central bag containing p,t,r; child bags include one original variable each, and a path for every split clause contains the corresponding base bag plus at most two consecutive auxiliaries. The bag size is at most k+5 and the construction is polynomial. It applies also to empty source formulas and empty clauses. Thus even when a projected circuit can be compiled in polynomial time, recognizing semantic unateness is coNP-complete on a logarithmic-width domain. A general polynomial-time semantic-polarity detector for that domain would imply P=NP. This is not a lower bound on evaluating the projected function or on computing any one feasible witness. The syntactic kernel algorithm avoids this recognition problem by checking explicit literal occurrences only.

## Finite controls

Positive: all 4096 subsets of the previous four-bag 12-clause template, both parameter sets. Compare each worst-slice query with exhaustive slice feasibility and test reuse of every successful seed for all slice assignments. Expected: 8192 families, 592 total, 7600 non-total, 30964 seed probes, 24508 missing, 6456 successful slices, 13421 reused witnesses, 65536 parameter cases, max eight probes per family. The repository uses the prior factored-interface reconstruction as the seed solver.

Negative: all 4096 subsets of the previous three-variable mixed-width template. Check the guarded CNF projection at all x,t,r and count rising/falling edges in t; check unateness equivalence with source UNSAT. Expected: 2736 unate, 1360 non-unate, 131072 projection checks, 32768 rising edges, 2304 falling edges, max 109 variables and 127 clauses. The repository additionally checks the supplied decomposition. Independent finite tests validate the construction, not the asymptotic complexity claims.

## Resolution boundary

This supplies a constructive polynomial-time witness synthesis and certification domain that includes logarithmic-width inputs with logarithmic mixed-polarity parameter count. It does not establish that arbitrary CNF admits such a parameterization, or that semantic unate orientations can be recognized in polynomial time. Pure syntactic polarity is sufficient but not necessary. With no universal parameters, the width bound still limits the SAT solver; no universal polynomial-time SAT algorithm or unrestricted lower bound follows. Next: investigate polarity reduction via certified equivalence-preserving transformations, with explicit bounds on width, mixed parameter count, and total transformation cost, or directly confront unrestricted SAT.
