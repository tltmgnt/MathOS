# F038-REX-023D2 — Physical globally consistent rows and original-order latent ranks

Parent 8c1499281ba8801e82a459989e8ee9cdb2c21d29 (REX-023D1). Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

Previous exact-head [D1 Proctor run 45897812792](https://github.com/tltmgnt/MathOS/actions/runs/45897812792) completed successfully. D2 extends the single fixed raw-selector descriptor with reverse-elimination-order selection and physical rank emission. It neither takes host-selected rows nor supplies host-generated ranks. It is still not an original Boolean witness-interface program.

## Interface

781408 nonhalt states, 2344224 transition entries, 57042788 descriptor bits. Worker entry 533704, selection entry 585083 (observer metadata only). Preserve D1's header, masks, selector, pins, and relation grammar. On SAT, the physical decision bit 1 is followed by nine selected owner rank fields in original group-ID order. Each is w=ceil(log2 m) tokens 00b (MSB first) and delimiter 010; rank-word length 27(w+1). Mark exactly one row in every bag with flag 111, retain 101 for other subtree-feasible rows and 100 for infeasible rows. The terminal head remains the blank workspace separator. The successful label FOREST_SELECTED is observational. UNSAT or structural refusal does not enter selection and emits no rank word. D1 malformed cleanup and refusal conventions remain unchanged.

## Top-down physical algorithm

D1 processes every child before its parent, giving exactly the subtree-feasible row sets. After its successful root pass, iterate bags from 8 down to 0 using the four-bit physical index. For a root, scan for the first 101 row and mark it 111. For a nonroot, reread its record and its parent's record; compute their sorted field masks for the shared separator, storing both masks and the parent index in the inherited group suffix. Enumerate separator keys in A,B using the existing binary odometer, and scan the parent for its uniquely marked 111 row matching the entire joint key. After locating that key, scan the child for the first live compatible 101 row and write the middle bit of its flag to 1. Reset A,B and decrement the bag index. All scans skip other bag sections via the aligned 110 terminator; selected flags 111 do not change token alignment. Mode 2 searches selected parent flags, mode 3 selects a compatible live row. Temporary digit and field markers are restored exactly as in D1. A failure to locate a parent key or matching child is an internal invariant violation, not a normal UNSAT decision.

Induction in reverse elimination order: every root has a feasible row by D1. Every nonroot's parent has already been selected from its subtree-feasible rows, so at least one feasible child row agrees on the separator; exhaustive key enumeration identifies that separator and the first compatible row is chosen. Each bag is selected once. Thus every selected parent-child edge agrees. Running intersection implies all occurrences of each variable agree, and exact-once factor ownership implies the selected assignment satisfies all original latent factors. All components are independently handled. This is a constructive correctness argument and experimental check, not a mechanized proof.

## Physical original-order rank projection

After all selections, enumerate original group IDs 0..8. Find the unique elimination record whose first field is that owner by scanning the constant header. Decode its three IDs, determine the owner's sorted field, and locate the corresponding relation section. Scan aligned tokens to its unique 111 flag. Move left over the flag and decode reversed three-bit tokens until the reversed row start 110 is found; advance to the first rank digit. Read fields in sorted order, and use the inherited digit shuttle to accumulate only the owner field into lane C. The unique temporary blank guides each shuttle back to the exact digit cell. At its field delimiter return to the workspace separator, physically emit C's fixed-width rank using the C2 rank emitter, append 010 and clear C. After all nine ranks, clear the 12 scratch bits and restore the group suffix [19,20,20]. All stored input bits, masks, rank digits and separators remain unchanged. Only selected flag bits and the appended rank word differ from the D1 result.

A selected owner rank determines the same value in every bag containing that group, so the original-group order projection is a satisfying latent assignment. Host witnesses obtained from these ranks by E.witness and checked with E.valid are independent validation only, not machine outputs. The original n-bit witness, physical final halt-head interface and original-selector schedule remain unfinished.

## Resources

Top-down processing uses at most eight joint-key searches, each enumerating at most m^2 keys; charged scans and digit shuttles cost O(N(N+log m)) per key for relation length N. Root selection costs O(N); owner lookup uses fixed header walks, row scanning/rewinding O(N), digit shuttles and emission O((N+log m) log m) per owner. All counts include physical movement and binary scans. D2 additional time O(m^2 N(N+log m)+m^2 log m+N log m+log^2 m), with N=O(L log L) and L=Theta(m^3) on normalized inputs. Therefore the composed bound remains O(L^(8/3) log^2 L), space O(L log L), O(log L) active binary workspace plus constant scratch. This is a conservative asymptotic upper bound, not a finite admission clock or original-witness solver bound.

## Executed evidence

Twelve completed principal original-input runs; compare every mask, header field, rank digit and final row flag with independently decoded factors and bottom-up support sets, then compute the deterministic top-down choice independently and compare every selected row and emitted rank field. Exhaustive m^9 latent enumeration checks SAT/UNSAT. On SAT, independently reconstruct an original Boolean witness and check all selected clauses. All six admitted SAT fixtures yielded valid ranks and host-verified original witnesses. All five UNSAT and one structural refusal yielded no rank word.

| Fixture | m | Models | Total transitions | Selection transitions | Result |
|---|---:|---:|---:|---:|---|
| empty |2|512|29628406|96490|selected|
| outside triple |2|448|34515004|138654|selected|
| nonmonotone star |2|8|39883222|362662|selected|
| nonempty inconsistent |2|0|30968165|0|UNSAT|
| joint-pair inconsistent |2|0|34465372|0|UNSAT|
| disconnected UNSAT |2|0|35143066|0|UNSAT|
| unary UNSAT |2|0|29496152|0|UNSAT|
| K4 SAT refusal |2|160|26655850|0|refusal|
| nonfirst chain |2|64|31249953|128552|selected|
| middle-owner joint SAT |2|128|58508080|873565|selected|
| middle-owner joint UNSAT |2|0|58051426|0|UNSAT|
| seeded mixed |3|882|481125438|1131508|selected|

Totals: 578905 original input bits, 99 admitted bag sections, 303 local rows, 279 subtree-feasible rows (including selected rows), 54 selected rows, 351 emitted rank bits, 889690134 physical transitions of which 2731431 in selection/projection. No observed discrepancies. For the forced nonfirst chain, ranks [1,0,0,0,1,0,0,0,1] are recovered, and two bags select the second row. For the middle-owner joint SAT fixture, ranks [1,0,0,0,0,0,0,0,1] and nonadjacent separator key (1,1) require nonfirst rows, including an owner in the middle sorted field. The m=3 mixed fixture emits [1,1,0,0,1,0,0,0,0] in nine two-digit fields. All four m=2 pin patterns are tested. Seven malformed controls and ten cutoffs including worker and selection boundaries pass. Exact outside-triple halt 34515004, worker entry 34283827, selection entry 34376350.

Independent sparse Map interpreter separately decodes and executes outside-triple SAT (34515004 transitions) and joint-pair UNSAT (34465372 transitions), checking entire word including selected flags, rank stream, raw selector, mask and pin storage. Additional 68980376 physical transitions; combined 958670510 completed principal and independent replay transitions (excludes smoke and cutoff repeats). Current physical tests executed in JS V8. Native original-codec gate and workflow committed, not yet verified executed for this head. No full m>=4 D2 run. Initial compiler smoke exposed a duplicate generated state name; corrected by separating the owner record parser namespace before successful compilation.

## Next bounded mission

D3: translate the physically emitted nine rank fields into the original Boolean assignment (one-hot X, OR-chain Y, original pins, guards), with blank refusal for malformed, UNSAT and unsupported structure, and halt at the first of exactly n=19m-7 original bits. Reuse appropriate B6 charged reconstruction primitives, but adapt to D2's contiguous rank suffix and block 36 pins. Verify using original tape_run and valid at exact clocks. Preserve previous fixed-path B6. General width-two witness and original finite-stage admission remain OPEN. All four global P versus NP routes and six overarching Omega obligations remain open.

Reproduce:
```sh
for suite in small select joint larger controls; do
  node mathos/research/f038_rex_width_two_selection_audit.js "$suite"
done
node mathos/research/f038_rex_width_two_selection_replay.js
node mathos/research/f038_rex_width_two_selection.js --descriptor > /tmp/selection.desc
python -m mathos.research.f038_rex_width_two_selection_codec /tmp/selection.desc
```
