/-! Static validation on the previously emitted typed fixtures. -/
namespace ProctorTerminalPolynomialMain
open ProctorHallDeficiency
open ProctorTerminalPolynomial
open ProctorPolynomialMeter (formulaMass supportMass)
open ProctorCapacityMeter (capacityBudget capacityMeter)
open ProctorXorMeter (xorBudget xorMeter)

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def run (dir : String) : IO UInt32 := do
  let mut nc : Nat := 0
  let mut nx : Nat := 0
  for i in List.range 53 do
    let stem := dir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnfdata")
    let b ← readData (stem ++ ".proofdata")
    match ProctorDataParser.decodeExpected a,ProctorDataParser.decodeEnvelope b with
    | some (_,f),some e =>
      let t := ProctorUnifiedReplay.target f e.proof
      match e.proof.terminal with
      | .capacity c =>
        let B := 1+formulaMass t+mass rowWeight c.demands+
          mass rowWeight c.conflicts+mass groupWeight c.groups
        if capacityBudget t c>capacityUnit B || (capacityMeter t c).2>capacityUnit B then
          throw (IO.userError ("capacity polynomial mismatch " ++ toString i))
        nc := nc+1
      | .xor bs =>
        let B := 1+formulaMass t+mass blockWeight bs+supportMass bs
        if xorBudget t bs>xorUnit B || (xorMeter t bs).2>xorUnit B then
          throw (IO.userError ("XOR polynomial mismatch " ++ toString i))
        nx := nx+1
      | .empty => pure ()
    | _,_ => throw (IO.userError "typed fixture parse failure")
  if nc != 24 || nx != 21 then throw (IO.userError "terminal count mismatch")
  IO.println "F034_TERMINAL_POLYNOMIAL_OK capacity=24 xor=21"
  pure 0
end ProctorTerminalPolynomialMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorTerminalPolynomialMain.run dir
  | _ => pure 2
