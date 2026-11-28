import Init

namespace PnpSignedHorn

inductive AllHolds {L : Type} (truth : L → Prop) : List L → Prop where
  | nil : AllHolds truth []
  | cons {a : L} {as : List L} : truth a → AllHolds truth as → AllHolds truth (a :: as)

theorem bodySound {L : Type} (truth : L → Prop) (body : List L)
    (known : ∀ a, a ∈ body → truth a) : AllHolds truth body := by
  induction body with
  | nil => exact AllHolds.nil
  | cons a as ih =>
    exact AllHolds.cons (known a (List.Mem.head _))
      (ih (fun b hb => known b (List.Mem.tail _ hb)))

theorem forwardSound {L : Type} (truth : L → Prop) (body : List L) (h : L)
    (known : ∀ a, a ∈ body → truth a)
    (rule : AllHolds truth body → truth h) : truth h :=
  rule (bodySound truth body known)

theorem conflictSound {L : Type} (truth : L → Prop) (body : List L)
    (known : ∀ a, a ∈ body → truth a)
    (rule : AllHolds truth body → False) : False :=
  rule (bodySound truth body known)

inductive Trace {L : Type} (truth : L → Prop) : List L → Prop where
  | start : Trace truth []
  | extend {known body : List L} {h : L} :
      Trace truth known →
      (∀ a, a ∈ body → a ∈ known) →
      (AllHolds truth body → truth h) →
      Trace truth (h :: known)

theorem traceSound {L : Type} (truth : L → Prop) {known : List L}
    (t : Trace truth known) : ∀ a, a ∈ known → truth a := by
  induction t with
  | start =>
    intro a hm
    nomatch hm
  | extend _ includes rule ih =>
    intro a hm
    cases hm with
    | head => exact forwardSound truth _ _ (fun b hb => ih b (includes b hb)) rule
    | tail _ hb => exact ih a hb

theorem traceConflict {L : Type} (truth : L → Prop) {known body : List L}
    (t : Trace truth known) (includes : ∀ a, a ∈ body → a ∈ known)
    (rule : AllHolds truth body → False) : False :=
  conflictSound truth body (fun a ha => traceSound truth t a (includes a ha)) rule

#print axioms PnpSignedHorn.bodySound
#print axioms PnpSignedHorn.forwardSound
#print axioms PnpSignedHorn.conflictSound
#print axioms PnpSignedHorn.traceSound
#print axioms PnpSignedHorn.traceConflict

end PnpSignedHorn
