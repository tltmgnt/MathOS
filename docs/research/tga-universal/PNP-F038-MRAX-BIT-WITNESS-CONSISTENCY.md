# F038 / negative route — MRA-X: bit witnesses, advice consistency and nondeterministic circuit avoidance

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Verified parent 47dc1f300792950502f72ca6aa9ade79e02ea3eb: https://github.com/tltmgnt/MathOS/actions/runs/45726741786 (success).

## Backward gap analysis

The preceding oracle transcript obstruction does not constrain ordinary NP membership: a verifier for a single bit need not certify global circuit hardness. Examine what succinct individual bit witnesses and shared advice would actually imply, and distinguish their consistency from totality. Alternative: perform avoidance directly against nondeterministic circuits. Target universal_lower_bound, machine_cost, discovery, short_proofs. This applies standard quantifier and counting techniques; no novelty claim. MRA-X seven stages are locally authored records, not independent live agents.

## Constructive track: exact witness/advice quantifiers

Let V(x,a,b,w) be a deterministic polynomial-time predicate with polynomial-length advice a and witness w, and bit b. Let D(n,a) be an optional polynomial-time advice validity predicate. Assume bounded lengths are explicitly specified and can be padded. Define S_a(x)={b: exists w V(x,a,b,w)} and S(x)=union over D-valid a of S_a(x). The following distinctions are exact.

1. A uniform positive-only verifier (exists w V(x,1,w)) defines an NP language, with no promise of a negative witness.
2. If some advice a_n works for every x of length n, in the sense S_{a_n}(x)={L(x)}, both L and its complement lie in NP/poly. The choice of a_n need not be computable. The same advice can be included in both verifier families. This does not establish uniform NP membership.
3. If valid advice exists and the union S(x) is the singleton {L(x)} for every x, then guessing a,w, checking D and V, gives L in NP intersect coNP. The union condition can be replaced by totality of every valid advice plus agreement among all valid advice. Merely requiring each advice to define some total function is insufficient: two valid advice strings could give different functions. Without negative witnesses, union of positive acceptances still defines an NP language but need not equal the intended lengthwise chosen language.
4. If the selected advice is uniformly polynomial-time constructible, the advice can be computed rather than guessed; both sides are in NP under the two-sided singleton promise for that selected advice. Efficiently checking D alone does not provide construction or cross-advice agreement.

These are conditional statements about a supplied predicate, not a construction of witnesses for the previous hard language. They separate shared lengthwise advice, per-input existential choices, totality and uniqueness. Under P=NP every uniform NP language is in P, hence has polynomial circuits; merely guessing one bit certificate does not evade the original hardness obstacle.

### Certification of the promises

For an explicit Boolean circuit V and explicit input dimensions, cross-advice consistency (no x and two allowed advice/witness pairs accepting opposite labels) is in coNP: a violation has two polynomial-size witness tuples. It is coNP-hard even when the union is total on every input and all advice is allowed. Reduce UNSAT(G) by setting V(x,a,0,w)=true and V(x,a,1,w)=G(w), ignoring x and a. The union always contains zero, and contains one iff G is satisfiable. Thus consistency is exactly UNSAT(G). This does not say checking consistency of a particular fixed verifier is always hard.

Union totality is in Pi_2^P, using forall x exists a,b,w with D and V. It is Pi_2^P-hard even when consistency is guaranteed: given forall x exists w phi(x,w), accept only label 1 iff phi(x,w), with no advice. Totality is exactly the quantified formula's truth; the accepted label set is either empty or {1}. These reductions use explicit circuits, polynomial variable dimensions, and standard SAT and two-block QBF completeness; no oracle is assumed in the actual finite audit. If D depends on advice only, requiring every valid advice to be total has a similar forall a,x exists w formulation, but is not needed for the theorem. Neither promise can in general be assumed to have polynomial existential certificates: such a guarantee for consistency would imply NP=coNP, and for totality would put Pi_2^P in NP.

## Alternative track: nondeterministic circuit range avoidance

Use circuits with n ordinary input bits, h witness input bits, free constants, at most s fan-in-two gates from the 16 binary functions, output one wire. The accepted Boolean function is f(x)=1 iff there exists w such that C(x,w)=1. Independent witnesses are allowed per x. Any such circuit of size <=s can be renamed to use at most h=2s+1 witness bits (only 2s gate predecessor references plus one output reference; unused witness variables can be discarded). This includes arbitrary witness lengths after renaming. With this h the previous counting bound applied to n+h input wires gives B(n+h,s). Choose m as before with 2^m>B(n+h,s), m<=2^n. Evaluating each circuit existentially on the first m x-values gives at most B distinct m-bit words. Thus there is a missing word even for nondeterministic circuits. Zero-extend the least absent word and use zero at exceptional lengths where m>2^n.

Range membership for an explicit m-bit word y and unary budgets is in Sigma_2^P. Existentially guess a circuit C and one witness for every position labeled 1; verify all those positive evaluations. Universally quantify a position labeled 0 and a candidate witness, requiring rejection. This is polynomial in the explicit instance size (m and s charged); if there are no zero positions the universal check is vacuous. Missing-word verification is consequently in Pi_2^P. Prefix completion for a missing word is in Sigma_3^P by adding an existential full-word guess. Greedy prefix completion yields the least missing word with m queries. No hardness/completeness is asserted for these particular circuit range predicates.

For fixed k>=1, s=n^k yields a language in P^{Sigma_3^P} whose nondeterministic circuit complexity exceeds n^k eventually. It excludes one exponent, not all NP verifiers. Choosing s=n^ceil(log2 n) instead gives one language L_nd outside NP/poly. Indeed an NP verifier with polynomial advice and polynomial runtime compiles to polynomial-size deterministic Boolean circuits on input and witness with advice fixed, so any NP/poly language has polynomial-size nondeterministic circuits. The converse follows by using the circuit descriptions as polynomial advice and guessing witnesses; thus this is the appropriate model for NP/poly. The growing-budget hard language is NOT in NP, unconditionally, since NP is contained in NP/poly. This is a different language from the previous deterministic-circuit avoidance language; it does not decide that earlier language's NP membership. The stronger avoidance diagonal cannot achieve the desired NP-membership target by definition.

A direct construction enumerates circuits and their witness assignments and stores the represented words. Bit time is bounded by 2^{O((s+1)log(n+s+2))} poly(n+s+m), since h<=2s+1; the growing budget is superpolynomial in n. The alternative quantified algorithm uses polynomial in explicit budget and prefix lengths plus charged oracle queries; even collapsing the hierarchy under P=NP gives quasipolynomial in n, not polynomial. No actual oracle or general machine compiler is implemented. These are upper bounds, not claims of minimal runtime.

### Topology and transfer scope

The relation S_a(x) projects local witnesses to bit labels; the union over advice can destroy uniqueness, even if every individual fiber is a total function. A single uniform language requires the appropriate projection semantics rather than an arbitrary choice of advice. Nondeterministic circuit range avoidance quantifies over all those independent per-bit witnesses, not a single witness shared by all inputs. No SAT homology claim. The desired separation is still one language in NP outside deterministic P/poly (or outside P); avoiding the larger nondeterministic class makes that target impossible for the newly constructed language. Neither a verifier for the earlier deterministic hard language nor a fixed SAT lower-bound transfer has been obtained.

## Evidence and cost

Independent JS scalar circuit/witness enumeration gave per [n,h,s,m,ordered sequences,output choices,distinct existential prefix words,least absent word or -1]:
[2,0,1,4,257,1284,16,-1],
[3,0,2,8,230801,1615205,152,22],
[3,1,1,8,577,4038,38,1],
[3,1,2,8,452161,3616710,152,22],
[3,2,2,8,803601,7231623,152,22],
[4,1,1,10,785,6279,54,1].
The equality of several deterministic and nondeterministic small ranges is a finite observation, not a general equivalence of models.

Independent JS exhaustively classified all 65536 relations on one bit each of input, advice, witness and label (all advice valid). Union total 65025, union consistent 961, union singleton everywhere 900, every advice singleton everywhere 1296, some singleton-everywhere advice 17136, both such advice disagree 972, good advice but inconsistent union 16308, each advice locally consistent but inconsistent union 1440. The Python regression uses bit-parallel range enumeration with witness bits at the low positions, explicit existential projection, exact least missing words, and independent advice/label masks, and verifies the consistency/totality reduction fixtures and a nondeterministic circuit witness-control example. All enumeration is finite and not an efficient global solver. Independent JS did not execute Python. CI required.

Forward TGA: BARRIER_IDENTIFIED. No universal obligation closes. Next investigate a genuinely different negative-route criterion, such as a resource-preserving reduction from unrestricted computation to a lower-bound model, or a quantitative witness-to-circuit construction with an independently justified structural restriction. Do not treat nondeterministic hardness, advice consistency, or quantifier collapse as a proof of P!=NP. No independent expert review, Lean declaration or mathematical promotion.
