# Phase III — tape reference and candidate projection proof

Run `python tools/mra_x_tape.py --output tape-evidence.json`. The local audit replayed identically: 313 cases (52 across 11 topology families, 256 exhaustive two-variable factor tables, five boundary cases), 297 feasible and 16 infeasible. All optimum, witness and backpointer traces matched the logical reference; optima also matched exhaustive enumeration. Primary runs performed 121,944 simulated transitions, including 100,558 unit head moves. Thirteen trusted mid-execution snapshots resumed exactly. Maximum tested induced width 4, tape length 116 cells, control program 500 instructions.

The topology-specialized compiler uses scopes, domain sizes, an elimination order and a cost cap, not actual input costs. The machine reads and writes one current cell per transition and moves left, right or stays. Bounded cost and witness registers are part of finite control. This is not the original RE-X implementation, hardware, or a uniform fixed-alphabet Turing machine. Dynamic scope edits are recompiled.

## Informal equivalence
For each boundary assignment the tape program enumerates domain values in logical order, adds the relevant factor rows (infeasibility propagates), and retains the first strict minimum and its backpointer. Induction on the elimination order yields the same projected factors and witness rows. The terminal constant sum yields the optimum. Reverse equality scans recover the witness from tape. Bounded sums use disjoint subsets of original factors. Trusted configurations are assumed; no adversarial snapshot validation is claimed.

For fixed control length L and N tape cells, with successive instruction head positions p_i and p_0=0, the transition count is exactly L + sum_i abs(p_i-p_(i-1)), at most L*N. This is a symbol-level bound excluding compilation, initialization, snapshot I/O and bit encoding.

## Candidate formal proof
`formal/MraXTapeProjection.lean` states scoped optimality preservation under attainment, domination, order and monotonicity assumptions, and witness lifting. It does not certify the compiler or general machine equivalence. Lean was not installed locally. Pinned Lean 4.14.0 CI and axiom-printing are added; acceptance is unverified. No claim registry promotion.

REX-402/403 and VER-603 remain open. Integrate the original RE-X source, establish uniform bit-level encoding, mechanize multi-step compiler equivalence and run independent reproduction. Other curriculum gates are unchanged. This is an opt-in extension, not a 10/10 claim.
