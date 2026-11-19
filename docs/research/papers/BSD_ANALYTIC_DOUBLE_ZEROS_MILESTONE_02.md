# MathOS BSD milestone 02 — unconditional analytic order at least two on a cofinite family

**Working research note.** Status: \`CLASSICAL_COROLLARY\` / \`ANALYTIC_LOWER_BOUND_ESTABLISHED_BY_EXTERNAL_THEOREMS\` / \`EXACT_RANK_EQUALITY_NOT_PROVED\` / \`NOVELTY_NOT_ESTABLISHED\` / \`BSD_NOT_PROVED\`.

**Source provenance:** This manuscript builds on the [MathOS 01 two-section benchmark](BSD_RANK_TWO_FAMILY_MILESTONE_01.md) and cites two outside *proven theorems* (Silverman specialization; Gross–Zagier–Kolyvagin low-analytic-rank theorem). It does not claim a new theorem in the mathematical literature or a full rank comparison.

## Main theorem

For indeterminate \(T\) let

\[
E_T:\;y^2+y=x^3+(1+T)x^2-(2+T)x,\qquad P=(0,0),\;Q=(1,0).
\]

Its invariants are

\[
c_4(T)=16(T^2+5T+7),\qquad
\Delta(T)=16T^4+144T^3+472T^2+696T+389,\qquad
j(T)=\frac{4096(T^2+5T+7)^3}{\Delta(T)}.
\]

**Theorem.** There exists a finite set \(F\subset\mathbb Q\) such that for every \(t\in\mathbb Q\setminus F\) the fiber is smooth and

\[
\mathrm{rank}\,E_t(\mathbb Q)\ge2,\qquad
\mathrm{ord}_{s=1}L(E_t,s)\ge2,\qquad
L(E_t,1)=L'(E_t,1)=0.
\]

Infinitely many of these elliptic curves are pairwise nonisomorphic over \(\mathbb Q\).

**Proof, with named external inputs.**

1. Exact substitution puts P and Q on \(E_T\). At \(T=0\) this is the smooth rank-two curve [LMFDB 389.a1](https://www.lmfdb.org/EllipticCurve/Q/389/a/1), whose independent generators are P and Q. Any hypothetical integral relation between P and Q over \(\mathbb Q(T)\) specializes at \(T=0\), contradicting that independence. Consequently \(\mathrm{rank}\,E_T(\mathbb Q(T))\ge2\).
2. Since \(\Delta(0)=389\ne0\) and \(j(T)\) is nonconstant, this family is non-isotrivial. [Silverman's specialization theorem](https://www.cambridge.org/core/journals/bulletin-of-the-australian-mathematical-society/article/low-rank-specialisations-of-elliptic-surfaces/D5F0B5DA1AA13722810E85F630672867) (original source: J. reine angew. Math. 342 (1983), 197–211) gives a finite set \(F\) outside which P and Q stay independent. Thus every such fiber has algebraic rank at least two.
3. For **every** elliptic curve over \(\mathbb Q\), the [Gross–Zagier–Kolyvagin low-analytic-rank theorem](https://math.mcgill.ca/darmon/pub/Articles/Research/36.NSF-CBMS/chapter.pdf), Theorem 1.14/3.22, establishes: if \(\mathrm{ord}_{s=1}L(E,s)\le1\), then \(\mathrm{rank}\,E(\mathbb Q)=\mathrm{ord}_{s=1}L(E,s)\). The contrapositive says that algebraic rank at least two forces analytic rank at least two. Apply this to each \(E_t\). Analytic continuation of the *complete* Hasse–Weil \(L\)-function then forces \(L(E_t,1)=L'(E_t,1)=0\).
4. Because \(j(T)\) is nonconstant, it takes infinitely many values on the cofinite rational parameter set, so infinitely many fibers are pairwise nonisomorphic. QED.

### Signed refinement

For any \(t\notin F\) with *independently established* root number \(w(E_t)=-1\), the completed functional equation \(\Lambda(E_t,s)=w(E_t)\Lambda(E_t,2-s)\) forces odd analytic rank. Combining parity with the double zero proves \(\mathrm{ord}_{s=1}L(E_t,s)\ge3\), i.e. \(L(E_t,1)=L'(E_t,1)=L''(E_t,1)=0\). If \(w=+1\) the order is even and at least two.

**Do not infer** that infinitely many members of the family have negative root number. That has not been proved here. The derivation uses the parity of *analytic* order under the functional equation, **not** an assumed equality of algebraic and analytic rank parities.

### Benchmarks

- At \(T=0\): [LMFDB 389.a1](https://www.lmfdb.org/EllipticCurve/Q/389/a/1) records algebraic rank 2 and analytic rank 2. Only its independent generators are used in the proof.
- At \(T=2\): the coordinate change \(X=x+1\) gives [LMFDB 5077.a1](https://www.lmfdb.org/EllipticCurve/Q/5077/a/1) of recorded algebraic and analytic rank 3; its global sign is negative (nonsplit multiplicative reduction at 5077 has local sign +1, and the archimedean local sign is -1). The recorded analytic order is *not* used to prove the family theorem.

## What is *not* established

- The exceptional set \(F\) is finite **but not effectively identified**. This is not a published list of parameters each individually certified by an executable rank algorithm.
- The exact generic algebraic rank and exact analytic orders for arbitrary \(t\) remain unknown here. A common **lower bound** is not the BSD equality.
- No new-to-literature result is established. This is a corollary of classical, established theorems, and the mathematical source inputs have not been independently reproved in MathOS.
- The full BSD conjecture and refined leading-term formula remain open.

## Implementation and reproducibility

[Companion logic audit](../../../mathos/research/bsd_analytic_milestone_02.py) imports the [exact symbolic invariant audit from milestone 01](../../../mathos/research/bsd_rank_two_family.py), verifies the polynomial identities and two benchmark fibers, and checks the integer *logical implication* \`analytic_rank<=1 => algebraic_rank=analytic_rank\` in a bounded truth table. The CI does **not** compute any complex L-value, prove the external low-rank theorem, or certify a rank for any newly sampled curve.

    python -m unittest discover -s tests -p 'test_bsd_analytic_milestone_02.py' -v
    python -m mathos.research.bsd_analytic_milestone_02

The next uncompleted mathematical target is an **effectively described infinite set** \(S\subset\mathbb Q\) for which an unconditional new proof establishes **exact equality** \(\mathrm{ord}_{s=1}L(E_t,s)=\mathrm{rank}\,E_t(\mathbb Q)\ge2\) for all \(t\in S\). No such theorem follows from the present note.

**AI disclosure:** ChatGPT helped propose this classical corollary, draft the research note, design the logic audit and typeset a companion manuscript. Author must independently verify citations, code, and proofs before any submission or claim of priority.
