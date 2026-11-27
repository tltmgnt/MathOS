// Domain-four actual C1 checkpoint, observer-formatted D2C stream, exact worker clock and physical output projection.
function four(Fast,Space,A,B,W,F,R,C,V,L,E,Admission,Direct=null){
 const ok=(v,s)=>{if(!v)throw Error(s)},m=4,pins=[1,0,1,0],z=[3,2,1,0,3,2,1,0,3],clauses=z.flatMap((a,g)=>[0,1,2,3].filter(i=>i!==a).map(i=>[-(m*g+i+1)]));
 clauses.push(...[...E.subsets([0,3,6,8],2)].map(h=>h.map(v=>-(m*v+1))));
 const raw=E.encode(m,pins,clauses),J=V.compact(W.machine(F,R,C,V)),G=L.compile(),D={...L.decode(G.desc),plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry},p=L.run(D,raw,3000000000,null,true);
 ok(p.status==="WIDTH_THREE_FACTORS","C1 physical checkpoint");
 const h=p.snapshot.indexOf("H"),header=p.snapshot.slice(h,h+851).replaceAll("_","b"),q=p.checkpoint,fields=[(m-1).toString(2).split("").reverse().join(""),q.pins,...q.masks],stream=fields.map(s=>[...s].map(x=>"0"+x).join("")+"10").join("");
 // Observer-created canonical D2C stream from actual C1 mask data.
 // Verify every field against original factors, not a second copy of C1.
 const d=E.decode(raw),scopes=[1,2,3].flatMap(k=>[...E.subsets([0,1,2,3,4,5,6,7,8],k)]);
 ok(q.pins===pins.join("")&&q.masks.length===129&&q.masks.every((s,i)=>{let f=d.F.find(x=>x.h.join()===scopes[i].join());return s===[...E.tup(m,scopes[i].length)].map(t=>+(!!f&&!f.S.has(t.join()))).join("");}),"original mask oracle");
 let models=0;for(let r of E.tup(m,9))if(d.F.every(f=>f.S.has(f.h.map(g=>r[g]).join())))models++;
 ok(models===1,"unique latent model");
 const I=[...Array(19).fill(""),header,stream,...Array(40).fill("")],a=Fast.count(J,I),space=Space.space(m);
 ok(a.lengths.every((n,i)=>BigInt(n)<=space.caps[i]+2n)&&BigInt(a.N)<=space.N,"space");
 const O=A.projector(B.bridge(J)),r=A.run(O,a.encoded,69,10000000);
 ok(r.status==="HALT"&&r.witness===E.witness(m,pins,z)&&E.valid(raw,r.witness)&&r.nextSymbol===2,"projector");
 let direct=null;
 if(Direct){
  const G=Direct.compile(),D={...Direct.decode(G.desc),plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry,loaderEntry:G.loaderEntry},p2=Direct.run(D,raw,20000000000,null,true);
  ok(p2.status==="MASK_STREAM_LOADED"&&p2.stream===stream,"direct D2C stream");
  const h2=p2.snapshot.indexOf("H"),rawSuffix=p2.snapshot.slice(h2,h2+851).replace(/[H_]/g,"2")+stream;
  ok(p2.snapshot.slice(h2,h2+851).replaceAll("_","b")===header,"direct D2C header");
  const I=B.bridge(J),T=Uint32Array.from(I.T,v=>(v>>>4)===I.q+1?(I.q<<4)|(v&15):v),init=A.run({q:I.q,T},rawSuffix,1,5000000000);
  ok(init.status==="HALT"&&init.head===rawSuffix.length+1,"bridge");
  const t=p2.t+init.t+a.clock+r.t,head=p2.checkpoint.head+init.head+r.head,span=head+68-(p2.checkpoint.head-h2+1)+1;
  direct={producer:p2.t,bridge:init.t,t,head,span,slot:Admission.slot(69,928445994,t)};
 }
 const fieldsTotal=fields.reduce((n,s)=>n+s.length,0);
 return{direct,m,rawBits:raw.length,c1Clock:p.t,c1Span:p.span,models,fields:fields.length,fieldsTotal,stream:stream.length,steps:a.steps,workerClock:a.clock,workerBound:a.upper,N0:a.N0,N:a.N,spaceBound:Number(space.N),growth:a.growth,equalCarries:a.equalCarries,changedCarries:a.changedCarries,projection:r.t,witness:r.witness,encodedBits:a.encoded.length,slot:Admission.slot(69,928445994,null),lengths:a.lengths};
}
module.exports={four};
if(require.main===module){const Fast=require('./f038_rex_width_three_fast_clock.js'),Space=require('./f038_rex_width_three_space_bound.js'),A=require('./f038_rex_width_three_halt_witness.js'),B=require('./f038_rex_width_three_physical_bridge.js'),W=require('./f038_rex_width_three_witness_ir.js'),F=require('./f038_rex_width_three_forest_ir.js'),R=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),V=require('./f038_rex_width_three_projection.js'),L=require('./f038_rex_width_three_factors.js'),E=require('./f038_tga_normalized_integration.js').engine(),Admission=require('./f038_rex_width_three_admission.js');console.log('F038_REX_WIDTH_THREE_DOMAIN_FOUR_OK '+JSON.stringify(four(Fast,Space,A,B,W,F,R,C,V,L,E,Admission,process.argv[2]==='direct'?require('./f038_rex_width_three_direct_loader.js'):null)));}
