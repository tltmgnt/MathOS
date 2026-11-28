// D7C integration: predecessor algebra, verified contradiction adapter and exact physical replay.
function audit(U,Q,R,A,AV,C,V,P,K,F,Min){
 const ok=(b,msg)=>{if(!b)throw Error(msg);},J=P.machine(),M=P.singleExit(K.compile(J)),N0=Min.refine(M),N={...M,...N0};
 const factor=(h,fn)=>({h,S:new Set([...U.tuples(2,h.length)].filter(fn).map(z=>z.join()))});
 const nae=k=>({k,m:2,F:[...U.subsets(Array.from({length:k},(_,i)=>i),3)].map(h=>factor(h,z=>z.some(x=>x!==z[0])))});
 const cases=[["NAE5",nae(5)],["NAE4",nae(4)],["narrow-mixed",{k:4,m:2,F:[factor([0,1,3],z=>(z[0]^z[1])===z[2]),factor([2,3],z=>z[0]+z[1]<=1)]}],["wide-mixed",{k:6,m:2,F:[factor([0,1,4],z=>(z[0]^z[1])===z[2]),factor([2,3,5],z=>(z[0]^z[1])===z[2]),factor([4,5],z=>z[0]+z[1]<=1)]}]];
 const rows=[];
 for(const [name,d] of cases){
  const pre=R.reduce(U,Q,d),a=A.reduce(U,pre.d);AV.verify(pre.d,a.a);
  const c=C.reduce(a.d,V.verify),os=P.stream(U,a.d),ns=P.stream(U,c.d);
  const old=P.run(N,os,300000000),newRun=P.run(M,ns,300000000),min=P.run(N,ns,newRun.t),cut=P.run(N,ns,newRun.t-1);
  const oc=F.count(J,["",os],M.codes),nc=F.count(J,["",ns],M.codes);
  const expected=[...U.tuples(2,d.k)].find(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))??null;
  const oldZ=old.z?pre.expand(a.expand(old.z)):null,newZ=newRun.z?pre.expand(a.expand(c.expand(newRun.z))):null;
  ok(old.status===newRun.status&&old.status===(expected?"SAT":"UNSAT")&&JSON.stringify(oldZ)===JSON.stringify(expected)&&JSON.stringify(newZ)===JSON.stringify(expected),"witness "+name);
  ok(old.t===oc.clock&&old.encoded===oc.encoded&&newRun.t===nc.clock&&newRun.encoded===nc.encoded,"clock "+name);
  ok(JSON.stringify(min)===JSON.stringify(newRun)&&cut.status==="TIMEOUT"&&cut.t===newRun.t-1&&cut.z===null,"replay "+name);
  rows.push({name,affineKind:a.kind,certificate:c.cert.kind,status:newRun.status,oldPhysical:old.t,newPhysical:newRun.t});
 }
 return {rows,clockChecks:2*rows.length,cutoffs:rows.length,resources:{logical:J.ins.length,...N0.stats}};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'))));
