# F038 — mobile projection workspace closes the six-group cubic candidate

PNP_RESOLUTION_STATUS = OPEN. Mathematical machine-existence construction and finite reference checks; not a compiled original-U solver, Lean proof, or independent review.

Parent 049514801a6b6fc0dcf2ac42cb6fbe5c795f9312 (distributed hyperclique). Exact-head CI not confirmed by the available connector. Same promised normalized selectors, same U, original three-symbol tape, verifier, description syntax and weighted clocks.

## 1. New cutoff

Fix r>=3. For the complete distributed family in the parent (arbitrary selected negative cross-group clauses of widths 1..3, fixed one-hot/OR/pin/guard clauses), there is a fixed original one-tape program with running time

    O((L^2 + m^(r+2)) polylog L)
    = O(L^max(2,(r+2)/3) polylog L),

where L=Theta(m^3) for fixed r. In particular for r=6 the exponent drops from 3 to 8/3. Every satisfiable member of this six-partite hyperclique family is eventually solved within the exact cubic stage, including uniquely satisfiable members. This upper bound is uniform in the forbidden masks and pin pattern, but not in growing r.

The reason is that after fixing r-3 coordinates, only the pure three-suffix-group constraint table has cubic size. It need not be copied to workspace or sorted: it can be streamed from its original selector locations. Everything else fits a quadratic-size mobile workspace.

## 2. Exact residual decomposition

Use the parent's n=(2r+1)m-r+2 layout, with groups numbered 0..r-1. Fix the prefix p in [0,m)^(r-3). For each selected cross-group negative clause other than a clause using all three suffix groups, discard it if any specified prefix digit differs from p. Otherwise project away its prefix literals, retaining its h<=2 suffix group/digit pairs. The result is a forbidden partial pattern: it excludes a suffix iff all its specified digits match that suffix. An empty pattern excludes every suffix and can be stored without special treatment. Keep duplicates if different original clauses project to the same pattern.

For d=r-3, the number of stored patterns is at most

    K_r(m)=sum_{h=0}^2 binom(3,h) m^h sum_{k=0}^{3-h} binom(d,k) - 1.

Here binom(d,k)=0 for k>d. A group subset with h suffix and k prefix groups has at most m^h clauses compatible with p, since its prefix digits are fixed. Subtract one for the excluded empty original clause. This bound is attained when every cross-group clause is selected. It is O_r(m^2), counting duplicate projected patterns separately.

The pure suffix clauses are exactly the m^3 all-negative triples with one variable in each final group. Their actual canonical pool positions are in lexicographic order of suffix digits. For a candidate suffix z, its own pure ternary bit must be zero. Then p,z survives exactly when no stored pattern matches z. This is equivalent to satisfying all cross-group clauses, since every selected clause either was satisfied by p, became a forbidden partial pattern, or is the pure ternary clause associated with z (all other pure clauses are satisfied). The parent's fixed clauses give the unique full witness extension. No membership oracle or auxiliary mask input is used.

## 3. Mobile-workspace one-tape implementation

A global O(TS) sweep simulation is not required for a read-only sequential input with local workspace. Here are the charged physical operations.

Use a fixed finite product alphabet of an input track and work tracks, with delimiter, marker and scratch variants. Represent product symbols by constant-width binary blocks, reserving an all-2 block for the unoccupied blank; the product alphabet depends only on fixed r. Convert the raw input to these blocks by right-to-left shifts (constant expansion) in O(L^2) original transitions, retaining left/right input end markers. This is the same kind of physical conversion as the earlier copier. Thereafter no write to the work tracks changes the input track. The input is not on a separate physical tape.

Let w=ceil(log2(n+1))+O(1), enough for the variable, group and digit counters (for fixed r), and let W=O_r((m^2+1)w) blocks. Work data occupy a single contiguous interval of at most W blocks, with its left boundary at the current input position. It can extend past the right input end into blank blocks. Work includes the fixed number of binary counters, current prefix, m pin bits, and a packed sequence of projected records of O(w) blocks each with a constant number of fields and scratch tracks. Use self-delimiting tagged fields with widths derived from n; no finite-state counter of unbounded size is assumed.

Advance the input position by one by shifting the entire work interval one block right, leaving input-track symbols in place. One left-to-right carry sweep suffices: retain the previous work-track symbol in the finite control, write it over the current work-track symbol while retaining that cell's input component, and carry the overwritten work symbol to the next block. Begin with a blank work symbol and include the cell just beyond the right delimiter. Boundary tags move with the data. Traverse back to the new left-boundary marker. Leftward movement uses the reverse sweep. If the interval grows, append a tagged record at the end, then return to the left boundary; no input position changes. Blank blocks outside the initialized region can be converted to the product blank when visited. This gives O(W) physical transitions per one-block input advance or rewind, including returning the head to the workspace boundary. Fixed-width block operations cost a constant number of original transitions. The input track and origin marker remain stationary even when workspace moves.

Parse the unary header and derive m from n using binary counters, and compute the canonical pool positions by incrementing support/sign counters as in the parent. Initial header/pin recovery may use a workspace of O(m+polylog L) blocks; cost is bounded by O(L W polylog L) plus initial conversion. The parser's counters remain at the left boundary in a small header and cost polylog L per input position. Pins stay in the workspace throughout. For every prefix perform two passes:

1. Scan the entire normalized input and collect compatible projected patterns as above. Test the prefix using the small header. Append an O(w)-block record to the end by carrying its small value in a temporary tagged register. Carrying across the record array costs O(W polylog L), by moving the small register record by record. Rewind the input to its origin by shifting the workspace left. At most O(L) input positions and O(L) appends occur.

2. Scan the actual normalized input again, examining each pure suffix triple position. If its bit is one, skip it; otherwise compare its three digit values against the stored patterns. If no pattern matches, produce the full witness and halt. If the pass finds none, rewind, erase/reuse only the record array, and advance the prefix counter. Exhaustion of all prefixes produces a malformed halt. No checking of arbitrary-input SAT membership is required; the claim is for promised inputs and U continues to verify all proposals.

Crucial local record test: do not simulate each comparison by a full workspace sweep. Reserve an O(w)-block query field and scratch bits in each record (and an initial query field in the header). Copy the three query digits from the header to the first record, then from each record to the next, using marked bit-by-bit local copies within two adjacent O(w)-block records. Such a copy or comparison takes O(w^2) block moves: use a marker on the source and destination, shuttle at most O(w) positions for each of O(w) bits, and advance the markers. Delimiters and group tags specify which digit fields are compared; the group tags are from a fixed finite set. Check equality on the at most two specified fields, with the empty pattern always matching. Preserve the data fields; the scratch query fields may be overwritten on the next test. Keep a finite flag if a match is found. Returning to the header takes O(W). This scans K_r(m) records in O((K_r(m)+1)w^2)=O(W polylog L) block moves, not O(W^2). Appending a new record can use the same local-copy procedure with its value instead of the query. The parser and prefix counters are not moved independently of the workspace, and any pin-array traversal for reconstruction can use the same local-copy operations. The input is never random-accessed.

Both passes, including rewinds and cleanup, thus cost O(L W polylog L) per prefix. Workspace reuse makes its size independent of the number of prefixes. The head may visit O(L+W) blocks in total. At success produce the n bits in the prescribed order (one-hot, OR, pins, guards) in a scratch region, then append them into a fresh raw contiguous output region outside the coded tape. A simple shuttle per bit costs O(n(L+W) polylog L), dominated by the claimed total. Position the head on the first raw output bit as required by tape_run. At failure halt on a raw blank. All operations described use a finite fixed number of tracks and tags and local moves; after constant-width encoding they use only the original symbols 0,1,2. The bound charges initial conversion and output; this is a mathematical finite-control construction, not a generated table or measured physical runtime.

There are m^(r-3) prefixes, L=Theta(m^3), W=O(m^2 log L), so the total is O((L^2+m^(r+2)) polylog L). The machine and its description length ell_r are fixed for fixed r. If j=ceil(log2 L), its exact cubic clock 2^(3j-ell_r) is at least L^3/2^ell_r for sufficiently large L. For r<=6 the exponent max(2,(r+2)/3) is strictly less than 3, so the runtime/budget ratio tends to zero. Thus the earlier open six-group candidate cannot yield unbounded cubic-stage SAT residuals. For seven groups this upper bound is O(L^3 polylog L) and lacks power slack; it implies neither exact cubic inclusion nor any lower bound. The upper bound also yields eventual inclusion at each fixed stage exponent greater than max(2,(r+2)/3).

## 4. Finite reference validation

Independent JavaScript checked the canonical pool order, extracted pin bits, pure suffix-bit ordering, projected patterns and actual fixed/variable clause truth. Layouts r=3..7 and m=2,3, eight fixtures each (the seven parent modes and all cross-group clauses selected) gave 80 selectors, 28,120 candidate tuples, 1,216 prefixes, 59,852 projected records including duplicates, 3,667 satisfying tuples, 54 SAT fixtures and 22 unique SAT fixtures. Dense fixtures attain the exact record bound K_r(m); the largest observed per-prefix record count was 248 (r=7,m=3). Separate abstract track-shift reference checks exercised 15,360 right/left shifts with work strings of length 1..4 and different stationary input tracks/anchors. These are logical track tests, not execution of a compiled original three-symbol table or timing evidence.

The Python regression uses the parent's actual pool/selector and verifier helpers, checks the exact pattern count and saturated dense fixture, and implements a separate finite track-shift reference. Its execution and new exact-head CI remain unconfirmed at writing. The mathematical bound rests on the charged local workspace and query operations, not on the finite enumeration.

## 5. Disposition

Six-group distributed hyperclique is now another family-specific upper-bound obstruction to the search for unbounded cubic failures. Seven is the first fixed group count at which this particular mobile-projection upper bound lacks power slack. Do not equate this with hardness or assume the seven-group case resists other algorithms. Next investigate stronger local batching/join methods or a different lower-bound family and sound semantic rejection mechanism. No unrestricted SAT cutoff or lower bound, no new Lean declaration, and no change to the finite cubic interval 52..233. Promotion NONE.
