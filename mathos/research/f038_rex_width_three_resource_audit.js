// Regression: exact scan-based and adjacency-count clock models agree, including terminal encoding.
function audit(U,Fast,Space,W,F,R,C,V,L,E,Admission,name){
 const f=Admission.fixtures(E,name)[0],ok=(v,s)=>{if(!v)throw Error(s)},J=V.compact(W.machine(F,R,C,V)),G=L.compile(),D={...L.decode(G.desc),loaderEntry:G.loaderEntry,plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry};
 const p=L.run(D,f.raw,5000000000,null,true);ok(p.status==="MASK_STREAM_LOADED","producer");
 const h=p.snapshot.indexOf("H"),I=[...Array(19).fill(""),p.snapshot.slice(h,h+851).replaceAll("_","b"),p.stream,...Array(40).fill("")];
 const a=U.count(J,I),b=Fast.count(J,I),{lengths,...rest}=b,sp=Space.space(f.m);
 ok(JSON.stringify(a)===JSON.stringify(rest),"exact clock equality");
 ok(lengths.every((n,i)=>BigInt(n)<=sp.caps[i]+2n)&&BigInt(b.N)<=sp.N,"space");
 return {name,clock:b.clock,N:b.N,steps:b.steps,upper:b.upper,growth:b.growth,spaceBound:Number(sp.N),witness:b.tapes[57]};
}
module.exports={audit};
if(require.main===module){const U=require('./f038_rex_width_three_clock_audit.js'),Fast=require('./f038_rex_width_three_fast_clock.js'),Space=require('./f038_rex_width_three_space_bound.js'),W=require('./f038_rex_width_three_witness_ir.js'),F=require('./f038_rex_width_three_forest_ir.js'),R=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),V=require('./f038_rex_width_three_projection.js'),L=require('./f038_rex_width_three_direct_loader.js'),E=require('./f038_tga_normalized_integration.js').engine(),Admission=require('./f038_rex_width_three_admission.js');console.log('F038_REX_WIDTH_THREE_RESOURCE_OK '+JSON.stringify(audit(U,Fast,Space,W,F,R,C,V,L,E,Admission,process.argv[2]||'empty')));}
