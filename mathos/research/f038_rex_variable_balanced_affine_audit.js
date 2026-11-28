// D7N: local orientation, higher-order affine derivations, family and integer-balance limitation.
function audit(U,Q,R,A,AV,L,M,N,NV,PN,C,D,T,H,B,G,I,P,J,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);},models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(x=>z[x]).join())));
 const nae=(h,sign=[])=>({h,S:new Set([...U.tuples(2,3)].filter(z=>{const y=z.map((x,j)=>x^+sign.includes(h[j]));return y.some(x=>x!==y[0]);}).map(z=>z.join()))});
 const block=(h,s=[])=>[...U.subsets(h,3)].map(t=>nae(t,s));
 const sig=k=>Array.from({length:k},(_,i)=>+(i*17%7<3));
 function graph(n,flip=true){const edges=[];for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)if(n===5||[1,2,n-1,n-2].includes(j-i))edges.push([i,j]);const F=[];for(let i=0;i<n;i++){const v=edges.flatMap((e,j)=>e.includes(i)?[j]:[]);F.push(...block(v,i===0&&flip?[v[0]]:[]));}return {k:edges.length,m:2,F};}
 if(section==="oracle"){
  const stats={cases:0,sat:0,unsat:0,models:0,rows:0,blocks:0,affine:0,strict:0,unknown:0,localTypes:0,masks:0,graphMasks:0,tamperRejected:0};
  function check(d){
   const m=models(d),p=N.discover(L,A,d),r=N.infer(L,A,d);stats.cases++;stats[m.length?"sat":"unsat"]++;stats.models+=m.length;stats.rows+=p.rows.length;stats.blocks+=p.blocks.length;
   for(const b of p.blocks){if(b.kind==="strict"){NV.checkBlock(d,b);ok(!m.length,"strict oracle");}else{const rows=b.kind==="local"?NV.checkLocal(d,b):NV.checkBlock(d,b);ok(m.every(z=>rows.every(q=>q.h.reduce((s,x)=>s^z[x],0)===q.rhs)),"source row oracle");}}
   ok(m.every(z=>p.rows.every(q=>q.h.reduce((s,x)=>s^z[x],0)===q.rhs)),"row oracle");
   if(r.kind==="unknown")stats.unknown++;else{stats[r.kind==="affine-conflict"?"affine":"strict"]++;ok(!m.length&&NV.verify(d,r),"soundness");}return r;
  }
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){const h=Array.from({length:n},(_,i)=>i),S=new Set([...U.tuples(2,n)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()));check({k:n,m:2,F:[{h,S}]});stats.localTypes++;}
  const b4={k:4,m:2,F:block([0,1,2,3])};for(let mask=0;mask<16;mask++){const d=PN.transform(b4,Array.from({length:4},(_,i)=>mask>>i&1)).d,p=N.discover(L,A,d);ok(p.rows.some(q=>q.h.length===4&&q.rhs===Array.from({length:4},(_,i)=>mask>>i&1).reduce((s,x)=>s^x,0))&&models(d).length===6,"block masks");check(d);stats.masks++;}
  const g=graph(5),sat=graph(5,false);for(let mask=0;mask<64;mask++){const s=Array.from({length:10},(_,i)=>mask>>(i%6)&1),d=PN.transform(g,s).d;ok(check(d).kind==="affine-conflict","graph masks");stats.graphMasks++;}
  ok(check(sat).kind==="unknown"&&models(sat).length>0,"consistent not SAT claim");
  const mixed={k:4,m:2,F:[...b4.F,...[1,0,0,0].map((x,i)=>({h:[i],S:new Set([String(x)])}))]},mc=check(mixed);ok(mc.kind==="affine-conflict"&&mc.blocks.some(b=>b.kind==="local")&&mc.blocks.some(b=>b.kind==="tight"),"mixed provenance");
  const fano={k:7,m:2,F:[[0,1,2],[0,3,4],[0,5,6],[1,3,5],[1,4,6],[2,3,6],[2,4,5]].map(h=>nae(h))};ok(check(fano).kind==="count-conflict","strict");
  let seed=0xd7c024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  for(let i=0;i<128;i++){const k=3+i%5,F=[];for(let j=0;j<2+i%9;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b),mask=rand()>>>16;F.push({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});}check({k,m:2,F});}
  const r=N.infer(L,A,g),reject=fn=>{let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;};
  reject(()=>NV.verify(g,{...r,combination:r.combination.slice(1)}));reject(()=>NV.verify(g,{...r,combination:[...r.combination,r.combination[0]]}));reject(()=>NV.verify(g,{...r,rows:r.rows.map((q,i)=>i?q:{...q,rhs:1-q.rhs})}));reject(()=>NV.verify(g,{...r,blocks:r.blocks.map((b,i)=>i?b:{...b,lower:"999"})}));reject(()=>NV.verify(g,{...r,blocks:r.blocks.map((b,i)=>i?b:{...b,sigma:b.sigma.map((x,j)=>j?x:1-x)})}));reject(()=>NV.verify(g,{...r,rows:r.rows.map((q,i)=>i?q:{...q,source:999})}));
  return {stats,local:{balancedModels:models(b4).length,satGraphModels:models(sat).length,mixedSources:mc.combination.length,previousCombination:r.combination.length}};
 }
 if(section==="large"){
  const rows=[];for(const [n,global,pre] of [[5,false,true],[5,true,true],[11,false,true],[31,true,true],[101,true,false],[501,true,false]]){
   let d=graph(n);if(global)d=PN.transform(d,sig(d.k)).d;const p=pre?R.reduce(U,Q,d):null,a=pre?A.reduce(U,p.d):null;if(pre){AV.verify(p.d,a.a);ok(a.a.free.length===d.k&&!a.a.rows.length,"pre");}const e=pre?a.d:d,r=N.infer(L,A,e);
   ok(r.kind==="affine-conflict"&&r.combination.length===n&&r.rank===n-1&&NV.verify(e,r),"family");
   rows.push({n,global,pre,k:d.k,factors:d.F.length,metrics:r.metrics,rank:r.rank,xors:r.xors,combination:r.combination.length});
  }return {rows};
 }
 if(section==="barrier"){
  function mul(a,b){let r=0;while(b){if(b&1)r^=a;b>>=1;a<<=1;if(a&4)a^=7;}return r;}
  const lines=[];for(let x=0;x<4;x++)lines.push(Array.from({length:4},(_,y)=>4*x+y));for(let slope=0;slope<3;slope++)for(let b=0;b<4;b++)lines.push(Array.from({length:4},(_,x)=>4*x+(mul(slope,x)^b)));
  const signs=[[],[0,3],[1,3],[],[0,2],[1,2],[2,3],[0,3],[1,2],[0,1],[0,2],[0,3],[],[],[0,1],[]],F=lines.flatMap((h,i)=>block(h,signs[i].map(j=>h[j]))),d={k:16,m:2,F};
  const m=models(d),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=N.infer(L,A,a.d),j=J.infer(PN,G,B,H,C,I,P,a.d),t=D.tree(C,a.d,2000000),l=L.discover(a.d),q=M.close(L,a.d);
  ok(!m.length&&a.a.free.length===16&&!a.a.rows.length&&r.kind==="unknown"&&r.rank===9&&r.metrics.rows===16&&N.discover(L,A,a.d).rows.every(q=>q.rhs===0)&&l.kind==="unknown"&&q.status==="fixed-point"&&!q.rounds.length&&j.kind==="unknown"&&j.status==="fixed-point"&&t.kind==="tree"&&T.verifyTree(a.d,t),"barrier");
  // Explicit integer linear combination of the sixteen local balance equations.
  const weights=[4,2,3,1,0,-4,-3,3,4,-2,1,-1,2,-2,0,-2],coeff=Array(16).fill(0);let rhs=0;
  for(let i=0;i<lines.length;i++){rhs+=weights[i]*(2-signs[i].length);let sum=0;for(let j=0;j<4;j++){const a=signs[i].includes(j)?-1:1;coeff[lines[i][j]]+=weights[i]*a;sum+=a;}ok(sum===2*(2-signs[i].length),"half-valued rational relaxation");}
  ok(coeff.every((x,i)=>x===(i===0?10:i===15?2:0))&&rhs===6,"integer identity");
  ok(![0,1].some(x=>[0,1].some(y=>5*x+y===3)),"binary support contradiction");
  return {barrier:{k:16,factors:F.length,assignments:65536,integerIdentity:{weights,coeff,rhs,halfFeasible:true},affineAssignments:2**(16-r.rank),balanced:r,count:l,tight:q.metrics,iterative:j,tree:{work:t.work,nodes:t.nodes,leaves:t.leaves,splits:t.splits,units:t.units}}};
 }
 if(section==="adapter"){
  const d=graph(5),r=N.reduce(L,A,NV,...Array(19).fill(null),d);ok(r.contradiction&&r.cert.kind==="affine-conflict"&&r.d.k===1&&!r.d.F[0].S.size,"adapter");return {adapter:{kind:r.cert.kind,k:r.d.k,allowed:r.d.F[0].S.size}};
 }
 throw Error("section");
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_pair_counting.js'),require('./f038_rex_variable_tight_counting.js'),require('./f038_rex_variable_balanced_affine.js'),require('./f038_rex_variable_balanced_affine_certificate.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_conflict_cliques.js'),require('./f038_rex_variable_disjunction_alternatives.js'),require('./f038_rex_variable_implication_closure.js'),require('./f038_rex_variable_conditional_propagation.js'),require('./f038_rex_variable_iterative_consequences.js'),process.argv[2]||'oracle')));
