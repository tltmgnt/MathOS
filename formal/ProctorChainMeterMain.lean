/-! Static checks of metered chain and indexed references on raw
data fixtures, including semantically rejected certificates. -/
namespace ProctorChainMeterMain
open ProctorHallDeficiency
open ProctorExecutableReplay
open ProctorCapacityReplay (RefRow refCheck every)
open ProctorUnifiedReplay (Terminal)
open ProctorChainMeter

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def refsOf : Terminal → List RefRow
  | .empty => []
  | .capacity c => c.demands ++ c.conflicts
  | .xor bs => bs.flatMap (fun b => b.refs)

def run (dir : String) : IO UInt32 := do
  let f : Formula := [[(1,true),(2,true)],[(1,false),(2,true)]]
  let s : Step := ⟨0,1,1,[(2,true)]⟩
  let bad : Step := ⟨99,0,1,[(2,true)]⟩
  let r : RefRow := ⟨1,[(1,false),(2,true)]⟩
  let wrong : RefRow := ⟨0,[(1,false)]⟩
  let missing : RefRow := ⟨99,[]⟩
  if stepMeter f s != (true,9) || (stepMeter f bad).1 ||
      refMeter f r != (true,5) || refMeter f wrong != (false,2) ||
      refMeter f missing != (false,2) then
    throw (IO.userError "meter hand-count mismatch")
  let mut chainTotal : Nat := 0
  let mut refTotal : Nat := 0
  let mut count : Nat := 0
  for i in List.range 53 do
    let stem := dir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnfdata")
    let b ← readData (stem ++ ".proofdata")
    match ProctorDataParser.decodeExpected a, ProctorDataParser.decodeEnvelope b with
    | some (_,expected), some e =>
      let cm := chainMeter expected e.proof.batches
      let target := ProctorUnifiedReplay.target expected e.proof
      let refs := refsOf e.proof.terminal
      let rm := refsMeter target refs
      if cm.1 != chainCheck expected e.proof.batches ||
          cm.2 > chainBudget expected e.proof.batches ||
          rm.1 != every (refCheck target) refs ||
          rm.2 > refsBudget target refs then
        throw (IO.userError ("meter fixture mismatch " ++ toString i))
      chainTotal := chainTotal+cm.2
      refTotal := refTotal+rm.2
      count := count+1
      IO.println ("F034_METER_CASE " ++ toString i ++ " chain=" ++
        toString cm.2 ++ " refs=" ++ toString rm.2)
    | _,_ => throw (IO.userError "typed fixture parse failure")
  if count != 53 then
    throw (IO.userError "fixture count mismatch")
  IO.println ("F034_CHAIN_METER_TOTAL chain=" ++ toString chainTotal ++ " refs=" ++ toString refTotal)
  IO.println "F034_CHAIN_METER_OK cases=53 hand_controls=5"
  pure 0

end ProctorChainMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorChainMeterMain.run dir
  | _ => pure 2
