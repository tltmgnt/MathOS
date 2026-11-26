# F038 / unrestricted route — cubic-stage exclusion and a planted-density obstruction

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Parent 49c5a2f451fc9fda4ccbec993630047540cf19c6 exact-head Proctor: https://github.com/tltmgnt/MathOS/actions/runs/45741475515 (success). Six parent workflows passed at inspection; TOPO-406 was still running.

## Objective and result

Return to the actual cubic stage on the unchanged universal machine U, rather than another discovery or compiler theorem. Earlier finite cubic examples used unique pins and independently added satisfied ternary clauses to generate enormous families. Can the dense redundant-clause approach supply bad instances at unbounded lengths? We prove a necessary structural condition for ANY satisfiable cubic-stage residual at all sufficiently large n, and a strong upper bound on the failure probability in the full planted ternary-selector distribution. This rules out using mere dense redundancy or naive uniform planted sampling as an asymptotic existence proof. It does not rule out a rare or deliberately structured hard selector, and does not establish unbounded cubic failure or a polynomial SAT cutoff. No new machine or restriction of the scheduled competitors is introduced. Seven MRA-X roles are authored local records. No novelty claim for elementary planted recovery or tape simulation.

## 1. A fixed witness algorithm on the original full selector tape

Recall N=2n+4 binom(n,2)+8 binom(n,3), L=n+1+N and s_3=3 ceil(log2 L). The actual selector pool is ordered by width, lexicographic support, and lexicographic signs with negative before positive. The last 8 binom(n,3) bits therefore consist of eight-bit blocks, one per three-variable support. Call a support complete if exactly seven of its eight bits are one. The omitted clause has exactly one falsifying assignment on that support. Every satisfying assignment of the selected formula must have exactly those three values: the other seven local assignments each falsify one of the seven selected clauses. If all eight are selected, there is no satisfying assignment. If complete supports disagree on any common variable, there is no satisfying assignment.

Let u(p) be the number of variables not covered by any complete triple. Set b(n)=floor(log2(n)/4). A fixed algorithm reads the original unary header and full selector tape, scans every triple block in the actual order, and stores the forced bit values. It can return FAIL on a conflict, an all-eight block, or when u(p)>b(n). Otherwise it enumerates every assignment to the at most b(n) uncovered variables and verifies each completed assignment against the original full selector, including the unit and binary blocks. On a satisfiable selector with u<=b(n) the forced values are consistent and at least one candidate must be a verified model. On other selectors it never claims UNSAT from a failed search. It can emit a fixed malformed proposal on FAIL. This is a partial-success witness procedure with total bounded runtime, not a general polynomial SAT decider.

## 2. Explicit cubic clock inclusion

Implement this algorithm on a fixed multitape bit machine with input, counters, assignment and work tapes. Use binary loop counters for the supports in the original width/support/sign order; copying the input, parsing the unary header and advancing through all N selector bits cost O(L polylog L). Each block update or clause check needs at most a constant number of indexed accesses to the length-n assignment tape. Implement each by an explicit scan of at most n cells with binary counter comparison and reset, costing O(n polylog L) bit steps. Enumerating one completion and checking it costs O(n L polylog L), and enumerating at most 2^b<=n^(1/4) costs O(n^(5/4) L polylog L). The cost includes copying/verifying all actual selector bits, counter arithmetic and output. No random-access operation is free.

Use the ordinary fixed multitape-to-one-tape simulation by storing a constant number of tracks with head markers in a constant-width block encoding. Each simulated step can scan and update the entire used region, whose length is O(L+T); initializing and converting the raw binary input and copying the n output bits into the original required contiguous window also fit O((L+T)^2) steps. The three-symbol tape alphabet suffices for a fixed binary block encoding and blank separators; the number of states and binary transition-table length ell are fixed independent of n. This is the standard quadratic simulation argument, not an implemented source compiler. It gives an actual general tape program of U with successful run time bounded by

    O(n^(5/2) L^2 polylog L) = O(L^(17/6) polylog L),

since L=Theta(n^3). The same bound holds for failed runs. The output head is placed on the first of the n assignment bits and halts, exactly as in U. Because 17/6<3, for all sufficiently large n this bound is at most 2^(s_3-ell): indeed 2^s_3>=L^3 and ell is a fixed constant. The description is eligible then. This inclusion is about the EXACT original cubic stage, not a scheduler with altered weights. It uses no hypothesis P=NP or NP!=RP.

Consequently there exists n0 such that for every n>=n0,

    p in B_3(n)  implies  u(p)>=floor(log2(n)/4)+1.

This is an unconditional necessary condition on unrestricted residual inputs. It covers all satisfiable selectors, not just a particular family. We do not assert the converse, and the fixed program's code length and constants are not computed, so no explicit numerical n0 is supplied. In particular the finite examples at n=52..92 are not contradicted.

## 3. Exact probability and census bound for the planted distribution

Choose a witness w uniformly from {0,1}^n. Set all unit and binary selectors to zero. Independently for every ternary clause true under w, select it with probability 1/2. Never select a clause false under w. This defines a uniform pair (w,p) in a space of 2^n * 2^(7 binom(n,3)) pairs; a selector with several models can occur with several choices of w. Conditional on any fixed w, the eight-bit block on a support is complete with probability 1/128, independently of all other supports. These probabilities hold for every w, so they also hold unconditionally for the block indicators.

Let r=b(n)+1. If at least r variables are uncovered, choose an r-element subset R of them. No complete support can intersect R. The number of supports intersecting R is exactly H=binom(n,3)-binom(n-r,3). For each fixed R all those independent block events must be absent, of probability (127/128)^H. A union bound over R gives, for n>=n0,

    Pr[p in B_3(n)] <= min(1, binom(n,r) (127/128)^H).

As n tends to infinity, r=Theta(log n) and H>=r binom(n-r,2)=Omega(n^2 log n), while log binom(n,r)=O(log^2 n). Thus

    Pr[p in B_3(n)] <= exp(-Omega(n^2 log n)).

All probability is over planted pairs, not a uniform distribution over all SAT or all selector strings. This is a bound on failure probability, not the claim that cubic residuals are empty. Even this exponentially small fraction could contain astronomically many hard formulas.

In particular if u=0 all variables are pinned, so the selected formula has a unique model. The same union bound at r=1 gives Pr[unique] >= 1 - n(127/128)^binom(n-1,2), which tends to one. Each uniquely satisfiable ternary-only selector contributes exactly one pair to the uniform pair distribution. Conditioning on uniqueness is therefore exactly uniform over such selectors. For all sufficiently large n the proportion of cubic failures among those selectors is at most

    min(1, binom(n,r) (127/128)^H /
        (1-n(127/128)^binom(n-1,2))),

where the denominator is positive eventually. The same exp(-Omega(n^2 log n)) upper bound holds. An absolute census bound follows by multiplying the unconditioned failure probability by the number of pairs, which is an upper bound on the number of unique bad selectors. This is compatible with the earlier conditional exponential LOWER census under NP!=RP, and with the finite interval construction: neither gives a density lower bound in this distribution at large n.

More generally, with independent selection probability rho for each satisfied ternary clause, the same union bound replaces 127/128 by 1-rho^7. The probability calculation alone does not apply to correlated clause choices; the structural condition still applies. No randomness is needed by the fixed recovery algorithm.

## 4. Consequence for the unrestricted proof strategy

The compact sparse trace CNF from the preceding cycle is exact, but a generic planted model approach to finding its cubic-stage witnesses would have vanishing success probability at large n. Any genuine unbounded B_3 construction must leave at least floor(log2 n/4)+1 variables uncovered by complete triple blocks. One can impose that necessary condition on the cubic counterexample search without changing satisfiability beyond an unspecified finite threshold; no efficient search over the remaining selectors is established. This prunes a natural dense region of the exact unrestricted failure space, not a restricted-model lower bound. It is not an obstruction to all planted distributions, to sparse structured formulas, or to alternative algebraic or existential constructions. The next goal remains an unconditional unbounded-length cubic-stage failure proof or a uniform polynomial SAT cutoff. No universal obligation closes.

## 5. Evidence and scope

Independent JS constructed explicit normalized clause lists and scanned all n=1,2 selectors, all 256 ternary-only selectors at n=3, and 12 fixtures each at n=4,16 (four planted patterns, with zero, one or two omitted vertices in the complete-block region; unit clauses on omitted vertices). It independently checked returned assignments against selected clauses. Rows [n,inputs,successes,complete blocks processed,conflict/all-eight aborts,cap aborts,candidate verifications,sum emitted assignments] are in the plan JSON. Python uses the actual parent pool and verifier, tests all small model sets, checks actual block order, contradictory forced-block and enumeration-cap boundaries. Independent JS also enumerated all block-presence subsets for n=3,4,5, calculating exact weighted uncovered-vertex histograms with weights 127^(absent supports), denominator 128^binom(n,3). Python checks the identical histograms and every finite r union bound by exact integer multiplication. These tests are finite and do not execute the fixed general U program whose existence follows by the mathematical simulation argument. The generic compiler, explicit program code, n0, independent mathematical review and Lean formalization are outstanding. New exact-head CI required. No large cubic-stage counterexample was constructed or claimed.
