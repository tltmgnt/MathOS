# PNP-F034 — Input-sensitive complete token grammar

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base fd58817a54542ed3b68ef3e7d0307187a63e0ac9 (PR #207). Four files copied byte-identically
from verified PR #208 head e7f61e135052a0851c6bbfcb38aa4e0edbb793d9, exact replay 45542540971/job
138964265237/artifact 14990211587, eight zero-axiom declarations and
1142 controls. Require #208 merge and new exact-SHA replay before PR.

Keep existing grammar meter definitions from merged PR #206 unchanged.
Weak contract allows zero-consuming pure returns and rejection:
successful cost+residual potential <= initial potential; rejecting cost
<= initial potential+1. Strong contract reserves two additional units
on success and uses the same rejecting allowance. Strong-left sequential
composition with weak continuations preserves the strong contract.
Conditional selection preserves weak contract. Nat and Boolean token
parsers have strong contracts, and verified list closure handles nested
lists. Apply these compositional lemmas to the complete existing grammar.
Candidate bound for expected and envelope token meters on all inputs:
selected cost <= 64*input.length+3, including malformed inputs and
arbitrarily large declared list counts. No executable changes, no
complete byte decoder or machine-cost claim. The bound measures only
the previously specified selected resource charges, excluding allocation,
bit encoding, reversal, guard comparisons, tokenizer and typed checker.

20 candidate declarations; 131 controls (8 expected, 12 envelope,
3 actual list-limit boundaries, 108 short-tail adversarial cases).
Marker F034_AMORTIZED_GRAMMAR_OK expected=8 envelope=12 boundary=3 short=108.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gate unchanged.
No local Lean execution. Independent review and resolution remain open.
