// D7T: signed clique discovery, independent nested proofs and larger clique frontier.
function fixture(U,n,w){
 const F=[];for(let i=0;i<n;i++)for(const h of U.subsets(Array.from({length:w},(_,j)=>w*i+j),2))F.push({h,S:new Set(["0,0","1,0","0,1"])});
 for(let i=0;i<n;i++)for(let j=0;j<w;j++)F.push({h:[w*i+j,w*((i+1)%n)+j,w*((i+3)%n)+j],S:new Set([...U.tuples(2,3)].filter(z=>z.some(Boolean)).map(z=>z.join()))});
 return {k:n*w,m:2,F};
}

function nestedFive(U,d){
 const n=d.k/5,nodes=[],cache=new Map(),add=x=>(nodes.push(x),nodes.length-1);
 const fIndex=new Map(d.F.slice(0,10*n).map((f,i)=>[f.h.join(),i]));
 function cut(h){
  const key=h.join();if(cache.has(key))return cache.get(key);
  let id;
  if(h.length===2)id=add({kind:"source",row:{h,a:[1,1],b:1,f:fIndex.get(key)}});
  else{id=add({kind:"divide",parent:add({kind:"sum",parents:[...U.subsets(h,h.length-1)].map(cut)}),divisor:String(h.length-1)});}
  cache.set(key,id);return id;
 }
 const upper=Array.from({length:n},(_,i)=>cut(Array.from({length:5},(_,j)=>5*i+j)));
 const lower=[];for(let f=10*n;f<d.F.length;f++)lower.push(add({kind:"source",row:{h:d.F[f].h.slice().sort((a,b)=>a-b),a:[-1,-1,-1],b:-1,f}}));
 const l=add({kind:"divide",parent:add({kind:"sum",parents:lower}),divisor:"3"});
 const terminal=add({kind:"sum",parents:[...upper,l]});
 return {kind:"cutting-conflict",nodes,terminal,lower:"0",rhs:String(n-Math.ceil(d.k/3))};
}

function audit(U,Q,R,A,AV,J,JV,JA,S,SV,SA,T,TV,PN,C,D,DV,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);},models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(x=>z[x]).join())));
 const sig=k=>Array.from({length:k},(_,i)=>+(i*17%7<3));
 if(section==="oracle"){
  const stats={cases:0,sat:0,unsat:0,models:0,certified:0,unknown:0,localTypes:0,proofNodes:0,divisions:0,tamperRejected:0};
  function check(d){const m=models(d),r=T.discover(S,d);stats.cases++;stats[m.length?"sat":"unsat"]++;stats.models+=m.length;
   if(r.kind==="cutting-conflict"){ok(!m.length&&TV.verify(JV,SV,d,r),"soundness");stats.certified++;stats.proofNodes+=r.nodes.length;stats.divisions+=r.nodes.filter(n=>n.kind==="divide").length;}
   else stats.unknown++;return r;}
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){const h=Array.from({length:n},(_,i)=>n-1-i),S=new Set([...U.tuples(2,n)].filter((_,i)=>mask>>i&1).map(z=>z.join()));check({k:n,m:2,F:[{h,S}]});stats.localTypes++;}
  let seed=0xd7f524;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  for(let i=0;i<192;i++){const k=4+i%4,F=[];for(let j=0;j<3+i%7;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b),mask=rand()>>>16;F.push({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});}check({k,m:2,F});}
  // Four-clique plus every triple requiring one: three-of-four lower constraints force >=2.
  const k4={k:4,m:2,F:[...[...U.subsets([0,1,2,3],2)].map(h=>({h,S:new Set(["0,0","1,0","0,1"])})),...[...U.subsets([0,1,2,3],3)].map(h=>({h,S:new Set([...U.tuples(2,3)].filter(z=>z.some(Boolean)).map(z=>z.join()))}))]};
  const r=check(k4);ok(r.kind==="cutting-conflict"&&r.metrics.cliques[4]===1,"K4");
  for(let mask=0;mask<16;mask++){const d=PN.transform(k4,Array.from({length:4},(_,i)=>mask>>i&1)).d;ok(check(d).kind==="cutting-conflict","signed K4");}
  const perm={...k4,F:k4.F.slice().reverse().map(f=>({h:f.h.slice().reverse(),S:new Set([...f.S].map(s=>s.split(",").reverse().join()))}))};ok(check(perm).kind==="cutting-conflict","scope and factor permutation");
  const sat={...k4,F:k4.F.slice(0,6)};ok(check(sat).kind==="unknown"&&models(sat).length===5,"sat clique");
  const zero=T.reduce(J, S, SV, TV,k4,e=>({d:e,cert:{kind:"sentinel"},expand:z=>z}),0),limited=T.discover(S,k4,r.nodes.length-1),checks=T.discover(S,k4,4096,0);
  ok(zero.d===k4&&zero.cert.kind==="sentinel"&&limited.kind==="unknown"&&limited.status==="budget"&&checks.kind==="unknown"&&checks.status==="budget","limits");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  const i=r.nodes.findIndex(n=>n.kind==="divide"),replace=(i,n)=>({...r,nodes:r.nodes.map((x,j)=>i===j?n:x)});
  reject(()=>TV.verify(JV,SV,k4,replace(i,{...r.nodes[i],divisor:"3"})));
  reject(()=>TV.verify(JV,SV,k4,replace(i,{...r.nodes[i],divisor:"0"})));
  reject(()=>TV.verify(JV,SV,k4,replace(i,{...r.nodes[i],parent:i})));
  reject(()=>TV.verify(JV,SV,k4,replace(r.terminal,{kind:"sum",parents:[r.terminal]})));
  reject(()=>TV.verify(JV,SV,k4,replace(0,{kind:"source",row:{...r.nodes[0].row,b:r.nodes[0].row.b-1}})));
  reject(()=>TV.verify(JV,SV,k4,{...r,rhs:"0"}));
  return {stats,limits:{zero:zero.cliqueCuts.metrics.nodes,limited:limited.metrics.nodes,complete:r.nodes.length,checks:checks.metrics.checks},satControlModels:models(sat).length};
 }
 if(section==="large"){
  const rows=[];for(const [n,flip,pre] of [[5,false,true],[7,false,true],[7,true,true],[101,true,false],[201,true,false]]){
   let d=SA.fixture(U,n);if(flip)d=PN.transform(d,sig(d.k)).d;const p=pre?R.reduce(U,Q,d):null,a=pre?A.reduce(U,p.d):null;if(pre){AV.verify(p.d,a.a);ok(!p.contradiction&&a.a.free.length===d.k&&!a.a.rows.length,"pre");}
   const e=pre?a.d:d,r=T.discover(S,e);ok(r.kind==="cutting-conflict"&&r.lower==="0"&&r.rhs===String(n-Math.ceil(d.k/3))&&TV.verify(JV,SV,e,r),"large");
   rows.push({k:d.k,factors:d.F.length,flip,pre,rhs:r.rhs,metrics:r.metrics});
  }return {rows};
 }
 if(section==="barrier"){
  const rows=[];for(const n of [5,7]){
   const d=fixture(U,n,5),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=T.discover(S,a.d),t=D.tree(C,a.d,2000000),manual=nestedFive(U,d);
   ok(!p.contradiction&&a.a.free.length===d.k&&!a.a.rows.length&&r.kind==="unknown"&&t.kind==="tree"&&DV.verifyTree(a.d,t)&&TV.verify(JV,SV,d,manual),"K5 barrier");
   let fractional=0;for(const f of d.F)for(const q of J.supports(f)){ok(q.a.reduce((s,x)=>s+x,0)<=3*q.b,"fractional witness");fractional++;}
   rows.push({k:d.k,factors:d.F.length,metrics:r.metrics,fractional,aggregateBounds:[Math.ceil(d.k/3),2*n],manual:{nodes:manual.nodes.length,divisions:manual.nodes.filter(x=>x.kind==="divide").length,rhs:manual.rhs},tree:{work:t.work,nodes:t.nodes,leaves:t.leaves,splits:t.splits,units:t.units}});
  }return {barrier:rows};
 }
 throw Error("section");
}

function physical(U,W,K,F,Min,J,JV,S,SV,SA,T,TV){
 const d=SA.fixture(U,5),r=T.reduce(J,S,SV,TV,d);
 if(!r.contradiction||r.cert.kind!=="cutting-conflict")throw Error("adapter");
 const machine=W.machine(),M=W.singleExit(K.compile(machine)),N0=Min.refine(M),q={...M,...N0},s=W.stream(U,r.d),b=W.run(M,s,300000000),c=W.run(q,s,b.t),cut=W.run(q,s,b.t-1),clock=F.count(machine,["",s],M.codes);
 if(b.status!=="UNSAT"||b.z!==null||JSON.stringify(b)!==JSON.stringify(c)||b.t!==clock.clock||b.encoded!==clock.encoded||cut.status!=="TIMEOUT"||cut.t!==b.t-1||cut.z!==null)throw Error("physical");
 return {physical:{status:b.status,transitions:b.t,stream:s.length,clock:clock.clock,cutoff:cut.t,states:N0.stats.quotientStates,bits:N0.stats.quotientBits}};
}

function fallback(U,J,JV,JA,S,SV,T,TV){
 const d=JA.fixture(U,31,1),r=T.reduce(J,S,SV,TV,d,e=>{if(e!==d)throw Error("changed residual");return S.reduce(J,JV,SV,e);});
 if(!r.contradiction||r.cert.kind!=="cutting-conflict"||r.cliqueCuts.kind!=="unknown")throw Error("fallback");
 return {fallback:{kind:r.cert.kind,nodes:r.cert.nodes.length,cliqueCuts:r.cliqueCuts.status}};
}
module.exports={fixture,nestedFive,audit,physical,fallback};
if(require.main===module&&process.argv[2]==='physical')console.log(JSON.stringify(physical(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'),require('./f038_rex_variable_inequality_certificates.js'),require('./f038_rex_variable_inequality_certificate.js'),require('./f038_rex_variable_cutting_planes.js'),require('./f038_rex_variable_cutting_plane_certificate.js'),require('./f038_rex_variable_cutting_plane_audit.js'),require('./f038_rex_variable_clique_cuts.js'),require('./f038_rex_variable_clique_cut_certificate.js'))));
else if(require.main===module&&process.argv[2]==='fallback')console.log(JSON.stringify(fallback(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_inequality_certificates.js'),require('./f038_rex_variable_inequality_certificate.js'),require('./f038_rex_variable_inequality_audit.js'),require('./f038_rex_variable_cutting_planes.js'),require('./f038_rex_variable_cutting_plane_certificate.js'),require('./f038_rex_variable_clique_cuts.js'),require('./f038_rex_variable_clique_cut_certificate.js'))));
else if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_inequality_certificates.js'),require('./f038_rex_variable_inequality_certificate.js'),require('./f038_rex_variable_inequality_audit.js'),require('./f038_rex_variable_cutting_planes.js'),require('./f038_rex_variable_cutting_plane_certificate.js'),require('./f038_rex_variable_cutting_plane_audit.js'),require('./f038_rex_variable_clique_cuts.js'),require('./f038_rex_variable_clique_cut_certificate.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),process.argv[2]||'oracle')));
