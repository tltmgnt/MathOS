# Partial affine subsystem certificates — isolated research candidate

## Verified predecessor

PR #291 completed both evidence and formal jobs, run 46136400147.
Conflict portfolio achieved 129/129 vs Hall 105/129 and standalone
CDCL 125/129. All 24 new random transition cases gained (15 SAT,
9 UNSAT), no paired losses. Random-transition counted work: Hall
2293224 vs candidate 129427; observed call time 763.108 ms vs
48.055 ms. Parity cycles already solved by Hall and CDCL: 8/8
each, so they establish an efficiency question, not a coverage gap.
Candidate credited 40 CDCL decisions and eight nonchronological
jumps on the random-transition group. The standalone CDCL missed
four structural cases; retaining Hall is useful. All synthetic,
public development evidence. No industrial or asymptotic claim.

## What changes relative to existing algebra

The repository already has v7 whole-formula affine/bijunctive
recognition and Gaussian provenance, plus bounded conditioning.
The new route extracts **implied** XOR equations from subsets of
an arbitrary original CNF, without requiring exact whole-formula
affine equivalence. For a width <=4 scope, if every assignment
violating parity b is blocked by a cited original clause, the
scope equation follows. Extra non-affine clauses are retained.
Duplicate and tautological clauses cannot establish an implication
without covering the required wrong-parity assignments.

Gaussian elimination over GF(2) records a subset of input equations
whose XOR has zero left side and RHS one. The independent checker
enumerates all wrong-parity local assignments against cited original
clauses and verifies cancellation and odd RHS. It never calls the
extractor, elimination, or graph generator. A consistent system
does not imply SAT for mixed CNF. Only a model satisfying every
original clause is credited; try the zero-free particular solution
and bounded enumeration when active free dimension <=12. Exhaustion
or failure to lift a model is UNKNOWN. No assertion of completeness,
novel theorem, polynomial general SAT, or P versus NP result.

## Protocol

Frozen predecessor 129 cases plus 16 connected cubic graph parity
encodings (cycle plus antipodal matching, 20/32/48/64 vertices,
SAT/UNSAT and pure/mixed), and eight seeded small mixed CNFs.
Signed graph SAT references are planted models satisfying appended
clauses; UNSAT follows from each edge occurring twice in the XOR
of vertex equations and a single flipped RHS. This is a constructed
reference, not exhaustive enumeration. Small mixed cases use existing
independent bitset reference. Seed 192004; public synthetic manifest,
not an external blind test. The graph mixed SAT witness is not passed
to the solver; limited nullspace search may miss it.

Compare frozen conflict portfolio, standalone XOR and candidate
under 100000 work steps/5 cooperative seconds. Candidate probes
only active>16 with two plausible width 3–4 parity scopes and no
Hall gate; takes one quarter of configured budget, then passes
unused resources to unchanged predecessor. This gate is conservative:
mixed graph instances may trigger Hall eligibility accidentally and
skip XOR. Expose such misses, route contributions, timing, work and
stored certificate bytes. No paired loss, retain all 129 archived
decisions and strict new graph coverage gain are required. All
credited certificates are replayed after report serialization.
Feature scanning, input checks and independent outer audit are not
fully charged; work counters are route specific and observed.
No claim of equal-budget dominance or optimal allocation.
Lean checks local Boolean row addition and contradiction only,
not the full cardinality of proof provenance or Python checker.
No existing solver/test changed. The separate v18 integration is
not modified. Integrated results pending; no new outcome claimed.
