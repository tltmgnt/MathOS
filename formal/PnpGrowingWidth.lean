import Init

namespace PnpGrowingWidth

theorem crossingBound (a b c t : Nat)
    (ha : a ≤ t) (hb : b ≤ t) (hc : c ≤ a+b) :
    c ≤ t+t :=
  Nat.le_trans hc (Nat.add_le_add ha hb)

theorem cutLiteralBound {E : Type} (cut support : E → Prop)
    (h : ∀ e, cut e → support e) (e : E) (he : cut e) :
    support e := h e he

theorem contradiction (p : Bool) (h0 : p = false) (h1 : p = true) : False := by
  rw [h0] at h1
  nomatch h1

#print axioms PnpGrowingWidth.crossingBound
#print axioms PnpGrowingWidth.cutLiteralBound
#print axioms PnpGrowingWidth.contradiction

end PnpGrowingWidth
