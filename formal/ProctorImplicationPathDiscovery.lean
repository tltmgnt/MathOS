/-! F035/F040: bounded implication reachability and checked path compilation.
The fallback is the verified binary-square/exhaustive discovery interface.
Standalone graph completeness and bit-cost theorems are separate obligations. -/
namespace ProctorImplicationPathDiscovery
open ProctorHallDeficiency
open ProctorCapacityDeficiency (opposite)
open ProctorExecutableReplay (Step lookup stepCheck)
open ProctorUnifiedReplay (Proof boundCheck validFormula)
open ProctorResolutionBridge (Unsat step_complete compile)
open ProctorExecutableDiscovery (findRow contained contained_complete contained_sound find_complete find_sound)
open ProctorBinarySquareDiscovery (checked checked_sound checked_complete)

abbrev Arc := Literal × Literal

-- Both orientations of a binary clause, and the implication of a unit.
def rowArcs : Clause → List Arc
  | [a] => [(opposite a,a)]
  | [a,b] => [(opposite a,b),(opposite b,a)]
  | _ => []

def arcs : Formula → List Arc
  | [] => []
  | c::cs => rowArcs c ++ arcs cs

def Edge (f : Formula) (a b : Literal) : Prop :=
  ∃ c∈f, ∀ l∈c, l∈[opposite a,b]

def Holds (x : Assignment) (a : Literal) : Prop := x a.1=a.2

theorem opposite_twice (a : Literal) : opposite (opposite a)=a := by
  cases a with
  | mk v b => cases b <;> rfl

theorem opposite_excludes (x : Assignment) (a : Literal)
    (ha : Holds x a) (hb : Holds x (opposite a)) : False := by
  cases a with
  | mk v b =>
    cases b with
    | false =>
      change x v=false at ha
      change x v=true at hb
      exact Bool.noConfusion (ha.symm.trans hb)
    | true =>
      change x v=true at ha
      change x v=false at hb
      exact Bool.noConfusion (ha.symm.trans hb)

theorem edge_sound (f : Formula) (x : Assignment) (a b : Literal)
    (hf : FormulaSat f x) (he : Edge f a b) (ha : Holds x a) :
    Holds x b := by
  obtain ⟨c,hc,hsub⟩ := he
  obtain ⟨l,hl,ht⟩ := hf c hc
  have hm := hsub l hl
  cases hm with
  | head => exact (opposite_excludes x a ha ht).elim
  | tail _ hm =>
    cases hm with
    | head => exact ht
    | tail _ hz => cases hz

inductive Path (f : Formula) : Literal → Literal → Prop where
  | refl (a : Literal) : Path f a a
  | cons {a b c : Literal} : Edge f a b → Path f b c → Path f a c

theorem path_sound (f : Formula) (x : Assignment) {a b : Literal}
    (h : Path f a b) (hf : FormulaSat f x) (ha : Holds x a) : Holds x b := by
  induction h with
  | refl => exact ha
  | cons he hp ih => exact ih (edge_sound f x _ _ hf he ha)

theorem mutual_paths_unsat (f : Formula) (v : Nat)
    (hp : Path f (v,true) (v,false)) (hn : Path f (v,false) (v,true)) :
    Unsat f := by
  intro h
  obtain ⟨x,hx⟩ := h
  cases e : x v with
  | true =>
    have he : Holds x (v,true) := e
    exact opposite_excludes x (v,true) he (path_sound f x hp hx he)
  | false =>
    have he : Holds x (v,false) := e
    exact opposite_excludes x (v,false) he (path_sound f x hn hx he)

theorem path_append_edge (f : Formula) {a b c : Literal}
    (h : Path f a b) (e : Edge f b c) : Path f a c := by
  induction h with
  | refl => exact Path.cons e (Path.refl _)
  | cons h _ ih => exact Path.cons h (ih e)

private theorem row_arc_sound (c : Clause) (e : Arc) (he : e∈rowArcs c) :
    ∀ l∈c, l∈[opposite e.1,e.2] := by
  cases c with
  | nil => cases he
  | cons a cs =>
    cases cs with
    | nil =>
      change e∈[(opposite a,a)] at he
      cases he with
      | head =>
        intro l hl
        cases hl with
        | head => exact List.Mem.tail _ (List.Mem.head _)
        | tail _ hz => cases hz
      | tail _ hz => cases hz
    | cons b bs =>
      cases bs with
      | nil =>
        change e∈[(opposite a,b),(opposite b,a)] at he
        cases he with
        | head =>
          change ∀ l∈[a,b], l∈[opposite (opposite a),b]
          rw [opposite_twice]
          exact fun _ h => h
        | tail _ ht =>
          cases ht with
          | head =>
            change ∀ l∈[a,b], l∈[opposite (opposite b),a]
            rw [opposite_twice]
            intro l hl
            cases hl with
            | head => exact List.Mem.tail _ (List.Mem.head _)
            | tail _ hm =>
              cases hm with
              | head => exact List.Mem.head _
              | tail _ hz => cases hz
          | tail _ hz => cases hz
      | cons d ds => cases he

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

theorem arcs_sound (f : Formula) (e : Arc) (he : e∈arcs f) :
    Edge f e.1 e.2 := by
  induction f with
  | nil => cases he
  | cons c cs ih =>
    change e∈rowArcs c ++ arcs cs at he
    cases append_cases (rowArcs c) (arcs cs) e he with
    | inl h => exact ⟨c,List.Mem.head _,row_arc_sound c e h⟩
    | inr h =>
      obtain ⟨d,hd,hs⟩ := ih h
      exact ⟨d,List.Mem.tail _ hd,hs⟩

theorem edge_find (f g : Formula) (a b : Literal)
    (he : Edge f a b) (sub : ∀ c∈f, c∈g) :
    ∃ i, findRow (contained [opposite a,b]) g=some i := by
  obtain ⟨c,hc,hs⟩ := he
  exact find_complete _ _ ⟨c,sub c hc,contained_complete _ _ hs⟩

-- Reachability saturation. Each destination is inserted at most once;
-- paths are retained as forward vertex lists excluding the source.
abbrev Routes := List (Literal × List Literal)

def routeFor (a : Literal) : Routes → Option (List Literal)
  | [] => none
  | (b,ps)::rs => if a=b then some ps else routeFor a rs

def relax (rs : Routes) (e : Arc) : Routes :=
  match routeFor e.1 rs, routeFor e.2 rs with
  | some ps,none => (e.2,ps++[e.2])::rs
  | _,_ => rs

def sweep (es : List Arc) (rs : Routes) : Routes :=
  es.foldl relax rs

def saturate (es : List Arc) : Nat → Routes → Routes
  | 0,rs => rs
  | k+1,rs => saturate es k (sweep es rs)

def reach (es : List Arc) (a b : Literal) : Option (List Literal) :=
  routeFor b (saturate es es.length [(a,[])])

def RouteOK (f : Formula) (a : Literal) (rs : Routes) : Prop :=
  ∀ e∈rs, Path f a e.1

theorem routeFor_sound (f : Formula) (a b : Literal) (rs : Routes)
    (h : RouteOK f a rs) (ps : List Literal) (hp : routeFor b rs=some ps) :
    Path f a b := by
  induction rs with
  | nil => cases hp
  | cons e rs ih =>
    cases e with
    | mk c qs =>
      change (if b=c then some qs else routeFor b rs)=some ps at hp
      by_cases z : b=c
      · cases z
        exact h (b,qs) (List.Mem.head _)
      · rw [if_neg z] at hp
        exact ih (fun e he => h e (List.Mem.tail _ he)) hp

theorem relax_preserves (f : Formula) (a : Literal) (rs : Routes) (e : Arc)
    (h : RouteOK f a rs) (he : Edge f e.1 e.2) :
    RouteOK f a (relax rs e) := by
  unfold relax
  cases hs : routeFor e.1 rs with
  | none => exact h
  | some ps =>
    cases hd : routeFor e.2 rs with
    | some _qs => exact h
    | none =>
      intro p hp
      change p∈(e.2,ps++[e.2])::rs at hp
      cases hp with
      | head => exact path_append_edge f (routeFor_sound f a e.1 rs h ps hs) he
      | tail _ hm => exact h p hm

theorem sweep_preserves (f : Formula) (a : Literal) (es : List Arc) (rs : Routes)
    (h : RouteOK f a rs) (he : ∀ e∈es, Edge f e.1 e.2) :
    RouteOK f a (sweep es rs) := by
  induction es generalizing rs with
  | nil => exact h
  | cons e es ih =>
    change RouteOK f a (sweep es (relax rs e))
    exact ih _ (relax_preserves f a rs e h (he e (List.Mem.head _)))
      (fun e hm => he e (List.Mem.tail _ hm))

theorem saturate_preserves (f : Formula) (a : Literal) (es : List Arc)
    (fuel : Nat) (rs : Routes) (h : RouteOK f a rs)
    (he : ∀ e∈es, Edge f e.1 e.2) :
    RouteOK f a (saturate es fuel rs) := by
  induction fuel generalizing rs with
  | zero => exact h
  | succ k ih =>
    exact ih _ (sweep_preserves f a es rs h he)

theorem reach_sound (f : Formula) (a b : Literal) (ps : List Literal)
    (h : reach (arcs f) a b=some ps) : Path f a b := by
  have h0 : RouteOK f a [(a,[])] := by
    intro e he
    cases he with
    | head => exact Path.refl _
    | tail _ hz => cases hz
  exact routeFor_sound f a b _ (saturate_preserves f a (arcs f) (arcs f).length
    _ h0 (arcs_sound f)) ps h

theorem reach_pair_unsat (f : Formula) (v : Nat) (ps qs : List Literal)
    (hp : reach (arcs f) (v,true) (v,false)=some ps)
    (hq : reach (arcs f) (v,false) (v,true)=some qs) :
    Unsat f :=
  mutual_paths_unsat f v (reach_sound f _ _ ps hp) (reach_sound f _ _ qs hq)

-- Local compilation preserves two-literal implication clauses.
-- Duplicate literals in the final implication are allowed by the checker.
def advanceStep (s a b : Literal) (i : Nat) : Step :=
  if a.2 then ⟨0,i,a.1,[opposite s,b]⟩
  else ⟨i,0,a.1,[opposite s,b]⟩

private theorem pair_left (s a b : Literal) :
    ∀ l∈[opposite s,a], l=a ∨ l∈[opposite s,b] := by
  intro l hl
  cases hl with
  | head => exact Or.inr (List.Mem.head _)
  | tail _ hm =>
    cases hm with
    | head => exact Or.inl rfl
    | tail _ hz => cases hz

private theorem pair_right (s a b : Literal) :
    ∀ l∈[opposite a,b], l=opposite a ∨ l∈[opposite s,b] := by
  intro l hl
  cases hl with
  | head => exact Or.inl rfl
  | tail _ hm =>
    cases hm with
    | head => exact Or.inr (List.Mem.tail _ (List.Mem.head _))
    | tail _ hz => cases hz

theorem advance_checked (g : Formula) (s a b : Literal) (i : Nat)
    (h0 : lookup g 0=some [opposite s,a])
    (hi : findRow (contained [opposite a,b]) g=some i) :
    stepCheck g (advanceStep s a b i)=true := by
  obtain ⟨c,hc,hs⟩ := find_sound _ _ _ hi
  have hr : ∀ l∈c, l=opposite a ∨ l∈[opposite s,b] :=
    fun l hl => pair_right s a b l (contained_sound _ _ hs l hl)
  have hp := pair_left s a b
  cases a with
  | mk v pol =>
    cases pol with
    | true =>
      exact step_complete g ⟨0,i,v,[opposite s,b]⟩ _ _ h0 hc hp hr
    | false =>
      exact step_complete g ⟨i,0,v,[opposite s,b]⟩ _ _ hc h0 hr hp

def firstStep (s b : Literal) (i : Nat) : Step :=
  ⟨i,i,s.1,[opposite s,b]⟩

theorem first_checked (g : Formula) (s b : Literal) (i : Nat)
    (hi : findRow (contained [opposite s,b]) g=some i) :
    stepCheck g (firstStep s b i)=true := by
  obtain ⟨c,hc,hs⟩ := find_sound _ _ _ hi
  exact step_complete g (firstStep s b i) c c hc hc
    (fun l hl => Or.inr (contained_sound _ _ hs l hl))
    (fun l hl => Or.inr (contained_sound _ _ hs l hl))

def pathTail (s a : Literal) (g : Formula) : List Literal → Option (List Step × Formula)
  | [] => some ([],g)
  | b::bs => do
    let i ← findRow (contained [opposite a,b]) g
    let t := advanceStep s a b i
    let (ts,h) ← pathTail s b (t.tail::g) bs
    some (t::ts,h)

def pathStart (g : Formula) (s : Literal) : List Literal → Option (List Step × Formula)
  | [] => none
  | b::bs => do
    let i ← findRow (contained [opposite s,b]) g
    let t := firstStep s b i
    let (ts,h) ← pathTail s b (t.tail::g) bs
    some (t::ts,h)

-- The positive endpoint is on top of the frontier; the negative
-- endpoint was prepended by the first path and shifted by the second.
def closeStep (v offset : Nat) : Step := ⟨0,offset,v,[]⟩

private theorem same_pair (a : Literal) :
    ∀ l∈[a,a], l=a ∨ l∈([] : Clause) := by
  intro l hl
  cases hl with
  | head => exact Or.inl rfl
  | tail _ hm =>
    cases hm with
    | head => exact Or.inl rfl
    | tail _ hz => cases hz

theorem close_checked (g : Formula) (v offset : Nat)
    (hp : lookup g 0=some [(v,true),(v,true)])
    (hn : lookup g offset=some [(v,false),(v,false)]) :
    stepCheck g (closeStep v offset)=true :=
  step_complete g (closeStep v offset) _ _ hp hn (same_pair _) (same_pair _)

def compilePair (f : Formula) (v : Nat) (pos neg : List Literal) : Option Proof := do
  let (a,g) ← pathStart f (v,true) pos
  let (b,_) ← pathStart g (v,false) neg
  some ⟨compile v f (a++(b++[closeStep v b.length])),false,.empty⟩

def tryVar (f : Formula) (es : List Arc) (v : Nat) : Option Proof := do
  let pos ← reach es (v,true) (v,false)
  let neg ← reach es (v,false) (v,true)
  compilePair f v pos neg

def scan (f : Formula) (es : List Arc) : List Nat → Option Proof
  | [] => none
  | v::vs =>
    match tryVar f es v with
    | some p => some p
    | none => scan f es vs

def candidate (f : Formula) : Option Proof :=
  scan f (arcs f) (ProctorOrdinaryCompleteness.variables f)

def discover (n : Nat) (f : Formula) : Option Proof :=
  match checked n f (candidate f) with
  | some p => some p
  | none => ProctorBinarySquareDiscovery.discover n f

theorem discover_accepts (n : Nat) (f : Formula) (p : Proof)
    (h : discover n f=some p) : boundCheck n f ⟨n,f,p⟩=true := by
  unfold discover at h
  cases e : checked n f (candidate f) with
  | none =>
    rw [e] at h
    exact ProctorBinarySquareDiscovery.discover_accepts n f p h
  | some q =>
    rw [e] at h
    change some q=some p at h
    cases h
    exact checked_sound n f _ _ e

theorem discover_complete (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hu : Unsat f) :
    ∃ p, discover n f=some p := by
  unfold discover
  cases e : checked n f (candidate f) with
  | some p => exact ⟨p,rfl⟩
  | none => exact ProctorBinarySquareDiscovery.discover_complete n f hf hu

theorem discover_iff (n : Nat) (f : Formula) (hf : validFormula n f=true) :
    (∃ p, discover n f=some p) ↔ Unsat f := by
  constructor
  · intro h
    obtain ⟨p,hp⟩ := h
    exact ProctorUnifiedReplay.bound_sound n f _ (discover_accepts n f p hp)
  · exact discover_complete n f hf

end ProctorImplicationPathDiscovery

#print axioms ProctorImplicationPathDiscovery.opposite_twice
#print axioms ProctorImplicationPathDiscovery.opposite_excludes
#print axioms ProctorImplicationPathDiscovery.edge_sound
#print axioms ProctorImplicationPathDiscovery.path_sound
#print axioms ProctorImplicationPathDiscovery.mutual_paths_unsat
#print axioms ProctorImplicationPathDiscovery.edge_find
#print axioms ProctorImplicationPathDiscovery.advance_checked
#print axioms ProctorImplicationPathDiscovery.first_checked
#print axioms ProctorImplicationPathDiscovery.close_checked
#print axioms ProctorImplicationPathDiscovery.discover_accepts
#print axioms ProctorImplicationPathDiscovery.discover_complete
#print axioms ProctorImplicationPathDiscovery.discover_iff

#print axioms ProctorImplicationPathDiscovery.path_append_edge
#print axioms ProctorImplicationPathDiscovery.arcs_sound
#print axioms ProctorImplicationPathDiscovery.routeFor_sound
#print axioms ProctorImplicationPathDiscovery.relax_preserves
#print axioms ProctorImplicationPathDiscovery.sweep_preserves
#print axioms ProctorImplicationPathDiscovery.saturate_preserves
#print axioms ProctorImplicationPathDiscovery.reach_sound
#print axioms ProctorImplicationPathDiscovery.reach_pair_unsat
