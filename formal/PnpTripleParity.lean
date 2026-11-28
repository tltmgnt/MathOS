import Init

/-! Exact equivalence for every finite list of signed complementary triple
blocks. No claim about arbitrary 3-SAT or the Python implementation. -/
namespace PnpTripleParity

def mixed (x y z : Bool) : Bool :=
  (x || y || !z) && (x || !y || z) && (!x || y || z) &&
  (!x || !y || z) && (!x || y || !z) && (x || !y || !z)

def parity (x y s t : Bool) : Bool := (x != y) == (s != t)

theorem localReduction (x y z s t u : Bool) :
    mixed (x != s) (y != t) (z != u) =
      (parity x y s t && parity x z s u) := by
  cases x <;> cases y <;> cases z <;> cases s <;> cases t <;> cases u <;> decide

structure Block where
  x : Nat
  y : Nat
  z : Nat
  sx : Bool
  sy : Bool
  sz : Bool

def source (a : Nat → Bool) (b : Block) : Bool :=
  mixed (a b.x != b.sx) (a b.y != b.sy) (a b.z != b.sz)

def target (a : Nat → Bool) (b : Block) : Bool :=
  parity (a b.x) (a b.y) b.sx b.sy &&
  parity (a b.x) (a b.z) b.sx b.sz

def evaluate (p : Nat → Bool) (f : List Block) (r : (Nat → Bool) → Block → Bool) : Bool :=
  match f with
  | [] => true
  | b :: rest => r p b && evaluate p rest r

theorem allBlocks (a : Nat → Bool) (f : List Block) :
    evaluate a f source = evaluate a f target := by
  induction f with
  | nil => rfl
  | cons b rest ih =>
    change (source a b && evaluate a rest source) =
      (target a b && evaluate a rest target)
    have h : source a b = target a b :=
      localReduction (a b.x) (a b.y) (a b.z) b.sx b.sy b.sz
    rw [h, ih]

theorem satEquivalence (f : List Block) :
    (∃ a : Nat → Bool, evaluate a f source = true) ↔
    (∃ a : Nat → Bool, evaluate a f target = true) := by
  constructor
  · intro h
    rcases h with ⟨a, ha⟩
    exact ⟨a, (allBlocks a f).symm.trans ha⟩
  · intro h
    rcases h with ⟨a, ha⟩
    exact ⟨a, (allBlocks a f).trans ha⟩

/-- A signed family with one global seed has a model for ANY finite block list. -/
def seeded (s : Nat → Bool) (b : Block) : Block :=
  { b with sx := s b.x, sy := s b.y, sz := s b.z }

theorem seedBlock (s : Nat → Bool) (b : Block) : source s (seeded s b) = true := by
  change mixed (s b.x != s b.x) (s b.y != s b.y) (s b.z != s b.z) = true
  cases s b.x <;> cases s b.y <;> cases s b.z <;> decide

theorem seedFamily (s : Nat → Bool) (f : List Block) :
    evaluate s (f.map (seeded s)) source = true := by
  induction f with
  | nil => rfl
  | cons b rest ih =>
    change (source s (seeded s b) && evaluate s (rest.map (seeded s)) source) = true
    rw [seedBlock, ih] <;> rfl

#print axioms PnpTripleParity.localReduction
#print axioms PnpTripleParity.allBlocks
#print axioms PnpTripleParity.satEquivalence
#print axioms PnpTripleParity.seedFamily

end PnpTripleParity
