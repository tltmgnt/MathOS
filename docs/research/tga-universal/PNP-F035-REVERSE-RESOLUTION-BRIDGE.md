# MathOS TGA-PNP — backward resolution specification (F035)

25 November 2026. PNP_RESOLUTION_STATUS = OPEN.
This imports the reverse-engineered proof architecture as a research
specification, not a solution, novelty claim or authorization to publish.
Base: c6fcac63fd7ade7e6b4ce7d5df48608ae66f62a3, merged F034 research branch.
No production/main change. The AND/OR graph is in
mathos/research/tga_pnp_resolution_gap.py; run it as a module. Minimal
completion sets are relative to authored sufficient routes, not a
topological invariant of mathematical truth or a measure of progress.

## Final class-level target

Construct ONE uniform deterministic machine A deciding every encoded
3-CNF F. Prove A(F)=SAT iff F has a model and total bit-machine time
T_A(F)<=c*(1+|F|)^k for fixed c,k. Specify malformed encodings as well.
Cook–Levin and polynomial reduction to 3-SAT imply NP subset P; P subset
NP gives equality. A different sufficient route is a universal lower
bound: every correct deterministic SAT machine has no polynomial
worst-case bound. Lower bounds for one inference system, finite tests,
or failed heuristic search cannot give that conclusion.

## Backward certificate route

For an unrestricted sound checker C(F,pi), distinguish:

* Ordinary completeness: every UNSAT F has SOME accepted certificate.
* Polynomial completeness: there exist fixed c,k, for every UNSAT F
  there exists accepted pi with |pi|<=c*(1+|F|)^k.
* Efficient discovery: one deterministic generator with a known uniform
  polynomial cutoff finds an accepted certificate for every UNSAT F.
  In a bit model its output length is necessarily polynomial.
* Verify in total polynomial time in |F|+|pi|, accounting for every
  operation. Then bounded generation plus validation decides UNSAT;
  lack of a certificate implies SAT only under discovery completeness.
  Existing UNKNOWN must not be relabeled SAT.

Polynomial-size completeness and polynomial verification imply NP=coNP,
not by themselves P=NP. Ordinary completeness is weaker still. These
work packages overlap logically: efficient discovery already entails
polynomial existence. A direct polynomial SAT algorithm is an alternate
positive route without this architecture. Independent review is an
evidence/publication gate, not a premise of the mathematical implication.

## Status and evidence

- F034 unified byte-level acceptance and UNSAT soundness verified:
  PR #233, run 45613607279/job 139203196711.
- F034 capacity and unified selected checker ledgers verified on exact
  candidate heads, PRs #235/236 open at this snapshot, runs
  45622968605/job 139235874499 and 45622979373/job 139235721205.
- Front-end seven-coordinate ledger verified on 2ec90467652972fe26a459f750194c4274526d03,
  PR #237, run 45626656164/job 139248536651.
  For B combined byte length, reservations are
  (5235B,1046B+16,20B,1047B,21B,1536B,64B+6) for bounded implementation.
- Nine-coordinate integration initial run 45630291027 failed with
  elaboration recursion limit; local maxRecDepth repair a92790846ee3738bde4fc05e9ae7c84327afd040
  requires fresh strict replay. No theorem weakening or relaxed axiom gate.
- The preceding bounded parser rejects every expected byte stream longer
  than 1,000,000; its fixed list cap 100,000, decimal digit cap 128 and
  selected 512-bit representation cannot directly cover general SAT.
  This is an architecture obstruction, not a complexity-class separation.

## F035 work implemented in this branch (candidate)

ProctorUnboundedCodec removes fixed byte, decimal digit and list limits
with the same grammar and typed boundCheck. Arbitrarily sized Nat values
replace fixed-width comparison operands here. It proves candidate legacy
scanner success preservation, old byte-limit rejection and new byte
checker soundness. It does NOT assert complete legacy checker equivalence
on previously accepted bytes, or constant-time Nat operations.

ProctorUnboundedRoundtrip reuses original token encoders and proves
roundtrip for every typed formula and certificate envelope without list
size premises. Byte exactness assumes a successful tokenization into
the encoded tokens. Universal decimal encoder correctness and polynomial
bit-cost simulation remain open. Numeric list iteration uses manyAux
and Nat structural recursion; malformed declared counts require a
separate consumption/cost theorem, not a constant-cost assumption.

ProctorResolutionBridge closes the local rule converse: a parent shape
or pair of shapes satisfying the semantic membership conditions passes
the executable check. A same-parent weakening step copies a row; a
copy batch retains the complete frontier. Compiling a sequential checked
resolution step by prepending its derived row and copying all old rows
preserves the sequential Boolean check and final frontier, including
invalid traces. The candidate typed refutation bridge needs a sequential
checked trace ending in an empty clause; no universal trace existence
or polynomial size theorem is asserted. Typed copy pivot can be any Nat;
a valid boundCheck envelope additionally requires pivot in 1..n.
Proof overhead from repeated copying must be analyzed.

The decision adapter is total as a Lean function given a total generator,
and its UNSAT iff theorem assumes DiscoveryComplete explicitly. SAT iff
additionally receives a constructive satisfiable-or-unsatisfiable
alternative. No actual universal complete or efficient generator is
supplied. No complexity theorem follows merely from Lean termination.

36 candidate declarations (4 codec, 16 roundtrip, 16 resolution bridge);
15 control groups: 2 sequential traces, 4 positive certificate byte
fixtures, one 129-digit operand exceeding legacy cap, one 100001-row token
input exceeding list cap, five malformed inputs and two generator adapters.
Exact marker F035_RESOLUTION_BRIDGE_OK sequential=2 positives=4 digit=1 list=1 malformed=5 adapter=2.
Strict Lean 4.14.0 warnings-as-errors and explicit zero-axiom audit.
Fresh replay required; no local Lean execution.

## Remaining attack sequence

F035: verify this branch; establish universally correct unbounded wire
encoding, semantic binding and input-sensitive malformed-input parsing.
F036: establish variable-width resource ceilings in serialized bits.
Existing selected budget source suggests O(w B^4) comparison work and
O((w+1) B^3) selected lookup visits; derive actual inequalities from
aggregate masses, not independent maxima for nested groups. Candidate
only. Use adaptive compact indexing or prove variable-width bound.
F037: machine simulation with total costs including allocation, control,
structural traversal and integer arithmetic. Fixed-width theorems do
not automatically generalize.
F038: prove ordinary unbounded completeness via constructive finite
assignment splitting/resolution and compile checked sequential proofs.
Such a construction can be exponential; do not label it polynomial.
F039: investigate polynomial proof sizes or proof-system obstructions.
F040: construct and analyze deterministic polynomial proof discovery.
F041–F043: instantiate the decision bridge, total polynomial-time
machine theorem, classical class implication, and independent audit.

Do not set PNP_RESOLUTION_STATUS to SOLVED without actual unrestricted
resolution evidence. Every missing hypothesis remains visible.
