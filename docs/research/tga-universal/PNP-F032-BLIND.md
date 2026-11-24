# PNP-F032 — Blind sparse-label recovery and a stronger negative control

PNP_RESOLUTION_STATUS = OPEN. Stacked on still-open PR #152 at
ebd16744441c9a038447b7265b913d2c3a037328, not on main. The actual
PR #152 Lean run 45446683002, job 138632242071, passed Lean 4.14.0
warnings-as-errors and the exact zero-axiom gate for ten new
ProctorParityElimination declarations plus four inherited GF(2)
declarations. Evidence artifact 14945534245.
https://github.com/tltmgnt/MathOS/actions/runs/45446683002/job/138632242071
This verifies local semantic theorems, not Python refinement.

## Blind schedule

The previous BVE recovery explicitly supplied auxiliary IDs. This
follow-up computes a schedule solely from normalized original clauses:
select variables with exactly one positive and one negative occurrence
after deduplicating clauses and dropping tautologies. Visit those
initially selected variables once, in increasing ID order. Use the
existing width-five, no-growth, global pair-budget BVE and combined
resolution/parity certificate checker. No graph, auxiliary map,
original formula, parity equations, or generator seed is given to
the solver. All positive and even fixtures use the same fixed pair budget of
1000, independent of the number of auxiliary variables. Their measured
pair counts are compared with the predicted bound only after solving.
The solver also has a fixed default budget of 100000. The checker does not depend on this schedule.

For each original cubic Tseitin clause (a,b,c), test both depth-one
(a,z), (-z,b,c) and depth-two (a,z), (-z,w), (-w,b,c) encodings.
Each introduced variable is private to one chain. Original edge
variables appear eight times (four clauses per endpoint); auxiliaries
appear exactly twice, with opposite signs. Thus the initial degree-two
schedule identifies precisely the auxiliaries in these fixtures,
regardless of numerical labels or polarity complementation.
Each auxiliary elimination has exactly one cross pair, preserves
the other chain variable's two occurrences if present, and decreases
the active clause count by one. Any order reconstructs the original
clauses, up to permutation and complementing variables. Hence for q
vertices and chain depth h, the recovery schedule needs 4qh pair
tests and the final parity detector recognizes q rows. Odd total
charge remains inconsistent under relabeling; the even-charge systems
remain consistent. This is a family-specific argument, not a general
gate-recognition theorem.

Relabel all occurring variables with shuffled sparse IDs >=10^40,
independently complement variables, shuffle clauses and literal
orders, and use declared n=2^200. The solver receives only that
transformed formula. Direct recognition is expected to find zero
rows; blind preprocessing is expected to recover the odd-charge
contradiction and leave even controls UNKNOWN.

## Stronger negative result

A distinct width-four hiding scheme replaces each original clause C
with (C OR g) AND (C OR NOT g), with one shared fresh selector g for
the entire formula. The two clauses are pointwise equivalent to C.
For the cubic Tseitin family each vertex support has exactly the
four forbidden parity assignments. Including both selector values
creates eight forbidden patterns on four variables, but only four
of each four-variable parity. Consequently no complete parity
block is recognized. Every original edge has sixteen occurrences
and g has 8q occurrences, so the degree-two schedule is empty.
Both direct recognition and blind BVE are expected to return
UNKNOWN on these UNSAT inputs. A stronger elimination strategy
could recover the original clauses; this is a counterexample to
the present heuristic, not to arbitrary bounded elimination.
The control is deliberately width four, outside the earlier
width-three search contract but inside F032's width-five detector.

## Evidence and scope

New suite: 36 odd-charge fixtures (q=4,8,16,32,64,80; three seeds;
two depths), 36 matched even-charge controls, 36 zero-budget
controls, 12 shared-selector negatives, and 1200 small random
sparse formulas with projection checked by brute force. Also
check local chain equivalence, normalization, original-clause
certificate replay without the scheduler, tamper and empty cases.
No new empirical claims until actual CI logs. Degree counting is
polynomial in explicit formula length; earlier BVE structural bounds
still apply, not a measured bit-transition count. The initial
schedule is not iteratively recomputed, may miss hidden equations,
and may eliminate variables in already useful parity blocks.
No independent review, executable Lean refinement, complete SAT
decision or original scratch port. Existing Lean gates unchanged.
Next: direct-XOR/BVE/dynamic certificate routing and budget semantics,
with stronger negative controls and explicit scope.
