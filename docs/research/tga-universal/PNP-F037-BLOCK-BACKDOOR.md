# F037 — Block-local backdoors and exact separator messages

PNP_RESOLUTION_STATUS = OPEN.

## Improvement over componentwise backdoors

Normalize a width-at-most-three CNF by deduplicating literals and
discarding tautologies. An empty clause immediately proves UNSAT.
Build its primal graph: variables are vertices, and variables in the
same clause are adjacent. Split at articulation vertices into
biconnected blocks (including bridge edges). Each nonunit clause
has clique support and belongs to exactly one block. Unit clauses
are attached directly to their variable.

The bipartite incidence graph of blocks and all variables is a
forest: the ordinary block-cut forest with its nonarticulation
vertices attached as leaves, and isolated variables retained.
This decomposition can be found in polynomial time, including
by the prototype's elementary recursive articulation search.

Root each tree at a variable. A message from a variable to its
parent block gives the Boolean values compatible with its unary
clauses and every child block. It is the intersection of their
allowed-value sets. A block message to its parent variable p is
the set of values a such that the block's own clauses, p=a, and
the unary domains from all its child variables are jointly
satisfiable. If a child domain is empty the message is empty.
Otherwise each singleton child domain becomes a unit clause.

The earlier bounded-backdoor decision procedure determines each
block message by two calls, one per parent bit. Adding units does
not increase the minimum hitting-set size of ternary clauses.
If a required call returns UNKNOWN the prototype returns UNKNOWN;
it does not guess a message.

## Correctness and resource theorem

Induct up the tree. A variable message is exact because the
child subtrees share only that variable. A block message is exact
because each allowed child value has a witness in its own subtree,
and these subtrees share no variables except the corresponding
block interface. Hence a satisfying local block assignment and
its selected child witnesses combine consistently. Conversely
every satisfying assignment on a subtree restricts to such a
local assignment and permissible child values. This establishes
both directions for every message. A nonempty root domain permits
model reconstruction; an empty root domain proves UNSAT. All
connected trees must have a nonempty domain for SAT. The Python
prototype checks the reconstructed model against the original CNF.

Let b be the maximum, over primal blocks, of the minimum number
of variables meeting every ternary clause in that block. If b<=k,
every required message is decided exactly by the earlier solver.
There are at most polynomially many blocks and two local solver
calls per block, so total work is

    (3^k + 2^k) poly(N)

for encoded input length N. With k<=c log_2(N+1) for fixed c,
this gives a polynomial-time promise decision theorem. No
enumeration of the Cartesian product of block backdoors occurs.
The prototype takes an explicit budget; it is not a fully
formalized bit-cost implementation. Local UNSAT proofs are
checked by the imported solver, but the block message procedure
does not yet emit a standalone global UNSAT certificate.

## Strict parameter improvement

Take t pairwise disjoint positive triples and connect their first
variables by binary bridge clauses in a chain. For t>=2 the
formula is connected, and any strong deletion backdoor to 2-CNF
for the whole formula must meet each disjoint triple: its minimum
size is t. Each ternary block has a backdoor of size one, while
every bridge block has size zero. Thus the block-local procedure
decides this family at budget one for all t, even though the
componentwise promise fails for arbitrarily large t.

This separation is in the sufficient structural parameter, not
a lower bound on the runtime of general SAT solvers. The example
is readily satisfiable. Another fixture uses two ternary blocks
that independently force opposite values of their common
articulation variable. Each is satisfiable alone but their joined
message domains are disjoint, proving the whole formula UNSAT.

## Evidence

The preceding logarithmic-backdoor repository replay passed at
f4fdff6b1658343398da1302c5dc480e6a24449a
(run 45686082061, job 139458931811).

Independent JavaScript execution of the block-tree message algorithm
used exhaustive local block evaluation and an independent hitting-set
gate. It agreed with exhaustive global truth evaluation on all 4096
three-variable fixture formulas at budget one: 1280 SAT, 2816 UNSAT.
It also passed seven connected chains of 2 through 128 ternary
blocks (largest 384 variables, 255 total blocks), and the shared
articulation contradiction. This tests the decomposition and message
logic, not the exact Python local solver or model reconstruction.

The Python candidate adds full model reconstruction and reuses
the previously replayed local decision/certificate checker. Its
exact-head replay remains pending.

## Remaining limitation

This is a standard separator dynamic program combined with
backdoor discovery; no novelty claim is made. A single large
biconnected ternary block can still have a large backdoor.
The next structural question is whether efficiently discoverable
bounded interfaces larger than one can similarly extend the
promise, with a uniform cost bound for interface discovery as
well as messages. The current theorem does not establish that
arbitrary 3-CNF has any such decomposition. No new Lean theorem
credit. Main unchanged.
