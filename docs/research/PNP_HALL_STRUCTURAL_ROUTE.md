# Hall structural certificate route — isolated research candidate

## Verified predecessor and obstruction

CI run 46134170709 for PR #284 reproduced the original 24/24 and
scaled random 16/16, but integrated v16 solved only 11/14 structural
cases (51/54 total). The six long-chain cases were recovered by fallback.
The three unresolved cases were pigeon_5_4 (UNSAT), pigeon_5_5 (SAT),
pigeon_6_5 (UNSAT). Full standalone search solved the first two, so
v16's quota can sacrifice coverage even when the stronger full-budget
search would succeed. Resolution and learning were never attempted
on that structural suite. The v12 full versus one-third ablation
lost seven original decisions (18 versus 11, five SAT and two UNSAT);
this is direct evidence of the resource-allocation effect, not an
exhaustive causal account of the original v14 hybrid.

## Structural mathematical certificate

For disjoint nonempty positive clauses G_i, every satisfying assignment
must choose a true variable from each G_i. Partition those variables
into resources R_j such that for any u,v in the same resource but
different groups, the original CNF contains the binary clause
(-u OR -v). Therefore any satisfying assignment induces an injection
from groups into resources, by choosing one true variable per group.
If a subset of k groups has all its variables covered by fewer than
k resources, no such injection exists (finite pigeonhole principle).
The entire original CNF is then UNSAT. Extra clauses cannot invalidate
the contradiction. The verifier checks original clause indices,
disjointness, complete resource coverage, every required cross-group
binary incompatibility, and strict cardinality deficiency. It does
not trust the matching algorithm, reference label or benchmark name.

The proposer greedily extracts disjoint groups, builds conflict
components and splits any non-complete component into singletons.
It uses iterative augmenting paths. A failed augment yields the
reachable deficient subset; successful matching proposes a concrete
Boolean model, accepted only by checking every original clause.
Greedy extraction, incomplete clique recognition, polarity restrictions
and the choice of one matching are incomplete. Failure to find a proof
does not decide anything. This is a known matching/Hall reduction,
not a new mathematical theorem, a general SAT reduction or P=NP.

## Controlled implementation

No existing engine or test changes. The route is gated by at least two
nontrivial positive clauses and a negative binary incompatibility.
Eligible inputs get one fifth of the configured work and time; unused
resources pass to unchanged v16. Ineligible inputs receive full v16.
This is an experiment, not equal-budget dominance by theorem. Input
feature scanning and ordinary Python overhead are not charged as
work. Explicit checkers are independently replayed; timing and search
counters are observational.

Local standalone Hall core with the existing Budget/validate contract
transcribed solved all six prior pigeon cases and seven new structural
controls, including 12-by-11 UNSAT and 12-by-12 SAT, within 20,000
steps per case. All 13 certificates replayed after JSON roundtrip.
On 2,400 seeded small general CNFs the core credited 267 decisions
without reference disagreement. These are local route-only results,
not integrated portfolio measurements; the seven scaling cases are
now public development evidence, not blind holdout.

## Evaluation and gate

The fixed manifest has 73 cases: 54 previous stress cases, seven
additional scaling controls and 12 newly seeded mixed-constraint cases
(seed 181902). Compare frozen v16 with Hall-first, both at 100000 work
steps and 5 cooperative seconds. Recheck upstream evidence, reference
labels, every credited certificate, work accounting and summary.
Small instances use independent bit-vector exhaustive reference;
larger pigeon and chain instances use checked generator arguments.
The gate retains all prior baseline decisions, requires 24/24 original,
16/16 scaled random, 14/14 structural and 7/7 scaling, and specifically
requires recovering the three previously unresolved pigeon cases.
All mixed-case misses are reported; none may lose a baseline decision.
No v18 or external industrial comparator is included in this experiment.
No third-party blind validation or unrestricted performance claim.
Lean checks only the abstract exclusivity/injection and conditional
collision bridge, not finite cardinality arithmetic or Python code.

Run with the previous audited source/scheduler/failure artifacts:

    python -m mathos.research.pnp_hall_frontier --benchmark source.json --scheduler scheduler.json --failures failures.json --checkpoint hall.json
    python -m mathos.research.pnp_hall_frontier --benchmark source.json --scheduler scheduler.json --failures failures.json --audit hall.json --gate

Do not merge before integrated evidence and review. Stress and mixed
failures, if any, remain explicit. No changes to the v18 integration.
