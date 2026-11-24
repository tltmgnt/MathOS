/-! Static capacity meter fixture checks. -/
namespace ProctorCapacityMeterMain
open ProctorHallDeficiency
open ProctorCapacityReplay (RefRow capacityCheck)
open ProctorCapacityDeficiency (Group)
open ProctorCapacityMeter

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def run (dir : String) : IO UInt32 := do
  let ys : Clause := [(1,true),(2,true)]
  let rs : List RefRow := [⟨2,[(1,false),(2,false)]⟩]
  let ds : List RefRow := [⟨0,[(1,true)]⟩,⟨1,[(2,true)]⟩]
  let gs : List Group := [⟨ys,1⟩]
  if distinctMeter ys != (true,1) ||
      wordsMeter ys 2 (fun _ => (true,1)) != (true,10) ||
      conflictMeter rs ys != (true,11) ||
      differentMeter ds 0 1 != (true,7) ||
      coverageMeter [⟨0,[(1,true)]⟩] gs != (true,4) ||
      (groupMeter rs ⟨ys,3⟩) != (false,1) then
    throw (IO.userError "capacity meter hand control mismatch")
  let mut count : Nat := 0
  let mut total : Nat := 0
  let mut accepted : Nat := 0
  for i in List.range 53 do
    let stem := dir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnfdata")
    let b ← readData (stem ++ ".proofdata")
    match ProctorDataParser.decodeExpected a, ProctorDataParser.decodeEnvelope b with
    | some (_,expected),some e =>
      match e.proof.terminal with
      | .capacity c =>
        let target := ProctorUnifiedReplay.target expected e.proof
        let m := capacityMeter target c
        let budget := capacityBudget target c
        if m.1 != capacityCheck target c || m.2 > budget then
          throw (IO.userError ("capacity meter fixture mismatch " ++ toString i))
        total := total+m.2
        count := count+1
        if m.1 then accepted := accepted+1
        IO.println ("F034_CAPACITY_METER_CASE " ++ toString i ++
          " count=" ++ toString m.2 ++ " budget=" ++ toString budget)
      | _ => pure ()
    | _,_ => throw (IO.userError "typed fixture parse failure")
  if count != 24 then
    throw (IO.userError ("capacity fixture count mismatch " ++ toString count))
  IO.println ("F034_CAPACITY_METER_TOTAL count=" ++ toString total ++
    " terminal_accept=" ++ toString accepted)
  IO.println "F034_CAPACITY_METER_OK cases=24 hand_controls=6"
  pure 0

end ProctorCapacityMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorCapacityMeterMain.run dir
  | _ => pure 2
