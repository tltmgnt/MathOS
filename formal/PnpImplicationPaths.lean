import Init

namespace PnpImplicationPaths

def Lit := Nat × Bool

def neg (l : Lit) : Lit := (l.1, !l.2)

def Holds (v : Nat → Bool) (l : Lit) : Prop := v l.1 = l.2

def Edge (v : Nat → Bool) (a b : Lit) : Prop :=
  Holds v (neg a) ∨ Holds v b

theorem complementExclusive (v : Nat → Bool) (l : Lit)
    (h : Holds v l) (hn : Holds v (neg l)) : False := by
  rcases l with ⟨x,s⟩
  change v x = s at h
  change v x = !s at hn
  have impossible : s = !s := h.symm.trans hn
  cases s <;> cases impossible

theorem complementTotal (v : Nat → Bool) (l : Lit) :
    Holds v l ∨ Holds v (neg l) := by
  rcases l with ⟨x,s⟩
  cases s <;> cases hv : v x <;>
    first | exact Or.inl hv | exact Or.inr hv

theorem edgeSound (v : Nat → Bool) (a b : Lit)
    (edge : Edge v a b) (ha : Holds v a) : Holds v b := by
  cases edge with
  | inl hn => exact False.elim (complementExclusive v a ha hn)
  | inr hb => exact hb

inductive Path (v : Nat → Bool) : Lit → Lit → Prop where
  | refl (a : Lit) : Path v a a
  | step {a b c : Lit} : Edge v a b → Path v b c → Path v a c

theorem pathSound (v : Nat → Bool) {a b : Lit} (p : Path v a b) :
    Holds v a → Holds v b := by
  induction p with
  | refl _ => exact fun h => h
  | step edge _ ih => exact fun h => ih (edgeSound v _ _ edge h)

theorem oppositePaths (v : Nat → Bool) (a : Lit)
    (forward : Path v a (neg a)) (backward : Path v (neg a) a) : False := by
  cases complementTotal v a with
  | inl h => exact complementExclusive v a h (pathSound v forward h)
  | inr hn => exact complementExclusive v a (pathSound v backward hn) hn

#print axioms PnpImplicationPaths.complementExclusive
#print axioms PnpImplicationPaths.complementTotal
#print axioms PnpImplicationPaths.edgeSound
#print axioms PnpImplicationPaths.pathSound
#print axioms PnpImplicationPaths.oppositePaths

end PnpImplicationPaths
