# PNP-F034 — Binary capacity terminal refinement

PNP_RESOLUTION_STATUS = OPEN.

Candidate based on merged research head
03b9d7c80fb4f412df7227d2d59e09fe8da072e6. Independent of pending
binary chain and XOR replay. Uses verified binary lookup, literal
equality, membership and reference validation, decoded width and
intermediate target width closure.

Substitutes selected binary operations in reference checks, duplicate
detection, complementary conflict tests, demand selection, demand
identifier disjointness and group coverage. Retains structural Nat
enumeration, the capacity guard and final totalCapacity comparison.
Conditional equality with the original capacity checker preserves
its existing acceptance semantics. The decoded demand-list count
token supplies the generated-index width premise; the decoded
certificate and target-width theorems supply the remaining premises.

Selected demand lookup visits are bounded by (w+1)*D for D demand
rows (513*D at width 512), including failed lookup. No aggregate
capacity gate, encoding, padding, allocation, or whole-machine bound.
The final capacity arithmetic remains Nat, not a binary replacement.

Seventeen candidate declarations and 1394 executable control groups:
8 distinct, 96 group, 1024 disjointness, 256 demand, 8 terminal,
1 positive and 1 wide contradiction. Strict Lean 4.14.0
warnings-as-errors; exact marker F034_BINARY_CAPACITY_OK distinct=8
groups=96 pairs=1024 demands=256 terminals=8 positive=1 wide=1 and
all seventeen zero-axiom checks. No local Lean execution.
Fresh exact-head replay required before PR. No polynomial
certificate existence or P vs NP resolution claim.
