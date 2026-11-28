// D7F: robust, polynomially restricted conflict-clique partitions; inherited Hall checker.
function robust(H,C,d,groupPolicy=null){
 const metrics={supportEdges:0,supportProbes:0,thresholds:0,componentVisits:0,greedyTests:0,greedyTrials:0};
 function* alternatives(adj,owner){
  const vertices=[...adj.keys()],sets=new Map(vertices.map(x=>[x,new Set(adj.get(x))])),scores=new Map(vertices.map(x=>[x,new Map()])),values=new Set();
  for(const x of vertices)for(const y of adj.get(x))if(Math.abs(x)<Math.abs(y)){
   let s=0;metrics.supportEdges++;
   const a=sets.get(x),b=sets.get(y),small=a.size<=b.size?a:b,large=small===a?b:a;
   for(const z of small){metrics.supportProbes++;if(large.has(z))s++;}
   scores.get(x).set(y,s);scores.get(y).set(x,s);values.add(s+1);
  }
  // Only thresholds at which the retained edge set changes need testing.
  for(const threshold of [...values].sort((a,b)=>a-b)){
   metrics.thresholds++;const visited=new Set(),holes=[];
   for(const x of vertices)if(!visited.has(x)){
    const q=[x];visited.add(x);
    for(let i=0;i<q.length;i++)for(const y of adj.get(q[i])){
     metrics.componentVisits++;if(scores.get(q[i]).get(y)>=threshold&&!visited.has(y)){visited.add(y);q.push(y);}
    }
    holes.push(q);
   }
   yield {strategy:"support-"+threshold,holes};
  }
  // Fixed portfolio of greedy clique partitions; no optimal clique-cover claim.
  const rank=(x,y)=>Math.abs(x)-Math.abs(y);
  const orderings=[["rank",vertices.slice().sort(rank)],["reverse",vertices.slice().sort((a,b)=>rank(b,a))],
   ["degree-low",vertices.slice().sort((a,b)=>sets.get(a).size-sets.get(b).size||rank(a,b))],
   ["degree-high",vertices.slice().sort((a,b)=>sets.get(b).size-sets.get(a).size||rank(a,b))]];
  for(const [name,order] of orderings){
   metrics.greedyTrials++;const holes=[];
   for(const x of order){
    let best=-1;
    for(let i=0;i<holes.length;i++){
     let good=true;
     for(const y of holes[i]){metrics.greedyTests++;if(owner.get(x)!==owner.get(y)&&!sets.get(x).has(y)){good=false;break;}}
     if(good&&(best<0||holes[i].length>holes[best].length))best=i;
    }
    if(best<0)holes.push([x]);else holes[best].push(x);
   }
   yield {strategy:"greedy-"+name,holes};
  }
 }
 const h=H.hall(C,d,alternatives,groupPolicy);return {...h,metrics};
}

function reduce(H,C,V,D,T,HV,d,budget=2000000){
 const h=robust(H,C,d);
 if(h.kind==="unknown")return {...D.reduce(C,V,T,d,budget),hall:h};
 if(HV.verify(d,h)!==true)throw Error("unverified conflict partition certificate");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:h,hall:h,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={robust,reduce};
