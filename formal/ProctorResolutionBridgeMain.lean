namespace ProctorResolutionBridgeMain
open ProctorHallDeficiency
open ProctorExecutableReplay (Step)
open ProctorUnifiedReplay (Envelope Proof)
open ProctorWireRoundtrip (encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)

def bytes (ts : List Nat) : List Nat :=
  ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])

def run : IO UInt32 := do
  let f : Formula := [[(1,true),(2,true)],[(1,false)],[(2,false)]]
  let ss : List Step := [⟨0,1,1,[(2,true)]⟩,⟨0,3,2,[]⟩]
  let p : Proof := ⟨ProctorResolutionBridge.compile 1 f ss,false,.empty⟩
  let e : Envelope := ⟨2,f,p⟩
  if ProctorResolutionBridge.sequentialCheck f ss != true ||
      ProctorUnifiedReplay.check f p != true then
    throw (IO.userError "compiled sequential refutation rejected")
  let bad : Proof := ⟨ProctorResolutionBridge.compile 1 f [⟨0,99,1,[]⟩],false,.empty⟩
  if ProctorUnifiedReplay.check f bad != false then
    throw (IO.userError "bad compiled reference accepted")
  let v := 10^128
  let wf : Formula := [[(v,true)],[(v,false)]]
  let we : Envelope := ⟨v,wf,⟨[[⟨0,1,v,[]⟩]],false,.empty⟩⟩
  let g : Formula := [[(1,true)],[(2,true)],[(1,false),(2,false)]]
  let ce : Envelope := ⟨2,g,⟨[],false,.capacity
    ⟨[⟨0,[(1,true)]⟩,⟨1,[(2,true)]⟩],[⟨[(1,true),(2,true)],1⟩],[⟨2,[(1,false),(2,false)]⟩]⟩⟩⟩
  let xf : Formula := [[(1,true)],[(1,false)]]
  let xe : Envelope := ⟨1,xf,⟨[],false,.xor
    [⟨[1],true,[⟨0,[(1,true)]⟩]⟩,⟨[1],false,[⟨1,[(1,false)]⟩]⟩]⟩⟩
  for z in [e,we,ce,xe] do
    let a := bytes (encExpected z.variableBound z.original)
    let b := bytes (encEnvelope z)
    if ProctorUnboundedCodec.checkBytes a b != true then
      throw (IO.userError "unbounded positive fixture rejected")
  if ProctorDataParser.checkBytes (bytes (encExpected v wf)) (bytes (encEnvelope we)) != false then
    throw (IO.userError "legacy digit cap not detected")
  let ts := 3401::1::100001::List.replicate 100001 0
  match ProctorUnboundedCodec.expectedToken ts with
  | some ((_,rows),[]) =>
    if rows.length != 100001 then throw (IO.userError "unbounded list truncated")
  | _ => throw (IO.userError "unbounded list rejected")
  if (ProctorDataParser.expectedToken ts).isSome then
    throw (IO.userError "legacy list cap not detected")
  let mut invalid : Nat := 0
  for a in [[],[10],[48,48,10],[49],[255]] do
    if ProctorUnboundedCodec.checkBytes a (bytes (encEnvelope e)) then
      throw (IO.userError "malformed expected input accepted")
    invalid := invalid+1
  if ProctorResolutionBridge.decideUnsat (fun _ => some p) f != true ||
      ProctorResolutionBridge.decideUnsat (fun _ => none) f != false then
    throw (IO.userError "generator decision adapter mismatch")
  if invalid != 5 then throw (IO.userError "count mismatch")
  IO.println "F035_RESOLUTION_BRIDGE_OK sequential=2 positives=4 digit=1 list=1 malformed=5 adapter=2"
  pure 0
end ProctorResolutionBridgeMain

def main : IO UInt32 := ProctorResolutionBridgeMain.run
