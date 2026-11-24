# PNP-F007 — Formal bitmask codec, counting parity and dual certificate transport

**MathOS | Specialist formal research | Classical scoped result**

## 1. Exact bitmask codec

The existing decoder takes n bits of a natural-number mask in least-significant-first order. Define encode([])=0 and encode(b::bs)=2 encode(bs)+b, with Boolean b interpreted as 0 or 1. The low bit is b and every higher bit is the corresponding bit of encode(bs). Induction gives decode(length(bs),encode(bs))=bs. The converse is encode(decode(n,a))=a mod 2^n, not unconditional equality: truncation discards high bits. If a<2^n the converse is exact. Every encoded list fits its declared width. Equality of natural numbers follows from equality of all their bits. The proof explicitly invokes Lean core bitwise lemmas.

## 2. Counting parity

Define countAt(n,a,k) as the number of true bits among positions k through k+n-1. Its recurrence adds 0 or 1 to the tail count. The parity of b+c is b XOR parity(c). Thus induction proves odd(countAt(n,a,k))=parityAt(n,a,k). Combining F006's dot-product theorem gives the dot product of decoded masks a,b as the oddness of countAt(n,a AND b,0). Counting true entries of the decoded vector gives the same number. If a<2^n then all higher bits vanish and extending the width by any amount does not change the count. For nonnegative in-width integers this is precisely the mathematical set-bit count computed by Python int.bit_count. This is not a proof of CPython's internal implementation or cost.

## 3. Direct mask certificate transport

Given a finite list of natural-number mask rows and selection bits w, recursively XOR the selected original coefficient masks and their right sides. Selection vectors are zero-padded/truncated to the row list, as in F004. The weighted left-side theorem states that the dot product of the decoded combined mask against any Boolean assignment equals the weighted original decoded left-side evaluations. The right-side theorem identifies the combined right side with the weighted original right sides. If the combined mask is zero modulo 2^n and the combined right side is true, the decoded aggregate row has zero coefficients and right side one; the F004 dual soundness theorem refutes every length-n assignment. This directly connects a mask XOR certificate to the mathematical affine specification. The original disjoint-block domain reduction from F006 transports accepted affine contradictions to the original problem.

## 4. Verification boundary and evidence

The replay concatenates prior exact modules and checks the new codec, count and certificate statements with Lean 4.14.0. Prior empty-axiom gates remain unchanged; library-backed results are separately audited against the explicit allowed dependencies propext and Quot.sound. No sorryAx or unknown dependency is accepted. Exhaustive finite Python controls cover widths zero through eight including high-bit truncation, widths zero through six for dot products, and all systems of at most three rows and at most three variables. The reference Python certificate solver is separately replayed. These finite controls are not universal program refinement. The formal proof has no claim to literature novelty.

## 5. Remaining work

Formal program semantics for the optimized highest-bit Python elimination, including its provenance and domain assembly, and a formal polynomial total bit-cost theorem remain open. The new result supplies mathematical representation and certificate semantics but does not equate the execution traces of different solvers. Canonical Millennium obligations remain unchanged. No live AI execution, independent review or educational validation is claimed.

Reproduction: baseline 87318e9dcb72b3c69ded1a14a6a888220ae99c3a, F006 run 45390200763. Run python -m mathos.research.tga_proctor_gf2_codec --output-dir artifacts/gf2-codec. Actual status and dependency audit are recorded in report.json.
