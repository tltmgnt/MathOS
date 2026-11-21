import TECTXFiniteTopology

/-!
Independent theorem-type contract: the expected boundary operators are
written out here, rather than accepting the proof module's lemma labels
or its self-reported status. The Lean kernel checks each assignment.
-/
set_option warningAsError true

namespace MathOS.TECTX

/-- Independent C₄ specification: xor incidence at each of four vertices. -/
example (a b c d : Bool) :
    (Bool.xor a d, Bool.xor a b, Bool.xor b c, Bool.xor c d) =
      (false, false, false, false) ↔
        ((a = false ∧ b = false ∧ c = false ∧ d = false) ∨
         (a = true ∧ b = true ∧ c = true ∧ d = true)) :=
  square_cycle_iff a b c d

/-- Independent four-vertex path specification. -/
example (a b c : Bool) :
    (a, Bool.xor a b, Bool.xor b c, c) =
      (false, false, false, false) ↔
        (a = false ∧ b = false ∧ c = false) :=
  path_cycle_iff a b c

/-- Independently spelled-out ∂₁(∂₂(face)) = 0. -/
example (f : Bool) :
    (Bool.xor f f, Bool.xor f f, Bool.xor f f) =
      (false, false, false) :=
  triangle_boundary_squared_zero f

/-- Independent specification that every filled-triangle cycle is a face boundary. -/
example (a b c : Bool) :
    (Bool.xor a c, Bool.xor a b, Bool.xor b c) =
      (false, false, false) ↔
        ((a, b, c) = (false, false, false) ∨
         (a, b, c) = (true, true, true)) :=
  triangle_kernel_is_face_image a b c

end MathOS.TECTX

#print axioms MathOS.TECTX.square_cycle_iff
#print axioms MathOS.TECTX.path_cycle_iff
#print axioms MathOS.TECTX.triangle_boundary_squared_zero
#print axioms MathOS.TECTX.triangle_kernel_is_face_image
