/-! F034 candidate: checker equality and identifier range tests
with the existing gate result, separate padding construction visits,
and selected encoder events. Encoder work includes both operands even
if either fails. No allocation or Nat bit-complexity assertion.
Independent of the pending binary reference and scanner composition PRs. -/
namespace ProctorCheckerPaddingEncoder
open ProctorPaddingVisits (compareResources compare_projection compare_bounds)
open ProctorCheckerBinaryTests (eqMeter idMeter checkedTest checkedEq checkedId
  checked_eq_bound checked_id_bound checked_eq_value checked_id_value)
open ProctorCheckedBinaryScanner (encode encode_sound cap)
open ProctorEncodeVisits (encodeMeter encode_projection encode_bound budget)
open ProctorCapacityReplay (test)
open ProctorUnifiedReplay (validId)

def eqResources (a b : List Bool) : (Bool × Nat) × Nat :=
  let l := compareResources a b
  let r := compareResources b a
  ((!l.1.1 && !r.1.1,l.1.2+r.1.2+3),l.2+r.2)

def idResources (n v : List Bool) : (Bool × Nat) × Nat :=
  let l := compareResources [] v
  let r := compareResources n v
  ((l.1.1 && !r.1.1,l.1.2+r.1.2+2),l.2+r.2)

theorem eq_projection (a b : List Bool) : (eqResources a b).1=eqMeter a b := by
  change (!(compareResources a b).1.1 && !(compareResources b a).1.1,
    (compareResources a b).1.2+(compareResources b a).1.2+3)=_
  rw [compare_projection a b,compare_projection b a] <;> rfl

theorem id_projection (n v : List Bool) : (idResources n v).1=idMeter n v := by
  change ((compareResources [] v).1.1 && !(compareResources n v).1.1,
    (compareResources [] v).1.2+(compareResources n v).1.2+2)=_
  rw [compare_projection [] v,compare_projection n v] <;> rfl

theorem eq_padding_bound (a b : List Bool) (w : Nat)
    (ha : a.length≤w) (hb : b.length≤w) : (eqResources a b).2≤w+w :=
  Nat.add_le_add (compare_bounds a b w ha hb).right (compare_bounds b a w hb ha).right

theorem id_padding_bound (n v : List Bool) (w : Nat)
    (hn : n.length≤w) (hv : v.length≤w) : (idResources n v).2≤w+w :=
  Nat.add_le_add (compare_bounds [] v w (Nat.zero_le _) hv).right
    (compare_bounds n v w hn hv).right

-- Substitute the metered encoder and the padded circuits. Preserve the
-- entire previous (optional Boolean, gates) pair, including rejection.
-- Shape: (((result, gates), padding), encoder selected events).
def checkedResources (w : Nat)
    (f : List Bool → List Bool → (Bool × Nat) × Nat)
    (a b : Nat) : ((Option Bool × Nat) × Nat) × Nat :=
  let x := encodeMeter w a
  let y := encodeMeter w b
  let p := match x.1,y.1 with
    | some xs,some ys =>
      let q := f xs ys
      ((some q.1.1,q.1.2),q.2)
    | _,_ => ((none,0),0)
  (p,x.2+y.2)

theorem checked_gate_projection (w : Nat)
    (f : List Bool → List Bool → (Bool × Nat) × Nat)
    (g : List Bool → List Bool → Bool × Nat)
    (hf : ∀ x y, (f x y).1=g x y) (a b : Nat) :
    (checkedResources w f a b).1.1=checkedTest w g a b := by
  change (match (encodeMeter w a).1,(encodeMeter w b).1 with
    | some x,some y => ((some (f x y).1.1,(f x y).1.2),(f x y).2)
    | _,_ => ((none,0),0)).1=checkedTest w g a b
  rw [encode_projection w a,encode_projection w b]
  unfold checkedTest
  cases ex : encode w a with
  | none => rfl
  | some x =>
    cases ey : encode w b with
    | none => rfl
    | some y =>
      change (some (f x y).1.1,(f x y).1.2)=(some (g x y).1,(g x y).2)
      rw [hf x y]

theorem checked_padding_bound (w K : Nat)
    (f : List Bool → List Bool → (Bool × Nat) × Nat)
    (hf : ∀ x y, x.length≤w → y.length≤w → (f x y).2≤K)
    (a b : Nat) : (checkedResources w f a b).1.2≤K := by
  change (match (encodeMeter w a).1,(encodeMeter w b).1 with
    | some x,some y => ((some (f x y).1.1,(f x y).1.2),(f x y).2)
    | _,_ => ((none,0),0)).2≤K
  rw [encode_projection w a,encode_projection w b]
  cases ex : encode w a with
  | none => exact Nat.zero_le _
  | some x =>
    cases ey : encode w b with
    | none => exact Nat.zero_le _
    | some y =>
      have hx : x.length≤w := by
        rw [(encode_sound w a x ex).left]
        exact Nat.le_refl _
      have hy : y.length≤w := by
        rw [(encode_sound w b y ey).left]
        exact Nat.le_refl _
      exact hf x y hx hy

theorem checked_encoder_bound (w : Nat)
    (f : List Bool → List Bool → (Bool × Nat) × Nat) (a b : Nat) :
    (checkedResources w f a b).2≤budget w+budget w :=
  Nat.add_le_add (encode_bound w a) (encode_bound w b)

def checkedEqResources (w : Nat) := checkedResources w eqResources
def checkedIdResources (w : Nat) := checkedResources w idResources

theorem eq_checked_projection (w a b : Nat) :
    (checkedEqResources w a b).1.1=checkedEq w a b :=
  checked_gate_projection w eqResources eqMeter eq_projection a b

theorem id_checked_projection (w n v : Nat) :
    (checkedIdResources w n v).1.1=checkedId w n v :=
  checked_gate_projection w idResources idMeter id_projection n v

theorem eq_bounds (w a b : Nat) :
    (checkedEqResources w a b).1.1.2≤(5*w+5*w)+3 ∧
    (checkedEqResources w a b).1.2≤w+w ∧
    (checkedEqResources w a b).2≤budget w+budget w := by
  constructor
  · rw [eq_checked_projection]
    exact checked_eq_bound w a b
  · exact ⟨checked_padding_bound w (w+w) eqResources
      (fun x y => eq_padding_bound x y w) a b,checked_encoder_bound w eqResources a b⟩

theorem id_bounds (w n v : Nat) :
    (checkedIdResources w n v).1.1.2≤(5*w+5*w)+2 ∧
    (checkedIdResources w n v).1.2≤w+w ∧
    (checkedIdResources w n v).2≤budget w+budget w := by
  constructor
  · rw [id_checked_projection]
    exact checked_id_bound w n v
  · exact ⟨checked_padding_bound w (w+w) idResources
      (fun x y => id_padding_bound x y w) n v,checked_encoder_bound w idResources n v⟩

theorem eq_value (w a b : Nat) (ha : a<cap w) (hb : b<cap w) :
    (checkedEqResources w a b).1.1.1=some (test (a=b)) := by
  rw [eq_checked_projection]
  exact checked_eq_value w a b ha hb

theorem id_value (w n v : Nat) (hn : n<cap w) (hv : v<cap w) :
    (checkedIdResources w n v).1.1.1=some (validId n v) := by
  rw [id_checked_projection]
  exact checked_id_value w n v hn hv

end ProctorCheckerPaddingEncoder

#print axioms ProctorCheckerPaddingEncoder.eq_projection
#print axioms ProctorCheckerPaddingEncoder.id_projection
#print axioms ProctorCheckerPaddingEncoder.eq_padding_bound
#print axioms ProctorCheckerPaddingEncoder.id_padding_bound
#print axioms ProctorCheckerPaddingEncoder.checked_gate_projection
#print axioms ProctorCheckerPaddingEncoder.checked_padding_bound
#print axioms ProctorCheckerPaddingEncoder.checked_encoder_bound
#print axioms ProctorCheckerPaddingEncoder.eq_checked_projection
#print axioms ProctorCheckerPaddingEncoder.id_checked_projection
#print axioms ProctorCheckerPaddingEncoder.eq_bounds
#print axioms ProctorCheckerPaddingEncoder.id_bounds
#print axioms ProctorCheckerPaddingEncoder.eq_value
#print axioms ProctorCheckerPaddingEncoder.id_value
