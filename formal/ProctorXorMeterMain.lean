/-! Static tests on previously exported raw data, not generated Lean. -/
namespace ProctorXorMeterMain
open ProctorHallDeficiency
open ProctorXorReplay (Block xorCheck)
open ProctorXorMeter

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def run (dir : String) : IO UInt32 := do
  let f : Formula := [[(1,false)]]
  let b : Block := ⟨[1],false,[⟨0,[(1,false)]⟩]⟩
  if toggleMeter 2 [1,2,3] != ([1,3],2) ||
      toggleMeter 4 [1,2,3] != ([1,2,3,4],3) ||
      combineMeter [1,2] [2,3] != ([3,1],2) ||
      patternsMeter [1,2] (fun _ => (true,1)) != (true,7) ||
      patternMeter b [(1,false)] != (true,5) ||
      blockMeter f ⟨[1,2,3,4,5,6],false,[]⟩ != (false,1) then
    throw (IO.userError "XOR meter hand control mismatch")
  let mut count : Nat := 0
  let mut total : Nat := 0
  let mut accepted : Nat := 0
  for i in List.range 53 do
    let stem := dir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnfdata")
    let p ← readData (stem ++ ".proofdata")
    match ProctorDataParser.decodeExpected a,ProctorDataParser.decodeEnvelope p with
    | some (_,expected),some e =>
      match e.proof.terminal with
      | .xor bs =>
        let target := ProctorUnifiedReplay.target expected e.proof
        let m := xorMeter target bs
        let budget := xorBudget target bs
        if m.1 != xorCheck target bs || m.2 > budget then
          throw (IO.userError ("XOR meter fixture mismatch " ++ toString i))
        count := count+1
        total := total+m.2
        if m.1 then accepted := accepted+1
        IO.println ("F034_XOR_METER_CASE " ++ toString i ++ " count=" ++
          toString m.2 ++ " budget=" ++ toString budget)
      | _ => pure ()
    | _,_ => throw (IO.userError "typed fixture parse failure")
  if count != 21 then
    throw (IO.userError ("XOR fixture count mismatch " ++ toString count))
  IO.println ("F034_XOR_METER_TOTAL count=" ++ toString total ++
    " terminal_accept=" ++ toString accepted)
  IO.println "F034_XOR_METER_OK cases=21 hand_controls=6"
  pure 0
end ProctorXorMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorXorMeterMain.run dir
  | _ => pure 2
