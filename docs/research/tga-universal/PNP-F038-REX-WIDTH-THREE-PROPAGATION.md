# F038-REX-024D5J — Physical binary arc consistency and radius-two repair

Parent 8de2b2477cd8ac4b49b1430a25d7514c38388fe1. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE. Global routes 0/4; Omega obligations 0/6.

## Previous verification

D5I exact-head Proctor [45941554645](https://github.com/tltmgnt/MathOS/actions/runs/45941554645), job 140316793497, completed successfully. Domain-four physical replay: t=10969397704, head=505381, span=511571, exact quotient and one-short cutoff passed. Independent native ASCII descriptor replay of four m2 cases and the original Python clause verifier passed, as did governance. The 122349668-bit descriptor remains a valid separate partial witness machine.

## Physical algorithm and invariant

The new worker uses 19 tapes. It loads unary domains as allowed-bit words once. For every pair (g,h), copy the current words into two rank cursors, zero two support words, and scan the canonical binary mask in lexicographic order. At each nonforbidden tuple (a,b) with both old domain bits allowed, set support_g[a] and support_h[b]. After the whole pair mask, replace both domains with their support words, setting a one-bit change flag on any deletion. An empty support word refuses. Repeat all 36 pair scopes until an entire pass causes no deletions. Absent constraints are represented by zero masks and impose no additional restriction if domains are nonempty. The ternary suffix is not traversed during propagation. This is genuine binary arc consistency, not only singleton propagation or host preprocessing.

Each support update is monotone (a supported value was in the old domain), preserves every globally satisfying assignment, and never adds values. At a no-change pass each binary arc has support in the final domain of its neighbor. Because every change removes at least one value, at most 9(m-1) complete changing passes can occur on a nonempty path; one final unchanged pass suffices. Early empty-domain refusal is sound for that reason, but the external blank output does not distinguish this from incomplete candidate search.

After convergence, mark the first or second allowed value of each domain using a distinct symbol x, retaining all other allowed bits. A nine-bit counter enumerates masks in ascending little-endian numeric order, skipping weight >2. Thus at most 1+9+36=46 actual candidate attempts. A missing second value skips that candidate. Validate every higher-arity factor on the chosen tuple. Once its selected row passes, consume the remaining field tokens without rank-cursor updates; canonical shape is a producer precondition. This is not a general search of all ranks or all assignments. Any accepted candidate is converted to the original X/Y/pin/zero witness. A refused radius-three example is SAT. A third original rank can be recovered by propagation when its lower ranks lose binary support.

## Conditional physical resource accounting

Reuse D5I direct producer, five-bit segmented lowering and S notation. On successful genuine normalized inputs, S>=1936, S>=168m^3 and S<=L/16. For 19 tapes there are 58 fixed blocks (G and sentinel/blank/separator triples). Data: S stream bits, 444 scope-table symbols, nine counter bits, 9m domain cells, 3m rank cells, 2m support cells, m pins and n=19m-7 output bits. Clears and rewrites reuse the extents. Hence N<=S+34m+504<=2S.

Conservative source-level pass accounting: each pair costs at most 64m^2+256(m+1) IR primitives (token handling, support writes, rank and support cursor increments and amortized rewinds, loading/clearing/copying four scratch words, two domain updates and fixed dispatch). The one-bit flag update is constant work per deletion. A whole pass has 36 pairs and additional rewind/skip of the bound, pins, unary and binary-prefix stream and scope-table positioning, which together fit the slack in 15000m^2 per pass. No ternary mask body is scanned in propagation. At most 9m+1<=10m passes, so at most 150000m^3<=893S primitives. The prior D5I per-attempt 140S allowance covers selecting marks, stream reset/skip, factor validation, scratch loading and terminal handling; 46 attempts cost at most 6440S. Counter increments/checks are bounded by 512 iterations over nine bits (well within 64S), and initial setup/emission overhead is covered by 200S. Thus use T<=8192S. These are deliberately loose source-level macro costs, not machine-checked certificates.

W<=(26N+16)T+8<=524288S^2. With the inherited producer P<=35000L^2, bridge I<=128S^2 and projector O<=256S^2, conditional total t<=35000L^2+524672S^2<=2^16 L^2. Bridge has 30 additional encoded prefix bits over D5I, still covered by the prior bridge slack. Producer bound for arbitrary normalized inputs and original compiler proof remain inherited assumptions.

Descriptor ell=165869273 gives sufficient cubic admission threshold H>=ell+16=165869289, still astronomical. No finite measured fixture is admitted at cubic stage by this descriptor.

## Executed evidence

Original compiled states 3481614 (producer 230467, bridge 327, worker 3250693, projector 126, blank 1). Exact quotient 2099611 states, 10444842 transition checks, ell=165869273. More coverage costs more descriptor bits than D5I. Before the suffix-skip optimization the compiled quotient was 2095609 states / 159266288 bits. Suffix skip crosses the 2^21 state-number width boundary, so it has a nontrivial descriptor penalty. It reduced worker transitions in the source accounting for the two-disjoint fixture from 287563898 to 276982494 (pins [0,1]); this is not a claim of global speedup against D5I. The shared smaller normalization controller remains unimplemented.

Independent simultaneous AC oracle versus sequential physical-IR AC fixed point and candidate selection: 68 cases (8 named, 60 seeded), 40 witnesses, 28 refusals; 17 witnesses gained versus D5I, 27 empty-domain proofs cross-checked with exhaustive tuple oracle, one SAT radius-three refusal. 10017 exact resource arithmetic checks; all successful IR cases checked physical worker accounting and original clauses. The nonempty terminal domain words matched the independent fixed point even on candidate refusal.

Fresh end-to-end physical raw-selector replays with pins [0,0]:

| case | clock | head | span |
|---|---:|---:|---:|
| chain requiring three propagated deletions |425690086|52392|53421|
| two disjoint conflicts requiring two changes |401408188|52392|53421|

Both valid original witnesses and exact worker clocks checked. Chain quotient replay and t-1 cutoff checked interactively. New CI registers all five replay cases, native descriptor replay of these two, Python clause oracle and inherited governance. A combined interactive replay timed out before finishing; split runs established the stated results. Do not claim new CI/native success until confirmed.

Next: confirm D5J workflow, investigate smaller alphabet/controller to cross below the state-width boundary, and extend to ternary support propagation with explicit cost audit. No changes to main or PR #248.
