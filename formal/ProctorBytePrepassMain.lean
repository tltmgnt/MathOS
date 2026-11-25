namespace ProctorBytePrepassMain
open ProctorBytePrepass
open ProctorDataParser (byteLimit tokenize)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def run : IO UInt32 := do
  let mut small : Nat := 0
  for w in List.range 7 do
    for n in List.range (2^w) do
      let c := bits n w
      for k in List.range (2^w+2) do
        let xs := List.replicate k 0
        if lengthOK xs c != decide (k≤n) then
          throw (IO.userError "length guard mismatch")
        let v := visits xs c
        if v>w*k || v>w*(n+1) then
          throw (IO.userError "visit bound mismatch")
        small := small+1
  for k in [0,1,byteLimit-1,byteLimit,byteLimit+1,byteLimit+2] do
    if byteOK (List.replicate k 0) != decide (k≤byteLimit) then
      throw (IO.userError "full byte limit mismatch")
  let cases := [[],[10],[48,10],[49,50,10],[49],[48,48,10],
    [49,10,50,10],[58,10],List.replicate 128 57++[10],
    List.replicate 129 57++[10]]
  for bs in cases do
    if tokenizeBounded bs != tokenize bs then
      throw (IO.userError "tokenizer composition mismatch")
  if small != 5715 then
    throw (IO.userError "prepass control count mismatch")
  IO.println "F034_BYTE_PREPASS_OK small=5715 large=6 scanner=10"
  pure 0
end ProctorBytePrepassMain

def main : IO UInt32 := ProctorBytePrepassMain.run
