/-! Raw-pair meter fixture controls. -/
namespace ProctorEndToEndMeterMain
open ProctorEndToEndMeter
open ProctorDataParser (checkBytes)
open ProctorDimacsInput (checkDimacs)
open ProctorUnifiedMeter (boundMeter)

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def ascii (s : String) : List Nat := s.toUTF8.data.toList.map (fun c => c.toNat)

def one (dimacs : Bool) (a b : List Nat) : IO (Bool × Nat) := do
  let x := if dimacs then ProctorDimacsDecoderMeter.decodeMeter a else expectedDecode a
  let y := proofDecode b
  let r := if dimacs then dimacsMeter a b else customMeter a b
  let want := if dimacs then checkDimacs a b else checkBytes a b
  let budget := if dimacs then dimacsBudget a b else customBudget a b
  let v := match x.1,y.1 with
    | some (n,f),some e => (boundMeter n f e).2
    | _,_ => 0
  if r.1 != want || r.2 > budget || r.2 != x.2+y.2+v then
    throw (IO.userError "raw pair meter mismatch")
  pure r

def run (customDir dimacsDir : String) : IO UInt32 := do
  let proof := ascii "3402\n0\n1\n0\n0\n0\n0\n"
  let expected := ascii "3401\n0\n1\n0\n"
  let dimacs := ascii "p cnf 0 1\n0\n"
  let controls : List (Bool × List Nat × List Nat × Bool) :=
    [(false,expected,proof,true),(true,dimacs,proof,true),
     (false,[],proof,false),(true,[],proof,false),
     (false,expected,[],false),(true,dimacs,[],false),
     (true,ascii "p cnf 0 0\n",proof,false),(false,ascii "3401\n0\n0\n",proof,false)]
  for (mode,a,b,want) in controls do
    let r ← one mode a b
    if r.1 != want then throw (IO.userError "raw pair hand control")
  let mut customYes : Nat := 0
  let mut dimacsYes : Nat := 0
  let mut customCount : Nat := 0
  let mut dimacsCount : Nat := 0
  for i in List.range 67 do
    let stem := customDir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnfdata")
    let b ← readData (stem ++ ".proofdata")
    let r ← one false a b
    if r.1 then customYes := customYes+1
    customCount := customCount+r.2
  for i in List.range 73 do
    let stem := dimacsDir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnf")
    let b ← readData (stem ++ ".proofdata")
    let r ← one true a b
    if r.1 then dimacsYes := dimacsYes+1
    dimacsCount := dimacsCount+r.2
  if customYes != 19 || dimacsYes != 22 then
    throw (IO.userError "raw pair fixture count mismatch")
  IO.println ("F034_END_TO_END_TOTAL custom_selected=" ++ toString customCount ++
    " dimacs_selected=" ++ toString dimacsCount)
  IO.println "F034_END_TO_END_METER_OK custom=67 accepted=19 dimacs=73 accepted=22 hand_controls=8"
  pure 0
end ProctorEndToEndMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [a,b] => ProctorEndToEndMeterMain.run a b
  | _ => pure 2
