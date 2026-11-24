/-! F029: local Boolean renaming and the pair-constraint encoding.
Not a formal SCC algorithm, backdoor minimizer or complexity-class theorem. -/
namespace ProctorRenamableHorn

def orientedPositive (positive flip : Bool) : Bool :=
  positive != flip

def flipLiteral (positive flip : Bool) : Bool :=
  positive == flip

def pairClause (a b f g : Bool) : Bool :=
  flipLiteral a f || flipLiteral b g

def countPositive (a b c : Bool) : Nat :=
  (if a then 1 else 0) + (if b then 1 else 0) + (if c then 1 else 0)

def pairGuard (a b c : Bool) : Bool :=
  !(a && b) && !(a && c) && !(b && c)

theorem pair_encoding (a b f g : Bool) :
    pairClause a b f g = !(orientedPositive a f && orientedPositive b g) := by
  cases a <;> cases b <;> cases f <;> cases g <;> rfl

theorem guard_exact (a b c : Bool) :
    pairGuard a b c = decide (countPositive a b c ≤ 1) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem deletion_preserves_guard (a b c keepA keepB keepC : Bool) :
    pairGuard a b c = true →
    pairGuard (a && keepA) (b && keepB) (c && keepC) = true := by
  cases a <;> cases b <;> cases c <;>
    cases keepA <;> cases keepB <;> cases keepC <;> decide

theorem flip_involution (a f : Bool) :
    orientedPositive (orientedPositive a f) f = a := by
  cases a <;> cases f <;> rfl

end ProctorRenamableHorn

#print axioms ProctorRenamableHorn.pair_encoding
#print axioms ProctorRenamableHorn.guard_exact
#print axioms ProctorRenamableHorn.deletion_preserves_guard
#print axioms ProctorRenamableHorn.flip_involution
