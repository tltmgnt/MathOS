# F035 — Explicit binary byte solver

PNP_RESOLUTION_STATUS = OPEN.

Integrates the verified polynomial wire-size branch f8228960 and
explicit rank comparator 0c181ffe. The new producer uses the same
validity, width, empty-clause, conflict and UNSAT checks as the verified
producer; its SAT branch directly materializes bitModel without numeric
rank arithmetic. Equality of finite witnesses is proved by pointwise
model equivalence and list induction, not functional extensionality.
Candidate byte producer equality applies to every expected byte list,
including malformed, invalid and unsupported inputs. Soundness,
completeness, correct tags and the existing cubic canonical output
bound transfer by equality.

Ten public theorem candidates, 1034 controls. Exact-head replay required.
The alternative comparator visits 2L positions per score comparison.
This is not a native bit-time bound; graph construction, proof generation,
replay, serialization and machine cost still need accounting.
No unrestricted SAT or P versus NP claim.
