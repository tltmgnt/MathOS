/-! Complete row-parser projection and selected-charge checks. -/
namespace ProctorDimacsRowMeterMain
open ProctorHallDeficiency
open ProctorDimacsRowMeter
open ProctorDimacsInput (parseRow parseRows lexDimacs decodeDimacs)
open ProctorDataParser (listLimit)

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def run (dir : String) : IO UInt32 := do
  if rowMeter 1 [] != (none,1) ||
      rowMeter 1 [(0,true),(1,true)] != (some ([],[(1,true)]),1) ||
      rowMeter 1 [(0,false)] != (none,1) ||
      rowMeter 1 [(2,true),(0,true)] != (none,1) ||
      rowMeter 1 [(1,false)] != (none,2) ||
      rowMeter 1 [(1,false),(0,true)] != (some ([(1,false)],[]),2) ||
      rowsMeter 0 0 [] != (some [],1) ||
      rowsMeter 0 0 [(0,true)] != (none,1) ||
      rowsMeter 1 1 [(1,false),(0,true)] != (some [[(1,false)]],7) ||
      rowsMeter 0 2 [(0,true)] != (none,6) ||
      rowsMeter 0 1 [(0,true),(0,true)] != (none,4) then
    throw (IO.userError "row meter hand control")
  let long : List Literal := List.replicate (listLimit+1) (1,true) ++ [(0,true)]
  let longResult := rowsMeter 1 1 long
  if longResult.1.isSome || longResult.2 != (listLimit+2)*3 then
    throw (IO.userError "over-limit row control")
  let mut parsed : Nat := 0
  let mut lexed : Nat := 0
  let mut count : Nat := 0
  for i in List.range 73 do
    let bytes ← readData (dir ++ "/" ++ toString i ++ ".cnf")
    let r := decodeRowsMeter bytes
    if r.1 != decodeDimacs bytes || r.2 > rowsUnit bytes.length+1 then
      throw (IO.userError ("row decode mismatch " ++ toString i))
    if r.1.isSome then parsed := parsed+1
    count := count+r.2
    match lexDimacs bytes with
    | none => pure ()
    | some (n,m,ts) =>
      lexed := lexed+1
      let row := rowMeter n ts
      if row.1 != parseRow n ts || row.2 > ts.length+1 then
        throw (IO.userError "first row mismatch")
      match row.1 with
      | none => pure ()
      | some (c,rest) =>
        if row.2+rest.length != ts.length || row.2 != c.length+1 then
          throw (IO.userError "row consumption mismatch")
      if m≤listLimit then
        let rs := rowsMeter n m ts
        if rs.1 != parseRows n m ts || rs.2 > rowsUnit ts.length then
          throw (IO.userError "rows meter mismatch")
  if parsed != 56 || lexed != 63 then
    throw (IO.userError "row fixture aggregate mismatch")
  IO.println ("F034_DIMACS_ROW_METER_TOTAL lexed=" ++ toString lexed ++
    " parsed=" ++ toString parsed ++ " selected=" ++ toString count)
  IO.println "F034_DIMACS_ROW_METER_OK files=73 lexed=63 parsed=56 hand_controls=12"
  pure 0
end ProctorDimacsRowMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorDimacsRowMeterMain.run dir
  | _ => pure 2
