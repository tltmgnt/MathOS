/-! F035: exact prefix summaries for the equality relation. A blocked
variable order needs distinct summaries for every prefix, even when
semantic equality, rather than syntax, controls merging. This is a
restricted representation barrier, not a lower bound for SAT. -/
namespace ProctorSymbolicElimination

def equalBits : List Bool → List Bool → Bool
  | [],[] => true
  | a::as,b::bs => if a=b then equalBits as bs else false
  | _,_ => false

theorem equal_refl (xs : List Bool) : equalBits xs xs=true := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (if a=a then equalBits as as else false)=true
    rw [if_pos rfl]
    exact ih

theorem equal_sound (xs ys : List Bool) (h : equalBits xs ys=true) : xs=ys := by
  induction xs generalizing ys with
  | nil =>
    cases ys with
    | nil => rfl
    | cons y ys => cases h
  | cons x xs ih =>
    cases ys with
    | nil => cases h
    | cons y ys =>
      change (if x=y then equalBits xs ys else false)=true at h
      by_cases e : x=y
      · rw [if_pos e] at h
        rw [e,ih ys h]
      · rw [if_neg e] at h
        cases h

theorem equal_complete (xs ys : List Bool) (h : xs=ys) : equalBits xs ys=true := by
  rw [h]
  exact equal_refl ys

def Exact {α : Type} (k : Nat) (encode : List Bool → α)
    (answer : α → List Bool → Bool) : Prop :=
  ∀ xs ys : List Bool, xs.length=k → ys.length=k →
    answer (encode xs) ys=equalBits xs ys

theorem exact_injective {α : Type} (k : Nat) (encode : List Bool → α)
    (answer : α → List Bool → Bool) (h : Exact k encode answer)
    (xs ys : List Bool) (hx : xs.length=k) (hy : ys.length=k)
    (he : encode xs=encode ys) : xs=ys := by
  have h1 := h xs xs hx hx
  have h2 := h ys xs hy hx
  rw [equal_refl xs] at h1
  rw [he] at h1
  exact (equal_sound ys xs (h2.symm.trans h1)).symm

def words : Nat → List (List Bool)
  | 0 => [[]]
  | k+1 => (words k).map (List.cons false) ++ (words k).map (List.cons true)

private theorem map_length {α β : Type} (f : α → β) (xs : List α) :
    (xs.map f).length=xs.length := by
  induction xs with
  | nil => rfl
  | cons x xs ih => exact congrArg Nat.succ ih

private theorem append_length {α : Type} (xs ys : List α) :
    (xs++ys).length=xs.length+ys.length := by
  induction xs with
  | nil => exact (Nat.zero_add _).symm
  | cons x xs ih =>
    change (xs++ys).length+1=xs.length+1+ys.length
    rw [ih,Nat.add_assoc xs.length 1 ys.length,Nat.add_comm 1 ys.length,← Nat.add_assoc]

theorem words_length (k : Nat) : (words k).length=2^k := by
  induction k with
  | zero => rfl
  | succ k ih =>
    change ((words k).map (List.cons false)++(words k).map (List.cons true)).length=2^(k+1)
    rw [append_length,map_length,map_length,ih,Nat.pow_succ,Nat.mul_succ,Nat.mul_one]

private theorem map_origin {α β : Type} (f : α → β) (xs : List α)
    (y : β) (h : y∈xs.map f) : ∃ x∈xs, y=f x := by
  induction xs with
  | nil => cases h
  | cons x xs ih =>
    cases h with
    | head => exact ⟨x,List.Mem.head _,rfl⟩
    | tail _ hm =>
      obtain ⟨z,hz,he⟩ := ih hm
      exact ⟨z,List.Mem.tail _ hz,he⟩

private theorem append_cases {α : Type} (xs ys : List α) (a : α)
    (h : a∈xs++ys) : a∈xs ∨ a∈ys := by
  induction xs with
  | nil => exact Or.inr h
  | cons b bs ih =>
    cases h with
    | head => exact Or.inl (List.Mem.head _)
    | tail _ hm =>
      cases ih hm with
      | inl e => exact Or.inl (List.Mem.tail _ e)
      | inr e => exact Or.inr e

theorem words_width (k : Nat) (xs : List Bool) (h : xs∈words k) : xs.length=k := by
  induction k generalizing xs with
  | zero =>
    change xs∈[[]] at h
    cases h with
    | head => rfl
    | tail _ hm => cases hm
  | succ k ih =>
    change xs∈(words k).map (List.cons false)++(words k).map (List.cons true) at h
    cases append_cases _ _ xs h with
    | inl e =>
      obtain ⟨ys,hy,he⟩ := map_origin (List.cons false) _ xs e
      rw [he]
      exact congrArg Nat.succ (ih ys hy)
    | inr e =>
      obtain ⟨ys,hy,he⟩ := map_origin (List.cons true) _ xs e
      rw [he]
      exact congrArg Nat.succ (ih ys hy)

def Distinct {α : Type} : List α → Prop
  | [] => True
  | a::as => (∀ b∈as, a≠b) ∧ Distinct as

theorem map_distinct {α β : Type} (f : α → β) (xs : List α)
    (hd : Distinct xs) (hi : ∀ a∈xs, ∀ b∈xs, f a=f b → a=b) :
    Distinct (xs.map f) := by
  induction xs with
  | nil => exact True.intro
  | cons a as ih =>
    change (∀ b∈as.map f, f a≠b) ∧ Distinct (as.map f)
    constructor
    · intro b hb he
      obtain ⟨z,hz,hz'⟩ := map_origin f as b hb
      rw [hz'] at he
      exact hd.left z hz (hi a (List.Mem.head _) z (List.Mem.tail _ hz) he)
    · exact ih hd.right (fun b hb c hc he =>
        hi b (List.Mem.tail _ hb) c (List.Mem.tail _ hc) he)

theorem distinct_append {α : Type} (xs ys : List α)
    (hx : Distinct xs) (hy : Distinct ys)
    (sep : ∀ a∈xs,∀ b∈ys,a≠b) : Distinct (xs++ys) := by
  induction xs with
  | nil => exact hy
  | cons a as ih =>
    change (∀ b∈as++ys,a≠b) ∧ Distinct (as++ys)
    constructor
    · intro b hb
      cases append_cases as ys b hb with
      | inl e => exact hx.left b e
      | inr e => exact sep a (List.Mem.head _) b e
    · exact ih hx.right (fun b hb c hc => sep b (List.Mem.tail _ hb) c hc)

theorem words_distinct (k : Nat) : Distinct (words k) := by
  induction k with
  | zero =>
    change (∀ b∈([] : List (List Bool)), ([] : List Bool)≠b) ∧ True
    exact ⟨fun _ h => nomatch h,True.intro⟩
  | succ k ih =>
    change Distinct ((words k).map (List.cons false)++(words k).map (List.cons true))
    apply distinct_append
    · exact map_distinct _ _ ih (fun _ _ _ _ h => (List.cons.inj h).2)
    · exact map_distinct _ _ ih (fun _ _ _ _ h => (List.cons.inj h).2)
    · intro a ha b hb he
      obtain ⟨xs,hx,ha'⟩ := map_origin (List.cons false) _ a ha
      obtain ⟨ys,hy,hb'⟩ := map_origin (List.cons true) _ b hb
      rw [ha',hb'] at he
      exact Bool.noConfusion (List.cons.inj he).1

-- A finite list of 2^k pairwise distinct attainable summary states.
-- This is a state-count witness without classical cardinal arithmetic.
theorem exponential_states {α : Type} (k : Nat) (encode : List Bool → α)
    (answer : α → List Bool → Bool) (h : Exact k encode answer) :
    ∃ states : List α, states.length=2^k ∧ Distinct states ∧
      ∀ s∈states, ∃ xs : List Bool, xs.length=k ∧ s=encode xs := by
  refine ⟨(words k).map encode,?_,?_,?_⟩
  · rw [map_length,words_length]
  · exact map_distinct _ _ (words_distinct k) (fun a ha b hb he =>
      exact_injective k encode answer h a b (words_width k a ha) (words_width k b hb) he)
  · intro s hs
    obtain ⟨xs,hx,he⟩ := map_origin encode _ s hs
    exact ⟨xs,words_width k xs hx,he⟩

-- In contrast, the interleaved equality test only needs a flag that
-- records whether any corresponding pair differs.
def paired : List (Bool × Bool) → Bool
  | [] => true
  | (a,b)::ps => if a=b then paired ps else false

def leftBits : List (Bool × Bool) → List Bool
  | [] => []
  | p::ps => p.1::leftBits ps

def rightBits : List (Bool × Bool) → List Bool
  | [] => []
  | p::ps => p.2::rightBits ps

theorem paired_correct (ps : List (Bool × Bool)) :
    paired ps=equalBits (leftBits ps) (rightBits ps) := by
  induction ps with
  | nil => rfl
  | cons p ps ih =>
    cases p with
    | mk a b =>
      change (if a=b then paired ps else false)=(if a=b then equalBits (leftBits ps) (rightBits ps) else false)
      rw [ih]

end ProctorSymbolicElimination

#print axioms ProctorSymbolicElimination.equal_refl
#print axioms ProctorSymbolicElimination.equal_sound
#print axioms ProctorSymbolicElimination.equal_complete
#print axioms ProctorSymbolicElimination.exact_injective
#print axioms ProctorSymbolicElimination.words_length
#print axioms ProctorSymbolicElimination.words_width
#print axioms ProctorSymbolicElimination.map_distinct
#print axioms ProctorSymbolicElimination.distinct_append
#print axioms ProctorSymbolicElimination.words_distinct
#print axioms ProctorSymbolicElimination.exponential_states
#print axioms ProctorSymbolicElimination.paired_correct
