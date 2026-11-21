import Init

/-!
Proof-carrying elementary arithmetic argument with a universal quantifier.
Does not establish any open conjecture or theorem about arbitrary
unformalized natural-language claims.
-/
set_option warningAsError true

namespace MathOS.TECTX.Arguments

/-- Every natural number is unchanged by addition of zero on the right. -/
theorem nat_add_right_zero (n : Nat) : n + 0 = n := by
  exact Nat.add_zero n

end MathOS.TECTX.Arguments
