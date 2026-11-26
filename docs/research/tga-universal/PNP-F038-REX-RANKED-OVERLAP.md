# F038-REX-019 — Quadratic physical joint alignment

MRA-X-TGA-2.0 + RE-X. Parent 86e9b271672fec91f6c4bd468518482955112c3f.
PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE. Research branch only.

## Bounded hypothesis and design decision

REX-018 established correctness of a single variable-label edge, with a conservative O(N^3) physical time upper bound. The authorized target is to reduce the charged bound toward O(N^2 polylog N), preserving the identical raw grammar, output, all three overlap maps, original masks, row identity and witness selection. Instead of generating and sorting projected records (the proposed implementation), use pivot-synchronous refinement: broadcast one selected parent digit at a time to every active child row in a single bounded sweep. This alternative avoids data relocation, padding, sorting and scattering. No host key producer, precomputed matches or host handoffs. Acceptance requires the same full regression, full physical checkpoints, independent relational replay, increasing-row-count controls, and a proof charging every scan. Stop after this bounded task; full nested integration is not claimed. MRA-X roles applied locally rather than independently deployed agents.

## Identical input/output contract

Exactly REX-018: two-bit map 00/01/10 selects parent fields (0,1)/(0,2)/(1,2); parent and child explicit row tables separated by 110. Row 011, three nonempty bit-string fields (000/001 digits, each terminated by 010), Boolean local mask 100/101. Empty tables and duplicate rows permitted, opaque labels including leading zeros significant. Child fields 0,1 are retained and field 2 is fresh. Output one flag per parent input row, then one flag per child input row, marking first positive compatible child of first supported parent, if any. Negative cases output zero flags, not SAT rejection; malformed input halts on blank. No dense tensor or general decomposition validation, no original selector grammar, no all-parent predecessor table. See REX-018 report for full contract.

## Fixed mechanism and correctness

For parent row p_i with local u_i and child c_j with local v_j, f_i=u_i AND OR_j[v_j AND pi_k(p_i)=(c_j[0],c_j[1])]. The parser physically tags the retained parent fields A/B, retained child fields C/E, remaining fields X; every original bit preserved. Reuse REX-018 parser, parent traversal, serializer and final selection. Replace only the nested pairwise compare/restore loop.

For each positive parent row Q, activate every child header H as K by one sweep. For each next unconsumed digit in A, mark UA and store its bit in finite control. Broadcast that bit to the whole child region: at each K, scan within its own row to the first unconsumed C digit, mark UC if equal, otherwise return LEFT only within that row to K and set H, then skip the rest of the row. At an already inactive H skip its row. End-of-field broadcast (value 2 in finite control) retains K exactly when no unconsumed C digit remains; encountering child mask before a digit when a digit is expected drops K. Repeat for B/E while retaining K from the first comparison. The same child row must survive both coordinates. Inductive invariant after each digit broadcast: K headers denote precisely rows whose compared prefix has matched and not ended too early; used tags count consumed digits in each active row. End broadcast additionally requires equality of length. Hence after both fields K iff both labels exactly match. Disabled child rows can remain K during comparison, but their N0 mask prevents a positive contribution. Collect with a single scan, OR positive N1 among K; restore all headers and consumed child digits, then all consumed parent digits. Write T1h (h=hit) or skip disabled parent to T00. No parent or child record changes position, and original bits remain recoverable. After all parents choose first T11 and repeat the refinement once, mark first positive matching child N1 as O1 (preserves implied original bit). All other masks and tags restored. Thus duplicate rows retain independent flags, equal prefixes of unequal length fail, and deterministic support ordering agrees exactly with REX-018. Every forward parent progresses; each broadcast advances a pivot digit or ends a field; all scans bounded on valid input. No host state between phases. Final sparse projection emits the same flag sequence and erases input/history.

## Charged resource proof

Let N be raw input length, P number of parent rows, l_i the sum of retained parent label lengths. A broadcast starts with a bounded scan to D, scans each child row at most a constant number of times (a mismatch may rewind to its OWN K header, then skip that same row; never rewind to L per child). Thus O(N) per broadcast including locating/marking pivot digit with bounded scans. Two end-of-field broadcasts per positive pivot. Activation, collection, restoration and advancing the pivot cost O(N) each. Total forward work O(N*(P+sum_i(l_i+2)))=O(N^2) because P and sum of all retained lengths are O(N); backward repeats at most one pivot and is O(N^2). Parsing/cleanup O(N). This argument charges unequal widths, dense or sparse rows, inactive child scans and negative cases. It does not rely on a bounded label width, uniform rank labels or a fixed row count. No sorting is required.

The six-cell compiler charges 16 physical moves per moving logical rule and 11 transitions per staying rule (more precisely, 16/11 symbol transitions, respectively). Exact preparation 7N^2+17N+3. Inherited serializer exact 2wN+2w+2+sum_(i=0..N-1)[2w(i+1)+2c_i+2e_i+4]+H+3, w=6, H=P+C, e_i marks parent/child mask positions and c_i=sum_(j>i)e_j. O(N^2); output head -6N-H-2. Therefore total valid physical time Theta(N^2) (preparation supplies this implementation's lower bound), visited span O(N), no growing scratch region. Not a universal lower bound. For a dense pair of triple tables with positive uniform domain m, N=Theta(m^3 log m), this kernel costs O(m^6 log^2 m), improving the previous conservative O(m^9 log^3 m). This is a single edge, explicit input. Source generation, preserving a nested stack, multiple child updates, all-parent provenance, and final output translation remain open. The bound alone does not establish original F038 stage admission.

## Executed verification

Descriptor: 38 logical symbols, 476 logical states, 18088 rules, 48417 physical nonhalting states, 145251 physical entries, 2953441 description bits. Every entry decoded and checked. Exact same REX-018 825 logical cases (74 positive,751 negative), 873 parent rows,879 child rows; 45 actual physical executions (11 positive,34 negative), 90 full physical checkpoints, 63 parent and 65 child flags checked. All individual outputs agree with direct row predicate, and both complete physical tape snapshots preserve original labels and masks. Exact phase clocks, output head and cleanup checked. Main physical transitions 11149207, logical transitions within physical subset 192813. Prior REX-018 main physical transitions 11231735; improvement modest on small fixtures. 13 malformed controls 109276 physical transitions and two one-short controls excluded from main. No claim of universal pointwise speedup.

Local Python execution repeated unchanged hash-matched REX-018 reference (df4d6ac407ad8bc4bdc7c2533c11ea239c226c5d; inherited solver f0d633552d67fef7b3e29a6fc48a3f49c7c27091). All 825 cases and 873 parent flags matched; logical output checksum 3392018395 and physical subset 1193114046 match new audit. This is independent-code differential testing, not external certification. No fresh original universal interpreter run.

Additional width scaling (one parent, two children, prefix mismatch then exact support):
 [label width,N,physical,logical,span,phases]
 [1,80,130996,2779,568,[46163,44329,40504]]
 [2,98,198342,4339,694,[68897,69249,60196]]
 [4,134,374434,8467,946,[127973,135217,111244]]
 [8,206,892218,20755,1450,[300557,331665,259996]]
 [16,350,2590186,61459,2458,[863453,982609,744124]].

Additional growing-row-count comparison: n identical positive parent rows (101,11,0), n identical positive child rows (101,10,1), map 0. Late second-field mismatch means all flags zero. Both actual physical descriptors executed on identical raw inputs; new audit checks full snapshots for these cases. Results:
 n,N,old physical,new physical,old middle,new middle,span (same)
 1,71,96607,102890,28071,34354,505
 2,137,407269,367911,157217,117859,967
 4,269,2028925,1387697,1075281,434053,1895
 8,533,11757277,5386245,8034209,1663177,3751
Preparation and serializer identical. At n=8 new total is 45.81% of old, new middle phase 20.70% of old. At n=1 overhead makes the new worker slower. Scaling is evidence, not proof of asymptotic complexity; the bounded-sweep invariant provides the proof. Simulated symbol transitions, not hardware runtimes.

## Governance

ADVANCE quadratic single-edge alignment. PRESERVE exact row identity and all three maps. DECOMPOSE nested persistent lifecycle with reusable broadcast region, compatible per-parent provenance or recomputation, and original input/resource integration. RETIRE per-pair full-region scans for this kernel; do not infer a universal time lower bound from REX-018. STOP after bounded regression. Decision PRESERVE_QUADRATIC_EDGE_NESTED_LIFECYCLE_OPEN. All inherited local and global mathematical claims remain unchanged; 0/4 global alternatives closed. Status gate committed, not freshly executed locally; exact-head CI and independent formal certification unconfirmed.

Next bounded task: integrate this refinement into the nested introduction-tree grammar of REX-017 with variable-length explicit triple labels, retaining the parent feasibility vector on tape across child closes and restoring all transient markers. Charge total work across edges and recover global witness by recomputation or provenance. Do not merely chain host calls.

Reproduce:
 node mathos/research/f038_rex_ranked_overlap.js
 node mathos/research/f038_rex_ranked_overlap.js --description
 python -m mathos.research.validate_f038_rex_variable_overlap_alignment
 python -m mathos.research.tga_f038_rex_019

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
