# A polynomial decision procedure for disjoint AND blocks with affine output coupling

**MathOS PNP-B006 | Cycle 6 | 24 November 2026 | Scoped use case complete; independent review not performed**

## 1. Problem and exact scope

For n disjoint pairs of Boolean input variables, let B_i be an explicitly given subset of the four possible assignments to pair i. Define y_i=a_i b_i. The only cross-block constraints are m arbitrary affine equations Ay=b over GF(2). Decide satisfiability and return a verified witness or an inconsistency certificate. The procedure below completes the use case PNP-AND-XOR, which avoids the exponential auxiliary-free projection of PNP-B005. It is not an algorithm for unrestricted SAT.

## 2. Correctness and certificates

Compute D_i={a_i b_i:(a_i,b_i)∈B_i}, storing one original allowed pair for each output. If any B_i is empty, return its index as an impossibility certificate. Otherwise D_i is {0}, {1}, or {0,1}. Add the equation y_i=d for each singleton domain. The original problem is satisfiable if and only if this augmented affine system is consistent: every original witness gives a solution, and conversely each solution can be lifted by selecting the stored pair for each output. Disjointness guarantees these choices never conflict.

Perform Gaussian elimination using the largest set bit as pivot. Store a provenance bitset representing the original and singleton rows summed to obtain every current row. If elimination yields the inconsistent equation 0=1, the provenance supplies an explicit certificate. Otherwise set free variables to zero and solve pivot values in increasing pivot order, since every nonpivot term in a row has smaller index. Return one lifted pair per block.

A separate verifier reconstructs singleton equations from the ORIGINAL local domains, checks witness membership and all original affine equations, or verifies the claimed row sum is exactly 0=1. For empty-block certificates it checks the original domain is empty. This verifier does not trust the solver's intermediate state. It rejects malformed row references, duplicate references, and altered witnesses.

## 3. Total bit-complexity bound

Let r≤m+n be the number of augmented rows. An elimination row uses n coefficient bits, one right-hand-side bit and r provenance bits. Each insertion performs at most n pivot XORs, since the largest nonzero coefficient index strictly decreases after every reduction. Thus at most rn row XORs each using O(n+r) bit operations are needed. Initialization, pivot lookup, back substitution, certificate extraction and verification are polynomial; a conservative bound for this explicit dense-bitset implementation is O((n+r)^3) bit operations and O((n+r)^2) storage, including provenance. These bounds use the input length with explicit block domains and affine rows. There is no exponential projected CNF, and no reliance on a unit-cost arithmetic assumption for unbounded integers.

## 4. Executed end-to-end controls

All 15 nonempty local domains on each of three blocks were combined, yielding 3,375 instances with two fixed coupling rows. An independent exhaustive assignment enumerator agreed with the solver in every case: 2,121 satisfiable and 1,254 unsatisfiable. The separate verifier accepted every result. An empty-domain control was rejected as unsatisfiable; altered SAT and UNSAT certificates were rejected. The 16, 64, 256 and 1,024-block cases tested both a consistent global parity equation and contradictory global parity equations, with verified output in every case. The contradictory pairs required one row XOR; the consistent single-row cases required none. These large cases are deliberately structured, not general complexity benchmarks.

## 5. Completion and remaining boundary

The exact reduction and bit-complexity argument, executable solver, independent certificate-checking function, and completed regression run meet the internal use-case exit criteria. Independent human mathematical review is not performed and is nonblocking under BREAKTHROUGH_USE_CASE_POLICY.v1.json. PNP.sat_runtime remains open: arbitrary shared variables, nonlinear coupling and general SAT are outside the proven scope.

## Reproduction

Pinned source: dac9239e4bd2787e373a11322e4d8dbb3dd986d2. Execution: https://github.com/tltmgnt/MathOS/actions/runs/45374313360. Evidence: cycle6-evidence.json.

Run: python -m unittest discover -s tests -p 'test_breakthrough_cycle6.py' -v

Run: python -m mathos.research.breakthrough_cycle6

References: MathOS PNP-B004 and PNP-B005; elementary GF(2) Gaussian elimination. No claim of literature novelty or Millennium solution.
