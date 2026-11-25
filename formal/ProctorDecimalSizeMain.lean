namespace ProctorDecimalSizeMain
open ProctorDecimalEncoder (encode word)
open ProctorDecimalSize (byteCount)
def verify (ts : List Nat) (d : Nat) : IO Unit := do
  let cap := 10^(d+1)
  if ts.any (fun n => n≥cap) then throw (IO.userError "bad test cap")
  let bs := encode ts
  if bs.length != byteCount ts || bs.length>ts.length*(d+2) then
    throw (IO.userError "byte budget")
  for n in ts do
    if n≥10^(word n).length || (word n).length>d+1 ||
       n≥10^bs.length then
      throw (IO.userError "word magnitude or length")
  if ProctorUnboundedCodec.tokenize bs != some ts then
    throw (IO.userError "roundtrip")
def run : IO UInt32 := do
  for n in List.range 1000 do
    verify [n] 2
  for d in List.range 129 do
    let n := 10^d
    verify [n-1,n,n+1] d
  verify [] 0
  verify [0,1,10,100,3401,3402,10^512] 512
  IO.println "F035_DECIMAL_SIZE_OK singletons=1000 boundaries=129 lists=2"
  pure 0
end ProctorDecimalSizeMain
def main : IO UInt32 := ProctorDecimalSizeMain.run
