namespace ProctorEndToEndSelectedLedgerMain
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope Proof Terminal)
open ProctorUnifiedResourceLedger
open ProctorEndToEndSelectedLedger
open ProctorFrontendResourceLedger (Resources pairBudget)
open ProctorWireRoundtrip (encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)

def bytes (ts : List Nat) : List Nat :=
  ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])

def run : IO UInt32 := do
  let f : Formula := [[(1,true)],[(1,false)]]
  let g : Formula := [[(1,true)],[(2,true)],[(1,false),(2,false)]]
  let c : ProctorCapacityReplay.Certificate :=
    ⟨[⟨0,[(1,true)]⟩,⟨1,[(2,true)]⟩],[⟨[(1,true),(2,true)],1⟩],[⟨2,[(1,false),(2,false)]⟩]⟩
  let x : List ProctorXorReplay.Block :=
    [⟨[1],true,[⟨0,[(1,true)]⟩]⟩,⟨[1],false,[⟨1,[(1,false)]⟩]⟩]
  let v := 10^128-1
  let wf : Formula := [[(v,true)],[(v,false)]]
  let wx : List ProctorXorReplay.Block :=
    [⟨[v],true,[⟨0,[(v,true)]⟩]⟩,⟨[v],false,[⟨1,[(v,false)]⟩]⟩]
  let positives : List Envelope :=
    [⟨1,[[]],⟨[],false,.empty⟩⟩,
      ⟨1,f,⟨[[⟨0,1,1,[]⟩]],false,.empty⟩⟩,
      ⟨1,f,⟨[[⟨0,1,1,[]⟩]],true,.empty⟩⟩,
      ⟨2,g,⟨[],false,.capacity c⟩⟩,
      ⟨1,f,⟨[],false,.xor x⟩⟩,
      ⟨v,wf,⟨[],false,.xor wx⟩⟩]
  let negatives : List Envelope :=
    [⟨1,f,⟨[],false,.empty⟩⟩,
      ⟨1,f,⟨[[⟨0,2,1,[]⟩]],false,.empty⟩⟩,
      ⟨1,f,⟨[],false,.xor [⟨[1],true,[⟨1,[(1,true)]⟩]⟩]⟩⟩,
      ⟨2,g,⟨[],false,.capacity ⟨c.demands,c.groups,[]⟩⟩⟩,
      ⟨0,[[(0,true)]],⟨[],false,.empty⟩⟩]
  let es := positives++negatives
  for e in positives do
    let a := bytes (encExpected e.variableBound e.original)
    let b := bytes (encEnvelope e)
    if (meter a b).accepted != true || ProctorDataParser.checkBytes a b != true then
      throw (IO.userError "unified positive fixture rejected")
  for e in negatives do
    let a := bytes (encExpected e.variableBound e.original)
    let b := bytes (encEnvelope e)
    if (meter a b).accepted != false || ProctorDataParser.checkBytes a b != false then
      throw (IO.userError "unified negative fixture accepted")
  let as' := [[],[10],[255]] ++ es.map (fun e => bytes (encExpected e.variableBound e.original))
  let bs' := [[],[10],[255]] ++ es.map (fun e => bytes (encEnvelope e))
  let mut pairs : Nat := 0
  for a in as' do
    for b in bs' do
      if (meter a b).accepted != ProctorDataParser.checkBytes a b then
        throw (IO.userError "unified byte checker disagreement")
      let m := meter a b
      let p := pairBudget (a.length+b.length)
      let v := m.frontend
      if v.gates>p.gates || v.narrowVisits>p.narrowVisits ||
          v.prepassVisits>p.prepassVisits || v.paddingVisits>p.paddingVisits ||
          v.encoderEvents>p.encoderEvents || v.emissionEvents>p.emissionEvents ||
          v.grammarEvents>p.grammarEvents || m.lookupVisits>bytesVisitBudget a b ||
          m.comparisonGates>bytesGateBudget a b then
        throw (IO.userError "unified byte resource ledger exceeded")
      pairs := pairs+1
  for e in es do
    let m := checkerMeter e.variableBound e.original e
    if m.2.1>checkerVisitBudget e.original e ||
        m.2.2>checkerGateBudget e.original e then
      throw (IO.userError "unified checker ledger exceeded")
  if pairs != 196 then throw (IO.userError "control count mismatch")
  IO.println "F034_END_TO_END_SELECTED_LEDGER_OK pairs=196 positive=6 negative=5 ledgers=11"
  pure 0
end ProctorEndToEndSelectedLedgerMain

def main : IO UInt32 := ProctorEndToEndSelectedLedgerMain.run
