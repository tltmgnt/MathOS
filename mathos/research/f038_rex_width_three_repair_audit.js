// D5I: independent candidate oracle, actual direct mask stream and source-level resource tests.
function audit(U,P,E,F,V,Ad){
 const J=U.machine(),C=P.compile(),M={...P.decode(C.desc),bridgeReady:C.bridgeReady},ok=(x,s)=>{if(!x)throw Error(s)},rows=[];let checked=0,accepted=0,repaired=0,refused=0;
 for(let m=2;m<=6;m++)for(let g=0;g<9;g++){
  const pins=Array.from({length:m},(_,i)=>i%2),h=(g+1)%9,c=[[-(g*m+1),-(h*m+1)]],raw=E.encode(m,pins,c),I=[...Array(16).fill(""),U.stream(E,raw)],r=U.executeIR(J,I),z=Array(9).fill(0);z[Math.min(g,h)]=1;
  ok(r.status==="halt"&&r.tapes[0]===E.witness(m,pins,z)&&E.valid(raw,r.tapes[0]),"repair oracle");
  const a=F.count(J,I),v=V.envelope(m);ok(BigInt(a.N)<=2n*v.S&&BigInt(a.steps)<=1400n*v.S&&BigInt(a.clock)<=131072n*v.S*v.S,"resources");checked++;accepted++;repaired++;
 }
 for(const f of Ad.fixtures(E,"all").filter(f=>f.m<=3)){
  const s=U.stream(E,f.raw),r=U.executeIR(J,[...Array(16).fill(""),s]),p=P.run(M,f.raw,3000000000);
  ok(p.status==="MASK_STREAM_LOADED"&&p.stream===s,"producer mask oracle "+f.name);
  if(r.status==="halt"){ok(E.valid(f.raw,r.tapes[0]),"witness");accepted++;}else refused++;checked++;rows.push({name:f.name,producer:p.t,stream:s.length,ir:r.status});
 }
 const raw=E.encode(2,[0,0],[]);for(const bad of [raw.slice(0,-1),raw+"0",raw.slice(0,31)+"1"+raw.slice(32)]){const p=P.run(M,bad,3000000000);ok(p.status==="REFUSAL","malformed");}
 return {checked,accepted,repaired,refused,rows,malformed:3};
}
module.exports={audit};
if(require.main===module){const U=require('./f038_rex_width_three_repair_ir.js'),P=require('./f038_rex_width_three_repair_producer.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),Ad=require('./f038_rex_width_three_admission.js');console.log(JSON.stringify(audit(U,P,E,F,V,Ad)));}
