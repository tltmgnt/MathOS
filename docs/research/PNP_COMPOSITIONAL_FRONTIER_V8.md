# MathOS v8 — compositional proof obligations and strong backdoors

The v7 algebra is a restricted direct compiler into affine or bijunctive
systems. v8 adds disjoint-component composition and bounded strong backdoor
search into this exact compiler target. Both E01/E02 remain unresolved.

## Execute

    python -m mathos.research.pnp_compositional_frontier --checkpoint artifacts/pnp-v8.json
    python -m mathos.research.pnp_compositional_frontier --input cnf.json --k 3
    python -m mathos.research.pnp_compositional_frontier --resume artifacts/pnp-v8.json
    python -m unittest discover -s tests -p 'test_pnp_compositional.py' -v

Input JSON has n and signed integer clauses. Output references normalized
clause indices and variable labels; the new-to-old map is included.

## Constructive contract

A strong backdoor B for a component is a variable subset such that EVERY
assignment to B yields a residual that compiles into a v7 direct mode.
The mode may differ between assignments. The finder enumerates subsets by
size up to k<=3, at most 256 candidates per component. Even if a SAT branch
is found, every other branch must compile to certify the strong property.
The checker verifies complete and distinct branch assignments, independently
substitutes into the original normalized clauses, and replays v7 algebra
certificates. SAT is the OR of the branch decisions; UNSAT requires all
branches contradictory. Failed-search metadata is informational, not a
verified minimality or obstruction claim.

Partition normalized clauses by shared variables. Disjoint components have
independent assignments, so their decisions combine by AND. One certified
UNSAT component suffices, even if others are unresolved; SAT requires
all components certified SAT. The checker independently verifies clause
coverage and disjoint variable sets without trusting the partitioner.
It allows coarser disjoint partitions as well. No empty clause is dropped.

If components have sizes n_i and input lengths L_i, with a polynomial
direct compiler bound p, uncapped subset search uses at most
sum_i sum_{j=0}^k binomial(n_i,j) 2^j p(L_i) plus polynomial bookkeeping
(up to polynomial factors for global labels/normalization). This is
polynomial for fixed k. It is not a uniform polynomial guarantee if k
grows with the input. Given backdoor sets, replay has the simpler
sum_i 2^{|B_i|} p(L_i) bound. A supplied logarithmic-size backdoor may
therefore be polynomial to use, but finding it by enumeration need not
be polynomial. This separates discovery from execution, an important
unresolved part of O10. The implementation's finite caps and cooperative
budgets do not prove asymptotic performance.

## Obstruction and escape

An isolated signed ternary OR clause, in literal truth coordinates, has
seven allowed patterns. Majority of (100,010,001) is 000; ternary XOR
of (100,010,110) is 000. Thus it is neither bijunctive nor affine.
Sign flips preserve both closure properties. A global strong backdoor into
the original direct compiler must hit its support: otherwise that unchanged
isolated relation persists after every assignment outside the support.
For m such disjoint clauses, every global backdoor must hit m disjoint
supports, so |B|>=m. One variable per clause suffices: every residual is
2-CNF. Therefore the minimum global strong backdoor is exactly m on
this family. The checker verifies the isolated-clause premises and
closure witnesses; the universal counting argument is documented, not
machine-checked.

Full assignment enumeration on a minimum global backdoor has 2^m leaves.
The componentwise method instead replays exactly 2m local leaves using
one variable per component. The counts refer to these specified
enumeration schemes, not an unconditional runtime separation, and not
a lower bound on SAT solvers. This family is easy for many other methods.
For m>=1 the formula is SAT, and the finite probes replay the component
certificates independently. Additional controls require two splits
on a connected input, demonstrate an UNSAT control, and preserve unknown
when a single split is insufficient. The obstruction report can also
be used on arbitrary inputs with isolated ternary clauses.

## Formal and universal obligations

Lean proves abstract independent existential-product composition and
soundness of arbitrary finite OR decision trees combined by AND. It
does not formalize the Python partitioner, Boolean compiler, backdoor
search, counting theorem, or complexity model. The separate CI job
enforces an axiom-free policy. The research ledger retains O08/O09/O10/
O11/O12 as unresolved, including uniform discovery of transformations
and algorithm-independent lower bounds. It does not upgrade a
finite certificate, a restricted lower bound, or an abstract lemma
into a universal P versus NP proof. Checkpoint resume restarts input.
