# F038 / direct unrestricted route — exact integer exponent two via description-weighted crossing records

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Parent 1cb0ab6d73089d6e263b31c71df89e2c9b1fb0c6: https://github.com/tltmgnt/MathOS/actions/runs/45735135619 (success). Six parent workflows passed at inspection; TOPO-406 was still running.

## Target

Keep exactly the universal scheduler U, unary-n normalized clause-selector encoding, binary program descriptions, interpreter and stage clocks already defined. The previous proof established bad witnesses at a near-quadratic weighted budget. The target here is the exact integer stage s_2(n)=2 ceil(log2 L(n)), not a different machine or artificially delayed computation. The proof below establishes this target at infinitely many n, by exploiting the actual sparse syntax of valid program descriptions, especially the absence of any nonhalt crossing-state information for one-state programs. No novelty claim for the classical crossing argument or its coding ingredients. MRA-X roles are authored local records, not independent agents.

## 1. Exact weights of valid descriptions

For a general tape program with q>=1 nonhalting states the parent decoder uses b(q)=floor(log2 q)+1 bits for a next-state field (including the halt state q). The complete description length and number of valid descriptions with that state count are exactly

    e(q)=4+q+3q(b(q)+4)
    C(q)=[9(q+1)]^(3q)
    w_q=C(q)/2^e(q).

Indeed the header has 3 prefix bits, q unary ones and a delimiter, and there are 3q independent transitions, each choosing one of q+1 states, three written symbols and three moves. Invalid binary strings have no effect. All general program descriptions are distinct and all are included in the same U. For all q>=1, since q+1<=2^b(q),

    w_q <= 2^(-4-q)*(9/16)^(3q) = r^q/16,  r=729/8192.

In the previous rejection-preserving splice record, use a crossing count and one flag indicating whether the final crossing enters the halt state. Each other crossing enters one of q nonhalting states and needs only c(q)=ceil(log2 q) bits, with c(1)=0. These fields reconstruct the complete crossing-state sequence exactly. Keep the original left/right step counts, halt/timeout tag, final head and blank-offset or selected-clause rejection certificate. Thus the earlier splice lemma applies unchanged, including for output reads across the cut, last-transition halts and clock timeouts. Metadata is O(s+log L) bits per program; no per-crossing charge for the sole running state of a one-state program. Do not delete those programs or assume their runs have no crossings.

The weighted total crossing-state cost satisfies

    W=sum_{q>=1} c(q) w_q
      <= w_2+2w_3 + (1/16) sum_{q>=4} q r^q
       = 2^(-6)*(27/64)^6 + 2*2^(-7)*(36/64)^9
         + r^4(4-3r)/(16(1-r)^2)
       < 1/5000.

Here c(q)<=q, the q=1 term is zero, and the last comparison is an exact rational inequality, replayed in Python. For all scheduled general programs, the sum of allocated steps multiplied by their crossing-state widths is at most 2^s W. This holds even when only a subset of programs survives the prefix filter.

### Long-program metadata is lower order

For prefix threshold R=Theta(L), a long program with t=2^(s-e(q))>R has e(q)<=d=s-floor(log2 R)-1. At s=2 ceil(log2 L), d=log2 L+O(1). Let D count the surviving valid descriptions. For the descriptions with e(q)<=d/2 there are fewer than 2^(floor(d/2)+1) binary strings. For the remainder e(q)>d/2 and e(q)<=20q^2 imply q>sqrt(d/40); summing their weights and multiplying by 2^d bounds their count. Since w_q<=2^-q,

    D <= 2^(floor(d/2)+1) + 2^d * sum_{q>sqrt(d/40)} 2^-q
      = o(L/log L).

Consequently total metadata across these programs is o(L). This argument is asymptotic and does not require simulating or storing the enormous set of programs. It counts every valid description, not just distinct algorithms.

## 2. Improved separated SAT encoding

Let n=11m for integers m>=3; let M=m^3. Retain the previous exact three-group one-hot, equality-copy and lifted-pin encoding, but reposition the variables:

- original three groups of m variables: m+1 through 4m;
- three prefix OR auxiliary groups of m-1 variables: beginning at 4m+1 and ending at 7m-3;
- three equal-copy groups of m variables: 7m+1 through 10m;
- m-2 independent pin variables: 10m+1 through 11m-2;
- guard pair: n-1,n.

Unused variables are free. Fixed clauses enforce exactly one bit per original group and equality of the copies; each index j in [m]^3 has an extension. Alice selects ternary clauses negating the original triple at each forbidden index A; Bob selects the corresponding clauses on the copies for B. The encoding is SAT iff A union B differs from the whole index set. Independent pin constraints enforce an arbitrary common pattern, without changing that criterion. All clauses are in the same normalized width-at-most-three universal pool. No selector order changes.

With N=|U_n| and L=n+1+N, the actual tape positions are bounded by

    P=L-8 binom(10m,3),  E=L-8 binom(9m,3),
    F=L-8 binom(4m,3),   R=P-n,   g=F-E+1.

The Alice-variable selectors lie in [P,E), Bob-variable and pin selectors at or after F; all fixed selectors are common. This follows from the actual lexicographic triple-support order and width ordering. Every cut E<=c<=F separates the variable sets. In particular R=Theta(L), and

    M/L -> 3/(4*11^3)
    g/L -> (9^3-4^3)/11^3 = 665/1331
    Mg/L^2 -> 1995/(4*1331^2) > 1/4000.

For s=s_2(n), the m-2 pin bits eventually exceed s+1. The exhaustive built-in is inactive since s-3<n. Run all prefix-blind general programs (t<=R) on a common baseline tape before inserting pins and variable forbidden sets. The prefix contains fixed clauses but is identical up to P for all inputs, including the baseline. Even their final n-cell output read cannot reach P. Avoid all pin projections of their well-formed outputs and zero, which also eliminates every other built-in (their valid proposals are integers <=3 and the pin positions are beyond the first two bits). At most 2^(s+1) patterns need exclusion, so a missing pattern exists for all large m. This pattern is fixed across the whole complementary no-input family. The previous construction of this pattern costs polynomial in L+2^s; no SAT oracle or uncharged output selection is used.

## 3. Exact integer exponent two

For each sufficiently large integer j, choose the largest integer m with L(11m)<=2^j. Since L(11m) is an increasing cubic polynomial and L(11(m+1))/L(11m) tends to one, these choices tend to infinity and

    L/2^j -> 1,   ceil(log2 L)=j eventually,
    2^s/L^2 = 2^(2j)/L^2 -> 1

at the exact stage s=2j. This subsequence is essential: replacing 2^s by L^2 at every length without accounting for the ceiling would be incorrect.

On each of the 2^M complementary UNSAT inputs (A, complement A), take the combined compressed rejection records of all long programs. As before, over the g cuts every transition can cross at most one cut. The average record length is therefore bounded by

    average <= 2^s W/g + O((s+log L)D)
             = 2^s W/g + o(L).

Divide by M and use the exact weight and layout constants on the subsequence. The limit superior is at most (1/5000)/(1995/(4*1331^2)), strictly below 4/5 since the denominator is greater than 1/4000. Hence for all sufficiently large subsequence lengths the average is at most 9M/10 for every no input. At least 1/19 of its cuts have record length <=19M/20, by Markov's inequality. Some one cut therefore has at least 2^M/19 such inputs. There are fewer than 2^(floor(19M/20)+1) possible binary records within this bound, eventually fewer than 2^M/19. The encoding is unambiguous for a fixed program list and cut: fixed-width metadata determines the crossing count and terminal flag and hence the following crossing payload length for each program. Two distinct no inputs have identical records at that cut.

Splice both ways, retaining the exact local times, reconstructed crossing states, terminal head and common rejection certificate for each program. The previous lemma guarantees that every long program rejects its output or times out on both crossed inputs; all blind programs and built-ins were already excluded. At least one crossed instance is SAT since the two sets differ. Select an index in the corresponding difference and reconstruct a source witness via its one-hot groups, copies, OR auxiliaries and common pins.

Thus, with the same U and actual stage s_2(n),

    H_(n,2 ceil(log2 L(n))) is SAT for infinitely many n.

This advances the integer-exponent-two obligation of the unrestricted counterexample family. It is an unconditional existence proof for that machine's clock, not a quadratic lower bound for all ordinary SAT algorithms and not P!=NP. The finite collision search could enumerate all complementary no inputs and records, but is exponential in M; an efficient bad-instance constructor is not claimed. The proof does not execute the asymptotic collision search.

## Alternative and exact remaining gap

The weight W is a fixed positive constant; at s_k=k ceil(log2 L) the crossing upper bound contains a term of order L^(k-1). For k>2, the above proof cannot make it less than M=Theta(L). Moreover this explicit disjointness family has a polynomial-time witness finder: scan forbidden selector pairs, find a surviving index, decode pins, then construct the assignment. It cannot yield counterexamples at every exponent because its fixed solver will be included in U by some polynomial stage. This is a rigorous scope limitation, not a claim that exponent three is false. The use of sparse program syntax, actual crossing records and precise length subsequence closes only the integer-two subobligation. The direct research target remains existence of bad witnesses for every integer exponent k>=3 at unbounded lengths (or proof of a uniform polynomial success bound). A new computational mechanism beyond this fixed family is required; do not substitute a restricted-model lower bound.

## Evidence and cost

Independent JavaScript computed exact integer description counts for q=1..7 and the subsequence lengths using BigInt, and independently simulated compressed records and both crossed executions. It exhaustively tested 5832 one-state programs and 256 deterministic fixtures for each q=2,3 on compact two-block tapes, clocks 1,4,8 and cuts 2,3,4. Rows [q,programs,no records,equal pairs,cross checks,crossings,terminal crossings,payload bits,SAT crosses]:
[1,5832,209952,105870,211740,16238,1692,0,117698],
[2,256,9216,5289,10578,836,104,732,5933],
[3,256,9216,5923,11846,931,109,1644,6668].
Fixture table generation: q=1 enumerate base-18 transition choices in least-significant-first order; q=2,3 use x=seed+1 then x=(1664525*x+1013904223) mod 2^32, option=(x>>16) mod (9(q+1)). Each option indexes (next state,write,move) in that order. Both crossed outputs must retain equal compressed records and reject. A compact tape test is not an asymptotic SAT instance. Actual selector layout checks use m=3,4 and all 15 pairs of modular forbidden-set patterns A={j:j mod 3=a}, B={j:j mod 5=b}; rows [m,n,M,pairs,model checks,surviving models,SAT pairs]=[3,33,27,15,405,216,15],[4,44,64,15,960,512,15]. Python additionally verifies actual pool positions, one-hot/copy/pin witnesses and the exact rational infinite-series inequality. It computes subsequence rows at j=16,24,32,40,48,56,64 without constructing gigantic pools. Independent JS did not execute Python. The mathematical proof is independent of finite fixture success. No Lean formalization or independent human review supplied.

Forward TGA: NARROWED_RESTRICTED_CASE_ONLY — one more integer exponent of the unrestricted predicate established with the exact same machine. No universal obligation closes; exact-head CI required. Next target k>=3 via a different same-U computational obstruction or a universal polynomial cutoff, explicitly charging all construction and simulation costs.
