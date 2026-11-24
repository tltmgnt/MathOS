# PNP-F034 — DIMACS size bridge for selected certificate charges

PNP_RESOLUTION_STATUS = OPEN. PR #181 merged at
efc1e17ff4c3051f04b960c97d4eab42bdb3230d. Initial run 45511729538
job 138860862614 failed:
artifacts/pnp-f030/f034-parser-consumption-combined.lean:4966:20: error: application type mismatch
artifacts/pnp-f030/f034-parser-consumption-combined.lean:5033:19: error: unknown identifier 'xs.length'
artifacts/pnp-f030/f034-parser-consumption-combined.lean:5033:44: error: unknown identifier 'xs'
artifacts/pnp-f030/f034-parser-consumption-combined.lean:5034:10: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
artifacts/pnp-f030/f034-parser-consumption-combined.lean:5341:22: error: tactic 'rfl' failed, the left-hand side
artifacts/pnp-f030/f034-parser-consumption-combined.lean:5338:58: error: unsolved goals
Process completed with exit code 1.
Correction 1f011c5f2b164d52b0f30f3223138adcf48aef79
used reflexivity after cases, built evidence before substitution,
and explicit append associativity. Final CI 45512276063
job 138862751837 verified all 23 zero-axiom declarations and
67 fixtures, 53 successfully decoded pairs, 19 acceptances.
Artifact 14975732229.
https://github.com/tltmgnt/MathOS/actions/runs/45511729538/job/138860862614
https://github.com/tltmgnt/MathOS/actions/runs/45512276063/job/138862751837

## Candidate bridge

The DIMACS input differs from the custom decimal expected-input
encoding. Use the independent Header, Split, SignedSeq, Row and
Rows grammar relations to prove that every decoded formula's
formulaMass (literal occurrences plus clause rows) is at most
the raw expected-file byte length. Split uses the accumulator
invariant out.length <= bytes.length+word.length+acc.length.
SignedSeq preserves word count; each clause consumes its literal
tokens and exactly one zero, hence Rows token count equals
formulaMass. The canonical expected token length is at most
2*formulaMass+3: one sign token per literal and three header
tokens. This bound does not require successful proof verification.

Let a,b be the expected DIMACS and custom proof files and
A=length(a), D=length(b). The proof parser converse already gives
length(encEnvelope e)<=D. For any pair of successful decodes,
S<=2A+3+D, so the unified selected-charge meter is bounded by
globalUnit(2*(2A+3+D)+1). This is quartic in combined file size.
The candidate accepted_byte_sound adds independently specified
RawMeaning and UNSAT. The second acceptance-only bound
globalUnit(4D+1) follows because the envelope explicitly contains
the bound original formula. That stronger bound omits parsing,
reading and all unmetered charges; it is not a runtime bound in
proof size alone.

13 candidate declarations, strict Lean 4.14.0 zero-axiom gate.
Static runner checks 73 existing DIMACS pairs, 56 successful
DIMACS parses, 22 acceptances, both bounds and verdict agreement.
It reports how many pairs decode successfully; no assumption that
every proof file is well-formed. Required marker:
F034_DIMACS_SIZE_OK cases=73 parsed=56 accepted=22 rejected=51.
New CI pending, no local Lean. Existing strict gates preserved,
no production checker changes, no full DIMACS standard claim.

## Remaining scope

Parser operation counts (including rejecting malformed inputs),
natural-number bit representation, arithmetic, allocation,
recursion, compiler/IO and machine costs are not verified.
Correction to prior bounded-read description: the per-read
request is capped and cumulative returned bytes are at most
limit+1 under the handle contract. Cumulative requested bytes
need not be so bounded if short reads occur. No IO refinement
theorem is asserted. No independent review, original scratch
port, required proof size or proof discovery bound. Main
unchanged. Next: meter decimal scanning and parser token
consumption, then explicit bit-cost refinement.
