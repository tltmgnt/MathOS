import Init

/-!
Kernel-checkable finite F₂ chain examples underlying graph-based TGA diagnostics.

Edges are Boolean (the field F₂). A graph 1-chain is a tuple of edges,
and the incidence boundary is the xor of incident edge coefficients.

These are exact facts about C₄, a 3-edge path, and a filled triangle,
not claims about the zero locus of ζ, an arbitrary graph, or any Clay theorem.
-/
set_option warningAsError true

namespace MathOS.TECTX

/-- Incidence boundary of the four oriented edges of the undirected cycle C₄. -/
def squareBoundary (e01 e12 e23 e30 : Bool) : Bool × Bool × Bool × Bool :=
  (Bool.xor e01 e30, Bool.xor e01 e12,
   Bool.xor e12 e23, Bool.xor e23 e30)

/-- The only C₄ mod-2 1-cycles are the empty chain and the full cycle.
    This proves the cycle space is exactly {0, (1,1,1,1)}. -/
theorem square_cycle_iff (a b c d : Bool) :
    squareBoundary a b c d = (false, false, false, false) ↔
      ((a = false ∧ b = false ∧ c = false ∧ d = false) ∨
       (a = true ∧ b = true ∧ c = true ∧ d = true)) := by
  cases a <;> cases b <;> cases c <;> cases d <;> decide

/-- Incidence boundary of a path with three edges and four vertices. -/
def pathBoundary (e01 e12 e23 : Bool) : Bool × Bool × Bool × Bool :=
  (e01, Bool.xor e01 e12, Bool.xor e12 e23, e23)

/-- A finite path contains no nonzero mod-2 1-cycle. -/
theorem path_cycle_iff (a b c : Bool) :
    pathBoundary a b c = (false, false, false, false) ↔
      (a = false ∧ b = false ∧ c = false) := by
  cases a <;> cases b <;> cases c <;> decide

/-- The 1-boundary of a triangle's three edges. -/
def triangleBoundary (e01 e12 e20 : Bool) : Bool × Bool × Bool :=
  (Bool.xor e01 e20, Bool.xor e01 e12, Bool.xor e12 e20)

/-- The 2-boundary of the single filled triangular face, over F₂. -/
def triangleFaceBoundary (f : Bool) : Bool × Bool × Bool := (f, f, f)

/-- Exact chain-complex identity ∂₁ ∘ ∂₂ = 0 in this finite triangle. -/
theorem triangle_boundary_squared_zero (f : Bool) :
    triangleBoundary f f f = (false, false, false) := by
  cases f <;> decide

/-- Every triangle 1-cycle is a boundary of its filled 2-face.
    Together with ∂²=0, this makes H₁ of the filled triangle trivial. -/
theorem triangle_kernel_is_face_image (a b c : Bool) :
    triangleBoundary a b c = (false, false, false) ↔
      ((a, b, c) = triangleFaceBoundary false ∨
       (a, b, c) = triangleFaceBoundary true) := by
  cases a <;> cases b <;> cases c <;> decide

end MathOS.TECTX
