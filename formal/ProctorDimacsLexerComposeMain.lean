namespace ProctorDimacsLexerComposeMain
open ProctorDimacsLexerCompose
open ProctorDimacsInput (lexDimacs)

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def run (dir : String) : IO UInt32 := do
  if signedWordsMeter [] != (some [],1) ||
      signedWordsMeter [[49]] != (some [(1,true)],13) ||
      signedWordsMeter [[45,48],[49]] != (none,13) ||
      lexMeter [] != (none,2) ||
      lexMeter [112] != (none,4) ||
      lexMeter [10] != (none,9) then
    throw (IO.userError "complete lexical hand control mismatch")
  let mut yes : Nat := 0
  let mut no : Nat := 0
  let mut count : Nat := 0
  for i in List.range 73 do
    let a ← readData (dir ++ "/" ++ toString i ++ ".cnf")
    let r := lexMeter a
    if r.1 != lexDimacs a || r.2 > lexUnit a.length then
      throw (IO.userError ("complete lexical mismatch " ++ toString i))
    if r.1.isSome then yes := yes+1 else no := no+1
    count := count+r.2
  if yes+no != 73 || yes=0 || no=0 then
    throw (IO.userError "complete lexical coverage mismatch")
  IO.println ("F034_LEX_COMPOSE_TOTAL lexical_accept=" ++ toString yes ++
    " lexical_reject=" ++ toString no ++ " selected=" ++ toString count)
  IO.println "F034_LEX_COMPOSE_OK files=73 hand_controls=6"
  pure 0
end ProctorDimacsLexerComposeMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorDimacsLexerComposeMain.run dir
  | _ => pure 2
