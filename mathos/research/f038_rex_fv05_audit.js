// FV-05: audit real D7I budget counters against separately constructed graph.
const C=require('./f038_rex_variable_resolution_closure.js');
const D=require('./f038_rex_variable_adaptive_inference.js');
const I=require('./f038_rex_variable_implied_conflicts.js');
const IV=require('./f038_rex_variable_implied_certificate.js');
const R=require('./f038_rex_fv05_resources.js');
const U={*tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**j)%m);}};
const ok=(b,m)=>{if(!b)throw Error("FV05: "+m);};
function split(d){
 let k=d.k,F=[];
 for(const f of d.F){if(f.h.length!==2){F.push(f);continue;}const [x,y]=f.h,u=k++;
  F.push({h:[x,u],S:new Set(["0,0","0,1","1,1"])},{h:[u,y],S:new Set(["0,0","0,1","1,0"])});
 }
 return {k,m:2,F};
}
// Independent graph construction directly from forbidden rows, followed by
// distance computation. No call to C.clauses or D7I's path builder.
function expected(d){
 const adj=new Map(),keys=new Set(),boundary=new Set(),binary=new Set();
 for(const f of d.F){
  if(f.h.length!==2){f.h.forEach(v=>boundary.add(v+1));continue;}
  for(const a of [0,1])for(const b of [0,1])if(!f.S.has([a,b].join())){
   const x=(f.h[0]+1)*(a?-1:1),y=(f.h[1]+1)*(b?-1:1);
   const key=[x,y].sort((u,v)=>Math.abs(u)-Math.abs(v)).join();
   if(keys.has(key))continue;keys.add(key);
   binary.add(Math.abs(x));binary.add(Math.abs(y));
   for(const [s,t] of [[-x,y],[-y,x]]){if(!adj.has(s))adj.set(s,[]);adj.get(s).push(t);}
  }
 }
 const options=[...boundary].filter(x=>binary.has(x)).sort((a,b)=>a-b).flatMap(x=>[x,-x]);
 let scans=0,pairs=0,steps=0,peak=0;const pathLengths=new Map();
 for(let i=0;i<options.length;i++){
  const x=options[i],dist=new Map([[x,0]]),queue=[x];
  for(let j=0;j<queue.length;j++){
   const u=queue[j],ar=adj.get(u)||[];scans+=ar.length;
   for(const v of ar)if(!dist.has(v)){dist.set(v,dist.get(u)+1);queue.push(v);}
  }
  peak=Math.max(peak,dist.size);
  for(let j=i+1;j<options.length;j++){
   const y=options[j];pairs++;
   if(Math.abs(x)!==Math.abs(y)&&dist.has(-y)){
    const n=dist.get(-y);steps+=n;pathLengths.set([x,y].join(),n);
   }
  }
 }
 return {edges:2*keys.size,options:options.length,scans,pairs,steps,peak,pathLengths};
}
function check(d,cut=true){
 const limit=2000000,r=I.project(C,d,limit,true);ok(r.kind==="projection","complete");
 const size=R.verifyCounts(d,r,limit),m=r.metrics,e=expected(d);
 ok(m.edges===e.edges&&m.options===e.options&&m.edgeScans===e.scans&&m.pairTests===e.pairs&&m.pathSteps===e.steps&&m.peakQueue===e.peak&&m.peakPredecessors===e.peak,"oracle counters");
 ok(r.paths.length===e.pathLengths.size&&r.paths.every(p=>p.edges.length===e.pathLengths.get([p.x,p.y].join())),"shortest paths");
 const decoded=R.decodeProjection(d.k,d.F.length,R.encodeProjection(d.k,d.F.length,r));
 const q=IV.reconstruct(d,decoded);
 ok(q.F.length===r.d.F.length&&q.F.every((f,i)=>f.h.join()===r.d.F[i].h.join()&&f.S.size===r.d.F[i].S.size&&[...f.S].every(t=>r.d.F[i].S.has(t))),"decoded certificate replay");
 // Confirm optional instrumentation leaves the ordinary result unchanged.
 const uninstrumented=I.project(C,d,limit);const {metrics,...rest}=r;
 ok(JSON.stringify(uninstrumented)===JSON.stringify(rest),"ordinary API");
 let cutoffs=0,completions=0;
 if(cut)for(const b of [...new Set([0,1,Math.floor(r.work/2),Math.max(0,r.work-1),r.work,r.work+1])]){
  const t=I.project(C,d,b,true);R.verifyCounts(d,t,b);
  if(b<r.work){
   ok(t.kind==="unknown"&&t.work===b,"prefix cutoff");
   for(const n of ["edgeScans","pairTests","pathSteps","emitted","starts","peakQueue","peakPredecessors"])ok(t.metrics[n]<=m[n],"prefix counter");
   cutoffs++;
  }else{ok(t.kind==="projection"&&t.work===r.work,"exact budget");completions++;}
 }
 return {k:d.k,factors:d.F.length,paths:r.paths.length,work:r.work,...m,...size,cutoffs,completions};
}
function audit(){
 const rows=[3,6,8,12].map(n=>({holes:n,...check(split(D.php(U,n)))}));
 let seed=0xf03805,small=0,cutoffs=0,completions=0;
 const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<128;i++){
  const k=3+i%5,F=[];
  for(let j=0;j<2+i%11;j++){
   const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))];
   const mask=rand()>>>16;
   F.push({h,S:new Set([...U.tuples(2,h.length)].filter((_,a)=>mask>>a&1).map(z=>z.join()))});
  }
  if(i%8===0)F.push(F[0]);
  const a=check({k,m:2,F});small++;cutoffs+=a.cutoffs;completions+=a.completions;
 }
 const d=split(D.php(U,3)),r=I.project(C,d,2000000,true),bits=R.encodeProjection(d.k,d.F.length,r);
 let tamperRejected=0;
 for(const b of [bits.slice(0,-1),bits+"0".repeat(R.bounds(d.k,d.F.length).width),"x"+bits.slice(1)]){
  try{R.decodeProjection(d.k,d.F.length,b);}catch{tamperRejected++;continue;}throw Error("invalid encoding accepted");
 }
 return {rows,small,cutoffs,completions,tamperRejected};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit()));
