import F038Formal.ResidualRefinement

/-! FV-10: checked affine row-operation replay. Each row is justified
    directly from a source table or a prior checked addition. Claimed
    cancellation and output order are checked by the existing equation
    proof kernel. This reference checker uses lists rather than bitsets. -/
namespace MathOS.F038.AffineReplay
open MathOS.F038
open MathOS.F038.Cert
open MathOS.F038.Reduction

-- A source proof or a translated XOR/cancellation proof is checked
-- against a claimed equation. All accepted rows are entailed.
def logCheck {n : Nat} (fs : List (RowFactor n)) :
    List (EqProof n × Equation n) → Bool :=
  fun rows => allCheck (fun p => equationCheck fs p.1 p.2) rows

theorem logCheck_sound {n : Nat} (fs : List (RowFactor n))
    (rows : List (EqProof n × Equation n)) (h : logCheck fs rows = true)
    (x : Assignment n) (hx : TableModels fs x) (p : EqProof n × Equation n)
    (hp : p ∈ rows) : EqHolds x p.2 :=
  equationCheck_sound fs x hx p.1 p.2 (allCheck_sound _ _ h p hp)

theorem logContradiction_sound {n : Nat} (fs : List (RowFactor n))
    (rows : List (EqProof n × Equation n)) (h : logCheck fs rows = true)
    (p : EqProof n × Equation n) (hp : p ∈ rows)
    (he : p.2 = ⟨[],true⟩) : ¬ ∃ x, TableModels fs x := by
  rintro ⟨x,hx⟩
  have eq := logCheck_sound fs rows h x hx p hp
  rw [he] at eq
  change false = true at eq
  contradiction

#print axioms logCheck_sound
#print axioms logContradiction_sound
end MathOS.F038.AffineReplay
