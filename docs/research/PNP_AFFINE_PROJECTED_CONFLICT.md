# Affine-coordinate conflict learning — isolated candidate

## Predecessor evidence

PR #298, run 46137561141: evidence and formal jobs passed.
XOR portfolio 153/153 vs conflict portfolio 148/153, no paired
losses; new graph mixed 8/8 vs 4/8 and pure graph 8/8 vs 7/8.
Standalone XOR missed graph_32_0_1, graph_48_0_1, graph_64_0_1
(SAT), recovered by existing fallback. On mixed graph cases,
candidate counted work 53509 vs 420661, observed call time
27.193 vs 143.816 ms. Parity-cycle certificates grew from
1460 to 7510 bytes despite lower work. No blind validation or
uniform speedup claim. These are synthetic finite results.

## New exact residual projection

Use existing bounded implied XOR extractor, Gaussian provenance,
and existing CDCL. If the subsystem is inconsistent, use existing
dual replay. Otherwise solve pivot variables as affine forms of
free variables by echelon substitution. Each form carries an
explicit subset of original equation witnesses. Remove only cited
source clauses. Encode affine forms required by residual clauses
with cached XOR gates and signed literals (and a checked constant).
Run CDCL on the resulting free-coordinate/gate CNF. Lift SAT to
original variables and directly check all original clauses.

For projected UNSAT, the checker independently verifies source
truth-table equivalence, XOR provenance of every pivot, disjoint
pivot/free support, and that substituting forms satisfies every
source equation identically. It reconstructs the residual CNF using
deterministic variable allocation and a truth-table gate rule
rather than the proposer's static XOR clauses, then replays RUP
on that formula. Soundness: every original model yields a model
of the residual/gate CNF by restricting to free variables and
evaluating gates; contradiction of the latter excludes the former.
The checker shares the deterministic compiler and data layout;
not a completely separate compiler or machine-checked full proof.
SAT proof is a direct model; internal learned clauses on SAT runs
are not exported as certificates. No native XOR-CDCL inference
or online Gaussian propagation is claimed.

Gate width <=4, row count <=1024, repository projected variable/
clause/literal caps and cooperative work/time bounds. Dense forms
can cause gate blowup or replay exhaustion. UNKNOWN remains
UNKNOWN. Experimental route receives 40% of configured budget
on larger mixed parity candidates without Hall eligibility;
fallback gets unused resources. Ineligible cases receive full
unchanged predecessor. No dominance theorem; overhead outside
counted budget remains. No prior source or test changed.

## Protocol

171 cases: 153 archived, six fresh mixed graph controls and 12
seeded random base CNFs lifted through two affine copies per
variable, fixed z=0, random distribution of literal occurrences.
These lifted cases have a constructive equivalence to the small
base CNF whose reference is exhaustive; graph labels use the
existing planted witness/parity argument. Seed 192106.
Four matched arms (100000 work steps/5 cooperative seconds):
XOR portfolio, standalone XOR, standalone projected CDCL, new
portfolio. Require all archived decisions, no paired losses,
three archived standalone mixed SAT recoveries vs standalone XOR,
and at least one integrated projected RUP refutation on the
lifted group. All misses, coverage gains, work, observed time,
stored bytes and route contributions remain explicit. The strict
gain gate compares the standalone routes for the known misses,
not a claim that the predecessor portfolio failed those cases.
Public synthetic controls, no independent operator or external
industrial comparator.

Lean checks local Boolean substitution, semantic contradiction
transfer, and the four-clause XOR gate truth table only. Full
Python checker formalization remains open. New integrated and
local outcomes not yet measured. Keep draft before review.
