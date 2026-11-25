/-! F034 candidate: input-sensitive bounds for the existing complete
token grammar. Weak contracts permit zero-consumption returns; strong
contracts reserve two dispatch units. List closure uses the verified
amortized list theorem. Selected source-level charges only. -/
namespace ProctorAmortizedGrammar
open ProctorHallDeficiency
open ProctorExecutableReplay (Step)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorCapacityDeficiency (Group)
open ProctorXorReplay (Block)
open ProctorUnifiedReplay (Proof Terminal Envelope)
open ProctorParserMeterCompose (ParserMeter seqMeter listMeter natMeter boolMeter)
open ProctorGrammarMeter
open ProctorAmortizedParser (potential Amortized list_amortized nat_amortized all_bound)

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
      change 3+potential vs≤potential vs+64
      rw [Nat.add_comm 3 (potential vs)]
      exact Nat.add_le_add (Nat.le_refl _) (by decide : 3≤64)
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
  seq_amortized (listMeter (refMeter)) (fun ds => seqMeter (listMeter (groupMeter)) (fun gs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate)))) (list_amortized (refMeter) (ref_amortized)) (fun ds => weaken (seqMeter (listMeter (groupMeter)) (fun gs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate)))) (seq_amortized (listMeter (groupMeter)) (fun gs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate))) (list_amortized (groupMeter) (group_amortized)) (fun gs => weaken (seqMeter (listMeter (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate))) (seq_amortized (listMeter (refMeter)) (fun rs => ret (⟨ds,gs,rs⟩ : Certificate)) (list_amortized (refMeter) (ref_amortized)) (fun rs => ret_weak (⟨ds,gs,rs⟩ : Certificate))))))

theorem block_amortized : Amortized blockMeter :=
  seq_amortized (listMeter (natMeter)) (fun vs => seqMeter (boolMeter) (fun rhs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block)))) (list_amortized (natMeter) (nat_amortized)) (fun vs => weaken (seqMeter (boolMeter) (fun rhs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block)))) (seq_amortized (boolMeter) (fun rhs => seqMeter (listMeter (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block))) (bool_amortized) (fun rhs => weaken (seqMeter (listMeter (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block))) (seq_amortized (listMeter (refMeter)) (fun rs => ret (⟨vs,rhs,rs⟩ : Block)) (list_amortized (refMeter) (ref_amortized)) (fun rs => ret_weak (⟨vs,rhs,rs⟩ : Block))))))

theorem step_amortized : Amortized stepMeter :=
  seq_amortized (natMeter) (fun a => seqMeter (natMeter) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))))) (nat_amortized) (fun a => weaken (seqMeter (natMeter) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))))) (seq_amortized (natMeter) (fun b => seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step)))) (nat_amortized) (fun b => weaken (seqMeter (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step)))) (seq_amortized (natMeter) (fun p => seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))) (nat_amortized) (fun p => weaken (seqMeter (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step))) (seq_amortized (clauseMeter) (fun tail => ret (⟨a,b,p,tail⟩ : Step)) (clause_amortized) (fun tail => ret_weak (⟨a,b,p,tail⟩ : Step))))))))

theorem terminal_amortized : Amortized terminalMeter :=
  seq_amortized (natMeter) (fun tag => choose (tag=0) (ret (.empty : Terminal)) (choose (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal))))) (nat_amortized) (fun tag => choose_weak (tag=0) (ret (.empty : Terminal)) (choose (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal)))) (ret_weak (.empty : Terminal)) (choose_weak (tag=1) (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (choose (tag=2) (seqMeter (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal))) (weaken (seqMeter (capacityMeter) (fun c => ret (.capacity c : Terminal))) (seq_amortized (capacityMeter) (fun c => ret (.capacity c : Terminal)) (capacity_amortized) (fun c => ret_weak (.capacity c : Terminal)))) (choose_weak (tag=2) (seqMeter (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (reject (α := Terminal)) (weaken (seqMeter (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal))) (seq_amortized (listMeter (blockMeter)) (fun bs => ret (.xor bs : Terminal)) (list_amortized (blockMeter) (block_amortized)) (fun bs => ret_weak (.xor bs : Terminal)))) (reject_weak (α := Terminal)))))

theorem proof_amortized : Amortized proofMeter :=
  seq_amortized (listMeter (listMeter (stepMeter))) (fun bs => seqMeter (boolMeter) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof)))) (list_amortized (listMeter (stepMeter)) (list_amortized (stepMeter) (step_amortized))) (fun bs => weaken (seqMeter (boolMeter) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof)))) (seq_amortized (boolMeter) (fun aug => seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof))) (bool_amortized) (fun aug => weaken (seqMeter (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof))) (seq_amortized (terminalMeter) (fun t => ret (⟨bs,aug,t⟩ : Proof)) (terminal_amortized) (fun t => ret_weak (⟨bs,aug,t⟩ : Proof))))))

theorem expected_amortized : Amortized expectedMeter :=
  seq_amortized (natMeter) (fun magic => choose (magic=3401) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)))) (reject (α := Nat × Formula))) (nat_amortized) (fun magic => choose_weak (magic=3401) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)))) (reject (α := Nat × Formula)) (weaken (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)))) (seq_amortized (natMeter) (fun n => seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula))) (nat_amortized) (fun n => weaken (seqMeter (formulaMeter) (fun f => ret ((n,f) : Nat × Formula))) (seq_amortized (formulaMeter) (fun f => ret ((n,f) : Nat × Formula)) (formula_amortized) (fun f => ret_weak ((n,f) : Nat × Formula)))))) (reject_weak (α := Nat × Formula)))

theorem envelope_amortized : Amortized envelopeMeter :=
  seq_amortized (natMeter) (fun magic => choose (magic=3402) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))))) (reject (α := Envelope))) (nat_amortized) (fun magic => choose_weak (magic=3402) (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))))) (reject (α := Envelope)) (weaken (seqMeter (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))))) (seq_amortized (natMeter) (fun n => seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope)))) (nat_amortized) (fun n => weaken (seqMeter (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope)))) (seq_amortized (formulaMeter) (fun f => seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))) (formula_amortized) (fun f => weaken (seqMeter (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope))) (seq_amortized (proofMeter) (fun p => ret (⟨n,f,p⟩ : Envelope)) (proof_amortized) (fun p => ret_weak (⟨n,f,p⟩ : Envelope)))))))) (reject_weak (α := Envelope)))

theorem expected_bound (ts : List Nat) : (expectedMeter ts).2≤64*ts.length+3 :=
  all_bound _ expected_amortized ts

theorem envelope_bound (ts : List Nat) : (envelopeMeter ts).2≤64*ts.length+3 :=
  all_bound _ envelope_amortized ts

end ProctorAmortizedGrammar

#print axioms ProctorAmortizedGrammar.weaken
#print axioms ProctorAmortizedGrammar.ret_weak
#print axioms ProctorAmortizedGrammar.reject_weak
#print axioms ProctorAmortizedGrammar.bool_amortized
#print axioms ProctorAmortizedGrammar.seq_amortized
#print axioms ProctorAmortizedGrammar.choose_weak
#print axioms ProctorAmortizedGrammar.literal_amortized
#print axioms ProctorAmortizedGrammar.clause_amortized
#print axioms ProctorAmortizedGrammar.formula_amortized
#print axioms ProctorAmortizedGrammar.ref_amortized
#print axioms ProctorAmortizedGrammar.group_amortized
#print axioms ProctorAmortizedGrammar.capacity_amortized
#print axioms ProctorAmortizedGrammar.block_amortized
#print axioms ProctorAmortizedGrammar.step_amortized
#print axioms ProctorAmortizedGrammar.terminal_amortized
#print axioms ProctorAmortizedGrammar.proof_amortized
#print axioms ProctorAmortizedGrammar.expected_amortized
#print axioms ProctorAmortizedGrammar.envelope_amortized
#print axioms ProctorAmortizedGrammar.expected_bound
#print axioms ProctorAmortizedGrammar.envelope_bound
