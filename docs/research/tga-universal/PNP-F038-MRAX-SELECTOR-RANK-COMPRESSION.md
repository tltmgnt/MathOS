# F038 / negative route — MRA-X: exact selector communication ranks and symbolic compression

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivations and finite audit, not Lean.
Verified parent 4f90c7792d2d962ba38d744c55b49fb33877654a: https://github.com/tltmgnt/MathOS/actions/runs/45727878840 (success).

## Backward gap analysis

The prior universal witness layout has a linear minimum frontier, and its units-first ordered selector model needs exponential width. Determine what lower bounds survive symbolic factorization or adaptive interaction across the same selector partition. Work on the actual fixed universal 3CNF selector function, not a separate formula-specific constant function. Target universal_lower_bound, machine_cost, discovery, short_proofs. MRA-X stages are authored local records, not independent agents. Standard communication complexity rank/rectangle arguments are used with an explicit SAT submatrix; no novelty claim.

## Constructive track: exact rank across the unit/nonunit partition

Fix n>=2. Use the prior full normalized nonempty width-at-most-three clause pool. Alice controls all unit selectors, Bob all binary and ternary selectors. The communication matrix M has entries 1 iff the combined selected CNF is satisfiable. Its row and column labels are full presence vectors on their respective blocks.

An inconsistent unit selection (both signs of a variable) gives the all-zero row. Every consistent selection corresponds uniquely to a partial assignment a in {*,0,1}^n. Thus there are at most 3^n nonzero rows, so over every field rank(M)<=3^n.

For each partial assignment b, encode each pinned literal l of b using only nonunit clauses (l OR z), (l OR not z), where z is a different original variable, chosen deterministically for each coordinate (e.g. the next variable cyclically). Their conjunction is exactly l for every z. Take the union of these clauses (duplicates can be removed), yielding one Bob column per b. Its solution set is exactly the subcube of b. No extra source variable is required, and all clauses belong to the original binary pool. The selected submatrix K indexed by a,b is 1 iff the partial assignments are compatible. With symbol order *,0,1, it is the n-fold Kronecker product of

    H = [[1,1,1],[1,1,0],[1,0,1]].

Indeed compatibility is the product of coordinatewise compatibility bits. det(H)=-1, so H is invertible over every field, including characteristic two, and H^tensor n is invertible (its inverse is the tensor product of the inverses). Therefore

    rank_F(M) = 3^n   for every field F.

This includes real rank and rank over GF(2); the field addition/multiplication interpretation is essential. Every exact arithmetic separated representation M(a,b)=sum_{j=1}^t u_j(a)v_j(b) over a field must have t>=3^n. It is an unconditional size lower bound for this particular linear separability representation, not for arbitrary Boolean circuits or nonlinear boundary compression.

## Alternative track: exact Boolean rectangle rank and adaptive communication

A Boolean separated representation uses OR of ANDs: M(a,b)=OR_j (u_j(a) AND v_j(b)). Each term is a 1-rectangle. Every satisfying assignment x defines a rectangle of Alice and Bob selections all satisfied by x, and the union of the 2^n rectangles is exactly M. Conversely restrict both a and b in K to complete assignments. The resulting 2^n by 2^n submatrix is the identity. No 1-rectangle covers two different diagonal entries without covering a zero off diagonal. Thus the minimum number of terms is exactly 2^n. This also gives exact ceil(log2(number of rectangles))=n bits for the standard nondeterministic 1-rectangle certificate model (the witness is a full assignment, checked locally). This does not count communication needed to produce a witness or verify the global circuit construction.

For a deterministic two-party bit protocol with worst-case d bits, public fixed binary protocol tree, and each terminal transcript labeled with a common output, leaves are monochromatic rectangles, at most 2^d. Sum the rank-one indicator matrices for accepting leaves to reconstruct M over any field; hence d>=ceil(log2(3^n)). This bound permits arbitrary adaptive alternation and unlimited local computation, not only a one-way scan. The identity submatrix alone would give the weaker n-bit bound. A one-way protocol in which only Bob outputs has exactly 3^n+1 distinct Alice rows: distinguish any two partial assignments by a complete assignment satisfying one but not the other, and distinguish each from the inconsistent zero row. Thus its optimal fixed-length message is ceil(log2(3^n+1)) bits; with common output, append one answer bit. The two-way common-output optimum is bounded between ceil(n log2 3) and ceil(log2(3^n+1))+1, not claimed exact. Adaptive messages can be simulated by a bounded-width block-access machine: if a deterministic computation has at most k crossings between selector blocks, an explicit B-bit state suffices to communicate its continuation on each crossing, provided local input access, scheduling and halting are locally determined by that state and common program, and the output is sent at termination. Then kB+1>=ceil(n log2 3); the model must count every continuation bit including counters, memory and addresses. This is not a bound for arbitrary random-access machines without such a crossing/state premise. The inequality is a conditional transfer, not a new unrestricted computational lower bound.

## TECT-X adversarial scope: why rank does not imply circuit hardness

The same K submatrix has an O(n)-gate circuit in an explicit two-bit encoding of each ternary symbol: compute conflict at each coordinate (both pinned and disagree) and AND their negations. This evaluates compatibility directly without enumerating 3^n separated arithmetic terms or 2^n Boolean rectangles. Therefore both exponential ranks coexist with small ordinary Boolean circuits on the restriction. The full M is NP-complete as a function family, but the rank argument does not prove that general circuits for it must be large. Nor does the adaptive communication lower bound rule out polynomial-time SAT: it is linear in n, while the selector length is O(n^3). Even an arbitrary deterministic one-way protocol can transmit the entire unit block in 2n bits; the real hardness may lie in Bob's unrestricted local computation. Communication and circuit cost are different quantities.

A useful exact compression is available for unit information: encode each variable as *,0,1, or one global contradiction flag. This reduces 4^n raw unit selections to 3^n+1 semantic rows and gives the one-way protocol above. However no lossless merging of further rows is possible against unrestricted Bob selectors. The state-domain lower bound is therefore semantic at this cut, not only a count of potential indices. A symbolic circuit can still exploit coordinate products and gate sharing. Neither rank nor exact row count closes the unrestricted lower-bound target.

Topology: the partition fixes two constraint regions sharing the n assignment coordinates. A compatible global witness is their common section; rectangles are separable witness regions, and the tensor-product submatrix captures exact independent coordinate gluing. This is a finite communication/factorization statement, not an unrestricted topological invariant of SAT.

## Evidence and cost

Independent JavaScript constructed every partial-assignment pair for n=2..5, tested compatibility by explicit Boolean source assignments including the nonunit forcing gadget, and computed GF(2) rank by row elimination. Rows [n,3^n,pairs,source assignment checks,ones,GF2 rank,distinct rows,identity size]:
[2,9,81,324,49,9,9,4]
[3,27,729,5832,343,27,27,8]
[4,81,6561,104976,2401,81,81,16]
[5,243,59049,1889568,16807,243,243,32].
The number of ones is 7^n, since H has seven ones. The Python regression constructs the actual clause gadgets using the fixed prior pool, compiles each Bob selection into a model bitset, compares the matrix to independent coordinate compatibility, checks exact rank over GF(2) and GF(3), identity submatrix, witness-rectangle coverage and distinct rows. For n<=3 it also enumerates all raw unit selections to check the exact semantic row partition, and checks every signed-binary residual signature. The JS reference did not execute Python. Full matrices are exponential and used only in finite tests; the compact K circuit and all forcing gadgets are polynomial-time constructible. No full communication protocol optimizer or unrestricted circuit lower-bound solver is implemented. Exact-head CI required.

Forward TGA: BARRIER_IDENTIFIED. The exact ranks strengthen the prior order-specific residual obstruction to all separated arithmetic/Boolean representations and deterministic adaptive protocols across this fixed partition. The compact K circuit demonstrates the nontransfer to general circuits. Next examine a fundamentally stronger model or identify a structural theorem linking general circuits to a lower-bound measure without assuming exponential simulation overhead; do not continue treating fixed partition rank as a universal bound. No universal obligation closes, no independent mathematical review or Lean formalization.
