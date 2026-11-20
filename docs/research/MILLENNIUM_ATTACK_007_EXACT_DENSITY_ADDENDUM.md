# MathOS 007: exact congruence-class separation of two elliptic curves

**Status:** DERIVED CLASSICAL CONSEQUENCE / NOVELTY NOT ESTABLISHED / NOT CERTIFIED / NOT A BSD PROOF.

This note extends [MathOS research attempt 007](MILLENNIUM_ATTACK_007.md) with a precise classification of **all** good primes at which
\[
E_1: y^2=x^3-x,\qquad E_5:y^2=x^3-25x
\]
have equal point counts. It does not claim a mathematically new theorem. Its proof combines standard facts about quadratic twists, rational 2-torsion, quadratic reciprocity, and the prime number theorem for arithmetic progressions.

## Proposition (exact agreement and disagreement classes)

For every prime \(p\ne 2,5\), put \(N_d(p)=\#E_d(\mathbb F_p)\) and \(a_d(p)=p+1-N_d(p)\).

1. \(N_1(p)=N_5(p)\) **if and only if**
   \[
   p\bmod20\in\{1,3,7,9,11,19\}.
   \]
2. \(N_1(p)\ne N_5(p)\) **if and only if**
   \[
   p\bmod20\in\{13,17\}.
   \]
   In these two classes,
   \[
   N_5(p)-N_1(p)\equiv4\pmod8.
   \]
3. Among all rational primes, the agreement set has natural density \(3/4\) and the disagreement set has natural density \(1/4\).

The sets exclude the bad primes \(2\) and \(5\); omitting finitely many primes does not affect natural density.

## Proof

Let \(\chi_p\) be the quadratic character of \(\mathbb F_p\), extended by \(\chi_p(0)=0\). For nonzero \(d\bmod p\), write
\[
S_d=\sum_{x\in\mathbb F_p}\chi_p(x^3-d^2x),\qquad N_d(p)=p+1+S_d.
\]
Substitute \(x=du\), which permutes \(\mathbb F_p\), and use
\[
(du)^3-d^2(du)=d^3(u^3-u).
\]
Consequently
\[
S_d=\chi_p(d^3)\sum_u\chi_p(u^3-u)=\chi_p(d)S_1,
\quad\text{so}\quad
a_d(p)=\chi_p(d)a_1(p). \tag{1}
\]

If \(p\equiv3\pmod4\), the involution \(u\mapsto-u\) and \(\chi_p(-1)=-1\) give \(S_1=0\), so both traces are zero and the point counts agree.

If \(p\equiv1\pmod4\), the points \(\mathcal O,(-1,0),(0,0),(1,0)\) form the full rational \(2\)-torsion subgroup of \(E_1(\mathbb F_p)\), with four elements. Thus \(4\mid N_1(p)\). Therefore
\[
a_1(p)=p+1-N_1(p)\equiv2\pmod4,
\]
and in particular \(a_1(p)\ne0\). Applying (1) with \(d=5\), the two point counts agree precisely when \(\chi_p(5)=1\), and disagree precisely when \(\chi_p(5)=-1\).

Quadratic reciprocity (since \(5\equiv1\pmod4\)) gives \(\chi_p(5)=(p/5)\). This equals \(+1\) for \(p\bmod5\in\{1,4\}\) and \(-1\) for \(p\bmod5\in\{2,3\}\). Combined with \(p\equiv1\pmod4\), these are respectively the classes \(\{1,9\}\) and \(\{13,17\}\) modulo \(20\). Adding the four classes \(\{3,7,11,19\}\) with \(p\equiv3\pmod4\) proves assertions 1 and 2.

If \(p\bmod20\in\{13,17\}\), then \(a_5(p)=-a_1(p)\), giving
\[
N_5(p)-N_1(p)=2a_1(p)\equiv4\pmod8.
\]
Finally, the prime number theorem for arithmetic progressions gives equal natural density \(1/\varphi(20)=1/8\) to primes in each of the eight reduced residue classes modulo \(20\). Six classes agree and two disagree, proving the densities. \(\square\)

For example, \(p=13\) gives \(N_1(13)=8\) and \(N_5(13)=20\); \(p=17\) gives \(16\) and \(20\).

## Finite regression check (not a proof)

A companion test at tests/test_bsd_007_density.py verifies the exact class prediction, the trace-twist identity, and the mod-8 assertion for all good primes \(3\le p\le401\), using the existing MathOS point-count implementation. It must not be used in place of the proof.

From the repository root:

    python -m unittest discover -s tests -p 'test_bsd_007_density.py' -v

An independent local enumeration of primes through 401 found **77** good primes, of which **55** matched and **22** differed, with **zero** counterexamples. These finite ratios are not the density proof.

## Novelty and the unproved BSD bridge

- Equation (1) is the **standard quadratic-twist trace relation**; the trace-zero case for \(j=1728\) is classical. The mod-20 characterization and density statement above are **a derived presentation of known mathematics**, not an established new research contribution.
- No comprehensive literature review or independent expert novelty assessment has been completed. **Do not represent this as a novel theorem without one.**
- This argument never establishes \(\operatorname{ord}_{s=1}L(E,s)=\operatorname{rank}E(\mathbb Q)\) for every elliptic curve, or the full Birch--Swinnerton--Dyer leading-term formula. The distinction between local traces and the **complete** analytically continued \(L\)-function remains.
- Existing MathOS 007 proof boundaries and open BSD obligations are unchanged; no proof status may be promoted from this note.

Background: [CMI BSD problem](https://www.claymath.org/millennium/birch-and-swinnerton-dyer-conjecture/); [Local data of elliptic curves under quadratic twist (2025)](https://link.springer.com/article/10.1007/s40993-025-00650-w); [MathOS original research note](MILLENNIUM_ATTACK_007.md).
