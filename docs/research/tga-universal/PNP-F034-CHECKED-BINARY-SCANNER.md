# PNP-F034 — Checked binary representation and scanner accumulator

PNP_RESOLUTION_STATUS = OPEN.

Candidate based on verified merged research base 41a181566e692a35c64fad5a433b57afcf51cf85 (PR #191).
The four binary-primitives files are copied byte-for-byte from exact
head 9fd2fef7a0ec3badae645f5dbe8c464007c6dec5, whose strict preflight passed
[45525367117 / job 138907240232](https://github.com/tltmgnt/MathOS/actions/runs/45525367117/job/138907240232)
with 14 zero-axiom declarations and 4486 controls. PR #192 merged at f2d8f5722a97a0f981debdd8644a747cf64eaa76. Do not open a new PR until #192 is merged and
the exact new head passes mandatory preflight.

Candidate semantics: little-endian fixed-width lists, checked
Nat-to-binary high-bit comparison/subtraction conversion, zero-padding for short inputs,
and explicit rejection of nonzero discarded high bits. Soundness and
completeness are separate theorems, not a modulo-truncation contract.
Use recursive capacity cap(0)=1, cap(w+1)=2*cap(w). A candidate
bridge identifies cap(w)=2^w. The admissible scanner step uses
the prior decimal invariant to show that its retained-carry output
fits into exactly 512 bits after checked narrowing. A general
512-bit input need not fit after multiplication by ten.

Candidate scanBits uses the checked accumulator and a Boolean
zero test for redundant leading zero; byte classification,
digit counters, byte-limit check, Nat token projection and
list reversal remain outside bit-level cost accounting.
Candidate scan/tokenize equivalence covers rejection as well as
acceptance. No production change.

14 named declarations, strict warning and zero-axiom gates.
Candidate controls: 4608 encodes (width 0..8, n 0..511), 4599
narrowing cases (all representations of widths 0..8 against each
target width), five full-width controls and 13 scanner controls.
Marker F034_CHECKED_BINARY_SCANNER_OK encode=4608 narrow=4599 wide=5 scanner=13.
No local Lean execution available; all new statements and controls
await exact-SHA replay. No total cost, conversion cost, independent
review, proof discovery or unrestricted SAT claim.

## Initial preflight failure and correction

Exact candidate b44a678b4483369adcfd9619b61071ff3f3c83fd failed mandatory preflight
45526025614, job 138909452282, artifact 14981779046 (exit 1).
https://github.com/tltmgnt/MathOS/actions/runs/45526025614/job/138909452282
The binary primitives replay passed, but the checked scanner had four
elaboration errors (two redundant tactics, one unreduced conditional,
one unreduced match) and three encoder declarations reported propext.
Three of fourteen scanner declarations printed zero axioms; the
required executable marker was not reached. No explicit sorry was
introduced. The correction removes redundant tactics, reduces the
conditional/match explicitly and replaces quotient/remainder encoding
with recursive high-bit comparison and subtraction. The exact-width,
value-preservation and representability theorem statements, all controls
and all strict gates remain unchanged. An independent Python model of
the corrected algorithm passed 9225 controls (4608/4599/5/13); this is
not Lean execution or a kernel proof. Corrected exact SHA needs replay.

## Second preflight failure and targeted correction

Exact candidate 81335713fe40309751a4ceaa13f17754964c1753 failed mandatory preflight
45526431200, job 138910839982, artifact 14981939456 (exit 1).
https://github.com/tltmgnt/MathOS/actions/runs/45526431200/job/138910839982
Twelve of fourteen named declarations printed zero axioms, including
all encoding/narrowing theorems and checked_digit_refines. The only
reported elaboration error was a deterministic whnf timeout at
combined.lean:8865:11 (200000 heartbeats), in scan_refines; that
and tokenize_refines reported sorryAx as a consequence. No explicit
sorry is present. The execution marker was not reached.
The repair rewrites the scanner equations instead of unfolding,
reduces the successful match explicitly, and transports the induction
hypothesis with congrArg. A declaration-local elaboration heartbeat
budget of 1000000 is used only for scan_refines. No global setting,
theorem statement, implementation, fixtures, Lean version, warning
or axiom gate changes. Corrected exact SHA must pass preflight.
A fresh independent Python reference model executed all 9225 controls
(4608/4599/5/13) successfully in the current review; this is not Lean
execution or a kernel proof.

## Third preflight failure and proof abstraction

Exact candidate 4a49ed07150dd77d64f2855d95ef19c6aa772869 failed mandatory preflight
45526655511, job 138911585230, artifact 14982637600 (exit 1).
https://github.com/tltmgnt/MathOS/actions/runs/45526655511/job/138911585230
Again twelve of fourteen declarations printed zero axioms; only
scan_refines and its dependent tokenize_refines remained blocked.
The sole reported elaboration error was deterministic whnf timeout
at combined.lean:8868:8 (1000000 heartbeats). The required marker
was not reached. No explicit sorry was introduced.
Instead of raising the budget again, the correction factors scanner
control into a recursive scanCore parameterized by reset word and
checked digit transition, proves the simulation from their contracts,
then specializes to zeroWord and checkedDigit. The initialization
proof is also parameterized by its zero-valued reset. The concrete
scanner delegates to the same control cases via this core; the public
contracts and arithmetic are unchanged. The local heartbeat override
is removed; the default applies. No warning, axiom or fixture gate
changes. All new claims await exact-SHA replay.
In this turn a separate Python reference model actually ran 9225
controls (4608 encode, 4599 narrow, 5 wide, 13 scanner), all passed.
This is model evidence, not Lean execution or kernel verification.
