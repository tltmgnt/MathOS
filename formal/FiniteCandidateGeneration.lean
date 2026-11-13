/-!
# Stage 3b: finite candidate generation for AND/OR proof-route formulas

This is a structurally recursive (hence terminating) reference recurrence
for finite AND/OR formulas. The generated predicate-sets represent the open
obligations sufficient to satisfy a formula. AND combines candidates by union;
OR appends alternatives; assumed leaves need no obligations.

Theorems prove soundness and completeness of raw candidate generation,
minimality of the pruned output, and coverage of every minimal solution up to
mutual inclusion. This models an *unfolded* finite acyclic route formula,
not an indexed, sharing-aware DAG or the Python implementation.
-/
import BooleanRoutes
import FiniteCompletionPruning

namespace MathOS

universe u

def unionCandidates {α : Type u} (a b : α → Prop) : α → Prop :=
  fun x => a x ∨ b x

def candidateSets {α : Type u} : RouteFormula α → List (α → Prop)
  | .assumed => [fun _ => False]
  | .openLeaf x => [fun y => y = x]
  | .andNode left right =>
      (candidateSets left).flatMap (fun a =>
        (candidateSets right).map (fun b => unionCandidates a b))
  | .orNode left right => candidateSets left ++ candidateSets right

theorem eval_iff_candidate {α : Type u}
    (f : RouteFormula α) (accepted : α → Prop) :
    f.eval accepted ↔
      ∃ c, c ∈ candidateSets f ∧ SetIncluded c accepted := by
  induction f with
  | assumed =>
      constructor
      · intro _
        refine ⟨(fun _ => False), ?_, ?_⟩
        · simp [candidateSets]
        · intro x hx
          exact False.elim hx
      · intro _
        trivial
  | openLeaf x =>
      constructor
      · intro hx
        refine ⟨(fun y => y = x), ?_, ?_⟩
        · simp [candidateSets]
        · intro y hy
          cases hy
          exact hx
      · intro h
        cases h with
        | intro c h =>
          cases h with
          | intro hc hca =>
            have heq : c = (fun y => y = x) := by
              simpa [candidateSets] using hc
            change accepted x
            exact hca x (by simp [heq])
  | andNode left right ihLeft ihRight =>
      constructor
      · intro h
        change left.eval accepted ∧ right.eval accepted at h
        cases ihLeft.mp h.left with
        | intro cl hclpair =>
          cases hclpair with
          | intro hcl hla =>
            cases ihRight.mp h.right with
            | intro cr hcrpair =>
              cases hcrpair with
              | intro hcr hra =>
                refine ⟨unionCandidates cl cr, ?_, ?_⟩
                · change unionCandidates cl cr ∈
                    (candidateSets left).flatMap (fun a =>
                      (candidateSets right).map (fun b => unionCandidates a b))
                  apply List.mem_flatMap.mpr
                  refine ⟨cl, hcl, ?_⟩
                  apply List.mem_map.mpr
                  exact ⟨cr, hcr, rfl⟩
                · intro x hx
                  change cl x ∨ cr x at hx
                  cases hx with
                  | inl hl => exact hla x hl
                  | inr hr => exact hra x hr
      · intro h
        cases h with
        | intro c h =>
          cases h with
          | intro hc hca =>
            change c ∈ (candidateSets left).flatMap (fun a =>
              (candidateSets right).map (fun b => unionCandidates a b)) at hc
            have hp := List.mem_flatMap.mp hc
            cases hp with
            | intro cl hclpair =>
              cases hclpair with
              | intro hcl hrow =>
                have hr := List.mem_map.mp hrow
                cases hr with
                | intro cr hcrpair =>
                  cases hcrpair with
                  | intro hcr hEq =>
                    have hUnion : SetIncluded (unionCandidates cl cr) accepted := by
                      rw [hEq]
                      exact hca
                    change left.eval accepted ∧ right.eval accepted
                    constructor
                    · apply ihLeft.mpr
                      exact ⟨cl, hcl, by
                        intro x hx
                        exact hUnion x (Or.inl hx)⟩
                    · apply ihRight.mpr
                      exact ⟨cr, hcr, by
                        intro x hx
                        exact hUnion x (Or.inr hx)⟩
  | orNode left right ihLeft ihRight =>
      constructor
      · intro h
        change left.eval accepted ∨ right.eval accepted at h
        cases h with
        | inl hl =>
          cases ihLeft.mp hl with
          | intro c hcPair =>
            cases hcPair with
            | intro hc hca =>
              refine ⟨c, ?_, hca⟩
              change c ∈ candidateSets left ++ candidateSets right
              exact List.mem_append.mpr (Or.inl hc)
        | inr hr =>
          cases ihRight.mp hr with
          | intro c hcPair =>
            cases hcPair with
            | intro hc hca =>
              refine ⟨c, ?_, hca⟩
              change c ∈ candidateSets left ++ candidateSets right
              exact List.mem_append.mpr (Or.inr hc)
      · intro h
        cases h with
        | intro c hcPair =>
          cases hcPair with
          | intro hc hca =>
            change c ∈ candidateSets left ++ candidateSets right at hc
            have ha := List.mem_append.mp hc
            change left.eval accepted ∨ right.eval accepted
            cases ha with
            | inl hl => exact Or.inl (ihLeft.mpr ⟨c, hl, hca⟩)
            | inr hr => exact Or.inr (ihRight.mpr ⟨c, hr, hca⟩)

theorem candidate_self_eval {α : Type u}
    (f : RouteFormula α) (c : α → Prop)
    (hc : c ∈ candidateSets f) : f.eval c := by
  apply (eval_iff_candidate f c).mpr
  exact ⟨c, hc, by intro x hx; exact hx⟩

noncomputable def minimalCandidateSets {α : Type u}
    (f : RouteFormula α) : List (α → Prop) :=
  pruneCandidates (candidateSets f)

theorem minimalCandidateSets_sound {α : Type u}
    (f : RouteFormula α) (c : α → Prop)
    (hc : c ∈ minimalCandidateSets f) : MinimalCompletion f c := by
  have hraw : c ∈ candidateSets f :=
    pruneCandidates_sound (candidateSets f) c hc
  constructor
  · exact candidate_self_eval f c hraw
  · intro other heval hsub
    cases (eval_iff_candidate f other).mp heval with
    | intro d h =>
      cases h with
      | intro hd hdc =>
        have hdsub : SetIncluded d c := by
          intro x hx
          exact hsub x (hdc x hx)
        have hcsub : SetIncluded c d := by
          apply Classical.byContradiction
          intro hncd
          exact (pruneCandidates_minimal (candidateSets f) c hc)
            ⟨d, hd, ⟨hdsub, hncd⟩⟩
        intro x hx
        exact hdc x (hcsub x hx)

theorem minimalCandidateSets_complete {α : Type u}
    (f : RouteFormula α) (accepted : α → Prop)
    (hmin : MinimalCompletion f accepted) :
    ∃ c, c ∈ minimalCandidateSets f ∧
      SetIncluded c accepted ∧ SetIncluded accepted c := by
  cases (eval_iff_candidate f accepted).mp hmin.left with
  | intro c h =>
    cases h with
    | intro hc hca =>
      have hac : SetIncluded accepted c :=
        hmin.right c (candidate_self_eval f c hc) hca
      have undominated :
          ¬ ∃ d, d ∈ candidateSets f ∧ StrictlyIncluded d c := by
        intro hbad
        cases hbad with
        | intro d h =>
          cases h with
          | intro hd hstrict =>
            have hdaccepted : Included d accepted := by
              intro x hx
              exact hca x (hstrict.left x hx)
            have hacd : Included accepted d :=
              hmin.right d (candidate_self_eval f d hd) hdaccepted
            apply hstrict.right
            intro x hx
            exact hacd x (hca x hx)
      exact ⟨c, pruneCandidates_exact (candidateSets f) c hc undominated,
        hca, hac⟩

theorem minimalCandidateSets_antichain {α : Type u}
    (f : RouteFormula α) (a b : α → Prop)
    (ha : a ∈ minimalCandidateSets f)
    (hb : b ∈ minimalCandidateSets f)
    (hab : SetIncluded a b) : SetIncluded b a :=
  pruneCandidates_antichain (candidateSets f) a b ha hb hab

end MathOS
