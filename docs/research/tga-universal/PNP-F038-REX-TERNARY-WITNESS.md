# F038-REX-022B6 — Physical original Boolean witness recovery

MRA-X 2.0 + RE-X; MRA-X Omega Phase III. Parent REX-022B5 fb03a92be6a0faeaf1625f30e5c11bfa115f1923. Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

## Implemented contract

A single fixed original-format ternary transition descriptor now starts with the original contiguous raw normalized selector at head zero, validates normalization and fixed-path eligibility, deposits forbidden masks and pins, serializes the nested bags, physically isolates and executes REX-020 elimination, recovers the nine selected ranks, and emits the original n-bit Boolean assignment at the physical halt head. No host tape reset, rank recovery, assignment construction or storage update participates in this computation. The abstract machine is independent of input dimension.

The composed descriptor has 278200 nonhalt states, 834600 transition entries, and 19474004 serialized bits. Components: 127040 producer, 116 bridge, 126999 two-bit-projection worker, and 24045 marking/relocation/reconstruction extension states. The ordinary one-bit worker compiler output was compared byte-for-byte against the exact parent and remains identical (126995 states, 8127684 bits). The new compiler mode only adds two-bit projection support; logical elimination rules are unchanged. B6 splices the successful ready transition into a marking pass and the successful projection exit into witness recovery. Producer refusal halts are remapped to blank, so outside-normalization or outside-path refusal cannot produce an accidental one-bit witness for original n=1. UNSAT worker rejection also halts on blank. No physical distinction between these blank refusal categories is asserted; audit labels use observed phase entry. Remaining scratch outside the output word is allowed by the original tape_run contract, which reads n consecutive cells at the halt head.

Scope: strict normalized family with n=19m-7, m>=2, nine X/Y groups and lifted pins, selected negative cross scopes contained in the seven fixed consecutive triple bags. Outside-path refusal is not a SAT decision for other formulas. The fixed machine gives correct SAT witness or blank UNSAT on this family under the constructive invariants below; this is not an unrestricted SAT solver or a proof of P=NP.

## Selected-rank recovery at worker ready checkpoint

B5 preserves the original producer region to the left of h. The isolated worker receives N prepared bits at o=h+11N+3. The B5 isolation argument applies to elimination. At its ready state the worker has a contiguous six-cell encoded product region: opening markers G, selected row headers W, other row headers P, restored field digits d[k][b], field terminators J, masks T, and final R. Its head is at the first block and the previous cell is blank. No used digit u[k][b] or unfinished X close is present after successful logical backtracking and cleanup.

B6 scans this product region forward in finite control. In the first bag, mark all three fields of its W row; in subsequent bags mark only the third field of each W row. The selected row's digit d[k][b] is rewritten to u[k][b], its selected field terminator J to X. Other blocks are left unchanged. The scan stops at R and rewinds to the initial blank boundary, then enters the inherited projection serializer with a new projection table: u[k][b] -> 0b, X -> 11, everything else -> empty. The serializer visits blocks in reverse order and prepends the two-bit code in correct order, using an additional write state for each code prefix. Ordinary single-bit output mode is unchanged. This does not depend on the chosen row being the first row of any bag. The REX-020 consistency invariant and the fixed child code 2 imply every child retains parent positions 1 and 2 and introduces the next variable; root's three ranks and the six later third ranks therefore give the nine global ranks in group order. Each has w=ceil(log2 m) digits. The projected word has exactly R=18(w+1) bits: nine fields of w digit tokens 00/01 followed by 11. This direct ready-state projection deliberately replaces the row-index projection in the B6 descriptor, rather than regenerating every bag from the masks and interpreting row-index bits.

The new projection writes R=O(log m) output bits; in fact R<=N for accepted prepared words since a SAT word contains at least seven rows. Its leftward extent is no larger than the conservative o-8(N+2) bound used for isolation. Thus original producer storage is untouched during marking and projection. Once recovery starts, physical access to that region is intentional.

## Physical rank relocation and Boolean expansion

A compact contiguous rank-token word stands alone in the worker region. From its leftmost bit, test the preceding two cells. If the second is a nonblank workspace bit, the word is already immediately right of the protected separator h. Otherwise shift the entire word one cell left using a moving blank and single held bit; scan back to its start and repeat. All cells between it and h are blank by worker projection cleanup and the B5 isolation construction. The procedure stops at h without crossing into the workspace. It uses no physical coordinate supplied by a simulator.

Reuse the five interleaved binary lanes M=m-1,Y=m-2,A,B,C and the 15 group bits, with A,B initially zero. At h consume each two-bit token by the inherited moving workspace shift (append consumed rank bits to retained selector prefix). On a digit token 0b, set A=2A+b using a carry scan from the least-significant column. The exact selected rank fits the existing bit_length(m) columns. Token 11 ends a rank; the nine group phases are in finite control. To the right of the remaining rank stream, maintain two blank-separated output blocks X and Y (initially empty). For each group loop B from 0 to M. Append [B=A] to X; for B>0 append [A<=B] to Y. Binary equality and order are computed by scans; the highest differing bit determines the result. X appends shift the Y block right one cell with finite carry, Y appends extend its right edge, and every shuttle returns to the workspace separator. Reset A and B before consuming the next rank. Consequently X contains 9m one-hot bits in group order; Y contains 9(m-1) bits encoding Y_j = [rank<=j+1], precisely the unique OR-chain extension.

After all nine rank terminators, physically require the remaining rank stream to be empty. Read the first bit of pin block 49 by counting the 50 mask/pin delimiters across the retained prefix. Append it to Y and rotate the pin block once; count m iterations with B, restoring the original pin order. Append two zero guard bits. Remove the separator between X and extended Y by shifting Y left one cell; scan left to the leading blank, then move right and halt at the first X bit. The output is contiguous and bounded by blanks. Its length is 9m+9(m-1)+m+2=19m-7=n. It is in original variable order, least significant bit first for the original integer witness convention. The actual output uses no host-generated witness.

Induction over tokens, candidate counters and pin rotations gives the exact Boolean assignment from the chosen globally consistent ranks. Every mandatory normalized clause holds by construction: one-hot X, OR-chain extension Y, lifted-pin sign, and negative guard units. Every selected negative cross factor is satisfied by some containing bag's selected row and therefore by the recovered global rank assignment. If the normalized formula is satisfiable, the unique-extension argument gives a global rank assignment, hence nonempty consistent row choices; the worker finds such choices. If UNSAT, no consistent rows exist and the worker halts blank. These are informal constructive arguments, not mechanized proof certification.

## Resource composition

For accepted normalized inputs L=Theta(m^3), N=O(L log L), and R=18(w+1)=O(log L). B4 and B5 provide O(L^2+N^2) producer, bridge and elimination work, with O(L+N) span. The marking pass is O(N) (fixed-width blocks and bounded rewrites). Projection is O(N^2+NR)=O(N^2) by the same monotone shrinking-product and growing-output scans as REX-020. Rank relocation costs O(NR), since the word begins O(N) cells from h and every shift costs O(R). Rank consumption and binary lane scans use O(R log m+m log m) transitions. Output append operations cost O(m(m+R+1)); each output bit causes at most a sweep over rank stream and output blocks. Pin lookups and rotations cost O(m(L+R+log m)) because each traverses the retained selector and masks. Final joining costs O(m). All extra recovery terms are O(N^2+L^2), so complete accepted raw-to-original-witness time is O(L^2+N^2)=O(L^2 log^2 L), worst-case Theta(L^2 log^2 L) over the family (empty constraints cause B4 output append lower bound). Space O(L+N+R+m)=O(L log L). Malformed/outside raw inputs reject before recovery, with inherited producer bound. This is an asymptotically subcubic restricted-family algorithm; no finite-clock deadline, constant-factor bound suitable for original stage admission, or unrestricted SAT result follows automatically.

The original universal search enumerates descriptions of length ell<=s and assigns 2^(s-ell) transitions to each. For this descriptor ell=19474004, the 44654867-step forced fixture needs s>=19474030 for this specific program to have its observed halt budget (ceil(log2 T)=26). This is a budget calculation, not a full universal stage replay, not a statement about the minimal successful stage across all other programs, and not proof of a prescribed stage schedule. The original descriptor is far longer than the tested finite selector stages. A native original codec and interpreter regression is committed but remains unexecuted here.

## Executed evidence

The actual serialized composite descriptor was decoded and simulated from raw original input. Each principal fixture compared against the exact inherited encoder, isolated original one-bit worker, independent exhaustive m^9 assignment enumeration, and the original JS Boolean clause verifier. On SAT, the extracted rank-token stream, full emitted witness, exact length and choice of global ranks matched host reconstruction from the independently run original worker's row certificate. The producer region was checked unchanged at the projection exit. Host checks are observations only.

| Fixture | m | L | N | Models | Result | Physical transitions |
|---|---:|---:|---:|---:|---|---:|
| forced ones |2|37914|245|1|SAT|44654867|
| forced zeros |2|37914|245|1|SAT|44654867|
| multiple rows |2|37914|269|2|SAT|46090469|
| empty bag |2|37914|1229|0|UNSAT|112649341|
| inconsistent nonempty bags |2|37914|365|0|UNSAT|54399245|
| mixed ranks |3|161851|308|1|SAT|522655657|
| nonfirst root |2|37914|389|1|SAT|58391750|

Seven principal completions, 389335 raw bits, 3050 prepared bits, 883496196 physical transitions, five SAT witnesses totaling 174 original bits and two UNSAT refusals; zero observed witness/rank/decision discrepancies. All four m=2 pin patterns covered. The m=3 mixed rank assignment [0,1,2,0,2,1,2,0,1] exercises nontrivial Y-chain values and two-digit rank fields. The nonfirst-root fixture selects certificate 0101010101011, with the first root row globally infeasible; the physical mark pass recovers the second root row, not an assumed first. Both empty-table and all-nonempty inconsistent rejection controls tested.

Exact principal phase totals: producer 798877747, handoff 45898256, eliminate 31574685, mark+project 2730581, rank relocation 1176389, Boolean reconstruction 3238538. Recovery total after logical selection: 7145508 transitions. The forced witness is 0101010101010101011111111111000, original integer 268348074; the mixed-rank m=3 witness is 10001000110000101000110001011110111011101111110100 (50 bits).

Independent sparse Map tape interpreter, separately written descriptor parser and integer verifier matching the original Python witness-interface semantics: forced SAT 44654867 transitions with valid integer 268348074, nonempty-inconsistent UNSAT 54399245 transitions with blank refusal. Both confirmed nonhalt one step before completion. Combined headline 982550308 physical transitions = seven principal + two independent completions, excluding smoke runs, cutoff repetitions and controls. Eleven cutoff tests around ready, projection, relocation, final joining and halt passed, exact budget 44654867. Five outside/malformed controls (including original n=1 and n=2 shape) halt blank without entering worker.

Development decisions: preserve B4/B5 producer and isolation; directly project selected rank fields at ready rather than replay all mask rows from the row-index certificate; reuse existing binary workspace and two-block output shuttles; make out-of-family refusals blank instead of the former single status bit. Added an explicit rank-stream end check after smoke verification. The ordinary worker descriptor was compared byte-for-byte against parent and is unchanged. V8 executed all reported tests with exact retrieved code; original Python tape_run/valid replay and native Node workflow are committed as gates, not confirmed executed. No full m>=4 B6 execution, independent formal review, or mechanized correctness proof yet.

## Governance

ADVANCE complete original raw-to-Boolean-witness physical path for this fixed family. PRESERVE all original formal claim gates. FORMALIZE exact description and clock accounting; DECOMPOSE finite original-selector admission and wider width-two decomposition coverage; RETIRE interpreting subcubic restricted-family computation as an unrestricted SAT breakthrough. STOP after this bounded mission. All four global routes and all six overarching Omega obligations remain open.

Next F038-REX-023A: verify the native original universal interpreter contract at exact clocks, audit prescribed stage schedules and constants versus descriptor length, separate actual finite admission from eventual single-program admission, and test wider domains and adversarial fixed-path instances. Only then consider generalizing the fixed path to arbitrary admitted width-two decompositions. No promotion.

Reproduce:
```sh
for suite in small three backtrack controls; do
  node mathos/research/f038_rex_ternary_witness_audit.js "$suite"
done
for mode in sat unsat; do
  node mathos/research/f038_rex_ternary_witness_replay.js "$mode"
done
node mathos/research/f038_rex_ternary_witness.js --descriptor > /tmp/witness.desc
python -m mathos.research.f038_rex_ternary_witness_codec /tmp/witness.desc
```

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
