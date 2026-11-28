import F038Formal.Resources

/-! FV-06: finite-state quotient simulation for a ternary single-tape worker.
The tape is an unbounded integer-indexed function. The theorem concerns the
physical transition table and quotient, not the two-tape IR compiler. -/
namespace MathOS.F038.Physical
open MathOS.F038.Cert

abbrev Symbol := Fin 3
inductive Direction where
  | left | stay | right
  deriving DecidableEq, Repr

def delta : Direction → Int
  | .left => -1
  | .stay => 0
  | .right => 1

structure Action (n : Nat) where
  next : Fin n
  write : Symbol
  move : Direction
  deriving DecidableEq

structure Machine (n : Nat) where
  initial : Fin n
  halt : Fin n
  action : Fin n → Symbol → Action n

structure Config (n : Nat) where
  state : Fin n
  head : Int
  tape : Int → Symbol

def step {n : Nat} (m : Machine n) (c : Config n) : Config n :=
  if c.state = m.halt then c else
    let a := m.action c.state (c.tape c.head)
    ⟨a.next, c.head + delta a.move,
      fun i => if i = c.head then a.write else c.tape i⟩

-- Fuel is a physical transition budget, not a logical IR step count.
-- A halted configuration is frozen, and no further clock ticks accrue.
def run {n : Nat} (m : Machine n) : Nat → Config n → Config n × Nat
  | 0, c => (c,0)
  | fuel+1, c =>
    if c.state = m.halt then (c,0) else
      let r := run m fuel (step m c)
      (r.1,r.2+1)

def related {n q : Nat} (mapping : Fin n → Option (Fin q))
    (a : Config n) (b : Config q) : Prop :=
  mapping a.state = some b.state ∧ a.head = b.head ∧ a.tape = b.tape

-- Partial maps admit unreachable original states. Mapped successors must
-- remain mapped; halt is distinguished, and writes/moves are identical.
def Local {n q : Nat} (a : Machine n) (b : Machine q)
    (mapping : Fin n → Option (Fin q)) (s : Fin n) : Prop :=
  ∀ t, mapping s = some t →
    (s = a.halt ↔ t = b.halt) ∧
    (s ≠ a.halt → ∀ x : Symbol,
      mapping (a.action s x).next = some (b.action t x).next ∧
      (a.action s x).write = (b.action t x).write ∧
      (a.action s x).move = (b.action t x).move)

def rowCheck {n q : Nat} (a : Machine n) (b : Machine q)
    (mapping : Fin n → Option (Fin q)) (s : Fin n) : Bool :=
  match mapping s with
  | none => true
  | some t =>
    decide (s = a.halt ↔ t = b.halt) &&
    (if s = a.halt then true else
      allCheck (fun x =>
        decide (mapping (a.action s x).next = some (b.action t x).next ∧
          (a.action s x).write = (b.action t x).write ∧
          (a.action s x).move = (b.action t x).move)) (List.finRange 3))

def quotientCheck {n q : Nat} (a : Machine n) (b : Machine q)
    (mapping : Fin n → Option (Fin q)) : Bool :=
  decide (mapping a.initial = some b.initial ∧ mapping a.halt = some b.halt) &&
    allCheck (rowCheck a b mapping) (List.finRange n)

theorem rowCheck_sound {n q : Nat} (a : Machine n) (b : Machine q)
    (mapping : Fin n → Option (Fin q)) (s : Fin n)
    (h : rowCheck a b mapping s = true) : Local a b mapping s := by
  intro t ht
  have hh : (decide (s = a.halt ↔ t = b.halt) &&
    (if s = a.halt then true else
      allCheck (fun x =>
        decide (mapping (a.action s x).next = some (b.action t x).next ∧
          (a.action s x).write = (b.action t x).write ∧
          (a.action s x).move = (b.action t x).move)) (List.finRange 3))) = true := by
    simpa [rowCheck, ht] using h
  obtain ⟨hhalt,hrows⟩ := and_parts hh
  have eq : s = a.halt ↔ t = b.halt := of_decide_eq_true hhalt
  refine ⟨eq, ?_⟩
  intro hn x
  have hr : allCheck (fun x =>
        decide (mapping (a.action s x).next = some (b.action t x).next ∧
          (a.action s x).write = (b.action t x).write ∧
          (a.action s x).move = (b.action t x).move)) (List.finRange 3) = true := by
    simpa [hn] using hrows
  exact of_decide_eq_true (allCheck_sound _ _ hr x (by simp))

theorem quotientCheck_sound {n q : Nat} (a : Machine n) (b : Machine q)
    (mapping : Fin n → Option (Fin q)) (h : quotientCheck a b mapping = true) :
    (mapping a.initial = some b.initial ∧ mapping a.halt = some b.halt) ∧
    ∀ s, Local a b mapping s := by
  obtain ⟨hi,hr⟩ := and_parts (show
    (decide (mapping a.initial = some b.initial ∧ mapping a.halt = some b.halt) &&
      allCheck (rowCheck a b mapping) (List.finRange n)) = true from h)
  exact ⟨of_decide_eq_true hi, fun s => rowCheck_sound a b mapping s
    (allCheck_sound _ _ hr s (by simp))⟩

theorem step_related {n q : Nat} (a : Machine n) (b : Machine q)
    (mapping : Fin n → Option (Fin q)) (valid : ∀ s, Local a b mapping s)
    (c : Config n) (d : Config q) (h : related mapping c d) :
    related mapping (step a c) (step b d) := by
  rcases c with ⟨s,p,tape⟩
  rcases d with ⟨u,r,other⟩
  rcases h with ⟨hm,hp,ht⟩
  dsimp at hm hp ht
  subst r
  subst other
  obtain ⟨hh,ha⟩ := valid s u hm
  by_cases hs : s = a.halt
  · have hu := hh.mp hs
    simpa [step, hs, hu] using (show related mapping ⟨s,p,tape⟩ ⟨u,p,tape⟩ from ⟨hm,rfl,rfl⟩)
  · have hu : u ≠ b.halt := fun h => hs (hh.mpr h)
    obtain ⟨hn,hw,hd⟩ := ha hs (tape p)
    simp only [step, hs, hu, if_false, related]
    exact ⟨hn, by rw [hd], by rw [hw]⟩

theorem run_related {n q : Nat} (a : Machine n) (b : Machine q)
    (mapping : Fin n → Option (Fin q)) (valid : ∀ s, Local a b mapping s)
    (fuel : Nat) (c : Config n) (d : Config q) (h : related mapping c d) :
    related mapping (run a fuel c).1 (run b fuel d).1 ∧
      (run a fuel c).2 = (run b fuel d).2 := by
  induction fuel generalizing c d with
  | zero => exact ⟨h,rfl⟩
  | succ fuel ih =>
    have hh := (valid c.state d.state h.1).1
    by_cases hs : c.state = a.halt
    · have hu := hh.mp hs
      simpa [run, hs, hu] using (show related mapping c d ∧ (0 : Nat) = 0 from ⟨h,rfl⟩)
    · have hu : d.state ≠ b.halt := fun e => hs (hh.mpr e)
      obtain ⟨hr,hc⟩ := ih _ _ (step_related a b mapping valid c d h)
      simp only [run, hs, hu, if_false]
      exact ⟨hr, congrArg (fun x : Nat => x+1) hc⟩

theorem run_clock_le {n : Nat} (a : Machine n) (fuel : Nat) (c : Config n) :
    (run a fuel c).2 ≤ fuel := by
  induction fuel generalizing c with
  | zero => exact Nat.zero_le _
  | succ fuel ih =>
    by_cases hs : c.state = a.halt
    · simp [run, hs]
    · simpa [run, hs] using Nat.succ_le_succ (ih (step a c))

def initialConfig {n : Nat} (m : Machine n) (head : Int) (tape : Int → Symbol) :
    Config n := ⟨m.initial,head,tape⟩

theorem checked_simulation {n q : Nat} (a : Machine n) (b : Machine q)
    (mapping : Fin n → Option (Fin q)) (ok : quotientCheck a b mapping = true)
    (fuel : Nat) (head : Int) (tape : Int → Symbol) :
    let r := run a fuel (initialConfig a head tape)
    let s := run b fuel (initialConfig b head tape)
    related mapping r.1 s.1 ∧ r.2 = s.2 ∧
      (r.1.state = a.halt ↔ s.1.state = b.halt) := by
  obtain ⟨hi,hv⟩ := quotientCheck_sound a b mapping ok
  obtain ⟨hr,hc⟩ := run_related a b mapping hv fuel
    (initialConfig a head tape) (initialConfig b head tape) ⟨hi.1,rfl,rfl⟩
  exact ⟨hr,hc,(hv _ _ hr.1).1⟩

#print axioms quotientCheck_sound
#print axioms step_related
#print axioms run_related
#print axioms run_clock_le
#print axioms checked_simulation

end MathOS.F038.Physical
