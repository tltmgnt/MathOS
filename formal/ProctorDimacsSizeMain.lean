/-! Static validation on the existing 73 strict DIMACS controls. -/
namespace ProctorDimacsSizeMain
open ProctorDimacsInput (decodeDimacs checkDimacs)
open ProctorDataParser (decodeEnvelope)
open ProctorDimacsSize

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def run (dir : String) : IO UInt32 := do
  let mut parsed : Nat := 0
  let mut pairs : Nat := 0
  let mut accepted : Nat := 0
  for i in List.range 73 do
    let stem := dir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnf")
    let b ← readData (stem ++ ".proofdata")
    match decodeDimacs a with
    | none => pure ()
    | some (n,f) =>
      parsed := parsed+1
      if (ProctorWireRoundtrip.encExpected n f).length>a.length*2+3 then
        throw (IO.userError ("expected size mismatch " ++ toString i))
      match decodeEnvelope b with
      | none => pure ()
      | some e =>
        pairs := pairs+1
        let m := ProctorUnifiedMeter.boundMeter n f e
        if ProctorEncodedSize.size n f e>pairBound a b ||
            m.2>ProctorEncodedSize.globalUnit (byteCap a b) ||
            m.1 != checkDimacs a b then
          throw (IO.userError ("DIMACS byte budget mismatch " ++ toString i))
        if m.1 then
          accepted := accepted+1
          if m.2>ProctorEncodedSize.globalUnit (b.length+b.length+b.length+b.length+1) then
            throw (IO.userError "accepted envelope budget mismatch")
  if parsed != 56 || accepted != 22 then
    throw (IO.userError "DIMACS size aggregate mismatch")
  IO.println ("F034_DIMACS_SIZE_PAIRS " ++ toString pairs)
  IO.println "F034_DIMACS_SIZE_OK cases=73 parsed=56 accepted=22 rejected=51"
  pure 0
end ProctorDimacsSizeMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorDimacsSizeMain.run dir
  | _ => pure 2
