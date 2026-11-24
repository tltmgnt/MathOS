# Exact finite-domain validation of a C++ polynomial multiplication kernel under TECT evidence governance

**MathOS milestone paper M001 · 2026-11-24 · Research technical note (not peer reviewed)**

## Abstract

We report a deterministic, exhaustive software validation of the MathOS C++17 polynomial multiplication kernel over coefficient vectors of length zero through three with integer coefficients in {-2,-1,0,1,2}. A separate Python arbitrary-precision evaluation oracle checked all 24,336 ordered input pairs at five distinct integer points and verified output lengths. All pairs passed, and an intentionally incorrect product was rejected. A versioned evidence register recorded the bounded claim as SUPPORTED; no general scientific efficacy or independent external reproduction was established. The contribution is a reproducible MathOS engineering milestone, not a new polynomial identity or claim of priority in mathematics.

## 1. Problem and scope

The kernel implements ascending-power integer coefficient convolution. The question is whether the actual implementation returns the exact product, with the specified empty-vector convention, on the declared finite domain. General integer inputs can overflow a fixed-width implementation and are excluded.

## 2. Method and mathematical justification

For each length n in {0,1,2,3}, enumerate every vector in {-2,-1,0,1,2}^n. There are 1+5+25+125=156 vectors and 156^2=24,336 ordered pairs. Compile the actual C++17 source with warnings treated as errors and run a harness calling model::multiply. For nonempty vectors, require output length n+m-1; for empty inputs require an empty output. Independently evaluate the inputs and candidate product using Python exact integers and Horner evaluation at x=-2,-1,0,1,2.

**Proposition.** If two polynomials of degree at most four agree at five distinct points, they are identical. Proof: their difference has degree at most four. If nonzero, it can have at most four distinct roots, by repeated application of the factor theorem. Five roots force the difference to be zero. Therefore, with the length check, agreement at all five points certifies the coefficient vector for each nonempty input pair. Empty inputs are checked directly by output length. With these bounded inputs, each coefficient has at most three products of magnitude at most four, so intermediate accumulation magnitude is at most 12.

## 3. Results

| Measure | Observed |
|---|---:|
| Ordered input pairs | 24,336 |
| Correct pairs | 24,336 |
| Incorrect pairs | 0 |
| Incorrect-product negative control | Rejected |
| Evidence claim state | SUPPORTED |
| External independent reproduction | Not established |

GitHub Actions run [45361551662](https://github.com/tltmgnt/MathOS/actions/runs/45361551662) completed successfully and its logs recorded these results on November 24, 2026. This is an exhaustive census of the declared domain, not a random sample; a statistical confidence interval would not describe coverage of this census.

## 4. Evidence and reproducibility

Source commit: [2c1071fac566ca6ba06597ab4643d99891fa15e9](https://github.com/tltmgnt/MathOS/commit/2c1071fac566ca6ba06597ab4643d99891fa15e9).

From that checkout, with Python 3 and g++ installed:

```sh
python3 evidence_tect/validate_polynomials.py --check
python3 evidence_tect/check.py --self-test
python3 evidence_tect/check.py
```

The deterministic report binds the C++ source digest and is compared on replay. The register binds the report digest. The checker rejects unsupported claims, scope mismatches and unresolved in-scope failed evidence. SHA-256 detects changed bytes relative to a trusted digest; it is not author authentication.

## 5. Limitations and next steps

The result is limited to the stated kernel, input domain, exact oracle and observed toolchain. It does not validate other MathOS modules, larger coefficients, overflow handling, neural reasoning, scientific benefit, deployment or any open Millennium problem. Cross-compiler replay, adversarial mutation tests and external reproduction are separate milestones. Independent reviewers must obtain and run the pinned source themselves; this paper is not peer-reviewed.

## 6. Conclusion

The bounded multiplication claim is supported by actual exhaustive computation with an exact oracle. The appropriate evidence status is SUPPORTED, not ASSURED. The next milestone is adversarial verification of the evidence gate and implementation.

## References and evidence

1. MathOS, [C++ reference kernel](https://github.com/tltmgnt/MathOS/blob/2c1071fac566ca6ba06597ab4643d99891fa15e9/cpp_model/model.cpp).
2. MathOS, [exact oracle implementation](https://github.com/tltmgnt/MathOS/blob/2c1071fac566ca6ba06597ab4643d99891fa15e9/evidence_tect/validate_polynomials.py).
3. MathOS, [recorded validation](https://github.com/tltmgnt/MathOS/blob/2c1071fac566ca6ba06597ab4643d99891fa15e9/evidence_tect/polynomial-validation.json).
4. MathOS, [execution logs](https://github.com/tltmgnt/MathOS/actions/runs/45361551662/job/138332603834).
