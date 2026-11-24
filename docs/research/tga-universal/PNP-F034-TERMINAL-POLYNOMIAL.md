# PNP-F034 — Terminal polynomial selected-charge bounds

PNP_RESOLUTION_STATUS = OPEN. PR #178 merged at
633c0fca0905c92baef3068dc16de24ab7526bdf. Initial run
45503601628 job 138832955813 failed on seven proof obligations,
including the following reported errors:
artifacts/pnp-f030/f034-polynomial-meter-combined.lean:3112:11: error: type mismatch
artifacts/pnp-f030/f034-polynomial-meter-combined.lean:3223:11: error: tactic 'rfl' failed, the left-hand side
artifacts/pnp-f030/f034-polynomial-meter-combined.lean:3264:8: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
Process completed with exit code 1.
Correction 0a757bea53e08a804ac2214a348597cef404a99a
uses constructive arithmetic and explicit reduction. Final run
45504464911 job 138835948137 passed all 21 zero-axiom declarations
and 53 chains, 21 XOR sums, one word control. Artifact 14972497969.
https://github.com/tltmgnt/MathOS/actions/runs/45503601628/job/138832955813
https://github.com/tltmgnt/MathOS/actions/runs/45504464911/job/138835948137

## Candidate bounds on existing terminal budgets

A structural cap B >= 1 dominates formulaMass, the weighted row
mass of demands and conflicts, and the weighted group mass. A row
or group weighs one plus its literal length. For XOR, a block weighs
one plus its support length and reference mass; B also dominates
supportMass. These hypotheses are explicit, not yet linked by a
kernel theorem to the wire encoder length. B may be chosen as
one plus the sum of these structural masses.

Weighted visits: if each callback budget plus one is at most its
item weight times K, traversal budget <= total weight times K.
This prevents independent worst-case maxima for group size and
number of groups from spuriously increasing the degree.

Capacity conflict leaf <= 7B at width <=3; tuple leaf <=9+7B.
For g<=B and depth 1..3 the word budget is at most g times
B*(B*(L+1)+1)+1 with L=9+7B. A group plus its visit is bounded by
its weight times groupFactor(B)=B+B*(B*(L+1)+1)+1+2.
Consequently all group work is bounded by B*groupFactor(B),
a quartic. Demand pair and coverage terms, reference scans and
final comparison are added in capacityUnit. Demand pair bound
uses a deliberately loose quartic maximum rather than the tighter
analytical estimate. Thus the capacity unit is a polynomial of
degree at most four in B.

For XOR, each leaf <=6+6B, tree recurrence V(0,L)=L,
V(k+1,L)=2V(k,L)+1, depth at most five. Per-block reference
budget <=B*(2B+1); summing over at most B blocks yields a
conservative cubic terminal unit including quadratic support
cancellation. This is looser than the earlier analytical
quadratic estimate but sufficient for a global quartic envelope.

24 candidate declarations connect the actual terminal budgets
and metered counts to these explicit polynomials. Static controls
replay all 24 capacity and 21 XOR fixtures. Exact marker:
F034_TERMINAL_POLYNOMIAL_OK capacity=24 xor=21.
Strict zero-axiom gate unchanged; new CI pending, no local Lean.
No encoded-size bridge, complete unified polynomial theorem,
machine cost, parser cost or independent review yet. These are
bounds on selected abstract charges, not total runtime or proof
discovery. No main change or unrestricted SAT claim.
Next: formal structural-to-encoder-length bridge and unified
selected-cost polynomial composition.
