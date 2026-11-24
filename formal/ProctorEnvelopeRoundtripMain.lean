/-! Static data-only fixture check for the full envelope token encoder. -/
open ProctorDataParser ProctorEnvelopeRoundtrip

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] =>
    let mut decoded : Nat := 0
    for i in List.range 53 do
      let file := dir ++ "/" ++ toString i ++ ".proofdata"
      let bytes ← IO.FS.readBinFile (System.FilePath.mk file)
      let raw := bytes.data.toList.map (fun b => b.toNat)
      match decodeEnvelope raw, tokenize raw with
      | some e, some ts =>
        if ts != encEnvelope e then
          throw (IO.userError ("envelope roundtrip mismatch " ++ toString i))
        decoded := decoded+1
      | _, _ => throw (IO.userError "expected envelope syntax parse failure")
    if decoded != 53 then
      throw (IO.userError "roundtrip fixture count mismatch")
    IO.println "F034_ENVELOPE_ROUNDTRIP_OK envelopes=53"
    pure 0
  | _ => pure 2
