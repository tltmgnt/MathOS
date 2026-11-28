// FV-07: actual relational/affine preparation, D7I certificate, physical replay,
// and independently checked original-instance release.
const req=n=>require('./f038_rex_'+n+'.js');
const [U,Q,R,A,AV,C,D,H,B,G,N,I,E,P,K,Clock,Min,Physical,F]=[
 "variable_rank_reduction","variable_rank_quotient","variable_relational_closure","variable_affine_closure","variable_affine_certificate","variable_resolution_closure","variable_adaptive_inference","variable_hall_inference","variable_conflict_cliques","variable_disjunction_alternatives","variable_polarity_normalization","variable_implied_conflicts","fv04_export","variable_rank_worker","width_three_local_motion_compiler","width_three_local_motion_clock","width_two_quotient","fv06_audit","fv07_composition"].map(req);
const ok=(b,m)=>{if(!b)throw Error("FV07: "+m);};
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const factor=(h,rows)=>({h,S:new Set(rows)});
const constant=()=>({k:1,m:2,F:[factor([0],[])]});
function split(d){
 let k=d.k,fs=[];for(const f of d.F){
  if(f.h.length!==2){fs.push(f);continue;}
  const [x,y]=f.h,u=k++;fs.push(factor([x,u],["0,0","0,1","1,1"]),factor([u,y],["0,0","0,1","1,0"]));
 }return {k,m:2,F:fs};
}
function emptyEvidence(d){
 const raw=F.raw(d),proof={kind:"resolution",left:{kind:"source",index:0,row:[false]},right:{kind:"source",index:0,row:[true]},pivot:1};
 return {kind:"residual",data:{...raw,packet:{retained:[0],paths:[],holeCount:0,groups:[{options:[],proof}],placements:[],conflicts:[]}}};
}
function prep(d){
 const p=R.reduce(U,Q,d,true);
 if(p.contradiction)return {d:p.d,expand:p.expand,kind:"relational-contradiction"};
 const a=A.reduce(U,p.d);AV.verify(p.d,a.a);
 return {d:a.d,expand:z=>p.expand(a.expand(z)),kind:a.kind};
}
function audit(){
 const J=P.machine(),M=P.singleExit(K.compile(J)),ref=Min.refine(M),min={...M,...ref};
 Physical.checkQuotient(M,min,ref.map);
 function run(d,fuel){
  const s=P.stream(U,d),a=P.run(M,s,fuel),b=P.run(min,s,fuel),c=Physical.sparseRun(min,s,fuel);
  ok(same(a,b)&&same(a,c),"physical agreement");
  return a;
 }
 function terminal(d){
  const s=P.stream(U,d),clock=Clock.count(J,["",s],M.codes),r=run(d,clock.clock);
  ok(r.status!=="TIMEOUT"&&r.t===clock.clock&&r.encoded===clock.encoded,"exact clock");return r;
 }
 const rows=[];let cutoffs=0;
 for(const [name,d] of [
  ["free",{k:1,m:2,F:[]}],
  ["equal",{k:2,m:2,F:[factor([0,1],["0,0","1,1"])]}],
  ["forced",{k:2,m:2,F:[factor([0,1],["0,0","1,1"]),factor([1],["1"])]}],
  ["ternary",{k:3,m:2,F:[factor([0,1,2],["0,1,1","1,0,0","1,1,1"])]}],
  ["local-conflict",{k:2,m:2,F:[factor([0],["0"]),factor([0],["1"])]}]
 ]){
  const p=prep(d),r=terminal(p.d),ev=r.status==="UNSAT"?emptyEvidence(p.d):null,
   result=F.release(d,p.d,p.expand,r,ev),models=[...F.assignments(d.k)].filter(x=>F.model(d,x));
  ok(F.exactImage(d,p.d,p.expand),"finite exact image");
  ok(result.status===(models.length?"SAT":"UNSAT")&&same(result.witness,models[0]??null),"original oracle");
  ok(F.release(d,p.d,p.expand,run(p.d,r.t-1),ev).status==="UNKNOWN","cutoff");cutoffs++;
  rows.push({name,k:d.k,residual:p.d.k,kind:p.kind,status:result.status,witness:result.witness,transitions:r.t});
 }
 for(const [holes,mode] of [[3,"plain"],[6,"plain"],[6,"signed"]]){
  let d=split(D.php(U,holes));
  if(mode==="signed")d=N.transform(d,Array.from({length:d.k},(_,i)=>+(i%2===0))).d;
  const p=prep(d),cert=I.infer(N,G,B,H,C,d);
  ok(cert.kind==="implied-hall","original proof");
  const residualCert=I.infer(N,G,B,H,C,p.d);
  ok(residualCert.kind==="implied-hall","prepared residual proof");
  const evidence={kind:"direct",data:E.exportPacket(d,cert)},target=constant(),r=terminal(target);
  const result=F.release(d,target,()=>{throw Error("UNSAT");},r,evidence);
  ok(result.status==="UNSAT","bound original certificate");
  ok(F.release(d,target,z=>z,run(target,r.t-1),evidence).status==="UNKNOWN","cutoff");cutoffs++;
  rows.push({name:"split-"+holes+"-"+mode,k:d.k,residual:p.d.k,kind:cert.hall.kind,status:result.status,witness:null,transitions:r.t,paths:cert.paths.length});
 }
 const d={k:1,m:2,F:[factor([0],["1"])]},target=constant(),r=terminal(target),bad=emptyEvidence(target);
 const test=(b,m)=>ok(b.status==="UNKNOWN",m);let rejected=0;
 for(const [result,label] of [
  [F.release(d,target,z=>z,r,null),"missing evidence"],
  [F.release(d,target,z=>z,r,bad),"false residual transfer"],
  [F.release(d,target,z=>z,r,{kind:"direct",data:bad.data}),"wrong source packet"],
  [F.release(d,d,z=>z,{status:"SAT",z:[0]}),"false witness"],
  [F.release(d,d,()=>[0],{status:"SAT",z:[1]}),"bad reconstruction"],
  [F.release(d,d,z=>z,{status:"SAT",z:[1,0]}),"wrong witness length"],
  [F.release(d,d,z=>z,{status:"bogus"}),"bad status"],
  [F.release({k:11,m:2,F:[]},target,z=>z,r,bad),"unproved large transfer"]
 ]){test(result,label);rejected++;}
 const packet=emptyEvidence(target);packet.data.packet.groups[0].proof.left.index=99;
 test(F.release(target,target,z=>z,r,packet),"tampered packet");rejected++;
 return {rows,cutoffs,rejected};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit()));
