# PNP-F032 — Gate-obscured parity and certified bounded elimination

PNP_RESOLUTION_STATUS = OPEN. Native implementation, not the missing
Claude scratch files. PR #150 merged at 0db1a572334d0832c602e7b97e5e083f737b051b.
Its CI run 45443754815 job 138621728283 passed six tests and 3000 random
controls: 1398 certified UNSAT, 1602 UNKNOWN, 1507 brute-force SAT.
Thus 95 of the 1493 brute-force UNSAT cases were not certified.
Sixteen odd-charge cubic controls passed through 400 vertices (600 edge
variables, 1600 clauses, 400 dual rows, 798 row XORs at the largest size);
all sixteen even-charge controls returned UNKNOWN. Artifact 14945715973.
https://github.com/tltmgnt/MathOS/actions/runs/45443754815/job/138621728283

## Obfuscation construction and negative result

For each original non-tautological width-three clause (a,b,c) with
distinct variables, introduce a private fresh variable z and replace
it by (a OR z) AND (NOT z OR b OR c). Seeded permutation selects a.
Existentially eliminating z is exactly equivalent to a OR b OR c:
if a is false, z must be true and then b OR c must hold; if a is true,
z=false works. Distinct private auxiliaries allow the equivalence to
compose across clauses. This is a clause-splitting encoding, not a
general theorem about hidden circuits or cryptographic obfuscation.

Every resulting support contains a private auxiliary and occurs once
per clause width. No full width-two or width-three parity block exists
(two or four distinct forbidden patterns are required), and there are
no unit clauses. The previous syntactic XOR detector therefore
recognizes zero rows, regardless of the original parity contradiction.

## Bounded variable elimination

For pivot v, split active clauses into positive P, negative N and
unaffected U. Replace P and N with every non-tautological resolvent
(A without v) union (B without -v), deduplicated against U. This is
exact existential projection: if a residual assignment satisfies all
resolvents, it cannot simultaneously require v=true from some positive
clause and v=false from some negative clause. Therefore it extends to
a satisfying value of v. Conversely every old model satisfies all
resolvents. Tautological clauses and duplicates may be deleted safely.

Skip any pivot whose pair count exceeds remaining global pair budget,
any whose non-tautological resolvent is wider than the configured
bound, or any with more new distinct clauses than removed clauses.
Pure pivots have zero pairs. Accepted elimination never increases the
active clause count. Every considered pair is charged even on a
subsequently skipped pivot. These are abstract structural counters,
not total running-time limits. The default schedule is descending
occurring ID order, once each; an explicit order can be supplied.

For the clause-split Tseitin fixtures, the schedule explicitly lists
the known private auxiliary IDs. Each has one positive and one negative
clause, one resolvent of width three, and replaces two clauses with
one. A budget of m original clauses suffices to reconstruct the
original CNF exactly. This is an informed fixture schedule, not a
claim of blind gate discovery. With budget zero the direct negative
result persists. The default schedule is separately exercised on
random formulas, but not claimed to recover arbitrary hidden parity.

## Proof objects and checker

Keep original clause indices and a sequential list of resolution
parent pairs with signed pivot (positive parent first). The
elimination log names all active positive and negative parent IDs
and all newly created IDs. Replay recomputes original clause sets,
active parent lists, every non-tautological cross-product, exact
deduplication, width/no-growth conditions, derived clause IDs and
final active references. It checks that no required resolvent was
omitted and no unsupported clause was inserted. The replay does not
call the elimination solver. Claimed counters, skipped choices and
the cached residual clauses are not trusted.

The reconstructed residual is passed to the existing F032 parity
certificate checker. UNSAT of this residual proves UNSAT of the
input by resolution consequence alone; the stronger exact
projection property is checked too. A consistent extracted parity
system yields UNKNOWN, never SAT. This checker shares input helpers
and the previous parity checker, so independent authorship and
formal executable refinement remain absent.

## Complexity and scope

With m original clauses and r occurring IDs, active clauses never
exceed m. At most r pivots are considered, each with at most m^2
pairs; a separate global pair budget can reduce this further.
Accepted proof lines are at most rm (at most m additions per pivot).
For fixed width bound, preprocessing and certificate replay have
polynomial bit cost using explicit finite list-based representations:
original widths and signed-ID lengths are charged by input size,
resolvents by parent widths, and all references by binary proof size.
No allocation or loop over the declared n is used. This is not a
measured transition bound, not a kernel-checked cost proof, and not
a complete SAT algorithm. The prior resolution-only lower bound does
not automatically apply to this stronger combined inference language.

## New controls

1500 deterministic small random sparse CNFs, exact projection versus
brute force, combined-certificate soundness, no-growth and pair-budget
checks; twelve odd-charge cubic fixtures through 80 vertices at seeds
11 and 29 with known auxiliary schedules, matching even-charge and
zero-budget negative controls. Local clause-split truth table,
width/growth skip, pure and tautological cases, and tampered resolution
parents, pivot, missing batch additions, residual references, trailing
lines and parity payload. No new empirical result is claimed before
CI. Original handoff benchmarks remain unreproduced. Strict Lean
policy unchanged; next gate is formal local parity extraction and
resolution projection semantics, broader blind adversaries and
independent review. No P vs NP promotion.
