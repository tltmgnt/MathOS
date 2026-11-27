// D5E envelope regression. Phase execution is separate from full native replay.
function audit(U,Phase,Clock,A,B,W,F,R,C,V,L,E,Admission,name){
 const r=Phase.phaseAudit(Clock,A,B,W,F,R,C,V,L,E,Admission,name);
 return U.check([r])[0];
}
function arithmetic(U){
 let count=0;
 for(let m=2;m<=10000;m++){U.bound(m);count++;}
 for(let k of [20n,30n,40n,50n,100n,1024n])for(let d of [-1n,0n,1n]){U.bound((1n<<k)+d);count++;}
 const q=U.threshold(),rhs=H=>3n*(q.ell+q.C+3n*U.ceilLog(H+1n));
 let checks=0;
 for(let H of [q.H0-1n,q.H0,q.H0+1n,...Array.from({length:64},(_,i)=>1n<<BigInt(i+32)).flatMap(H=>[H-1n,H,H+1n])]){
  if((H>=q.H0)!==(H>=rhs(H)))throw Error("boundary arithmetic");checks++;
 }
 return {count,checks,threshold:Object.fromEntries(Object.entries(q).map(([k,v])=>[k,typeof v==="bigint"?v.toString():v]))};
}
module.exports={audit,arithmetic};
if(require.main===module){const U=require('./f038_rex_width_three_cubic_bound.js'),name=process.argv[2]||'arithmetic';if(name==='arithmetic')console.log('F038_REX_CUBIC_ARITHMETIC_OK '+JSON.stringify(arithmetic(U)));else {const Phase=require('./f038_rex_width_three_phase_audit.js'),Clock=require('./f038_rex_width_three_fast_clock.js'),A=require('./f038_rex_width_three_halt_witness.js'),B=require('./f038_rex_width_three_physical_bridge.js'),W=require('./f038_rex_width_three_witness_ir.js'),F=require('./f038_rex_width_three_forest_ir.js'),R=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),V=require('./f038_rex_width_three_projection.js'),L=require('./f038_rex_width_three_direct_loader.js'),E=require('./f038_tga_normalized_integration.js').engine(),Admission=require('./f038_rex_width_three_admission.js');console.log('F038_REX_CUBIC_PHASE_OK '+JSON.stringify(audit(U,Phase,Clock,A,B,W,F,R,C,V,L,E,Admission,name)));}}
