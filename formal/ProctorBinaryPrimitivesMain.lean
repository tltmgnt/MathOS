namespace ProctorBinaryPrimitivesMain
open ProctorDecimalBitWidth (bitsValue)
open ProctorBinaryPrimitives

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def run : IO UInt32 := do
  let mut cmp : Nat := 0
  let mut add : Nat := 0
  let mut dec : Nat := 0
  -- Exhaustive unequal-width representations, including empty lists.
  for wa in List.range 5 do
    for wb in List.range 5 do
      for a in List.range (2^wa) do
        for b in List.range (2^wb) do
          let x := bits a wa
          let y := bits b wb
          let r := compareMeter x y
          let s := addMeter x y
          let w := max wa wb
          if r.1 != decide (a<b) || r.2 != 5*w then
            throw (IO.userError "unsigned comparator mismatch")
          if bitsValue s.1 != a+b || s.1.length != w+1 || s.2 != 5*w then
            throw (IO.userError "padded adder mismatch")
          cmp := cmp+1
          add := add+1
  for a in List.range 256 do
    for d in List.range 10 do
      let r := decimalMeter (bits a 8) (bits d 4)
      if bitsValue r.1 != 10*a+d || r.1.length != 13 || r.2 != 115 then
        throw (IO.userError "decimal shift-add mismatch")
      dec := dec+1
  let v := List.replicate 512 true
  let zero := List.replicate 512 false
  let c1 := compareMeter v zero
  let c2 := compareMeter zero v
  let c3 := compareMeter v v
  let r := decimalMeter v (bits 9 4)
  if c1 != (false,2560) || c2 != (true,2560) || c3 != (false,2560) ||
      bitsValue r.1 != 10*bitsValue v+9 || r.1.length != 517 || r.2 != 5155 then
    throw (IO.userError "wide binary control mismatch")
  if cmp != 961 || add != 961 || dec != 2560 then
    throw (IO.userError "control count mismatch")
  IO.println "F034_BINARY_PRIMITIVES_OK comparisons=961 additions=961 decimal=2560 wide=4"
  pure 0
end ProctorBinaryPrimitivesMain

def main : IO UInt32 := ProctorBinaryPrimitivesMain.run
