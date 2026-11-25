# F038 — Symbolic interface compression and certification complexity

PNP_RESOLUTION_STATUS = OPEN. Structural derivation and finite regression, not a Lean declaration.
Verified base abe903096e491c48025348f311cd88d1078f2371, dedicated replay https://github.com/tltmgnt/MathOS/actions/runs/45702868333 (success). The original factored-interface replay failed on an unclosed Python fixture tuple; the repair adds the missing closing parenthesis without changing its mathematical statement or test expectations.

## Symbolic compression of every attainable table

For a supplied rooted variable-scope tree decomposition of CNF F(x,y), use the notation B_v, F_v, V_v and maximum bag size b from F038 factored interface. For every assignment a to B_v construct a Boolean circuit P_v,a(x) over the universal parameter bits. Define L_v,a to be the constant truth of all local clauses on a, conjoined with the literals requiring a to agree with x on B_v intersect X. For child c let S=B_v intersect B_c. Define

P_v,a = L_v,a AND (AND over children c of (OR over assignments d to B_c with d|S=a|S of P_c,d)).

The empty OR is false and empty AND is true. Running intersection proves inductively that P_v,a(x)=1 iff a extends to a model of F_v with parameters in V_v pinned to x. In particular C_F(x)=OR_a P_root,a(x) equals exists y F(x,y). The symbolic representation retains correlations between different table rows through shared parameter inputs. It does not replace the family of possible tables by the union of their rows, which would lose correlations.

Build a shared DAG bottom-up, never expand child circuits as formulas. At most 2^b rows per bag and at most 2^(2b) pairs per tree edge suffice to construct all compatibility gates. With binary fan-in via linear-size AND/OR trees, the total circuit size and compilation time are 2^O(b) poly(L) for explicit input/decomposition length L. No enumeration of parameter assignments or of attainable tables occurs during compilation. At fixed x all tables can be read by evaluating the DAG, then the preceding top-down reconstruction yields a witness. Universal totality is equivalent to C_F being a tautology. Thus a compact circuit does not by itself give efficient universal certification.

## Logarithmic-width certification hardness with supplied decomposition

Take an explicit normalized 3-CNF D(x) on n variables with m clauses. Let k=max(1,ceil(log2(max(1,m)))). Introduce k existential bits p encoding a clause index. For every invalid index j>=m forbid p=j with the mismatch clause M_j(p). For each valid j and literal l in clause D_j, impose (p=j) implies not l, i.e. M_j(p) OR not l. If D_j is empty, no constraints for that index are needed. Every clause is existentially split into width at most three using private chain auxiliaries. For fixed x and p=j, the resulting formula H has an extension exactly when j is valid and D_j is false on x. Consequently
exists p,u H(x,p,u) iff not D(x);
forall x exists p,u H(x,p,u) iff D is unsatisfiable.

Supply an explicit tree decomposition with central bag p, a child bag p union {x_i} for each input variable, and one attached path per implication. Along the path, bags contain its base bag and the at most two chain auxiliaries incident to each split clause. Invalid-index paths attach to the central bag. Running intersection holds for each address bit, each x_i, and each private auxiliary; every clause has a containing bag. Maximum bag size is at most k+3, including when the source has zero or empty clauses. The size of H and decomposition is polynomial in n+m. The problem of universal totality on this logarithmic-bag-size family is coNP-hard, even though the symbolic circuits can be constructed in polynomial time. Membership in coNP on supplied logarithmic-width decompositions follows because a counterexample x can be checked by the fixed-input bag DP in polynomial time. Hence universal certification on this restricted family is coNP-complete (or on the promise of the specified logarithmic bound). Ordinary tautology checking, not circuit evaluation, is the remaining obligation.

## Conditional time barrier

Under the Exponential Time Hypothesis (ETH), 3-SAT on n variables cannot be solved in 2^o(n) poly(input length) time. Normalize away duplicates and tautologies so m=O(n^3), with polynomial preprocessing; then b<=k+3=O(log n) and output length is polynomial in n. A universal certification algorithm running in 2^(2^o(b)) poly(L) on supplied decompositions would decide 3-SAT by complementing its result in 2^(n^o(1)) poly(n)=2^o(n) time, contradicting ETH. This matches the double-exponential parameter scale of the previous exact DP, conditional on ETH. The proof is a direct clause-address reduction, consistent with the known quantified-SAT treewidth lower bounds of Lampis and Mitsou, Treewidth with a Quantifier Alternation Revisited, https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.IPEC.2017.26 . It is not claimed as a new general complexity theorem.

The conditional bound concerns certification of totality over all x, not finding a witness for a given x. Indeed in the reduction, given x one may scan D for a violated clause in polynomial time. The previous double-exponential state-diversity result is not a time lower bound; this separate ETH argument supplies a conditional one. Neither implies an unrestricted SAT runtime bound unconditionally or resolves P versus NP.

## Finite validation

Exhaust the previous 4096-subset four-bag template with both parameter sets. Compare the compiled symbolic DAG at every parameter assignment with every explicit subtree row and the whole formula. Expected: 8192 families, 65536 parameter assignments, 1835008 row checks, 592 total families, maximum 91 DAG nodes (unbounded-fan-in nodes, with all fan-ins explicitly stored). Separately exhaust 4096 subsets of the earlier mixed three-variable matrix; check every parameter and clause-address pair with an exact SAT oracle. Expected 1360 satisfiable source formulas, 2736 unsatisfiable, 32768 parameter cases, 30464 feasible, 254608 address checks, max bag size 7, 55 variables and 74 clauses. Repository audit additionally checks actual decomposition validity and verifies the reduction via the compiled circuit. The finite controls do not prove ETH or the asymptotic theorem.

Next: identify tractable symbolic certificate languages (e.g. common unate polarity) with explicit closure and coverage guarantees, or focus directly on uniform SAT computation rather than treating universal certification hardness as a separation.
