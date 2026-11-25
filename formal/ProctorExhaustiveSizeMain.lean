namespace ProctorExhaustiveSizeMain
open ProctorHallDeficiency
open ProctorExhaustiveSize
open ProctorExecutableDiscovery (generate)
open ProctorOrdinaryCompleteness (variables)

def run : IO UInt32 := do
  for k in List.range 7 do
    let f := padded k
    match generate 2 f with
    | none => throw (IO.userError "missing padded certificate")
    | some p =>
      if !ProctorUnifiedReplay.boundCheck 2 f ⟨2,f,p⟩ ||
        p.batches.length != nodes (k+2) ||
        p.batches.length < 2^(k+2) ||
        stepCount p.batches != copies (nodes (k+2)) f.length then
        throw (IO.userError "padded size mismatch")
  for k in List.range 20 do
    if nodes k + 1 != 2^(k+1) then
      throw (IO.userError "tree count mismatch")
  IO.println "F035_EXHAUSTIVE_SIZE_OK padded=7 trees=20"
  pure 0
end ProctorExhaustiveSizeMain

def main : IO UInt32 := ProctorExhaustiveSizeMain.run
