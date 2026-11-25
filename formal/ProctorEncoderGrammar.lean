/-! F034 candidate: complete encoder-aware token grammar.
Each list uses the verified guarded header-accounting wrapper.
Pointwise result equivalence and reusable amortized bounds apply
to arbitrary token lists, including rejection. Selected events only. -/
namespace ProctorEncoderGrammar
open ProctorHallDeficiency
open ProctorExecutableReplay (Step)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorCapacityDeficiency (Group)
open ProctorXorReplay (Block)
open ProctorUnifiedReplay (Proof Terminal Envelope)
open ProctorDataParser (Parser natToken boolToken listToken)
open ProctorParserMeterCompose (ParserMeter project seqMeter seq_projection seq_bound
  listMeter list_projection list_refines natMeter boolMeter)
open ProctorNestedEncoderAmortization (chargedList charged_projection headerCharge header_bound potential Amortized list_amortized nat_amortized all_bound)

def listBudget (B : Nat) : Nat := ProctorParserMeterCompose.listBudget B+307

def Contract {α : Type} (m : ParserMeter α) (p : Parser α) (B : Nat) : Prop :=
  (∀ ts, (m ts).1=p ts) ∧ (∀ ts, (m ts).2≤B)

def ret {α : Type} (a : α) : ParserMeter α := fun ts => (some (a,ts),0)
def retPlain {α : Type} (a : α) : Parser α := fun ts => some (a,ts)
def reject {α : Type} : ParserMeter α := fun _ => (none,0)
def rejectPlain {α : Type} : Parser α := fun _ => none
def seqPlain {α β : Type} (p : Parser α) (q : α → Parser β) : Parser β := fun ts => do
  let (a,rest) ← p ts
  q a rest

def choose {α : Type} (h : Prop) [Decidable h] (a b : ParserMeter α) :
    ParserMeter α := fun ts => if h then a ts else b ts
def choosePlain {α : Type} (h : Prop) [Decidable h] (a b : Parser α) :
    Parser α := fun ts => if h then a ts else b ts

theorem ret_contract {α : Type} (a : α) : Contract (ret a) (retPlain a) 0 :=
  ⟨fun _ => rfl,fun _ => Nat.le_refl 0⟩
theorem reject_contract {α : Type} : Contract (reject (α := α)) rejectPlain 0 :=
  ⟨fun _ => rfl,fun _ => Nat.le_refl 0⟩
theorem nat_contract : Contract natMeter natToken 1 :=
  ⟨fun _ => rfl,fun _ => Nat.le_refl 1⟩
theorem bool_contract : Contract boolMeter boolToken 1 :=
  ⟨fun _ => rfl,fun _ => Nat.le_refl 1⟩

theorem seq_contract {α β : Type} (m : ParserMeter α) (p : Parser α)
    (n : α → ParserMeter β) (q : α → Parser β) (A B : Nat)
    (hm : Contract m p A) (hn : ∀ a, Contract (n a) (q a) B) :
    Contract (seqMeter m n) (seqPlain p q) (A+B) := by
  constructor
  · intro ts
    rw [seq_projection]
    change (do
      let (a,rest) ← (m ts).1
      (n a rest).1)=(do
      let (a,rest) ← p ts
      q a rest)
    rw [hm.1 ts]
    cases e : p ts with
    | none => rfl
    | some pair =>
      cases pair with
      | mk a rest => exact (hn a).1 rest
  · intro ts
    exact seq_bound m n A B hm.2 (fun a xs => (hn a).2 xs) ts

theorem list_contract {α : Type} (m : ParserMeter α) (p : Parser α)
    (B : Nat) (h : Contract m p B) :
    Contract (chargedList m) (listToken p) (listBudget B) := by
  constructor
  · intro ts
    rw [charged_projection,list_projection]
    exact ProctorFuelFreeParser.list_congr_pointwise (project m) p h.1 ts
  · intro ts
    change (listMeter m ts).2+headerCharge ts≤ProctorParserMeterCompose.listBudget B+307
    exact Nat.add_le_add (ProctorParserMeterCompose.list_bound m B h.2 ts) (header_bound ts)

theorem choose_contract {α : Type} (h : Prop) [Decidable h]
    (m n : ParserMeter α) (p q : Parser α) (A B : Nat)
    (hm : Contract m p A) (hn : Contract n q B) :
    Contract (choose h m n) (choosePlain h p q) (A+B) := by
  constructor
  · intro ts
    unfold choose choosePlain
    by_cases e : h
    · rw [if_pos e,if_pos e]
      exact hm.1 ts
    · rw [if_neg e,if_neg e]
      exact hn.1 ts
  · intro ts
    change (if h then m ts else n ts).2≤A+B
    by_cases e : h
    · rw [if_pos e]
      exact Nat.le_trans (hm.2 ts) (Nat.le_add_right _ _)
    · rw [if_neg e]
      exact Nat.le_trans (hn.2 ts) (Nat.le_add_left _ _)

def literalMeter : ParserMeter Literal := seqMeter (natMeter) (fun v => seqMeter (boolMeter) (fun b => ret ((v,b) : Literal)))
def literalBudget : Nat := (1)+((1)+(0))

theorem literal_contract : Contract literalMeter ProctorDataParser.literalToken literalBudget :=
  seq_contract (natMeter) (natToken) (fun v => seqMeter (boolMeter) (fun b => ret ((v,b) : Literal))) (fun v => seqPlain (boolToken) (fun b => retPlain ((v,b) : Literal))) (1) ((1)+(0)) (nat_contract) (fun v => seq_contract (boolMeter) (boolToken) (fun b => ret ((v,b) : Literal)) (fun b => retPlain ((v,b) : Literal)) (1) (0) (bool_contract) (fun b => ret_contract ((v,b) : Literal)))

def clauseMeter : ParserMeter Clause := chargedList (literalMeter)
def clauseBudget : Nat := listBudget (literalBudget)

theorem clause_contract : Contract clauseMeter ProctorDataParser.clauseToken clauseBudget :=
  list_contract (literalMeter) (ProctorDataParser.literalToken) (literalBudget) (literal_contract)

def formulaMeter : ParserMeter Formula := chargedList (clauseMeter)
def formulaBudget : Nat := listBudget (clauseBudget)

theorem formula_contract : Contract formulaMeter ProctorDataParser.formulaToken formulaBudget :=
  list_contract (clauseMeter) (ProctorDataParser.clauseToken) (clauseBudget) (clause_contract)

def refMeter : ParserMeter RefRow := seqMeter (natMeter) (fun i => seqMeter (clauseMeter) (fun row => ret (⟨i,row⟩ : RefRow)))
def refBudget : Nat := (1)+((clauseBudget)+(0))

theorem ref_contract : Contract refMeter ProctorDataParser.refToken refBudget :=
  seq_contract (natMeter) (natToken) (fun i => seqMeter (clauseMeter) (fun row => ret (⟨i,row⟩ : RefRow))) (fun i => seqPlain (ProctorDataParser.clauseToken) (fun row => retPlain (⟨i,row⟩ : RefRow))) (1) ((clauseBudget)+(0)) (nat_contract) (fun i => seq_contract (clauseMeter) (ProctorDataParser.clauseToken) (fun row => ret (⟨i,row⟩ : RefRow)) (fun row => retPlain (⟨i,row⟩ : RefRow)) (clauseBudget) (0) (clause_contract) (fun row => ret_contract (⟨i,row⟩ : RefRow)))

def groupMeter : ParserMeter Group := seqMeter (clauseMeter) (fun vs => seqMeter (natMeter) (fun cap => ret (⟨vs,cap⟩ : Group)))
def groupBudget : Nat := (clauseBudget)+((1)+(0))

theorem group_contract : Contract groupMeter ProctorDataParser.groupToken groupBudget :=
  seq_contract (clauseMeter) (ProctorDataParser.clauseToken) (fun vs => seqMeter (natMeter) (fun cap => ret (⟨vs,cap⟩ : Group))) (fun vs => seqPlain (natToken) (fun cap => retPlain (⟨vs,cap⟩ : Group))) (clauseBudget) ((1)+(0)) (clause_contract) (fun vs => seq_contract (natMeter) (natToken) (fun cap => ret (⟨vs,cap⟩ : Group)) (fun cap => retPlain (⟨vs,cap⟩ : Group)) (1) (0) (nat_contract) (fun cap => ret_contract (⟨vs,cap⟩ : Group)))

def capacityMeter : ParserMeter Certificate := seqMeter (chargedList (refMeter)) (fun ds => seqMeter (chargedList (groupMeter)) (fun gs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate))))
def capacityBudget : Nat := (listBudget (refBudget))+((listBudget (groupBudget))+((listBudget (refBudget))+(0)))

theorem capacity_contract : Contract capacityMeter ProctorDataParser.capacityToken capacityBudget :=
  seq_contract (chargedList (refMeter)) (listToken (ProctorDataParser.refToken)) (fun ds => seqMeter (chargedList (groupMeter)) (fun gs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate)))) (fun ds => seqPlain (listToken (ProctorDataParser.groupToken)) (fun gs => seqPlain (listToken (ProctorDataParser.refToken)) (fun rs => retPlain (⟨ds,gs,rs⟩ : Certificate)))) (listBudget (refBudget)) ((listBudget (groupBudget))+((listBudget (refBudget))+(0))) (list_contract (refMeter) (ProctorDataParser.refToken) (refBudget) (ref_contract)) (fun ds => seq_contract (chargedList (groupMeter)) (listToken (ProctorDataParser.groupToken)) (fun gs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate))) (fun gs => seqPlain (listToken (ProctorDataParser.refToken)) (fun rs => retPlain (⟨ds,gs,rs⟩ : Certificate))) (listBudget (groupBudget)) ((listBudget (refBudget))+(0)) (list_contract (groupMeter) (ProctorDataParser.groupToken) (groupBudget) (group_contract)) (fun gs => seq_contract (chargedList (refMeter)) (listToken (ProctorDataParser.refToken)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate)) (fun rs => retPlain (⟨ds,gs,rs⟩ : Certificate)) (listBudget (refBudget)) (0) (list_contract (refMeter) (ProctorDataParser.refToken) (refBudget) (ref_contract)) (fun rs => ret_contract (⟨ds,gs,rs⟩ : Certificate))))

def blockMeter : ParserMeter Block := seqMeter (chargedList (natMeter)) (fun vs => seqMeter (boolMeter) (fun rhs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block))))
def blockBudget : Nat := (listBudget (1))+((1)+((listBudget (refBudget))+(0)))

theorem block_contract : Contract blockMeter ProctorDataParser.blockToken blockBudget :=
  seq_contract (chargedList (natMeter)) (listToken (natToken)) (fun vs => seqMeter (boolMeter) (fun rhs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block)))) (fun vs => seqPlain (boolToken) (fun rhs => seqPlain (listToken (ProctorDataParser.refToken)) (fun rs => retPlain (⟨vs,rhs,rs⟩ : Block)))) (listBudget (1)) ((1)+((listBudget (refBudget))+(0))) (list_contract (natMeter) (natToken) (1) (nat_contract)) (fun vs => seq_contract (boolMeter) (boolToken) (fun rhs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block))) (fun rhs => seqPlain (listToken (ProctorDataParser.refToken)) (fun rs => retPlain (⟨vs,rhs,rs⟩ : Block))) (1) ((listBudget (refBudget))+(0)) (bool_contract) (fun rhs => seq_contract (chargedList (refMeter)) (listToken (ProctorDataParser.refToken)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block)) (fun rs => retPlain (⟨vs,rhs,rs⟩ : Block)) (listBudget (refBudget)) (0) (list_contract (refMeter) (ProctorDataParser.refToken) (refBudget) (ref_contract)) (fun rs => ret_contract (⟨vs,rhs,rs⟩ : Block))))

def stepMeter : ParserMeter Step := seqMeter (natMeter) (fun a => seqMeter (natMeter) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step)))))
def stepBudget : Nat := (1)+((1)+((1)+((clauseBudget)+(0))))

theorem step_contract : Contract stepMeter ProctorDataParser.stepToken stepBudget :=
  seq_contract (natMeter) (natToken) (fun a => seqMeter (natMeter) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))))) (fun a => seqPlain (natToken) (fun b => seqPlain (natToken) (fun p => seqPlain (ProctorDataParser.clauseToken) (fun tail => retPlain (⟨a,b,p,tail⟩ : Step))))) (1) ((1)+((1)+((clauseBudget)+(0)))) (nat_contract) (fun a => seq_contract (natMeter) (natToken) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step)))) (fun b => seqPlain (natToken) (fun p => seqPlain (ProctorDataParser.clauseToken) (fun tail => retPlain (⟨a,b,p,tail⟩ : Step)))) (1) ((1)+((clauseBudget)+(0))) (nat_contract) (fun b => seq_contract (natMeter) (natToken) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))) (fun p => seqPlain (ProctorDataParser.clauseToken) (fun tail => retPlain (⟨a,b,p,tail⟩ : Step))) (1) ((clauseBudget)+(0)) (nat_contract) (fun p => seq_contract (clauseMeter) (ProctorDataParser.clauseToken) (fun tail => ret (⟨a,b,p,tail⟩ : Step)) (fun tail => retPlain (⟨a,b,p,tail⟩ : Step)) (clauseBudget) (0) (clause_contract) (fun tail => ret_contract (⟨a,b,p,tail⟩ : Step)))))

def terminalMeter : ParserMeter Terminal := seqMeter (natMeter) (fun tag => choose (tag=0) (ret (.empty : Terminal)) (choose (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal)))))
def terminalBudget : Nat := (1)+((0)+(((capacityBudget)+(0))+(((listBudget (blockBudget))+(0))+(0))))

theorem terminal_contract : Contract terminalMeter ProctorDataParser.terminalToken terminalBudget :=
  seq_contract (natMeter) (natToken) (fun tag => choose (tag=0) (ret (.empty : Terminal)) (choose (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal))))) (fun tag => choosePlain (tag=0) (retPlain (.empty : Terminal)) (choosePlain (tag=1) (seqPlain (ProctorDataParser.capacityToken) (fun c => retPlain (.capacity c : Terminal))) (choosePlain (tag=2) (seqPlain (listToken (ProctorDataParser.blockToken)) (fun bs => retPlain (.xor bs : Terminal))) (rejectPlain (α := Terminal))))) (1) ((0)+(((capacityBudget)+(0))+(((listBudget (blockBudget))+(0))+(0)))) (nat_contract) (fun tag => choose_contract (tag=0) (ret (.empty : Terminal)) (choose (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal)))) (retPlain (.empty : Terminal)) (choosePlain (tag=1) (seqPlain (ProctorDataParser.capacityToken) (fun c => retPlain (.capacity c : Terminal))) (choosePlain (tag=2) (seqPlain (listToken (ProctorDataParser.blockToken)) (fun bs => retPlain (.xor bs : Terminal))) (rejectPlain (α := Terminal)))) (0) (((capacityBudget)+(0))+(((listBudget (blockBudget))+(0))+(0))) (ret_contract (.empty : Terminal)) (choose_contract (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal))) (seqPlain (ProctorDataParser.capacityToken) (fun c => retPlain (.capacity c : Terminal))) (choosePlain (tag=2) (seqPlain (listToken (ProctorDataParser.blockToken)) (fun bs => retPlain (.xor bs : Terminal))) (rejectPlain (α := Terminal))) ((capacityBudget)+(0)) (((listBudget (blockBudget))+(0))+(0)) (seq_contract (capacityMeter) (ProctorDataParser.capacityToken) (fun c => ret (.capacity c : Terminal)) (fun c => retPlain (.capacity c : Terminal)) (capacityBudget) (0) (capacity_contract) (fun c => ret_contract (.capacity c : Terminal))) (choose_contract (tag=2) (seqMeter (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal)) (seqPlain (listToken (ProctorDataParser.blockToken)) (fun bs => retPlain (.xor bs : Terminal))) (rejectPlain (α := Terminal)) ((listBudget (blockBudget))+(0)) (0) (seq_contract (chargedList (blockMeter)) (listToken (ProctorDataParser.blockToken)) (fun bs => ret (.xor bs : Terminal)) (fun bs => retPlain (.xor bs : Terminal)) (listBudget (blockBudget)) (0) (list_contract (blockMeter) (ProctorDataParser.blockToken) (blockBudget) (block_contract)) (fun bs => ret_contract (.xor bs : Terminal))) (reject_contract (α := Terminal)))))

def proofMeter : ParserMeter Proof := seqMeter (chargedList (chargedList (stepMeter))) (fun bs => seqMeter (boolMeter) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof))))
def proofBudget : Nat := (listBudget (listBudget (stepBudget)))+((1)+((terminalBudget)+(0)))

theorem proof_contract : Contract proofMeter ProctorDataParser.proofToken proofBudget :=
  seq_contract (chargedList (chargedList (stepMeter))) (listToken (listToken (ProctorDataParser.stepToken))) (fun bs => seqMeter (boolMeter) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof)))) (fun bs => seqPlain (boolToken) (fun aug => seqPlain (ProctorDataParser.terminalToken) (fun t => retPlain (⟨bs,aug,t⟩ : Proof)))) (listBudget (listBudget (stepBudget))) ((1)+((terminalBudget)+(0))) (list_contract (chargedList (stepMeter)) (listToken (ProctorDataParser.stepToken)) (listBudget (stepBudget)) (list_contract (stepMeter) (ProctorDataParser.stepToken) (stepBudget) (step_contract))) (fun bs => seq_contract (boolMeter) (boolToken) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof))) (fun aug => seqPlain (ProctorDataParser.terminalToken) (fun t => retPlain (⟨bs,aug,t⟩ : Proof))) (1) ((terminalBudget)+(0)) (bool_contract) (fun aug => seq_contract (terminalMeter) (ProctorDataParser.terminalToken) (fun t => ret (⟨bs,aug,t⟩ : Proof)) (fun t => retPlain (⟨bs,aug,t⟩ : Proof)) (terminalBudget) (0) (terminal_contract) (fun t => ret_contract (⟨bs,aug,t⟩ : Proof))))

def expectedMeter : ParserMeter (Nat × Formula) := seqMeter (natMeter) (fun magic => choose (magic=3401) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)))) (reject (α := Nat × Formula)))
def expectedBudget : Nat := (1)+(((1)+((formulaBudget)+(0)))+(0))

theorem expected_contract : Contract expectedMeter ProctorDataParser.expectedToken expectedBudget :=
  seq_contract (natMeter) (natToken) (fun magic => choose (magic=3401) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)))) (reject (α := Nat × Formula))) (fun magic => choosePlain (magic=3401) (seqPlain (natToken) (fun n => seqPlain (ProctorDataParser.formulaToken) (fun f => retPlain ((n,f) : Nat × Formula)))) (rejectPlain (α := Nat × Formula))) (1) (((1)+((formulaBudget)+(0)))+(0)) (nat_contract) (fun magic => choose_contract (magic=3401) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)))) (reject (α := Nat × Formula)) (seqPlain (natToken) (fun n => seqPlain (ProctorDataParser.formulaToken) (fun f => retPlain ((n,f) : Nat × Formula)))) (rejectPlain (α := Nat × Formula)) ((1)+((formulaBudget)+(0))) (0) (seq_contract (natMeter) (natToken) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula))) (fun n => seqPlain (ProctorDataParser.formulaToken) (fun f => retPlain ((n,f) : Nat × Formula))) (1) ((formulaBudget)+(0)) (nat_contract) (fun n => seq_contract (formulaMeter) (ProctorDataParser.formulaToken) (fun f => ret ((n,f) : Nat × Formula)) (fun f => retPlain ((n,f) : Nat × Formula)) (formulaBudget) (0) (formula_contract) (fun f => ret_contract ((n,f) : Nat × Formula)))) (reject_contract (α := Nat × Formula)))

def envelopeMeter : ParserMeter Envelope := seqMeter (natMeter) (fun magic => choose (magic=3402) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))))) (reject (α := Envelope)))
def envelopeBudget : Nat := (1)+(((1)+((formulaBudget)+((proofBudget)+(0))))+(0))

theorem envelope_contract : Contract envelopeMeter ProctorDataParser.envelopeToken envelopeBudget :=
  seq_contract (natMeter) (natToken) (fun magic => choose (magic=3402) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))))) (reject (α := Envelope))) (fun magic => choosePlain (magic=3402) (seqPlain (natToken) (fun n => seqPlain (ProctorDataParser.formulaToken) (fun f => seqPlain (ProctorDataParser.proofToken) (fun p => retPlain (⟨n,f,p⟩ : Envelope))))) (rejectPlain (α := Envelope))) (1) (((1)+((formulaBudget)+((proofBudget)+(0))))+(0)) (nat_contract) (fun magic => choose_contract (magic=3402) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))))) (reject (α := Envelope)) (seqPlain (natToken) (fun n => seqPlain (ProctorDataParser.formulaToken) (fun f => seqPlain (ProctorDataParser.proofToken) (fun p => retPlain (⟨n,f,p⟩ : Envelope))))) (rejectPlain (α := Envelope)) ((1)+((formulaBudget)+((proofBudget)+(0)))) (0) (seq_contract (natMeter) (natToken) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope)))) (fun n => seqPlain (ProctorDataParser.formulaToken) (fun f => seqPlain (ProctorDataParser.proofToken) (fun p => retPlain (⟨n,f,p⟩ : Envelope)))) (1) ((formulaBudget)+((proofBudget)+(0))) (nat_contract) (fun n => seq_contract (formulaMeter) (ProctorDataParser.formulaToken) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))) (fun f => seqPlain (ProctorDataParser.proofToken) (fun p => retPlain (⟨n,f,p⟩ : Envelope))) (formulaBudget) ((proofBudget)+(0)) (formula_contract) (fun f => seq_contract (proofMeter) (ProctorDataParser.proofToken) (fun p => ret (⟨n,f,p⟩ : Envelope)) (fun p => retPlain (⟨n,f,p⟩ : Envelope)) (proofBudget) (0) (proof_contract) (fun p => ret_contract (⟨n,f,p⟩ : Envelope))))) (reject_contract (α := Envelope)))

theorem expected_refines (ts : List Nat) :
    (expectedMeter ts).1=ProctorDataParser.expectedToken ts :=
  expected_contract.1 ts
theorem envelope_refines (ts : List Nat) :
    (envelopeMeter ts).1=ProctorDataParser.envelopeToken ts :=
  envelope_contract.1 ts
theorem expected_uniform_bound (ts : List Nat) : (expectedMeter ts).2≤expectedBudget :=
  expected_contract.2 ts
theorem envelope_uniform_bound (ts : List Nat) : (envelopeMeter ts).2≤envelopeBudget :=
  envelope_contract.2 ts

def Weak {α : Type} (p : ParserMeter α) : Prop :=
  (∀ ts a rest, (p ts).1=some (a,rest) →
    (p ts).2+potential rest≤potential ts) ∧
  (∀ ts, (p ts).1=none → (p ts).2≤potential ts+1)

private theorem drop_two (a b x : Nat) (h : (a+2)+b≤x) : a+b≤x :=
  Nat.le_trans (Nat.add_le_add (Nat.le_add_right a 2) (Nat.le_refl b)) h

private theorem shift (a b c : Nat) : (a+b)+c=(a+c)+b := by
  calc
    (a+b)+c = a+(b+c) := Nat.add_assoc _ _ _
    _ = a+(c+b) := congrArg (fun n => a+n) (Nat.add_comm _ _)
    _ = (a+c)+b := (Nat.add_assoc _ _ _).symm

theorem weaken {α : Type} (p : ParserMeter α) (hp : Amortized p) :
    Weak p := by
  constructor
  · intro ts a rest h
    exact drop_two _ _ _ (hp.1 ts a rest h)
  · intro ts h
    have hb := hp.2 ts h
    change (p ts).2+2≤(potential ts+1)+2 at hb
    exact Nat.le_of_succ_le_succ (Nat.le_of_succ_le_succ hb)

theorem ret_weak {α : Type} (a : α) : Weak (ret a) := by
  constructor
  · intro ts b rest h
    change some (a,ts)=some (b,rest) at h
    have e : ts=rest := congrArg Prod.snd (Option.some.inj h)
    change 0+potential rest≤potential ts
    rw [← e,Nat.zero_add]
    exact Nat.le_refl _
  · intro ts h
    cases h

theorem reject_weak {α : Type} : Weak (reject (α := α)) := by
  constructor
  · intro ts a rest h
    cases h
  · intro ts h
    exact Nat.zero_le _

theorem bool_amortized : Amortized boolMeter := by
  constructor
  · intro ts a rest h
    cases ts with
    | nil => cases h
    | cons v vs =>
      change (if v=0 then some (false,vs)
        else if v=1 then some (true,vs) else none)=some (a,rest) at h
      have e : vs=rest := by
        by_cases hz : v=0
        · rw [if_pos hz] at h
          exact congrArg Prod.snd (Option.some.inj h)
        · rw [if_neg hz] at h
          by_cases ho : v=1
          · rw [if_pos ho] at h
            exact congrArg Prod.snd (Option.some.inj h)
          · rw [if_neg ho] at h
            cases h
      rw [← e]
      change 3+potential vs≤potential vs+512
      rw [Nat.add_comm 3 (potential vs)]
      exact Nat.add_le_add (Nat.le_refl _) (by decide : 3≤512)
  · intro ts h
    change 3≤potential ts+3
    exact Nat.le_add_left _ _

private theorem seq_none {α β : Type} (p : ParserMeter α)
    (q : α → ParserMeter β) (ts : List Nat) (e : (p ts).1=none) :
    seqMeter p q ts=(none,(p ts).2) := by
  change (match (p ts).1 with
    | none => (none,(p ts).2)
    | some (a,rest) => ((q a rest).1,(p ts).2+(q a rest).2))=_
  rw [e]

private theorem seq_some {α β : Type} (p : ParserMeter α)
    (q : α → ParserMeter β) (ts : List Nat) (a : α) (rest : List Nat)
    (e : (p ts).1=some (a,rest)) :
    seqMeter p q ts=((q a rest).1,(p ts).2+(q a rest).2) := by
  change (match (p ts).1 with
    | none => (none,(p ts).2)
    | some (b,next) => ((q b next).1,(p ts).2+(q b next).2))=_
  rw [e]

theorem seq_amortized {α β : Type} (p : ParserMeter α) (q : α → ParserMeter β)
    (hp : Amortized p) (hq : ∀ a, Weak (q a)) :
    Amortized (seqMeter p q) := by
  constructor
  · intro ts b rest hs
    cases e : (p ts).1 with
    | none =>
      rw [seq_none p q ts e] at hs
      cases hs
    | some pair =>
      cases pair with
      | mk a next =>
        rw [seq_some p q ts a next e] at hs ⊢
        change (q a next).1=some (b,rest) at hs
        change (((p ts).2+(q a next).2)+2)+potential rest≤potential ts
        rw [shift (p ts).2 (q a next).2 2,Nat.add_assoc]
        exact Nat.le_trans (Nat.add_le_add (Nat.le_refl _)
          ((hq a).1 next b rest hs)) (hp.1 ts a next e)
  · intro ts hs
    cases e : (p ts).1 with
    | none =>
      rw [seq_none p q ts e]
      exact hp.2 ts e
    | some pair =>
      cases pair with
      | mk a next =>
        rw [seq_some p q ts a next e] at hs ⊢
        change (q a next).1=none at hs
        change ((p ts).2+(q a next).2)+2≤potential ts+3
        rw [shift (p ts).2 (q a next).2 2]
        calc
          ((p ts).2+2)+(q a next).2 ≤
              ((p ts).2+2)+(potential next+1) :=
            Nat.add_le_add (Nat.le_refl _) ((hq a).2 next hs)
          _ = (((p ts).2+2)+potential next)+1 :=
            (Nat.add_assoc _ _ _).symm
          _ ≤ potential ts+3 :=
            Nat.add_le_add (hp.1 ts a next e) (by decide : 1≤3)

theorem choose_weak {α : Type} (h : Prop) [Decidable h]
    (p q : ParserMeter α) (hp : Weak p) (hq : Weak q) :
    Weak (choose h p q) := by
  by_cases e : h
  · constructor
    · intro ts a rest hs
      change (if h then p ts else q ts).1=some (a,rest) at hs
      change (if h then p ts else q ts).2+potential rest≤potential ts
      rw [if_pos e] at hs ⊢
      exact hp.1 ts a rest hs
    · intro ts hs
      change (if h then p ts else q ts).1=none at hs
      change (if h then p ts else q ts).2≤potential ts+1
      rw [if_pos e] at hs ⊢
      exact hp.2 ts hs
  · constructor
    · intro ts a rest hs
      change (if h then p ts else q ts).1=some (a,rest) at hs
      change (if h then p ts else q ts).2+potential rest≤potential ts
      rw [if_neg e] at hs ⊢
      exact hq.1 ts a rest hs
    · intro ts hs
      change (if h then p ts else q ts).1=none at hs
      change (if h then p ts else q ts).2≤potential ts+1
      rw [if_neg e] at hs ⊢
      exact hq.2 ts hs

theorem literal_amortized : Amortized literalMeter :=
  seq_amortized (natMeter) (fun v => seqMeter (boolMeter) (fun b => ret ((v,b) : Literal))) (nat_amortized) (fun v => weaken (seqMeter (boolMeter) (fun b => ret ((v,b) : Literal))) (seq_amortized (boolMeter) (fun b => ret ((v,b) : Literal)) (bool_amortized) (fun b => ret_weak ((v,b) : Literal))))

theorem clause_amortized : Amortized clauseMeter :=
  list_amortized (literalMeter) (literal_amortized)

theorem formula_amortized : Amortized formulaMeter :=
  list_amortized (clauseMeter) (clause_amortized)

theorem ref_amortized : Amortized refMeter :=
  seq_amortized (natMeter) (fun i => seqMeter (clauseMeter) (fun row => ret (⟨i,row⟩ : RefRow))) (nat_amortized) (fun i => weaken (seqMeter (clauseMeter) (fun row => ret (⟨i,row⟩ : RefRow))) (seq_amortized (clauseMeter) (fun row => ret (⟨i,row⟩ : RefRow)) (clause_amortized) (fun row => ret_weak (⟨i,row⟩ : RefRow))))

theorem group_amortized : Amortized groupMeter :=
  seq_amortized (clauseMeter) (fun vs => seqMeter (natMeter) (fun cap => ret (⟨vs,cap⟩ : Group))) (clause_amortized) (fun vs => weaken (seqMeter (natMeter) (fun cap => ret (⟨vs,cap⟩ : Group))) (seq_amortized (natMeter) (fun cap => ret (⟨vs,cap⟩ : Group)) (nat_amortized) (fun cap => ret_weak (⟨vs,cap⟩ : Group))))

theorem capacity_amortized : Amortized capacityMeter :=
  seq_amortized (chargedList (refMeter)) (fun ds => seqMeter (chargedList (groupMeter)) (fun gs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate)))) (list_amortized (refMeter) (ref_amortized)) (fun ds => weaken (seqMeter (chargedList (groupMeter)) (fun gs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate)))) (seq_amortized (chargedList (groupMeter)) (fun gs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate))) (list_amortized (groupMeter) (group_amortized)) (fun gs => weaken (seqMeter (chargedList (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate))) (seq_amortized (chargedList (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate)) (list_amortized (refMeter) (ref_amortized)) (fun rs => ret_weak (⟨ds,gs,rs⟩ : Certificate))))))

theorem block_amortized : Amortized blockMeter :=
  seq_amortized (chargedList (natMeter)) (fun vs => seqMeter (boolMeter) (fun rhs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block)))) (list_amortized (natMeter) (nat_amortized)) (fun vs => weaken (seqMeter (boolMeter) (fun rhs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block)))) (seq_amortized (boolMeter) (fun rhs => seqMeter (chargedList (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block))) (bool_amortized) (fun rhs => weaken (seqMeter (chargedList (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block))) (seq_amortized (chargedList (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block)) (list_amortized (refMeter) (ref_amortized)) (fun rs => ret_weak (⟨vs,rhs,rs⟩ : Block))))))

theorem step_amortized : Amortized stepMeter :=
  seq_amortized (natMeter) (fun a => seqMeter (natMeter) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))))) (nat_amortized) (fun a => weaken (seqMeter (natMeter) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))))) (seq_amortized (natMeter) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step)))) (nat_amortized) (fun b => weaken (seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step)))) (seq_amortized (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))) (nat_amortized) (fun p => weaken (seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))) (seq_amortized (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step)) (clause_amortized) (fun tail => ret_weak (⟨a,b,p,tail⟩ : Step))))))))

theorem terminal_amortized : Amortized terminalMeter :=
  seq_amortized (natMeter) (fun tag => choose (tag=0) (ret (.empty : Terminal)) (choose (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal))))) (nat_amortized) (fun tag => choose_weak (tag=0) (ret (.empty : Terminal)) (choose (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal)))) (ret_weak (.empty : Terminal)) (choose_weak (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal))) (weaken (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (seq_amortized (capacityMeter) (fun c => ret (.capacity c : Terminal)) (capacity_amortized) (fun c => ret_weak (.capacity c : Terminal)))) (choose_weak (tag=2) (seqMeter (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal)) (weaken (seqMeter (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (seq_amortized (chargedList (blockMeter)) (fun bs => ret (.xor bs : Terminal)) (list_amortized (blockMeter) (block_amortized)) (fun bs => ret_weak (.xor bs : Terminal)))) (reject_weak (α := Terminal)))))

theorem proof_amortized : Amortized proofMeter :=
  seq_amortized (chargedList (chargedList (stepMeter))) (fun bs => seqMeter (boolMeter) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof)))) (list_amortized (chargedList (stepMeter)) (list_amortized (stepMeter) (step_amortized))) (fun bs => weaken (seqMeter (boolMeter) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof)))) (seq_amortized (boolMeter) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof))) (bool_amortized) (fun aug => weaken (seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof))) (seq_amortized (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof)) (terminal_amortized) (fun t => ret_weak (⟨bs,aug,t⟩ : Proof))))))

theorem expected_amortized : Amortized expectedMeter :=
  seq_amortized (natMeter) (fun magic => choose (magic=3401) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)))) (reject (α := Nat × Formula))) (nat_amortized) (fun magic => choose_weak (magic=3401) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)))) (reject (α := Nat × Formula)) (weaken (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)))) (seq_amortized (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula))) (nat_amortized) (fun n => weaken (seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula))) (seq_amortized (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)) (formula_amortized) (fun f => ret_weak ((n,f) : Nat × Formula)))))) (reject_weak (α := Nat × Formula)))

theorem envelope_amortized : Amortized envelopeMeter :=
  seq_amortized (natMeter) (fun magic => choose (magic=3402) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))))) (reject (α := Envelope))) (nat_amortized) (fun magic => choose_weak (magic=3402) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))))) (reject (α := Envelope)) (weaken (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))))) (seq_amortized (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope)))) (nat_amortized) (fun n => weaken (seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope)))) (seq_amortized (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))) (formula_amortized) (fun f => weaken (seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))) (seq_amortized (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope)) (proof_amortized) (fun p => ret_weak (⟨n,f,p⟩ : Envelope)))))))) (reject_weak (α := Envelope)))

theorem expected_bound (ts : List Nat) : (expectedMeter ts).2≤512*ts.length+3 :=
  all_bound _ expected_amortized ts

theorem envelope_bound (ts : List Nat) : (envelopeMeter ts).2≤512*ts.length+3 :=
  all_bound _ envelope_amortized ts


end ProctorEncoderGrammar
#print axioms ProctorEncoderGrammar.ret_contract
#print axioms ProctorEncoderGrammar.reject_contract
#print axioms ProctorEncoderGrammar.nat_contract
#print axioms ProctorEncoderGrammar.bool_contract
#print axioms ProctorEncoderGrammar.seq_contract
#print axioms ProctorEncoderGrammar.list_contract
#print axioms ProctorEncoderGrammar.choose_contract
#print axioms ProctorEncoderGrammar.literal_contract
#print axioms ProctorEncoderGrammar.clause_contract
#print axioms ProctorEncoderGrammar.formula_contract
#print axioms ProctorEncoderGrammar.ref_contract
#print axioms ProctorEncoderGrammar.group_contract
#print axioms ProctorEncoderGrammar.capacity_contract
#print axioms ProctorEncoderGrammar.block_contract
#print axioms ProctorEncoderGrammar.step_contract
#print axioms ProctorEncoderGrammar.terminal_contract
#print axioms ProctorEncoderGrammar.proof_contract
#print axioms ProctorEncoderGrammar.expected_contract
#print axioms ProctorEncoderGrammar.envelope_contract
#print axioms ProctorEncoderGrammar.expected_refines
#print axioms ProctorEncoderGrammar.envelope_refines
#print axioms ProctorEncoderGrammar.expected_uniform_bound
#print axioms ProctorEncoderGrammar.envelope_uniform_bound
#print axioms ProctorEncoderGrammar.weaken
#print axioms ProctorEncoderGrammar.ret_weak
#print axioms ProctorEncoderGrammar.reject_weak
#print axioms ProctorEncoderGrammar.bool_amortized
#print axioms ProctorEncoderGrammar.seq_amortized
#print axioms ProctorEncoderGrammar.choose_weak
#print axioms ProctorEncoderGrammar.literal_amortized
#print axioms ProctorEncoderGrammar.clause_amortized
#print axioms ProctorEncoderGrammar.formula_amortized
#print axioms ProctorEncoderGrammar.ref_amortized
#print axioms ProctorEncoderGrammar.group_amortized
#print axioms ProctorEncoderGrammar.capacity_amortized
#print axioms ProctorEncoderGrammar.block_amortized
#print axioms ProctorEncoderGrammar.step_amortized
#print axioms ProctorEncoderGrammar.terminal_amortized
#print axioms ProctorEncoderGrammar.proof_amortized
#print axioms ProctorEncoderGrammar.expected_amortized
#print axioms ProctorEncoderGrammar.envelope_amortized
#print axioms ProctorEncoderGrammar.expected_bound
#print axioms ProctorEncoderGrammar.envelope_bound
