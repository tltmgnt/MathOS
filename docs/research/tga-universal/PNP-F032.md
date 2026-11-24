# PNP-F032 — Native syntactic XOR recognition and GF(2) certificates

PNP_RESOLUTION_STATUS = OPEN. Baseline PR #149 merged into the F031
bit-cost branch at 376d6e42d8e6610437362caf161870b9777dcd1b. CI run
45442457156, job 138617041990, passed five tests, 600 sparse random
cases (317 UNSAT resolution extractions) and 14 cubic Tseitin
resolution replays. Evidence artifact 14943234359.
https://github.com/tltmgnt/MathOS/actions/runs/45442457156/job/138617041990
At 16 vertices, seeds 11/29 required 959/1023 dynamic nodes and
3391/8255 extracted resolution lines. These finite samples are not
certified expanders.

## Implemented

This is a new native implementation, not a port of Claude's missing
sources. Accept arbitrary finite signed CNF with a binary declared
variable count. Normalize repeated literals and skip tautologies.
Only exact parity blocks on 1–5 distinct variables are recognized.
Group original clauses by identical support S. A non-tautological
clause with that support forbids exactly one assignment to S: bit
x_v=1 precisely when the literal on v is negative. If the group
contains all 2^(|S|-1) assignments with parity different from b,
their conjunction is exactly XOR(S)=b. Keep original clause indices,
one per required pattern. Detect both parities when both occur.
Unrecognized clauses impose no assumptions.

Compact the union of recognized supports (never allocate by declared n)
and reuse F003's certificate_solver and verify_result, rather than
reimplementing Gaussian elimination. If the affine subsystem is
consistent, return UNKNOWN even when the original CNF is SAT.
If inconsistent, return only selected original-clause parity blocks
whose XOR is 0=1. A direct empty-clause certificate is also supported.

## Certificate semantics and replay

The outer verifier does not call the syntactic detector, its signature
routine, the affine solver or its bitmask verifier. For each selected
block it checks canonical support, unique in-range original indices,
one non-tautological clause per forbidden assignment, and enumerates
all at most 32 assignments on that support to check exact equivalence
to the claimed parity. It then XORs supports using symmetric difference
and XORs the right-hand bits. Only an empty support with right-hand
side 1 is accepted. If the CNF had a model, it would satisfy every
selected block and hence every corresponding equation, contradicting
0=1. This is a mathematical soundness argument, not executable
kernel refinement or independently authored review.

## Complexity

Let L be explicit CNF encoding length, d the number of detected
equations and r the number of distinct recognized variables. With
width fixed at five, the grouped-pattern search and certificate
verification use polynomial work in L and explicit proof size
under ordinary list-based implementations. The existing GF(2)
solver uses at most rd row XORs, each over coefficient/provenance
bit vectors of O(r+d) bits. The counter counts row XORs, not bit
steps; initialization, scanning, shifting, back substitution and
output also have polynomial bit cost for compact explicit rows.
This is a scoped polynomial-time UNSAT preprocessor, not a total
SAT decision or a formal machine-transition bound. Selected
blocks use at most 16 original clauses per row. Original sparse
ID bit lengths are charged in L; no loop over declared n occurs.

## Controls and acceptance

3,000 seeded random formulas with sparse IDs and injected parity
contradictions, brute-force soundness checks, all widths 1–5, missing
patterns, duplicates, tautologies, width-six UNSAT negative control,
tampered blocks and a three-row dual. Sixteen seeded cubic Tseitin
odd-charge controls at 4 through 400 vertices, plus even-charge
negative controls; record row counts and row XORs, not unmeasured
runtime. A connected odd-charge graph requires all vertex equations
in any XOR contradiction because every edge belongs to its two
endpoints; a selected vertex set has zero boundary only if empty
or all vertices. Summing all rows gives RHS 1. These finite controls
are distinct from the prior resolution lower bound and require actual CI.

## Formal status and remaining work

F002–F005 provide existing GF(2) semantics, constructive solver and
dual certificates in Lean. This new CNF-to-parity bridge and Python
implementation have not been kernel-refined; no new Lean theorem or
independent review is claimed. Strict existing gates remain unchanged.
The syntactic detector is deliberately incomplete. Gate-obfuscated
parity, certificate-producing bounded variable elimination, a formal
CNF extraction bridge and machine refinement remain open. Original
scratch files and logs remain unavailable. No P vs NP promotion.
