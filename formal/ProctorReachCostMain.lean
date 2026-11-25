namespace ProctorReachCostMain
open ProctorHallDeficiency
open ProctorImplicationPathDiscovery (Arc Routes)
open ProctorReachCost (reachCost chargedReach)
def vertices : List Literal := [(1,true),(2,true),(3,true)]
def allArcs : List Arc := vertices.flatMap (fun a => vertices.map (fun b => (a,b)))
def subsets : List Arc → List (List Arc)
  | [] => [[]]
  | e::es => let rs := subsets es; rs++rs.map (fun r => e::r)
def checkCost (es : List Arc) (a b : Literal) : IO Unit := do
  let n := es.length
  let cap := n*(n*((1+n)+(1+n)))+(1+n)
  if reachCost es a b>cap || chargedReach es a b 257>257*cap then
    throw (IO.userError "comparison bound violated")
def run : IO UInt32 := do
  for es in subsets allArcs do
    for a in vertices do
      for b in vertices do
        checkCost es a b
  for j in List.range 20 do
    let n := j+1
    let es : List Arc := ((List.range n).map (fun i => ((i+1,true),(i+2,true)))).reverse
    checkCost es (1,true) (n+1,true)
    checkCost es (n+1,true) (1,true)
  let big := 10^128
  checkCost [((1,true),(big,false)),((big,false),(1,true)),((1,true),(big,false))] (1,true) (big,false)
  IO.println "F035_REACH_COST_OK graphPairs=4608 chains=40 sparse=1"
  pure 0
end ProctorReachCostMain
def main : IO UInt32 := ProctorReachCostMain.run
