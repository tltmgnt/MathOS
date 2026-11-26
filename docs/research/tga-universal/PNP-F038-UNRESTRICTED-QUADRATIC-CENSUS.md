# F038 — unconditional exponential quadratic residual census

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation with finite semantic regression; not Lean or independent proof review.
Parent a6c82c4f1cf687efb4ebaa048c36d315d6496b70: six exact-head workflows passed, including https://github.com/tltmgnt/MathOS/actions/runs/45751773081 . TOPO-406 was running at inspection.

## Result

Strengthen the earlier unconditional exact quadratic existence theorem, without changing U or its complete normalized selector representation. Along the same unbounded subsequence n=11m, M=m^3, L=L(n), s=2 ceil(log2 L), for all sufficiently large subsequence sizes,

    |{p in B_2(n): M(p) >= (M/128) 2^(m+5)}| >= 2^(57M/50).

Here M(p) denotes the number of satisfying assignments; M without argument is the disjointness universe size. In particular |B_2(n)| >= 2^(L/2000) eventually on that subsequence. This is a quantitative unconditional lower bound on the residual census of the actual universal search stage, not a lower bound for arbitrary polynomial SAT algorithms. It does not advance the exponent from two to three. The previous exact cubic finite interval 52..233 remains unchanged. The disjointness family is eventually solved at the cubic stage, as established in the quadratic-family cutoff note. This cycle extracts a stronger consequence of the already-proved crossing lemma rather than claiming a new asymptotic cubic construction.

## 1. Parent premises

Use the exact layout and weighted compressed rejection records from PNP-F038-UNRESTRICTED-QUADRATIC-STAGE.md. There are M=m^3 possible one-hot indices. The independently selected forbidden sets A,B have distinct actual selector positions on opposite sides of g separated cuts. For each sufficiently large m in the parent subsequence choose its single common pin pattern excluding all prefix-blind programs and built-ins. For each A subset [M], the input (A, complement A) is UNSAT. For each cut, the combined record of all remaining programs includes actual local clock counts, the crossing sequence, and rejection information. Equal records imply both crossed inputs reject every scheduled program, even when output straddles the cut or a halt occurs during a crossing. The parent proof supplies these facts; this note does not assume a weaker unclocked crossing lemma.

The parent average record bound, uniform over all complementary inputs, is

    average <= 2^s W/g + o(L),

where W<1/5000 and Mg/L^2 tends to 1995/(4*1331^2)>1/4000. The subsequence satisfies 2^s/L^2 -> 1. Consequently the limit superior of average/M is strictly less than 4/5, so for all sufficiently large subsequence lengths average <= 4M/5. This is slightly stronger than the 9M/10 slack used in the original existence argument and follows from its same strict constants. At least 1/17 of the cuts for every A have record length <=17M/20: Markov bounds the fraction of longer records by (4/5)/(17/20)=16/17. Averaging over cuts gives a common cut with at least N=2^M/17 such inputs. Let S be the set of their A masks (its actual integer size is at least N).

## 2. Equal-weight record classes and many far pairs

Partition S by its combined binary record AND its Hamming weight |A|. The latter is an extra mathematical partition label, not a modification of the actual machine or of the splice record. The number J of nonempty classes is at most

    J <= (M+1) 2^(floor(17M/20)+1).

For class sizes s_i, Cauchy-Schwarz gives sum_i s_i^2 >= |S|^2/J, counting ordered pairs including diagonal. This is at least

    2^(23M/20) / [578(M+1)].

We remove all pairs at Hamming distance <= floor(M/64). The Hamming ball size V satisfies, using lambda=1/64,

    V = sum_{j<=floor(M/64)} binom(M,j)
      <= 64^(M/64) (1+1/64)^M
      < 2^(M/8).

The first inequality follows by weighting the binomial expansion by lambda^j, with lambda^j>=lambda^(M/64) for these j. The second uses the exact integer inequality 65^32<2*64^32, so log2(65/64)<1/32 and (log2 64)/64=3/32. At most 2^M V <2^(9M/8) ordered pairs in the entire cube have that distance. Thus the number of ordered pairs in the same class at distance > floor(M/64) is at least

    2^(23M/20)/[578(M+1)] - 2^(9M/8).

The exponent 23/20=1.15 exceeds 9/8=1.125 and 57/50=1.14. The displayed difference is at least 2^(57M/50) eventually, since fixed polynomial factors are subexponential. No numerical starting M is claimed.

## 3. Transfer pairs into distinct actual residuals

For each retained ordered pair (A,A'), use the input (A, complement A'). By construction their records agree at the common cut, so the original full-clock splice lemma rejects every remaining program, and the chosen pins reject all other descriptions. Since |A|=|A'| and A!=A', both directions of the cross are SAT. In fact the surviving indices are exactly A' minus A, of size |A xor A'|/2 > M/128. Unlike the original collision proof, no loss of a factor of two is needed: both ordered crosses are satisfiable. Distinct ordered pairs give distinct selectors because the original two forbidden masks occupy disjoint positions and can be recovered separately.

The exact model multiplicity is also available. For each surviving index, the original 3m one-hot bits, 3(m-1) OR auxiliaries, 3m equality copies and m-2 data pin bits are uniquely forced. All remaining n-[3m+3(m-1)+3m+(m-2)]=m+5 bits are free, including the two guards: each four-clause lifted pin is equivalent to a pin unit for every choice of the guards. Thus each surviving index has exactly 2^(m+5) extensions. The count of models of the cross is |A' minus A| 2^(m+5), exceeding (M/128)2^(m+5). All these selectors belong to the actual B_2, proving the result. Finally M/L ->3/(4*11^3)>1/2000, and 57/50>1, so the stated exponential-in-L lower bound follows on the same subsequence.

This is a lower bound on distinct residual SELECTORS, not on descriptions, proof sizes, or a probability over arbitrary SAT. In particular the complete selector space is much larger. The theorem still relies on the parent splice argument and its machine-cost premises. It uses no hypothesis P!=NP, no efficient collision finder and no actual asymptotic enumeration. It also does not imply even a single unbounded cubic residual: the parent family's subcubic solver explicitly prevents that extrapolation. The census and the model multiplicity are the new quantities.

## 4. Independent finite evidence

Independent JavaScript enumerated all 5832 one-state transition tables and 256 deterministic tables each for q=2,3. For clocks 1,4,8 and cuts 2,3,4 on the parent compact two-bit separated-data fixture, partitioned the four complementary inputs by complete rejection record and weight. It checked the class-square inequality, both ordered crosses, exact equal records, rejection, and the surviving-index count equal to half the distance. It checked 228384 no-input records and 26434 distinct ordered cross executions (counted with repetitions across table, cut and clock). Separately it exhaustively tested synthetic partitions by weight and low-half bits of all masks at M=4,6,8,10,12, verifying the ordered-pair and Hamming-ball inequalities (finite radius floor(M/4), not the asymptotic radius). Python reuses the actual parent compressed records and decoder, checks the exact integer ball bound and geometry constants, and checks free-variable count and representative flipped free-bit models on actual m=3,4 selector formulas. The synthetic partitions are not actual asymptotic crossing partitions. JS did not run the new Python. New exact-head CI and independent mathematical review remain outstanding; no Lean declaration added.

Forward TGA: NARROWED_RESTRICTED_CASE_ONLY. The known unconditional quadratic existence argument yields an exponential residual census with explicit witness multiplicity. The remaining direct target is still unbounded B_3 or a general polynomial cutoff. MRA-X roles are locally authored records, not independent agents. No universal obligation closes.
