# TECT-X — Vanishing negative floors are RH-equivalent, and compact support truncates primes

**Status:** exact structural equivalence and finite arithmetic-support reduction. **No all-index positivity theorem or RH proof.** The preceding PR #83 constructed a countable dense compactly supported smooth core for Weil's quadratic form. This PR makes the remaining sign barrier precise and supplies a finite prime-power support bound for each matrix entry.

## 1. The vanishing-negative-floor alternative is not weaker

Let H_m be the Hermitian Weil Gram matrix of the *first m* compact bump functions. The matrices are nested: H_k is the leading principal submatrix of H_m whenever m>=k.

**Theorem.** The following statements are equivalent:

(i) H_m is PSD for EVERY integer m>=1.

(ii) There exists a nonnegative real sequence eps_m -> 0 such that
H_m >= -eps_m I_m for EVERY m>=1.

Proof: (i) => (ii) take eps_m=0. For (ii) => (i), choose arbitrary k and vector v in C^k. Extend v by zeros to C^m. For all m>=k, the nested-principal-submatrix property gives v*H_k v >= -eps_m ||v||². Sending m to infinity gives v*H_k v >=0. As k,v are arbitrary, every H_k is PSD.

The proof also works for lower bounds relative to a *consistent nested positive reference form* L_m, since a fixed vector's reference quadratic value is unchanged under zero-extension.

By the compact-bump density and Weil continuity bridge of PR #83, and the classical Weil criterion, (i) is equivalent to RH. Therefore (ii) is **also RH-equivalent**. One cannot declare an all-m sequence eps_m tending to zero as a numerical error estimate: it would be a global theorem of the same strength as RH. No such bound is constructed here.

## 2. Arithmetic advantage of compactly supported tests: only finitely many prime powers per entry

Let a,b in C_c^infinity(R) with supports [a_left,a_right] and [b_left,b_right]. Let tilde(b)(x)=conjugate(b(-x)). Then the convolution h=a*tilde(b) is supported within

    [a_left-b_right, a_right-b_left].

Call the maximum absolute endpoint B. In the additive logarithmic Weil explicit formula, the prime-power terms for h involve its values at +/-log(p^k). If either evaluation is nonzero then log(p^k)<=B, hence

    p^k <= exp(B) <= 3^ceil(B).

The last inequality follows from e<3 and B>=0, without any floating-point evaluation. This is a rigorous, conservative finite integer cap for each entry. Consequently the **prime-power side** of the Weil explicit formula for each compact-bump matrix entry consists of finitely many possible integers. It is not necessary to truncate an infinite prime sum or assume RH to obtain this finite support bound.

The code uses exact Python Fraction arithmetic for support endpoints and the conservative cap; it can enumerate every prime power up to a bounded cap with integer sieving. The *archimedean contribution remains an actual integral/distributional term* and is not computed or certified. The program does not evaluate the bump convolution, complete the Weil formula, or calculate any compact-bump eigenvalue.

## 3. An exact answer to the all-index research request

The existing signed Gaussian coefficient operator in PR #82 has rigorous negative lower bounds for every compression, but those bounds do NOT approach zero for a fixed certified prefix. This PR shows that a successful vanishing negative error theorem for the *correct compactly supported Weil core* is logically equivalent to proving all its finite Gram matrices PSD, hence RH.

There are valid useful partial objectives:
- Prove exact lower estimates on individual bounded-support windows, with explicit dependence on window size.
- Derive independently validated archimedean and finite prime-side integrals for each compact bump, without using zeros as input.
- Find a global operator-theoretic inequality that covers ALL test directions, not merely finitely many windows or dimensions.

No finite experiment can by itself discharge that universal quantifier.

## 4. Reproduce

    python -m unittest discover -s tests -p 'test_riemann_weil_vanishing_floor_gate.py' -v
    python -m mathos.research.riemann_weil_vanishing_floor_gate --count 8 --output artifacts/riemann/weil_vanishing_gate.json

The output lists exact rational support intervals and provably safe integer prime-power caps for all pairs among the first eight bumps, and records every missing theorem with false assurance flags. The mathematical equivalence and prime-support reasoning are written proofs, not formal proof-assistant declarations.

## 5. Sources and scientific boundary

- [Weil's positivity criterion](https://openmaths.org/courses/NT-EXPF/NT-EXPF-04.html)
- [Suzuki, Aspects of the screw function corresponding to the Riemann zeta-function](https://londmathsoc.onlinelibrary.wiley.com/doi/full/10.1112/jlms.12785)
- [MathOS compact bump LF-topology core PR #83](https://github.com/tltmgnt/MathOS/pull/83)
- [Classical compact-window positivity work](https://arxiv.org/abs/2608.24827)

**No all-m PSD, no vanishing all-m error theorem, no unconditional positive Weil Hilbert-space completion, no noncircular zeta-zero operator, and no RH proof are claimed.**
