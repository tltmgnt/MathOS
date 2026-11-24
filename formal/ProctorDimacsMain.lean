/-! Static DIMACS input CLI. Proof file is the existing data envelope. -/
namespace ProctorDimacsMain

/-- Read at most limit+1 bytes from each stream, including a one-byte
EOF probe at the exact limit. A short read is not assumed to be EOF. -/
def readBounded (h : IO.FS.Handle) : Nat → ByteArray → IO (Option ByteArray)
  | 0, _ => pure none
  | fuel+1, acc => do
    let remaining := ProctorDataParser.byteLimit + 1 - acc.size
    let chunk ← h.read (min 65536 remaining).toUSize
    if chunk.size = 0 then
      pure (some acc)
    else if acc.size + chunk.size > ProctorDataParser.byteLimit then
      pure none
    else
      readBounded h fuel (acc ++ chunk)

def readBytes (path : String) : IO (Option (List Nat)) := do
  let h ← IO.FS.Handle.mk (System.FilePath.mk path) IO.FS.Mode.read
  let bytes ← readBounded h (ProctorDataParser.byteLimit+1) ByteArray.empty
  pure (bytes.map (fun b => b.data.toList.map (fun c => c.toNat)))


def runPair (expected proof : String) : IO Bool := do
  let a ← readBytes expected
  let b ← readBytes proof
  match a,b with
  | some a,some b => pure (ProctorDimacsInput.checkDimacs a b)
  | _,_ => pure false

def runFixtures (dir : String) : IO UInt32 := do
  let mut accepted : Nat := 0
  let mut parsed : Nat := 0
  for i in List.range 73 do
    let stem := dir ++ "/" ++ toString i
    let a ← readBytes (stem ++ ".cnf")
    let b ← readBytes (stem ++ ".proofdata")
    let expected ← IO.FS.readFile (System.FilePath.mk (stem ++ ".verdict"))
    let status ← IO.FS.readFile (System.FilePath.mk (stem ++ ".parse"))
    let got := a.bind ProctorDimacsInput.decodeDimacs
    if status = "1\n" then
      let raw ← readBytes (stem ++ ".cnfdata")
      let reference := raw.bind ProctorDataParser.decodeExpected
      if reference.isNone || got != reference then
        throw (IO.userError ("DIMACS decoded formula mismatch " ++ toString i))
      parsed := parsed+1
    else if status != "0\n" || got.isSome then
      throw (IO.userError ("DIMACS malformed input accepted " ++ toString i))
    let ok := match a,b with
      | some x,some y => ProctorDimacsInput.checkDimacs x y
      | _,_ => false
    if expected != (if ok then "1\n" else "0\n") then
      throw (IO.userError ("DIMACS certificate mismatch " ++ toString i))
    if ok then
      accepted := accepted+1
  if accepted != 22 || parsed != 56 then
    throw (IO.userError "DIMACS aggregate mismatch")
  IO.println "F034_DIMACS_REPLAY_OK cases=73 parsed=56 accepted=22 rejected=51"
  pure 0
end ProctorDimacsMain

def main (args : List String) : IO UInt32 := do
  match args with
  | ["--fixtures",dir] => ProctorDimacsMain.runFixtures dir
  | [expected,proof] =>
    if ← ProctorDimacsMain.runPair expected proof then
      IO.println "CERTIFIED_UNSAT"
      pure 0
    else
      IO.println "REJECTED"
      pure 1
  | _ =>
    IO.println "usage: checker expected.cnf certificate.proofdata"
    pure 2
