# F038 — recursive domain tiling and eight-group cubic cutoff

PNP_RESOLUTION_STATUS = OPEN. Mathematical machine-existence construction and finite reference checks; not a compiled original-U solver, Lean proof, or independent mathematical review.

Parent 7a4fe51abb97d35c64377b449b96fb559b434e23 (mobile projection). The available connector returned no combined statuses and no PR-triggered workflow runs for that head; push-triggered CI is not confirmed. The promised distributed family, original three-symbol tape, U syntax, verifier and weighted clocks are unchanged.

## 1. Result

For each fixed r>=4, the full distributed family (negative cross-group clauses of widths 1..3 and fixed one-hot/OR/pin/guard clauses) admits a fixed original machine with time

    O((m^6 + m^(r+6/(r-1))) polylog(m+2)),

where the normalized input length L=Theta_r(m^3). In particular the seven-group time exponent in L drops from 3 to 8/3, and the eight-group exponent drops from 10/3 to 62/21 < 3. Every satisfiable member of the r=7 and r=8 families is eventually solved at the exact cubic stage, uniformly over masks and pins. No unrestricted lower bound follows.

A fixed number of recursive tiling levels additionally gives, for any fixed r>=6 and epsilon>0, a fixed machine with time O(m^(r+epsilon) polylog(m+2)). The machine, depth, constants and description length can depend on r and epsilon. This is not a single machine uniform in r, epsilon or depth and is not an O(m^r) bound. Nine groups remain undecided at the exact cubic stage.

## 2. Disjoint domain partition and exact local selector

Use the parent's layout n=(2r+1)m-r+2, with X_g[j]=gm+j+1 and r groups g=0..r-1. The fixed clauses make each surviving tuple a in [0,m)^r correspond to exactly one full assignment for the input's fixed pins. A selected negative cross clause forbids the tuples agreeing with its specified digits.

For an integer b with 2<=b<=m let k=ceil(m/b). For each tile t in [0,k)^r, take group g's interval [b*t_g,min(b*(t_g+1),m)). Represent a digit by a_g=b*t_g+z_g with 0<=z_g<b. These intervals partition [0,m); the last interval can be short.

A selected cross clause using groups H is irrelevant on this tile if any specified digit lies outside its tile interval. Otherwise translate its digit d in group g to d-b*t_g and emit the corresponding negative clause in the local r-group layout of size b. This translation is injective on retained clauses. For each group subset of size h there are at most b^h retained clauses, so their total number is <=sum_{h=1}^3 binom(r,h)b^h=O_r(b^3). Add a negative unary clause for every padded digit z with b*t_g+z>=m. Those clauses are disjoint from translated clauses, whose digits are in range.

Build the complete local normalized selector using n_b=(2r+1)b-r+2, the same fixed clauses for size b but with local pins all zero, and precisely these translated clauses and padding units. All other pool bits are zero. This is an instance of exactly the same promised family; padding units are allowed cross clauses of width one, not a new verifier rule. Local auxiliary and pin variables do not represent outer auxiliary or pin variables.

The local assignment corresponding to z satisfies this selector iff all translated digits are in range and the outer tuple a=b*t+z satisfies every original cross clause. Proof: an omitted clause is already true everywhere in the tile; a retained clause has the same truth value under the digit translation; padding eliminates out-of-range choices. The fixed clauses extend each tuple uniquely on both layouts. Thus the local solution sets are in bijection with the outer solution set, with disjoint images across tiles. On finding a local solution, recover z from its one-hot groups and reconstruct the outer full assignment using a and the actual outer pins. It is not sufficient to copy the local witness directly.

## 3. Charged original-machine implementation

The parent mobile-projection theorem gives a fixed local solver for each fixed r with time O(b^(r+2) polylog(b+2)) for r>=4 (including its O(b^6) raw conversion), and visited interval O(b^3 polylog(b+2)). Its failure is a malformed output, and its success is a valid local witness on promised inputs. These are machine-existence bounds, not measured timings.

On one physical tape, use constant-width codes over the three original symbols for a finite product alphabet with a stationary outer input track, mobile scratch and counters, and a local-machine track. Initially expand the raw outer selector to these codes at cost O(L^2), preserving input end markers. Use the parent's stationary-input carry shifts and adjacent-record query-copy operations. Tile counters, indices and coordinates have O(log(m+2)) bits for fixed r. The outer pins need not travel with the workspace during tile extraction; recover them only once, after finding a surviving tuple, or keep them on a stationary marked track. This avoids introducing an O(m) mobile workspace term for arbitrarily small b.

For a tile:
1. Scan the actual full outer selector in its canonical width/support/sign order, using binary counters to identify cross clauses and test membership in the tile intervals. Append the translated local clause records to a mobile list. The list holds O_r(b^3) records of O(log(m+2)) blocks each. Shifting it one block while retaining input symbols costs linear workspace time, and carrying a new record across adjacent records costs the workspace length times polylog(m+2), as proved in the parent. The full scan and rewind/reset cost O(L b^3 polylog(m+2)).
2. Near the outer input endpoint, enumerate the full local normalized pool and emit its unary header, fixed/padding clause bits, and translated clause bits in the actual original order. Test each local pool position against the bounded list by adjacent-record query propagation. Append the bit in an adjacent scratch region. The total is O(b^6 polylog(m+2)), including the cost of moving query data and appending the contiguous local input; there are O(b^3) positions and the workspace and output region have O(b^3 polylog(m+2)) blocks. The smaller fixed clauses and padding are generated directly by binary counters.
3. Simulate the fixed local original machine on its own product-track component, starting at the first bit of that local raw string. Its symbols 0,1,2 are encoded as a finite component of the outer block alphabet; each local physical transition uses only a constant number of outer physical transitions. Local code expansion, tape edits and output take place on this component and never overwrite the outer input or tile counters. A fixed marker denotes the local origin; outer marks recording visited positions are set as the local head passes them, so its used interval can be swept and cleared after failure. Adjacent local steps do not require returning to an outer header. The local solver's visited span is O(b^3 polylog(m+2)); returning to the tile header, testing the local output and cleaning up are within the same polylogarithmic bound times b^3. This is not a global sweep for each local step.
4. On local success read the local witness (the local solver halts at its first output bit); recover each one-hot index with local counters, recover the outer pins by scanning the outer selector, and reconstruct the actual outer witness. The one-time cost, including raw contiguous output and positioning the final head, is O(m L polylog(m+2)) by sequential scans and shuttles of O(L polylog(m+2)) per output bit. On local failure continue to the next tile; after exhausting all tiles halt on a blank.

The fixed number of tracks, finite tags, bit copying and counter arithmetic admit constant-width binary codes with an all-2 unoccupied block, as in the previous construction. No random-access operation, free multitape transition or input-specific description is used. The local solver is a fixed subroutine whose finite control can be incorporated into the outer machine. A constant description length results for fixed r and a fixed chosen tiling depth. Reusing tile and local regions bounds the total visited span by O(m^3 polylog(m+2)), including the stationary outer input. The outer algorithm need only be correct on promised inputs; U still verifies every output.

## 4. Optimization and exact clocks

There are ceil(m/b)^r=O_r((m/b)^r) tiles. For the parent local solver, total time is

    O((m^6 + (m/b)^r (m^3 b^3 + b^(r+2))) polylog(m+2)).

Choose b as the least integer >=2 with b^(r-1)>=m^3, so b=Theta(m^(3/(r-1))) and b<=m for r>=4. It can be computed by ordinary binary arithmetic with O(log m)-bit counters (even trying all b<=m is within the bound). The two tile costs balance:

    (m/b)^r m^3 b^3 = O(m^(r+6/(r-1)))
    (m/b)^r b^(r+2) = O(m^(r+6/(r-1))).

For r=7 this is O(m^8 polylog m)=O(L^(8/3) polylog L). For r=8 it is O(m^(62/7) polylog m)=O(L^(62/21) polylog L). Let j=ceil(log2 L). The original fixed description of length ell is eligible for 3j>=ell and receives 2^(3j-ell)>=L^3/2^ell original transitions. Both improved bounds have a strictly smaller power of L, so eventually fit even with the fixed description penalty and logarithmic factors. The eight-group slack is only 1/21 in the L exponent; no practical inclusion threshold is asserted.

For a fixed r>=6 let a local solver have exponent e=r+delta>r, visited span O(m^3 polylog m), and correctness as above. The same construction with b=Theta(m^(3/(e-3))) gives a new exponent

    e_new = r + 3(e-r)/(e-3),
    delta_new = 3 delta/(r-3+delta).

Use rational exponents at each finite level (start delta=2); if 3/(e-3)=p/q in lowest terms, choose the least b>=2 with b^q>=m^p. The exponents are constants in the fixed program. Since e>=r>=6, the O(b^6) local selector construction and O(m^6) initial cost are dominated. The visited-span invariant persists by region reuse and a fixed number of levels. For r=6, 1/delta_new=1/delta+1/3; for r>6, delta_new<=(3/(r-3))*delta with contraction factor <1. Therefore for any fixed epsilon>0 choose finite depth with delta<epsilon and obtain O(m^(r+epsilon) polylog(m+2)) (or absorb logs using a smaller epsilon). The proof does not choose increasing depth with input size; this is an existence result for a separate fixed machine at each depth. For r=9 these exponents approach cubic in L from above and do not establish exact cubic inclusion or a lower bound.

## 5. Finite reference validation

A separate JavaScript reference constructed canonical outer/local pools, selected arbitrary cross clauses in eight deterministic fixture modes (including all clauses), translated every tile, checked local pool positions and padding, and compared every local tuple with the direct outer predicate. It also checked that in-range tuples partition the outer tuple space and that satisfying tuples have no duplicates or omissions. Layouts r=4..9,m=2,3 with the exact integer b rule gave 96 selectors, 7,744 tiles, 2,795,936 local tuple checks, 243,936 in-range tuple checks, 2,552,000 padded tuple checks, 614,481 retained translated clauses (counting occurrences across tiles), 31,744 padding clauses, and 30,616 satisfying tuples. Zero reference violations. This JS reference uses the cross-clause predicate and actual pool positions, not the full fixed clauses or a compiled original machine.

A Python regression additionally uses the parent's actual normalized input, fixed clauses and verifier on reconstructed witnesses, with bitset projection/reference checks. Python execution and exact-head CI are unconfirmed at writing. Neither finite check demonstrates asymptotic runtime, and no new compiled transition table or Lean declaration is supplied.

## 6. Disposition

Seven and eight groups are now further family-specific upper-bound obstructions. Nine groups are the first fixed group count where the finite-depth tiling argument cannot give a strict subcubic upper bound (even its limiting exponent is three in L). This is not a proof of hardness of nine-partite hyperclique or any broader SAT lower bound. Next seek an actual subcubic improvement or a lower-bound method for nine or more groups that does not merely rely on candidate count. Finite cubic interval 52..233 and reported Lean census unchanged and not recounted. No universal obligation closes. Promotion NONE.
