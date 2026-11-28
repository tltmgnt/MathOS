// D7I: deterministic independent replay, oracle and integration regressions.
const assert=require('node:assert/strict');
const C=require('./f038_rex_variable_resolution_closure.js'),D=require('./f038_rex_variable_adaptive_inference.js'),H=require('./f038_rex_variable_hall_inference.js'),HV=require('./f038_rex_variable_hall_certificate.js'),B=require('./f038_rex_variable_conflict_cliques.js'),G=require('./f038_rex_variable_disjunction_alternatives.js'),N=require('./f038_rex_variable_polarity_normalization.js'),NV=require('./f038_rex_variable_polarity_certificate.js'),I=require('./f038_rex_variable_implied_conflicts.js'),IV=require('./f038_rex_variable_implied_certificate.js');
const U={*tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**j)%m);}};
function split(d){
 let k=d.k;const F=[];
 for(const f of d.F){if(f.h.length!==2){F.push(f);continue;}const [x,y]=f.h,u=k++;F.push({h:[x,u],S:new Set(["0,0","0,1","1,1"])},{h:[u,y],S:new Set(["0,0","0,1","1,0"])});}
 return {k,m:2,F};
}
const model=(d,z)=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join()));
function audit(){
 const rows=[];
 for(const n of [3,6,8]){
  const d=split(D.php(U,n)),r=I.infer(N,G,B,H,C,d);
  assert.equal(r.kind,"implied-hall");assert(IV.verify(NV,HV,d,r));
  assert.equal(r.hall.hall.groups.length,n+1);assert.equal(r.hall.hall.holes.length,n);
  assert(r.paths.every(p=>p.edges.length===2));
  rows.push({n,k:d.k,factors:d.F.length,paths:r.paths.length,work:r.work});
 }
 const d=split(D.php(U,6)),r=I.infer(N,G,B,H,C,d);
 const mutate=f=>{const t=JSON.parse(JSON.stringify(r));f(t);assert.throws(()=>IV.verify(NV,HV,d,t));};
 mutate(t=>t.paths[0].edges[0].f=-1);
 mutate(t=>t.paths[0].edges[0].to=-t.paths[0].edges[0].to);
 mutate(t=>t.paths[0].edges.pop());
 mutate(t=>t.paths[0].y=-t.paths[0].y);
 mutate(t=>t.paths.push(t.paths[0]));
 assert.equal(I.infer(N,G,B,H,C,d,0).reason,"budget");
 let seed=0x7d1024,oracles=0,models=0,refuted=0;
 const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let t=0;t<256;t++){
  const k=3+t%4,F=[];
  for(let j=0;j<2+t%9;j++){
   const h=[...new Set(Array.from({length:1+(rnd()>>>16)%3},()=> (rnd()>>>16)%k))].sort((a,b)=>a-b),mask=rnd()>>>16;
   F.push({h,S:new Set([...U.tuples(2,h.length)].filter((_,i)=>mask>>i&1).map(z=>z.join()))});
  }
  const d={k,m:2,F},p=I.project(C,d),e=IV.reconstruct(d,p),r=I.infer(N,G,B,H,C,d);
  assert.equal(p.kind,"projection");let count=0;
  for(const z of U.tuples(2,k)){assert.equal(model(p.d,z),model(e,z));if(model(d,z)){count++;assert(model(e,z));}}
  oracles++;models+=count;
  if(r.kind==="implied-hall"){assert.equal(count,0);assert(IV.verify(NV,HV,d,r));refuted++;}
 }
 // A satisfiable matching instance must not produce a Hall refutation.
 const sat={k:4,m:2,F:[{h:[0,1],S:new Set(["0,1","1,0","1,1"])},{h:[2,3],S:new Set(["0,1","1,0","1,1"])},{h:[0,2],S:new Set(["0,0","0,1","1,0"])}]};
 assert([...U.tuples(2,4)].some(z=>model(sat,z)));assert.equal(I.infer(N,G,B,H,C,sat).kind,"unknown");
 return {rows,oracles,models,refuted,tamperRejected:5,budgetCutoff:true};
}
module.exports={audit,split};
if(require.main===module)console.log(JSON.stringify(audit()));
