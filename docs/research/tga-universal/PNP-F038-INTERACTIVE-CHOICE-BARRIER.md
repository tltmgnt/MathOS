# F038 — Interactive nonmonotone branch-choice communication barrier

Status: scoped mathematical reduction and executable regression; not a Lean declaration. PNP_RESOLUTION_STATUS = OPEN.
Verified research base: aae85d3561e765c41abd03ba25eda17b770ea59b, dedicated replay https://github.com/tltmgnt/MathOS/actions/runs/45698200544 (success).

## Direct linear-size guarded CNF

Let Alice have x and Bob have y, each in {0,1}^m, m>=1. Introduce selector z and variables t_i,w_i. Fixed clauses are (not z OR not w_i OR t_i) for each i, and the guarded disjunction (not z OR w_1 OR ... OR w_m), split by private chain variables into width at most three. Alice supplies exactly one clause per i: (z OR not t_i) when x_i=1, otherwise (not z OR not w_i). Bob supplies exactly one clause per i: (z OR t_i) when y_i=1, otherwise (not z OR not t_i). The clauses and their possible slots are distinct across the parties; the fixed template is public. There are exactly 1+2m+max(0,m-2) variables and 3m+max(1,m-1) clauses, with 4m possible nonconstant presence slots in two disjoint blocks. In the oriented representation each party's bit is copied to its false-branch presence and true-branch absence coordinates. This is a direct CNF family, not a claim about every graph encoding.

At z=0 all true-branch constraints are vacuous, including the guarded disjunction after existential elimination of its chain auxiliaries. Each shared 1 imposes both t_i and not t_i; in the absence of a shared 1 all t_i constraints are compatible. Thus branch 0 is satisfiable iff x AND y is zero.

At z=1 some w_i must be true, which forces t_i true. Alice's zero bit forbids w_i; Bob's zero bit forbids t_i. Therefore any true w_i certifies x_i=y_i=1. Conversely, given a shared 1, set the corresponding w_i,t_i true and all others false, then extend the chain variables. Thus branch 1 is satisfiable iff x AND y is nonzero. Exactly one branch is satisfiable on EVERY pair, so no off-promise behavior can evade the reduction.

## Arbitrarily interactive selectors

Model: two parties see only their respective private clause blocks and public template, can compute arbitrarily, exchange adaptively chosen bits for any number of rounds, and must output a safe branch. Count all communicated bits, including the final branch bit if needed so that the transcript determines the answer. The selector computes the complement of set disjointness.

Deterministic bound: the 2^m inputs (x, complement(x)) all require branch 0. For distinct x,x', at least one crossed input (x, complement(x')) or (x', complement(x)) has a shared 1 and requires branch 1. Each deterministic transcript leaf is a rectangle, so no two of these 2^m inputs can share a leaf. A binary protocol of worst-case cost c has at most 2^c leaves. Hence c>=m (or c>=m-1 if a single party's output bit is not counted).

Randomized bound: the classical Kalyanasundaram-Schnitger / Razborov two-party set disjointness theorem gives public-coin worst-case communication Omega(m) for fixed two-sided error below 1/2 (equivalently by constant amplification from any fixed such error). Private randomness cannot improve on public randomness. This is independent of number of rounds and local computational power. See Tim Roughgarden, Communication Complexity (for Algorithm Designers), lecture 4, https://www.timroughgarden.algorithmsilluminated.org/w15/l/l4.pdf and Alexander Sherstov, Thirty-Five Years of Set Disjointness, https://web.cs.ucla.edu/~sherstov/pdf/mfcs-disjointness.pdf. Sending the m input bits then announcing the answer uses m+1 bits, so the communication order is tight.

## Multipass consequence

Suppose a streaming selector reads the public fixed template and then the two private presence blocks in fixed Alice-then-Bob order in each of p complete passes, with s bits of mutable state and public randomness. Assume the state captures all retained private information and the scan schedule has no uncharged side channel; the output is produced at the end. Alice simulates her block, sends the state to Bob, who simulates his block, and returns the state before each further pass. Public template processing can be simulated by the holder of the state. The communication cost is at most (2p-1)s+1, counting the output. Consequently (2p-1)s+1>=m deterministically, and ps=Omega(m) for fixed bounded error as m grows. The measure is the number of variable clause slots (Theta(m)), not the bit length of an explicitly serialized DIMACS file (which also encodes variable indices). This does not cover arbitrary interleaved or random-access scans, or state with uncharged external storage.

## Validation

Exhaust every x,y for m=1,...,6; check both restricted CNFs with the existing finite exact SAT oracle; check every pair of distinct complement inputs for the crossed contradiction; verify clause slots are distinct and the local blocks depend only on their own data. Expected: 5460 inputs, 10920 branch checks, 1092 disjoint, 4368 intersecting, 2667 fooling-pair checks, max 17 variables and 23 clauses.

## Resolution boundary

This extends the one-way reusable summary obstruction to adaptive two-party communication and a fixed-block multipass model, but only establishes a linear lower bound in the direct CNF slot count. It is neither a superpolynomial time lower bound nor an unrestricted circuit lower bound. The finite SAT oracle is for validation only. No claim about P vs NP, formal declaration increment, unrestricted selector impossibility or main-branch change follows.
