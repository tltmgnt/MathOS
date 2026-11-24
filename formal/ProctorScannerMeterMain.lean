/-! Scanner validation on existing raw custom data fixtures. -/
namespace ProctorScannerMeterMain
open ProctorDataParser
open ProctorScannerMeter

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def checkOne (bytes : List Nat) : IO (Bool × Nat) := do
  let r := tokenizeMeter bytes
  if r.1 != tokenize bytes || r.2 > tokenBudget bytes then
    throw (IO.userError "scanner projection or bound mismatch")
  match r.1 with
  | none => pure (false,r.2)
  | some ts =>
    if r.2 != (bytes.length+1)+(bytes.length+1)+ts.length then
      throw (IO.userError "scanner success count mismatch")
    pure (true,r.2)

def run (dir : String) : IO UInt32 := do
  if tokenizeMeter [] != (some [],2) ||
      tokenizeMeter [49,10] != (some [1],7) ||
      tokenizeMeter [48,49,10] != (none,6) ||
      tokenizeMeter [49] != (none,4) ||
      tokenizeMeter [10] != (none,3) ||
      tokenizeMeter [49,10,50,10] != (some [1,2],12) then
    throw (IO.userError "scanner hand-count mismatch")
  let good := List.replicate 128 57 ++ [10]
  let bad := List.replicate 129 57 ++ [10]
  let (goodOk,goodCount) ← checkOne good
  let (badOk,badCount) ← checkOne bad
  if !goodOk || badOk || goodCount != 261 || badCount != 260 then
    throw (IO.userError "digit boundary mismatch")
  let mut yes : Nat := 0
  let mut no : Nat := 0
  let mut count : Nat := 0
  for i in List.range 67 do
    let stem := dir ++ "/" ++ toString i
    for ext in [".cnfdata",".proofdata"] do
      let bytes ← readData (stem ++ ext)
      let (ok,c) ← checkOne bytes
      if ok then yes := yes+1 else no := no+1
      count := count+c
  if yes+no != 134 || no=0 then
    throw (IO.userError "scanner fixture count mismatch")
  IO.println ("F034_SCANNER_TOTAL lexical_accept=" ++ toString yes ++
    " lexical_reject=" ++ toString no ++ " selected=" ++ toString count)
  IO.println "F034_SCANNER_METER_OK files=134 hand_controls=8"
  pure 0
end ProctorScannerMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorScannerMeterMain.run dir
  | _ => pure 2
