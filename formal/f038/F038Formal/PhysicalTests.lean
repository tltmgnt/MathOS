import F038Formal.Physical

namespace MathOS.F038.Physical.Tests
open MathOS.F038.Physical

-- A redundant four-state original; states 0 and 1 have equal observable
-- actions and both go to halt. State 2 is unmapped and unreachable.
def original : Machine 4 :=
  ⟨0,3,fun s x => if s.val = 2 then ⟨2,x,.left⟩
    else if s.val = 3 then ⟨3,x,.stay⟩ else ⟨3,1,.right⟩⟩

def quotient : Machine 2 :=
  ⟨0,1,fun s x => if s.val = 1 then ⟨1,x,.stay⟩ else ⟨1,1,.right⟩⟩

def mapping (s : Fin 4) : Option (Fin 2) :=
  if s.val = 2 then none else if s.val = 3 then some 1 else some 0

def blank : Int → Symbol := fun _ => 2

example : quotientCheck original quotient mapping = true := by decide
example : quotientCheck original quotient (fun _ => none) = false := by decide
example : quotientCheck original quotient (fun _ => some 0) = false := by decide
example : quotientCheck original { quotient with action := fun _ x => ⟨1,x,.left⟩ } mapping = false := by decide
example : (run original 0 (initialConfig original 0 blank)).2 = 0 := by decide
example : (run original 1 (initialConfig original 0 blank)).2 = 1 := by decide
example : (run original 10 (initialConfig original 0 blank)).2 = 1 := by decide
example : (run quotient 10 (initialConfig quotient 0 blank)).1.head = 1 := by decide
example : (run quotient 10 (initialConfig quotient 0 blank)).1.tape 0 = 1 := by decide
example : (run quotient 10 (initialConfig quotient 0 blank)).1.tape 1 = 2 := by decide

theorem fixture_simulation (fuel : Nat) (head : Int) (tape : Int → Symbol) :
    let r := run original fuel (initialConfig original head tape)
    let s := run quotient fuel (initialConfig quotient head tape)
    related mapping r.1 s.1 ∧ r.2 = s.2 ∧
      (r.1.state = original.halt ↔ s.1.state = quotient.halt) :=
  checked_simulation original quotient mapping (by decide) fuel head tape

#print axioms fixture_simulation
end MathOS.F038.Physical.Tests
