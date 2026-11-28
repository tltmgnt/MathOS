// D7D independently checked closure obstruction, budget fallback, model oracle and reduced physical replay.
function audit(U,Q,R,A,AV,C,V,D,T,P,K,F,Min){
 const ok=(b,s)=>{if(!b)throw Error(s);};
 const stats={cases:0,models:0,sat:0,unsat:0,indexedRefuted:0,treeRefuted:0,unknownUnsat:0,localMasks:0,tamperRejected:0};
 function factor(h,mask){return {h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((a,b,i)=>a+(b<<i),0))&1).map(z=>z.join()))};}
 function models(d){return [...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join()))).map(z=>z.join());}
 function check(d){
  const expected=models(d),r=D.reduce(C,V,T,d,20000),actual=models(r.d).map(t=>r.expand(t.split(",").map(Number)).join());
  ok(JSON.stringify(expected)===JSON.stringify(actual),"models");
  stats.cases++;stats.models+=expected.length;stats[expected.length?"sat":"unsat"]++;
  if(r.contradiction)ok(!expected.length,"false contradiction");else if(!expected.length)stats.unknownUnsat++;
  if(r.cert.kind==="resolution")stats.indexedRefuted++;if(r.cert.kind==="tree")stats.treeRefuted++;
  return r;
 }
 for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){check({k:n,m:2,F:[factor(Array.from({length:n},(_,i)=>i),mask)]});stats.localMasks++;}
 for(let k of [2,3])for(let mask=0;mask<256;mask++){
  const F=[];
  if(k===2){const scopes=[[0],[0],[1],[1],[0,1],[0,1],[0,1],[0,1]];for(let j=0;j<8;j++)if(mask>>j&1)F.push(factor(scopes[j],((1<<(2**scopes[j].length))-1)^(1<<(j<4?j%2:j-4))));}
  else for(let j=0;j<8;j++)if(mask>>j&1)F.push(factor([0,1,2],255^(1<<j)));
  check({k,m:2,F});
 }
 let seed=0xd7c024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let t=0;t<128;t++){const k=3+t%4,F=[];for(let j=0;j<2+t%11;j++){const h=[...new Set(Array.from({length:1+rand()%3},()=>rand()%k))].sort((a,b)=>a-b);F.push(factor(h,rand()>>>16));}check({k,m:2,F});}
 const nae=k=>({k,m:2,F:[...U.subsets(Array.from({length:k},(_,i)=>i),3)].map(h=>factor(h,126))});
 const fano={k:7,m:2,F:[[0,1,2],[0,3,4],[0,5,6],[1,3,5],[1,4,6],[2,3,6],[2,4,5]].map(h=>factor(h,126))};
 const indexRows=[];
 for(const [name,d] of [["NAE5",nae(5)],["Fano",fano]]){
  const old=C.resolution(d,4),r=D.indexed(C,d,4,2000000);ok(old.kind==="resolution"&&r.kind==="resolution"&&V.verify(d,r),"index proof");
  indexRows.push({name,oldPairs:old.pairs,newPairs:r.pairs,oldNodes:old.nodes.length,newNodes:r.nodes.length,work:r.work});
 }
 check(nae(4));check(nae(5));check(fano);
 const d=D.php(U,5),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);
 ok(!p.contradiction&&p.d.k===42&&a.a.free.length===42&&a.a.rows.length===0&&C.cardinality(a.d).kind==="unknown","predecessor survival");
 const saturated=D.indexed(C,a.d,4,20000000);
 const closure=T.verifyClosure(a.d,saturated);ok(saturated.reason==="saturated"&&closure.axioms===93,"closure");
 const tr=D.tree(C,a.d,2000000);ok(T.verifyTree(a.d,tr),"tree proof");
 const limited=D.reduce(C,V,T,a.d,1000);ok(!limited.contradiction&&limited.cert.reason==="budget"&&limited.first.reason==="budget"&&limited.d===a.d,"budget fallback");
 const adapted=D.reduce(C,V,T,a.d,2000000);ok(adapted.contradiction&&adapted.cert.kind==="tree"&&adapted.first.reason==="budget","adaptive");
 function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
 reject(()=>T.verifyClosure(a.d,{...saturated,closure:[]}));
 reject(()=>T.verifyClosure(a.d,{...saturated,closure:[...saturated.closure,[]]}));
 reject(()=>T.verifyTree(a.d,{...tr,root:{...tr.root,v:-1}}));
 reject(()=>T.verifyTree(a.d,{...tr,root:{...tr.root,one:null}}));
 reject(()=>T.verifyTree(a.d,{...tr,root:{type:"conflict",f:0,c:[1,2,31]}}));
 const J=P.machine(),M=P.singleExit(K.compile(J)),N0=Min.refine(M),N={...M,...N0};
 const ns=P.stream(U,adapted.d),b=P.run(M,ns,300000000),c=P.run(N,ns,b.t),cut=P.run(N,ns,b.t-1),clock=F.count(J,["",ns],M.codes);
 ok(b.status==="UNSAT"&&b.z===null&&JSON.stringify(b)===JSON.stringify(c)&&b.t===clock.clock&&b.encoded===clock.encoded&&cut.status==="TIMEOUT"&&cut.t===b.t-1&&cut.z===null,"physical replay");
 const {closure:_,...saturationStats}=saturated,{root:__,...treeStats}=tr;
 return {stats,indexRows,barrier:{k:d.k,factors:d.F.length,pre:p.d.k,free:a.a.free.length,equations:a.a.rows.length,saturation:saturationStats,closure,tree:treeStats,limited:{first:limited.first.reason,final:limited.cert.reason},physical:{transitions:b.t,stream:ns.length,clockChecks:1,cutoffs:1,states:N0.stats.quotientStates,bits:N0.stats.quotientBits}}};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'))));
