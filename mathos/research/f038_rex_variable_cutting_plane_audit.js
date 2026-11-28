// D7S: bounded cutting-plane oracle and verified two-level clique-rounding frontier.
function fixture(U,n){
 const F=[];for(let i=0;i<n;i++)for(const h of U.subsets(Array.from({length:4},(_,j)=>4*i+j),2))F.push({h,S:new Set(["0,0","1,0","0,1"])});
 for(let i=0;i<n;i++)for(let j=0;j<4;j++)F.push({h:[4*i+j,4*((i+1)%n)+j,4*((i+3)%n)+j],S:new Set([...U.tuples(2,3)].filter(z=>z.some(Boolean)).map(z=>z.join()))});return {k:4*n,m:2,F};
}

function rankTwo(U,d){
 const n=d.k/4,nodes=[],add=x=>(nodes.push(x),nodes.length-1),upper=[];
 for(let i=0;i<n;i++){
  const vs=Array.from({length:4},(_,j)=>4*i+j),edges=new Map();
  for(const h of U.subsets(vs,2)){const f=d.F.findIndex(t=>t.h.join()===h.join());edges.set(h.join(),add({kind:"source",row:{h,a:[1,1],b:1,f}}));}
  const triangles=[];
  for(const h of U.subsets(vs,3)){
   const s=add({kind:"sum",parents:[...U.subsets(h,2)].map(p=>edges.get(p.join()))});
   triangles.push(add({kind:"divide",parent:s,divisor:"2"}));
  }
  const s=add({kind:"sum",parents:triangles});upper.push(add({kind:"divide",parent:s,divisor:"3"}));
 }
 const lower=[];for(let f=6*n;f<d.F.length;f++)lower.push(add({kind:"source",row:{h:d.F[f].h.slice().sort((a,b)=>a-b),a:[-1,-1,-1],b:-1,f}}));
 const l=add({kind:"divide",parent:add({kind:"sum",parents:lower}),divisor:"3"});
 const terminal=add({kind:"sum",parents:[...upper,l]});return {kind:"cutting-conflict",nodes,terminal,lower:"0",rhs:String(n-Math.ceil(d.k/3))};
}

function audit(U,Q,R,A,AV,J,JV,JA,S,SV,PN,C,D,T,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);},models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(x=>z[x]).join())));
 const sig=k=>Array.from({length:k},(_,i)=>+(i*17%7<3));
 if(section==="oracle"){
  const stats={cases:0,sat:0,unsat:0,models:0,certified:0,unknown:0,localTypes:0,proofNodes:0,divisions:0,tamperRejected:0};
  function check(d){const m=models(d),r=S.discover(J,d);stats.cases++;stats[m.length?"sat":"unsat"]++;stats.models+=m.length;
   if(r.kind==="cutting-conflict"){ok(!m.length&&SV.verify(JV,d,r),"soundness");stats.certified++;stats.proofNodes+=r.nodes.length;stats.divisions+=r.nodes.filter(n=>n.kind==="divide").length;}else stats.unknown++;return r;}
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){const h=Array.from({length:n},(_,i)=>n-1-i),S=new Set([...U.tuples(2,n)].filter((_,i)=>mask>>i&1).map(z=>z.join()));check({k:n,m:2,F:[{h,S}]});stats.localTypes++;}
  let seed=0xd7f424;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  for(let i=0;i<192;i++){const k=4+i%4,F=[];for(let j=0;j<3+i%7;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b),mask=rand()>>>16;F.push({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});}check({k,m:2,F});}
  const d=JA.fixture(U,11,1),r=check(d);ok(r.kind==="cutting-conflict"&&r.metrics.divisions===2,"rounding");
  const flipped=check(PN.transform(d,sig(11)).d);ok(flipped.kind==="cutting-conflict","signed");
  const sat=JA.fixture(U,12,1);check(sat);
  const zero=S.reduce(J,SV,d,e=>({d:e,cert:{kind:"sentinel"},expand:z=>z}),0),limited=S.discover(J,d,r.nodes.length-1);
  ok(zero.d===d&&zero.cert.kind==="sentinel"&&limited.kind==="unknown"&&limited.status==="budget","limits");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  const i=r.nodes.findIndex(n=>n.kind==="divide"),replace=(i,n)=>({...r,nodes:r.nodes.map((x,j)=>i===j?n:x)});
  reject(()=>SV.verify(JV,d,replace(i,{...r.nodes[i],divisor:"2"})));
  reject(()=>SV.verify(JV,d,replace(i,{...r.nodes[i],divisor:"0"})));
  reject(()=>SV.verify(JV,d,replace(i,{...r.nodes[i],parent:i})));
  reject(()=>SV.verify(JV,d,replace(r.terminal,{kind:"sum",parents:[r.terminal]})));
  reject(()=>SV.verify(JV,d,replace(0,{kind:"source",row:{...r.nodes[0].row,b:r.nodes[0].row.b-1}})));
  reject(()=>SV.verify(JV,d,{...r,rhs:"0"}));
  ok(S.floor(-31n,3n)===-11n&&S.floor(31n,3n)===10n&&S.floor(-30n,3n)===-10n,"signed floor");
  return {stats,limits:{zero:zero.cutting.metrics.nodes,limited:limited.metrics.nodes,complete:r.nodes.length},satControlModels:models(sat).length};
 }
 if(section==="large"){
  const rows=[];for(const [k,flip,pre] of [[31,false,true],[31,true,true],[127,true,true],[1001,true,false]]){
   let d=JA.fixture(U,k,1);if(flip)d=PN.transform(d,sig(k)).d;const p=pre?R.reduce(U,Q,d):null,a=pre?A.reduce(U,p.d):null;if(pre){AV.verify(p.d,a.a);ok(!p.contradiction&&a.a.free.length===k&&!a.a.rows.length,"pre");}
   const e=pre?a.d:d,r=S.discover(J,e);ok(r.kind==="cutting-conflict"&&r.lower==="0"&&r.rhs==="-1"&&SV.verify(JV,e,r),"large");
   rows.push({k,factors:d.F.length,flip,pre,metrics:r.metrics,divisors:r.nodes.filter(n=>n.kind==="divide").map(n=>n.divisor)});
  }return {rows};
 }
 if(section==="barrier"){
  const rows=[];for(const n of [5,7]){
   const d=fixture(U,n),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=S.discover(J,a.d),t=D.tree(C,a.d,2000000),manual=rankTwo(U,d);
   ok(!p.contradiction&&a.a.free.length===d.k&&!a.a.rows.length&&r.kind==="unknown"&&t.kind==="tree"&&T.verifyTree(a.d,t)&&SV.verify(JV,d,manual),"rank two");
   let fractional=0;for(const f of d.F)for(const q of J.supports(f)){ok(q.a.reduce((s,x)=>s+x,0)<=3*q.b,"fractional witness");fractional++;}
   rows.push({k:d.k,factors:d.F.length,metrics:r.metrics,fractional,aggregateBounds:[Math.ceil(d.k/3),d.k/2],manual:{nodes:manual.nodes.length,divisions:manual.nodes.filter(x=>x.kind==="divide").length,rhs:manual.rhs},tree:{work:t.work,nodes:t.nodes,leaves:t.leaves,splits:t.splits,units:t.units}});
  }return {barrier:rows};
 }
 throw Error("section");
}
module.exports={fixture,rankTwo,audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_inequality_certificates.js'),require('./f038_rex_variable_inequality_certificate.js'),require('./f038_rex_variable_inequality_audit.js'),require('./f038_rex_variable_cutting_planes.js'),require('./f038_rex_variable_cutting_plane_certificate.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),process.argv[2]||'oracle')));
