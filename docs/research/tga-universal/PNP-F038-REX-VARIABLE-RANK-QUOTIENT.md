# F038-REX-024D6Z — Permutation quotient and uniform binary-rank physical worker

Parent D6Y 0a110b13d05af0759feaa70872e622f2c9c401fd. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent and scope
[D6Y exact-head host Proctor 46088369471](https://github.com/tltmgnt/MathOS/actions/runs/46088369471) completed successfully. D6X fixed-nine Proctor remains 29/29. This stage implements two distinct layers: polynomial host permutation-factor preprocessing for arbitrary common m, and a fixed physical binary-rank worker on a new explicit canonical stream for arbitrary k. The old original raw selector is converted to this stream by D6Y's HOST decoder. The quotient computation and witness expansion are also HOST operations, not physical worker steps. No claim of a physical raw-selector parser, physical quotient algorithm or unrestricted polynomial SAT algorithm. No change to D6X's fixed-nine descriptor.

## Exact permutation quotient
An active binary factor on (u,v) is a full permutation relation if its m rows have each possible first and second coordinate exactly once. Write z_v=p_uv(z_u), with inverse edge. Construct its undirected component graph. Choose smallest original vertex r of each component as representative and set its map pi_r to identity. Traverse a spanning tree, composing edge permutations to give pi_v for every vertex. For each edge whose endpoints already have maps, retain exactly the root ranks a satisfying pi_v(a)=p_uv(pi_u(a)). These are unary restrictions on the representative; inconsistent cycles may retain some ranks rather than force UNSAT. Every original solution determines its representatives, and every choice satisfying these edge restrictions uniquely expands along the tree to an assignment satisfying all permutation factors.

For every old factor, replace its scope by the sorted distinct representative IDs. Enumerate at most m^3 reduced tuples and accept a tuple precisely if substitution of the corresponding maps passes the old factor. This includes repeated representatives in a factor (e.g. a ternary becomes unary), empty relations and unary restrictions. Intersect factors sharing a reduced scope; omit universal factors. Thus the reduced CSP is model-bijective to the old one, with explicit expansion map. Lex order is preserved: among two distinct reduced solutions, the first differing component in representative order has its smallest original vertex as the first differing original coordinate, and its map is identity. Repeating the process after rewriting may discover new binary permutations. Each continuing round strictly decreases the variable count; there are at most k rounds including the final stable round. Compose expansions in reverse round order. Empty relation certifies UNSAT without enumeration. Otherwise invoke D6Y exact separator reference on reduced variables. The proof assumes valid explicit factors with nonempty sorted distinct scopes and common positive domain (m>=2); it is not a validator for arbitrary JS objects.

Each round uses polynomial scans of the explicit factor tables, O(k*m) map storage, O(|F|*m^3) row tests and at most O(|F|*m) edge-rank checks, with polynomial indexing/intersection overhead in a bit-cost model. At most k rounds. The post-quotient enumeration cost still depends exponentially on residual component sizes in general. For fixed separator cap h<=2 and residual size b, D6Y's conditional host candidate bound O(k*m^(h+b)) applies to the reduced graph, in addition to polynomial preprocessing. No unconditional polynomial bound.

## Uniform canonical binary-rank physical worker
Canonical logical tape1 contains 1^k 0, followed by a sequence of forbidden tuple records, then blank. Each record begins x, followed by one to three literal fields of form 1^(g+1) 0 r (g zero-based coordinate, r=0 or1). Stream producer enumerates forbidden rows of valid arity<=3 factors; neither selector bits nor oracle answers are supplied to the worker. Tape0 initially empty. This is an explicit canonical stream, NOT the original raw selector input. Unary indices intentionally trade space for simple uniform finite control.

The two-tape finite IR uses alphabet L,0,_,1,x and 219 instructions including jumps. Read header to create k zero ranks on tape0. For each record, rewind assignment head to the first rank; unary index moves it to the designated coordinate. A finite flag tracks whether every rank in the current forbidden tuple matches. If all match at the record boundary, reject that candidate, move to the right end of the assignment word, increment the binary counter (carry resets 1 to0), rewind stream, and retry. Carry past L signals exhaustion. If every record passes, rewind assignment head and halt successfully. The counter visits all 2^k binary assignments lexicographically; the first accepted one is the least solution. Each record rejects precisely the indicated forbidden tuple, hence exhaustion iff UNSAT for genuine streams. All writes are off the sentinel, left scans stop at L. Only bounded arity/flag states are compiled, never k-indexed control. The same emitted transition table runs every audited binary-coordinate count. Malformed stream paths are not a complete parser/validator and are not certified.

Compile with the existing D6T paired four-bit segmented compiler and local continuation. The worker has two logical tapes encoded on one ternary physical tape. Initial physical encoding is G hL u_ D hL u(stream) u_ E. On successful terminal G remains its binary code; on reject G is overwritten by 2222. Merge the two terminal IDs into one standard halt ID without changing any write/movement, then use existing exact Mealy quotient. Distinguish genuine terminal outcomes by the G block; retain rank word on tape0 for SAT. This is a new fixed uniform canonical-stream descriptor, not an end-to-end original raw-input machine. Host prepares the encoded tape and reconstructs original-format expanded witness. No native C++ execution is claimed.

Let S be canonical logical stream length. Input and assignment extent O(S+k+1), including growth of k assignment cells. Unary field length charges both its forward indexed motion and the following rewind from that index (plus O(1) per literal), so a complete candidate scan and counter update require O(S+k+1) logical primitives, including stream reset. Initialization O(k), full enumeration <=2^k candidates, hence O((2^k+1)(S+k+1)) logical primitives. Inherited physical compiler gives O(S+k+1) transitions per primitive, so physical time O((2^k+1)(S+k+1)^2), span O(S+k+1). For fixed binary domain, at most O(k^3) distinct normalized scopes, each with at most eight forbidden tuples of O(k) length; S=O(k^4), polynomial in raw L=Theta(k^3). The exponential candidate factor is not removed. This is a source-level resource bound under the compiler invariant, not an explicit universal numeric clock certificate or a polynomial physical time claim.

## Verification and measured physical resources
Independent numeric-index exhaustive oracle compares complete model sets before/after quotient and exact least witness after repeated quotient, including 512 CNF families (all subsets of unary/binary clauses on two variables and of signed ternary clauses on three),120 seeded mixed permutation/factor cases at m=2,3,4, two named cycle/derived cases and12 barrier fixtures. 646 model cases,211510 original assignments,77098 first-round quotient assignments,3012 expanded quotient models,646 exact least-witness checks. Two cases exhibit strict multi-round contraction and two remove inconsistent cycle ranks. Named three-rank cycle with transposition (0 1) keeps rank2 and one solution; derived ternary relation becomes a new permutation after first collapse, reducing 3->2->1 with three models.

558 original canonical-stream physical cases (388 SAT,170 UNSAT) execute actual emitted rows, then compare dual-exit, single-exit, minimized execution, exact source accountant clock and entire terminal encoding. 558 exact one-short cutoffs TIMEOUT/no witness. One additional execution of minimized physical worker on each host-reduced stream checks expanded least rank witness, classification, exact clock and terminal encoding. 558 reduced physical runs:75 improve,483 tie,0 regress on this corpus, aggregate worker transitions55366513 ->38981158. 350 SAT raw-format projection checks on decoded inputs (projection, not independent revalidation of all raw clauses; D6Y separately audits raw correspondence). Physical counts exclude host decoding, quotient and witness reconstruction. There is no universal runtime dominance claim. 
| resource | value |
|---|---:|
| IR instructions including jumps |219|
| original physical nonhalting states |4934|
| original standard descriptor bits |256572|
| minimized physical nonhalting states |3683|
| minimized descriptor bits |180471|
| original transition-row relation checks |14802|
| independent standard descriptor row decode checks |11049|

The minimized descriptor uses12-bit state identifiers (including terminal); original uses13-bit. Do not compare these directly with D6X's richer 20-tape machine: this is a simpler worker with different input/output interfaces and exponential enumeration. It is not a compression of that physical pipeline. All original states reachable in syntactic transition graph. Descriptor roundtrip independently parses header, all state/write/move rows and length. No wall-clock or peak RAM measurements.

## D6Y equality barrier removed; new residual barrier
Dense equality plus a ternary factor forbidding every diagonal tuple collapses to one variable with empty unary relation. D6Y enumeration 2^k -> zero host enumeration candidates (preprocessing is charged separately). Actual original and reduced-stream physical worker counts:
| k | unquotiented physical transitions | reduced physical transitions | original/reduced stream bits (logical symbols) |
|---|---:|---:|---:|
|4|292837|2092|151/10|
|6|1916171|2092|393/10|
|8|8767105|2092|819/10|

Larger k10,12,16 equality cases tested at host only, all reduced to one variable with empty relation. At k16 old enumeration65536, new zero. No physical original replay at these larger k.

A different all-k>=4 binary family survives the implemented quotient: impose at most one 1 on every pair, and at least two 1s on the first triple. Every binary factor has three allowed rows, not a permutation; every value has support in every factor, so GAC retains all values. The complete primal graph remains connected after deletion of <=2 vertices. Globally the pair constraints and ternary factor contradict. The reduced graph is unchanged and D6Y capped-separator/full-tuple policy tests exactly 2^k assignments. The new physical worker also enumerates all 2^k on genuine instances by its correctness invariant.
| k | residual host candidates | actual unreduced and reduced physical transitions |
|---|---:|---:|
|4|16|327609|
|6|64|3129327|
|8|256|26268031|
|10|1024|not replayed|
|12|4096|not replayed|
|16|65536|not replayed|

This is a counterexample to universal polynomial performance of these specific preprocessing and enumeration policies, not a lower bound for arbitrary solvers. The residual family is trivially refuted by checking each allowed first-triple row against its pair projections. It motivates sound local relational consistency, not a claim of hard SAT instances in an absolute sense.

## Remaining obligations and next D7A
Source reduction to variable-coordinate binary family remains established at D6Y source level. A uniform physical binary canonical-stream worker is now implemented and tested; direct original-selector physical normalization, on-tape structural preprocessing, on-tape full original witness reconstruction and polynomial physical time for arbitrary k remain open. Investigate pair-to-triple semijoins and bounded-width consistency with exact witness preservation and explicit cost; determine what survives those refinements. Separately build a uniform raw-selector producer without externally supplied rank metadata. No promotion; P vs NP remains open. Main and PR #248 not modified. New dedicated D6Z audit workflow configured; completion unconfirmed. Development note: an initial script attempted to serialize BigInt result directly and failed before branch creation; subsequent explicit string serialization and separate complete audits succeeded.
