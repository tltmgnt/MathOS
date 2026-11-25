/-! F035: affine GF(2) constraint systems are closed under ternary XOR,
even after projecting arbitrary auxiliary variables. General clauses
violate this closure. A degree-three polynomial representation is
exact for 3-CNF, but solving nonlinear equations is a separate problem. -/
namespace ProctorAffineBarrier
open ProctorHallDeficiency
open ProctorXorReplay (bx evalSupport)
open ProctorGeneralBranching (formula_cons)

def mix (x y z : Assignment) : Assignment :=
  fun v => bx (x v) (bx (y v) (z v))

theorem bx_shuffle (a b c d e f : Bool) :
    bx (bx a (bx b c)) (bx d (bx e f)) =
      bx (bx a d) (bx (bx b e) (bx c f)) := by
  cases a <;> cases b <;> cases c <;> cases d <;> cases e <;> cases f <;> rfl

theorem bx_triple (b : Bool) : bx b (bx b b)=b := by
  cases b <;> rfl

theorem eval_mix (x y z : Assignment) (vs : List Nat) :
    evalSupport (mix x y z) vs =
      bx (evalSupport x vs) (bx (evalSupport y vs) (evalSupport z vs)) := by
  induction vs with
  | nil => rfl
  | cons v vs ih =>
    change bx (bx (x v) (bx (y v) (z v))) (evalSupport (mix x y z) vs)=
      bx (bx (x v) (evalSupport x vs))
        (bx (bx (y v) (evalSupport y vs)) (bx (z v) (evalSupport z vs)))
    rw [ih]
    exact bx_shuffle _ _ _ _ _ _

structure Equation where
  support : List Nat
  rhs : Bool

def Satisfies (e : Equation) (x : Assignment) : Prop :=
  evalSupport x e.support=e.rhs

def SystemSat (es : List Equation) (x : Assignment) : Prop :=
  ∀ e∈es, Satisfies e x

theorem equation_closed (e : Equation) (x y z : Assignment)
    (hx : Satisfies e x) (hy : Satisfies e y) (hz : Satisfies e z) :
    Satisfies e (mix x y z) := by
  unfold Satisfies at *
  rw [eval_mix,hx,hy,hz,bx_triple]

theorem system_closed (es : List Equation) (x y z : Assignment)
    (hx : SystemSat es x) (hy : SystemSat es y) (hz : SystemSat es z) :
    SystemSat es (mix x y z) :=
  fun e he => equation_closed e x y z (hx e he) (hy e he) (hz e he)

-- Projection can hide arbitrarily many auxiliary coordinates.
-- No finite bound on the extension assignment is assumed.
def Projected (es : List Equation) (visible : List Nat) (x : Assignment) : Prop :=
  ∃ y : Assignment, SystemSat es y ∧ ∀ v∈visible, y v=x v

theorem projected_closed (es : List Equation) (visible : List Nat)
    (x y z : Assignment) (hx : Projected es visible x)
    (hy : Projected es visible y) (hz : Projected es visible z) :
    Projected es visible (mix x y z) := by
  obtain ⟨a,ha,ea⟩ := hx
  obtain ⟨b,hb,eb⟩ := hy
  obtain ⟨c,hc,ec⟩ := hz
  refine ⟨mix a b c,system_closed es a b c ha hb hc,?_⟩
  intro v hv
  unfold mix
  rw [ea v hv,eb v hv,ec v hv]

def positiveThree : Clause := [(1,true),(2,true),(3,true)]
def one : Assignment := fun v => v==1
def two : Assignment := fun v => v==2
def both : Assignment := fun v => v==1 || v==2

theorem one_sat : ClauseSat positiveThree one :=
  ⟨(1,true),List.Mem.head _,rfl⟩

theorem two_sat : ClauseSat positiveThree two :=
  ⟨(2,true),List.Mem.tail _ (List.Mem.head _),rfl⟩

theorem both_sat : ClauseSat positiveThree both :=
  ⟨(1,true),List.Mem.head _,rfl⟩

theorem mixed_false : ¬ ClauseSat positiveThree (mix one two both) := by
  intro h
  obtain ⟨l,hl,he⟩ := h
  change l∈[(1,true),(2,true),(3,true)] at hl
  cases hl with
  | head => exact Bool.noConfusion he
  | tail _ hm =>
    cases hm with
    | head => exact Bool.noConfusion he
    | tail _ hn =>
      cases hn with
      | head => exact Bool.noConfusion he
      | tail _ hz => cases hz

theorem no_affine_projection (es : List Equation) (visible : List Nat)
    (h : ∀ x : Assignment, Projected es visible x ↔ ClauseSat positiveThree x) : False := by
  have a := (h one).2 one_sat
  have b := (h two).2 two_sat
  have c := (h both).2 both_sat
  exact mixed_false ((h _).1 (projected_closed es visible one two both a b c))

-- Boolean polynomial factor for a false literal: x_v+1 for a
-- positive literal, x_v for a negative literal, over GF(2).
def falseFactor (x : Assignment) (l : Literal) : Bool :=
  bx (x l.1) l.2

def falseProduct (x : Assignment) : Clause → Bool
  | [] => true
  | l::ls => falseFactor x l && falseProduct x ls

theorem factor_zero (x : Assignment) (l : Literal) :
    falseFactor x l=false ↔ x l.1=l.2 := by
  cases l with
  | mk v b =>
    unfold falseFactor
    change bx (x v) b=false ↔ x v=b
    cases hv : x v <;> cases b <;> exact ⟨fun h => by cases h; rfl,fun h => by cases h; rfl⟩

theorem product_zero (x : Assignment) (c : Clause) :
    falseProduct x c=false ↔ ClauseSat c x := by
  induction c with
  | nil =>
    constructor
    · intro h
      cases h
    · intro h
      obtain ⟨l,hl,_⟩ := h
      cases hl
  | cons l ls ih =>
    constructor
    · intro h
      change (falseFactor x l && falseProduct x ls)=false at h
      cases e : falseFactor x l with
      | false => exact ⟨l,List.Mem.head _,(factor_zero x l).1 e⟩
      | true =>
        rw [e] at h
        obtain ⟨a,ha,he⟩ := ih.1 h
        exact ⟨a,List.Mem.tail _ ha,he⟩
    · intro h
      obtain ⟨a,ha,he⟩ := h
      change (falseFactor x l && falseProduct x ls)=false
      cases ha with
      | head =>
        rw [(factor_zero x l).2 he]
        rfl
      | tail _ hm =>
        have ht := ih.2 ⟨a,hm,he⟩
        rw [ht]
        cases falseFactor x l <;> rfl

def PolynomialSat (f : Formula) (x : Assignment) : Prop :=
  ∀ c∈f,falseProduct x c=false

theorem polynomial_correct (f : Formula) (x : Assignment) :
    PolynomialSat f x ↔ FormulaSat f x :=
  ⟨fun h c hc => (product_zero x c).1 (h c hc),
    fun h c hc => (product_zero x c).2 (h c hc)⟩

-- A syntactic degree bound for the factored polynomial encoding.
def degree (c : Clause) : Nat := c.length

theorem width_degree (f : Formula) (h : ∀ c∈f,c.length≤3) :
    ∀ c∈f,degree c≤3 := h

end ProctorAffineBarrier

#print axioms ProctorAffineBarrier.bx_shuffle
#print axioms ProctorAffineBarrier.bx_triple
#print axioms ProctorAffineBarrier.eval_mix
#print axioms ProctorAffineBarrier.equation_closed
#print axioms ProctorAffineBarrier.system_closed
#print axioms ProctorAffineBarrier.projected_closed
#print axioms ProctorAffineBarrier.one_sat
#print axioms ProctorAffineBarrier.two_sat
#print axioms ProctorAffineBarrier.both_sat
#print axioms ProctorAffineBarrier.mixed_false
#print axioms ProctorAffineBarrier.no_affine_projection
#print axioms ProctorAffineBarrier.factor_zero
#print axioms ProctorAffineBarrier.product_zero
#print axioms ProctorAffineBarrier.polynomial_correct
#print axioms ProctorAffineBarrier.width_degree
