# F035 — Wire token count bounds

PNP_RESOLUTION_STATUS = OPEN.

Based on verified tagged witness interface 171332b7. The candidate
proves expected tokens = 2L+m+3 and SAT witness tokens = 2L+2.
For successful solver UNSAT results all proof tails have width at most
two and the terminal is empty. Each step occupies at most eight tokens;
each batch adds one token, and the proof header/terminal add three.
With B=2L+1 and S=(m+B)*B, the tagged UNSAT witness token count is at
most 2L+m+1+(8S+B+3)+3. This is quadratic in m+L.

The proof does not count decimal digits, token magnitude, serialized
bytes, or runtime. The separate decimal encoder is not a dependency.
21 public theorem candidates; 1028 controls. Exact-head replay required.
