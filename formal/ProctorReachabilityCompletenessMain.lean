namespace ProctorReachabilityCompletenessMain
open ProctorHallDeficiency
open ProctorImplicationPathDiscovery (Arc Routes routeFor reach sweep saturate)
open ProctorReachabilityCompleteness (missing)

def vertices : List Literal := [(1,true),(2,true),(3,true)]
def allArcs : List Arc :=
  vertices.flatMap (fun a => vertices.map (fun b => (a,b)))

def subsets : List Arc → List (List Arc)
  | [] => [[]]
  | e::es => let rs := subsets es; rs++rs.map (fun r => e::r)

-- Independent bounded walk enumeration, with no route-table reuse.
def oracle (es : List Arc) (b : Literal) : Nat → Literal → Bool
  | 0,a => a==b
  | k+1,a => a==b || es.any (fun e => e.1==a && oracle es b k e.2)

def checkFixed (es : List Arc) (a : Literal) : IO Unit := do
  let rs := saturate es es.length [(a,[])]
  if sweep es rs != rs then
    throw (IO.userError "saturation is not a fixed point")
  let tight := saturate es (missing [(a,[])] es) [(a,[])]
  if sweep es tight != tight then
    throw (IO.userError "potential fuel did not suffice")

def checkPair (es : List Arc) (a b : Literal) (expected : Bool) : IO Unit := do
  if (reach es a b).isSome != expected then
    throw (IO.userError "reachability differs from independent oracle")

def chain (r : Nat) : List Arc :=
  (List.range r).map (fun i => ((i+1,true),(i+2,true)))

def run : IO UInt32 := do
  for es in subsets allArcs do
    for a in vertices do
      checkFixed es a
      for b in vertices do
        checkPair es a b (oracle es b 3 a)
  for j in List.range 20 do
    let r := j+1
    let es := (chain r).reverse
    checkFixed es (1,true)
    checkPair es (1,true) (r+1,true) true
    checkPair es (r+1,true) (1,true) false
  let big := 10^128
  let a : Literal := (1,true)
  let b : Literal := (big,false)
  let es : List Arc := [(a,b),(b,a),(a,b),(b,b)]
  checkFixed es a
  checkPair es a b true
  checkPair es b a true
  checkPair es a (big,true) false
  IO.println "F035_REACHABILITY_COMPLETENESS_OK graphPairs=4608 chainPairs=40 sparsePairs=3 fixedSources=1557"
  pure 0
end ProctorReachabilityCompletenessMain

def main : IO UInt32 := ProctorReachabilityCompletenessMain.run
