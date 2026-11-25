/-! Complete decoder meter controls. -/
namespace ProctorDimacsDecoderMeterMain
open ProctorHallDeficiency
open ProctorDimacsDecoderMeter
open ProctorDimacsInput (lexDimacs decodeDimacs)
open ProctorDimacsLexerCompose (lexMeter)
open ProctorDimacsRowMeter (decodeRowsMeter)

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def ascii (s : String) : List Nat := s.toUTF8.data.toList.map (fun c => c.toNat)

def checkOne (a : List Nat) : IO (Bool × Bool × Nat) := do
  let l := lexMeter a
  let r := decodeMeter a
  if l.1 != lexDimacs a || r.1 != decodeDimacs a ||
      r.2 != l.2+(decodeRowsMeter a).2 ||
      r.2 > decoderUnit a.length || decoderUnit a.length != a.length*34+29 then
    throw (IO.userError "complete DIMACS decoder mismatch")
  pure (l.1.isSome,r.1.isSome,r.2)

def run (dir : String) : IO UInt32 := do
  let controls : List (String × Option (Nat × Formula) × Nat) :=
    [("",none,0),
     ("p cnf 0 0\n",some (0,[]),2),
     ("p cnf 0 1\n0\n",some (0,[[]]),5),
     ("p cnf 1 1\n2 0\n",none,4),
     ("p cnf 0 0\n0\n",none,2),
     ("p cnf 0 100001\n",none,1)]
  for (s,want,k) in controls do
    let a := ascii s
    let _ ← checkOne a
    if (decodeMeter a).1 != want || (decodeRowsMeter a).2 != k then
      throw (IO.userError "decoder hand control mismatch")
  let mut lexed : Nat := 0
  let mut parsed : Nat := 0
  let mut count : Nat := 0
  for i in List.range 73 do
    let a ← readData (dir ++ "/" ++ toString i ++ ".cnf")
    let (l,r,c) ← checkOne a
    if l then lexed := lexed+1
    if r then parsed := parsed+1
    count := count+c
  if lexed != 63 || parsed != 56 || count != 1652056 then
    throw (IO.userError "decoder fixture aggregate mismatch")
  IO.println ("F034_DIMACS_DECODER_TOTAL lexed=" ++ toString lexed ++
    " parsed=" ++ toString parsed ++ " selected=" ++ toString count)
  IO.println "F034_DIMACS_DECODER_METER_OK files=73 lexed=63 parsed=56 hand_controls=6"
  pure 0
end ProctorDimacsDecoderMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorDimacsDecoderMeterMain.run dir
  | _ => pure 2
