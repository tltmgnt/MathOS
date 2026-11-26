# F038 — Explicit supergroup-table materialization barrier at the exact cubic stage

PNP_RESOLUTION_STATUS = OPEN. New mathematical, family-specific obstruction and finite reference checks; not a general SAT lower bound, compiled solver, Lean proof, or independent review.

Parent: 728f13aac9ba3f3e50a482dab0786febd6457cf0 (algebraic transfer). The available connector reported no combined statuses or PR-triggered workflow runs for that head; push-triggered CI is unconfirmed. This argument does not depend on the external algebraic algorithm or its claimed exponent.

## 1. Result: explicit materialization can fail even on easily solved SAT inputs

Retain the parent's actual original U: three tape symbols 0,1,2 (2 is blank), head initially at cell 0, input the contiguous normalized selector 1^n 0 followed by the canonical pool bits, fixed transition table syntax and exact allocation 2^(s-ell) to a description of length ell<=s. Let r=9, n=19m-7, L=n+1+2n^2+8 binom(n,3), j=ceil(log2 L) and s=3j.

There are unbounded m for which, among a subfamily of 2^(m^3) selectors, at most 2^((4/5)m^3) selectors admit any original general description that at any time within its exact cubic allocation has explicitly written the designated full lexicographic supergroup table as contiguous raw binary tape symbols (any starting position, including overlap with the input).

All but one of the subfamily selectors are satisfiable. Moreover, a fixed original-machine witness algorithm for the subfamily has time O(L^2 polylog L), so eventually every satisfiable member is accepted by the original cubic stage. Thus, for a 1-2^(-Omega(m^3)) fraction along the specified subsequence, cubic-stage witness production is possible but full explicit table materialization is not possible by any eligible original tape program. This is a separation of tasks, not a claim that those selectors belong to B_3.

## 2. Subfamily and table geometry

Use the parent's full fixed one-hot, OR auxiliary, zero-pin and guard clauses. The only variable cross clauses are the negative ternary clauses selecting digits a,b,c of original groups 1,3,5 (zero-based). Each is independently selected by a bit B(a,b,c), with a,b,c in [0,m). Put M=m^3. There are exactly 2^M normalized inputs, because these M distinct canonical positions are disjoint from the fixed clauses.

Each original tuple survives iff B(a_1,a_3,a_5)=0. Therefore only the all-one mask is UNSAT. In the parent's nine-group supergroup reduction, fix any ninth digit and pair original groups (0,1),(2,3),(4,5),(6,7), with pair index m*x+y. The single variable support belongs to the unique supergroup triple (0,1,2). Its allowed table, with N=m^2, is

    A(u,v,w)=1-B(u mod m,v mod m,w mod m),   0<=u,v,w<N.

The other three owner tables are all one. Let Q=N^3=m^6 be the number of entries in A. Materialization means that for some integer h, at some time tau (including intermediate configurations before halt or timeout), the Q consecutive physical cells [h,h+Q) equal the table's bits in increasing lexicographic order, with w fastest. No supplied table address, extra input or output track is assumed. The theorem treats arbitrary h but only this explicit raw representation.

Both the first and last P=m*N^2=m^5 bits of this table determine B completely: in the first block read u=a,v=b,w=c; in the last block read u=(m-1)m+a,v=b,w=c, for a,b,c in [0,m). Complementing these M sampled entries recovers the mask.

Write e=h+Q. Since Q-L tends to infinity, for every h at least one of e-L and -h is >=(Q-L)/2. Use the right side in the former case and the left side in the latter. Define J=floor(Q/3). On the right use cuts c=L+i, 1<=i<=J, with the exterior half x>=c; on the left use cuts c=-i, 1<=i<=J, with exterior x<c. A cut is between c-1 and c. For all sufficiently large m, P+L<=Q/6, which implies P+J<=(Q-L)/2. Consequently the entire recoverable last P-bit block lies in the exterior half at every chosen right cut, or the entire first P-bit block lies in the exterior half at every chosen left cut. The chosen exterior half is initially blank and the initial head is on the other side. This argument includes tables overlapping, containing or lying far away from the original input.

## 3. Local replay certificate

For a valid original general machine with q>=1 running states and halt state q, record, through time tau, the state after each crossing of a chosen cut and the total number u of transitions whose departing head cell lies in the exterior half. The crossing sequence alternates between entry and exit because the head starts outside that half; the last crossing can enter the exterior, leave it, or be absent. A transition writes its departing cell, then moves.

Given the machine, cut, crossing sequence and u, reconstruct the exterior half at time tau without the original input. Begin with a blank exterior tape. For each entry state, start at the boundary cell just entered and replay deterministic transitions locally until the recorded next exit; the exit transition's write is in the exterior and its resulting state matches the exit record. If there is an unmatched last entry, replay precisely the remaining exterior steps, allowing zero steps when entry is the last transition or enters in the halt state. For a last exit there are no remaining exterior steps. Induction on the exterior visits proves exact reconstruction of every exterior symbol. This works for a time prefix, not only a complete halting execution; u disambiguates a last interrupted visit. No global execution time, input-dependent oracle or actual table value is given to the replay procedure.

Let b=ceil(log2 q)=(q-1).bit_length(), so b=0 for q=1. The running-state crossings can be encoded using b bits each. At most the very last crossing can contain the halt state, which needs one terminal flag rather than a larger alphabet at every event. For k crossings the payload therefore uses at most b*k bits, plus metadata for k, the flag, u, cut and h. Knowing h and the chosen side, the recovered exterior contains a P-bit block determining the entire mask B by Section 2. Thus each such certificate determines at most one mask.

A run with tau<=t transitions crosses the J distinct chosen cuts in total at most t times (a stay move crosses none; a left/right move crosses one). At least one chosen cut has k<=floor(t/J). Select that cut for the certificate. For q=1 its crossing-state payload is empty, regardless of the crossing count; k and the terminal flag still matter.

## 4. Exact description-length accounting and exponential obstruction

The actual general table syntax gives

    ell(q)=4+q+3*q*(bit_length(q)+4).

In particular ell(1)=20, ell(2)=42, ell(3)=61. For all q>=2,

    b / 2^ell(q) <= 2^(-42).

Equality holds for q=2. For q>=3, b<=q and ell(q)>=4+19q, so b/2^ell(q)<=q/2^(4+19q)<=3/2^61<2^(-42) (the last sequence decreases). The q=1 contribution to crossing-state payload is zero. No transition tables are omitted from the general description set, and invalid descriptions cannot materialize through the interpreter. The special builtins return proposals abstractly, not a tape containing an expanded table; the initial tape alone has fewer than Q binary symbols.

Take an unbounded dyadic subsequence: for each sufficiently large integer j choose m_j maximal with L(m_j)<=2^j. L is a strictly increasing cubic polynomial for m>=2 and L(m+1)/L(m)->1. Hence m_j tends to infinity, ceil(log2 L(m_j))=j eventually, and 2^j<=(21/20)L(m_j) eventually. For n=19m-7, L=n+1+2n^2+8 binom(n,3) <=9146*m^3. Also J>=3Q/10 for sufficiently large m.

Every eligible general description has t=2^(3j-ell(q)). At the cut from Section 3 its crossing payload satisfies

    b*k <= b*t/J
         <= (10/3)*(21/20)^3*9146^3*2^(-42)*M
         < (3/4)*M.

The final inequality is exact integer arithmetic:

    40*21^3*9146^3 < 9*20^3*2^42.

For q=1 it holds trivially. We have deliberately used a near-dyadic subsequence, not assumed that the stage rounding factor is negligible at all lengths.

Count all certificates for all eligible descriptions. There are at most 2^(s+1)-1 description strings, and s=O(log m). The chosen cut has O(Q) possible positions. The table start h must be within [-t,max(t,L-1)] because its first cell is nonblank, initially or after a write; a looser O(L+2^s+Q) range suffices. The counts k,u are each <=2^s; the terminal flag has two possibilities. These metadata and description choices contribute only a polynomial in m (equivalently O(log m) bits). The payload contributes at most 2^((3/4)M) for fixed metadata. Since every valid materialization produces a certificate determining its entire B, the number of distinct masks admitting a materialization by any eligible program, even at arbitrary intermediate times and input-dependent table starts, is at most

    2^((3/4)M+O(log m)) <= 2^((4/5)M)

for all sufficiently large members of the subsequence. This is a union bound over all original competitors, not merely one fixed compiler or program. It proves the stated exponential fraction. The constants use the actual original syntax and exact clocks; no practical threshold or explicit asymptotic nonmaterializable mask is constructed.

## 5. Cheap witness production on exactly the same inputs

Parse the original unary header, compute m=(n+7)/19, enumerate the canonical pool, and locate a zero selector bit among the M distinguished clauses. Store its three digits, set the corresponding one-hot choices in groups 1,3,5, and set the other six choices to zero. Reconstruct the full n-bit witness using the parent's prescribed OR auxiliary bits, zero pins and guards. If the mask is all one, halt on a blank. On the promised inputs this produces a valid witness iff the instance is SAT.

A fixed sequential multitape bit implementation uses O(L polylog L) time and space, with binary counters and no indexed lookup into the outer tape. The earlier fixed-track original-machine simulation, charging raw-input block expansion and final raw witness output, gives O(L^2 polylog L) original transitions and constant description length. Thus this program eventually fits the exact cubic budget on all promised SAT inputs. This is a machine-existence proof, not a compiled transition table. For the many masks in Section 4 on which explicit table materialization is impossible, this direct solver need not produce A at all. The obstruction consequently concerns a representation choice in the algebraic-transfer route, not the difficulty of finding a witness.

## 6. Finite reference checks and proof boundaries

Separate JavaScript checks used the canonical pool, actual distinguished clause positions, all 256 masks at m=2 and 32 fixtures at m=3. They checked 39,712 full-table entries and 5,824 recovery-bit reads across the first/last P-bit blocks, and reconstructed witnesses for 286 SAT masks. A separate local-replay reference exhaustively enumerated all 5,832 one-state tables and sampled 256 two-state and 256 three-state tables, checking 152,256 bounded run/cut combinations on two raw inputs, three clocks and four exterior cuts (including a cut at the initial origin). These include timeouts, terminal entries/exits and zero-step final visits. It reconstructed the exterior tape with zero discrepancies. Further checks covered 99 cut-geometry cases, 12 near-dyadic size checks and 127 state-count encoding checks; the strict rational slack was checked by exact integer arithmetic. These are finite reference checks, not executions of full cubic schedules or an asymptotic proof by enumeration.

The accompanying Python regression checks the same counts, actual normalized selector positions and selected original verifier controls. Its execution and exact-head CI remain unconfirmed at writing. The mathematical obstruction assumes explicit contiguous raw binary lexicographic materialization of this particular A. It does not prohibit implicit tables, a different layout or compression, partial/blockwise contraction, recomputation, or an algebraic algorithm that never forms A. In particular it does not establish a lower bound for all methods of computing hyperclique or SAT. The external preprints are neither assumed nor audited here.

Next priority: seek a contraction algorithm that consumes the original small forbidden tables implicitly and never materializes the supergroup tensor, charging every physical tape operation. Alternatively seek a different adversarial family that cannot be solved by earlier direct witness reconstruction. Nine-group general original-machine cubic coverage is still open; no unbounded B_3 result follows. Finite cubic interval 52..233 and reported Lean count are unchanged and not recounted. Promotion NONE.
