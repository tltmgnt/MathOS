namespace ProctorAllOrderBarrierMain
open ProctorHallDeficiency
open ProctorAllOrderBarrier (advance countRow marker growth)
open ProctorTotalTwoCNF (supported)
def family (vs : List Nat) : Formula :=
  vs.map marker ++ vs.flatMap (fun u => vs.flatMap (fun w =>
    if u=w then [] else [false,true].flatMap (fun a =>
      [false,true].map (fun b => [(u,a),(w,b)]))))
def verify (prefix suffix : List Nat) : IO Unit := do
  let f := family (prefix++suffix)
  let g := advance prefix f
  let m := growth prefix.length 1
  for u in suffix do
    if countRow (marker u) g == 0 || supported g then
      throw (IO.userError "marker lost")
    for w in suffix do
      if u != w then
        for a in [false,true] do
          for b in [false,true] do
            if countRow [(u,a),(w,b)] g < m then
              throw (IO.userError "pair multiplicity")
def run : IO UInt32 := do
  verify [] [1,2,3,4]
  for v in [1,2,3,4] do
    let rest := [1,2,3,4].filter (fun w => w != v)
    verify [v] rest
    for w in rest do
      verify [v,w] (rest.filter (fun u => u != w))
  IO.println "F035_ALL_ORDER_BARRIER_OK prefixes=17"
  pure 0
end ProctorAllOrderBarrierMain
def main : IO UInt32 := ProctorAllOrderBarrierMain.run
