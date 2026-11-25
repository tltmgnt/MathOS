/-! F034 candidate: selected resource meter for the complete token grammar.
Each contract gives pointwise result equality and a uniform bound on
selected charges, including rejection. No complete machine-cost claim. -/
namespace ProctorGrammarMeter
open ProctorHallDeficiency
open ProctorExecutableReplay (Step)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorCapacityDeficiency (Group)
open ProctorXorReplay (Block)
open ProctorUnifiedReplay (Proof Terminal Envelope)
open ProctorDataParser (Parser natToken boolToken listToken)
open ProctorParserMeterCompose (ParserMeter project seqMeter seq_projection seq_bound
  listMeter list_projection listBudget list_bound list_refines natMeter boolMeter)

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
    Contract (listMeter m) (listToken p) (listBudget B) := by
  constructor
  · intro ts
    rw [list_projection]
    exact ProctorFuelFreeParser.list_congr_pointwise (project m) p h.1 ts
  · exact list_bound m B h.2

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

def clauseMeter : ParserMeter Clause := listMeter (literalMeter)
def clauseBudget : Nat := listBudget (literalBudget)

theorem clause_contract : Contract clauseMeter ProctorDataParser.clauseToken clauseBudget :=
  list_contract (literalMeter) (ProctorDataParser.literalToken) (literalBudget) (literal_contract)

def formulaMeter : ParserMeter Formula := listMeter (clauseMeter)
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

def capacityMeter : ParserMeter Certificate := seqMeter (listMeter (refMeter)) (fun ds => seqMeter (listMeter (groupMeter)) (fun gs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate))))
def capacityBudget : Nat := (listBudget (refBudget))+((listBudget (groupBudget))+((listBudget (refBudget))+(0)))

theorem capacity_contract : Contract capacityMeter ProctorDataParser.capacityToken capacityBudget :=
  seq_contract (listMeter (refMeter)) (listToken (ProctorDataParser.refToken)) (fun ds => seqMeter (listMeter (groupMeter)) (fun gs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate)))) (fun ds => seqPlain (listToken (ProctorDataParser.groupToken)) (fun gs => seqPlain (listToken (ProctorDataParser.refToken)) (fun rs => retPlain (⟨ds,gs,rs⟩ : Certificate)))) (listBudget (refBudget)) ((listBudget (groupBudget))+((listBudget (refBudget))+(0))) (list_contract (refMeter) (ProctorDataParser.refToken) (refBudget) (ref_contract)) (fun ds => seq_contract (listMeter (groupMeter)) (listToken (ProctorDataParser.groupToken)) (fun gs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate))) (fun gs => seqPlain (listToken (ProctorDataParser.refToken)) (fun rs => retPlain (⟨ds,gs,rs⟩ : Certificate))) (listBudget (groupBudget)) ((listBudget (refBudget))+(0)) (list_contract (groupMeter) (ProctorDataParser.groupToken) (groupBudget) (group_contract)) (fun gs => seq_contract (listMeter (refMeter)) (listToken (ProctorDataParser.refToken)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate)) (fun rs => retPlain (⟨ds,gs,rs⟩ : Certificate)) (listBudget (refBudget)) (0) (list_contract (refMeter) (ProctorDataParser.refToken) (refBudget) (ref_contract)) (fun rs => ret_contract (⟨ds,gs,rs⟩ : Certificate))))

def blockMeter : ParserMeter Block := seqMeter (listMeter (natMeter)) (fun vs => seqMeter (boolMeter) (fun rhs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block))))
def blockBudget : Nat := (listBudget (1))+((1)+((listBudget (refBudget))+(0)))

theorem block_contract : Contract blockMeter ProctorDataParser.blockToken blockBudget :=
  seq_contract (listMeter (natMeter)) (listToken (natToken)) (fun vs => seqMeter (boolMeter) (fun rhs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block)))) (fun vs => seqPlain (boolToken) (fun rhs => seqPlain (listToken (ProctorDataParser.refToken)) (fun rs => retPlain (⟨vs,rhs,rs⟩ : Block)))) (listBudget (1)) ((1)+((listBudget (refBudget))+(0))) (list_contract (natMeter) (natToken) (1) (nat_contract)) (fun vs => seq_contract (boolMeter) (boolToken) (fun rhs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block))) (fun rhs => seqPlain (listToken (ProctorDataParser.refToken)) (fun rs => retPlain (⟨vs,rhs,rs⟩ : Block))) (1) ((listBudget (refBudget))+(0)) (bool_contract) (fun rhs => seq_contract (listMeter (refMeter)) (listToken (ProctorDataParser.refToken)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block)) (fun rs => retPlain (⟨vs,rhs,rs⟩ : Block)) (listBudget (refBudget)) (0) (list_contract (refMeter) (ProctorDataParser.refToken) (refBudget) (ref_contract)) (fun rs => ret_contract (⟨vs,rhs,rs⟩ : Block))))

def stepMeter : ParserMeter Step := seqMeter (natMeter) (fun a => seqMeter (natMeter) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step)))))
def stepBudget : Nat := (1)+((1)+((1)+((clauseBudget)+(0))))

theorem step_contract : Contract stepMeter ProctorDataParser.stepToken stepBudget :=
  seq_contract (natMeter) (natToken) (fun a => seqMeter (natMeter) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))))) (fun a => seqPlain (natToken) (fun b => seqPlain (natToken) (fun p => seqPlain (ProctorDataParser.clauseToken) (fun tail => retPlain (⟨a,b,p,tail⟩ : Step))))) (1) ((1)+((1)+((clauseBudget)+(0)))) (nat_contract) (fun a => seq_contract (natMeter) (natToken) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step)))) (fun b => seqPlain (natToken) (fun p => seqPlain (ProctorDataParser.clauseToken) (fun tail => retPlain (⟨a,b,p,tail⟩ : Step)))) (1) ((1)+((clauseBudget)+(0))) (nat_contract) (fun b => seq_contract (natMeter) (natToken) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))) (fun p => seqPlain (ProctorDataParser.clauseToken) (fun tail => retPlain (⟨a,b,p,tail⟩ : Step))) (1) ((clauseBudget)+(0)) (nat_contract) (fun p => seq_contract (clauseMeter) (ProctorDataParser.clauseToken) (fun tail => ret (⟨a,b,p,tail⟩ : Step)) (fun tail => retPlain (⟨a,b,p,tail⟩ : Step)) (clauseBudget) (0) (clause_contract) (fun tail => ret_contract (⟨a,b,p,tail⟩ : Step)))))

def terminalMeter : ParserMeter Terminal := seqMeter (natMeter) (fun tag => choose (tag=0) (ret (.empty : Terminal)) (choose (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal)))))
def terminalBudget : Nat := (1)+((0)+(((capacityBudget)+(0))+(((listBudget (blockBudget))+(0))+(0))))

theorem terminal_contract : Contract terminalMeter ProctorDataParser.terminalToken terminalBudget :=
  seq_contract (natMeter) (natToken) (fun tag => choose (tag=0) (ret (.empty : Terminal)) (choose (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal))))) (fun tag => choosePlain (tag=0) (retPlain (.empty : Terminal)) (choosePlain (tag=1) (seqPlain (ProctorDataParser.capacityToken) (fun c => retPlain (.capacity c : Terminal))) (choosePlain (tag=2) (seqPlain (listToken (ProctorDataParser.blockToken)) (fun bs => retPlain (.xor bs : Terminal))) (rejectPlain (α := Terminal))))) (1) ((0)+(((capacityBudget)+(0))+(((listBudget (blockBudget))+(0))+(0)))) (nat_contract) (fun tag => choose_contract (tag=0) (ret (.empty : Terminal)) (choose (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal)))) (retPlain (.empty : Terminal)) (choosePlain (tag=1) (seqPlain (ProctorDataParser.capacityToken) (fun c => retPlain (.capacity c : Terminal))) (choosePlain (tag=2) (seqPlain (listToken (ProctorDataParser.blockToken)) (fun bs => retPlain (.xor bs : Terminal))) (rejectPlain (α := Terminal)))) (0) (((capacityBudget)+(0))+(((listBudget (blockBudget))+(0))+(0))) (ret_contract (.empty : Terminal)) (choose_contract (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal))) (seqPlain (ProctorDataParser.capacityToken) (fun c => retPlain (.capacity c : Terminal))) (choosePlain (tag=2) (seqPlain (listToken (ProctorDataParser.blockToken)) (fun bs => retPlain (.xor bs : Terminal))) (rejectPlain (α := Terminal))) ((capacityBudget)+(0)) (((listBudget (blockBudget))+(0))+(0)) (seq_contract (capacityMeter) (ProctorDataParser.capacityToken) (fun c => ret (.capacity c : Terminal)) (fun c => retPlain (.capacity c : Terminal)) (capacityBudget) (0) (capacity_contract) (fun c => ret_contract (.capacity c : Terminal))) (choose_contract (tag=2) (seqMeter (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal)) (seqPlain (listToken (ProctorDataParser.blockToken)) (fun bs => retPlain (.xor bs : Terminal))) (rejectPlain (α := Terminal)) ((listBudget (blockBudget))+(0)) (0) (seq_contract (listMeter (blockMeter)) (listToken (ProctorDataParser.blockToken)) (fun bs => ret (.xor bs : Terminal)) (fun bs => retPlain (.xor bs : Terminal)) (listBudget (blockBudget)) (0) (list_contract (blockMeter) (ProctorDataParser.blockToken) (blockBudget) (block_contract)) (fun bs => ret_contract (.xor bs : Terminal))) (reject_contract (α := Terminal)))))

def proofMeter : ParserMeter Proof := seqMeter (listMeter (listMeter (stepMeter))) (fun bs => seqMeter (boolMeter) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof))))
def proofBudget : Nat := (listBudget (listBudget (stepBudget)))+((1)+((terminalBudget)+(0)))

theorem proof_contract : Contract proofMeter ProctorDataParser.proofToken proofBudget :=
  seq_contract (listMeter (listMeter (stepMeter))) (listToken (listToken (ProctorDataParser.stepToken))) (fun bs => seqMeter (boolMeter) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof)))) (fun bs => seqPlain (boolToken) (fun aug => seqPlain (ProctorDataParser.terminalToken) (fun t => retPlain (⟨bs,aug,t⟩ : Proof)))) (listBudget (listBudget (stepBudget))) ((1)+((terminalBudget)+(0))) (list_contract (listMeter (stepMeter)) (listToken (ProctorDataParser.stepToken)) (listBudget (stepBudget)) (list_contract (stepMeter) (ProctorDataParser.stepToken) (stepBudget) (step_contract))) (fun bs => seq_contract (boolMeter) (boolToken) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof))) (fun aug => seqPlain (ProctorDataParser.terminalToken) (fun t => retPlain (⟨bs,aug,t⟩ : Proof))) (1) ((terminalBudget)+(0)) (bool_contract) (fun aug => seq_contract (terminalMeter) (ProctorDataParser.terminalToken) (fun t => ret (⟨bs,aug,t⟩ : Proof)) (fun t => retPlain (⟨bs,aug,t⟩ : Proof)) (terminalBudget) (0) (terminal_contract) (fun t => ret_contract (⟨bs,aug,t⟩ : Proof))))

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
theorem expected_bound (ts : List Nat) : (expectedMeter ts).2≤expectedBudget :=
  expected_contract.2 ts
theorem envelope_bound (ts : List Nat) : (envelopeMeter ts).2≤envelopeBudget :=
  envelope_contract.2 ts
end ProctorGrammarMeter

#print axioms ProctorGrammarMeter.ret_contract
#print axioms ProctorGrammarMeter.reject_contract
#print axioms ProctorGrammarMeter.nat_contract
#print axioms ProctorGrammarMeter.bool_contract
#print axioms ProctorGrammarMeter.seq_contract
#print axioms ProctorGrammarMeter.list_contract
#print axioms ProctorGrammarMeter.choose_contract
#print axioms ProctorGrammarMeter.literal_contract
#print axioms ProctorGrammarMeter.clause_contract
#print axioms ProctorGrammarMeter.formula_contract
#print axioms ProctorGrammarMeter.ref_contract
#print axioms ProctorGrammarMeter.group_contract
#print axioms ProctorGrammarMeter.capacity_contract
#print axioms ProctorGrammarMeter.block_contract
#print axioms ProctorGrammarMeter.step_contract
#print axioms ProctorGrammarMeter.terminal_contract
#print axioms ProctorGrammarMeter.proof_contract
#print axioms ProctorGrammarMeter.expected_contract
#print axioms ProctorGrammarMeter.envelope_contract
#print axioms ProctorGrammarMeter.expected_refines
#print axioms ProctorGrammarMeter.envelope_refines
#print axioms ProctorGrammarMeter.expected_bound
#print axioms ProctorGrammarMeter.envelope_bound
