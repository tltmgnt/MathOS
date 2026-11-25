# F036 — Boolean views for finite-domain constraint systems

PNP_RESOLUTION_STATUS = OPEN.

## New constructive mechanism

Let a finite-domain CSP have n variables, domain size q, and explicitly
specified constraints. Choose M Boolean views: each view is a total
truth table on a scope of at most r original variables. The views need
not be variables of the original problem, and can express parity,
conditional recoloring, or any other fixed-scope Boolean function.

For each pair of views A,B, enumerate assignments on the union of
their scopes and retain assignments satisfying every original
constraint fully contained in that union. For any absent output pair
(a,b), infer the sound implication A=a -> B=1-b and its contrapositive.
Every full satisfying assignment induces Boolean outputs that obey
all of these implications. Thus if some view value and its opposite
are mutually reachable in the implication graph, the original CSP
has no model. The certificate is two paths between complementary
view values; the checker independently enumerates the local union
for each path edge to establish its claimed implication. No complete
global circuit-equivalence or SAT oracle is assumed. Failure to
find such a certificate is UNKNOWN.

For fixed q,r, each local test enumerates at most q^(2r) assignments.
There are O(M^2) pairs; using explicit relation tables and scanning
the input constraints gives polynomial total cost in the input and
view descriptions. Breadth-first search suffices to find the two
paths (each at most 2M-1 edges). With fixed q,r, even enumerating all
Boolean functions of all nonempty scopes of size <=r gives
M <= sum_{i=1}^r binom(n,i) 2^(q^i), polynomial in n. This count has a
very large fixed constant; the implementation uses selected views,
not that entire enumeration. This is a mathematical cost argument
on explicit finite tables, not a formal Python bit-cost refinement.

## Two constructive examples

For Boolean constraints x XOR y = z, x XOR y = w, and z != w, express
each parity equation by four width-three clauses, and disequality by
two binary clauses. Unary views alone cannot infer the contradiction:
neither parity clause has its full scope in a union of two singleton
views, and the remaining disequality is satisfiable. Add the view
P=x XOR y, automatically selected as a parity view of a cooccurring
pair. Local inference gives P=z, P=w, and z!=w. The resulting
implication graph refutes the formula. Replacing disequality by
equality produces a satisfiable control.

The earlier recoloring certificate also fits this mechanism.
Condition on the apex having color 2 (colors 0,1,2), permissible by
global color symmetry in the graph-coloring problem. Use the view
for original vertex v and its shadow s that outputs v's color
if it is 0 or 1, otherwise s's color. The shadow is constrained
not to have color 2; extend the truth table arbitrarily to the
excluded inputs. Each neighboring pair of such views is forced to
be unequal by the original local edges and unary shadow exclusions.
An odd cycle yields contradictory implications. Even cycles
give satisfiable controls. The example supplies the paired views
from the known Mycielski construction; no arbitrary graph-to-view
compiler is claimed. The previous polynomial graph-level discovery
algorithm can separately find the relevant recoloring witnesses.

## General obstruction, including every fixed-scope truth table

Suppose the original CSP has a nonempty family H(S) of locally
satisfying assignments for every scope S of size <=3r, with
restriction closure and extension to every larger tracked scope.
This is the strategy property exhibited by the prefix-OR pigeonhole
3-CNF of PNP-F036-LOCAL-CONSISTENCY-BARRIER.md. Then NO contradiction
of the Boolean-view kind can occur for ANY selection of views with
scope size <=r, including all their possible truth tables.

Proof: assume paths A=0 -> A=1 and A=1 -> A=0 exist. Fix an arbitrary
member h of H(S_A). Its output is some b in {0,1}. Follow the path
from A=b to A=1-b while retaining h. At a current view B maintain
a member of H(S_A union S_B) that agrees with h and outputs the
asserted value at B. This is possible initially. For the next view C,
extend the member to S_A union S_B union S_C, of size at most 3r.
Its restriction to S_B union S_C satisfies all contained constraints,
so the certified implication forces the next asserted output.
Restrict to S_A union S_C and continue. At the end the retained h
would give A both b and 1-b. This is impossible. Thus no such pair
of paths exists. The argument handles any number of views and any
path length without changing the local scope bound.

For each fixed r>=1, take k>=max(3,3r) in the earlier pigeonhole
family: k+1 pigeons and k holes, width-three prefix-OR gate clauses,
and all pairwise hole conflicts. It is UNSAT but has the above
strategy because each tracked variable touches just one pigeon.
All assignments induced by injective placements of the touched
pigeons survive, and extend while at most k pigeons are touched.
Hence even complete enumeration of fixed-scope Boolean truth tables
cannot make this inference mechanism universally complete.

The obstruction survives branching on at most b original variables
before applying the mechanism, for any fixed b: take k>=b+3r
(and k>=3). At each adaptive split choose the value from an
extension of the retained H assignment on the branch scope.
One can reach a branch of length <=b whose assignment is in H(B).
Condition on it, and use the same path argument on scopes that
also retain B. Every needed extension has size <=b+3r.
Consequently no refutation tree of depth <=b using these leaves
can close every branch. This is a restricted proof-language
obstruction, not a lower bound against all algorithms, arbitrary
introduced global constraints, or variable-width views. The
pigeonhole family admits the independent counting certificate.

## Verification and decision

The previous recoloring certificate exact-head repository replay
passed at 4cf870540ec42e7631d163eb178a971f7910ed8d
(run 45683606149, job 139450260774), including 54 accepted
random graph certificates checked against the finite coloring oracle.

Independent JavaScript execution of the new mechanism passed eight
parity UNSAT block instances where unary-only inference failed,
eight satisfiable parity controls, six odd and six even Mycielski
cycle controls, and 128 random five-variable CSPs. Forty returned
random contradiction certificates were checked against exhaustive
truth evaluation, with no false positives. Both directions of the
certificate paths were independently rechecked by local enumeration.
The Python implementation includes three malformed-certificate
rejections and its exact-head repository replay is pending.
Different random generators can yield different acceptance counts.

The broader mechanism captures both conditional recoloring and parity
without a general semantic equivalence oracle. But the strategy
argument rules out universal completeness for this entire fixed-scope
architecture, even with all fixed-scope view predicates. New global
views or inference rules must be discovered with a separate
generality and cost argument. No new Lean theorem credit. Main
unchanged.
