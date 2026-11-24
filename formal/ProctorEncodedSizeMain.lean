/-! Static check of the global selected-charge polynomial. -/
namespace ProctorEncodedSizeMain
open ProctorHallDeficiency
open ProctorEncodedSize
open ProctorUnifiedMeter (boundBudget boundMeter)

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def run (dir : String) : IO UInt32 := do
  let mut accepted : Nat := 0
  for i in List.range 53 do
    let stem := dir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnfdata")
    let b ← readData (stem ++ ".proofdata")
    match ProctorDataParser.decodeExpected a,ProctorDataParser.decodeEnvelope b with
    | some (n,f),some e =>
      let s := size n f e
      let m := boundMeter n f e
      let limit := globalUnit (cap n f e)
      if s > a.length+b.length || boundBudget f e > limit || m.2 > limit ||
          m.1 != ProctorUnifiedReplay.boundCheck n f e then
        throw (IO.userError ("global size bound mismatch " ++ toString i))
      if m.1 then accepted := accepted+1
      IO.println ("F034_ENCODED_SIZE_CASE " ++ toString i ++ " tokens=" ++
        toString s ++ " selected=" ++ toString m.2 ++ " polynomial=" ++ toString limit)
    | _,_ => throw (IO.userError "typed fixture parse failure")
  if accepted != 19 then throw (IO.userError "acceptance count mismatch")
  IO.println "F034_ENCODED_SIZE_OK cases=53 accepted=19 rejected=34"
  pure 0
end ProctorEncodedSizeMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorEncodedSizeMain.run dir
  | _ => pure 2
