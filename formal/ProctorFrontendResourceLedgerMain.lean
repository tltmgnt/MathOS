namespace ProctorFrontendResourceLedgerMain
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope)
open ProctorFrontendResourceLedger
open ProctorWireRoundtrip (encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)

def bytes (ts : List Nat) : List Nat :=
  ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])

def strings : Nat → List (List Nat)
  | 0 => [[]]
  | k+1 => [10,48,49,57,255].flatMap (fun c => (strings k).map (fun xs => c::xs))

def fits (a b : Resources) : Bool :=
  a.gates≤b.gates && a.narrowVisits≤b.narrowVisits &&
  a.prepassVisits≤b.prepassVisits && a.paddingVisits≤b.paddingVisits &&
  a.encoderEvents≤b.encoderEvents && a.emissionEvents≤b.emissionEvents &&
  a.grammarEvents≤b.grammarEvents

def run : IO UInt32 := do
  let small := (List.range 4).flatMap strings
  for a in small do
    let x := expectedMeter a
    let y := envelopeMeter a
    if x.1.isSome != (ProctorFuelFreeDecoder.decodeExpected a).isSome ||
        y.1.isSome != (ProctorFuelFreeDecoder.decodeEnvelope a).isSome ||
        !fits x.2 (budget a.length) || !fits y.2 (budget a.length) then
      throw (IO.userError "front-end small fixture mismatch")
  let v := 10^128-1
  let f : Formula := [[(1,true)],[(1,false)]]
  let wide : Formula := [[(v,true)],[(v,false)]]
  let e : Envelope := ⟨1,f,⟨[[⟨0,1,1,[]⟩]],false,.empty⟩⟩
  let ew : Envelope := ⟨v,wide,⟨[[⟨0,1,v,[]⟩]],true,.empty⟩⟩
  let as' := [[],[10],[255],bytes (encExpected 1 f),bytes (encExpected v wide),
    bytes (encExpected 1 f)++[48,10],bytes [3401,1,100001]]
  let bs' := [[],[10],[255],bytes (encEnvelope e),bytes (encEnvelope ew),
    bytes (encEnvelope e)++[48,10],bytes [3402,1,100001]]
  if !(expectedMeter (bytes (encExpected 1 f))).1.isSome ||
      !(expectedMeter (bytes (encExpected v wide))).1.isSome ||
      !(envelopeMeter (bytes (encEnvelope e))).1.isSome ||
      !(envelopeMeter (bytes (encEnvelope ew))).1.isSome then
    throw (IO.userError "front-end positive fixture rejected")
  let mut pairs : Nat := 0
  for a in as' do
    for b in bs' do
      let p := pairMeter a b
      if p.1.1.isSome != (ProctorFuelFreeDecoder.decodeExpected a).isSome ||
          p.1.2.isSome != (ProctorFuelFreeDecoder.decodeEnvelope b).isSome ||
          !fits p.2 (pairBudget (a.length+b.length)) ||
          (budget a.length).add (budget b.length) != pairBudget (a.length+b.length) then
        throw (IO.userError "front-end pair mismatch")
      pairs := pairs+1
  if small.length != 156 || pairs != 49 then throw (IO.userError "control count mismatch")
  IO.println "F034_FRONTEND_RESOURCE_LEDGER_OK small=156 pairs=49 positive=4"
  pure 0
end ProctorFrontendResourceLedgerMain

def main : IO UInt32 := ProctorFrontendResourceLedgerMain.run
