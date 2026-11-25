# F035 — Polynomial canonical wire size

PNP_RESOLUTION_STATUS = OPEN.

Integrates verified end-to-end bytes 2663f488, wire token bounds
a30e9016, decimal size 30c38d8e and token magnitude 4e0d5cdf.
For N = length of canonical expected input bytes, the candidate bounds
all successful generated output tokens below 10^(2N+4).
The token budget is N+(8N^2+N+3)+3. The resulting byte budget is
(8N^2+2N+6)(2N+5), a cubic polynomial in canonical input bytes.
This uses a deliberately conservative digit budget, not a numerical
identifier charged in unary. It covers both SAT and UNSAT outputs.

14 public theorem candidates; 1028 executable controls. Strict
exact-head replay required. The result is an output size bound for
the specialized width-two producer, not a bound on execution time,
and does not imply unrestricted SAT polynomial discovery.
