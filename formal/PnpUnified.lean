import Init

/-! Abstract soundness of chaining equisatisfiable transformations and
independent decision evidence. Does not prove Python implementation soundness. -/
namespace PnpUnified

def Equisat (p q : Prop) : Prop := p ↔ q

theorem chain {p q r : Prop} (h : Equisat p q) (g : Equisat q r) :
    Equisat p r :=
  ⟨fun hp => Iff.mp g (Iff.mp h hp), fun hr => Iff.mpr h (Iff.mpr g hr)⟩

theorem liftSat {p q : Prop} (h : Equisat p q) (hq : q) : p :=
  Iff.mpr h hq

theorem liftUnsat {p q : Prop} (h : Equisat p q) (hq : ¬ q) : ¬ p :=
  fun hp => hq (Iff.mp h hp)

inductive Verdict where
  | sat
  | unsat
  | unknown

def Sound (p : Prop) : Verdict → Prop
  | .sat => p
  | .unsat => ¬ p
  | .unknown => True

theorem liftVerdict {p q : Prop} (h : Equisat p q) (v : Verdict) :
    Sound q v → Sound p v := by
  cases v
  · exact liftSat h
  · exact liftUnsat h
  · intro _
    exact True.intro

theorem noConflict (p : Prop) (hs : Sound p .sat) (hu : Sound p .unsat) : False :=
  hu hs

#print axioms PnpUnified.chain
#print axioms PnpUnified.liftSat
#print axioms PnpUnified.liftUnsat
#print axioms PnpUnified.liftVerdict
#print axioms PnpUnified.noConflict

end PnpUnified
