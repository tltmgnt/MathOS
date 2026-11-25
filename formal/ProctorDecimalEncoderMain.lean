namespace ProctorDecimalEncoderMain
open ProctorDecimalEncoder (encode)
open ProctorUnboundedCodec (tokenize decodeExpected decodeEnvelope checkBytes)
open ProctorHallDeficiency
open ProctorWireRoundtrip (encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)
open ProctorUnifiedReplay (Proof Envelope)
def oracle (ns : List Nat) : List Nat :=
  ns.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])
def check (ns : List Nat) : IO Unit := do
  let bs := encode ns
  if bs != oracle ns || tokenize bs != some ns then
    throw (IO.userError "decimal encoder disagreement")
def run : IO UInt32 := do
  for n in List.range 1000 do
    check [n]
  for k in List.range 129 do
    let n := 10^k
    check [n-1,n,n+1]
  check []
  check [0,0,10,100,1000,3401,3402,10^512]
  let big := 10^128
  let f : Formula := [[(big,true)],[(big,false)]]
  let e := encode (encExpected big f)
  match ProctorTwoCNFModel.discover big f with
  | none => throw (IO.userError "missing proof")
  | some p =>
    if !checkBytes e (encode (encEnvelope ⟨big,f,p⟩)) then
      throw (IO.userError "proof bytes rejected")
  let empty : Formula := [[]]
  let p : Proof := ⟨[],false,.empty⟩
  if !checkBytes (encode (encExpected 0 empty)) (encode (encEnvelope ⟨0,empty,p⟩)) then
    throw (IO.userError "zero-bound proof bytes rejected")
  for bad in [[48,48,10],[49],[10],[45,49,10]] do
    if (tokenize bad).isSome then throw (IO.userError "noncanonical bytes accepted")
  IO.println "F035_DECIMAL_ENCODER_OK singletons=1000 boundaries=129 lists=2 proofs=2 rejection=4"
  pure 0
end ProctorDecimalEncoderMain
def main : IO UInt32 := ProctorDecimalEncoderMain.run
