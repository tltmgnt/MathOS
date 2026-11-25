/-! DIMACS primitive checks, including rejected words and headers. -/
namespace ProctorDimacsLexMeterMain
open ProctorDimacsInput
open ProctorDataParser (byteLimit)
open ProctorDimacsLexMeter

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def checkSplit (bytes : List Nat) : IO (List (List Nat) × Nat) := do
  let m := splitMeter bytes
  if m.1 != splitWords bytes [] [] ||
      m.2 > (bytes.length+1)+bytes.length+bytes.length then
    throw (IO.userError "split meter mismatch")
  pure m

def run (dir : String) : IO UInt32 := do
  if headerMeter [] != (none,1) ||
      headerMeter [112,10,49] != (some ([112],[49]),3) ||
      headerMeter [112] != (none,2) ||
      splitMeter [] != ([],1) ||
      splitMeter [49,32,50,10] != ([[49],[50]],9) ||
      naturalMeter [49] != (some 1,9) ||
      signedMeter [45,49] != (some (1,false),11) ||
      signedMeter [49] != (some (1,true),10) ||
      signedMeter [45,48] != (none,11) then
    throw (IO.userError "DIMACS lexical meter hand control")
  let mut files : Nat := 0
  let mut skipped : Nat := 0
  let mut headers : Nat := 0
  let mut splits : Nat := 0
  let mut words : Nat := 0
  let mut badWords : Nat := 0
  let mut count : Nat := 0
  for i in List.range 73 do
    let bytes ← readData (dir ++ "/" ++ toString i ++ ".cnf")
    files := files+1
    if bytes.length>byteLimit then
      skipped := skipped+1
    else
      let h := headerMeter bytes
      if h.1 != takeHeader bytes [] || h.2 > (bytes.length+1)+bytes.length then
        throw (IO.userError "header meter mismatch")
      count := count+h.2
      match h.1 with
      | none => pure ()
      | some (header,body) =>
        headers := headers+1
        match stripPrefix [112,32,99,110,102,32] header with
        | none => pure ()
        | some rest =>
          let hw ← checkSplit rest
          let bw ← checkSplit body
          count := count+hw.2+bw.2
          splits := splits+2
          for w in hw.1 do
            let m := naturalMeter w
            if m.1 != naturalWord w || m.2 > naturalUnit w.length then
              throw (IO.userError "header number meter mismatch")
            count := count+m.2
            words := words+1
            if m.1.isNone then badWords := badWords+1
          for w in bw.1 do
            let m := signedMeter w
            if m.1 != signedWord w || m.2 > signedUnit w.length then
              throw (IO.userError "signed word meter mismatch")
            count := count+m.2
            words := words+1
            if m.1.isNone then badWords := badWords+1
  if files != 73 || skipped=0 || badWords=0 then
    throw (IO.userError "DIMACS lexical coverage mismatch")
  IO.println ("F034_DIMACS_LEX_METER_TOTAL skipped=" ++ toString skipped ++
    " headers=" ++ toString headers ++ " splits=" ++ toString splits ++
    " words=" ++ toString words ++ " bad_words=" ++ toString badWords ++
    " selected=" ++ toString count)
  IO.println "F034_DIMACS_LEX_METER_OK files=73 hand_controls=9"
  pure 0
end ProctorDimacsLexMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorDimacsLexMeterMain.run dir
  | _ => pure 2
