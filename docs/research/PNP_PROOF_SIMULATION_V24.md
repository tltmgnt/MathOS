# MathOS v24 — proof-system simulation and obstruction invariance

v23 evidence CI passed (46139153440): twelve exact finite spectral
checks and parity decisions, up to 360 variables. Two of the six
odd instances had a positive width–size exponent parameter.
The exponential lower bound is asymptotic, not a measured proof size.

## A proof-preserving transformation

For normalized CNF F, introduce one fresh variable z and replace
each clause C by (C OR z) AND (C OR NOT z). Call the result P(F).
For every assignment to the original variables and either value of z,
the two clauses are equivalent to C. Restricting z to either Boolean
value recovers F, up to the existing syntactic normalization.

If F has a resolution refutation with t derived records and m axioms,
resolve each padded pair once to recover C, then replay the old DAG.
This costs at most t+m derived records. The maximum derived width
is at most the maximum of the original derived and original axiom
widths. The implementation accounts for dense normalization and
original variable labels, including unused declared variables.

In the other direction, ordinary resolution is closed under
restrictions up to subclauses. For an unsatisfied restricted axiom,
keep its restricted clause. Inductively maintain a representative
subclause for every unsatisfied restricted inference. If its pivot is
assigned, reuse the representative of the parent with the false
pivot. If unassigned and a representative lacks the pivot, reuse it.
Otherwise resolve the two representatives. The result is a subclause
of the restricted conclusion; no extra inference is needed beyond one
per original inference. A satisfied conclusion needs no representative.
The empty conclusion forces its representative to be empty. This
constructs a refutation of the restricted CNF with no more derived
records or maximum derived width than the original. The executable
translator covers arbitrary partial Boolean assignments, and both
source and result independently replay in the v13 verifier.

Hence for minimum derived-record count R, R(F) <= R(P(F)) <= R(F)+m.
For maximum clause width including axioms, W(F) <= W(P(F)) <=
max(W(F),w0+1), where w0 is maximum input width. The lower bound follows
from restriction, and the upper bound from recovery and replay.
The same argument applies to DAGs without unfolding them. These
claims concern ordinary non-tautological binary resolution; no
extension axioms, arbitrary semantic rules, or proof-search runtime
are included. Actual executables retain their dimension and proof caps.

## A representation-changing escape

On v23 expander Tseitin instances, fresh padding preserves the
original exponential resolution lower bound via restriction. The
padded input is still linear in the family parameter (ignoring
logarithmic bit encoding). This does NOT require constructing an
exponentially large resolution proof in CI. The inherited width and
width-size exponent metadata are source bounds, not measurements
or new numerical proof-size estimates for the padded instance.

By contrast, decode the original parity structure and verify the
v23 all-row XOR conflict (odd charge) or spanning-tree SAT witness
(even charge), with explicit padding equivalence. This certifies a
reduction to the empty clause or empty conjunction respectively.
The odd case has a constant-size resolution refutation in the
*output* CNF, but the full reduction relies on a different inference
mechanism. It is not a short resolution refutation of the input.
This demonstrates why equisatisfiable polynomial transformations
alone do not preserve restricted proof lower bounds. Transferring
a lower bound back across a transformation requires an appropriate
proof simulation with a controlled overhead.

In particular ordinary resolution cannot polynomially simulate the
parity-certificate refutations of this family as a proof system
over the original formulas: polynomial-length XOR certificates and
the imported exponential ordinary-resolution size lower bound
would be incompatible with such a translation. This is a known
restricted proof-system separation, not a lower bound on every
SAT algorithm. v23's imported Margulis–Gabber–Galil spectral and
Ben-Sasson–Wigderson width–size theorems remain dependencies;
see PNP_EXPANDER_SIZE_V23.md. No new theorem is claimed.

## Execute

    python -m mathos.research.pnp_proof_simulation_frontier --checkpoint artifacts/pnp-v24.json
    python -m mathos.research.pnp_proof_simulation_frontier --audit artifacts/pnp-v24.json

Six implication chains provide explicit resolution lift/project
controls. Five expander sizes (2,3,4,6,8), both charge variants,
test bound provenance and semantic escape. Side 10 is excluded
because padded literal occurrences exceed the existing input cap.
Random small CNFs test general restrictions and independent replay.
The audit checks source binding, padding, proof bounds, both
restriction branches, exact finite spectral and parity certificates,
constant output and report arithmetic. Proof verification does not
authenticate search work or show that a particular derivation is
optimal. Lean checks abstract Boolean padding/resolution and
implication transport, not full DAG restriction or the asymptotic
theorems. Universal obligations remain unresolved.
