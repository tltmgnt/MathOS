/-! Static validation of unified selected charges on raw fixtures. -/
namespace ProctorUnifiedMeterMain
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope boundCheck)
open ProctorUnifiedMeter

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def run (dir : String) : IO UInt32 := do
  let f : Formula := [[]]
  let e : Envelope := ⟨0,f,⟨[],false,.empty⟩⟩
  if formulaMeter f f != (true,3) ||
      formulaMeter f [] != (false,1) ||
      clauseMeter 2 [(1,true),(2,false)] != (true,6) ||
      boundMeter 0 f e != (true,6) then
    throw (IO.userError "unified meter hand control mismatch")
  let mut accepted : Nat := 0
  let mut total : Nat := 0
  let mut budgetTotal : Nat := 0
  for i in List.range 53 do
    let stem := dir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnfdata")
    let b ← readData (stem ++ ".proofdata")
    let verdict ← IO.FS.readFile (System.FilePath.mk (stem ++ ".verdict"))
    match ProctorDataParser.decodeExpected a,ProctorDataParser.decodeEnvelope b with
    | some (n,expected),some env =>
      let m := boundMeter n expected env
      let budget := boundBudget expected env
      if m.1 != boundCheck n expected env || m.2 > budget ||
          verdict != (if m.1 then "1\n" else "0\n") then
        throw (IO.userError ("unified meter fixture mismatch " ++ toString i))
      let size := (a.length+b.length)+1
      if budget > 256*size*size*size*size then
        throw (IO.userError ("analytical budget envelope exceeded " ++ toString i))
      if m.1 then accepted := accepted+1
      total := total+m.2
      budgetTotal := budgetTotal+budget
      IO.println ("F034_UNIFIED_METER_CASE " ++ toString i ++ " count=" ++
        toString m.2 ++ " budget=" ++ toString budget)
    | _,_ => throw (IO.userError "typed fixture parse failure")
  if accepted != 19 then throw (IO.userError "unified meter acceptance count")
  IO.println ("F034_UNIFIED_METER_TOTAL count=" ++ toString total ++
    " budget=" ++ toString budgetTotal)
  IO.println "F034_UNIFIED_METER_OK cases=53 accepted=19 rejected=34 hand_controls=4"
  pure 0
end ProctorUnifiedMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorUnifiedMeterMain.run dir
  | _ => pure 2
