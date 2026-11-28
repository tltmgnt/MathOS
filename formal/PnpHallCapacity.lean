import Init

namespace PnpHallCapacity

def occupancy : List Nat → Nat
  | [] => 0
  | c :: cs => c + occupancy cs

/-- If each bucket holds at most one selected item, total occupancy is
bounded by the number of buckets. This is the cardinality step, not a
formalization of the Python CNF-to-bucket extraction. -/
theorem bucketCapacity (counts : List Nat)
    (h : ∀ c, c ∈ counts → c ≤ 1) :
    occupancy counts ≤ counts.length := by
  induction counts with
  | nil => exact Nat.le_refl 0
  | cons c cs ih =>
    have hc : c ≤ 1 := h c (List.Mem.head cs)
    have ht : occupancy cs ≤ cs.length :=
      ih (fun x hx => h x (List.Mem.tail c hx))
    calc
      occupancy (c :: cs) = c + occupancy cs := rfl
      _ ≤ 1 + cs.length := Nat.add_le_add hc ht
      _ = (c :: cs).length := Nat.add_comm 1 cs.length

theorem deficitContradiction (groups : Nat) (counts : List Nat)
    (hcap : ∀ c, c ∈ counts → c ≤ 1)
    (hcount : occupancy counts = groups)
    (deficit : counts.length < groups) : False := by
  have h := bucketCapacity counts hcap
  rw [hcount] at h
  exact Nat.not_le_of_lt deficit h

#print axioms PnpHallCapacity.bucketCapacity
#print axioms PnpHallCapacity.deficitContradiction

end PnpHallCapacity
