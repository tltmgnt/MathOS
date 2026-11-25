# F035 — Decimal word and byte length bounds

PNP_RESOLUTION_STATUS = OPEN.

Based on the verified unbounded decimal encoder e8d40782. For all
natural n < 10^(d+1), the word length is at most d+1. Conversely
n < 10^(word n).length. For any finite token list T, every member is
less than 10^(encode T).length. Encoded length is exactly the sum of
each decimal word length plus one delimiter. If every token is less
than 10^(d+1) and the token count is at most K, the encoded byte count
is at most K*(d+2).

The upper bound is independent of token magnitude as a unit cost.
This is a structural length theorem, not a runtime theorem. To apply
it to solver output, a further theorem must bound all generated
identifier, parent-index, and count tokens in terms of the encoded
expected input. No bound on arbitrary noncanonical input is asserted
by encoded_token_magnitude. The decimal scanner and encoder are
unchanged. 12 public theorem candidates, 1131 controls.
Exact-head replay required before credit.
