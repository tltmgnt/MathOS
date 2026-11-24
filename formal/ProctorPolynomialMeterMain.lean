/-! Actual static polynomial budget checks on existing raw fixtures. -/
namespace ProctorPolynomialMeterMain
open ProctorHallDeficiency
open ProctorPolynomialMeter
open ProctorCapacityMeter (wordsBudget)
open ProctorChainMeter (chainBudget chainMeter)
open ProctorXorMeter (sumBudget sumMeter)

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def run (dir : String) : IO UInt32 := do
  let xs : Clause := [(1,true),(2,true),(3,true),(4,true)]
  if wordsBudget xs 3 (fun _ => 2) != 212 || wordUnit 4 3 2 != 212 then
    throw (IO.userError "ordered word budget hand control mismatch")
  let mut xorCount : Nat := 0
  for i in List.range 53 do
    let stem := dir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnfdata")
    let b ← readData (stem ++ ".proofdata")
    match ProctorDataParser.decodeExpected a,ProctorDataParser.decodeEnvelope b with
    | some (_,f),some e =>
      let bs := e.proof.batches
      let B := chainMass f bs
      let limit := B*stepUnit B
      if chainSteps bs > B || chainBudget f bs > limit ||
          (chainMeter f bs).2 > limit then
        throw (IO.userError ("chain polynomial mismatch " ++ toString i))
      match e.proof.terminal with
      | .xor blocks =>
        let u := supportMass blocks
        if sumBudget blocks > u*u || (sumMeter blocks).2 > u*u then
          throw (IO.userError ("sum polynomial mismatch " ++ toString i))
        xorCount := xorCount+1
      | _ => pure ()
    | _,_ => throw (IO.userError "typed fixture parse failure")
  if xorCount != 21 then throw (IO.userError "XOR fixture count mismatch")
  IO.println "F034_POLYNOMIAL_METER_OK chains=53 xor_sums=21 word_controls=1"
  pure 0
end ProctorPolynomialMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorPolynomialMeterMain.run dir
  | _ => pure 2
