# F038 / direct unrestricted route — full-input crossing transcript adversary

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Parent fdc8a45a4ee97c5629c237b1cc06e3f5d8d89989: https://github.com/tltmgnt/MathOS/actions/runs/45734377327 (success). Six parent workflows passed at inspection; TOPO-406 was still running.

## Goal

Keep the exact universal scheduler U, selector ordering, three-symbol one-tape interpreter and clock of the preceding two unrestricted cycles. The prior prefix adversary defeated programs that could not read the distinguishing input. Here we also account for all surviving programs that can read the full input, by their actual tape crossings. The resulting bad-instance theorem reaches a near-quadratic weighted stage budget, not just a linear one. It remains specific to this U, and does not settle exponent two or any higher exponent. Classical crossing-sequence and disjointness arguments are used; no claim of novelty. Seven MRA-X roles are locally authored records, not independent agents.

## Constructive track: a separated disjointness encoding in the same selector pool

Let m>=1, n=32m, M=m^3, N=|U_n|, L=n+1+N. Use three groups of m original variables in positions 8m+1 through 11m, and three equal copies in positions 24m+1 through 27m. For each original group require exactly one bit true: pairwise negative binary clauses for at most one, and a prefix OR chain with m-1 fresh variables and forced output for at least one. For m=1 just use a unit. The auxiliary variables occupy the first 3(m-1) positions. Binary equality clauses force the copies to agree. A satisfying assignment of these fixed clauses therefore determines one index j in [m]^3, and every index has an extension. The OR auxiliaries are uniquely determined.

For each index j there is an Alice ternary clause negating the three original variables for that index, and a Bob clause negating the three corresponding copies. The two clauses are distinct. Given A,B subsets of [M], select the Alice clauses indexed by A and the Bob clauses indexed by B. With the fixed clauses selected, SAT iff some index is in neither A nor B. Independently force a pattern a on m pin variables in positions 27m+1 through 28m by the four signed ternary lifts of each pin unit, using guards n-1,n as in the preceding cycle. These pins do not affect the disjointness equivalence. All unmentioned selectors are zero.

In the actual unary-n selector encoding define P=L-8 binom(24m,3), E=L-8 binom(21m,3), F=L-8 binom(8m,3), R=P-n, and g=F-E+1. By the increasing width, lexicographic support and sign ordering, all variable Alice selectors occur between P and E-1, all variable Bob selectors occur at or after F, and all pin selectors occur at or after F. Positions are zero-based tape cells including the unary header. This follows because the ternary suffix beginning with first variable greater than j contains 8 binom(n-j,3) clauses. Fixed clauses can occur anywhere but agree on all inputs. Thus every cut c in [E,F] separates Alice from Bob (cut between c-1 and c), with identical padding/fixed bits on either side as appropriate. R and g are positive Theta(L), and M=Theta(L).

Fix a stage s, with m>s+1 and s-3<n so the exhaustive built-in is inactive. A general description of length ell has t=2^(s-ell) simulated steps. For t<=R, the preceding clock-locality lemma (including final output read of n consecutive cells) applies to the common prefix of all these instances, even though it includes fixed nonzero selectors. Collect the pin projections of all such well-formed emissions by simulating the common prefix baseline, and include zero to eliminate constant/p mod 4 built-ins. There are fewer than 2^(s+1) such patterns including the reserved zero (constant-zero description already provides that pattern when s>=1); 2^m is larger. Choose one missing pattern and fix it identically on all instances. Invalid programs and built-ins are now harmless. Only valid general programs with t>R need further consideration. Their number D is at most 2^(s+1)/R. This selection needs polynomial time in L+2^s, not polynomial uniformly in binary s. No oracle or SAT solution is used.

## Full-input splice lemma with clock and output verification

For any cut c, a run of a surviving program on an UNSAT input is recorded by:
- the ordered states entered just after each head crossing of c (directions alternate, starting from the left);
- the number of transitions executed on each side, counting a crossing transition on its departing side;
- timeout versus halt with a malformed output versus halt with a well-formed but falsifying output;
- on halt, the final head position, and either an output offset at which a blank is read or the index of a selected clause falsified by the emitted assignment.

The selected-clause certificate exists because the input is unsatisfiable; the parent verifier accepts exactly n binary bits satisfying every selected clause. Use a deterministic choice, e.g. first blank or first violated clause. The clock is not ignored. Two runs of the SAME program with equal records can be spliced: take the left initial tape and left local execution history from the first, the right ones from the second. Local determinism and equality of the crossing state sequences imply by induction over crossing events that the actual combined run follows these local histories in order. A crossing writes only on its departing side, then enters the other side at the boundary cell in the recorded state. The last local segment is in the side determined by crossing parity. Equal local transition totals preserve the same full halting or timeout clock, so a timed-out splice cannot gain extra steps. This applies also when a halt transition crosses the cut.

If both records indicate timeout, the splice times out. For halts, the common head position determines the n output cells; each comes from the corresponding original side's final tape. A common blank-offset certificate remains a blank, even if the output window straddles the cut. For a common violated-clause certificate, each literal's output position carries the same falsifying bit in both original runs, so it remains false after splicing. The clause is selected on both original inputs; its selector cell is therefore selected on the splice. Thus the combined output is rejected by the actual verifier. The same holds for the opposite splice. No assumption that the programs finish on one side or have unread input is used. Records are only used for an existence/counting proof, not sent to U for free.

## Counting theorem: simultaneous failure of every program at a near-quadratic stage

Consider the 2^M UNSAT inputs (A,B)=(A,[M] minus A). For each cut record all D surviving programs in a fixed order. Use fixed-size fields for each program's tag (2 bits), left/right transition totals and number of crossings (s+1 bits each), halt head offset by t (s+2 bits, dummy if timeout), and rejection certificate index (u bits, dummy if timeout), with u=ceil(log2 L)+1. Each crossing state uses at most s+1 bits (state count is bounded by description length). Parsing is unambiguous given the fixed program list and crossing-count fields. Metadata size per program is 4s+u+7, at most 16u when s<=2u.

For any single input the sum of crossing counts over the g cuts is at most t for each program: a transition crosses at most one cut. The sum of their time budgets is at most (s+1)2^s, by the original schedule. Hence the average bit length of the combined record over cuts is bounded by

    Abar <= (s+1)^2 * 2^s / g + 16u*D
         <= 41u^2 * 2^s / min(g,R),

using s<=2u and D<=2^(s+1)/R. This counts records for all long programs, not just one chosen program.

Choose Q=floor(M min(g,R)/(256u^2)), and s=floor(log2 Q) when Q>=1. For all sufficiently large m, s>=1, s<=2u, m>s+1, s-3<n and M>=8. The average bound is at most 41M/256<M/4. For each of the 2^M no inputs at least half of the cuts have record length <=M/2. Averaging over cuts, some one cut has at least 2^(M-1) such inputs. There are fewer than 2^(floor(M/2)+1) distinct binary strings of that length bound, strictly fewer than 2^(M-1) when M>=8. Thus two different sets A,A' have identical combined records at that cut.

Their crossed inputs (A,complement A') and (A',complement A) are actual inputs in the same pool with the same fixed pin pattern, and at least one is SAT because the sets differ. The witness selects an index from the appropriate set difference; the OR auxiliaries, copies, and pins give an explicit model once the collision is known. By the splice lemma all surviving programs fail on BOTH crosses within their original clocks. All other programs were eliminated by the common prefix. Therefore on the satisfiable cross S_s(p)=0 for the SAME U and SAME stage. It follows that H_(n,s) is satisfiable for every sufficiently large m with n=32m.

Since M,g,R are Theta(L) and u is Theta(log L),

    2^s = Theta(L^2/(log L)^2).

The weighted stage budget needed by U on some satisfiable input is at least Omega(L^2/(log L)^2), stronger than the preceding linear-stage result. Equivalently, for every fixed real alpha<2 with alpha>0, arbitrarily large inputs fail at stage ceil(alpha log2 L), by stage monotonicity and the asymptotic bound. This includes full-input programs within the specified stage clocks. The original target s_k(n)=k ceil(log2 L) for integer k=2 is NOT reached; a near-quadratic budget is not a quadratic budget, much less all polynomial budgets. For the actual scheduler that fully enumerates descriptions this also implies a lower bound on its loop iterations before successful stage. General bit-machine simulation overhead is not free and no corresponding near-quadratic lower bound on every SAT algorithm is asserted.

The argument is constructive in the finite computability sense: enumerate the no inputs and cuts, compute signatures, find a collision, and output a crossed model. This costs exponential in M in general, in addition to bounded simulation and record storage; no efficient collision-finding theorem is supplied. The proof of existence does not require executing that enumeration. The finite prototype checks the encoding and splice mechanism; it does not find the enormous asymptotic collisions.

## Alternative track: obstruction to simply raising the exponent

The encoding is easy with explicit access: check each index for two absent forbidden selectors, then set the one-hot groups, copies, OR auxiliaries and pins. This is a deterministic polynomial-time witness finder on this family, including all adversarially chosen pins. Its implementation in the SAME general machine family has some fixed polynomial simulation exponent. The universal scheduler consequently solves every satisfiable member by some s_K for a fixed K. Thus this family cannot witness the all-exponent statement, even though it supplies actual simultaneous failures at earlier stages. The counting budget also grows beyond M when s increases past the near-quadratic threshold. To continue the unrestricted proof route one needs an adversary with an independently justified computational bottleneck beyond physical tape communication, or a proof of a uniform polynomial cutoff. Replacing the underlying machine by one that artificially delays computation is not a proof against arbitrary polynomial algorithms. No restricted lower bound is substituted for the unresolved theorem.

## Evidence

Independent JS computed geometry/budget constants for m=1,2,4,8,16,32,64,128,256,512 and exhaustively checked the one-hot encoding for group sizes 1..6. It evaluated every pair of two eight-bit forbidden sets: [M,pairs,SAT pairs,total surviving indices,UNSAT pairs]=[8,65536,58975,131072,6561]. It enumerated all 5832 one-state tape transition tables on compact six-cell two-block tapes at clocks 1,4,8 and cuts 2,3,4. On the four complementary no instances it included local times, crossing states, halt head and actual rejection reason in each signature. Every equal-signature pair was spliced in both directions and every crossed output rejected. Rows [clock,machines,no-run records,equal-record pairs,crosses with same record,cross checks,SAT crosses,straddling halt crosses]:
[1,5832,69984,45576,91152,91152,50490,324],
[4,5832,69984,30837,61674,61674,34356,330],
[8,5832,69984,29457,58914,58914,32852,330].
A separate JS test checked local history splicing and mixed output reads over all sixteen two-block tapes (not just no inputs); the committed regression focuses on rejection preservation. Python additionally uses actual pool indices and width-three one-hot/copy/pin clauses to check the real encoding, and compares a tape-trace control to the parent interpreter. The small tape tests are deliberately compact fixtures, not the asymptotic full selector tapes. JS did not execute Python. No novel all-exponent theorem, Lean proof, or independent human mathematical review is claimed.

Forward TGA: NARROWED_RESTRICTED_CASE_ONLY (machine-specific clock range improved while quantifying all programs at each included stage). Next target the exact unresolved H family at integer exponent two and beyond, with a decision-preserving computational obstruction not capped by this finite communication argument. Independent review and exact-head CI required. No universal obligation closes.
