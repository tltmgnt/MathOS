// D7Q: exhaustive local hull completeness, mixed sources, regular exact-one and inequality limit.
function audit(U,Q,R,A,AV,L,N,NV,O,P,PV,J,JV,PN,C,D,T,I,IV,PNV,HV,PA,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);},models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(x=>z[x]).join()))).map(z=>z.join());
 const ex=h=>({h,S:new Set(["1,0,0","0,1,0","0,0,1"])}),nae=h=>({h,S:new Set(["0,0,1","0,1,0","0,1,1","1,0,0","1,0,1","1,1,0"])}),sig=k=>Array.from({length:k},(_,i)=>+(i*17%7<3));
 const regular=(k,s,t)=>({k,m:2,F:Array.from({length:k},(_,i)=>ex([i,(i+s)%k,(i+t)%k]))});
 const mixed={k:7,m:2,F:[...[...U.subsets([0,1,2,3],3)].map(nae),ex([4,5,6]),...Array.from({length:3},(_,i)=>({h:[i,i+4],S:new Set(["0,0","1,1"])})),{h:[3],S:new Set(["0"])}]};
 const binary=e=>{const p=I.closure(C,e);return p.kind==="view"?{kind:"unknown"}:p;};
 const verify=(d,p)=>JV.verify(NV,PV,IV,PNV,HV,d,p);
 if(section==="oracle"){
  const stats={cases:0,sat:0,unsat:0,models:0,views:0,records:0,direct:0,strict:0,conditional:0,unknown:0,localTypes:0,hullRows:0,empty:0,full:0,tamperRejected:0};
  function det(a){if(a.length===1)return a[0][0];return a[0].reduce((s,x,j)=>s+(j%2?-1:1)*x*det(a.slice(1).map(r=>r.filter((_,i)=>i!==j))),0);}
  function independentRank(a,n){for(let r=Math.min(a.length,n);r>0;r--)for(const rr of U.subsets(a,r))for(const cc of U.subsets(Array.from({length:n},(_,i)=>i),r))if(det(rr.map(x=>cc.map(i=>x[i]))))return r;return 0;}
  function check(d){
   const m=models(d),p=J.discover(P,O,N,L,A,d);stats.cases++;stats[m.length?"sat":"unsat"]++;stats.models+=m.length;
   if(p.kind==="view"){const v=JV.reconstruct(NV,PV,d,p);ok(JSON.stringify(models(v))===JSON.stringify(m)&&JSON.stringify(models(p.d))===JSON.stringify(m),"exact augmentation");stats.views++;stats.records+=p.records.length;
    const t=binary(v);if(p.records.length&&t.kind!=="unknown"){ok(!m.length&&verify(d,{...p,kind:"conditional",proof:t}),"conditional");stats.conditional++;}else stats.unknown++;
   }else{ok(!m.length&&verify(d,p),"direct");stats[p.kind==="direct"?"direct":"strict"]++;}
   return p;
  }
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){
   const h=Array.from({length:n},(_,i)=>n-1-i),z=[...U.tuples(2,n)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1),f={h,S:new Set(z.map(v=>v.join()))},basis=J.hull(f);
   if(!z.length){ok(basis.length===1&&basis[0].b===1&&basis[0].c.every(x=>!x),"empty");stats.empty++;}
   else{const rank=independentRank(z.slice(1).map(v=>v.map((x,i)=>x-z[0][i])),n);ok(basis.length===n-rank&&independentRank(basis.map(q=>q.c),n)===basis.length,"complete basis");if(rank===n)stats.full++;}
   for(const q of basis)ok(z.every(v=>v.reduce((s,x,i)=>s+x*q.c[i],0)===q.b),"local identity");
   stats.hullRows+=basis.length;stats.localTypes++;check({k:n,m:2,F:[f]});
  }
  for(let mask=0;mask<8;mask++){const d=PN.transform({k:3,m:2,F:[ex([0,1,2])]},Array.from({length:3},(_,i)=>mask>>i&1)).d,p=check(d);ok(p.kind==="view"&&p.records.length===3,"exact-one masks");}
  let seed=0xd7f224;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  for(let i=0;i<128;i++){const k=3+i%5,F=[];for(let j=0;j<2+i%9;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b),mask=rand()>>>16;F.push({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});}check({k,m:2,F});}
  const r=check(mixed),used=r.record.combination.map(([i])=>r.blocks[r.rows[i].source].kind);ok(used.includes("tight")&&used.includes("integer-local")&&used.includes("local"),"mixed sources");
  const prev=PA.fixture(U),p=check(prev);ok(p.kind==="view"&&p.records.length===172&&verify(prev,{...p,kind:"conditional",proof:binary(p.d)}),"prior discharge");
  const a=check(regular(7,1,3));ok(a.kind==="direct"||a.kind==="count-conflict","regular");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  const i=r.blocks.findIndex(b=>b.kind==="integer-local"),b=r.blocks[i];
  reject(()=>JV.verify(NV,PV,IV,PNV,HV,mixed,{...r,blocks:r.blocks.map((q,j)=>i===j?{...q,b:q.b+1}:q)}));
  reject(()=>JV.checkLocal(mixed,{...b,c:b.c.map((x,j)=>j?x:-x)}));reject(()=>JV.checkLocal(mixed,{...b,factor:0}));reject(()=>JV.checkLocal(mixed,{...b,h:[b.h[0],b.h[0],b.h[2]]}));
  reject(()=>JV.verify(NV,PV,IV,PNV,HV,mixed,{...r,rows:r.rows.map(q=>q.source===i?{...q,rule:"parity"}:q)}));reject(()=>JV.verify(NV,PV,IV,PNV,HV,mixed,{...r,record:{...r.record,combination:r.record.combination.slice(1)}}));
  const sat={k:3,m:2,F:[ex([0,1,2])]},lim=J.discover(P,O,N,L,A,sat,0),s=J.reduce(P,O,N,L,A,NV,PV,JV,IV,PNV,HV,sat,binary,d=>({d,cert:{kind:"sentinel"},expand:z=>z}),0);
  ok(lim.status==="budget"&&s.d===sat&&s.cert.kind==="sentinel","limits");
  return {stats,mixed:{used,prime:r.record.prime,combination:r.record.combination.length},priorRecords:p.records.length,limit:lim.metrics.probes};
 }
 if(section==="large"){
  const rows=[];for(const [k,s,t,pre,flip] of [[31,2,5,true,false],[127,1,7,true,false],[127,1,7,true,true],[253,1,7,false,true]]){
   let d=regular(k,s,t);if(flip)d=PN.transform(d,sig(k)).d;const p=pre?R.reduce(U,Q,d):null,a=pre?A.reduce(U,p.d):null;if(pre){AV.verify(p.d,a.a);ok(a.kind==="wide-fallback"&&a.d.k===k,"pre");}
   const e=pre?a.d:d,r=J.infer(P,O,N,L,A,e);ok(r.kind==="direct"&&r.record.prime===3&&r.record.combination.length===k&&verify(e,r),"large");
   rows.push({k,pre,flip,free:a?.a.free.length??null,metrics:r.metrics,discovery:r.discovery,combination:r.record.combination.length});
  }return {rows};
 }
 if(section==="barrier"){
  const k=31,d={k,m:2,F:[...Array.from({length:k},(_,i)=>({h:[i,(i+1)%k,(i+3)%k],S:new Set(["1,1,0","1,0,1","0,1,1","1,1,1"])})),...Array.from({length:k},(_,i)=>({h:[i,(i+4)%k,(i+9)%k],S:new Set(["0,0,0","1,0,0","0,1,0","0,0,1"])}))]};
  for(const half of [d.F.slice(0,k),d.F.slice(k)]){const deg=Array(k).fill(0);for(const f of half)f.h.forEach(x=>deg[x]++);ok(deg.every(x=>x===3),"regular inequality");}
  const p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=J.infer(P,O,N,L,A,a.d),t=D.tree(C,a.d,2000000);
  ok(!p.contradiction&&a.a.free.length===k&&!a.a.rows.length&&r.kind==="unknown"&&r.status==="complete"&&!r.metrics.probes&&r.discovery.integerHull.full===62&&t.kind==="tree"&&T.verifyTree(a.d,t),"barrier");
  return {barrier:{k,factors:d.F.length,free:a.a.free.length,r,tree:{work:t.work,nodes:t.nodes,leaves:t.leaves,splits:t.splits,units:t.units}}};
 }
 throw Error("section");
}
function physical(U,W,K,F,Min,A,L,N,NV,O,P,PV,J,JV){
 const d={k:31,m:2,F:Array.from({length:31},(_,i)=>({h:[i,(i+2)%31,(i+5)%31],S:new Set(["1,0,0","0,1,0","0,0,1"])}))},r=J.reduce(P,O,N,L,A,NV,PV,JV,null,null,null,d);
 if(!r.contradiction||r.cert.kind!=="direct")throw Error("adapter");
 const machine=W.machine(),M=W.singleExit(K.compile(machine)),N0=Min.refine(M),q={...M,...N0},s=W.stream(U,r.d),b=W.run(M,s,300000000),c=W.run(q,s,b.t),cut=W.run(q,s,b.t-1),clock=F.count(machine,["",s],M.codes);
 if(b.status!=="UNSAT"||b.z!==null||JSON.stringify(b)!==JSON.stringify(c)||b.t!==clock.clock||b.encoded!==clock.encoded||cut.status!=="TIMEOUT"||cut.t!==b.t-1||cut.z!==null)throw Error("physical");
 return {physical:{status:b.status,transitions:b.t,stream:s.length,clock:clock.clock,cutoff:cut.t,states:N0.stats.quotientStates,bits:N0.stats.quotientBits}};
}
module.exports={audit,physical};
if(require.main===module&&process.argv[2]==='physical')console.log(JSON.stringify(physical(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_pair_counting.js'),require('./f038_rex_variable_balanced_affine.js'),require('./f038_rex_variable_balanced_affine_certificate.js'),require('./f038_rex_variable_modular_balance.js'),require('./f038_rex_variable_conditional_modular.js'),require('./f038_rex_variable_conditional_modular_certificate.js'),require('./f038_rex_variable_integer_hull.js'),require('./f038_rex_variable_integer_hull_certificate.js'))));
else if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_pair_counting.js'),require('./f038_rex_variable_balanced_affine.js'),require('./f038_rex_variable_balanced_affine_certificate.js'),require('./f038_rex_variable_modular_balance.js'),require('./f038_rex_variable_conditional_modular.js'),require('./f038_rex_variable_conditional_modular_certificate.js'),require('./f038_rex_variable_integer_hull.js'),require('./f038_rex_variable_integer_hull_certificate.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_implication_closure.js'),require('./f038_rex_variable_implication_certificate.js'),require('./f038_rex_variable_polarity_certificate.js'),require('./f038_rex_variable_hall_certificate.js'),require('./f038_rex_variable_conditional_modular_audit.js'),process.argv[2]||'oracle')));
