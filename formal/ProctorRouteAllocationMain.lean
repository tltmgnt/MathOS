namespace ProctorRouteAllocationMain
open ProctorHallDeficiency
open ProctorImplicationPathDiscovery (Arc arcs)
open ProctorRouteAllocation (reachCells)
open ProctorPathResourceBounds (occurrences)
def subsets : List Arc → List (List Arc)
  | [] => [[]]
  | a::as => let rs := subsets as; rs++rs.map (fun r => a::r)
def verify (es : List Arc) (a : Literal) : IO Unit := do
  let e := es.length
  if reachCells es a>(e+2)*(e+1) then
    throw (IO.userError "route allocation bound")
def run : IO UInt32 := do
  let vs : List Literal := [(1,true),(2,false),(3,true)]
  let all := vs.flatMap (fun a => vs.map (fun b => (a,b)))
  for es in subsets all do
    for a in vs do
      verify es a
      verify es.reverse a
  let big := 10^128
  verify [((big,true),(1,false)),((1,false),(big,false)),((big,true),(1,false))] (big,true)
  IO.println "F035_ROUTE_ALLOCATION_OK graphSources=1536 reversed=1536 sparse=1"
  pure 0
end ProctorRouteAllocationMain
def main : IO UInt32 := ProctorRouteAllocationMain.run
