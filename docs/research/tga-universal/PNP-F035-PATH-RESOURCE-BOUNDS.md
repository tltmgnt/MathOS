# F035/F040 — Structural path certificate resource bounds

PNP_RESOLUTION_STATUS = OPEN.

Based on independently verified path compiler (1ce648a3) and reachability
(0ea47406) modules, integrated unchanged at 3aa3f054.
The separate 2-CNF model branch is not a dependency.

For E arcs, the invariant length(R)+missing(R,E) never increases at
relaxation: insertion adds one row and consumes at least one unit of
potential. Therefore the table seeded with a single vertex has at most
E+1 rows. Every stored route has length strictly less than the table
length, so returned paths have at most E edges. E <= L, the literal
occurrence count. These statements apply with duplicate arcs and sparse
identifiers.

For a successful compilePair with routes p,q, B=p.length+q.length+1
batches. The sequential compiler adds one new inference and copies all
current rows; with m original rows, total inferences equal m*B plus the
triangular sum 1+...+B. Thus a successful tryVar on the formula graph
has B <= 2L+1 and at most (m+2L+1)*(2L+1) inferences.
These bounds do not count bit operations, serialized bytes, or all
search work. They also do not bound unrestricted fallback.

20 public theorem candidates and 42 controls. Strict replay is required.
