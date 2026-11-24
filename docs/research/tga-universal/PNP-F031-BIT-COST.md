# PNP-F031 — Native root-component search: deterministic bit-cost model

PNP_RESOLUTION_STATUS = OPEN. Scope: the native root-only adapter merged
in PR #146, using F025 partition and F030 adaptive propagation. This is
an explicit mathematical upper bound for a deterministic realization of
that algorithm, not an extracted machine, an interpreter benchmark,
a proof of Python-to-machine refinement, or a Lean-checked complexity theorem.

## Input and machine

Use a deterministic multitape Turing machine with a fixed finite alphabet,
separate read-only input, rewritable work tapes and sequential proof/output
tapes. A tape transition reads/writes at most one symbol per tape and moves
heads at most one cell each. All signed IDs, counts and budget K are binary,
with self-delimiting lengths (e.g. unary length followed by binary digits);
clauses have length 0–3 and are explicitly delimited. Let B be the total
encoding length plus 2, including the declared n and K. Let m count clauses,
r count occurring IDs, r_j count IDs in root component j, and V be the sum
of F030 visited nodes actually used. Then m<=B, r<=3m=O(B), each original
ID uses O(B) bits, and every compact ID and row index uses O(log B) bits.
A proof node contains only bounded-size fields and at most O(B) propagation
events or Horn trace entries. The budget counter and cumulative metadata
require O(B) bits: even unbudgeted, a forest of full binary trees has at
most sum_j (2^(r_j+1)-1) nodes, so counts multiplied by any fixed polynomial
in B still fit O(B) bits. No array of length n is used. F027 compression's
F024 compile call receives the number of *occurring* IDs, never declared n.

Realize all maps/sets by finite lists of records and linear scans,
all sorted collections by comparison-based insertion sort, and all
random indexed access by scanning from the beginning of its list.
Use encounter order for iteration where relevant, retain F030's deterministic
tie breaks, and use explicit stack frames for DFS. Each record has O(B)
bits; represent variable-length tuples as sequences of records, comparing
their fields rather than treating the tuple as a unit-cost word.
Arithmetic on these bounded-size counters and signed integers uses ordinary
binary scan/add/subtract/compare algorithms. No unit-cost hashing, unbounded
integer operations, pointer arithmetic or random-access memory is assumed.

## Work storage and record operations

At any instant the active formula, sparse-ID tables, normalized clauses,
component membership, union-find parent table, SCC graphs and search
worklists contain O(B) records each (width is bounded, so there are at most
three pair constraints per clause before deduplication and a constant
number of arcs per pair). The DFS stack has O(r+1) frames because each
split fixes an unassigned variable, each frame stores O(r+1) assignment
records, and a propagation or closure pass uses O(B) additional records.
The native wrapper retains at most O(B) component descriptors and O(B)
total membership/literal records, and a single active F030 solver.
Consequently the work area is O(B^2) records or O(B^3) tape cells.
Do not include the potentially exponential preorder tree in this work
area. Append its events/terminals to a separate sequential spool;
after a SAT or UNKNOWN result discard it, after UNSAT rewind and replay
it in order. Use a separate final output tape. Sequentially reading,
writing or rewinding a spool is charged by its actual length; there
is no random access to it and no copying its prefix at each node.

A single record operation (access, comparison, insertion, deletion,
bounded integer update or move) costs at most O(B^3) transitions on this
work area, even if it scans or shifts the entire area. Operations on
tuples are counted by the number of constituent records. A constant
number of scratch tapes suffices for scanning/copying a record or shifting
a contiguous region. This loose bound covers the O(B)-bit arithmetic.

## Preprocessing and per-node schedule

The following are conservative upper bounds on record operations,
*before* multiplying by the O(B^3) cost per record operation.

- Normalize and sort occurring IDs, remap the O(B) literals, remove
  duplicates/tautologies in F027 compression, and construct the compact
  F024 validation rows/gates: O(B^2) comparisons/accesses. Root F025
  partition uses O(B) unions/finds, each of length at most O(B), plus
  grouping and local renaming. Comparing component index tuples during
  ordering can take O(B) operations each; O(B^3) covers all preprocessing
  and repeated per-component preparation even if O(B) components each
  use the global B bound. Empty/invalid/budget-zero cases take no search
  nodes but still pay preprocessing.
- At a search node, F030 simplification does at most r+1 passes.
  Every successful unit or pure assignment fixes a new variable.
  Each pass scans O(m) width-three rows, accesses assignments, constructs
  signs and sorts pure literals; the list-machine schedule has at most
  O(B^2) record operations per pass (including insertion sorting),
  thus O(B^3) per node.
- Renamable-Horn recognition constructs O(B) pairs and arcs, sorts and
  deduplicates pairs, and performs two DFS passes. Each vertex/arc is
  visited a bounded number of times; list accesses are charged, not
  assumed constant-time on a tape. O(B^2) record operations suffice.
  Orientation and Horn closure scan O(B) rules at most r+1 times; O(B^2).
  Branch selection, copying assignments, counters and node-log construction
  are bounded by O(B^2) operations per node.
- For an emitted UNSAT tree, F030 replay scans original clauses after each
  propagation event, checks literal signs/indices and consumes both split
  children in preorder; a Horn trace has at most r distinct derived heads
  and one terminal conflict on a valid generated proof. O(B^3) record
  operations per node covers these checks and the DFS stack. SAT witness
  checking and union, subset selection and outer replay use O(B^3)
  operations over the wrapper apart from local proof replay. A returned
  UNSAT proof is from one component; charging all generated node logs
  and a constant number of replays of each only overestimates total cost.

No phase above enumerates assignments outside F030's visited search tree.
The record count bounds allow redundant comparisons and scans; list
lookup itself is charged by the tape cost per operation. The preprocessing
and postprocessing O(B^3) bounds are independent of V.

## Time, proof size and space

Multiplying by O(B^3) tape transitions per record operation gives

    T(B,V) = O((V+1) B^6).

This includes sparse normalization, decomposition, preprocessing for all
components, propagation, recognition, branch selection, complete witness
or refutation construction, in-solver verification and final serialization.
Each node has O(B) records of O(B) bits, so the total spooled data and
returned result are O((V+1) B^2) bits (including metadata). Sequential
spool operations therefore fit the time bound. Working space excluding
the sequential proof spools is O(B^3); including them and explicit output,
O(B^3 + (V+1) B^2). The total time is also bounded by

    O((1 + min(K, sum_j (2^(r_j+1)-1))) B^6).

The sum is zero for an empty partition. K is a binary value, not its bit
length; an exponentially large K can still permit exponential running
time. For max component size b and k nonempty components, the corresponding
unbudgeted search schedule is O((1+k*2^b) B^6) with budget arithmetic
bounded as above (choose a binary budget of O(B) bits large enough).
If b=O(log B), this is polynomial for that structural promise. No such
promise holds for unrestricted inputs.

For an externally supplied, finite, explicitly encoded proof of P bits,
the same sequential verifier can reject malformed records, invalid
identifiers, oversize lengths, extraneous/missing children and invalid
propagations. Bound all working integer/record lengths by B+P,
charge parsing by explicit input size, and process at most P node/event
records. The conservative bound O((B+P+1)^7) follows from the same scans;
it is polynomial in the *combined* input/proof length, not necessarily
in formula length. This analysis concerns the defined finite encoding,
not arbitrary Python objects, generators, or malicious __iter__ methods.
No parser or bit-trace implementation for this encoding is supplied.

## Acceptance boundaries

This is a paper upper-bound argument for the specified deterministic
list-based realization, with no claim of tightness. It does not replace
the code's abstract node counter with measured transitions. A concrete
machine implementation, bit-trace validation, proof of equivalence with
the Python implementation, and independent review are future obligations.
The new connected guarded family in PNP-F031.md demonstrates an
exponential node lower bound for the root-only algorithm itself, not for
a dynamic-component variant or any unrestricted SAT algorithm.
