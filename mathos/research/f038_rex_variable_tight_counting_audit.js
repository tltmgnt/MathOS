// D7M: tight-count exact witness bijections, weighted inequality, composition and balanced-block limit.
function audit(U,Q,R,A,AV,L,LV,M,MV,N,C,D,T,H,B,G,I,P,J,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);},S=["0,0,1","0,1,0","0,1,1","1,0,0","1,0,1","1,1,0"],f=h=>({h,S:new Set(S)});
 const h=[[0,3,4],[0,5,6],[1,3,5],[1,4,6],[2,3,6],[2,4,5]],map=[0,7,8,9,10,11,12],g={k:7,m:2,F:h.map(f)};
 const comp={k:13,m:2,F:[...h.map(f),...h.map(x=>f(x.map(y=>map[y]))),f([1,2,7])]},hh=h.map((x,i)=>x.map(y=>y===0&&i===1?1:map[y])),nested={k:13,m:2,F:[...h.map(f),...hh.map(f)]};
 const weighted={k:7,m:2,F:[...g.F,f([0,1,3])]},models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())));
 const sig=k=>Array.from({length:k},(_,i)=>+(i*17%7<3));
 function chain(n,flip){const F=[];let k=1,last=0;for(let i=0;i<n;i++){const a=[last,...Array.from({length:6},()=>k++)];for(const x of h)F.push(f(x.map(y=>a[y])));last=a[1];}F.push(f([0,2,last]));const d={k,m:2,F};return flip?N.transform(d,sig(k)).d:d;}
 if(section==="oracle"){
  const stats={cases:0,sat:0,unsat:0,models:0,certified:0,quotientViews:0,modelChecks:0,blocks:0,equations:0,rounds:0,maxRounds:0,tamperRejected:0,localTypes:0,masks:0};
  function check(d){
   const m=models(d),r=M.close(L,d);stats.cases++;stats[m.length?"sat":"unsat"]++;stats.models+=m.length;stats.rounds+=r.rounds.length;stats.maxRounds=Math.max(stats.maxRounds,r.rounds.length);
   let view=d,exp=z=>z;
   for(const batch of r.rounds){
    const before=models(view);for(const b of batch){const eq=MV.verifyTight(view,b);stats.blocks++;stats.equations+=eq.length;ok(before.every(z=>eq.every(([x,y,c])=>(z[x]^z[y])===c)),"equation oracle");}
    const a=M.quotient(view,batch),b=MV.reconstruct(view,batch);ok(a.kind===b.kind,"independent terminal");
    if(a.kind!=="view"){ok(!before.length,"terminal oracle");break;}
    ok(JSON.stringify(a.forms)===JSON.stringify(b.forms)&&JSON.stringify(a.d.F.map(f=>[f.h,[...f.S].sort()]))===JSON.stringify(b.d.F.map(f=>[f.h,[...f.S].sort()])),"independent quotient");
    const mm=models(a.d).map(a.expand);ok(JSON.stringify(mm)===JSON.stringify(before),"ordered model bijection");stats.modelChecks++;
    const old=exp;exp=z=>old(a.expand(z));view=a.d;
   }
   if(r.kind==="view"){stats.quotientViews++;ok(JSON.stringify(models(view).map(exp))===JSON.stringify(m),"composed model bijection");}
   else{stats.certified++;ok(!m.length&&MV.verify(LV,d,r),"verified refutation");}
   return r;
  }
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){const h=Array.from({length:n},(_,i)=>i),S=new Set([...U.tuples(2,n)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()));check({k:n,m:2,F:[{h,S}]});stats.localTypes++;}
  for(let mask=0;mask<128;mask++){const d=N.transform(g,Array.from({length:7},(_,i)=>mask>>i&1)).d,r=check(d);ok(r.kind==="view"&&r.d.k===5,"signed gadget");stats.masks++;}
  for(let mask=0;mask<64;mask++)check({...g,F:g.F.filter((_,i)=>mask>>i&1)});
  for(let mask=0;mask<128;mask++)check(N.transform(weighted,Array.from({length:7},(_,i)=>mask>>i&1)).d);
  let seed=0xd7a024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  for(let i=0;i<128;i++){const k=3+i%5,F=[];for(let j=0;j<2+i%9;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b),mask=rand()>>>16;F.push({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});}check({k,m:2,F});}
  const a=check(comp),b=check(N.transform(comp,sig(13)).d),c=check(nested),e=check({...nested,F:[...nested.F,f([7,8,2])]});
  ok(a.kind==="factor-conflict"&&b.kind==="factor-conflict"&&c.kind==="view"&&c.rounds.length===2&&c.d.k===9&&e.kind==="count-conflict"&&e.rounds.length===1,"composition");
  const w=M.close(L,weighted);ok(w.kind==="view"&&models(weighted).length===8&&w.rounds[0][0].equations.some(x=>x[2]===1),"weighted inequality");
  const limited=M.close(L,nested,1);ok(limited.kind==="view"&&limited.status==="round-limit"&&limited.d.k===11,"round limit");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  const t=a.rounds[0][0];reject(()=>MV.verifyTight(comp,{...t,lower:"999"}));reject(()=>MV.verifyTight(comp,{...t,equations:t.equations.slice(1)}));reject(()=>MV.verifyTight(comp,{...t,equations:t.equations.map((x,i)=>i?x:[x[0],x[1],1-x[2]])}));reject(()=>MV.verifyTight(comp,{...t,factors:[...t.factors,t.factors[0]]}));reject(()=>MV.verify(LV,comp,{...a,kind:"parity-conflict"}));reject(()=>MV.reconstruct(nested,c.rounds[1]));
  const map2=[0,1,7,8,9,10,11],left={k:12,m:2,F:g.F},right=N.transform({k:12,m:2,F:h.map(x=>f(x.map(y=>map2[y])))},Array.from({length:12},(_,i)=>+(i===1))).d;
  const both={k:12,m:2,F:[...left.F,...right.F]},l=M.candidates(L,left).blocks.find(x=>x.kind==="tight"),rr=M.candidates(L,right).blocks.find(x=>x.kind==="tight"),batch=[l,{...rr,factors:rr.factors.map(x=>x+6)}],pc={kind:"parity-conflict",rounds:[batch]};
  ok(M.quotient(both,batch).kind==="parity-conflict"&&MV.verify(LV,both,pc)&&!models(both).length,"explicit incompatible parity certificates");
  return {stats,parityConflict:{kind:pc.kind,equations:batch.reduce((s,x)=>s+x.equations.length,0)},local:{models:models(g).length,weightedModels:models(weighted).length,weightedEquations:w.rounds[0][0].equations,nestedModels:models(nested).length,nestedMetrics:c.metrics,nestedUnsat:e.metrics,limit:limited.d.k}};
 }
 if(section==="large"){
  const rows=[];for(const [name,d,pre] of [["prior",comp,true],["signed",N.transform(comp,sig(13)).d,true],["chain5",chain(5,false),true],["chain20",chain(20,true),true],["chain100",chain(100,true),false]]){
   const p=pre?R.reduce(U,Q,d):null,a=pre?A.reduce(U,p.d):null;if(pre){AV.verify(p.d,a.a);ok(a.a.free.length===d.k&&a.a.rows.length===0,"pre");}
   const e=pre?a.d:d,r=M.close(L,e);ok(r.kind!=="view"&&MV.verify(LV,e,r),"large certificate");
   rows.push({name,k:d.k,factors:d.F.length,pre,kind:r.kind,metrics:r.metrics});
  }return {rows};
 }
 if(section==="adapter"){
  const r=M.reduce(L,LV,MV,...Array(16).fill(null),comp);
  ok(r.contradiction&&r.cert.kind==="factor-conflict"&&r.d.k===1&&r.d.F.length===1&&!r.d.F[0].S.size,"adapter");
  return {adapter:{kind:r.cert.kind,k:r.d.k,allowed:r.d.F[0].S.size}};
 }
 if(section==="barrier"){
  const edges=[];for(let i=0;i<5;i++)for(let j=i+1;j<5;j++)edges.push([i,j]);const F=[];
  for(let i=0;i<5;i++){const v=edges.flatMap((e,j)=>e.includes(i)?[j]:[]),s=i===0?v[0]:-1;for(const h of U.subsets(v,3))F.push({h,S:new Set([...U.tuples(2,3)].filter(z=>{const y=z.map((x,j)=>x^+(h[j]===s));return y.some(x=>x!==y[0])}).map(z=>z.join()))});}
  const d={k:10,m:2,F},p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=M.close(L,a.d),l=L.discover(a.d),j=J.infer(N,G,B,H,C,I,P,a.d),t=D.tree(C,a.d,2000000);
  ok(!models(d).length&&a.a.free.length===10&&a.a.rows.length===0&&r.kind==="view"&&r.status==="fixed-point"&&!r.rounds.length&&l.kind==="unknown"&&j.kind==="unknown"&&j.status==="fixed-point"&&t.kind==="tree"&&T.verifyTree(a.d,t),"balance barrier");
  return {barrier:{k:10,factors:20,assignments:1024,metrics:r.metrics,count:l,iterative:j,tree:{work:t.work,nodes:t.nodes,leaves:t.leaves,splits:t.splits,units:t.units}}};
 }
 throw Error("section");
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_pair_counting.js'),require('./f038_rex_variable_pair_counting_certificate.js'),require('./f038_rex_variable_tight_counting.js'),require('./f038_rex_variable_tight_counting_certificate.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_conflict_cliques.js'),require('./f038_rex_variable_disjunction_alternatives.js'),require('./f038_rex_variable_implication_closure.js'),require('./f038_rex_variable_conditional_propagation.js'),require('./f038_rex_variable_iterative_consequences.js'),process.argv[2]||'oracle')));
