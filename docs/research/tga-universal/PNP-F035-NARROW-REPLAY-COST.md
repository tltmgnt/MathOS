# F035 — Narrow replay and finite model checker cost

PNP_RESOLUTION_STATUS = OPEN.

Based on verified binary byte solver 60dd7370. Reuses F034
ProctorCheckerCost local value/charge meters unchanged, rather than
overwriting that existing module. Extends them to step, batch and
chain value projections and introduces a finite SAT model meter.

Each narrow inference charges at most two parent-list traversals
plus twelve literal equality comparisons. For K=2L+1, S=(m+K)K,
C=m+S, the generated UNSAT chain's charge is at most S(2C+12).
The SAT model's charge is at most L(L+1) for a materialized witness.
Both meters conservatively evaluate both parents or every clause/
batch where the original may short-circuit. The value projection
agrees with the original checker even for unsuccessful witnesses.

17 public theorem candidates; 1030 controls. Strict replay required.
The charges exclude terminal checks, formula binding, range checks,
parsing, arithmetic bit cost, allocation, and other execution overhead.
This is not a full independent checker runtime theorem or an
unrestricted SAT result.
