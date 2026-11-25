/-! F034 candidate: lift verified token width and exact parser
consumption to all explicit numeric fields in a decoded certificate.
Does not bound values constructed later by checker arithmetic.
Independent of pending reference and checker-resource candidates. -/
namespace ProctorDecodedWidth
open ProctorHallDeficiency
open ProctorDataParser
open ProctorWireRoundtrip (encNat encLiteral encItems encList encClause encFormula encExpected)
open ProctorEnvelopeRoundtrip (encRef encGroup encCapacity encBlock encStep encBatch
  encTerminal encProof encEnvelope)
open ProctorExecutableReplay (Step Batch)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorUnifiedReplay (Proof Terminal Envelope)
open ProctorCheckedBinaryScanner (cap cap_pow)

def AllFit (ts : List Nat) : Prop := ∀ n ∈ ts, n<cap 512
def ClauseFit (c : Clause) : Prop := ∀ l ∈ c, l.1<cap 512
def FormulaFit (f : Formula) : Prop := ∀ c ∈ f, ClauseFit c
def RefFit (r : RefRow) : Prop := r.index<cap 512 ∧ ClauseFit r.row
def GroupFit (g : ProctorCapacityDeficiency.Group) : Prop :=
  ClauseFit g.literals ∧ g.cap<cap 512
def CapacityFit (c : Certificate) : Prop :=
  (∀ r ∈ c.demands, RefFit r) ∧ (∀ g ∈ c.groups, GroupFit g) ∧
    (∀ r ∈ c.conflicts, RefFit r)
def BlockFit (b : ProctorXorReplay.Block) : Prop :=
  AllFit b.support ∧ (∀ r ∈ b.refs, RefFit r)
def StepFit (s : Step) : Prop :=
  s.left<cap 512 ∧ s.right<cap 512 ∧ s.pivot<cap 512 ∧ ClauseFit s.tail
def TerminalFit : Terminal → Prop
  | .empty => True
  | .capacity c => CapacityFit c
  | .xor bs => ∀ b ∈ bs, BlockFit b
def ProofFit (p : Proof) : Prop :=
  (∀ b ∈ p.batches, ∀ s ∈ b, StepFit s) ∧ TerminalFit p.terminal
def EnvelopeFit (e : Envelope) : Prop :=
  e.variableBound<cap 512 ∧ FormulaFit e.original ∧ ProofFit e.proof

private theorem head_fit (n : Nat) (ts : List Nat) (h : AllFit (n::ts)) :
    n<cap 512 := h n (List.Mem.head _)

private theorem tail_fit (n : Nat) (ts : List Nat) (h : AllFit (n::ts)) :
    AllFit ts := fun a ha => h a (List.Mem.tail _ ha)

theorem append_left (a b : List Nat) (h : AllFit (a++b)) : AllFit a := by
  induction a with
  | nil => intro n hm; cases hm
  | cons x xs ih =>
    intro n hm
    cases hm with
    | head => exact h x (List.Mem.head _)
    | tail _ hm => exact ih (tail_fit x (xs++b) h) n hm

theorem append_right (a b : List Nat) (h : AllFit (a++b)) : AllFit b := by
  induction a with
  | nil => exact h
  | cons x xs ih => exact ih (tail_fit x (xs++b) h)

theorem items_fit {α : Type} (enc : α → List Nat) (xs : List α)
    (h : AllFit (encItems enc xs)) : ∀ a ∈ xs, AllFit (enc a) := by
  induction xs with
  | nil => intro a ha; cases ha
  | cons x xs ih =>
    intro a ha
    cases ha with
    | head => exact append_left (enc x) (encItems enc xs) h
    | tail _ hm => exact ih (append_right (enc x) (encItems enc xs) h) a hm

theorem list_fit {α : Type} (enc : α → List Nat) (xs : List α)
    (h : AllFit (encList enc xs)) : ∀ a ∈ xs, AllFit (enc a) :=
  items_fit enc xs (tail_fit xs.length (encItems enc xs) h)

theorem literal_fit (l : Literal) (h : AllFit (encLiteral l)) :
    l.1<cap 512 := h l.1 (List.Mem.head _)

theorem clause_fit (c : Clause) (h : AllFit (encClause c)) : ClauseFit c :=
  fun l hl => literal_fit l (list_fit encLiteral c h l hl)

theorem formula_fit (f : Formula) (h : AllFit (encFormula f)) : FormulaFit f :=
  fun c hc => clause_fit c (list_fit encClause f h c hc)

theorem ref_fit (r : RefRow) (h : AllFit (encRef r)) : RefFit r :=
  ⟨head_fit r.index (encClause r.row) h,
    clause_fit r.row (tail_fit r.index (encClause r.row) h)⟩

theorem group_fit (g : ProctorCapacityDeficiency.Group) (h : AllFit (encGroup g)) :
    GroupFit g :=
  ⟨clause_fit g.literals (append_left (encClause g.literals) (encNat g.cap) h),
    head_fit g.cap [] (append_right (encClause g.literals) (encNat g.cap) h)⟩

theorem capacity_fit (c : Certificate) (h : AllFit (encCapacity c)) : CapacityFit c := by
  change AllFit (encList encRef c.demands ++
    (encList encGroup c.groups ++ encList encRef c.conflicts)) at h
  have hd := append_left _ _ h
  have hr := append_right _ _ h
  have hg := append_left _ _ hr
  have hc := append_right _ _ hr
  exact ⟨fun r hm => ref_fit r (list_fit encRef c.demands hd r hm),
    fun g hm => group_fit g (list_fit encGroup c.groups hg g hm),
    fun r hm => ref_fit r (list_fit encRef c.conflicts hc r hm)⟩

theorem block_fit (b : ProctorXorReplay.Block) (h : AllFit (encBlock b)) : BlockFit b := by
  change AllFit (encList encNat b.support ++
    (ProctorWireRoundtrip.encBool b.rhs ++ encList encRef b.refs)) at h
  have hv := append_left _ _ h
  have hr := append_right _ _ (append_right _ _ h)
  exact ⟨fun n hm => head_fit n [] (list_fit encNat b.support hv n hm),
    fun r hm => ref_fit r (list_fit encRef b.refs hr r hm)⟩

theorem step_fit (s : Step) (h : AllFit (encStep s)) : StepFit s := by
  change AllFit (s.left::s.right::s.pivot::encClause s.tail) at h
  have hr := tail_fit _ _ h
  have hp := tail_fit _ _ hr
  exact ⟨head_fit _ _ h,head_fit _ _ hr,head_fit _ _ hp,
    clause_fit s.tail (tail_fit _ _ hp)⟩

theorem terminal_fit (t : Terminal) (h : AllFit (encTerminal t)) : TerminalFit t := by
  cases t with
  | empty => exact True.intro
  | capacity c => exact capacity_fit c (tail_fit 1 (encCapacity c) h)
  | xor bs =>
    intro b hb
    exact block_fit b (list_fit encBlock bs (tail_fit 2 (encList encBlock bs) h) b hb)

theorem proof_fit (p : Proof) (h : AllFit (encProof p)) : ProofFit p := by
  change AllFit (encList encBatch p.batches ++
    (ProctorWireRoundtrip.encBool p.augmented ++ encTerminal p.terminal)) at h
  have hb := append_left _ _ h
  have ht := append_right _ _ (append_right _ _ h)
  exact ⟨fun b hm s hs => step_fit s
    (list_fit encStep b (list_fit encBatch p.batches hb b hm) s hs),
    terminal_fit p.terminal ht⟩

theorem envelope_fit (e : Envelope) (h : AllFit (encEnvelope e)) : EnvelopeFit e := by
  change AllFit (3402::e.variableBound::(encFormula e.original ++ encProof e.proof)) at h
  have hn := tail_fit _ _ h
  have hr := tail_fit _ _ hn
  exact ⟨head_fit _ _ hn,formula_fit e.original (append_left _ _ hr),
    proof_fit e.proof (append_right _ _ hr)⟩

theorem token_fit (bytes ts : List Nat) (h : tokenize bytes=some ts) : AllFit ts := by
  have eq : ProctorDecimalBitWidth.ceiling=cap 512 :=
    ProctorDecimalBitWidth.ceiling_bits.trans (cap_pow 512).symm
  intro n hm
  have hn := ProctorDecimalBitWidth.token_width bytes ts h n hm
  rw [eq] at hn
  exact hn

theorem decoded_expected (bytes : List Nat) (n : Nat) (f : Formula)
    (h : decodeExpected bytes=some (n,f)) : n<cap 512 ∧ FormulaFit f := by
  have ht := token_fit bytes (encExpected n f)
    (ProctorParserConsumption.expected_bytes bytes n f h).left
  have hr := tail_fit 3401 (n::encFormula f) ht
  exact ⟨head_fit n (encFormula f) hr,formula_fit f (tail_fit n (encFormula f) hr)⟩

theorem decoded_envelope (bytes : List Nat) (e : Envelope)
    (h : decodeEnvelope bytes=some e) : EnvelopeFit e :=
  envelope_fit e (token_fit bytes (encEnvelope e)
    (ProctorParserConsumption.envelope_bytes bytes e h).left)

theorem fuel_free_expected (bytes : List Nat) (n : Nat) (f : Formula)
    (h : ProctorFuelFreeDecoder.decodeExpected bytes=some (n,f)) :
    n<cap 512 ∧ FormulaFit f := by
  rw [ProctorFuelFreeDecoder.expected_bytes_refines] at h
  exact decoded_expected bytes n f h

theorem fuel_free_envelope (bytes : List Nat) (e : Envelope)
    (h : ProctorFuelFreeDecoder.decodeEnvelope bytes=some e) : EnvelopeFit e := by
  rw [ProctorFuelFreeDecoder.envelope_bytes_refines] at h
  exact decoded_envelope bytes e h

end ProctorDecodedWidth

#print axioms ProctorDecodedWidth.append_left
#print axioms ProctorDecodedWidth.append_right
#print axioms ProctorDecodedWidth.items_fit
#print axioms ProctorDecodedWidth.list_fit
#print axioms ProctorDecodedWidth.literal_fit
#print axioms ProctorDecodedWidth.clause_fit
#print axioms ProctorDecodedWidth.formula_fit
#print axioms ProctorDecodedWidth.ref_fit
#print axioms ProctorDecodedWidth.group_fit
#print axioms ProctorDecodedWidth.capacity_fit
#print axioms ProctorDecodedWidth.block_fit
#print axioms ProctorDecodedWidth.step_fit
#print axioms ProctorDecodedWidth.terminal_fit
#print axioms ProctorDecodedWidth.proof_fit
#print axioms ProctorDecodedWidth.envelope_fit
#print axioms ProctorDecodedWidth.token_fit
#print axioms ProctorDecodedWidth.decoded_expected
#print axioms ProctorDecodedWidth.decoded_envelope
#print axioms ProctorDecodedWidth.fuel_free_expected
#print axioms ProctorDecodedWidth.fuel_free_envelope
