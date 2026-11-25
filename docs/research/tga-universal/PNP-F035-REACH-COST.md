# F035 — Executable reachability comparison cost

PNP_RESOLUTION_STATUS = OPEN.

This module counts literal equality probes in routeFor, charges both
lookups at each relaxation, and accumulates charges along the actual
sweep/saturation schedule. A final destination lookup is included.
The counter charges both lookups even if an evaluator could skip one.

For E arcs, length(R)+missing(R,E) is nonincreasing and bounded by E+1
for a singleton seed. Each relaxation therefore costs at most 2(E+1)
literal comparisons. With E sweeps of E arcs and a final lookup, the
bound is 2 E^2 (E+1)+(E+1). For a supplied charge c per comparison the
modeled comparison charge is at most c times this bound.

This is a cost component only. It does not establish the cost of
comparison of binary natural numbers, list allocation, path append,
graph construction, proof compilation, serialization, checker
execution, or the full solver. A refinement to explicit bit operations
and a computational model is required. The separate model and resource
branches are not required dependencies. Eleven public theorem candidates
and 4649 cases. Exact strict replay required.
