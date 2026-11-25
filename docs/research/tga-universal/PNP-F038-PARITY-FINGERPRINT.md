# F038 — Affine parity fingerprints and the uniformity gap

PNP_RESOLUTION_STATUS = OPEN.

## Verified starting point

The resolution-first moment obstruction and updated gap model passed
exact-head replay at 2bd3feeb3f82f8135bdee78a1aba86b259ce31ac
(run 45696041554, job 139493565863). All three direct selector
obligations remain open. Historical reported verified count: 1603.

## Global invariant with a completeness argument

For a set S of satisfying n-bit assignments of a normalized 3-CNF,
consider the parity fingerprint

    P_H(S) = ( |S intersect {x : A_i x = b_i}| mod 2 )_i.

Here A_i and b_i are affine hash constraints over GF(2).
Unlike aggregate violation moments, these tests depend on
assignment coordinates. An odd entry proves satisfiability;
the difficult direction is detecting every nonempty S.
The following argument uses the established Valiant–Vazirani
isolation method (Valiant and Vazirani, Theoretical Computer
Science 47, 1986, pp. 85–93,
https://doi.org/10.1016/0304-3975(86)90135-0).
The proof below is explicit; no novelty claim for isolation,
randomized reductions or nonuniform amplification.

For random uniform k-by-n A and k-bit b, each x satisfies
Ax=b with probability 2^-k. Distinct x,y satisfy it jointly
with probability 2^-2k: in each independent row, a dot
(x+y) is unbiased, and the independent right-hand side gives
the remaining unbiased bit. Hence for X=|S intersect {Ax=b}|
and s=|S|>0,

    E X = mu = s/2^k,
    E[X(X-1)] = s(s-1)/2^(2k) <= mu^2.

Choose k=ceil(log2(s))+1, which lies in 1..n+1 and gives
1/4 < mu <= 1/2. Pointwise the indicator of X=1 is at least
X-X(X-1). Taking expectations gives

    Pr[X=1] >= mu-mu^2 >= 3/16.

Consequently some odd-parity test exists at that scale, with
constant probability. The unknown scale can be addressed by
trying every k, rather than knowing the model count in advance.

## Polynomial advice covering every 3-CNF of a fixed dimension

There are at most 2^M distinct nonempty-clause-set normalized
3-CNFs over n designated variables, where

    M = sum_{j=1}^3 2^j binom(n,j) = O(n^3).

Tautologies and duplicate clauses do not affect the model set;
the empty-clause case is trivially UNSAT. For each k=1..n+1
independently draw L=4(M+1) affine tests. For any fixed SAT
formula, the chance that no test at its good scale isolates a
model is at most (13/16)^L. Since (13/16)^4 < 1/2,
the union bound over all formulas is strictly less than one.
Thus for each n there exists ONE list H_n of O(n^4) tests
covering every normalized 3-CNF on that designated variable set.
The total explicit advice length is O(n^6) bits.

For that list, SAT(F) iff P_H(S) is nonzero. The same advice
handles both branches at any variable: append a unit clause
while keeping the original n-variable counting domain.
One may choose false if that branch has a nonzero fingerprint,
true otherwise. This satisfies the single-path preservation
condition because at least one branch of a satisfiable input
is satisfiable.

To query each parity on ordinary 3-CNF, encode each affine
row using a chain of binary XOR gates with fresh auxiliaries.
A gate z=x XOR y has four width-three clauses excluding the
four invalid triples. Pin the final output to the required
right-hand side. Every base assignment has exactly one
extension satisfying these gates and pins when the equation
holds, and zero otherwise. Zero rows with RHS one contribute
an empty clause; zero rows with RHS zero contribute nothing.
The hash formula has O(nk) gates/clauses and preserves counts
exactly, including parity. Count over the designated base
variable set and all introduced auxiliaries; if an oracle
counts only occurring variables, include tautological
clauses for otherwise absent base variables in its encoding.

**Two essential missing uniform ingredients remain:**
1. Deterministically generate a suitable covering list in
   polynomial bit time (existence by the union bound is not
   a construction).
2. Evaluate each parity query in deterministic polynomial
   bit time (the fixture enumerator is not such an algorithm).

Together these would imply P=NP via the direct selector gate.
Neither is established here. The advice argument alone yields
a nonuniform polynomial-time SAT reduction with a parity
oracle; efficient parity would give SAT in P/poly from that
advice, and the randomized isolation reduction would give
NP=RP. Neither conclusion alone establishes P=NP. This is
a sufficient research route, not an equivalence asserting
that P=NP would necessarily yield an efficient parity oracle.

## Why the input vocabulary and counted coordinates matter

Consider any fixed list of q Boolean probe predicates on
n original bits, with q<2^n. Select q+1 distinct points and
form their membership columns in GF(2)^q. They are linearly
dependent. A nonempty subset S of at most q+1 points has
column sum zero, so all q intersection counts are even.
The parity fingerprint is identically zero on both S and
the empty set.

Encode membership in S by an OR of |S| conjunctions fixing
all n base bits. A binary AND/OR gate circuit with O(n(q+1))
gates has a width-three definitional CNF with unique extensions
for accepted base assignments. Pin its output true. This gives
a succinct satisfiable formula whose projected model set is S
and whose parity fingerprint is zero for every test confined
to the original n bits. The linear dependence is effectively
findable in polynomial time given the q+1 measurement columns.

This does NOT contradict the preceding nonuniform existence
theorem: that theorem chooses advice for the total number of
Boolean variables in an unprojected 3-CNF. The membership
encoding introduces extra variables, and its size can grow
with the number of probes. Tests restricted to a predetermined
base domain, with arbitrary existential extensions in the
input formula, are a different model. No impossibility for
polynomial advice depending on the full input dimension,
nor for input-dependent or adaptive probing, is claimed.

## Independent finite evidence

Independent JavaScript execution:
- enumerated affine mask distributions for n=1,2,3 and
  checked singleton and pairwise inclusion probabilities;
- verified the isolation bound on every nonempty model set
  at those dimensions (273 sets total);
- synthesized exhaustive finite probe lists of lengths 2,4,8
  covering every set at each dimension, and checked 798 choices;
- enumerated 2048 base-assignment/hash-equation-pair cases
  to confirm unique-extension CNF encoding;
- found a nonempty set of four points on six base bits,
  invisible to 17 fixed projected parity tests (including
  the full-space test), and checked its definitional
  membership encoding on all 64 base assignments.

All checks passed. The independent random stream differs
from the Python fixture's stream; its exact point set need not
match. The exhaustive advice synthesis has no polynomial
asymptotic bound. The Python audit and exact-head CI are pending.
No Lean theorem candidates are added in this step.

## Research decision

The aggregate moment barrier did not eliminate every global
invariant. Affine parity fingerprints have a genuine global
completeness property, but the above result is conditional
on advice and an oracle. Do not count them as an implemented
universal polynomial selector. In the next resolution-first
cycle, assess a uniform evaluation/construction mechanism or
reject this route if no such mechanism can be established.
The three direct algorithm/preservation/bit-cost gates remain
open. No main change or PR; no new verified theorem credit.
