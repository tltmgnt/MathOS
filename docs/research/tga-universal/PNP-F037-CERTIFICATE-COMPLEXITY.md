# F037 — Exact branch safety and total certificate complexity

PNP_RESOLUTION_STATUS = OPEN.

## Previous evidence

The case-transport audit passed at
66eeb2747377ee3a396daf9bec33e6f93310659e
(run 45693413870, job 139484472835).

## Exact safety is not a free oracle

For an encoded 3-CNF F, variable v and bit b, let R_b be the
restriction at that bit. Define Safe(F,v,b) by

    SAT(F) implies SAT(R_b).

Shannon restriction gives the equivalent condition
not SAT(R_(1-b)) or SAT(R_b). The complement of Safe is thus
the intersection of an NP property and a coNP property. Define
DP = {L1 intersect L2 : L1 in NP, L2 in coNP} and coDP as its
complement class. Exact unsafe-choice recognition is DP-complete
under polynomial many-one reductions, and exact Safe is
coDP-complete.

To show hardness, take any pair A,B of 3-CNFs, on disjoint renamed
variables, and a fresh v. Guard A by v and B by not v. Each
four-literal guarded clause (g OR a OR b OR c) is split into
(g OR a OR u) AND (not u OR b OR c) with a private fresh u.
Existentially eliminating u gives precisely the original clause.
The inactive guarded side always has a satisfying extension,
independent of its original variable values. Thus R_false is
satisfiable iff A is, and R_true is satisfiable iff B is.
Choosing true is unsafe iff A is SAT and B is UNSAT.
The paired SAT-UNSAT language is DP-complete: reduce the NP
part of an arbitrary DP language to A by 3-SAT completeness
and the complement of its coNP part to B by the same theorem.
All renaming and splits cost polynomial bit length.
The classification assumes ordinary valid encodings (invalid
encodings can be rejected separately).

Even on guaranteed satisfiable inputs, recognizing the safety
of one prescribed bit is NP-hard: use a trivially satisfiable
A in the same reduction. It is witnessed by a model of the
chosen branch under that promise. This is not a lower bound
on finding SOME safe bit; the latter is the selector problem.
Exact recognition of all safe pairs is also stronger than
a total selector: a selector only needs one valid choice.

## Total short certificate supply is equivalent to NP=coNP

Suppose a uniform deterministic polynomial-time verifier V
accepts certificates of safe choices, with soundness on
ALL formulas, including unsatisfiable ones. Suppose for every
formula and occurring variable, at least one bit has an
accepted certificate of length bounded by a single polynomial
of the encoded input length. No deterministic discovery
algorithm is assumed. It is not necessary to certify every
safe choice.

For an unsatisfiable F, every restriction is unsatisfiable.
Take its distinct occurring variables in a deterministic order.
For each still occurring variable, supply an accepted bit
and certificate and restrict. A variable already absent may
be skipped. After at most n steps the residual contains only
empty clauses or no clauses. It is unsatisfiable and so
contains an empty clause. This sequence is an NP witness for
UNSAT. Check each certificate against the exact residual,
perform the indicated restriction, and check the empty clause.
Soundness is induction backwards: if the initial formula
were satisfiable, every certified restriction would preserve
satisfiability, contradicting the final empty clause.
The total witness length and verification cost are polynomial:
at most n steps, each residual has at most polynomial bit
length in the original input, and the certificate bound is
uniform. Thus UNSAT is in NP and NP=coNP.

Conversely, if NP=coNP, then UNSAT has a uniform polynomial
verifier with polynomial-length witnesses. Define a safe-choice
verifier with two certificate tags: a satisfying assignment to
R_b, or an UNSAT witness for F. Either proves safety. If F is
satisfiable, some restriction is satisfiable and has a short
model witness; if F is unsatisfiable, the second tag supplies
a certificate for either bit. This establishes the equivalence.
It does NOT establish a deterministic polynomial-time generator.
Adding uniform deterministic polynomial-time certificate
discovery at each occurring variable would instead give P=NP,
using the verified single-path framework. Conversely P=NP
gives a polynomial-time safe selector and verifier.

For SAT-promised inputs alone, short choice certificates exist
unconditionally (a chosen-branch model suffices). The difficult
total-coverage requirement includes unsatisfiable residuals.
The preceding certificate architectures were sound on all
formulas but did not prove such coverage. Universal short
proofs should not be confused with an efficient decision rule.

## Lean candidate and finite audit

ProctorChoiceCertificates defines an abstract checker, soundness,
total supply and an inductive trace ending in an empty clause.
Six theorem candidates establish that the trace is sound and,
conditionally on total supply, exists for every UNSAT formula.
The abstract logical theorem asks for supply even on absent
variables; a polynomial witness construction can instead skip
them or give a trivial absent-variable certificate. The Lean
module does not formalize encoded lengths, computational classes
or the polynomial cost argument. No total-supply instance is
asserted. Exact-head kernel verification is pending.

Independent JavaScript execution checked 4096 pairs of small
guarded formulas (1024 in each branch viability category).
It also enumerated every branch trace on 4096 small CNFs:
all 2816 UNSAT instances admitted accepted traces, none of
the 1280 SAT instances did, and 22122 UNSAT traces were
accepted. It used exhaustive SAT as a fixture oracle, not
a polynomial certificate generator. The Python fixture
also checks all 16 patterns of a guarded width-three clause
and three rejection controls. Python exact-head replay pending.

## Decision

Stop treating a general short local-certificate supply as an
easier routine engineering completion task: even total coverage
by one polynomial-size safe-choice certificate per step would
resolve NP versus coNP in the equality direction. Deterministic
discovery is a separate stronger gate. The reduction identifies
the complexity of a proposed obligation; it neither settles
NP versus coNP nor P versus NP. No new verified declarations
credited until strict replay; no main change.
