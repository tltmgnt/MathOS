// D7R: local support oracle, positive combination search, and rational relaxation limit.
function fixture(U,k,lower=2){
 return {k,m:2,F:[...Array.from({length:k},(_,i)=>({h:[i,(i+1)%k,(i+3)%k],S:new Set([...U.tuples(2,3)].filter(z=>z.reduce((a,b)=>a+b)>=lower).map(z=>z.join()))})),...Array.from({length:k},(_,i)=>({h:[i,(i+4)%k,(i+9)%k],S:new Set(["0,0,0","1,0,0","0,1,0","0,0,1"])}))]};
}
function audit(U,Q,R,A,AV,J,JV,PN,C,D,T,section="oracle"){
 const ok=(x,s)=>{if(!x)throw Error(s);},models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(x=>z[x]).join())));
 const sig=k=>Array.from({length:k},(_,i)=>+(i*17%7<3));
 const multi={k:6,m:2,F:[{h:[0,2,3],S:new Set(["0,0,0","0,1,1","1,1,1"])},{h:[2,3,5],S:new Set(["0,1,0","1,1,0","1,1,1"])},{h:[1],S:new Set(["0","1"])},{h:[0],S:new Set(["0","1"])},{h:[2],S:new Set(["0"])},{h:[2,3,5],S:new Set(["0,0,0","0,0,1","0,1,0","1,0,1","1,1,0","1,1,1"])}]};
 if(section==="oracle"){
  const stats={cases:0,sat:0,unsat:0,models:0,certified:0,unknown:0,localTypes:0,supportRows:0,excludedRows:0,multiRound:0,boxConflicts:0,tamperRejected:0};
  function check(d){const m=models(d),r=J.discover(d);stats.cases++;stats[m.length?"sat":"unsat"]++;stats.models+=m.length;
   if(r.kind==="inequality-conflict"){ok(!m.length&&JV.verify(d,r),"soundness");stats.certified++;if(r.metrics.rounds>1)stats.multiRound++;if(r.lower!=="0")stats.boxConflicts++;}
   else stats.unknown++;return r;
  }
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){
   const z=[...U.tuples(2,n)],h=Array.from({length:n},(_,i)=>n-1-i),f={h,S:new Set(z.filter((_,i)=>mask>>i&1).map(v=>v.join()))},d={k:n,m:2,F:[f]},rows=J.supports(f);
   for(const r of rows){ok(JV.checkRow(d,{...r,f:0}),"local source");if(f.S.size)ok([...f.S].some(s=>r.h.reduce((v,x,i)=>v+r.a[i]*Number(s.split(",")[h.indexOf(x)]),0)===r.b),"support exact");}
   for(const v of z){const feasible=rows.every(r=>r.h.reduce((s,x,i)=>s+r.a[i]*v[h.indexOf(x)],0)<=r.b);ok(feasible===f.S.has(v.join()),"Boolean table exact");if(!feasible)stats.excludedRows++;}
   stats.supportRows+=rows.length;stats.localTypes++;check(d);
  }
  let seed=0xd7f324;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  for(let i=0;i<192;i++){const k=4+i%4,F=[];for(let j=0;j<3+i%7;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b),mask=rand()>>>16;F.push({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});}check({k,m:2,F});}
  const r=check(multi);ok(r.kind==="inequality-conflict"&&r.metrics.rounds===2&&r.lower==="-1"&&r.rhs==="-2","multi-round");
  const one=J.discover(multi,1);ok(one.kind==="unknown","one round limit");
  const zero=J.reduce(JV,multi,d=>({d,cert:{kind:"sentinel"},expand:z=>z}),0);ok(zero.d===multi&&zero.cert.kind==="sentinel","fallback");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  const t=r.terms[0];
  reject(()=>JV.verify(multi,{...r,terms:[{...t,multiplier:-1},...r.terms.slice(1)]}));
  reject(()=>JV.verify(multi,{...r,terms:[{...t,multiplier:0},...r.terms.slice(1)]}));
  reject(()=>JV.verify(multi,{...r,terms:[{...t,row:{...t.row,b:t.row.b-1}},...r.terms.slice(1)]}));
  reject(()=>JV.verify(multi,{...r,terms:[{...t,row:{...t.row,f:999}},...r.terms.slice(1)]}));
  reject(()=>JV.verify(multi,{...r,lower:"0"}));
  reject(()=>JV.verify(multi,{...r,rhs:"-999"}));
  return {stats,multi:{rounds:r.metrics.rounds,terms:r.terms.length,lower:r.lower,rhs:r.rhs,one:one.kind,zero:zero.inequality.metrics.rounds}};
 }
 if(section==="large"){
  const rows=[];for(const [k,flip,pre] of [[31,false,true],[31,true,true],[127,true,true],[1001,true,false]]){
   let d=fixture(U,k);if(flip)d=PN.transform(d,sig(k)).d;const p=pre?R.reduce(U,Q,d):null,a=pre?A.reduce(U,p.d):null;if(pre){AV.verify(p.d,a.a);ok(!p.contradiction&&a.a.free.length===k&&!a.a.rows.length,"pre");}
   const e=pre?a.d:d,r=J.discover(e);ok(r.kind==="inequality-conflict"&&r.lower==="0"&&r.rhs===String(-k)&&r.terms.length===2*k&&JV.verify(e,r),"large");
   rows.push({k,factors:d.F.length,flip,pre,lower:r.lower,rhs:r.rhs,terms:r.terms.length,metrics:r.metrics});
  }return {rows};
 }
 if(section==="barrier"){
  const d=fixture(U,31,1),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=J.discover(a.d),t=D.tree(C,a.d,2000000);
  let checked=0;for(let i=0;i<a.d.F.length;i++)for(const q of J.supports(a.d.F[i])){ok(JV.checkRow(a.d,{...q,f:i})&&q.a.reduce((s,x)=>s+x,0)<=3*q.b,"fractional feasible");checked++;}
  for(const fs of [d.F.slice(0,31),d.F.slice(31)]){const deg=Array(d.k).fill(0);for(const f of fs)f.h.forEach(x=>deg[x]++);ok(deg.every(x=>x===3),"degree");}
  ok(!p.contradiction&&a.a.free.length===31&&!a.a.rows.length&&r.kind==="unknown"&&t.kind==="tree"&&T.verifyTree(a.d,t),"integrality barrier");
  // 3*sum x >=31 and <=31. Integer division yields sum x>=11 and <=10.
  ok(Math.ceil(31/3)>Math.floor(31/3),"rounding");
  return {barrier:{k:31,factors:62,free:a.a.free.length,checked,fractionalNumerator:1,fractionalDenominator:3,rounded:[Math.ceil(31/3),Math.floor(31/3)],r,tree:{work:t.work,nodes:t.nodes,leaves:t.leaves,splits:t.splits,units:t.units}}};
 }
 throw Error("section");
}
module.exports={fixture,audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_inequality_certificates.js'),require('./f038_rex_variable_inequality_certificate.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),process.argv[2]||'oracle')));
