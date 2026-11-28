// D7P: shared source oracle, bounded assumption discharge, Hall composition and source-language limit.
function fixture(U){
 function mul(a,b){let r=0;while(b){if(b&1)r^=a;b>>=1;a<<=1;if(a&4)a^=7;}return r;}
 const lines=[];for(let x=0;x<4;x++)lines.push(Array.from({length:4},(_,y)=>4*x+y));for(let slope=0;slope<3;slope++)for(let b=0;b<4;b++)lines.push(Array.from({length:4},(_,x)=>4*x+(mul(slope,x)^b)));
 const sel=[0,2,3,4,6,8,9,10,11,12,13,14],ss=[[2,3],[0,3],[],[0,1],[],[2,3],[0,3],[1,2],[0,3],[1,2],[1,2],[1,2]];
 return {k:16,m:2,F:sel.flatMap((i,j)=>[...U.subsets(lines[i],3)].map(h=>({h,S:new Set([...U.tuples(2,3)].filter(z=>{const y=z.map((x,l)=>x^+ss[j].includes(lines[i].indexOf(h[l])));return y.some(x=>x!==y[0]);}).map(z=>z.join()))})))};
}
function audit(U,Q,R,A,AV,L,N,NV,O,PN,PNV,HV,C,I,IV,P,PV,H,B,G,D,T,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);},models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(x=>z[x]).join()))).map(z=>z.join());
 const nae=h=>({h,S:new Set(["0,0,1","0,1,0","0,1,1","1,0,0","1,0,1","1,1,0"])}),block=h=>[...U.subsets(h,3)].map(nae);
 const sig=k=>Array.from({length:k},(_,i)=>+(i*17%7<3)),prior=fixture(U);
 const binary=e=>{const p=I.closure(C,e);return p.kind==="view"?{kind:"unknown"}:p;};
 const structural=e=>I.infer(PN,G,B,H,C,e);
 const verify=(d,p)=>PV.verify(NV,IV,PNV,HV,d,p);
 if(section==="oracle"){
  const stats={cases:0,sat:0,unsat:0,models:0,views:0,records:0,strict:0,direct:0,conditional:0,unknown:0,tamperRejected:0,localTypes:0,masks:0};
  function check(d){
   const m=models(d),p=P.discover(O,N,L,A,d);stats.cases++;stats[m.length?"sat":"unsat"]++;stats.models+=m.length;
   if(p.kind==="view"){const v=PV.reconstruct(NV,d,p);ok(JSON.stringify(models(v))===JSON.stringify(m)&&JSON.stringify(models(p.d))===JSON.stringify(m),"model preservation");stats.views++;stats.records+=p.records.length;
    const t=binary(v);if(t.kind!=="unknown"){ok(!m.length&&verify(d,{...p,kind:"conditional",proof:t}),"nested");stats.conditional++;}else stats.unknown++;
   }else{ok(!m.length&&verify(d,p),"direct");stats[p.kind==="direct"?"direct":"strict"]++;}
   return p;
  }
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){const h=Array.from({length:n},(_,i)=>i),S=new Set([...U.tuples(2,n)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()));check({k:n,m:2,F:[{h,S}]});stats.localTypes++;}
  const b4={k:4,m:2,F:block([0,1,2,3])},g={k:4,m:2,F:[...b4.F,{h:[2],S:new Set(["1"])}]};
  for(let m=0;m<16;m++){const s=Array.from({length:4},(_,i)=>m>>i&1);check(PN.transform(b4,s).d);const p=check(PN.transform(g,s).d);ok(p.kind==="view"&&p.records.length>0,"conditional SAT");stats.masks++;}
  let seed=0xd7f124;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  for(let i=0;i<128;i++){const k=3+i%5,F=[];for(let j=0;j<2+i%9;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b),mask=rand()>>>16;F.push({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});}check({k,m:2,F});}
  const fano={k:7,m:2,F:[[0,1,2],[0,3,4],[0,5,6],[1,3,5],[1,4,6],[2,3,6],[2,4,5]].map(nae)};ok(check(fano).kind==="count-conflict","strict");
  const p=check(prior),r={...p,kind:"conditional",proof:binary(p.d)};ok(p.records.length===172&&verify(prior,r),"prior");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  const t=p.records[0];reject(()=>PV.reconstruct(NV,prior,{...p,records:[{...t,prime:4}]}));reject(()=>PV.reconstruct(NV,prior,{...p,records:[{...t,assume:[t.assume[0],t.assume[0]]}]}));reject(()=>PV.reconstruct(NV,prior,{...p,records:[{...t,combination:[]}]}));reject(()=>PV.reconstruct(NV,prior,{...p,records:[t,t]}));reject(()=>PV.reconstruct(NV,prior,{...p,rows:p.rows.map((q,i)=>i?q:{...q,b:q.b+1})}));reject(()=>verify(prior,{...r,proof:{...r.proof,paths:r.proof.paths.slice(1)}}));
  const lim=P.discover(O,N,L,A,g,4096,0),stop=P.discover(O,N,L,A,g,0),partial=P.infer(O,N,L,A,prior,binary,250);
  ok(lim.status==="budget"&&!lim.metrics.work&&stop.status==="budget"&&!stop.metrics.probes&&JSON.stringify(models(PV.reconstruct(NV,g,lim)))===JSON.stringify(models(g))&&partial.kind==="conditional"&&partial.status==="budget"&&verify(prior,partial),"limits");
  const retained=P.reduce(O,N,L,A,NV,PV,IV,PNV,HV,g,binary,d=>({d,cert:{kind:"sentinel"},contradiction:false,expand:z=>z}),0);
  ok(retained.d===g&&retained.cert.kind==="sentinel","fallback exact input");
  return {stats,limits:{zeroWork:lim.metrics.work,zeroProbes:stop.metrics.probes,partialRecords:partial.records.length,partialProbes:partial.metrics.probes,partialWork:partial.metrics.work,partialPaths:partial.proof.paths.map(p=>p.steps.length)}};
 }
 if(section==="large"){
  const controls={k:416,m:2,F:[...prior.F,...Array.from({length:100},(_,i)=>block([16+4*i,17+4*i,18+4*i,19+4*i])).flat()]},out=[];
  for(const [name,d,pre] of [["prior",prior,true],["signed",PN.transform(prior,sig(16)).d,true],["controls",controls,false]]){
   const p=pre?R.reduce(U,Q,d):null,a=pre?A.reduce(U,p.d):null;if(pre){AV.verify(p.d,a.a);ok(a.a.free.length===d.k&&!a.a.rows.length,"pre");}
   const e=pre?a.d:d,r=P.infer(O,N,L,A,e,binary);ok(r.kind==="conditional"&&verify(e,r),"family");
   out.push({name,k:d.k,factors:d.F.length,pre,status:r.status,metrics:r.metrics,discovery:r.discovery,paths:r.proof.paths.map(p=>p.steps.length)});
  }return {rows:out};
 }
 if(section==="hall"){
  const raw=D.php(U,3);let k=raw.k,F=[];for(const f of raw.F){if(f.h.length!==2){F.push(f);continue;}const h=[...f.h,k++,k++];F.push(...block(h),{h:[h[2]],S:new Set(["1"])});}
  const d={k,m:2,F},r=P.reduce(O,N,L,A,NV,PV,IV,PNV,HV,d,structural);
  ok(r.contradiction&&r.cert.kind==="conditional"&&r.cert.proof.kind==="reach-hall"&&verify(d,r.cert),"Hall integration");
  return {hall:{k,factors:F.length,metrics:r.cert.metrics,discovery:r.cert.discovery,proof:r.cert.proof.kind,nested:r.cert.proof.proof.kind,kReduced:r.d.k,allowed:r.d.F[0].S.size}};
 }
 if(section==="barrier"){
  const rows=[];for(const [k,s,t] of [[31,2,5],[127,1,7]]){
   const d={k,m:2,F:Array.from({length:k},(_,i)=>({h:[i,(i+s)%k,(i+t)%k],S:new Set(["1,0,0","0,1,0","0,0,1"])}))},deg=Array(k).fill(0);
   for(const f of d.F)for(const x of f.h)deg[x]++;ok(deg.every(x=>x===3)&&k%3!==0,"integer count contradiction");
   const p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=P.infer(O,N,L,A,a.d,structural),q=D.tree(C,a.d,2000000);
   ok(a.kind==="wide-fallback"&&a.d.k===k&&r.kind==="unknown"&&r.status==="complete"&&!r.metrics.probes&&q.kind==="tree"&&T.verifyTree(a.d,q),"source limitation");
   rows.push({k,factors:k,free:a.a.free.length,localRows:a.a.rows.length,modular:r,tree:{work:q.work,nodes:q.nodes,leaves:q.leaves,splits:q.splits,units:q.units}});
  }return {barrier:rows};
 }
 throw Error("section");
}
module.exports={fixture,audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_pair_counting.js'),require('./f038_rex_variable_balanced_affine.js'),require('./f038_rex_variable_balanced_affine_certificate.js'),require('./f038_rex_variable_modular_balance.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_polarity_certificate.js'),require('./f038_rex_variable_hall_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_implication_closure.js'),require('./f038_rex_variable_implication_certificate.js'),require('./f038_rex_variable_conditional_modular.js'),require('./f038_rex_variable_conditional_modular_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_conflict_cliques.js'),require('./f038_rex_variable_disjunction_alternatives.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),process.argv[2]||'oracle')));
