# PNP-F034 — Capacity terminal selected resource ledger

PNP_RESOLUTION_STATUS = OPEN.

Candidate based on exact verified XOR ledger head
61f307590f7d003f243faeaa785198865c627131 (PR #234); uses its generic
two-coordinate folds, lookup and membership meters. Independent of
unified checker PR #233. Twenty-three candidate declarations compose
selected reference lookup visits, literal comparisons, duplicate tests,
complementary conflict tests, demand-pair comparisons and coverage.

The proposed result projects to capacityBinary for all typed operands,
including failed encoding cases. The group reservation respects cap<=2
before word enumeration, so guarded groups enumerate words of length at
most three. The demand-pair meter explicitly hoists two checked lookups
once per unequal index pair. This is a costed alternative with a proposed
Boolean projection proof, not a trace of the old nested demand function.
For D demand rows it reserves at most 2*(w+1)*D selected lookup visits per
pair (1026*D at width 512). Identifier comparisons use 10*w+3 gates;
literal comparisons use 10*w+6. The aggregate ledger sums all selected
reservations across demands, conflicts, groups, ordered demand pairs and
coverage; structural Nat capacity arithmetic is not charged.

Budgets remain recursive and data-dependent. Boolean combining,
structural enumeration, allocation, encoding, padding and total machine
runtime are excluded. Eager independent reservations need not coincide
with a single short-circuit trace.

Strict Lean 4.14.0 warnings-as-errors, 23 explicit zero-axiom checks,
1140 control groups (8 distinct, 96 groups, 1024 pairs, 8 terminals,
one each positive, guard, malformed and wide), and exact marker:
F034_CAPACITY_RESOURCE_LEDGER_OK distinct=8 groups=96 pairs=1024 terminals=8 positive=1 guards=1 malformed=1 wide=1.
Fresh exact-head replay required before PR; no local Lean execution.
No polynomial certificate existence or P vs NP resolution claim.
