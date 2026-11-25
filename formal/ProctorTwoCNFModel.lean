/-! F035/F040: constructive 2-CNF model extraction by ranking complete
reachability bit vectors. All comparisons are executable, with no choice
of SCC ordering and no exhaustive assignment enumeration. -/
namespace ProctorTwoCNFModel
open ProctorHallDeficiency
open ProctorCapacityDeficiency (opposite)
open ProctorImplicationPathDiscovery (Arc rowArcs arcs reach mutual_paths_unsat reach_pair_unsat opposite_twice)
open ProctorPathCompilerCompleteness (Walk walk_snoc reach_witness checked_tryVar_complete)
open ProctorReachabilityCompleteness (WalkN reach_complete)
open ProctorOrdinaryCompleteness (variables variable_mem)
open ProctorResolutionBridge (Unsat)
open ProctorUnifiedReplay (Proof validFormula boundCheck)
open ProctorBinarySquareDiscovery (checked checked_sound)
open ProctorImplicationPathDiscovery (tryVar)

def R (es : List Arc) (a b : Literal) : Bool := (reach es a b).isSome

theorem r_iff (es : List Arc) (a b : Literal) :
    R es a b=true ↔ ∃ ps, reach es a b=some ps := by
  unfold R
  cases h : reach es a b with
  | none =>
    constructor
    · intro e
      cases e
    · intro e
      obtain ⟨ps,hp⟩ := e
      cases hp
  | some ps =>
    exact ⟨fun _ => ⟨ps,rfl⟩,fun _ => rfl⟩

theorem walk_index (es : List Arc) {a b : Literal} {ps : List Literal}
    (h : Walk es a ps b) : WalkN es ps.length a b := by
  induction h with
  | nil => exact WalkN.nil _
  | cons he _ ih => exact WalkN.cons he ih

theorem walk_reaches (es : List Arc) {a b : Literal} {ps : List Literal}
    (h : Walk es a ps b) : R es a b=true :=
  (r_iff es a b).2 (reach_complete es a b ps.length (walk_index es h))

theorem r_refl (es : List Arc) (a : Literal) : R es a a=true :=
  walk_reaches es (Walk.nil a)

theorem r_edge (es : List Arc) (a b : Literal) (h : (a,b)∈es) :
    R es a b=true := walk_reaches es (Walk.cons h (Walk.nil b))

theorem walk_append (es : List Arc) {a b c : Literal} {ps qs : List Literal}
    (h : Walk es a ps b) (k : Walk es b qs c) : Walk es a (ps++qs) c := by
  induction h with
  | nil => exact k
  | cons he _ ih => exact Walk.cons he (ih k)

theorem r_trans (es : List Arc) (a b c : Literal)
    (h : R es a b=true) (k : R es b c=true) : R es a c=true := by
  obtain ⟨ps,hp⟩ := (r_iff es a b).1 h
  obtain ⟨qs,hq⟩ := (r_iff es b c).1 k
  exact walk_reaches es (walk_append es (reach_witness es a b ps hp)
    (reach_witness es b c qs hq))

private theorem append_cases {α : Type} (xs ys : List α) (a : α)
    (h : a∈xs++ys) : a∈xs ∨ a∈ys := by
  induction xs with
  | nil => exact Or.inr h
  | cons x xs ih =>
    cases h with
    | head => exact Or.inl (List.Mem.head _)
    | tail _ hm =>
      cases ih hm with
      | inl e => exact Or.inl (List.Mem.tail _ e)
      | inr e => exact Or.inr e

private theorem append_left {α : Type} (xs ys : List α) (a : α)
    (h : a∈xs) : a∈xs++ys := by
  induction xs with
  | nil => cases h
  | cons x xs ih =>
    cases h with
    | head => exact List.Mem.head _
    | tail _ hm => exact List.Mem.tail _ (ih hm)

private theorem append_right {α : Type} (xs ys : List α) (a : α)
    (h : a∈ys) : a∈xs++ys := by
  induction xs with
  | nil => exact h
  | cons x xs ih => exact List.Mem.tail _ ih

theorem row_dual (c : Clause) (a b : Literal) (h : (a,b)∈rowArcs c) :
    (opposite b,opposite a)∈rowArcs c := by
  cases c with
  | nil => cases h
  | cons l ls =>
    cases ls with
    | nil =>
      change (a,b)∈[(opposite l,l)] at h
      cases h with
      | head =>
        change (opposite l,opposite (opposite l))∈[(opposite l,l)]
        rw [opposite_twice]
        exact List.Mem.head _
      | tail _ hz => cases hz
    | cons k ks =>
      cases ks with
      | nil =>
        change (a,b)∈[(opposite l,k),(opposite k,l)] at h
        cases h with
        | head =>
          change (opposite k,opposite (opposite l))∈[(opposite l,k),(opposite k,l)]
          rw [opposite_twice]
          exact List.Mem.tail _ (List.Mem.head _)
        | tail _ ht =>
          cases ht with
          | head =>
            change (opposite l,opposite (opposite k))∈[(opposite l,k),(opposite k,l)]
            rw [opposite_twice]
            exact List.Mem.head _
          | tail _ hz => cases hz
      | cons _ _ => cases h

theorem arc_dual (f : Formula) (a b : Literal) (h : (a,b)∈arcs f) :
    (opposite b,opposite a)∈arcs f := by
  induction f with
  | nil => cases h
  | cons c cs ih =>
    change (a,b)∈rowArcs c++arcs cs at h
    cases append_cases (rowArcs c) (arcs cs) (a,b) h with
    | inl he => exact append_left _ _ _ (row_dual c a b he)
    | inr he => exact append_right _ _ _ (ih he)

theorem walk_dual (f : Formula) {a b : Literal} {ps : List Literal}
    (h : Walk (arcs f) a ps b) :
    ∃ qs, Walk (arcs f) (opposite b) qs (opposite a) := by
  induction h with
  | nil => exact ⟨[],Walk.nil _⟩
  | @cons a b z bs he _ ih =>
    obtain ⟨qs,hq⟩ := ih
    exact ⟨qs++[opposite a],walk_snoc _ hq (arc_dual f a b he)⟩

theorem r_dual (f : Formula) (a b : Literal) (h : R (arcs f) a b=true) :
    R (arcs f) (opposite b) (opposite a)=true := by
  obtain ⟨ps,hp⟩ := (r_iff _ _ _).1 h
  obtain ⟨qs,hq⟩ := walk_dual f (reach_witness _ _ _ ps hp)
  exact walk_reaches _ hq

theorem row_in_arcs (f : Formula) (c : Clause) (e : Arc)
    (hc : c∈f) (he : e∈rowArcs c) : e∈arcs f := by
  induction f with
  | nil => cases hc
  | cons d ds ih =>
    cases hc with
    | head => exact append_left _ _ _ he
    | tail _ hm => exact append_right _ _ _ (ih hm)

def vertices : List Nat → List Literal
  | [] => []
  | v::vs => (v,true)::(v,false)::vertices vs

theorem vertex_mem (vs : List Nat) (v : Nat) (b : Bool) (h : v∈vs) :
    (v,b)∈vertices vs := by
  induction vs with
  | nil => cases h
  | cons w ws ih =>
    cases h with
    | head =>
      cases b with
      | true => exact List.Mem.head _
      | false => exact List.Mem.tail _ (List.Mem.head _)
    | tail _ hm => exact List.Mem.tail _ (List.Mem.tail _ (ih hm))

-- A bit vector is encoded little-endian. Multiplicity of vertices is
-- harmless. Numeric magnitude is exponential, bit length is linear.
def bit (b : Bool) : Nat := if b then 1 else 0

def rank (p : Literal → Bool) : List Literal → Nat
  | [] => 0
  | a::as => bit (p a)+2*rank p as

theorem rank_mono (p q : Literal → Bool) (vs : List Literal)
    (h : ∀ a∈vs, p a=true → q a=true) : rank p vs≤rank q vs := by
  induction vs with
  | nil => exact Nat.le_refl _
  | cons a as ih =>
    have ht := ih (fun b hb => h b (List.Mem.tail _ hb))
    have hb := h a (List.Mem.head _)
    change bit (p a)+2*rank p as≤bit (q a)+2*rank q as
    cases ep : p a <;> cases eq : q a
    · change 0+2*rank p as≤0+2*rank q as
      omega
    · change 0+2*rank p as≤1+2*rank q as
      omega
    · have hfalse : false=true := eq.symm.trans (hb ep)
      cases hfalse
    · change 1+2*rank p as≤1+2*rank q as
      omega

theorem rank_eq_bits (p q : Literal → Bool) (vs : List Literal)
    (h : rank p vs=rank q vs) : ∀ a∈vs, p a=q a := by
  induction vs with
  | nil => intro a ha; cases ha
  | cons a as ih =>
    change bit (p a)+2*rank p as=bit (q a)+2*rank q as at h
    have he : p a=q a := by
      cases ep : p a <;> cases eq : q a
      · rfl
      · rw [ep,eq] at h
        change 0+2*rank p as=1+2*rank q as at h
        omega
      · rw [ep,eq] at h
        change 1+2*rank p as=0+2*rank q as at h
        omega
      · rfl
    rw [he] at h
    have ht : rank p as=rank q as := by omega
    intro b hb
    cases hb with
    | head => exact he
    | tail _ hm => exact ih ht b hm

def score (f : Formula) (a : Literal) : Nat :=
  rank (R (arcs f) a) (vertices (variables f))

def NoConflict (f : Formula) : Prop :=
  ∀ v∈variables f, ¬(R (arcs f) (v,true) (v,false)=true ∧
    R (arcs f) (v,false) (v,true)=true)

theorem score_edge (f : Formula) (a b : Literal) (h : (a,b)∈arcs f) :
    score f b≤score f a :=
  rank_mono _ _ _ (fun c _ hc => r_trans _ _ _ _ (r_edge _ a b h) hc)

theorem score_distinct (f : Formula) (v : Nat) (hv : v∈variables f)
    (h : NoConflict f) : score f (v,true)≠score f (v,false) := by
  intro he
  have hb := rank_eq_bits _ _ _ he
  have hp := hb (v,true) (vertex_mem _ v true hv)
  have hn := hb (v,false) (vertex_mem _ v false hv)
  exact h v hv ⟨hn.trans (r_refl _ _),hp.symm.trans (r_refl _ _)⟩

def model (f : Formula) : Assignment :=
  fun v => if score f (v,true)<score f (v,false) then true else false

theorem model_lt (f : Formula) (a : Literal) (hv : a.1∈variables f)
    (h : NoConflict f) :
    model f a.1=a.2 ↔ score f a<score f (opposite a) := by
  cases a with
  | mk v b =>
    have hn := score_distinct f v hv h
    cases b with
    | true =>
      change ((if score f (v,true)<score f (v,false) then true else false)=true) ↔
        score f (v,true)<score f (v,false)
      by_cases e : score f (v,true)<score f (v,false)
      · rw [if_pos e]
        exact ⟨fun _ => e,fun _ => rfl⟩
      · rw [if_neg e]
        exact ⟨fun h => (Bool.noConfusion h),fun h => (e h).elim⟩
    | false =>
      change ((if score f (v,true)<score f (v,false) then true else false)=false) ↔
        score f (v,false)<score f (v,true)
      by_cases e : score f (v,true)<score f (v,false)
      · rw [if_pos e]
        exact ⟨fun h => (Bool.noConfusion h),fun h => (Nat.not_lt_of_ge (Nat.le_of_lt e) h).elim⟩
      · rw [if_neg e]
        have hl : score f (v,false)<score f (v,true) := by omega
        exact ⟨fun _ => hl,fun _ => rfl⟩

theorem model_edge (f : Formula) (a b : Literal)
    (ha : a.1∈variables f) (hb : b.1∈variables f) (h : NoConflict f)
    (he : (a,b)∈arcs f) (ht : model f a.1=a.2) : model f b.1=b.2 := by
  have h1 := score_edge f a b he
  have h2 := score_edge f (opposite b) (opposite a) (arc_dual f a b he)
  exact (model_lt f b hb h).2 (Nat.lt_of_le_of_lt h1
    (Nat.lt_of_lt_of_le ((model_lt f a ha h).1 ht) h2))

private theorem model_opposite (f : Formula) (a : Literal)
    (h : model f a.1≠a.2) : model f (opposite a).1=(opposite a).2 := by
  cases a with
  | mk v b =>
    cases b <;> cases e : model f v
    · exact (h e).elim
    · exact e
    · exact e
    · exact (h e).elim

def TwoCNF (f : Formula) : Prop :=
  ∀ c∈f, (∃ a : Literal, c=[a]) ∨ (∃ a b : Literal, c=[a,b])

theorem model_satisfies (f : Formula) (hf : TwoCNF f) (h : NoConflict f) :
    FormulaSat f (model f) := by
  intro c hc
  cases hf c hc with
  | inl hu =>
    obtain ⟨a,ha⟩ := hu
    cases ha
    have hv := variable_mem f [a] a hc (List.Mem.head _)
    refine ⟨a,List.Mem.head _,?_⟩
    by_cases ht : model f a.1=a.2
    · exact ht
    · exact model_edge f (opposite a) a hv hv h
        (row_in_arcs f [a] _ hc (List.Mem.head _)) (model_opposite f a ht)
  | inr hb =>
    obtain ⟨a,b,he⟩ := hb
    cases he
    have hva := variable_mem f [a,b] a hc (List.Mem.head _)
    have hvb := variable_mem f [a,b] b hc (List.Mem.tail _ (List.Mem.head _))
    by_cases ht : model f a.1=a.2
    · exact ⟨a,List.Mem.head _,ht⟩
    · exact ⟨b,List.Mem.tail _ (List.Mem.head _),
        model_edge f (opposite a) b hva hvb h
          (row_in_arcs f [a,b] _ hc (List.Mem.head _)) (model_opposite f a ht)⟩

def conflictAt (f : Formula) (v : Nat) : Bool :=
  R (arcs f) (v,true) (v,false) && R (arcs f) (v,false) (v,true)

def findConflict (f : Formula) : List Nat → Option Nat
  | [] => none
  | v::vs => if conflictAt f v then some v else findConflict f vs

theorem findConflict_none (f : Formula) (vs : List Nat)
    (h : findConflict f vs=none) : ∀ v∈vs, conflictAt f v=false := by
  induction vs with
  | nil => intro v hv; cases hv
  | cons v vs ih =>
    change (if conflictAt f v then some v else findConflict f vs)=none at h
    cases e : conflictAt f v with
    | true => rw [e] at h; cases h
    | false =>
      rw [e] at h
      intro w hw
      cases hw with
      | head => exact e
      | tail _ hm => exact ih h w hm

theorem findConflict_some (f : Formula) (vs : List Nat) (v : Nat)
    (h : findConflict f vs=some v) : conflictAt f v=true := by
  induction vs with
  | nil => cases h
  | cons w ws ih =>
    change (if conflictAt f w then some w else findConflict f ws)=some v at h
    cases e : conflictAt f w with
    | true =>
      rw [e] at h
      cases h
      exact e
    | false =>
      rw [e] at h
      exact ih h

theorem noConflict_of_none (f : Formula) (h : findConflict f (variables f)=none) :
    NoConflict f := by
  intro v hv hp
  have e := findConflict_none f _ h v hv
  unfold conflictAt at e
  rw [hp.left,hp.right] at e
  cases e

theorem conflict_routes (f : Formula) (v : Nat) (h : conflictAt f v=true) :
    ∃ ps qs, reach (arcs f) (v,true) (v,false)=some ps ∧
      reach (arcs f) (v,false) (v,true)=some qs := by
  have he := Bool.and_eq_true.mp h
  obtain ⟨ps,hp⟩ := (r_iff _ _ _).1 he.left
  obtain ⟨qs,hq⟩ := (r_iff _ _ _).1 he.right
  exact ⟨ps,qs,hp,hq⟩

theorem conflict_unsat (f : Formula) (v : Nat) (h : conflictAt f v=true) :
    Unsat f := by
  obtain ⟨ps,qs,hp,hq⟩ := conflict_routes f v h
  exact reach_pair_unsat f v ps qs hp hq

theorem noConflict_iff_sat (f : Formula) (hf : TwoCNF f) :
    NoConflict f ↔ ∃ x, FormulaSat f x := by
  constructor
  · intro h
    exact ⟨model f,model_satisfies f hf h⟩
  · intro hs v _ h
    exact conflict_unsat f v (by unfold conflictAt; rw [h.left,h.right]; rfl) hs

-- Standalone certificate return, deliberately no exhaustive fallback.
def discover (n : Nat) (f : Formula) : Option Proof :=
  match findConflict f (variables f) with
  | none => none
  | some v => checked n f (tryVar f (arcs f) v)

theorem discover_sound (n : Nat) (f : Formula) (p : Proof)
    (h : discover n f=some p) : boundCheck n f ⟨n,f,p⟩=true := by
  unfold discover at h
  cases e : findConflict f (variables f) with
  | none => rw [e] at h; cases h
  | some v =>
    rw [e] at h
    exact checked_sound n f _ p h

theorem discover_complete (n : Nat) (f : Formula) (hf : validFormula n f=true)
    (hw : TwoCNF f) (hu : Unsat f) : ∃ p, discover n f=some p := by
  unfold discover
  cases e : findConflict f (variables f) with
  | none => exact (hu ⟨model f,model_satisfies f hw (noConflict_of_none f e)⟩).elim
  | some v =>
    obtain ⟨ps,qs,hp,hq⟩ := conflict_routes f v (findConflict_some f _ v e)
    exact checked_tryVar_complete n v f ps qs hf hp hq

theorem discover_iff (n : Nat) (f : Formula) (hf : validFormula n f=true)
    (hw : TwoCNF f) : (∃ p, discover n f=some p) ↔ Unsat f := by
  constructor
  · intro h
    obtain ⟨p,hp⟩ := h
    exact ProctorUnifiedReplay.bound_sound n f _ (discover_sound n f p hp)
  · exact discover_complete n f hf hw

end ProctorTwoCNFModel

#print axioms ProctorTwoCNFModel.r_iff
#print axioms ProctorTwoCNFModel.walk_index
#print axioms ProctorTwoCNFModel.walk_reaches
#print axioms ProctorTwoCNFModel.r_refl
#print axioms ProctorTwoCNFModel.r_edge
#print axioms ProctorTwoCNFModel.walk_append
#print axioms ProctorTwoCNFModel.r_trans
#print axioms ProctorTwoCNFModel.row_dual
#print axioms ProctorTwoCNFModel.arc_dual
#print axioms ProctorTwoCNFModel.walk_dual
#print axioms ProctorTwoCNFModel.r_dual
#print axioms ProctorTwoCNFModel.row_in_arcs
#print axioms ProctorTwoCNFModel.vertex_mem
#print axioms ProctorTwoCNFModel.rank_mono
#print axioms ProctorTwoCNFModel.rank_eq_bits
#print axioms ProctorTwoCNFModel.score_edge
#print axioms ProctorTwoCNFModel.score_distinct
#print axioms ProctorTwoCNFModel.model_lt
#print axioms ProctorTwoCNFModel.model_edge
#print axioms ProctorTwoCNFModel.model_satisfies
#print axioms ProctorTwoCNFModel.findConflict_none
#print axioms ProctorTwoCNFModel.findConflict_some
#print axioms ProctorTwoCNFModel.noConflict_of_none
#print axioms ProctorTwoCNFModel.conflict_routes
#print axioms ProctorTwoCNFModel.conflict_unsat
#print axioms ProctorTwoCNFModel.noConflict_iff_sat
#print axioms ProctorTwoCNFModel.discover_sound
#print axioms ProctorTwoCNFModel.discover_complete
#print axioms ProctorTwoCNFModel.discover_iff
