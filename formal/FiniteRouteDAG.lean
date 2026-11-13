import BooleanRoutes
import FiniteCompletionPruning
import FiniteCandidateGeneration

/-!
# Stage 3c: topologically indexed finite AND/OR dependency DAGs

A `RouteDag α n` is built in topological order. Each added node can
reference earlier nodes with `Fin n` pointers. Reusing pointers represents
shared subgraphs without duplicating stored nodes; cycles and forward edges
are unrepresentable in this type.

The interpreter evaluates nodes forward using those pointers. A separate
unfolding translates each node to Stage 2's finite `RouteFormula` syntax.
The compiler-checked refinement lemmas relate the indexed interpreter and
raw candidate recurrence to the unfolded semantics.

Limit: each derived node is binary AND or binary OR. This is not yet the
variable-arity, input-validated, memoized Python analyzer, nor a proof of
the truth of authored mathematical dependency edges.
-/
namespace MathOS

universe u

inductive RouteDagNode (α : Type u) (n : Nat) where
  | assumed : RouteDagNode α n
  | openLeaf : α → RouteDagNode α n
  | andNode : Fin n → Fin n → RouteDagNode α n
  | orNode : Fin n → Fin n → RouteDagNode α n

inductive RouteDag (α : Type u) : Nat → Type u where
  | nil : RouteDag α 0
  | snoc {n : Nat} (previous : RouteDag α n)
      (node : RouteDagNode α n) : RouteDag α (n + 1)

def RouteDagNode.toFormula {α : Type u} {n : Nat}
    (node : RouteDagNode α n) (prior : Fin n → RouteFormula α) :
    RouteFormula α :=
  match node with
  | .assumed => .assumed
  | .openLeaf x => .openLeaf x
  | .andNode left right => .andNode (prior left) (prior right)
  | .orNode left right => .orNode (prior left) (prior right)

def RouteDagNode.evaluate {α : Type u} {n : Nat}
    (node : RouteDagNode α n) (prior : Fin n → Prop)
    (accepted : α → Prop) : Prop :=
  match node with
  | .assumed => True
  | .openLeaf x => accepted x
  | .andNode left right => prior left ∧ prior right
  | .orNode left right => prior left ∨ prior right

def RouteDagNode.rawCandidates {α : Type u} {n : Nat}
    (node : RouteDagNode α n)
    (prior : Fin n → List (α → Prop)) : List (α → Prop) :=
  match node with
  | .assumed => [fun _ => False]
  | .openLeaf x => [fun y => y = x]
  | .andNode left right =>
      (prior left).flatMap (fun a =>
        (prior right).map (fun b => unionCandidates a b))
  | .orNode left right => prior left ++ prior right

/-- The formula represented at each DAG node (unfolding shared edges). -/
def RouteDag.unfold {α : Type u} {n : Nat} :
    RouteDag α n → Fin n → RouteFormula α
  | .nil => fun i => Fin.elim0 i
  | .snoc previous node =>
      let prior := RouteDag.unfold previous
      Fin.lastCases (node.toFormula prior) prior

/-- Direct, topologically ordered DAG interpreter. -/
def RouteDag.evaluate {α : Type u} {n : Nat}
    (graph : RouteDag α n) (accepted : α → Prop) : Fin n → Prop :=
  match graph with
  | .nil => fun i => Fin.elim0 i
  | .snoc previous node =>
      let prior := previous.evaluate accepted
      Fin.lastCases (node.evaluate prior accepted) prior

/-- Topologically ordered raw candidate-set generator. -/
def RouteDag.rawCandidates {α : Type u} {n : Nat}
    (graph : RouteDag α n) : Fin n → List (α → Prop) :=
  match graph with
  | .nil => fun i => Fin.elim0 i
  | .snoc previous node =>
      let prior := previous.rawCandidates
      Fin.lastCases (node.rawCandidates prior) prior

theorem RouteDagNode.evaluate_iff_formula {α : Type u} {n : Nat}
    (node : RouteDagNode α n) (values : Fin n → Prop)
    (formulas : Fin n → RouteFormula α) (accepted : α → Prop)
    (h : ∀ i, values i ↔ (formulas i).eval accepted) :
    node.evaluate values accepted ↔
      (node.toFormula formulas).eval accepted := by
  cases node with
  | assumed =>
      simp [RouteDagNode.evaluate, RouteDagNode.toFormula, RouteFormula.eval]
  | openLeaf x =>
      simp [RouteDagNode.evaluate, RouteDagNode.toFormula, RouteFormula.eval]
  | andNode left right =>
      change (values left ∧ values right) ↔
        ((formulas left).eval accepted ∧ (formulas right).eval accepted)
      exact and_congr (h left) (h right)
  | orNode left right =>
      change (values left ∨ values right) ↔
        ((formulas left).eval accepted ∨ (formulas right).eval accepted)
      exact or_congr (h left) (h right)

theorem RouteDagNode.candidates_eq_formula {α : Type u} {n : Nat}
    (node : RouteDagNode α n)
    (values : Fin n → List (α → Prop))
    (formulas : Fin n → RouteFormula α)
    (h : ∀ i, values i = candidateSets (formulas i)) :
    node.rawCandidates values = candidateSets (node.toFormula formulas) := by
  cases node with
  | assumed =>
      rfl
  | openLeaf x =>
      rfl
  | andNode left right =>
      simp [RouteDagNode.rawCandidates, RouteDagNode.toFormula,
        candidateSets, h left, h right]
  | orNode left right =>
      simp [RouteDagNode.rawCandidates, RouteDagNode.toFormula,
        candidateSets, h left, h right]

theorem RouteDag.evaluate_iff_unfold {α : Type u} {n : Nat}
    (graph : RouteDag α n) (accepted : α → Prop) :
    ∀ i, graph.evaluate accepted i ↔ (graph.unfold i).eval accepted := by
  induction graph with
  | nil =>
      intro i
      exact Fin.elim0 i
  | @snoc n previous node ih =>
      intro i
      refine Fin.lastCases ?_ (fun j => ?_) i
      · simpa [RouteDag.evaluate, RouteDag.unfold] using
          (RouteDagNode.evaluate_iff_formula node
            (previous.evaluate accepted) previous.unfold accepted ih)
      · simpa [RouteDag.evaluate, RouteDag.unfold] using (ih j)

theorem RouteDag.rawCandidates_eq_unfold {α : Type u} {n : Nat}
    (graph : RouteDag α n) :
    ∀ i, graph.rawCandidates i = candidateSets (graph.unfold i) := by
  induction graph with
  | nil =>
      intro i
      exact Fin.elim0 i
  | @snoc n previous node ih =>
      intro i
      refine Fin.lastCases ?_ (fun j => ?_) i
      · simpa [RouteDag.rawCandidates, RouteDag.unfold] using
          (RouteDagNode.candidates_eq_formula node
            previous.rawCandidates previous.unfold ih)
      · simpa [RouteDag.rawCandidates, RouteDag.unfold] using (ih j)

theorem RouteDag.evaluate_iff_candidate {α : Type u} {n : Nat}
    (graph : RouteDag α n) (target : Fin n) (accepted : α → Prop) :
    graph.evaluate accepted target ↔
      ∃ c, c ∈ graph.rawCandidates target ∧ SetIncluded c accepted := by
  have h := eval_iff_candidate (graph.unfold target) accepted
  simpa [graph.rawCandidates_eq_unfold target] using
    (Iff.trans (graph.evaluate_iff_unfold accepted target) h)

noncomputable def RouteDag.minimalCandidates {α : Type u} {n : Nat}
    (graph : RouteDag α n) (target : Fin n) : List (α → Prop) :=
  pruneCandidates (graph.rawCandidates target)

theorem RouteDag.minimalCandidates_sound {α : Type u} {n : Nat}
    (graph : RouteDag α n) (target : Fin n) (c : α → Prop)
    (hc : c ∈ graph.minimalCandidates target) :
    MinimalCompletion (graph.unfold target) c := by
  have h : c ∈ minimalCandidateSets (graph.unfold target) := by
    simpa [RouteDag.minimalCandidates, minimalCandidateSets,
      graph.rawCandidates_eq_unfold target] using hc
  exact minimalCandidateSets_sound (graph.unfold target) c h

theorem RouteDag.minimalCandidates_complete {α : Type u} {n : Nat}
    (graph : RouteDag α n) (target : Fin n) (accepted : α → Prop)
    (h : MinimalCompletion (graph.unfold target) accepted) :
    ∃ c, c ∈ graph.minimalCandidates target ∧
      SetIncluded c accepted ∧ SetIncluded accepted c := by
  have result := minimalCandidateSets_complete (graph.unfold target) accepted h
  simpa [RouteDag.minimalCandidates, minimalCandidateSets,
    graph.rawCandidates_eq_unfold target] using result

theorem RouteDag.minimalCandidates_antichain {α : Type u} {n : Nat}
    (graph : RouteDag α n) (target : Fin n) (a b : α → Prop)
    (ha : a ∈ graph.minimalCandidates target)
    (hb : b ∈ graph.minimalCandidates target)
    (hab : SetIncluded a b) : SetIncluded b a := by
  exact pruneCandidates_antichain (graph.rawCandidates target) a b ha hb hab

end MathOS
