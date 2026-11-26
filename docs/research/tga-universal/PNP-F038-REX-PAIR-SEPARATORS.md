# F038-REX-014 — Persistent physical two-coordinate separator elimination

MRA-X-TGA-2.0 + RE-X. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
Parent 088cf196e26f2ddfac1de12068be225197d03f2c. Main unchanged.

## Bounded mission and contract

The variable-domain tree worker used single-coordinate separators. This mission isolates the new issue of overlapping two-coordinate separators by implementing a fixed Boolean sliding triple chain. Hypothesis: exact pair messages and compatible predecessor records can survive an arbitrary number of overlapping bags with two factors per candidate, without host handoff, and separate unary marginals cannot replace the pair. Acceptance: fixed three-symbol descriptor; actual shared-candidate conjunction, intrinsic coordinate overlap, full tape checkpoints, persistent backward recovery, direct predicate agreement, independent Python replay and charged resource bound. Stop after bounded audit. No independent agent ensemble or formal certification claimed.

There are g>=0 triples and n=g+2 Boolean variables x0,...,x_(n-1). Raw input is four bits encoding initial allowed pair relation M0(x0,x1), indexed 2a+b, followed by g blocks of 16 bits. Block i (zero-based) encodes two arbitrary Boolean factors R_i,S_i on (x_i,x_(i+1),x_(i+2)). Four outgoing columns in order j=2b+c, each containing R_i(0,b,c), S_i(0,b,c), R_i(1,b,c), S_i(1,b,c). Input contiguous from head zero, blank elsewhere. N=4+16g. No supplied membership outcomes, projected keys, predecessor ranks or explicit topology indexes. Shared coordinate identity is implicit in the fixed sliding grammar, not an arbitrary supplied relation between encoded pair states. Missing a second factor can be represented by its all-one table. Input length must have the specified form; empty or incomplete streams reject. Successful output is n contiguous bits at halt head, in original variable order. Valid UNSAT and malformed inputs halt on blank and are not distinguished by output alone; rejecting scratch need not be erased. This is not the original F038 selector grammar.

## Exact semantics and proof

For each block i compute M_(i+1)(b,c)=OR_a [M_i(a,b) AND R_i(a,b,c) AND S_i(a,b,c)]. The two factors are evaluated at the SAME full triple, before OR over a. M_i is exactly the set of feasible frontier pairs of the prefix, by induction: any satisfying prefix ending with a,b extends by c iff both new factors allow that triple. Conversely any positive term has a valid prefix extension by the induction hypothesis. No past variable outside (a,b) appears in the new factors. Store p_i(b,c) as the least such a, or sentinel 2 if none. This four-entry predecessor history is complete for backtracking. Choose a final feasible pair in order of last coordinate first then penultimate, and repeatedly recover the least predecessor. Induction yields a satisfying assignment and the reverse-coordinate lexicographically least satisfying assignment. The coordinate b is carried unchanged at every overlap (a,b)->(b,c), rather than independently chosen at each stage. If final mask is zero the original conjunction is unsatisfiable. The proof uses exactly this chain structure and explicit Boolean factors, not arbitrary bag topology.

## Fixed physical mechanism

Inherit the five-cell REX block compiler. Logical alphabet contains blank, raw bits, R sentinel, I(raw,output) for two initial output bits, H(raw,p) retaining raw bit and predecessor p, O(raw,p,output) retaining both and emitting a bit. Forward pass reads the first four bits into a finite mask; each column then reads the two raw factor bits for each a in rank order. The first factor bit, hit flag and corresponding previous mask bits are held in finite control. At end of column write H to its last raw cell, with p=0,1,2. All original input bits remain recoverable. Build the next mask by appending one feasibility bit per column. Prior bits for b=0 can be discarded once both b=0 columns are processed. At the next boundary accept another complete 16-bit block or write R on blank and enter choose with the final four-entry mask. Neither number of bags nor witness length enters finite control. Final zero mask rejects explicitly.

Backward pass starts at last data cell. If H, traverse at most 16 cells to the selected column in this group, read p, replace H by O with output c and carry prior pair (p,b). Traverse the rest of the group leftward and repeat. If at initial raw bits instead, emit a,b via I at initial positions 2,3, move to first block and enter ready. The inherited sparse serializer projects I and O tags, skips other symbols and removes input/history; output has exactly n bits in original order. Full forward/backward snapshots verify original factor preservation. No host reset between phases.

Implementation development: sparse rejection rules in an initial draft let the physical decoder halt at the last block bit rather than execute the full explicit logical rejecting stay. A phase-clock comparison detected the four-transition discrepancy. Final worker totalizes all 783*22 rules, including aligned reject, and the complete audit passes. No failing draft counted.

## TECT-X — Two different loss-of-correlation obstructions

1. At every outgoing (b,c), factor R allows only a=0 (mask 85), S only a=1 (mask 170). Initial pair is full. Each has a witness but no shared triple, so the exact outgoing pair relation is empty. Actual physical run rejects.
2. First triple mask 195 (other factor full) forces its outgoing pair to equality, {00,11}. Second triple mask 90 (other factor full) requires its incoming pair to be unequal, {01,10}, and otherwise permits either new digit. Each triple alone is satisfiable. Both pair relations have full unary projections, but their intersection is empty. The integrated two-stage physical run rejects. Thus even individually feasible shared coordinates cannot substitute for their joint separator. This is a counterexample to marginal-only propagation, not a lower bound against all algorithms. Retain joint separator identity and conjoin complete candidate predicates.

## Charged resource ledger

For valid N=4+16g, successful forward/backward middle phase uses exactly 2N moves and g+2 stays: 2N+g+2 logical transitions. Each moving logical transition compiles to 13 physical transitions and each stay to 9; middle=26N+9(g+2). Valid UNSAT uses N+1 moves plus one rejecting stay (N+2 logical steps); no output serializer. Preparation exact P=6N^2+15N+3, valid UNSAT physical total 6N^2+28N+25. On success, let e_i indicate output at initial positions 2,3 and one selected column end in every block, with c_i=sum_(j>i)e_j. Serializer exact 2wN+2w+2 + sum_(i=0..N-1)[2w(i+1)+2c_i+2e_i+4]+n+3, w=5. Final head -5N-n-2. Both codecs cost O(N^2) and use linear span, logical solver O(N). Thus total physical time Theta(N^2), span O(N), for this implementation; the preparation supplies the lower bound. It is NOT a universal time lower bound. For explicit fixed Boolean sliding bags this is a polynomial algorithm, consistent with standard bounded-treewidth dynamic programming. It does not prove a uniform bound for variable rank cardinalities, arbitrary multi-coordinate bags, the complete original normalized selector grammar, or general SAT. No original U-stage admission asserted.

## Executed verification

Descriptor: 22 logical symbols, 783 states, 17226 rules, 29313 physical nonhalt states, 87939 physical entries, 1700158 description bits. Descriptor decoded entry-for-entry. Main audit 594 valid instances: all 16 initial masks, all 256 first-factor triple masks with full second factor and full initial pair, 256 pairs of repeated-four-bit masks, two explicit obstruction fixtures, 64 seeded one-to-six-bag paths (32 planted witnesses). 489 SAT, 105 UNSAT; 1923 variables across cases, 735 triple bags and 5880 complete triple candidates. 5459365 simulated physical transitions and 27140 logical transitions. 594 full aligned forward checkpoints and 489 full backward checkpoints, 1083 total; 5316 initial/derived feasibility entries represented by input and predecessor tags (including final mask independently checked), 1466 positive predecessor marks. Full tape output compared individually with direct assignment predicate oracle; exact middle clocks, preparation, output serializer/head and scratch cleanup checked. 45 malformed controls (all strings shorter than four bits and 30 partial-block truncations) halt on blank, 105710 physical transitions separate from main total. Four one-step-short controls, six extra scaling successes:
 [n,N,physical,logical,span,phases]
 [3,20,5702,43,127,[2703,547,2452]]
 [4,36,16600,76,224,[8319,972,7309]]
 [6,68,55388,142,418,[28767,1822,24799]]
 [10,132,200932,274,806,[106527,3522,90883]]
 [18,260,763892,538,1582,[409503,6922,347467]]
 [34,516,2977300,1066,3134,[1605279,13722,1358299]].
Scaling forces all-one witness, not precomputed message flags. Counts are simulated physical symbol transitions, not hardware time. No new original selector interpreter replay.

Actual local Python audit used the committed hash-matched sources d8e427bb767b9a91ad33f90f546457e25e9f7cd8 and f0d633552d67fef7b3e29a6fc48a3f49c7c27091. It independently enumerates original full models, compares the complete remaining relation after each left-to-right elimination, and checks bag candidate counts. 594 cases, 489 SAT, 105 UNSAT, 1923 reference stages, 9444 reference candidate rows (includes final two eliminations per instance), 2694 projected row occurrences. FNV-1a output-stream digest 2653112972 equals actual physical output digest. This is differential testing by the same assistant, not an external independent review; per-input JS comparisons and invariant proof supplement the checksum.

## Evidence and governance

Local modeled completion packages: interface 3, integrated machine 5, restricted stage 6, restricted evidence 7, uniform 8, all blocked. Global mathematical alternatives direct SAT 1, selector 3, certificate architecture 7, universal lower bound 1, all blocked. 0/4 closed; counts are not mathematical distance. Python status gate committed, not freshly executed locally. No independent certification or Lean formalization. ADVANCE exact physical pair separator lifecycle for Boolean sliding chains. PRESERVE variable-domain tree worker, complete-candidate and witness-provenance invariants. DECOMPOSE variable-domain sliding triples with validated tensor dimensions and explicit overlap identities; eventually general admitted bag plans and original F038 input. RETIRE independent unary marginals as a substitute for a joint pair. STOP automatic expansion. Decision PRESERVE_BOOLEAN_PAIR_SEPARATOR_VARIABLE_DOMAIN_OPEN. Next separately authorized mission should implement variable-domain pair separators, not merely host-flatten arbitrary pair states.

Reproduce:
 node mathos/research/f038_rex_pair_separators.js
 node mathos/research/f038_rex_pair_separators.js --description
 python -m mathos.research.validate_f038_rex_pair_separators
 python -m mathos.research.tga_f038_rex_014

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
