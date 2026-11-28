// D7J: bounded source-clause conditional propagation with independent trace replay.
function discover(C,I,d,budget=2000000){
 if(d.m!==2||!Number.isSafeInteger(budget)||budget<0)throw Error("parameters");
 const axioms=C.clauses(d),occ=new Map(),units=[],pairs=new Map();
 let work=0,tests=0,visits=0,assignments=0,derived=0;const stop={};
 function charge(){if(work===budget)throw stop;work++;}
 const info=()=>({work,tests,visits,assignments,derived,pairScopes:pairs.size});
 for(const a of axioms){
  if(!a.c.length)return {kind:"conflict",trace:{assume:[],steps:[],conflict:a},metrics:info()};
  if(a.c.length===1)units.push(a);
  for(const x of a.c){if(!occ.has(x))occ.set(x,[]);occ.get(x).push(a);}
  for(let i=0;i<a.c.length;i++)for(let j=0;j<i;j++){
   const u=Math.abs(a.c[j]),v=Math.abs(a.c[i]);pairs.set(u+","+v,[u,v]);
  }
 }
 const known=new Set(axioms.map(a=>a.c.join())),records=[],rank=new Map(Array.from({length:d.k},(_,i)=>[i,i]));
 function probe(assume){
  charge();tests++;const z=new Map(),queue=[],steps=[];
  function set(x){z.set(Math.abs(x),x);queue.push(x);assignments++;}
  for(const x of assume)set(x);
  const value=x=>z.has(Math.abs(x))?+(z.get(Math.abs(x))===x):-1;
  function inspect(a){
   charge();visits++;let open=0,last=0;
   for(const x of a.c){const v=value(x);if(v===1)return;if(v===-1){open++;last=x;}}
   if(!open)return a;
   if(open===1){set(last);steps.push({...a,p:last});}
  }
  for(const a of units){const conflict=inspect(a);if(conflict)return {assume,steps,conflict};}
  for(let i=0;i<queue.length;i++)for(const a of occ.get(-queue[i])||[]){const conflict=inspect(a);if(conflict)return {assume,steps,conflict};}
  return null;
 }
 function trial(a){
  const c=a.map(x=>-x),key=c.join();
  if(known.has(key)||c.length===2&&c.some(x=>known.has(String(x))))return;
  const t=probe(a);if(t){known.add(key);records.push({c,trace:t});derived++;}
 }
 let status="complete";
 try{
  const t=probe([]);if(t)return {kind:"conflict",trace:t,metrics:info()};
  for(let i=1;i<=d.k;i++){trial([i]);trial([-i]);}
  for(const [u,v] of pairs.values())for(const a of [u,-u])for(const b of [v,-v])trial([a,b]);
 }catch(e){if(e!==stop)throw e;status="budget";}
 const F=d.F.slice();for(const r of records)F.push(I.factor(r.c,rank));
 return {kind:"view",status,d:{k:d.k,m:2,F},records,metrics:info()};
}

function infer(N,G,B,H,C,I,d,budget=2000000,beam=8){
 const original=I.infer(N,G,B,H,C,d,beam);
 if(original.kind!=="unknown")return {kind:"inherited",proof:original};
 const p=discover(C,I,d,budget);
 if(p.kind==="conflict")return {kind:"propagation-conflict",trace:p.trace,metrics:p.metrics};
 if(p.records.length){
  const h=I.infer(N,G,B,H,C,p.d,beam);
  if(h.kind!=="unknown")return {kind:"conditional",records:p.records,proof:h,status:p.status,metrics:p.metrics};
 }
 return {kind:"unknown",status:p.status,metrics:p.metrics};
}

function reduce(N,G,B,H,C,V,D,T,HV,NV,I,IV,PV,d,budget=2000000,beam=8){
 const p=infer(N,G,B,H,C,I,d,budget,beam);
 if(p.kind==="unknown")return {...D.reduce({...C,cardinality:x=>N.sparseCardinality(C,x)},V,T,d,budget),conditional:p};
 if(PV.verify(IV,NV,HV,d,p)!==true)throw Error("unverified conditional proof");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:p,conditional:p,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={discover,infer,reduce};
