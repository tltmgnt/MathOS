# PNP-F035/F038 — Ordinary typed refutation completeness

PNP_RESOLUTION_STATUS = OPEN.

Based on exact verified F035 head 7c38746dbb63e82dfe781c6cbe32ff6d483bebe7
(PR #238, run 45634100503, job 139274794944: 36 zero-axiom
declarations, 15 control groups). Candidate adds a constructive
finite-splitting existence argument for unrestricted typed CNFs.
It does not remove the remaining byte-encoder or bit-machine gaps.

## Candidate mathematical theorem

For every finite Formula f (arbitrary Nat variable identifiers),
(there exists p : ProctorUnifiedReplay.Proof with check f p = true)
if and only if no assignment satisfies f. No premise on variable
count or clause width. This is the typed check, not boundCheck or
checkBytes, and not a polynomial proof-size theorem.

Proof: finite clauses and formulas admit a constructive satisfied
or falsified-row alternative for a given assignment. Collect every
literal's variable identifier in the original formula, allowing
duplicates. Split over the list. At a leaf, UNSAT supplies an
original false row whose literals all belong to the blocking clause
(the complements of assigned values). A same-parent weakening
step derives that blocking clause. At an internal split, derive
(v,true)::path under assignment v=false and (v,false)::path under
assignment v=true. Keep both child derivations in the frontier;
resolve them to path. At the root path is empty. Reach preserves
every previous row; convert the reach witness into a sequential
checked trace, then apply the verified frontier-copy compiler and
empty-clause terminal. Soundness supplies the converse.

The construction has an exponential tree in the number of literal
occurrences if duplicates are not removed. Even deduplicated
splitting can be exponential in distinct variables. The theorem
establishes ordinary proof existence only, not efficient discovery.
The proof uses Prop-valued existence; executable prototype controls
do not establish its computational refinement or cost. Typed
weakening uses pivot 0, and compiler copies use pivot 0, so a
separate validProof identifier-range bridge is required for
serialized boundCheck envelopes with positive identifiers.
No claim of novelty for classical resolution completeness.

## Verification

19 candidate declarations, explicit zero-axiom audit and strict
Lean 4.14.0. 24 executable control groups: 16 subsets of four
two-variable full clauses, four one-variable subsets, two empty
cases, a wide sparse identifier and a zero-identifier typed case.
Prototype performs finite splitting and checks the generated
sequential trace, frontier and compiled typed proof against finite
truth-table controls. It is not a formally refined generator.
Marker F035_ORDINARY_COMPLETENESS_OK pairs=16 singles=4 empty=2 sparse=1 zero=1.
Fresh exact-head CI required. Main unchanged.

## Gap implications

If verified, ordinary typed certificate existence is discharged.
Still open: valid bound envelopes, universally correct decimal wire
encoder, unbounded decoder cost, selected polynomial ceilings for
variable width, total machine refinement, uniform polynomial
certificate-size bound and deterministic polynomial discovery.
Even polynomial certificate existence plus polynomial verification
would imply NP=coNP, not by itself P=NP.
