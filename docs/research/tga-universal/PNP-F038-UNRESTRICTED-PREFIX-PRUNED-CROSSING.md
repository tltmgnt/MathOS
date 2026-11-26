# F038 — common-prefix pruning and directional Kraft refinement

PNP_RESOLUTION_STATUS = OPEN. Finite mathematical/computational existence derivation, not Lean or independent proof review.

Parent e37fc29046649d29733a8d3c9c69c95e32930c18: exact-head Proctor https://github.com/tltmgnt/MathOS/actions/runs/45747127711 passed; six workflows passed, TOPO-406 still running at inspection.

## Result

For n=189 and n=190, the unchanged U exact cubic stage has uniquely satisfiable residuals. The proof combines a short exact common-prefix computation with a refined incoming-word counting argument. Together with the previous finite results, existence is derived at 179 sizes, namely 52..185 and 189..233. Only 186..188 remain uncovered within 52..233. No new asymptotic exponent, specific missed selector or unbounded sequence is established.

## 1. Prefix pruning without mistaking timeout for rejection

Reuse the preceding all-n-bit separated pin family and directional shape census. Every family member is ternary-only. Hence its actual initial tape begins with n ones and then zero through cell P0-1, where P0=n+1+2n^2. The left exterior is blank. For cap=512 and n=186..190, cap+n<=P0, so every initial cap-transition computation, including its final n-cell output in the event of a halt, is independent of the chosen pin bits. Every program that halts in that horizon can solve at most one member, since the family has distinct unique assignments. Exact recurrence of the entire configuration after positive elapsed time proves no subsequent halt, on every family input. A remaining horizon survivor is not rejected, and must be charged using its ORIGINAL t=2^30 clock.

The three high directional classes from the parent are (l,r)=(1,2),(2,1),(2,2). The local C++ prototype enumerates each using first-use transition branching. A partial shape uses six base-ten digits: zero for unknown, otherwise 1+3*next+(move+1). Count all full shape completions in the selected class using recursive digit filling and memoization; multiply by 3^u when u table entries are unknown, accounting for all writes. At first use of an unknown entry branch on every one of the 27 transition triples, restoring tape writes and the transition entry on return. This partitions the full tables, including entries never read. The running-state graph and class membership exactly match the parent shape census, excluding initial halts and unreachable halts. Zero-weight branches may be pruned.

Use a bounded array representing all possible accessed cells on the common prefix, with blank left and binary right. The time checkpoint recurrence is sound: same head and running state and a rolling hash equality propose a candidate, but the earliest prior value of EACH changed cell since the checkpoint is compared to its actual current value. Other cells are unchanged, including all cells outside the represented region. The hash is not a proof and any collision cannot cause a false positive. Since no undefined transition was executed on the segment, a certified cycle repeats under every completion of the partial table. Rollback restores all writes of each branch. Thus the weighted categories early halt, exact cycle, and unresolved at 512 partition the original high classes. They make no inference from failure to halt at 512 to failure at t. For a conservative bound we count both early halt and cycle descriptions as capable of solving one member each (cycles in fact solve none).

The locally executed census at n=189 has survivors [5420457,5966883,1344015] in the three classes; n=190 has [5436432,5962365,1349694]. All five sizes are in the JSON. A second independent JS first-use reference, without any cycle detection, evaluates horizon 8 and agrees with C++ on all three exact halt totals and the combined cycle/horizon totals. This checks the completion accounting in a short fixture, not independent full validation of the 512-step replay.

## 2. Direction-specific Kraft refinement

Let A=2^m and B=2^(n-m) be the numbers of side inputs; let g be the number of cuts, h=g-n, and K=floor((t+g)/2)=kh+r with 0<=r<h. Reuse the parent's exact geometry, local incoming prefix-free proof and discrete convexity. Every successful execution has at least h retained cuts, and summed incoming states over any h of these is <=K. Its summed binary Kraft weight is at least (2h-r)/2^(k+1).

For a remaining high-class program with (l,r')=(1,2), first count successes which have even ONE retained cut with output on the left. At a fixed cut and fixed left input, at most one incoming word can end in a noncrossing halt on the left: its alphabet is unary, so distinct words are prefix-comparable. Equal words give equal output and thus determine the right input. Hence at most A successes per cut, at most gA over all cuts. All other successful executions have output on the right at every retained cut. Their per-cut Kraft sum is bounded by B, not A+B, so their number is at most gB*2^(k+1)/(2h-r). The symmetric (2,1) case is bounded by gB+gA*2^(k+1)/(2h-r). For (2,2) retain the parent bound g(A+B)*2^(k+1)/(2h-r). This argument deliberately counts the unary-side exceptional successes by a union bound; it makes no assumption about which side is selected by a particular execution or whether it crosses every cut.

Write x,y,z for the 512-horizon survivors in these classes. Retain the parent low-class per-cut bound C (sum of class counts times A+B or A+r'B or A as appropriate), and put F=18^3+36^9+4+129140163+54963684-x-y-z. The last difference charges all high descriptions removed by prefix pruning at most one success each. The other terms account for the one-state and three-state prefix-independent proposals, four possible small built-in outputs, and immediate-halt two-state tables; unreachable-halt tables solve none. At these sizes s=72, t3=2^(s-61)=2048 and t3+n<=P0. The original length(4)=92 is too large and exhaustive built-in is inactive. All eligible descriptions are covered. The exact solved fraction is bounded above by

    U = [g*(x B+y A+z(A+B))*2^(k+1)/(2h-r)
         + g*C/h + g*(x A+y B) + F] / 2^n.

Here the symbol U in the displayed bound means the rational fraction, not the universal machine. All integer quantities and exact original clocks are charged. No timed-out table is omitted from the fraction.

## 3. Exact finite inequalities

Minimize the fraction over floor(2n/5)<=m<=ceil(13n/20) as before. Independent BigInt cross-multiplication and the submitted Fraction regression give the following upper ceilings of 10^9 times the fraction:
186:33063423674; 187:10274128294; 188:3282392398; 189:991694590; 190:338182062. Therefore it is strictly below one at 189,190. The exact ceil(2^n*(1-U)) lower counts are stored as decimal strings. The 189 bound is at least 6516738668618612649375491038576586784801086722652752347, and the 190 bound is at least 1038574631789309833482021344445833714781946850816954909894. The values above one at 186..188 do not establish absence of failures. The use of 512-step execution only prunes common-prefix computations; the mathematical counting argument covers the complete original clock for all remaining tables.

## 4. Evidence, scope and next obligation

Local C++ actually executed the short and 512-step census for all five sizes and classes. Independent JS short replay matched the halt census, and independent BigInt arithmetic evaluated exact rational bounds. The integrated submitted C++ has the same computation with argument/partition checks and a Python adapter; the new exact-head CI has not yet been run to completion. No independent review of the proof or Lean formalization is supplied. This is a finite improvement; the pin families have cheap witness reconstruction asymptotically and no finite gap calculation proves an unbounded cubic theorem. The next direct obligation remains unbounded cubic failures or a uniform polynomial cutoff. No universal obligation closes. MRA-X roles are locally authored records.
