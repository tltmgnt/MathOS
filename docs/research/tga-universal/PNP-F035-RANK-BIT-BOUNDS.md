# F035 — Explicit binary rank width and comparison

PNP_RESOLUTION_STATUS = OPEN.

Based on verified wire-token module a30e9016 and model extraction
d119286a. For L literal occurrences, the existing numeric score
is strictly less than 2^(2L). An explicit little-endian Boolean
list of length 2L represents the same score. A tail-first comparator
returns a correct ordering for equally long bit lists. Replacing
the numerical score comparison by this comparator yields the same
assignment at every natural variable identifier, even absent ones.

The structural comparison charge is exactly 2L paired positions,
not a measured machine instruction count. The alternative bitModel
is not yet wired into the main solver. No functional extensionality,
propositional extensionality, or unrestricted SAT claim is intended.
16 public theorem candidates; 1028 controls. Exact-head strict replay
required before verification credit.
