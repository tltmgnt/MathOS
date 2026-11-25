namespace ProctorCheckedBinaryScannerMain
open ProctorCheckedBinaryScanner
open ProctorDecimalBitWidth (bitsValue)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def run : IO UInt32 := do
  let mut enc : Nat := 0
  let mut nar : Nat := 0
  for w in List.range 9 do
    for n in List.range 512 do
      match encode w n with
      | none =>
        if n<cap w then throw (IO.userError "unexpected encode rejection")
      | some out =>
        if n≥cap w || out.length != w || bitsValue out != n then
          throw (IO.userError "encode mismatch")
      enc := enc+1
    for k in List.range 9 do
      for n in List.range (2^k) do
        match narrow w (bits n k) with
        | none =>
          if n<cap w then throw (IO.userError "unexpected narrow rejection")
        | some out =>
          if n≥cap w || out.length != w || bitsValue out != n then
            throw (IO.userError "narrow mismatch")
        nar := nar+1
  let top := List.replicate 512 true
  if (narrow 512 (top++[false,false,false,false,false])) != some top ||
      (narrow 512 (top++[true])).isSome ||
      (checkedDigit top 57).isSome ||
      (encode 512 (cap 512)).isSome ||
      encode 512 (cap 512-1) != some top then
    throw (IO.userError "wide checked representation mismatch")
  let cases : List (List Nat × Option (List Nat)) :=
    [([],some []),([10],none),([48,10],some [0]),([48,48,10],none),
     ([49,50,51,10],some [123]),([49,10,50,10],some [1,2]),
     ([49],none),([47,10],none),([58,10],none),([49,32,10],none),
     ([49,10,10],none),
     (List.replicate 128 57++[10],some [10^128-1]),
     (List.replicate 129 57++[10],none)]
  for (bytes,expected) in cases do
    if tokenizeBits bytes != expected || ProctorDataParser.tokenize bytes != expected then
      throw (IO.userError "scanner refinement mismatch")
  if enc != 4608 || nar != 4599 then
    throw (IO.userError "representation control count mismatch")
  IO.println "F034_CHECKED_BINARY_SCANNER_OK encode=4608 narrow=4599 wide=5 scanner=13"
  pure 0
end ProctorCheckedBinaryScannerMain

def main : IO UInt32 := ProctorCheckedBinaryScannerMain.run
