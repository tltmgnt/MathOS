# F038-REX-004 — Stable physical record sorting with retained payloads

System MRA-X-TGA-2.0 + RE-X. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
Parent 7fa619e302f5164b2f191737156d951dace0f4a4 (REX-003). Main unchanged. One bounded implementation task selected from the previous backward frontier: eliminate the externally supplied sortedness promise for fixed-width record keys while retaining arbitrary binary payloads, including candidate identifiers. This is a standalone physical sorter, not a compiled separator solver or deployment of a separate autonomous MRA-X engine.

## 1. Contract and research authorization

Given a finite list of records (key,payload), keys are nonempty binary strings of a COMMON width k>=1 (not supplied separately and not bounded in finite control); payloads are arbitrary finite binary strings, including empty. Keys need not be sorted. Encode each key digit and payload digit b by 0b, separate key and payload with 10, terminate every record with 11. Empty list is empty raw input. All data are initially a contiguous binary string starting at physical head zero, blank elsewhere. The output uses exactly the same grammar, sorted in nondecreasing binary lexicographic order by key, retaining every payload and preserving the original relative order among records with equal keys. Malformed grammar or unequal key widths must halt on blank; rejection need not preserve the input. The machine validates widths as part of sorting, not by host inspection. No external sortedness, key count, width, record positions or rank advice is required. Fixed-width binary encodings suffice for the intended bounded-domain tuple keys, provided a future producer emits those encodings. This is standard stable LSD radix sorting realized on a fixed one-head tape; no novelty claim for the abstract sorting algorithm.

## 2. Actual physical implementation

Reuse the REX-003 compiler with a new fixed 21-symbol logical alphabet: raw bit symbols, all-blank, sentinels L/R/E, consumed symbols X/Y, record-start and copy markers H/J/C, and data A0/A1,K0/K1,M0/M1,D,P0/P1,T. The raw first bit of each two-bit token becomes A0 or A1, the second becomes a typed key digit K, marked key digit M, divider D, payload digit P, or terminator T. A fixed code maps all-blank to 22222 and other symbols to distinct five-cell binary words. The compiler emits actual physical transitions over {0,1,2}, with 2 blank. A nonempty raw string of N bits is consumed right-to-left into N aligned blocks; the same machine runs the worker and serializes its output without resetting tape/head in the host. The empty list takes the empty-ready path.

Grammar parser: install L/R around the prepared interval; read token pairs, require a nonempty key before the unique divider and a complete terminator for each record. On each divider, move back two logical cells and mark the preceding key digit M. Thus every record initially has one active digit at its rightmost key bit. No key length counter is needed.

For each radix pass:
1. Install E immediately after R. In the source interval, scan records in order for active digit zero. At each record start place H, inspect its active M digit, and either return to H and copy the entire record, or mark its start J and skip it. Copy each logical cell to E, advance E, return to the unique C copy marker, overwrite it X and continue. Record terminator determines when to resume record search. The zero bucket is stable.
2. Rewind to L, skip consumed cells X, copy the remaining J records in source order (all have active digit one). The one bucket is stable, following the zero bucket. The destination is a complete permutation of the input records. Original source now contains N X cells.
3. Starting immediately after R, take each destination cell in order, mark it Y, shuttle to L, scan to first remaining X and restore the cell there. Return to R. At E erase the end marker and all Y cells, leaving only the restored N-cell source interval.
4. Scan restored records, replace each old M by its corresponding K and mark the previous key digit M if it exists. A record whose marker reaches its first key digit becomes finished; a finite-control flag detects whether some records finish while others continue. Reject on that mixture, establishing equal-width validation. Resume past the old marker so new marks are not processed twice. If all continue, repeat; if all finish, remove L, leave R, and enter ready at the source start.

The physical serializer consumes the N product symbols in reverse and prepends their raw bit projections, erases R and all scratch, and halts at the first bit of the contiguous sorted record encoding. Every key and payload bit is preserved in the output; no host-provided permutation or flags. The machine is destructive with respect to the original ordering, but retains the entire multiset of records, and stable order within ties. It does not preserve an additional raw input copy or retain multiple factor tables simultaneously.

## 3. Correctness theorem

At the beginning of each pass, source contains the original records in some order, each with exactly one active key digit at the same offset from the right unless the input has unequal widths. The two bucket loops copy every record exactly once, preserving record contents and order within each bucket. Restore preserves concatenation order, and marker update does not change key or payload values. Therefore each pass is a stable partition by the next digit from the right.

Induct on j: after j passes, records are sorted by their j-bit suffix, with the original relative order for equal suffixes. The base j=0 is trivial. A stable partition by the preceding digit puts zero before one and retains the suffix ordering and original tie order in each bucket. For common width k, after k passes all markers finish together and the order is the full key order. The resulting stable permutation carries each payload with its associated key. If widths differ, at the minimum key width some markers finish and some continue, triggering rejection rather than producing an incorrectly sorted answer. Each pass advances a marker or finishes; all loops scan finite sentinel-bounded regions and transfer a finite number of cells. Invalid token grammar rejects during parsing. This proves the contract for every finite valid input, independently of finite tests.

## 4. Exact transfer clocks and total resource bound

Let N be raw encoded bit length, k common key width, w=5 physical block width. Nonempty raw input has N>=6. A compiled moving logical transition costs 3w-2=13 physical transitions and a staying one costs 2w-1=9. Raw preparation and full projection costs are exactly

    P(N)=6N^2+15N+3,
    O(N)=6N^2+21N+15.

For empty input each interface phase costs 1, the middle phase 9, total 11 transitions.

Per nonempty pass, consider source cell i (0..N-1) copied to destination cell N+1+j (0..N-1 permutation index). Its append/return distance is d=N+1+j-i, and the copy-loop transitions are exactly 2d+3. Because the j form a permutation, sum d=N(N+1). Thus all copy loops per pass cost exactly

    C(N)=2N^2+5N

logical transitions. The j-th restore iteration costs 2N+2j+4 logical transitions (scan past j consumed destination cells, mark, return to L, find source slot, write, return to R). Summing and including the final N-cell destination scan and N-cell erase sweep plus two boundary transitions gives exactly

    B(N)=3N^2+5N+2.

Copy+restore alone therefore uses 5N^2+10N+2 logical transitions per radix pass, irrespective of record permutation. All other per-pass control work is O(N): bucket seek/return/skip traversals are charged to their own records, consumed cells scanned at most a constant number of times per bucket, sentinels rewound a fixed number of times, marker update scans each record once with constant extra work per key marker. Initialization and final rewind O(N). Therefore for this specific implementation, on valid nonempty input,

    T_logical(N,k)=Theta(k N^2),
    T_physical(N,k)=Theta(k N^2),
    S_physical(N)=11N+12.

The span follows from logical L at -1, source 0..N-1, R at N, destination N+1..2N, E at 2N+1, and the physical output to the left of the prepared source. Physical final head is -6N-2; leftmost turn -6N-3 and rightmost cell 5N+8. Empty span 5 and head zero. No asymptotic shortcut from a hidden random access operation. The exact per-pass transfer clocks also give an implementation-specific lower bound; this is not a lower bound on all sorting machines.

For fixed-width tuple keys in the intended F038 batch computation, k=O(log(m+2)) (constant-many digits, fixed-width codes). If N=O(m^3 polylog(m+2)), standalone sort cost O(m^6 polylog(m+2)) and space O(m^3 polylog(m+2)). At O(m^2) such calls, sorting alone remains O(m^8 polylog(m+2)), compatible with the previous conditional subcritical ledger. This does not prove the required call count for a complete integrated machine. In terms of unrestricted N, k can grow linearly in N, so the standalone sorter is not universally quadratic and may take cubic time. The k factor must not be dropped.

## 5. Executed verification

The committed JS source compiles a fixed descriptor: 21 logical symbols, 125 logical states, 2625 rules including rejection, 8959 physical states, 26877 physical transitions in table, 492749 description bits. The descriptor decodes entry-for-entry, independent of record count and width.

Main physical regression:
- 132 valid-list runs, 383 records, 4240 raw bits, 37753264 actual physical transitions and 2738336 logical transitions.
- Exhaust all ordered one-bit key sequences through four records and two-bit key sequences through three records, with distinct payload identifiers. Additional duplicate keys, empty payload/list, seeded variable payloads and 12-bit common-prefix controls.
- 263 radix passes, every intermediate logical pass checked against a separate stable suffix-sort reference. Logical reference final result and step count agree with actual physical execution. Complete final tape output (including cleanup/head/span) and exact preparation, logical compilation and serialization clocks checked.
- 1075790 copy-loop and 1588976 restore-loop logical transitions; exact transfer formulas checked on every main fixture. Five one-step-short physical timeout controls.
- Twelve explicit malformed/unequal-width inputs, all halt on blank, 87701 transitions. Independent grammar parser checked all 511 raw strings of length 0..8: 11 valid, 500 rejected; 338894 physical transitions. These small grammar cases are separate from main counts.

Scaling [record count,key width,N,physical steps,logical steps,span,phase counts]:
    [4,2,48,350523,24705,540,[14547,321129,14847]]
    [8,3,128,3479461,252179,1420,[100227,3278227,101007]]
    [16,4,320,28137559,2069037,3532,[619203,26897221,621135]].
Scaling/cutoff/grammar/original-selector controls excluded from main aggregate. These counts are interpreter transitions, not measured hardware runtime. Final assertions passed. The logical reference observes intermediate pass states; physical tests compare final output and exact logical step counts, not an independently checked full tape equality at every intermediate logical boundary.

The emitted descriptor was also decoded and replayed under a separately written JS version of the original selector interpreter loop for all 260 n=1,2 selector inputs. Each halted on blank, none produced a candidate. These inputs are not record streams in the sort grammar. This is a negative witness-contract test, not SAT decision. The committed Python replay imports the original decoder/interpreter; it and the Python status module are CI-gated but not claimed run locally in this cycle.

## 6. TECT-X and integration boundary

REX-003 required both lists sorted and erased keys when emitting flags. REX-004 removes the sorting promise for COMMON-width keys and preserves payloads/IDs through reordering. For the future separator use, the payload may contain full tuples and query IDs. This is not yet a retained-factor join: the two standalone grammars differ, no same-tape adapter, factor-cache lifecycle, membership result attachment, ID-based reordering or grouped reduction composition is implemented here. The original solver's normalized parser/tuple generation is also still missing at physical level. Unequal-width keys reject; the sorter does not implement the variable-length order admitted by REX-003 without an additional encoding scheme. Do not infer physical sorting implies full join integration or that fixed-width sorting eliminates the key-width factor.

The next separately authorized task can use a shared tagged record format to attach membership flags to payloads in place, preserving factor data and query IDs, and compose sorting and membership in one fixed physical machine. It should require an actual same-tape trace and a charged lifecycle rather than separate host-mediated invocations.

## 7. TGA / RE-X status and disposition

The separate REX-004 status module updates notes on REX-02/03/04/05 but leaves all Claim states unchanged. Local routes: interface (3), integrated machine (5), restricted stage (6), restricted evidence (7), uniform evidence (8), all BLOCKED in authored graph. Global alternatives: direct SAT (1), universal selector (3), certificate architecture (7), universal lower bound (1); all BLOCKED. Zero of four resolution routes closed. Independent review remains shared by separate editorial evidence gate. Counts are modeled work packages, not mathematical difficulty or percentage progress. No independent review, Lean certification, complete solver descriptor, actual U-stage admission or exact-head CI confirmation. No certification metric upgraded.

ADVANCE stable record sorter to review. PRESERVE membership, grouped OR and normalized host solver. DECOMPOSE shared record grammar, retained-factor join, ID reorder, actual normalized solver integration and exact-stage clock. RETIRE unsupported standalone-composition and width-independent quadratic claims. STOP after this bounded task; no automatic further authorization. Decision PRESERVE_STABLE_SORT_INTEGRATION_OPEN.

Reproduce:
    node mathos/research/f038_rex_stable_record_sort.js
    node mathos/research/f038_rex_stable_record_sort.js --description > /tmp/sort.txt
    python -m mathos.research.f038_rex_sort_replay /tmp/sort.txt
    python -m mathos.research.tga_f038_rex_004

P versus NP OPEN, PROMOTION NONE.
