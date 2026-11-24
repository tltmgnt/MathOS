# PNP-F003 — Total recursive Gaussian elimination over GF(2)

**MathOS | Specialist formal research | 24 November 2026**

## 1. Exact theorem

For every natural number n and every finite list R of Boolean coefficient rows with right-hand sides, define admissible witnesses as Boolean lists x of length exactly n. The equation semantics are the zero-padded dot product from PNP-F002. The new Lean solver is a total function returning a dependent result: either a concrete list x with proofs that its length is n and every row holds, or a proof that no such x exists. The usual n-variable finite system is included by encoding every row with n coefficient bits. Longer coefficient lists are truncated by the stipulated n-bit assignment semantics. No claim is made about arbitrary-length assignments to a fixed n-variable system.

The theorem witness_spec audits the extracted option-valued interface. The theorem none_iff identifies the no-witness result with nonexistence of an n-bit satisfying assignment. This is a general constructive decision result, not an inference from finitely many examples.

## 2. Algorithm and proof

At dimension zero the only admissible witness is the empty list. Its dot product with any row is zero. The system is satisfiable exactly when all right-hand sides are false. A recursive base decision checks this condition.

At dimension n+1, scan the rows for a first coefficient equal to true. The scan returns either a pivot with evidence of membership and nonzero head, or a proof that every row has zero head.

No-pivot branch: drop the first coefficient of every row, solve the dimension-n problem, and prepend false to a returned witness. The zero-head lemma shows that either leading bit has no effect. In the impossible branch any alleged original witness would yield a satisfying tail, a contradiction.

Pivot branch: retain the chosen pivot in the row list and clear every row with first coefficient one using XOR with the pivot (including the pivot itself). Drop the cleared first coefficients and solve the dimension-n problem. If a tail x exists, reconstruct the first bit as pivot.rhs XOR dot(tail(pivot.coeff),x). It satisfies the pivot, and the verified F002 row-replacement and reduction equivalences show that every original row holds. If the reduced system is impossible, any alleged original witness would satisfy the pivot because the pivot belongs to the original list; its tail would then satisfy the reduced system, a contradiction.

Both recursive calls strictly decrease n, and row scans and base checks recurse on finite lists. Hence the Lean definition is structurally terminating. All witness and impossibility proof fields are checked by the kernel. The algorithm does not search all Boolean assignments.

## 3. Executable row-provenance certificate generator

The companion Python implementation follows the same low-coordinate pivot strategy but uses explicit-width integer bitmasks. Initially attach the unit provenance bitset 2^i to row i. At each row XOR also XOR its provenance. Dropping a zero first coordinate loses no information about that coordinate. Inductively the XOR of original rows indicated by provenance equals the current row with the already-eliminated coordinates restored as leading zeros. At dimension zero, if any right-hand side is one, the provenance certifies 0=1. Otherwise back-substitute stored pivots and return a witness.

The independent checker uses the original rows only, recomputes the indicated XOR or checks the returned witness, rejects duplicate or out-of-range references, and enforces the exact dimension. This Python generator is tested against exhaustive assignment enumeration and large structured cases. The invariant argument is mathematical prose; there is not yet a Lean proof of correspondence to the Python code, nor formal generation of XOR provenance in the Lean solver. The Lean unsat result is a proof of nonexistence, not a serialized original-row XOR certificate.

For m rows and n columns, the implementation retains m rows, performs at most nm row XORs, and each packed row has n coefficient bits plus m provenance bits. A conservative dense representation bound is polynomial in the explicit dimensions; a formal total bit-cost theorem is still open. This is not a unit-cost claim for arbitrarily large integers.

## 4. Verification boundary and specialist topology

Recheck PNP-F001 projection and PNP-F002 row calculus in the same run. The new formal source extends the checked GF(2) module without changing its definitions; check scan, solve, witness_spec and none_iff using pinned Lean 4.14.0 with warnings as errors and the empty transitive axiom policy. The workflow records exact exit status and source/log digests, as well as all finite controls. Successful formal replay is required before accepting the solver iteration node.

The previous combined iteration/certificate gap is refined into total decision and witness reconstruction, and formal construction of original-row provenance certificates. Other remaining dependencies are refinement to the PNP-B006 Python implementation (including projection, affine singleton encoding and highest-bit pivot correspondence), and a formal bit-complexity theorem. The specialist route remains blocked. Neither this result nor completion of that restricted route resolves unrestricted SAT or P versus NP. All 14 canonical research obligations are unchanged.

## 5. Reproduction and scope

Baseline b03f162d3bc428a69bc1fd832c193da626271a3a. Prior exact sources: docs/research/breakthrough/PNP-B006.md; formal/ProctorPNPProjection.lean; formal/ProctorGF2.lean. New solver extension: formal/ProctorGF2Solver.lean, combined with its exact prior module by the replay tool. Run python -m unittest discover -s tests -p 'test_tga_proctor_gf2_solver.py' -v; then python -m mathos.research.tga_proctor_gf2_solver --output-dir artifacts/gf2-solver. The replay generates standalone DOCX and evidence. This is deterministic specialist research, not a live-model research run. No literature novelty, external mathematical review, educational validation or global proof promotion is asserted.
