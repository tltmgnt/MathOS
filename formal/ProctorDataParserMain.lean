/-! Static CLI / fixture runner for ProctorDataParser. No source
generated from certificates is loaded on this path. -/
namespace ProctorDataParserMain

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
  match a with
  | none => pure false
  | some a =>
    let b ← readBytes proof
    match b with
    | none => pure false
    | some b => pure (ProctorDataParser.checkBytes a b)

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
