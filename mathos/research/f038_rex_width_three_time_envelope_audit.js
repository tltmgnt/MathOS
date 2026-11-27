// Exact raw-IR phase accounting vs compact lowering, on independently checked C1 masks.
function audit(Time,Fast,Space,W,F,R,C,V,L,E,Admission,name){
 const f=Admission.fixtures(E,name)[0],ok=(v,s)=>{if(!v)throw Error(s)},J0=W.machine(F,R,C,V),J=V.compact(J0),G=L.compile(),D={...L.decode(G.desc),plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry},p=L.run(D,f.raw,3000000000,null,true);
 ok(p.status==="WIDTH_THREE_FACTORS","C1 physical");
 const q=p.checkpoint,h=p.snapshot.indexOf("H"),header=p.snapshot.slice(h,h+851).replaceAll("_","b"),fields=[(f.m-1).toString(2).split("").reverse().join(""),q.pins,...q.masks],stream=fields.map(s=>[...s].map(x=>"0"+x).join("")+"10").join("");
 const d=E.decode(f.raw),scopes=[1,2,3].flatMap(k=>[...E.subsets([0,1,2,3,4,5,6,7,8],k)]);
 ok(q.pins===f.pins.join("")&&q.masks.length===129&&q.masks.every((s,i)=>{let a=d.F.find(x=>x.h.join()===scopes[i].join());return s===[...E.tup(f.m,scopes[i].length)].map(t=>+(!!a&&!a.S.has(t.join()))).join("");}),"mask oracle");
 const I=[...Array(19).fill(""),header,stream,...Array(40).fill("")],a=Time.countPhases(J0,I,Space,f.m),b=Fast.count(J,I);
 ok(a.steps===b.steps&&a.tapes.join("|")===b.tapes.join("|")&&a.heads.join()===b.heads.join(),"exact raw/compact");
 ok(b.tapes[57]===(f.witness??"")&&(f.witness===null||E.valid(f.raw,b.tapes[57])),"witness");
 const sp=Space.space(f.m);
 ok(b.lengths.every((n,i)=>BigInt(n)<=sp.caps[i]+2n)&&BigInt(b.N)<=sp.N&&BigInt(b.clock)<=BigInt(a.bounds.physical),"space/clock");
 return {name,m:f.m,producer:p.t,steps:a.steps,totals:a.totals,ledger:a.ledger,bounds:a.bounds,worker:b.clock,N:b.N,witness:b.tapes[57]||null};
}
module.exports={audit};
if(require.main===module){const Time=require('./f038_rex_width_three_time_envelope.js'),Fast=require('./f038_rex_width_three_fast_clock.js'),Space=require('./f038_rex_width_three_space_bound.js'),W=require('./f038_rex_width_three_witness_ir.js'),F=require('./f038_rex_width_three_forest_ir.js'),R=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),V=require('./f038_rex_width_three_projection.js'),L=require('./f038_rex_width_three_factors.js'),E=require('./f038_tga_normalized_integration.js').engine(),Admission=require('./f038_rex_width_three_admission.js');console.log('F038_REX_WIDTH_THREE_TIME_OK '+JSON.stringify(audit(Time,Fast,Space,W,F,R,C,V,L,E,Admission,process.argv[2]||'empty')));}
