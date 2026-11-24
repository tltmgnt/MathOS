/-! Static CLI / fixture runner for ProctorDataParser. No source
generated from certificates is loaded on this path. -/
namespace ProctorDataParserMain

def readBytes (path : String) : IO (List Nat) := do
  let bytes ← IO.FS.readBinFile (System.FilePath.mk path)
  pure (bytes.data.toList.map (fun b => b.toNat))

def runPair (expected proof : String) : IO Bool := do
  let a ← readBytes expected
  let b ← readBytes proof
  pure (ProctorDataParser.checkBytes a b)

def runFixtures (dir : String) : IO UInt32 := do
  let mut accepted : Nat := 0
  for i in List.range 67 do
    let stem := dir ++ "/" ++ toString i
    let ok ← runPair (stem ++ ".cnfdata") (stem ++ ".proofdata")
    let verdict ← IO.FS.readFile (System.FilePath.mk (stem ++ ".verdict"))
    if verdict != (if ok then "1\n" else "0\n") then
      throw (IO.userError ("F034 data fixture disagreement " ++ toString i))
    if ok then
      accepted := accepted+1
  if accepted != 19 then
    throw (IO.userError "F034 data fixture acceptance count mismatch")
  IO.println "F034_DATA_REPLAY_OK cases=67 accepted=19 rejected=48"
  pure 0

end ProctorDataParserMain

def main (args : List String) : IO UInt32 := do
  match args with
  | ["--fixtures",dir] => ProctorDataParserMain.runFixtures dir
  | [expected,proof] =>
    let ok ← ProctorDataParserMain.runPair expected proof
    if ok then
      IO.println "CERTIFIED_UNSAT"
      pure 0
    else
      IO.println "REJECTED"
      pure 1
  | _ =>
    IO.println "usage: checker expected.cnfdata certificate.proofdata"
    pure 2
