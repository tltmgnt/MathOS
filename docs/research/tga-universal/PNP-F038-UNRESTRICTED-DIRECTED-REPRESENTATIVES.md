# F038 — Directed representative compression in a single coordinate

PNP_RESOLUTION_STATUS = OPEN. Parent 7a0b7ec3545f47135938525f2afbe09537b31d2a (adaptive quotients). Mathematical machine-existence construction conditional on the inherited spatial-frame/local-log density bounds; executed standalone semantic regression. Not a compiled original-U transition table, Lean proof, or independent review. Parent combined statuses and PR-triggered workflow runs were empty; push CI unconfirmed.

## 1. Result

Use the inherited nine-group normalized selector family, n=19m-7, L=Theta(m^3), negative cross clauses of widths 1..3, fixed one-hot/OR/pin/guard extension. Write F_H(z)=1 iff the exact raw negative clause on support H and digit tuple z is selected.

For a group g and two digits a,b define the DIRECTED substitution loss

    d_g(a,b) = sum_{H containing g} m^(3-|H|)
                  * #{z on H minus g : F_H(a,z)=0, F_H(b,z)=1}.

It counts only newly forbidden contexts when a is replaced by b. It need not be symmetric. The total weight of one signature is 37 m^2. For a nonempty representative set C define

    loss_g(C) = sum_a min_{b in C} d_g(a,b).

Suppose that along a sequence of SAT inputs, for at least one group (which may change with the input), there exists a nonempty C with

    |C|/m -> 0,   loss_g(C)/m^3 -> 0.

There exists ONE fixed deterministic original three-symbol single-tape witness machine, correct on the entire family, which runs in o(m^9)=o(L^3) on any such sequence and hence eventually fits the exact cubic stage. Neither the group, representatives, nor rates are supplied. Space O(m^3 polylog m).

The previous adaptive unary quotient requires approximately homogeneous classes in every group. This theorem needs only ONE compressed coordinate and permits a representative with many extra allowed contexts, even if all its source signatures are mutually far apart in symmetric Hamming distance. This is not a statement about arbitrary compression of pairs of coordinates, and does not establish general exact cubic coverage.

## 2. Exact recovery from a directed replacement

Fix g, C and a map p:[0,m)->C minimizing the directed loss per digit (ties can be arbitrary deterministic). For each of the 37 supports H containing g define

    E_H = {z on H : F_H(z)=0, F_H(z with digit g replaced by p(z_g))=1}.

Then sum_H |E_H|/m^|H|=loss_g(C)/m^3. All exception sets are computable using the raw selector bits and the map. There are no changed supports of width greater than three.

First construct the original selector restricted by negative unary clauses to digits in C on group g. KEEP all other original constraints. For every nonempty E_H construct another branch keeping all original clauses and adding the negative clauses on H excluding all tuples outside E_H. These are at most 38 original-format selector branches with unchanged n,L and actual pins. Their witnesses are original witnesses, not approximate predictions. They may overlap.

Let x be an original satisfying tuple. If replacing x_g by p(x_g) gives a satisfying tuple y, then y is a model of the representative-restricted branch. If it fails, a violated support must contain g because the other digits are unchanged. On that support the old bit is zero and the new bit is one, so x_H belongs to E_H. The original x is therefore a model of the corresponding exception branch. Conversely every model of every branch is an original model because clauses were only added. The OR of branch satisfiability is exactly original satisfiability. This is an existence/witness reduction, NOT necessarily a union of the entire original model set: a successful replacement can change a model. Under unique SAT the replacement, if successful, must be the same model. No uniqueness assumption is needed.

Each branch has a small proper join whenever the associated parameter is small. For the representative branch, any five-group support containing g has allowed density <=|C|/m. For an exception branch, any five-group superset of H has allowed density <=|E_H|/m^|H|<=loss_g(C)/m^3. Empty exception sets are skipped. Thus the inherited k=5 local-log spatial-frame solver covers all branches with the same fixed program, with uniform runtime bounds that vanish relative to m^9 as these density bounds tend to zero. The algorithm can return the first successful original witness; if none exists, halt on blank.

## 3. Adaptive directed facility selection without advice

For each group g form the m-by-m matrix D[a,b]=d_g(a,b), and start with an empty selected set and residual losses R_a=37 m^2. In each of m rounds, add the unused digit b minimizing sum_a min(R_a,D[a,b]); tie by smallest digit. Update R_a and retain its current nearest representative (earliest selected on ties). In round one assign a representative even if its distance equals the initial upper bound. With k selected digits write F_k=sum_a R_a. F_0=37 m^3. After any positive number of rounds F_k is the actual loss of the selected set.

Choose the pair (group,round) minimizing the integer k*m^2+F_k over all nine groups and all positive rounds, with fixed tie break. Store the resulting score and rerun the selected group's deterministic rounds to recover its map. Write

    sigma = |C|/m + loss_g(C)/m^3

for the selected normalized score. This is not the optimum facility selection over arbitrary subsets; only the computed greedy score is used.

For completeness, fix a competitor C_* of size h>=1 and loss F_*. At a state with residuals R_a and total F, the sum of gains from adding its h digits individually is

    sum_{b in C_*} sum_a max(0,R_a-D[a,b])
       >= sum_a max(0,R_a-min_{b in C_*}D[a,b])
       >= F-F_*.

Already selected digits have zero gain. If F>F_*, a best unused candidate gains at least (F-F_*)/h. If F<=F_* monotonicity suffices. Iterating gives

    F_k <= F_* + 37 m^3 exp(-k/h)

for k>=1, including h=1. The proof does not assume a metric or symmetry. Take k=ceil(sqrt(h*m))<=m. The minimum computed score satisfies

    sigma <= sqrt(h/m)+1/m + F_*/m^3
               +37 exp(-sqrt(m/h)).

Thus existence of sublinear representatives with vanishing average directed loss implies sigma->0, uniformly in the unknown group or competitor. The map is constructed from actual raw constraints, not guessed.

The parent approximate quotient promise is included. Even if only one group g has at most h signature classes with a common predicted signature in each class and total weighted prediction error E=o(m^3), choose in each class a digit minimizing its own weighted error to that prediction. By the triangle inequality for symmetric weighted Hamming distance through the predicted row, the sum of directed substitution losses to these representatives is <=2E. In particular any parent cell-constant prediction with aggregate normalized error Delta_0 gives E<=m^3 Delta_0 on each group's sections. No outlier splitting or compression of the other eight coordinates is required.

## 4. Original physical time and space

Extract the actual raw canonical selector positions, cross-clause bits and guarded pin bits with the inherited parsing routines. Construct weighted signature rows on fixed sequential bit tapes, sorted by group, digit, support and context; O(m^3) records total. For each group, copy a candidate representative row to scratch and scan all source rows, comparing aligned bits and summing the directed mismatches with binary counters. This builds all m^2 matrix entries in O(m^4 polylog m) bit steps, with O(m^3 polylog m) visited span. Store the matrix in candidate-major order. For each greedy round scan each candidate column against the current residual array (rewind the residual array per candidate); compute the new total and select its least-index minimizer among unused candidates. Even scanning the length-m selected-flag array for each candidate costs only O(m^2 polylog m) per round. Then rescan the winning column to update residuals and labels. Total O(m^3 polylog m) bit work for m rounds and one deterministic rerun. Scores, labels and weights use O(log m)-bit fields. Reuse matrix scratch across groups. The fixed-track sweep simulation from the earlier notes charges O(m^3 polylog m) original moves per bit step, hence O(m^7 polylog m) physical preprocessing, including initial raw conversion.

To compute exceptions, enumerate the raw support bits and emit queries for the translated tuple on H using the saved representative map. Use sequential scans of at most m label records per query and external sorting/merging by support and tuple to obtain the translated bit, carrying the original tuple and bit as payload. At most O(m^3) queries, O(m^4 polylog m) bit time and O(m^3 polylog m) span. Do not perform an original-scale random lookup for every context. Construct each restricted selector by enumerating canonical pool bits, OR-ing the needed restriction with the original bit; unchanged fixed clauses and pins are preserved. This also fits O(m^7 polylog m) physical moves, for the constant number of branches. Use the inherited fixed k=5 solver on a separate reusable encoded product component, preserving outer data. Follow its physical head at constant overhead per local physical transition, mark its visited extent and erase only its scratch on return. These are fixed tracks with constant-width binary encoding over original 0,1,2, not one track per representative or branch. Read its raw witness and copy it to a fresh contiguous raw output region with actual halt head at its first bit; per-bit shuttles O(m^4 polylog m) suffice. On exhaustion halt on blank.

For sufficiently small positive sigma, the inherited local-log bound with e=13/2 gives the total charged time

    O(m^7 polylog m + m^9 sigma^(1/2)(1+log(1/sigma))^a)

for some fixed integer a. Indeed each branch five-join density rho is <=sigma; x^(1/2)(1+log(1/x))^a is increasing sufficiently close to zero. Zero-density branch rejection O(m^(13/2) polylog m) is dominated by preprocessing; outside the small-score regime the inherited unconditional O(m^9) bound for each branch suffices. The representative set is nonempty so sigma>0. All data and solver scratch occupy O(m^3 polylog m) span. No asymptotic log m multiplier is attached to the small-density term. Consequently sigma->0 gives T=o(m^9)=o(L^3) even at arbitrarily slow convergence. Since the actual description length ell of this fixed machine is independent of all inputs, the clock 2^(3 ceil(log2 L)-ell)>=L^3/2^ell eventually covers the promised runtime. No explicit description, numerical threshold or actual stage run is supplied.

A necessary condition for any eventual exact-cubic SAT miss is sigma>=c for some fixed c>0 and sufficiently large m, by the uniform small-score bound and fixed clock coefficient. In particular no unbounded subsequence of misses can admit the above directed representative promise in any single group. This is not sufficient for hardness.

## 5. Linear symmetric complexity, constant directed representatives

Let q=2^d, m=2q+1. Digit zero is special, and every nonzero digit is 1+2x+tau, label x in [0,q) viewed as a d-bit vector, type tau in {0,1}. Use the nine-cycle on groups. On cycle edges allow (0,0), or opposite-type nonzero digits with DISTINCT labels; disallow mixed zero/nonzero. On every noncycle pair allow all pairs involving zero, and two nonzero digits exactly when the binary inner product of their labels is zero AND the actual digits differ. Select exactly the complements in binary negative clauses; no other cross clauses. Every pair has forbidden entries, so the primal graph is K9. Zero status propagates around the cycle and a nonzero solution would two-color an odd cycle. The unique global tuple is all zero, with its inherited unique extension for every pin pattern. It is an easy control, not a hardness example.

In any group choose C={0,1,2}, preserving zero and mapping every nonzero digit to the same type with label zero. On a cycle pair, the substitution can newly forbid only the opposite-type digit with label zero. On any noncycle pair, the zero vector has inner product zero with every vector; substitution can newly forbid only the digit equal to the representative. Thus at most one newly forbidden context per pair, for at most eight pairs per source digit. The directed loss per digit is <=8m and total loss<=8m^2; normalized loss O(1/m). The theorem applies even though the greedy chosen set need not equal this explicit set. The adaptive inequality with h=3 gives sigma=O(m^(-1/2)), and hence O(m^(35/4) polylog m)=O(L^(35/12) polylog L) by the main bound. This is a conservative bound, not a measured transition count.

For every group, choose a noncycle neighbor. Any two nonzero row digits with distinct labels have Hamming distance at least q-2 on this pair's full column domain, because different binary vectors have differing inner products on exactly half the q labels (two digits per label), and the two equality exceptions alter at most two positions. A prediction with B row classes supplies at most B expanded row vectors, regardless of the column partition. Each such vector can be at distance strictly less than (q-2)/2 from rows of at most one label, by the triangle inequality. Each label has two digits. Hence total normalized error on this pair is at least

    max(0,2q-2B)*(q-2)/(2m^2).

For every B=o(m) this tends to 1/4. In fact this obstruction holds separately for EVERY group, even if its neighbor's prediction is unrestricted in the column digit. Thus no sublinear symmetric unary quotient with vanishing error exists, whereas constant directed representatives suffice. This is a representation lower bound, not a computational lower bound.

For completeness the control also evades the preceding full-width, fanout, color and forbidden-degree promises. At each cycle neighbor the zero row is the singleton {0}, nonzero rows have size q-1, exclude zero, and are pairwise distinct (different types have disjoint supports, same types exclude different labels). This forces pairwise incomparable raw and closed signatures. Every prescribed local digit extends to any support of width <=3: for zero use all zero, otherwise color the induced paths respecting its type and choose other labels satisfying at most two homogeneous linear equations and avoiding at most two previous labels. For sufficiently large q there are at least q/4-2 choices for such an extension. All digits remain supported and incomparable after contextual filtering, so width m persists. The same extension count for a compatible choice of nonzero parents gives each directional max fanout Omega(m), hence W=Theta(m^9). The empty-context rows on every noncycle pair include at least q mutually distinct nonempty rows by the distance bound (q>2), and cycle pairs have m such rows, so K=Theta(m). Each noncycle pair has a nonzero-vector row forbidding at least q digits, and cycle pairs have the zero row forbidding m-1, giving D=Theta(m).

All proper joins have density bounded away from zero. For any support of size k<=8, two-color its induced cycle paths. Assign labels sequentially, imposing orthogonality to each previously assigned noncycle neighbor and choosing a label outside the linear span of previous labels. At step j there are at most j-1<=7 independent homogeneous equations, so at least q/128 candidate labels, with at most 128 excluded by the span. For sufficiently large q this gives >=q/256 choices per group, guaranteeing distinct labels and every required binary constraint. Thus at least (q/256)^k tuples are allowed.

Natural-order dyadic occupancy is also bounded away from zero for every proper projection test at sufficiently large dyadic scales. Here M=4q. For 2^18<=t<=q/2, there are at least q/t whole intervals inside the nonzero digit range. Within each such interval [jt,(j+1)t), take labels in [jt/2,jt/2+t/4) for either type. This aligned label block of size t/4 lies entirely inside the interval for both types; it has fixed high bits and freely choosable low vector of dimension log2(t/4)>=16. Choose any nine such intervals. For each proper support two-color its induced paths, and choose low vectors sequentially, maintaining linear independence. For each previously chosen noncycle neighbor impose the low-vector dot product that cancels the prescribed high-bit dot product. Previous low vectors are independent, so these at most seven linear equations have at least 2^(16-7) solutions, more than the at most 128 vectors in the previous span. Pick a solution outside that span. Labels are distinct, all cycle constraints and noncycle dot products hold, and the required types fit the digit intervals. Each proper projection therefore passes independently. At least (q/t)^9 tiles pass, giving nu_k(t)>=4^(-9). For t>q/2 there are fewer than eight blocks per coordinate and the all-zero tile passes, giving nu_k(t)>=8^(-9). For every sufficiently large m this rules out natural-order vanishing-occupancy scales t(m)->infty. This is not an assertion about every relabeling or arbitrary alternative algorithms. All these separation properties follow from the construction, not from exhaustive testing at unbounded sizes.

## 6. Executed semantic verification

Standalone JavaScript ran in the tool runtime; the same audit function was committed with a Node printing entry point. On 16 fixtures at m=2,3 across eight modes, it constructs directed weighted loss matrices, runs greedy selection on every group, checks the single-step averaging inequality against every nonempty competitor subset, selects the best score and checks exact directed error and replacement semantics by direct enumeration. Totals: 19 selected representatives summed over fixtures, total weighted directed loss 8, 36,408 original models, 14,929 original models already in the representative branch, 3 original models with failed substitutions recovered by exception membership, 36,405 successful substitutions, 0 multiple-exception overlaps for the selected maps, 161,560 full-tuple checks and 2 nonempty exception support sets. A separate deliberately nonoptimal map to digit 1 tests 15,441 failed substitutions, 13,377 multiple-exception overlaps and 201 nonempty exception support occurrences. It does not assert that all original models belong to the representative/exception branch union; it checks the precise existence reduction instead.

The q=4,8,16,32,64 control checks explicit directed loss, symmetric row separation and the zero witness. It reports maximum unweighted loss eight across the eight pair sections, with minimum sampled symmetric row distances 3,6,14,30,62. An initial finite linear-extension test incorrectly used dimension four for two prior independent vectors, where the solution set can equal the old span; the assertion failed. Dimension five suffices (8 solutions >4 previous span vectors), and the corrected exhaustive check passed all 3,720 cases of ordered independent pairs and prescribed dot products. The asymptotic proof above uses dimension at least 16 for up to seven prior vectors and is not affected by the failed small test. All assertions in the completed audit passed.

The reference uses indexed host arrays/sets, not the proposed sequential bit tapes. It does not simulate physical movement, run the inherited branch solvers, execute the actual normalized encoder/verifier or exact stage, or exhaustively verify all nine-dimensional occupancy counts. No compiled machine, independent mathematical review or Lean formalization. Exact-head CI unconfirmed.

## 7. Disposition

One-sided representative loss is a strictly more permissive approximation criterion than sublinear symmetric unary quotient error, and only one coordinate needs compression. The next target is context-dependent substitutions in two or more coordinates, with particular attention to the larger supports of the exceptions (a substitution depending on another coordinate can create width-four exception conditions). No uncharged transformation back into width three is asserted. The inherited unconditional O(L^3) with additive stage constant remains distinct from unrestricted exact cubic coverage. Unbounded B_3, general SAT and P vs NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
