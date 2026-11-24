/-! Static successful-decoding converse tests, including rejects. -/
namespace ProctorParserConsumptionMain
open ProctorDataParser
open ProctorWireRoundtrip (encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)
open ProctorParserConsumption

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def run (dir : String) : IO UInt32 := do
  let mut pairs : Nat := 0
  let mut accepted : Nat := 0
  for i in List.range 67 do
    let stem := dir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnfdata")
    let b ← readData (stem ++ ".proofdata")
    match decodeExpected a with
    | none => pure ()
    | some (n,f) =>
      if tokenize a != some (encExpected n f) || (encExpected n f).length>a.length then
        throw (IO.userError ("expected consumption mismatch " ++ toString i))
    match decodeEnvelope b with
    | none => pure ()
    | some e =>
      if tokenize b != some (encEnvelope e) || (encEnvelope e).length>b.length then
        throw (IO.userError ("envelope consumption mismatch " ++ toString i))
    match decodeExpected a,decodeEnvelope b with
    | some (n,f),some e =>
      let m := ProctorUnifiedMeter.boundMeter n f e
      if m.2>ProctorEncodedSize.globalUnit (byteCap a b) ||
          m.1 != checkBytes a b then
        throw (IO.userError ("byte budget mismatch " ++ toString i))
      pairs := pairs+1
      if m.1 then accepted := accepted+1
    | _,_ => pure ()
  if pairs < 53 || accepted != 19 then
    throw (IO.userError ("unexpected counts " ++ toString pairs ++ "/" ++ toString accepted))
  IO.println ("F034_CONSUMPTION_PAIRS " ++ toString pairs)
  IO.println "F034_PARSER_CONSUMPTION_OK cases=67 accepted=19"
  pure 0
end ProctorParserConsumptionMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorParserConsumptionMain.run dir
  | _ => pure 2
