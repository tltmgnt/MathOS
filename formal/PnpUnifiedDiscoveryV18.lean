import Init

namespace PnpUnifiedDiscovery

theorem conflictBlocker (guard path : Prop)
    (h : guard → path → False) : guard → ¬ path :=
  fun hg hp => h hg hp

theorem splitBlocker (guard path : Prop) (pivot : Bool)
    (hfalse : guard → ¬ (path ∧ pivot = false))
    (htrue : guard → ¬ (path ∧ pivot = true)) :
    guard → ¬ path := by
  intro hg hp
  cases pivot
  · exact hfalse hg ⟨hp, rfl⟩
  · exact htrue hg ⟨hp, rfl⟩

theorem rootBlocker (guard : Prop) (h : guard → ¬ True) : ¬ guard :=
  fun hg => h hg True.intro

#print axioms PnpUnifiedDiscovery.conflictBlocker
#print axioms PnpUnifiedDiscovery.splitBlocker
#print axioms PnpUnifiedDiscovery.rootBlocker

end PnpUnifiedDiscovery
