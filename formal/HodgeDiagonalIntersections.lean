import Init

/-!
# Hodge research attempt 006 — formal intersection-matrix consequence

On an elliptic-curve self-product E × E, let
  F1 = E × {p}, F2 = {p} × E, Delta = {(x,x)}.
Classical algebraic geometry yields the intersection numbers:
  F1^2 = F2^2 = Delta^2 = 0
  F1.F2 = F1.Delta = F2.Delta = 1.

The Lean definitions BELOW encode these six numbers as a FORMAL integer
pairing matrix; they do not define complex varieties, Chow groups, Hodge
structures, intersection theory, or prove the geometric input.
What Lean proves is the independent linear-algebra CONSEQUENCE:
the diagonal cannot lie in the Q-span of the two fiber classes.

Consequently there is no claim to solve the Hodge conjecture.
-/

namespace MathOS

/-- Intersection vector with F1, F2 and Delta in the fixed genus-one matrix.
If D=a*F1+b*F2+c*Delta, this is (D.F1, D.F2, D.Delta). -/
def ellipticDivisorIntersections (a b c : Int) : Int × Int × Int :=
  (b + c, a + c, a + b)

/-- The three intersection tests detect zero combination integrally.
The geometric matrix is an input to the model, not derived by Lean. -/
theorem elliptic_intersections_detect_zero (a b c : Int)
    (h : ellipticDivisorIntersections a b c = (0, 0, 0)) :
    a = 0 ∧ b = 0 ∧ c = 0 := by
  have hF1 : b + c = 0 := by
    have heq := congrArg (fun x : Int × Int × Int => x.1) h
    simpa [ellipticDivisorIntersections] using heq
  have hF2 : a + c = 0 := by
    have heq := congrArg (fun x : Int × Int × Int => x.2.1) h
    simpa [ellipticDivisorIntersections] using heq
  have hDelta : a + b = 0 := by
    have heq := congrArg (fun x : Int × Int × Int => x.2.2) h
    simpa [ellipticDivisorIntersections] using heq
  omega

/-- No nonzero integral multiple of the diagonal is an integer linear
combination of the fibers when all three intersection pairings agree.
Clearing denominators proves the same assertion for rational coefficients.
This is NOT a Lean proof that geometric intersection numbers are correct. -/
theorem elliptic_diagonal_not_in_fiber_span (a b d : Int)
    (h : ellipticDivisorIntersections a b 0 =
         ellipticDivisorIntersections 0 0 d) : d = 0 := by
  have hF1 : b = d := by
    have heq := congrArg (fun x : Int × Int × Int => x.1) h
    simpa [ellipticDivisorIntersections] using heq
  have hF2 : a = d := by
    have heq := congrArg (fun x : Int × Int × Int => x.2.1) h
    simpa [ellipticDivisorIntersections] using heq
  have hDelta : a + b = 0 := by
    have heq := congrArg (fun x : Int × Int × Int => x.2.2) h
    simpa [ellipticDivisorIntersections] using heq
  omega

/-- The determinant of the formal genus-one intersection matrix
[0,1,1; 1,0,1; 1,1,0] is exactly 2 (not just nonzero numerically). -/
theorem elliptic_intersection_matrix_determinant :
    ((0:Int) * (0 * 0 - 1 * 1) -
      1 * (1 * 0 - 1 * 1) +
      1 * (1 * 1 - 0 * 1)) = 2 := by
  decide

/-- Genus-zero contrast: the matrix for P1 × P1 has a null vector
F1 + F2 - Delta. This formal degeneracy is compatible with the known
geometric relation, but the geometry is not certified by this file. -/
def genusZeroDivisorIntersections (a b c : Int) : Int × Int × Int :=
  (b + c, a + c, a + b + 2 * c)

theorem genus_zero_null_vector :
    genusZeroDivisorIntersections 1 1 (-1) = (0, 0, 0) := by
  decide

end MathOS

#print axioms MathOS.elliptic_intersections_detect_zero
#print axioms MathOS.elliptic_diagonal_not_in_fiber_span
#print axioms MathOS.elliptic_intersection_matrix_determinant
