# F038-REX-003 — Physical sorted factor membership

System MRA-X-TGA-2.0 + RE-X. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
Parent b09c79f9d157529ab5c148a777bf90f787f90567 (REX-002). Bounded implementation mission, not automatic expansion of mathematical scope. Main unchanged. The RE-X backward acceptance contract selects physical factor membership as the missing predecessor of existential OR; the roles are applied locally, not a separately deployed agent ensemble.

## 1. Exact scope

Implement a fixed machine that discovers membership from two actual lists of variable-length binary keys, rather than externally supplied membership flags. Input is a contiguous binary string beginning at the physical head, blank elsewhere. Tokens are 00=key bit zero, 01=key bit one, 10=end record, 11=section separator. Exactly one separator is required between a factor list F and query list Q; every record terminates explicitly, including an empty key. Either list may be empty. Both lists are promised nondecreasing in binary lexicographic order (proper prefix precedes its extension); duplicates allowed. Syntactic grammar is validated by the machine, but sortedness is NOT validated. Arbitrary unsorted inputs are outside the membership correctness theorem. The result is one contiguous binary bit per query, in query order, equal to one iff that query occurs in F. Empty query list returns blank. On malformed grammar halt on blank, with no guarantee of preserving input. This is a destructive sorted semijoin membership primitive, NOT a full sorted join preserving tuples/factors or a SAT solver.

## 2. Fixed physical construction

Adapt the REX-002 logical-rule compiler to a fixed 36-symbol alphabet (raw input symbols, markers L/R, filler Z, result delimiters, and tagged factor/query tokens). All-blank symbol is 222222; other symbols have distinct six-bit binary words. The code length and alphabet are independent of input size and key length. The preparation phase consumes raw bits right-to-left into aligned blocks. The logical worker first parses pairs in place: first cell becomes Z, second a typed token. It installs L/R sentinels, records the factor and query starts, and uses independently tagged start and comparison-cursor marks. No host-generated positions, flag values or variable-length keys are embedded in the table. All control states are finite; comparisons use one current factor symbol in finite control.

A comparison starts at the current factor and query starts. Treat end-of-record D as less than either data bit and factor section end S as greater than either data bit or D. While both data bits are equal, advance both comparison cursors by one token, leaving the record-start marks. To locate a cursor, scan left to L then right to its marked token. When comparison terminates, clear both comparison marks with a sweep, retaining record starts. If F key is smaller, advance just F to its next record. Otherwise emit equality (one for equal, zero for greater/exhausted) at the current query delimiter and advance just Q. The result delimiter is not an active record marker. If query list exhausted, clear all marks and L and return ready at the first cell, with R immediately after the contiguous nonblank tagged region. Serializer consumes this region right-to-left, retaining only result delimiter bits and prepending them so query order is preserved. All other tagged cells erased. Final head points to first output bit or blank. No host phase reset or re-copy between phases.

Correctness invariant: before each comparison, all earlier query results are correct, current cursors point at unprocessed records, and every discarded factor key is strictly below the current query key. Sorted queries maintain this invariant when moving to the next query. A smaller factor cannot equal that query or any later query. If factor is equal, it supplies membership even for duplicate queries (do not consume that factor yet). If factor is greater or exhausted, no remaining factor can equal current query. The comparison procedure computes exact lexicographic order by the first differing bit or proper-prefix termination. At least one record advances per comparison, hence finite termination. Empty lists and empty keys follow the same rules. This proves exact output for all well-formed sorted finite inputs, independently of tests. It does not imply arbitrary unsorted input correctness.

## 3. Complexity auditor

Let N denote raw bit length, h query count and w=6 fixed physical block width. Each logical stay uses 2w-1=11 physical transitions; each move uses 3w-2=16. Prefix pruning in the compiler rejects impossible partial code words early, without affecting valid aligned steps. The full raw-preparation cost for N>=1 is

    P(N)=(w+1)N(N+1)+(w+4)N+3.

For comparison between keys of lengths a,b, at most min(a,b)+1 symbol comparisons occur. Each compared symbol and reset/record movement costs O(N) logical transitions because scans never cross the sentinels on valid inputs. Charge these symbol comparisons to the record that advances, whose length plus one is at least min(a,b)+1. Every record is advanced at most once, so the sum of comparison-symbol counts is O(N), even with repeated keys and long common prefixes. Comparison resets and record movements cost O(N) per comparison; number of comparisons at most number of records O(N). Initialization, parsing and cleanup O(N). Logical time O(N^2), visited logical span O(N). Sortedness is needed for semantic correctness, not for the progress bound. Malformed syntactic input rejects during parsing after preparation.

For the N-block successful ready interval, e_i indicates whether block i emits a result, c_i=sum_{j>i}e_j, h=sum e_i. The exact serializer count is

    O(N,e)=2wN+2w+2 + sum_i[2w(i+1)+2c_i+2e_i+4] + h+3.

Initial marker sweep/erase/return costs 2wN+2w+2. Each reverse-block iteration scans and erases the current word, traverses input prefix and output suffix, optionally emits a bit, and returns; final positioning costs h+3. Because h<=N the full serialization is O(N^2). Consequently the same compiled physical machine takes O(N^2) total transitions and O(N) visited span for the sorted-list contract. Tests check both exact phase clocks and the logical-phase multiplier, not merely output.

Relation to the SEP-002 resource ledger: if a prepared sorted factor/query batch has N=O(m^3 polylog m) bits, this primitive costs O(m^6 polylog m) physical, which has the same exponent as the previously charged full-span sweep over a sequential batch. At most O(m^2) such batches would give O(m^8 polylog m) for these primitive calls. This is a conditional arithmetic compatibility check, NOT a complete integration proof. Real batches must be generated, sorted, re-ordered by outgoing key/candidate ID, and combined with other factors; factor records and query IDs must be preserved or copied with charged costs. The standalone machine erases inputs and emits only flags, so its output cannot by itself replace the entire streamed join/elimination lifecycle. No automatic same-machine composition or original normalized witness discovery. The actual physical solver, description length, and exact eventual U clock remain open.

## 4. TECT-X controls

Both input lists must be sorted. With F=[1,0], Q=[0], the machine returns false because the first factor is greater than query; actual membership is true. With F=[0], Q=[1,0], it returns two false bits because it discards factor 0 when processing query 1; the correct unsorted membership vector is [0,1]. These are explicit scope counterexamples, not SAT hardness evidence. Retire the inference that syntactically valid token streams imply sortedness or that a sorted membership machine implies physical sorting. A further integration mission must enforce the promise through a charged sorting/validation routine, not merely assume it for arbitrary original input.

The original universal interpreter is witness-only. A machine may halt and still produce no candidate or an invalid candidate. The descriptor was decoded entry by entry and replayed with a separately implemented JS version of the retrieved original interpreter on every small selector n=1,2. All 260 halt on blank, none yields a candidate. These selector inputs are not the prepared factor/query format. This is a negative acceptance-contract control, not a claim that the machine decides their satisfiability. A Python original-module replay is committed for CI, not claimed run locally.

## 5. MathOS executed evidence

Fixed descriptor: 36 logical symbols, 60 logical nonterminal states, 2160 rules (including rejection), six-cell blocks, 9252 physical nonhalt states, 27756 transition entries, 508864 description bits. This is one fixed descriptor independent of key length and list size.

Final audit in the tool runtime:
- 133 sorted-list executions: all 128 subsets of a seven-key sorted universe queried with each key twice, plus five edge/long-prefix cases. 1802 query flags verified, 902 positive, 32623007 physical transitions and 1174721 logical transitions. Complete logical reference execution agrees with physical output and logical step count. Exact physical preparation/serialization clocks and middle-phase bound checked. Five one-step-short cutoff controls.
- Ten explicit malformed streams: all halt on blank, 2802 physical transitions. Separate exhaustive grammar controls for all binary strings length 0..6: 127 inputs, 10 well-formed, 117 rejected, 60996 transitions. All short well-formed outputs match direct membership (these short inputs have no unsortedness counterexample).
- Three larger scaling controls [factor records,N,physical steps,logical steps,span,phase counts]:
  [4,98,286675,9833,698,[68897,156853,60925]]
  [8,242,1663843,55553,1714,[414065,887693,362085]]
  [16,578,9272387,305273,4082,[2348417,4881613,2042357]].
  Scaling uses fixed-width binary keys within each fixture; the main regression also includes variable-length, duplicates, empty keys/lists and a 32-bit common-prefix control.
- Both unsortedness counterexamples reproduced. 260 decoded original-selector negative controls passed. Counts exclude scaling, cutoff, grammar and selector replays from the 133 sorted-list aggregate. All final JS assertions passed. The initial development run hit a runaway guard; blank guards were added to malformed logical scans and the worker was debugged with a separate logical interpreter before successful physical reruns. No claim that this initial failed attempt was certified.

No independent review, full Python repository replay, physical sorting, retained-factor lifecycle, original input generation, actual SAT witness discovery or Lean formalization. Finite tests support the stated algorithm, not all inputs or asymptotics by themselves. The fixed descriptor is vastly longer than the small tested cubic-stage budgets; no actual U stage enumeration/admission claim.

## 6. TGA / RE-X decision and status routes

The separate tga_f038_rex_003.py refines evidence notes on REX-02/03/04/05 without changing any Claim state. All prior local completion sets remain: interface 3, integrated machine 5, restricted stage 6, restricted evidence 7, uniform evidence 8. Original global alternatives remain blocked: direct SAT (1), universal selector (3), certificate architecture (7), universal lower bound (1). Independent review is common to the separate editorial evidence gate, not necessarily a mathematical prerequisite for all possible proofs. Counts are authored work packages, not progress or difficulty measures. Python route module is committed and workflow-gated, not freshly executed locally this cycle.

ADVANCE fixed physical membership for sorted record lists. PRESERVE previous physical compiler, grouped OR and normalized host solver. DECOMPOSE sortedness generation/validation, tuple-preserving join, reordering, streamed lifecycle, independent-head/fixed bit computation and same-machine stage proof. RETIRE sorted membership implies arbitrary membership and destructive flag output implies full join integration. STOP automatic follow-on; next separately authorized bounded task should target physical record sorting or a retained-factor and query-ID interface. Decision PRESERVE_SORTED_MEMBERSHIP_INTEGRATION_OPEN. Zero new-task budget means no automatic scheduling after the completed mission, not abandonment of research. No independent certification or global leaf closure.

Reproduce:

    node mathos/research/f038_rex_factor_membership.js
    node mathos/research/f038_rex_factor_membership.js --description > /tmp/membership.txt
    python -m mathos.research.f038_rex_membership_replay /tmp/membership.txt
    python -m mathos.research.tga_f038_rex_003

CI exact head unconfirmed. P versus NP OPEN, PROMOTION NONE.
