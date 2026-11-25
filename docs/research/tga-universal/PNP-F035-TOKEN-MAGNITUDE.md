# F035 — Generated witness token magnitude

PNP_RESOLUTION_STATUS = OPEN.

Based on verified wire-token bound module a30e9016. Let m be the
original clause count, L the literal occurrence count, K=2L+1.
For each successful output of produce n f, every witness token is
at most any cap satisfying cap >= n, 3402, L, K, m+(m+K)*K.
The proof uses the original input validation and proof range gates
for variable IDs and the actual successful parent lookups for index
bounds. The batch frontier length is bounded by m plus the number of
inferences, and the narrow proof theorem bounds each step tail.
The SAT witness uses only occurrence IDs. Fixed tags and list-count
tokens are covered explicitly.

17 public theorem candidates; 1028 fixture cases. The bound is on
natural token magnitude, NOT a claim that numerical identifiers are
unary input sizes. The verified decimal-size module is independent.
A subsequent integration must bound cap's digit length in terms of
canonical expected-input bytes and combine it with the verified
token-count bound. No runtime theorem or unrestricted SAT discovery
claim. Strict exact-head replay required.
