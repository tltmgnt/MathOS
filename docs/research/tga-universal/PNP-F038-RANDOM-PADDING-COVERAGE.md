# F038 — Random-padding coverage and deterministic hitting obligations

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not a Lean declaration.
Verified base 325c8079baf8cb8bb250b2aec4a995f86edcf995: https://github.com/tltmgnt/MathOS/actions/runs/45706937573 (success).

## Encoding and success mass

This note chooses a free-suffix variant of the previous zero-padding encoding: a raw valid CNF string r of length l is represented by 1^l 0 r s for any binary suffix s. The decoder ignores s, and the assignment ordering is determined by r. Canonical representations use the empty suffix and have linear overhead. Appending an arbitrary binary string preserves validity and the entire raw satisfying relation. Fix a universal witness-search procedure U_free for this encoding, with the verified-acceptance and fixed-program polynomial simulation guarantees of the preceding universal-clock construction. This is a choice of encoding and corresponding machine, not a claim about arbitrary suffixes in the earlier zero-only machine.

For valid f of length N, m>=N, and fixed integer k>=1, define the success mass
p(f,m,k) = Pr_s[U_free(fs) accepts within (m+1)^k actual U_free steps],
where s is uniform on {0,1}^(m-N). An accepted witness is checked against f. On unsatisfiable inputs p is zero by soundness. For integers a,k>=1, let P(f,a,k) be the success probability of one sweep sampling one independent uniform suffix at every length m=N,...,N^a, stopping at the first verified witness. Equivalently
P(f,a,k)=1-product_m(1-p(f,m,k)).
This probability refers to explicitly sampled suffixes, not to a random input distribution. Sampling, padding, simulation and witness verification take polynomial time for fixed a,k. The product expression is a mathematical description, not a demand that the algorithm compute probabilities.

## Exact randomized-clock equivalence

The following are equivalent:
1. NP=RP.
2. There exist fixed integers a,k>=1 and N0 such that for every satisfiable f of length N>=N0, p(f,N^a,k)>=1/2.
3. There exist fixed integers a,k,q>=1 and N0 such that for every satisfiable f of length N>=N0, P(f,a,k)>=N^(-q).

For (1) implies (2), assume SAT has a polynomial-time one-sided-error randomized decision algorithm. By self-reduction it has a randomized polynomial-time witness finder: repeatedly query the zero branch of the next variable, amplifying each query's success probability so that the probability of any false negative along at most polynomially many adaptive queries is <=1/4. If a zero branch is accepted, choose it; otherwise choose the one branch. Correct answers along the path preserve satisfiability, and the final assignment is independently verified. This gives success at least 3/4 on each satisfiable raw CNF and never falsely accepts. It uses a fixed polynomial bound R(l) on random bits for raw length l, with unused bits ignored.

A fixed deterministic program reads the raw formula from the padded input, uses the last R(l) suffix bits as the random tape, and executes that finder. If the suffix is too short it returns no witness. For sufficiently large N, choose constant a so that N^a-N>=R(l) for all l<=N. Uniform random appended bits then supply an exactly uniform tape even if the base f already has a suffix. This program has constant description length and polynomial runtime in m; the universal search overhead therefore fits (m+1)^k for some fixed k at all sufficiently large lengths. On at least 3/4 of suffixes it has a valid witness within the allotted budget, implying (2). This direction needs the free-suffix encoding and charges the random-tape storage, parsing, verification and universal simulation.

(2) implies (3) since the sweep includes m=N^a. For (3) implies (1), repeat independent sweeps ceil(2 N^q) times. For satisfiable inputs the failure probability is at most (1-N^(-q))^(2N^q)<=exp(-2)<1/2; unsatisfiable inputs never accept. Finitely many smaller inputs can be solved exhaustively. This is a uniform polynomial-time RP algorithm for SAT, giving NP subseteq RP by polynomial reductions. RP subseteq NP follows by using a successful random tape as a nondeterministic certificate. The equivalence does not settle NP=RP, much less P=NP.

## Conditional dense hard cylinders

Negating condition (3) yields: if NP!=RP, for every fixed a,k,q>=1 and arbitrarily large N there is ONE satisfiable f of length N with P(f,a,k)<N^(-q). Since each p(f,m,k)<=P(f,a,k), at EVERY length m in [N,N^a] more than a 1-N^(-q) fraction of its 2^(m-N) distinct suffix extensions miss the clock. Thus a conditional negative result holds on an entire cylinder of encodings of a shared formula, rather than on independent unrelated inputs. At m=N^a with a>=2 this cylinder is exponentially large in the padded length, though possibly an exponentially small fraction of all valid inputs. This stronger mass statement assumes NP!=RP, not just P!=NP.

Under P!=NP alone one gets a deterministic list statement: for fixed a,k,q>=1 enumerate the first min(N^q,2^(m-N)) suffixes in lexicographic order at every length m in the window. A uniform polynomial-time solver would result if this list always contained a success for every sufficiently large satisfiable base f. Hence under P!=NP there are arbitrarily large N and a shared satisfiable f for which ALL listed suffixes miss at EVERY length. In particular the number of distinct missed satisfiable inputs at length m is at least min(N^q,2^(m-N)). This conclusion also holds for any fixed polynomial-time enumerable polynomial-size list of suffixes, without assuming that it is lexicographic. It is not a claim of high relative mass under P!=NP.

## Hitting-set obligation

For any fixed a,k,q satisfying condition (3), a uniform polynomial-time generator that, for each input f, produces a polynomial-size list of allowed (m,s) pairs guaranteed to hit a successful pair whenever f is satisfiable would imply P=NP: run the fixed clock on every generated pair and verify each witness. The generator must be uniform and its cost charged; nonconstructive existence of one successful pair per input is insufficient. This isolates a deterministic derandomization obligation conditional on the randomized clock. No general generator is provided. Conversely P=NP gives a suitable polynomial clock that succeeds on every sufficiently long satisfiable encoding; it need not work at a previously chosen exponent k.

These results do not infer average-case hardness over arbitrary CNF inputs, or a lower bound for a fixed deterministic witness algorithm from low success mass in an unrelated encoding. The finite counterexample compilers and polynomial-window sweep are not being used as unrestricted SAT decision oracles.

## Finite audit

Use the previous 12-bit presence-mask toy template, but permit an arbitrary suffix of length j=0..4. Use toy stages (3,4,5,6,2), and for each suffix interpreted as integer v transform each valid-format candidate w to w XOR (v AND 7) XOR j. This deliberately creates variable success mass; it is not universal-machine timing or an RP SAT implementation.

Exhaust 4096 source masks, all 31 suffix variants, and all 15 contiguous suffix-length windows. Compare variant acceptance to exact source models. Count success mass as an exact fraction, calculate independent-sweep failure via integer products, and compare positive sweep mass to existence of a satisfying candidate in the union. Compare with the deterministic list of the first two suffixes at each length. Compile joint all-suffix misses using the previous shared-witness compiler and check all eight witness assignments and exact pinned SAT. Expected: 126976 variant checks, 11944 accepted, 30216 missed satisfiable variants, 84816 UNSAT checks, 20480 mass checks, 61440 window checks, 3656 jointly missed satisfiable windows, 16744 positive-mass satisfiable windows, 4952 deterministic-list misses, 15448 list successes, 1296 positive-mass windows missed by the list, 491520 witness checks. Across satisfiable formula/length pairs 3180 have mass >=1/2, 3124 mass zero and 764 mass one. Accepted suffix counts at j=0..4 are 128,1000,2748,8068,0. These numbers validate logical bookkeeping, not the asymptotic equivalences.

Next: investigate explicit uniform hitting-set constructions for successful padding tapes, with all costs charged, or a direct polynomial clock/lower bound. The randomized equivalence supplies no proof of its antecedent. No new Lean declaration or P versus NP resolution.
