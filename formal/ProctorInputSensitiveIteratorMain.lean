namespace ProctorInputSensitiveIteratorMain
open ProctorInputSensitiveIterator
open ProctorParserMeterCompose (listMeter natMeter)
open ProctorDataParser (listToken natToken)

def check (k n : Nat) : IO Unit := do
  let ts := k::List.replicate n 1
  let r := listMeter natMeter ts
  if r.1 != listToken natToken ts || r.2>3*ts.length+56 then
    throw (IO.userError "input-sensitive list mismatch")

def run : IO UInt32 := do
  let mut small : Nat := 0
  for k in List.range 33 do
    for n in List.range 34 do
      check k n
      small := small+1
  for (k,n) in [(100000,0),(100000,1),(100000,3),(99999,0),
    (99999,99999),(100000,100000),(100001,100000),(131071,0)] do
    check k n
  if (listMeter natMeter []).2 != 1 || small != 1122 then
    throw (IO.userError "empty or small-control count mismatch")
  IO.println "F034_INPUT_SENSITIVE_ITERATOR_OK small=1122 boundary=8 empty=1"
  pure 0
end ProctorInputSensitiveIteratorMain

def main : IO UInt32 := ProctorInputSensitiveIteratorMain.run
