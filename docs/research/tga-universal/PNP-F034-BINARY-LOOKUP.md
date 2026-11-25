# PNP-F034 — Checked binary list lookup

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base ee03c935217ac0488fe35c0809164fcd9df224be (PR #217). Independent of the three
pending encoder-byte-checker, value-projection and checker-binary-tests
candidates. Use the verified checked decrement directly for ordered
list lookup, including formula rows and generic capacity references.
A failed decrement on a nonempty list is exactly a zero index;
a successful decrement preserves width and reduces the index by one.
Each visited list cell and each inspected decrement bit costs one
selected visit. Candidate exact result projection to getAt and
formula lookup. For word width w, input list length L and represented
index i, both (w+1)*L and (w+1)*(i+1) bound selected visits.
The 512-bit checked Nat adapter has a 513*L visit bound and refines
the original lookup for i<cap 512; unrepresentable indices reject.
No truncation or claim that an arbitrary Nat index is representable.
The adapter does not charge encoding, allocation or complete runtime.
No production substitution. Full typed-checker width propagation
and bit-machine semantics remain open.

Eight candidate declarations and 3299 executable control
groups (2295 binary word/list combinations, 987 checked adapters,
12 wide cases, 5 exact counts). Marker F034_BINARY_LOOKUP_OK words=2295 adapters=987 wide=12 exact=5.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
No local Lean execution. Exact preflight required before PR.
Independent review and resolution remain open.
