# F038 / negative route — MRA-X: direct DAG restriction charging and shared address counterexample

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Verified parent 500b68dd2723f376d3e55b591a5102d9bc3787cd: https://github.com/tltmgnt/MathOS/actions/runs/45730185298 (success). All seven parent workflows succeeded.

## Backward gap analysis

The preceding selector restriction result gives a superlinear formula lower bound but requires charging DAG unfolding. Work directly with the physical circuit, without duplicating paths. Derive an exact restriction-interface bound and a summed gate incidence tradeoff for the same universal SAT selector function. Challenge any unqualified extension to gate count using an indirect-storage-access circuit. This uses elementary subfunction counting and standard multiplexer circuits, not a novelty claim. Seven MRA-X roles are authored local records, not independently running agents.

## Constructive theorem: restriction signatures in an arbitrary binary DAG

Let C be a single-output acyclic circuit with N Boolean input wires and S binary gates, each computing any of the 16 binary Boolean functions. Constants are permitted; repeated input wires count as separate incidences. Remove gates outside the output ancestor cone. Partition some input coordinates into disjoint nonempty blocks B_1,...,B_t, leaving remaining inputs unassigned to blocks. For each wire v let A(v) be the set of block indices represented among its input ancestors (including itself for an input); constants have empty support. These are syntactic reachability sets, not claims of semantic dependence. For a gate g with predecessors u,v, A(g)=A(u) union A(v).

For block i represented at the output, define D_i={w:i in A(w)} and boundary E_i as the distinct wires outside D_i that feed a gate in D_i. Let b_i=|E_i|. Setting all inputs outside B_i fixes every wire in E_i to a bit, independently of the values inside B_i. Given those b_i bits, the entire dependent sub-DAG is fixed as a function of B_i: evaluate it in topological order using B_i input wires and the supplied boundary bits. Induction proves equality to original evaluation for every value in B_i. Thus two outside restrictions with the same signature on E_i yield identical residual functions. If R_i is the number of distinct residual functions,

    log2 R_i <= log2(number of attainable boundary signatures) <= b_i.

For a block absent from the output cone there are at most two constant residuals; do not apply the boundary inequality to that case. If the output is directly a block input, the inequality applies with empty boundary and exactly one residual. The argument uses no formula unfolding or assumption of disjoint dependency cones.

Count distinct boundary wires by incoming incidences (which may count a wire more than once). For each gate, a contribution to block i occurs precisely when one predecessor has i in its support and the other does not. Therefore

    sum_i b_i <= sum_g |A(u_g) symmetric_difference A(v_g)| = J(C).

This holds over blocks present at the output; removing output-irrelevant gates ensures all represented blocks qualify. Consequently sum_i log2 R_i <= J(C). A stronger instance-specific bound can use exact numbers of attainable signatures rather than all 2^b_i possibilities. Computing these numbers is not assumed efficient. Supports and J are computable in polynomial time in explicit graph and block data by bitset unions and symmetric differences; computing b_i and boundary lists is also polynomial. This is a direct reuse-sensitive incidence measure on physical gates, not path copies.

### Transfer to the universal clause-selector function

Use exactly the disjoint guarded-pin blocks from the previous F038 restriction-formulas cycle. Let r=floor(n/3), h=floor(log2(r+1)), m=2^h and t=floor(r/h) binom(r,2). The earlier construction gives at least 2^m distinct residuals for each block by selecting an outside mux-tree CNF encoding an arbitrary m-bit truth table, with guard units set false. Each block is present at the output, since singleton truth-table choices make a nonconstant residual. Thus

    b_i >= m,   J(C) >= t*m = Omega(n^4/log n)
                       = Omega(N^(4/3)/log N).

Here N is the actual universal width-three pool size Theta(n^3). For any circuit in which every gate has symmetric support difference at most d>0, S>=t*m/d. In particular constant d gives a superlinear size lower bound in that structural subclass; generally S*d>=t*m. Equivalently the average support difference of a circuit of S gates is at least t*m/S. No assumption of monotonicity, bounded depth, formula tree structure, or bounded path multiplicity. However d may grow with t, and a gate can contribute to many block interfaces. The measure J is not a lower bound on physical size without a bound on this charge. The result does not establish such a universal bound for SAT.

## Alternative track: indirect storage access refutes a universal linear charging premise

For l>=1 set k=2^l. Inputs are a primary address a of l bits, k pointer blocks P_0,...,P_(k-1) each of l bits, and a table T of k bits. Define f(a,P,T)=T[P_a]. This is a fixed total Boolean function on M=l+k*l+k inputs. For each pointer block P_i, setting a=i and T arbitrarily realizes all 2^k Boolean functions on that block (other pointer blocks can be fixed to zero); there can be no more. Thus sum_i log2 R_i=k^2. But construct each of the l selected pointer bits by a binary mux tree with k leaves, then select the output table bit by a final such tree. A mux (x ? b : a) is ((not x) AND a) OR (x AND b), using three gates in the all-binary basis (the first gate implements not x AND a directly). The resulting explicit circuit has exactly 3(l+1)(k-1) gates. Hence the ratio of the summed log residual count to circuit size grows without bound, on a family with ordinary circuit size O(M).

This is a counterexample not just to linear charging by J, but to any universal inequality of the form sum_i log2 R_i <= K*S for an absolute constant K. It also shows why replacing a potential boundary count by exact residual counts cannot alone repair that particular transfer. It is not a counterexample to the derived bound J(C)>=sum_i log2 R_i. Shared address-dependent circuitry can legitimately support many residual tables, without enumerating them. For the SAT function the missing premise would be an independently proved structural reason that such sharing cannot achieve the desired computation, or another measure with justified general gate charging. We do not assume it.

Topology: each block has a syntactic dependency region and a cut of entering wires. Distinct regions can overlap, and the gate incidence symmetric difference counts their shared boundaries without unfolding. This is a finite graph and subfunction argument, not a homology invariant or an unrestricted lower-bound proof.

## Evidence and costs

Independent scalar JavaScript checked two fixed three-gate DAG skeletons over every assignment of all 16 binary gate types, one with sharing and three singleton blocks and one with two disjoint two-input blocks. Each row [inputs,circuits,circuit/block pairs,outside restrictions,inside/outside evaluations,sum distinct residuals,sum distinct signatures,max distinct residuals,sum boundary wires,sum gate incidence charges]:
[3,4096,12288,49152,98304,21280,40448,4,5,6]
[4,4096,8192,32768,131072,13344,15360,2,2,2].
Each signature determines its residual and the bound holds. Python additionally reconstructs each restricted sub-DAG computation from the actual cut values and verifies output equality. The JavaScript independently built the indirect storage circuits, enumerated every selected pointer block, data truth table and address within that block for l=1,2,3, and measured the actual support charges. Rows [l,k,M,S,sum log residual counts,sum boundary wires,J,output checks]:
[1,2,5,6,4,8,8,16], [2,4,14,27,16,40,48,256], [3,8,35,84,64,160,208,16384].
The Python prototype additionally checks all distinct tables per block and validates malformed references and duplicate block assignments. JavaScript did not execute Python. All enumeration is finite regression; computing the exact subfunction distribution can be exponential and is not claimed as a general compiler. Computing structural support charges is polynomial in the explicit circuit size and block description, and the asymptotic SAT bound is mathematical, not extrapolation. Exact-head CI required.

Forward TGA: BARRIER_IDENTIFIED. Direct circuit restriction charging works without unfolding, with an exact interface inequality and a superlinear lower bound on aggregate incidence, but the indirect-storage family refutes unqualified transfer to physical gate size. Next examine semantic rather than merely syntactic restriction measures (e.g. exact affine restrictions, gate elimination on disjoint independent coordinates, or measures controlling shared multiplexer computation). Require a noncircular general gate-charge theorem or stop that proposed route. No universal obligation closes. Independent review and Lean formalization outstanding.
