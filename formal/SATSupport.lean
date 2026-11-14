import Init

/-!
# Finite support of a disjoint-factor SAT expansion (SAT1 model)

Each factor (x_i + y_i - x_i*y_i) contributes exactly one of three
exponent pairs: x_i, y_i, or x_i*y_i. A list of choices encodes the
exponents for independent, indexed variable pairs. Different lists
are different exponent vectors; there is no cross-factor cancellation.

This checks a **specific finite polynomial-support combinatorics claim**,
not a SAT algorithm lower bound, P != NP, a complete SAT solver, or any
Millennium Prize Problem. The exact embedding into a generic polynomial
ring is intentionally not formalized by this file.
-/

namespace MathOS

inductive SATFactorChoice where
  | x
  | y
  | xy
  deriving DecidableEq, Repr

/-- Expansion terms, with factor indices represented by list positions. -/
def satTerms : Nat → List (List SATFactorChoice)
  | 0 => [[]]
  | n + 1 =>
      ((satTerms n).map (SATFactorChoice.x :: ·)) ++
      ((satTerms n).map (SATFactorChoice.y :: ·)) ++
      ((satTerms n).map (SATFactorChoice.xy :: ·))

/-- Each multiplication by a disjoint three-term factor triples the
number of syntactic terms, uniformly for every natural number m. -/
theorem satTerms_length (m : Nat) : (satTerms m).length = 3 ^ m := by
  induction m with
  | zero => simp [satTerms]
  | succ m ih =>
    calc
      (satTerms (m + 1)).length =
          (satTerms m).length + (satTerms m).length +
            (satTerms m).length := by simp [satTerms]
      _ = 3 ^ m + 3 ^ m + 3 ^ m := by rw [ih]
      _ = 3 ^ (m + 1) := by
        rw [pow_succ]
        omega

/-- Prefixing a fixed factor choice preserves distinct exponent words. -/
private theorem sat_map_nodup (tag : SATFactorChoice)
    (xs : List (List SATFactorChoice)) (h : xs.Nodup) :
    (xs.map (tag :: ·)).Nodup := by
  apply List.Nodup.map h
  intro a b hab
  cases List.cons.inj hab with
  | intro _ htail => exact htail

/-- Words with different first-factor exponents can never collide. -/
private theorem sat_disjoint (a b : SATFactorChoice) (hab : a ≠ b)
    (xs ys : List (List SATFactorChoice)) :
    List.Disjoint (xs.map (a :: ·)) (ys.map (b :: ·)) := by
  intro z hz1 hz2
  rcases List.mem_map.mp hz1 with ⟨u, _, hu⟩
  rcases List.mem_map.mp hz2 with ⟨v, _, hv⟩
  have hEq : a :: u = b :: v := hu.symm.trans hv
  exact hab (List.cons.inj hEq).1

/-- All expanded terms have distinct exponent vectors: no cancellation
is possible across the indexed, disjoint variable pairs. -/
theorem satTerms_nodup (m : Nat) : (satTerms m).Nodup := by
  induction m with
  | zero => simp [satTerms]
  | succ m ih =>
    unfold satTerms
    apply List.Nodup.append
    · apply List.Nodup.append
      · exact sat_map_nodup _ _ ih
      · exact sat_map_nodup _ _ ih
      · exact sat_disjoint _ _ (by decide) _ _
    · exact sat_map_nodup _ _ ih
    · intro z hz1 hz2
      have hd : List.Disjoint
          ((satTerms m).map (SATFactorChoice.x :: ·))
          ((satTerms m).map (SATFactorChoice.xy :: ·)) :=
        sat_disjoint _ _ (by decide) _ _
      have he : List.Disjoint
          ((satTerms m).map (SATFactorChoice.y :: ·))
          ((satTerms m).map (SATFactorChoice.xy :: ·)) :=
        sat_disjoint _ _ (by decide) _ _
      have hz := List.mem_append.mp hz1
      cases hz with
      | inl h => exact hd z h hz2
      | inr h => exact he z h hz2

/-- Coefficients of every choice word are +1 or -1; in particular,
they never vanish over the integers. -/
def satCoefficient : List SATFactorChoice → Int
  | [] => 1
  | .x :: tail => satCoefficient tail
  | .y :: tail => satCoefficient tail
  | .xy :: tail => -satCoefficient tail

theorem satCoefficient_sign (w : List SATFactorChoice) :
    satCoefficient w = 1 ∨ satCoefficient w = -1 := by
  induction w with
  | nil => simp [satCoefficient]
  | cons choice tail ih =>
    cases choice with
    | x => simpa [satCoefficient] using ih
    | y => simpa [satCoefficient] using ih
    | xy =>
      rcases ih with h | h
      · right
        simp [satCoefficient, h]
      · left
        simp [satCoefficient, h]

theorem satCoefficient_ne_zero (w : List SATFactorChoice) :
    satCoefficient w ≠ 0 := by
  rcases satCoefficient_sign w with h | h
  · simp [h]
  · simp [h]

/-- Combined support and nonzero-coefficient statement, for all m.
The list represents distinct exponent vectors, not a generic ring
polynomial's coefficient dictionary. -/
theorem satSupport_certificate (m : Nat) :
    (satTerms m).length = 3 ^ m ∧
    (satTerms m).Nodup ∧
    (∀ w ∈ satTerms m, satCoefficient w ≠ 0) := by
  exact ⟨satTerms_length m, satTerms_nodup m,
    by intro w _; exact satCoefficient_ne_zero w⟩

end MathOS
