# TECT-X — proof obligations for a publishable **new** 2-Selmer infinitude theorem

**Version:** 2026-11-19 · **Status:** MAIN THEOREM OPEN · **Intended venue:** not selected · **Submission:** blocked

## Precise research claim to establish (NOT PROVED)

For `n=5+759m` with `m>=0`, set

```text
a_n = (n²+27)/(27-n²),    b_n = 6n/(27-n²)
E_n : y² = x³ - a_n² x + b_n².
```

A genuinely new theorem would prove, with an **explicit arithmetic definition**
of an infinite set `I` of integers `m>=0`, that

```text
for all m in I:
  dim_F2 Sel_2(E_{5+759m}/Q) = 3.
```

Three rational points already yield dimension at least three in the
progression. The missing theorem must eliminate all **additional global
Selmer classes**, not merely count local obstructions or verify samples.
The curve at `m=0` has rank at least four, so `I` cannot be the full
progression.

## Two sufficient *conditional* strategies

### Route A: full 2-descent for an explicit infinite subprogression

Define `d_n=n²-27`, `A_n=n²+27` and

```text
h_n(U) = U³ - A_n² U + 36 n² d_n
K_n   = Q[U]/(h_n(U)).
```

Using an exact cubic étale-algebra realization, define `V_n` as
norm-one squareclasses with the **proved** admissible ramification
conditions. Construct an explicit linear local obstruction map
`lambda_n` with `ker(lambda_n) ≅ Sel_2(E_n/Q)` and mark
`W_n` as the span of the three rational-point Kummer classes.
It suffices to prove

```text
exists infinite explicit I:
  for all m in I:
    ker(lambda_{5+759m}) = W_{5+759m},
    dim_F2 W_{5+759m} = 3.
```

Required proof modules:

1. **Global squareclass parametrization:** prove exactness of the
   norm-one squareclass sequence, including class-group 2-torsion,
   sign and ramification constraints, and distinguish order and
   conductor of the cubic field from the defining polynomial.
2. **All local Kummer images:** compute conditions at primes above
   `2`, bad primes, varying split primes and infinity, with correct
   local models and twists; prove local matrices encode the exact
   Selmer condition, not an enlarged candidate space.
3. **Uniform global elimination:** control additional classes for
   infinitely many `n`, showing the quotient kernel vanishes.
   Local CRT congruences or finite examples are insufficient.
4. **Infinitude with exact hypotheses:** prove that the chosen set
   `I` is infinite without assuming a prime-values or class-group
   distribution theorem that is not known for these polynomials.

### Route B: strict first-moment bound

For positive integers `X`, define

```text
A(X) = (1/X) Σ_{0<=m<X} #Sel_2(E_{5+759m}/Q).
```

If `limsup A(X) < 16` is independently proved, then for some
`ε>0` and all large `X`, at least `ε X/8` members of the
progression have 2-Selmer dimension exactly three. This is an
**elementary conditional counting lemma**, not the sought statistical
estimate. A proof of the estimate must handle exceptional large
Selmer groups and the varying cubic-field class groups and local
conditions. General height-ordered average Selmer theorems do not
imply this one-parameter average.

## Independent review / novelty challenges

**High priority prior art:**
- Patel, Chakraborty, Chattopadhyay,
  *Two infinite families of elliptic curves with Mordell–Weil rank
  at least 3*, Czechoslovak Mathematical Journal,
  published 26 October 2026,
  https://doi.org/10.21136/CMJ.2026.0080-26 .
  **Already contains this Pell identity, model shape, the three
  rational points, and an infinite rank-at-least-three family.**
  These must be cited as prior art, not claimed as new.
- Patel, Chakraborty, Chattopadhyay,
  *On the Mordell–Weil rank and 2-Selmer group of a family
  of elliptic curves*, Ramanujan Journal **69** (2026), article 46,
  https://doi.org/10.1007/s11139-026-01317-5 .
  Investigates 2-Selmer groups in a different polynomial family.
- Zywina, *On the infinitude of elliptic curves over a number field
  with prescribed small rank*, arXiv:2602.10865 (2026).
  Establishes infinitely many geometrically distinct rank-3 curves,
  so general rank-3 infinitude is not new.
- Schaefer--Stoll, *How to do a p-descent on an elliptic curve*,
  Trans. AMS 356 (2004), 1209–1231.
- Bhargava--Shankar / Bhargava--Ho:
  average Selmer results use different counting families; identify
  exact missing uniformity when transferring to this thin progression.

**Novelty test:** A publishable new contribution must involve this
particular full 2-Selmer exhaustion or another substantial independent
theorem, not simply the prior rank-3 construction, finite-field checks,
or the elementary first-moment inequality.

## Required submission deliverables

- [ ] Complete proof of Route A or B, with a verifiable infinite parameter set.
- [ ] Explicitly constructed cubic-field Selmer complexes and exact
      local conditions (if Route A).
- [ ] Uniform quantitative or qualitative infinitude proof, citing
      each imported arithmetic theorem and checking hypotheses.
- [ ] Independent CAS computations of several **full 2-Selmer groups**
      (not merely rational point independence) plus reproducible logs.
- [ ] Independent specialist mathematical review and recorded corrections.
- [ ] A formal novelty/priority comparison to the 2026 Patel and
      Zywina works and any subsequent literature.
- [ ] Human authorship declaration, funding/conflict disclosures,
      journal style/length rules, and rights assessment.
- [ ] Typeset paper with abstract and title that assert only proved results.

**Strict submission rule:** Until the new theorem is proved and independently
reviewed, do **not** use the title/abstract/cover letter
to claim an unconditional Selmer-3 infinitude theorem. No editor submission
is authorized by this document.

## Evidence and machine-readable gate

See [submission status](TECT_X_SUBMISSION_STATUS.v1.json) and
[preliminary LaTeX manuscript](TECT_X_NONISOTRIVIAL_SELMER_PRELIMINARY.tex).
The status file is a workflow declaration, not a substitute for proof.
