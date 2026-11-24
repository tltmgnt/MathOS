/-! Executable grammar differential checks on actual expected files.
This is static test code; inputs remain raw data. -/
open ProctorDataParser ProctorWireRoundtrip

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] =>
    let mut decoded : Nat := 0
    for i in List.range 53 do
      let file := dir ++ "/" ++ toString i ++ ".cnfdata"
      let bytes ← IO.FS.readBinFile (System.FilePath.mk file)
      let raw := bytes.data.toList.map (fun b => b.toNat)
      match decodeExpected raw, tokenize raw with
      | some (n,f), some ts =>
        if ts != encExpected n f then
          throw (IO.userError ("token roundtrip mismatch " ++ toString i))
        decoded := decoded+1
      | _, _ => throw (IO.userError "expected fixture parse failure")
    if decoded != 53 then
      throw (IO.userError "roundtrip fixture count mismatch")
    IO.println "F034_WIRE_ROUNDTRIP_OK expected=53"
    pure 0
  | _ => pure 2
