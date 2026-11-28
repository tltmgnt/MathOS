# MathOS v5 — generalized certified semantic escape

Extends v4 with bounded Boolean conditioning and independent component
decomposition. The producer returns a SAT witness, a checked UNSAT proof
tree, or no candidate. Resource exhaustion is a separate exception. The
existing v4 rules, hypotheses and evidence remain unchanged.

## Certificate and scope

Run the new regression:
    
    python -m unittest discover -s tests -p 'test_pnp_generalized_escape.py' -v

The public API is propose(n, clauses, budget, depth=2) followed by
verify(n, clauses, artifact, budget). Input is normalized by the shared
kernel, so the signed witness refers to dense variables, not raw IDs.
The certificate is JSON round-trippable. A checked SAT certificate is
equisatisfiable with the empty conjunction; a checked UNSAT certificate
is equisatisfiable with a conjunction containing one empty clause.

The producer tries constant assignments, exact enumeration of at most
eight active variables, connected components of the clause-variable
incidence relation, and conditioning on the most frequent variable.
Components have disjoint active variables; their witnesses combine.
One contradictory component suffices for UNSAT. A split is refuted only
if both Boolean residuals are refuted. The verifier checks a total
witness directly, or independently replays each split and validates
subformula membership by indices and exhaustive bounded leaves.
It rejects consecutive subset nodes and bounds split depth by four.

For fixed split depth d and leaf cap k, each branching level explores
at most 2^d copies of input literals in aggregate across components;
components partition clauses, conditioning never increases their size.
The number of nonempty recursive calls is O((d+1) 2^d N), where N is
the normalized input size, since each component split has at least two
nonempty children and each split consumes depth. Empty residuals add at
most a constant factor. Each call uses at most polynomial work in N,
including sorting, set operations and at most 2^k leaf assignments;
a conservative polynomial operation bound is O((d+1) 2^(d+k) N^3)
under unit-cost integer operations. The certificate size is polynomial
for fixed d and k. This is an informal bound on the restricted
algorithm, not a formal complexity proof or process memory limit.
Input dimension and cooperative time/work limits still apply.

## Controls and formal layer

The signed six-variable block controls combine arbitrarily many small
components (within the kernel limits), with a mixed-sign planted SAT
assignment or a contradictory final block. The v4 constant-witness and
fixed-core recognizer returns no candidate for the tested controls.
A second family uses a high-occurrence separator, yielding independent
small residuals after conditioning. Tests include random brute-force
cross-checks, forged proofs, unknown results and exhaustion.

Lean checks generic logical identities for Boolean splitting,
independent existential conjunction and subformula contradiction, with
an axiom-free CI gate. It does not formalize the Python implementation,
complexity bound or all of SAT.

## Open obligation

Characterize larger inputs that admit a bounded number of useful
separator splits, then test certified strategies on families lacking
that property. No universal reduction or P vs NP result is established.
