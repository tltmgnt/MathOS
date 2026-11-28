// D7I: source-path certified binary implication projection. Research-only.
const Check=require('./f038_rex_variable_implied_certificate.js');
function project(C,d,limit=2000000,collect=false){
 if(d.m!==2||!Number.isSafeInteger(limit)||limit<0)throw Error("parameters");
 const adj=new Map(),nonbinary=[],boundary=new Set(),binary=new Set();
 d.F.forEach((f,i)=>{if(f.h.length!==2){nonbinary.push(i);f.h.forEach(v=>boundary.add(v+1));}});
 const add=(x,y,f)=>{if(!adj.has(x))adj.set(x,[]);adj.get(x).push({to:y,f});};
 for(const {c,f} of C.clauses(d))if(c.length===2){
  const [a,b]=c;binary.add(Math.abs(a));binary.add(Math.abs(b));add(-a,b,f);add(-b,a,f);
 }
 const options=[...boundary].filter(x=>binary.has(x)).sort((a,b)=>a-b).flatMap(x=>[x,-x]);
 const paths=[];let work=0;
 const metrics={vertices:2*d.k,edges:[...adj.values()].reduce((a,b)=>a+b.length,0),options:options.length,starts:0,edgeScans:0,pairTests:0,pathSteps:0,emitted:0,peakQueue:0,peakPredecessors:0};
 const detail=()=>collect?{metrics:{...metrics}}:{};
 const cutoff=()=>({kind:"unknown",reason:"budget",work,...detail()});
 function charge(kind){if(work>=limit)return false;work++;metrics[kind]++;return true;}
 // Every emitted clause (-x or -y) is justified by x -> -y.
 // Keep only boundary-to-boundary conflicts; omit binary-only auxiliaries.
 for(let i=0;i<options.length;i++){
  const x=options[i],q=[x],prev=new Map([[x,null]]);metrics.starts++;
  function peak(){metrics.peakQueue=Math.max(metrics.peakQueue,q.length);metrics.peakPredecessors=Math.max(metrics.peakPredecessors,prev.size);}
  peak();
  for(let j=0;j<q.length;j++)for(const e of adj.get(q[j])||[]){
   if(!charge("edgeScans"))return cutoff();
   if(!prev.has(e.to)){prev.set(e.to,{from:q[j],f:e.f});q.push(e.to);peak();}
  }
  for(let j=i+1;j<options.length;j++){
   if(!charge("pairTests"))return cutoff();
   const y=options[j];if(Math.abs(x)===Math.abs(y)||!prev.has(-y))continue;
   let t=-y;const edges=[];
   while(t!==x){if(!charge("pathSteps"))return cutoff();const p=prev.get(t);edges.push({from:p.from,to:t,f:p.f});t=p.from;}
   paths.push({x,y,edges:edges.reverse()});metrics.emitted++;
  }
 }
 const e={k:d.k,m:2,F:nonbinary.map(i=>d.F[i]).concat(paths.map(({x,y})=>{
  const h=[Math.abs(x)-1,Math.abs(y)-1],S=new Set();
  for(const a of [0,1])for(const b of [0,1])if(a!==+(x>0)||b!==+(y>0))S.add([a,b].join());
  return {h,S};
 }))};
 return {kind:"projection",d:e,nonbinary,paths,work,boundary:options.length/2,...detail()};
}
function infer(N,G,B,H,C,d,limit=2000000,beam=8){
 const p=project(C,d,limit);if(p.kind==="unknown")return p;
 const h=N.normalize(G,B,H,C,p.d,beam);
 if(h.kind==="unknown")return {kind:"unknown",reason:"no-hall",work:p.work,boundary:p.boundary,paths:p.paths.length};
 return {kind:"implied-hall",nonbinary:p.nonbinary,paths:p.paths,hall:h,work:p.work,boundary:p.boundary};
}
function reduce(N,G,B,H,C,V,D,T,HV,NV,d,budget=2000000,limit=2000000,beam=8){
 const cert=infer(N,G,B,H,C,d,limit,beam);
 if(cert.kind==="unknown")return {...N.reduce(G,B,H,C,V,D,T,HV,NV,d,budget,beam),implied:cert};
 if(Check.verify(NV,HV,d,cert)!==true)throw Error("unverified implied Hall");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert,implied:cert,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={project,infer,reduce};
