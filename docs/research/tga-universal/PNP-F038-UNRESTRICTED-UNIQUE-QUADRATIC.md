# F038 — exponential unique-model residuals at the exact quadratic stage

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation, finite regression, not Lean or independent proof review.
Parent 8a882a820d16f9106845c984cba35e4f65e5448e: six exact-head workflows passed, including https://github.com/tltmgnt/MathOS/actions/runs/45752108975 ; TOPO-406 was running at inspection.

## Result

There are unbounded source sizes n=101u (m=10u, M=m^3, L=L(n)) on which

    |B_2^uniq(n)| >= 2^(M/2) >= 2^(L/3000)

eventually. Here B_2^uniq denotes the uniquely satisfiable selectors missed by every actual scheduled description at s=2 ceil(log2 L). Unlike the previous high-multiplicity census, every counted selector has exactly ONE model. This is unconditional, not a consequence of P!=NP or NP!=RP. It is an improvement in the class of actual quadratic failures, not a higher asymptotic time exponent. The finite cubic interval 52..233 is unchanged.

Use the parent quadratic weighted crossing-record bound and full rejection-preserving splice lemma. For the combinatorial rectangle bound, see Tim Roughgarden, Communication Complexity (for Algorithm Designers), lecture 5, Theorem 4.4 and Lemma 4.5, https://timroughgarden.org/w15/l/l5.pdf . No novelty claim for that classical bound or crossing sequences. The project-specific combination requires a revised layout and actual-clock accounting below.

## 1. Compact unique-index encoding

Set m=10u, n=101u, u>=3. Retain the parent n=11m layout up to variable 10m: unused leading m, three original groups of m bits in m+1..4m, three OR auxiliary groups of m-1 bits in 4m+1..7m-3, three equality-copy groups of m bits in 7m+1..10m. Instead of m-2 data pins use v=u-2 data pins at 10m+1..n-2, with two guards n-1,n. Use the same one-hot constraints, OR chains, equality copies and four signed ternary lifts per data pin as in the parent. In addition force every otherwise unused variable to zero by a negative unit clause, including both guards and the three gaps before the copies. The fixed clauses now give exactly one extension for each one-hot index j and fixed data pin pattern. The guards being fixed is compatible with all lifted pins; the four lifts force the pin literal irrespective of guard values.

For each index j in [m]^3 select its left negated original triple iff j is NOT in S and its right negated copy triple iff j is NOT in T, for independently chosen allowed sets S,T subset [M]. Then the number of models is exactly |S intersect T|: one-hot forces the index, OR and copy bits are uniquely determined, pins and unused bits are fixed. The variable selectors encoding S and T occupy distinct positions, so every pair yields a distinct normalized selector. In particular disjoint pairs yield UNSAT and singleton intersections yield UNIQUE SAT.

The complete tape length is L=n+1+2n^2+8 binom(n,3). Put P=L-8 binom(n-m,3), E=L-8 binom(n-2m,3), F=L-8 binom(n-7m,3), R=P-n, g=F-E+1. As in the parent, all varying left selectors lie in [P,E) and right selectors and data pins at or after F. Fixed clauses, including new units, agree across the inputs. All cuts in [E,F] separate S from T. R,g=Theta(L), and

    Mg/L^2 -> C=3*1000*(81^3-31^3)/(4*101^6)
                =1504950000/4246080602404.

This constant satisfies (1/5000)/C < 57/100, by exact integer comparison. Choose u largest with L(101u)<=2^j for each sufficiently large j. Then L/2^j->1 and ceil(log2 L)=j, since the ratio of successive cubic lengths tends to one. At stage s=2j, the number of pin patterns 2^v eventually exceeds 2^(s+1); the exhaustive builtin is inactive since s-3<n. As before choose a common missing pin projection by excluding all valid proposals of prefix-blind descriptions with t<=R and zero. Prefix blindness includes the final output read. All other builtins have absent/invalid outputs or integers <=3 and thus fail the missing nonzero late pin pattern. This choice is independent of S,T and does not require a SAT oracle.

## 2. Average record length on every disjoint pair

For every disjoint S,T (not just complementary masks), take the parent compressed rejection record for each remaining valid general description, at each of the g cuts. The input is UNSAT, so every well-formed output has a violated-clause certificate. The exact record contains local step counts, crossing states including the terminal flag, halt/timeout tag, head and rejection certificate; identical records imply rejection on both crossed inputs at the original clocks. The proof applies to arbitrary pairs of UNSAT inputs, not just complements.

The parent weighted payload bound W<1/5000 and metadata bound o(L) apply unchanged because R=Theta(L), s=2j and the same actual description syntax and clocks are used. Therefore for every disjoint pair the average combined record length over cuts is <=2^s W/g+o(L), uniformly. Divide by M and use the revised constant and length subsequence to get an eventual bound <=57M/100. Markov's inequality implies at least 1/58 of the cuts have record length <=29M/50. There are 3^M disjoint pairs, because each index may be in S alone, T alone, or neither. Some one cut has at least 3^M/58 disjoint pairs with this record bound. Partition those pairs by their entire combined record. The number J of classes is at most 2^(floor(29M/50)+1).

For each record class let A be its set of left masks and B its set of right masks. Their Cartesian product is a rectangle of actual inputs all rejected by every scheduled description: for any left mask and right mask, choose one recorded pair realizing each, and splice their equal rejection records. The chosen common pin pattern and blind prefix are unchanged. The rectangle can contain pairs with any intersection size. Only the original recorded pairs are required to be disjoint; the spliced rectangle property is crucial.

## 3. Elementary unique-disjointness rectangle bound

Claim: if a rectangle A x B of subsets of an M-element universe contains no pair with intersection size one, it contains at most 2^M disjoint pairs.

Proof by induction. M=0 is immediate. Split A and B into A0,A1,B0,B1 on the final coordinate and delete that coordinate. Let D_ij be the sets of disjoint reduced pairs in A_i x B_j. D_11 is empty, because such a pair would have intersection exactly one before deletion. Original disjoint pairs number |D_00|+|D_01|+|D_10|. The two reduced rectangles (A0 union A1) x B0 and A0 x (B0 union B1) avoid singleton intersections, since any such intersection would also be singleton in the original with at least one final bit zero. Their disjoint-pair counts are |D_00 union D_10| and |D_00 union D_01|. The subsets D_00 intersect D_10 and D_00 intersect D_01 of D_00 are disjoint: a shared pair would belong to D_11. Hence the sum of those two union sizes is at least |D_00|+|D_01|+|D_10|. Induction bounds each by 2^(M-1), proving the claim.

## 4. Exponentially many distinct unique residuals

Let Z count distinct singleton-intersection pairs whose selectors belong to B_2 in this fixed-pin family. Let H be the set of left masks appearing in those Z pairs. Then |H|<=Z. Remove these rows globally from all J rectangles. Any singleton-intersection pair in an original rectangle would itself be an actual unique residual by splicing, and its left mask would be in H. Thus each remaining rectangle avoids singleton intersections and contains at most 2^M disjoint pairs by the claim. Globally at most |H|2^M recorded disjoint pairs have been removed, because a fixed row has at most 2^M possible right masks. Count the original recorded pairs by the union of remaining rectangles and removed rows:

    3^M/58 <= (J+Z)2^M,
    Z >= (3/2)^M/58 - 2^(floor(29M/50)+1).

The exact integer inequality 2^79<3^50 implies log2(3/2)>29/50>1/2. Hence the difference is at least 2^(M/2) for all sufficiently large M. Distinct masks give distinct selectors and each singleton pair has exactly one model. Finally M/(2L) tends to 3000/(8*101^3)>1/3000 (exact integer comparison), proving the stated lower census. The result does not depend on any efficient record collision finder; the proof counts actual failures without locating an explicit large pair.

## 5. Scope and evidence

Independent JavaScript exhaustively enumerated all rectangles in universes 0..3 (65812 rectangles), checking the maximum disjoint count among rectangles avoiding singleton intersection and the total disjoint mass. It also independently constructed the reduced variable layout with small m=2,3 and one data pin, tested each reconstructed witness and both forbidden-clause families (1586 index truth checks). These small layouts test geometry/semantics, not the asymptotic subsequence. The Python regression checks actual complete normalized pool positions, distinct clause groups, the fixed unique-index extension by exhaustive local one-hot OR truth tables, and the exact rational and integer slack. The classical rectangle argument above supplies the asymptotic combinatorial step, not the finite enumeration. JS did not run the new Python. New exact-head CI, independent proof review and Lean formalization remain outstanding. The same family has a polynomial witness finder by scanning corresponding forbidden bits and recovering pins, so this does not establish all-exponent hardness or unbounded cubic failures. No universal obligation closes; the next direct target remains unbounded B_3 or a uniform polynomial SAT cutoff. MRA-X roles are locally authored records.
