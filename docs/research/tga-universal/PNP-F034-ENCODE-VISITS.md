# PNP-F034 — Boundary encoder selected resource events

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base b62e243032e2a33716e96195fba08433fa6f4e28 (PR #212). Independent of the
scanner-resource-compose candidate (6d0051fe1d22095ca3ab917aeb2f97aa5ff0c334).
Instrument the existing checked high-bit encoder, preserving result
projection on successful and rejecting inputs. Count one abstract Nat
comparison (including base zero test), one subtraction on a high
branch, w cap multiplications at recursive level w+1 (one shared cap
value per level), and one append traversal visit per existing output
bit on success. The ledger is a selected source-level specification:
the original high branch may recompute cap w unless shared. It does
not claim that an implementation evaluates cap only once or that
Nat operations have constant bit cost. For the instrumented abstract
ledger the recurrence B(0)=1, B(w+1)=B(w)+2*w+2 bounds all inputs.
Concrete selected bounds B(4)=21 and B(17)=307. Preserve checked
encoding width and value via the existing soundness theorem.
This does not bound actual Nat operand comparisons, subtraction,
multiplication, storage, append allocation or total machine costs.
Further refinement to bounded binary representations remains required.

Five candidate declarations; 567 executable controls (538 small,
20 boundary, 9 exact), including arbitrarily large tested Nat inputs
rejected by small fixed widths.
Marker F034_ENCODE_VISITS_OK small=538 boundary=20 exact=9.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gate unchanged.
No local Lean execution; exact preflight required before PR.
Independent review and resolution remain open.
