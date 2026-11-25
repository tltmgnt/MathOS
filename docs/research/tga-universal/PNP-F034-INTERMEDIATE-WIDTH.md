# PNP-F034 — Intermediate checker operand width

PNP_RESOLUTION_STATUS = OPEN.

Independent candidate based on merged scanner PR #223
(0a405ad4376a9866e19d2ed12f9420bc6b106c03).
No dependency on the decoded-width, binary reference or checker
padding/encoder branches.

For any identifier ceiling K, lookup and demand selection preserve
clause fit; batch tails, frontier and augmented target preserve
formula fit; XOR toggle, combine, sumSupport and false-literal
projection preserve identifier fit. In particular K=cap 512 can be
used after separately establishing the input field-width conditions.

Generated indices i in indices d satisfy i<d; if d<=100000 they fit
17 bits. Successful groupCheck implies cap<=2 and cap+1<=3.
Successful capacityCheck implies every group cap<=2. If the group
list has length<=100000, totalCapacity<=200000<2^18.
These last conditions concern successful guards/checking, not
unconditional arithmetic on malformed inputs. The list-size premise
must be discharged separately for decoded groups.

Seventeen candidate declarations. Executable marker:
F034_INTERMEDIATE_WIDTH_OK pairs=7225 toggles=340 projections=170 capacities=101 guards=5 wide=2.
The wide groups test 1000-element recursive cases and the exact
100000-element arithmetic ceilings separately. Each of 85 small
support lists also exercises falseLits during projection controls.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom checks for
all seventeen declarations; exact marker required. No local Lean
execution or fresh verification yet. No total machine-cost,
certificate-size or P vs NP resolution claim.
