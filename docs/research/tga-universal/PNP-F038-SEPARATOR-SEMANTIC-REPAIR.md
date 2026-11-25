# F038 / TECT-X-13 — Two-pass affine separator semantic repair

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and executable regression, not a Lean declaration.
Verified base bb75a8ce7b8bc7026ad3a8577dffb9c50d63dd5c: https://github.com/tltmgnt/MathOS/actions/runs/45713314069 (success).

## Same-tree semantic repair theorem

Extract A AND B with verified source provenance and parametrize consistent A as x=x0+Gt. The designated candidate C is one residual occurrence, not an extracted affine row. Use any checked binary clause tree over B, with W_v, O_v, S_v=W_v intersect O_v as in the preceding separator theorem; b=max dim S_v and ell=max leaf dim W_v. Parameter directions are linear functionals on the ambient free-coordinate space; every functional on the global residual direction span extends. Adding a parameter translation d preserves A and yields original-coordinate translation Gd.

Let P_i be the allowed functional signatures on W_i for clause i. The bad-model relation M=A AND (B-C) AND not C is obtained by complementing just P_C. The tree and every separator rank remain unchanged. We need the exact projections R_i of M onto each W_i. The earlier general semantic compiler queried them one by one. Here compute them in two passes on the same tree.

Upward U_v: boundary signatures extending to a functional satisfying the modified predicates inside v. This is the established exact separator recurrence.
Downward V_v: boundary signatures extending to a functional satisfying all modified predicates outside v. At the root V_root={0}, even if the inside is inconsistent. At a join with children a,c, compute V_a from V_v and U_c, and V_c symmetrically. The outside space of a is O_v+W_c. Their intersection O_v intersect W_c is contained in S_v and S_c. Moreover S_a is contained in S_v+S_c: for s in S_a write s=o+w with o in O_v,w in W_c. Since s,w are in W_v, o is in S_v; and since w=s+o belongs to W_a+O_v, w is in S_c. Therefore two boundary rows can be glued precisely when their linear restrictions agree on the shared space. Solve their joint linear equations, and restrict the resulting functional to S_a. The restriction is independent of the representative because S_a is contained in their sum. Any compatible pair of exterior and sibling extensions glues on their full spans; conversely every exterior solution restricts to such a pair. This proves the downward recurrence without treating correlated projections as independent.

At leaf i, enumerate its modified allowed signatures z and retain precisely those whose restriction to S_i is in V_i. They are exactly R_i by the same gluing theorem. No SAT oracle or global assignment enumeration is needed.

## Translation compilation without increasing width

For a candidate parameter direction d, let h_i be its signature on W_i. For every z in R_i require z XOR h_i in P_i (the ORIGINAL allowed predicate, even at C). Equivalently define the translation predicate

Q_i = {h : R_i XOR h is a subset of P_i}.

If R_i is empty the predicate accepts every h. In particular if M is empty all predicates are unconstrained and zero works. Every actual bad model projects into each R_i, so these conditions suffice for a translation to repair every bad model. Necessity follows because every z in R_i comes from an actual bad model. Thus the conjunction of Q_i describes exactly the valid translations, including all directions that are invisible on the residual span. It uses the original leaf spaces, not new variables or added clause occurrences. Local truth tables represent the predicates; no CNF expansion or affine re-extraction is needed. Run an ordinary upward message pass on Q_i, reconstruct a direction and apply conditional repair. A failed translation search is not evidence that A AND B is UNSAT; simply retain C.

All preprocessing is polynomial in explicit length L including the tree. Each upward or downward join examines at most 2^(2b) pairs. Each leaf projection enumerates at most 2^ell signatures, and Q_i construction takes at most 2^(2ell) membership tests. Hence for a designated occurrence, the complete decision, translation reconstruction and certificate generation cost

poly(L) (1+2^(2b)+2^(2ell)).

For width-three source residual clauses ell<=3, giving 2^O(b) poly(L). The same bound suffices to examine all candidates and perform greedy repeated deletions: at most m rounds of m candidates, prune removed leaves and suppress unary nodes, retaining the original affine extraction and parametrization. Width cannot increase under deletion, so the original supplied tree budget bounds the cost throughout. This is a theorem about possible repeated deletion; the executable here implements one designated occurrence at a time. With the previously cited external connectivity oracle discovery theorem the end-to-end theoretical bound is 2^O(b^2) poly(L) where b is optimal ORIGINAL width. The external discovery algorithm remains unimplemented. A small final width alone does not bound the cost of initial semantic discovery.

## Certificates

For a designated candidate, retain upward and downward boundary row sets for the bad relation, all exact leaf projections, compiled Q_i sets, and upward row sets for the translation relation. A checker validates extraction and tree and recomputes each local recurrence from supplied neighboring rows in topological order, and each local predicate from supplied projections. No witness representatives are trusted in this checker. An empty translation root certifies no constant translation in this class; a nonempty root together with a concrete direction whose signatures belong to all Q_i certifies the repair. A valid translation preserves source A and all remaining actual models under conditional repair. The checker has the same parameterized cost. This does not give polynomial certificates for arbitrary width or verify arbitrary repair maps.

The code uses actual Gaussian elimination and explicit leaf truth tables. Small independent audits use exhaustive affine model enumeration and finite span arithmetic. The primary fixture has 4096 source selections, 2384 inconsistent extractions, 4736 designated residual occurrences, 3424 empty bad sets, 4294 semantic-existence cases, 4189 pairwise-existence cases, 105 strict-existence cases (35 with nonempty bad set), 26320 checks each for inside and outside tables, 15528 projected leaf checks, 11136 actual affine direction checks, 8587 valid directions, 1795 repaired bad-model/direction pairs. The eight-full-width fixture has 256 selections, one inconsistent extraction, 896 candidates, no empty bad sets, 896 semantic and pairwise existence, 6336 checks each for inside and outside tables, 3616 projections, 6944 directions, 3328 valid directions and repairs. Maximum separator width three in both. Repository regression also tests the odd/even cycle family on eight sizes up to 32 (global rank 32, boundary rank <=4), checks both satisfiable and impossible repair cases, and rejects altered projection and translation tables. Independent finite testing does not establish an unrestricted polynomial clock.

Next: investigate symbolic representations and certified compression of messages or repair predicates when separators have large rank; separate representation barriers from computational hardness. No new Lean declaration or P versus NP resolution.
