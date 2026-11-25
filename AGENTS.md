# Repository agent instructions

## Proctor PNP research pull requests

Do not treat generated Lean text or Python fixture results as a verified Lean proof.

Before opening a new F034 research pull request:
1. Start from the current verified research base, not an unverified sibling.
2. Run `python -m pip install PyYAML==6.0.2` and `python scripts/proctor_preflight.py` from the repository root (Python 3.11, Bash and network access for the existing pinned Lean installer).
3. If local Lean execution is unavailable, push the candidate branch **before creating its PR**, then use the branch's **Proctor F034 pre-PR replay** check. Do not open or mark the PR ready until the check for the exact candidate SHA succeeds. Repeat after any change. Do not bypass checks, change theorem statements merely to obtain a green check, or add `sorry` or unwanted axioms.
4. Preserve the existing strict Lean 4.14.0, warning-as-error, axiom and fixture gates. Record the actual commit and successful run/job IDs in the PR description; label unverified results as candidate only.
5. For older Proctor lanes, use the same local runner with `--workflow proctor-pnp-total-cost.yml` (or the applicable checked-in workflow name).

Frequent failure modes: Lean `rw` does not automatically rewrite both sides or reduce nested matches/lets; use explicit `change`, typed intermediate equalities, distinct names for dependent witnesses, and deliberate unused binder names. Avoid generic `simp` in zero-axiom equality proofs unless the audit establishes the result is axiom-free. Use tail recursion for executable scans of long fixtures. Check actual rejection and boundary controls, not only successful inputs.

The preflight replays existing CI shell steps and is additive, not a replacement for PR CI, independent review, or branch protection. The F034 push check applies to branches that inherit its workflow. No P vs NP resolution claim follows from these scoped results.
