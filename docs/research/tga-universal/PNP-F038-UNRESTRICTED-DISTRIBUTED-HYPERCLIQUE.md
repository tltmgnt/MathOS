# F038 — distributed hyperclique selectors and bounded-space stage cutoff

PNP_RESOLUTION_STATUS = OPEN. Mathematical construction, upper-bound derivation, and finite reference regression; not a compiled original-U solver, Lean proof, or independent review.

Parent f328aba90d402732746e994e275639d888641dd0: semantic rectangle barrier. Its exact-head CI was not confirmed at inspection. This note changes the promised input family, not U, its verifier, tape alphabet, description encoding, or weighted clock.

## 1. New distributed constraint family

Fix an integer r>=3 (a constant in the eventual machine), and m>=2. Set n=(2r+1)m-r+2. Use r ordered one-hot groups X_g of m variables each, g=0..r-1, and r OR auxiliary groups Y_g of m-1 variables each, followed by m pin variables and two guards. Precisely, X_g[j]=gm+j+1, Y_g[i]=rm+g(m-1)+i+1, pins start at n-m-1 and end at n-2; guards n-1,n. Indices are zero-based. These intervals partition all n variables.

Use the existing onehot(X_g,Y_g) clauses, guarded pin lifts (one signed pin literal and all four sign combinations of the guards), and negative units for both guards. These fixed clauses have exactly one extension for each tuple a in [0,m)^r and fixed pin pattern: X_g[a_g]=1 and all other X bits zero, Y_g[i]=1 iff a_g<=i+1, pins fixed, guards zero.

Allow an arbitrary subset of all cross-group negative clauses of width 1,2,3: each is the negation of the selected X variable in each of a subset H of distinct groups, with 1<=|H|<=3. No such clause overlaps a fixed clause. A selected clause forbids exactly the tuples matching its specified digits on H. The original normalized selector is still 1^n 0 followed by the actual pool(n) bits in canonical width/support/sign order. All remaining selector bits are zero except the fixed clauses. Each surviving tuple corresponds to exactly one model, so the verifier's SAT predicate is exactly nonemptiness of this distributed join.

In particular, for r=6 and using only width-three masks, the 20 group triples carry 20 independently selectable m^3-bit forbidden tables. This realizes arbitrary six-partite three-uniform hyperclique: keep an edge iff its triple is not forbidden, and a model is one vertex from each group with every induced triple present. The correspondence is exact and parsimonious, not a computational hardness claim. There are 2^(20m^3) distinct such selectors for fixed m and pins. The 20 masks constrain overlapping projections of the six-coordinate witness, unlike two aligned masks of a single three-coordinate index. This encoding still has substantial exploitable structure.

## 2. Prefix expansion with bounded workspace

The key audit is that a generic quadratic-time multitape simulation overestimates the cost when the algorithm has bounded space. A more precise simulation extends the family cutoff beyond four groups.

On a fixed multitape bit machine, parse n from the unary header and compute m=(n+r-2)/(2r+1), checking integrality and m>=2. Recover pin values by scanning the actual normalized selector and reading the positive-pin, negative-guard triple selector for each pin in order. Compute pool positions by enumerating supports/signs with O(log L)-bit counters, where L=n+1+2n^2+8 binom(n,3)=Theta(m^3) for fixed r. The input stays on its own tape; no random access or supplied mask streams.

For each of m^(r-3) assignments p to the first r-3 group digits, scan the entire input selector. For each selected cross-group negative clause:
- If a specified prefix digit differs from p, the clause is already satisfied, so skip it.
- Otherwise retain its specified digits in the last three groups and enumerate all completions of the unspecified suffix digits. Append the corresponding integer suffix indices in [0,m^3) to a scratch stream. If the clause is entirely in the prefix and matches p, it forbids every suffix (one may instead immediately discard p).

For a particular group subset H of width <=3, let h be its number of suffix groups. After prefix filtering, at most m^h distinct clauses on H can remain because all prefix digits are fixed. Each contributes exactly m^(3-h) suffix indices. Thus at most m^3 records are emitted for that group subset, counting duplicates across clauses and subsets. There are C_r=sum_{k=1}^3 binom(r,k) such subsets, a constant. The entire scratch stream has at most C_r m^3 records, each O(log L) bits.

Sort the suffix indices by bottom-up external merge sort on a fixed number of tapes. Split runs into two streams, merge successive pairs into two destination streams, then swap the tape roles. Run lengths, record comparisons, end positions and counters use O(log L) bits. There are O(log L) passes; each pass is sequential apart from local counter work and costs O(m^3 polylog L). The scratch space, including duplicate records and auxiliary streams, is O(m^3 log L) bits. Scan the sorted stream, skipping duplicates and maintaining the smallest not-yet-covered suffix index; if an index in [0,m^3) is missing, p plus that suffix is a surviving tuple. If all suffixes are covered, clear/reuse the scratch tapes and advance the prefix. The procedure is exact because a forbidden clause eliminates precisely those suffixes enumerated when the prefix is compatible with it.

On success reconstruct the n raw witness bits from the one-hot, OR, pin and guard formulas above. On exhaustion halt with malformed output (not an arbitrary-input UNSAT claim). The existing external verifier is unchanged. The algorithm need not certify membership of the input in the promised family; its outputs on other inputs are still verified by U.

For every prefix, parsing, expansion, sorting, scratch cleanup and gap search cost O(L polylog L) bit transitions. Total multitape time T=O(m^r polylog L), but the total tape interval required per simulated tape is bounded by S=O(L polylog L): the input, pins, counters, output and reusable scratch never grow with the number of prefixes. Here S includes the initial input and all visited cells; rewind and reuse scratch from fixed origins between prefixes, never allocate fresh space per prefix.

## 3. Original three-symbol machine and clock

Simulate the fixed multitape machine on one tape using a constant-width binary block code for combined finite symbols and simulated head markers, with all-2 blank blocks. Raw input conversion takes O(L^2) physical moves by right-to-left constant-width expansion. Keep all simulated tracks in a contiguous coded interval of O(S) blocks, with fixed boundaries and at most one head marker per track. A fixed number of sweeps of this interval collects the currently scanned symbols in finite control, then writes new symbols and relocates markers by one simulated cell, extending the interval when needed. A left-moving marker can be placed by a local reverse sweep; a right-moving one by a forward sweep. The interval is O(S) because the multitape algorithm uses fixed origins and bounded visited positions. Each simulated step costs O(S) original transitions, not O(T) unless the space actually grows to T. The number of tracks, code width and control states depend on fixed r, not m.

At halt copy the n output bits into a fresh contiguous raw region beyond the coded interval using marked processed output blocks and sequential appends; O(n(S+n)) steps suffice. Position the physical head on the first raw output bit, even if zero. On failure halt on a blank. The actual original verifier reads n cells starting at the halt head. This is a finite-control existence argument in the original three-symbol alphabet; no free multitape operations remain, but no concrete table or description length has been compiled.

Hence for fixed r and some finite constants C_r',d_r,

    t <= C_r' m^(r+3) (log(L+2))^d_r
      = O(L^((r+3)/3) polylog L).

The original fixed description has constant length ell_r. Writing j=ceil(log2 L), there exist constant a_r,b_r such that every satisfiable promised input is solved by stage

    ceil((r+3) j / 3) + a_r ceil(log2(j+1)) + b_r.

This follows directly from s>=ell_r+ceil(log2 t). At the exact cubic stage s=3j, the budget for that description is at least L^3/2^ell_r once 3j>=ell_r. For r<=5 the ratio of the upper bound to the budget tends to zero (the worst exponent is 8/3), uniformly over masks and pins. Thus every satisfiable member of each fixed r=3,4,5 distributed family is eventually outside B_3. This is stronger than the naive O(T^2) simulation cutoff r<=4.

For r=6 the upper bound is O(L^3 polylog L), with no power slack. It neither fits the exact cubic allocation by this argument nor proves that any input misses that allocation. It gives eventual success at every fixed exponent >3 for this family. For r>6 the bound is higher still; no uniform claim for r growing with m. The six-group hyperclique encoding is a concrete next candidate, not a proven hard instance or a lower bound on any algorithm. In particular the stage exponent ceiling of the preceding ordered two-mask family does not itself transfer to it.

## 4. Finite reference validation

Separate JavaScript enumerated the canonical clause pool and actual selected bits, checked extracted cross clauses and pins, expanded each prefix's suffix blocks and compared all tuples with direct forbidden-clause and fixed-clause truth. For r=3..6, m=2,3, seven deterministic fixtures per layout (empty, contradictory unary, unique unary, adjacent binary, mixed, ternary, planted unique ternary), the totals are 56 selectors, 8400 tuple checks, 385 prefix checks, 37059 emitted records including duplicates, 1338 satisfying tuples, 45 SAT fixtures and 18 unique fixtures. Zero violations. This is high-level finite enumeration, not a run of the proposed external sort or actual tape simulation. The Python reference additionally calls the original verifier on a reconstructed surviving witness for each SAT fixture. Python and exact-head CI have not been confirmed at writing. The theoretical cost uses direct completion enumeration, not the JavaScript scan of all suffixes for every active clause.

## 5. Research disposition

The new family has overlapping constraints rather than an aligned two-mask intersection, but up to five groups even these distributed masks are too cheap for unbounded cubic failures. Six is the first integer group count where this specific bounded-space prefix-expansion proof loses its power slack. Next audit six-partite three-uniform hyperclique for an alternative original-tape algorithm with exponent <3 or a genuine rejection-preserving lower-bound mechanism. Avoid mistaking the lack of slack in one upper bound for hardness. Finite cubic interval and reported Lean census unchanged, not recounted. No universal obligation closes, no unbounded cubic failures proved, no unrestricted SAT cutoff proved. Promotion NONE.
