# F035 — Unconditional byte-level 2-CNF completeness

PNP_RESOLUTION_STATUS = OPEN.

Integrates verified tagged witness interface 171332b7 and verified
decimal encoder e8d40782 unchanged. The executable producer consumes
expected-input bytes, decodes them, produces a typed witness, then
encodes it using the proved decimal encoder. The independent checker
uses the original expected bytes and the produced witness bytes.

Candidate results: every emitted witness is accepted; every decodable
valid width-two formula yields accepted witness bytes; canonical
encoding of every valid typed width-two formula therefore yields
accepted bytes, with the correct SAT/UNSAT tag. The checker on canonical
expected input is semantically sound even for arbitrary witness bytes.
Malformed expected inputs produce no witness. Accepted opposite tags
are mutually exclusive. No assumed tokenizer success remains in the
end-to-end completeness theorem.

11 public theorem candidates; 1034 executable controls. Exact-head
strict replay is required. This is a specialized correctness theorem,
not a bit-cost bound or a resolution of P versus NP. The token count
branch is independent.
