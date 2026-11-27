// REX-024D5B: predict joined clock using physical producer/bridge/projector and exact IR lowering accounting.
function phaseAudit(U,A,B,W,F,R,C,V,L,E,Admission,name){
 const f=Admission.fixtures(E,name)[0],ok=(v,s)=>{if(!v)throw Error(s)},J=V.compact(W.machine(F,R,C,V)),G=L.compile(),D={...L.decode(G.desc),loaderEntry:G.loaderEntry,plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry};
 const p=L.run(D,f.raw,5000000000,null,true);ok(p.status==="MASK_STREAM_LOADED","producer");
 const at=p.snapshot.indexOf("H"),header=p.snapshot.slice(at,at+851),rawSuffix=header.replace(/[H_]/g,"2")+p.stream,inputs=[...Array(19).fill(""),header.replaceAll("_","b"),p.stream,...Array(40).fill("")];
 const a=U.count(J,inputs),I=B.bridge(J),w=I.w;
 // Isolated exact bridge replay on literal producer suffix: distinct
 // execution, not a claim of end-to-end native replay.
 const T=Uint32Array.from(I.T,v=>(v>>>4)===I.q+1?(I.q<<4)|(v&15):v);
 const init=A.run({q:I.q,T},rawSuffix,1,2000000000);
 ok(init.status==="HALT"&&init.head===rawSuffix.length+1,"bridge halt");
 const codes=I.codes,O=A.projector(I),out=A.run(O,a.encoded,f.n,10000000);
 ok(out.status==="HALT"&&out.witness===f.witness&&out.head===a.encoded.length+1,"projector");
 if(f.witness!==null)ok(E.valid(f.raw,out.witness)&&out.nextSymbol===2,"witness");else ok(out.headSymbol===2,"blank");
 const t=p.t+init.t+a.clock+out.t,head=p.checkpoint.head+init.head+out.head;
 const lo=p.checkpoint.head-at+1,span=head+Math.max(0,(f.witness?.length??0)-1)-lo+1;
 ok(f.clock===null||(t===f.clock&&head===f.head&&span===f.span),"original total");
 const bound=(26*a.N+16)*a.steps+8;ok(bound===a.upper,"explicit worker bound");
 return {name,m:f.m,t,head,span,witness:out.witness,producer:p.t,bridge:init.t,worker:a.clock,projection:out.t,steps:a.steps,N0:a.N0,N:a.N,growth:a.growth,equalCarries:a.equalCarries,changedCarries:a.changedCarries,upper:bound,slot:out.witness===null?null:Admission.slot(f.n,928445994,t)};
}
module.exports={phaseAudit};
if(require.main===module){const U=require('./f038_rex_width_three_clock_audit.js'),A=require('./f038_rex_width_three_halt_witness.js'),B=require('./f038_rex_width_three_physical_bridge.js'),W=require('./f038_rex_width_three_witness_ir.js'),F=require('./f038_rex_width_three_forest_ir.js'),R=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),V=require('./f038_rex_width_three_projection.js'),L=require('./f038_rex_width_three_direct_loader.js'),E=require('./f038_tga_normalized_integration.js').engine(),Admission=require('./f038_rex_width_three_admission.js');console.log('F038_REX_WIDTH_THREE_CLOCK_OK '+JSON.stringify(phaseAudit(U,A,B,W,F,R,C,V,L,E,Admission,process.argv[2]||'empty')));}
