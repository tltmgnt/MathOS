# F038-REX-023A — Exact descriptor quotient and original selector-stage audit

MRA-X 2.0 + RE-X; MRA-X Omega Phase III. Parent 1b4f2ee331403a5380acc941dcad9d66375746e6. Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

## Scope

This bounded cycle audits the complete B6 original-format witness descriptor, without changing its computational path or broadening its fixed seven-bag normalized family. New work: (1) remove graph-unreachable states and compute the coarsest stable transition partition with halt distinguished, (2) emit an actual smaller original-format descriptor, (3) verify the exact clock and witness interface, (4) compare the descriptor's individual budget with the original schedule, and (5) replay the small original scheduler in native Python. The full large-descriptor native Python gate is committed but not executed; no full universal stage at the enormous slot indices is enumerated.

## Exact transition quotient

Let T(s,a)=(t,w,d) be an original B6 transition for read symbol a in {0,1,blank}. Compute the graph-reachable set from state zero by traversing all three possible symbols; this is an overapproximation of tape-realizable state paths, not a semantic reachability proof. Include halt separately even if unreachable. Initial partition is by the three (write,move) pairs, with halt in a singleton. Refine by predecessor sets for each symbol using a worklist and inverse adjacency. A split places predecessor members and nonmembers in different blocks; queued splitters are updated, otherwise enqueue the smaller split part. At stability any two states in a class have identical writes/moves and equivalent successors on each of the three symbols. Since every split is forced by a finite distinguishing read sequence, standard partition refinement yields the coarsest such partition on the reachable graph. This does not establish the smallest tape machine computing the same function, nor minimum description among unrelated algorithms.

Renumber initial class 0, halt last. Let f map reachable original states to class numbers. Verify for EVERY reachable nonhalt state s and read a:

    Q(f(s),a) = (f(t),w,d) whenever T(s,a)=(t,w,d).

At runtime induction on steps now proves exact tape contents, head location, halt/continuation, and clock equality for every finite input, including malformed and out-of-family inputs, and every cutoff. No phase metadata or additional runtime interpreter is inserted. The quotient description is encoded in the same original grammar and decoded entry-for-entry before replay. This is a constructive argument checked against the actual tables, not mechanized proof certification.

Measured result:

| Quantity | B6 | Quotient |
|---|---:|---:|
| Nonhalt states | 278200 | 103393 |
| Transition entries | 834600 | 310179 |
| State-address bit width | 19 | 17 |
| Serialized bits | 19474004 | 6617156 |

278199 graph-reachable nonhalt states, one unreachable; 70 initial blocks including halt, 103324 splits, 310182 splitter-symbol work items, 834597 transition homomorphism checks. Removed 174807 nonhalt states (62.84%); removed 12856848 descriptor bits (66.02%). The table check is exact, not a sample. Two small synthetic quotient controls exercised merging, unreachable states, and separating states that differ only in halt timing. Halt remains distinguished even if unreachable. Compression changes no physical transition counts.

## Executed quotient replay

| Fixture | m | Original raw bits | Physical transitions | Output |
|---|---:|---:|---:|---|
| forced |2|37914|44654867|31-bit valid witness |
| multirow |2|37914|46090469|31-bit valid witness |
| nonempty inconsistent bags |2|37914|54399245|blank UNSAT |
| outside-path SAT |2|37914|7687297|blank structural refusal |
| mixed ranks |3|161851|522655657|50-bit valid witness |

Five completed quotient runs, 675487535 transitions. All matched inherited exact halt clocks; three SAT outputs exactly matched the expected original witnesses and passed the original JS clause verifier. Outside-path input has an explicitly verified original model, so blank refusal is not an UNSAT result for the unrestricted domain. Exact forced halt budget and one-step-short timeout checked again, plus original n=1 blank refusal. Domain-four forced mixed ranks full replay was attempted but the tool execution limit was reached, so no completion is claimed. A separately executed 300000000-transition bounded run returned TIMEOUT exactly (raw length 428744, final simulated head 54581, span 429667). This bounded run is not an algorithmic failure or a measured full halt clock. Principal completions and bounded run total 975487535 transitions; excludes repeated controls and interrupted tool call.

## Native original scheduler replay

The exact-parent original source blob f038_unrestricted_universal_search.py is 751ff6a6d405a28e3d0df0af8b26cff0e9cef468; the pool source blob is 012ba69f4882a361b46f7c75cdcf070bb7c77d46. Direct container GitHub access failed DNS resolution, so the retrieved original scheduler core (BUILTINS through first_bad), pool function, and encode_tm/controls were transferred as source text to a native Python process. Byte lengths and FNV-1a checksums matched the retrieved snippets: (2999,2212533000), (215,1219568115), (996,218519402). These are transfer regression checks, not cryptographic attestation. The external require helper was replaced by an equivalent assertion/raise check; the repository's import orchestration and finite-CNF fixture were not run. The original stage, descriptions, run_program, tape_run, valid and codec bodies were executed unmodified.

Native results: all 256 two-variable selectors, stages 0..6 (1792 stage calls), 63232 binary description launches within these stage calls, 11008 built-in launches, five original controls passed. Additional universal() calls verify the first-success stage but their launches are excluded from the 63232 count. Solved selectors by stage [0,32,78,78,95,95,95]; bad SAT selectors [95,63,17,17,0,0,0]; first success histogram [0,32,46,0,17,0,0]. The smallest generic descriptor (one state) has 20 bits, so stages 0..6 admit no generic descriptor; the separate codec controls exercise generic tape_run and timeouts. The full large quotient descriptor was not transferred to the native environment. A native repo-import regression gate generates the quotient, roundtrips the original decoder, calls tape_run and valid at the forced clock, checks one-step-short and n=1 refusal. Its execution remains unconfirmed.

## Exact original stage ledger

Original schedule s_k(n)=k ceil(log2 L(n)), with L=n+1+2n^2+8*binom(n,3). For a particular descriptor of length ell and a verified witness execution time t>=1, the exact minimum stage at which that program's allotted clock suffices is s_d=ell+ceil(log2 t). This is not necessarily the first successful universal stage. A blank halt has no witness slot, even if its halt budget suffices. The minimum coefficient for that observed program execution is ceil(s_d / ceil(log2 L)). The s3 column is a studied cutoff, not an established universal deadline; the original unrestricted equivalence asks for existence of some integer k.

| m | L | ceil(log2 L) | s3 | B6 witness slot | quotient witness slot | quotient min k |
|---:|---:|---:|---:|---:|---:|---:|
|2|37914|16|48|19474030|6617182|413574|
|3|161851|18|54|19474033|6617185|367622|
|4|428744|19|57|unmeasured|unmeasured|unmeasured|

At all measured dimensions the quotient is not even listed by s3. Listing alone at s3 requires ceil(log2 L)>=2205719, hence L>2^2205718. Clock sufficiency is stronger. These statements concern this descriptor only.

Important countervailing evidence: the original interpreter has a built-in '000' of length 3, exhaustive Boolean search with charged clock 2^n. It guarantees a verified witness on every SAT input if s>=n+3. Thus at m=2 and m=3 the original universal stage s3 already succeeds on every satisfiable input (including outside the fixed path) by this built-in, despite neither large descriptor being listed. This is a mathematical budget implication, not execution of 2^31 or 2^50 assignments. At m=4,5, n+3 is 72,91 versus s3=57,60. For all m>=4 the exhaustive built-in is not budget-eligible at s3: each m increment increases n by 19; L(n+19)<8L(n) for n>=31 by termwise factor bounds, so ceil(log2 L) increases by at most 3 and s3 by at most 9. Arithmetic checked n=19m-7 for 99 dimensions m=2..100 using native Python. This does not establish failure of ANY universal stage for m>=4 because other descriptions may succeed.

## Asymptotic versus finite admission

By B6's constructive resource bound and exact quotient equivalence, a fixed C exists such that on every supported SAT input of sufficiently large length L, t(L)<=C L^2 (log2 L)^2. For the fixed quotient ell=6617156, the budget at s3 satisfies 2^(s3-ell)>=L^3 / 2^ell once the program is listed. Since L/(log2 L)^2 tends to infinity, eventually L >= C 2^ell (log2 L)^2, and s3 gives enough time on the entire supported SAT family at those lengths. This is an eventual restricted-family cubic-stage admission theorem conditional on the inherited constructive resource proof, not a numerical crossover bound: C has not been made explicit. Small dimensions m=2,3 are separately admitted by the built-in. The intermediate finite range has not been covered at s3. A larger fixed k could absorb the finite exceptions for this family, but that does not cover other normalized scopes or unrestricted SAT. The same reasoning applies to B6 before compression; the quotient improves description overhead, not time exponent. No claim that k=3 solves all SAT or that the failure predicate is satisfiable at untested stages.

## Governance / next mission

ADVANCE exact clock-preserving compression, original native small scheduler regression, and separation of observed program slots from universal-stage success. PRESERVE B6 and original interpreter grammar. DECOMPOSE remaining native large replay, explicit finite constants, intermediate cutoff coverage, and general admitted width-two structural coverage. RETIRE inferring stage failure from descriptor exclusion or asserting minimum algorithm size from transition quotient. STOP after bounded evidence. All four global routes and six formal Omega obligations remain open.

Next F038-REX-023B: investigate structural generalization from the fixed consecutive path to arbitrary nine-group width-two decompositions, using the already-established host width-two recognition theorem and an input-driven fixed physical plan. First verify a physical structural-scope summary and exact decomposition selection, including legal treewidth-one outside-path counterexamples and treewidth-three obstructions. Preserve exact selector/clock semantics and do not claim full coverage before physical replay.

Reproduce:
```sh
for suite in small three four-bounded; do
  node mathos/research/f038_rex_stage_audit.js "$suite"
done
node mathos/research/f038_rex_stage_audit.js --descriptor > /tmp/quotient.desc
python -m mathos.research.f038_rex_stage_native /tmp/quotient.desc
# Optional expensive full m=4 replay: node mathos/research/f038_rex_stage_audit.js four
```

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
