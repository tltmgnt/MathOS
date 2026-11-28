// D7U: complete component prefix proof, oracle, bridge limitation and physical audit.
function audit(U,Q,R,A,AV,J,JV,S,SV,TA,X,PN,C,D,DV,T,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);},models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(x=>z[x]).join())));
 const sig=k=>Array.from({length:k},(_,i)=>+(i*17%7<3));
 const local=w=>({k:w,m:2,F:[...[...U.subsets(Array.from({length:w},(_,i)=>i),2)].map(h=>({h,S:new Set(["0,0","1,0","0,1"])})),...[...U.subsets(Array.from({length:w},(_,i)=>i),3)].map(h=>({h,S:new Set([...U.tuples(2,3)].filter(z=>z.some(Boolean)).map(z=>z.join()))}))]});
 if(section==="oracle"){
  const stats={cases:0,sat:0,unsat:0,models:0,certified:0,unknown:0,localTypes:0,proofNodes:0,divisions:0,tamperRejected:0};
  function check(d){const m=models(d),r=X.discover(S,d);stats.cases++;stats[m.length?"sat":"unsat"]++;stats.models+=m.length;
   if(r.kind==="cutting-conflict"){ok(!m.length&&SV.verify(JV,d,r),"soundness");stats.certified++;stats.proofNodes+=r.nodes.length;stats.divisions+=r.nodes.filter(n=>n.kind==="divide").length;}else stats.unknown++;return r;}
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){const h=Array.from({length:n},(_,i)=>n-1-i),S=new Set([...U.tuples(2,n)].filter((_,i)=>mask>>i&1).map(z=>z.join()));check({k:n,m:2,F:[{h,S}]});stats.localTypes++;}
  let seed=0xd7f524;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  for(let i=0;i<192;i++){const k=4+i%4,F=[];for(let j=0;j<3+i%7;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b),mask=rand()>>>16;F.push({h,S:new Set([...U.tuples(2,h.length)].filter((z,i)=>mask>>i&1).map(z=>z.join()))});}check({k,m:2,F});}
  const d=local(5),r=check(d);ok(r.kind==="cutting-conflict"&&r.metrics.complete===1,"K5");
  for(let mask=0;mask<32;mask++){const e=PN.transform(d,Array.from({length:5},(_,i)=>mask>>i&1)).d;ok(check(e).kind==="cutting-conflict","signed K5");}
  const perm={...d,F:d.F.slice().reverse().map(f=>({h:f.h.slice().reverse(),S:new Set([...f.S].map(s=>s.split(",").reverse().join()))}))};ok(check(perm).kind==="cutting-conflict","permutation");
  const sat={...d,F:d.F.slice(0,10)};ok(check(sat).kind==="unknown"&&models(sat).length===6,"SAT");
  const lim=X.discover(S,d,r.nodes.length-1),checks=X.discover(S,d,4096,9),zero=X.reduce(JV,S,SV,d,e=>({d:e,cert:{kind:"sentinel"},expand:z=>z}),0);
  ok(lim.kind==="unknown"&&lim.status==="budget"&&checks.kind==="unknown"&&checks.status==="budget"&&zero.d===d&&zero.cert.kind==="sentinel","limits");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  const i=r.nodes.findIndex(n=>n.kind==="divide"),replace=(i,n)=>({...r,nodes:r.nodes.map((x,j)=>i===j?n:x)});
  reject(()=>SV.verify(JV,d,replace(i,{...r.nodes[i],divisor:"3"})));reject(()=>SV.verify(JV,d,replace(i,{...r.nodes[i],divisor:"0"})));reject(()=>SV.verify(JV,d,replace(i,{...r.nodes[i],parent:i})));reject(()=>SV.verify(JV,d,replace(r.terminal,{kind:"sum",parents:[r.terminal]})));reject(()=>SV.verify(JV,d,replace(0,{kind:"source",row:{...r.nodes[0].row,b:r.nodes[0].row.b-1}})));reject(()=>SV.verify(JV,d,{...r,rhs:"0"}));
  return {stats,limits:{complete:r.nodes.length,limited:lim.metrics.nodes,checks:checks.metrics.checks,zero:zero.completeComponents.metrics.nodes},satModels:models(sat).length};
 }
 if(section==="large"){
  const rows=[];for(const [n,w,flip,pre,cap] of [[5,5,false,true,4096],[7,5,true,true,4096],[7,4,true,true,4096],[11,9,true,true,4096],[41,13,true,false,20000],[5,31,true,false,4096]]){
   let d=TA.fixture(U,n,w);if(flip)d=PN.transform(d,sig(d.k)).d;const p=pre?R.reduce(U,Q,d):null,a=pre?A.reduce(U,p.d):null;if(pre){AV.verify(p.d,a.a);ok(!p.contradiction&&a.a.free.length===d.k&&!a.a.rows.length,"pre");}
   const e=pre?a.d:d,r=X.discover(S,e,cap);ok(r.kind==="cutting-conflict"&&r.lower==="0"&&r.rhs===String(n-Math.ceil(d.k/3))&&SV.verify(JV,e,r),"large");
   rows.push({n,w,k:d.k,factors:d.F.length,flip,pre,cap,rhs:r.rhs,metrics:r.metrics});
  }return {rows};
 }
 if(section==="barrier"){
  const rows=[];for(const n of [5,7]){
   const base=TA.fixture(U,n,5),d={...base,F:[...base.F,...Array.from({length:n-1},(_,i)=>({h:[5*i,5*(i+1)],S:new Set(["0,0","0,1","1,0"])}))]},p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=X.discover(S,a.d),t=D.tree(C,a.d,2000000),manual=TA.nestedFive(U,base);
   ok(!p.contradiction&&a.a.free.length===d.k&&!a.a.rows.length&&r.kind==="unknown"&&r.metrics.complete===0&&t.kind==="tree"&&DV.verifyTree(a.d,t)&&SV.verify(JV,d,manual),"bridge");
   const count=Array(d.k).fill(0);for(const f of base.F.filter(f=>f.h.length===3))for(const x of f.h)count[x]++;ok(count.every(x=>x===3),"degree");
   let fractional=0;for(const f of d.F)for(const q of J.supports(f)){ok(q.a.reduce((s,x)=>s+x,0)<=3*q.b,"fractional");fractional++;}
   rows.push({n,k:d.k,factors:d.F.length,metrics:r.metrics,fractional,aggregateBounds:[Math.ceil(d.k/3),2*n],manual:{nodes:manual.nodes.length,rhs:manual.rhs},tree:{work:t.work,nodes:t.nodes,leaves:t.leaves,splits:t.splits,units:t.units}});
  }return {barrier:rows};
 }
 if(section==="fallback"){
  const d=TA.fixture(U,5,4),r=X.reduce(JV,S,SV,d,e=>{ok(e===d,"fallback exact");return T.reduce(JV,S,SV,{verify:(v,s,e,p)=>s.verify(v,e,p)},e);},0);
  ok(r.contradiction&&r.cert.kind==="cutting-conflict"&&r.completeComponents.status==="budget","actual inherited");
  return {fallback:{kind:r.cert.kind,nodes:r.cert.nodes.length,status:r.completeComponents.status}};
 }
 throw Error("section");
}
function physical(U,W,K,F,Min,JV,S,SV,TA,X){
 const d=TA.fixture(U,5,5),r=X.reduce(JV,S,SV,d);
 if(!r.contradiction||r.cert.kind!=="cutting-conflict")throw Error("adapter");
 const machine=W.machine(),M=W.singleExit(K.compile(machine)),N0=Min.refine(M),q={...M,...N0},s=W.stream(U,r.d),b=W.run(M,s,300000000),c=W.run(q,s,b.t),cut=W.run(q,s,b.t-1),clock=F.count(machine,["",s],M.codes);
 if(b.status!=="UNSAT"||b.z!==null||JSON.stringify(b)!==JSON.stringify(c)||b.t!==clock.clock||b.encoded!==clock.encoded||cut.status!=="TIMEOUT"||cut.t!==b.t-1||cut.z!==null)throw Error("physical");
 return {physical:{status:b.status,transitions:b.t,stream:s.length,clock:clock.clock,cutoff:cut.t,states:N0.stats.quotientStates,bits:N0.stats.quotientBits}};
}
module.exports={audit,physical};
if(require.main===module&&process.argv[2]==='physical')console.log(JSON.stringify(physical(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'),require('./f038_rex_variable_inequality_certificate.js'),require('./f038_rex_variable_cutting_planes.js'),require('./f038_rex_variable_cutting_plane_certificate.js'),require('./f038_rex_variable_clique_cut_audit.js'),require('./f038_rex_variable_complete_components.js'))));
else if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_inequality_certificates.js'),require('./f038_rex_variable_inequality_certificate.js'),require('./f038_rex_variable_cutting_planes.js'),require('./f038_rex_variable_cutting_plane_certificate.js'),require('./f038_rex_variable_clique_cut_audit.js'),require('./f038_rex_variable_complete_components.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_clique_cuts.js'),process.argv[2]||'oracle')));
