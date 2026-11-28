// D6X executed producer comparison and batch counts for m=2,3,4.
function profile(P,Old,U,E,H,D){
 const C=P.compile(true),M=P.decode(C.desc),O=Old.compile(),OM={...Old.decode(O.desc),bridgeReady:O.bridgeReady},out=[];
 const flags=C.names.map(([n])=>n==="fastConsume0"?1:n.endsWith("Try4")?2:n==="shortConsume0"?3:n.endsWith("Try2")?4:0);
 for(const m of [2,3,4]){
  const raw=E.encode(m,Array(m).fill(0),m===2?D.family(E,2,1,false):H.family(E,m,false)),o=3*raw.length+1024,a=new Uint8Array(6*raw.length+4096);
  a.fill(2);for(let i=0;i<raw.length;i++)a[o+i]=+raw[i];
  let q=0,h=o,t=0;const count=new Float64Array(5);
  while(q!==M.q&&t<30000000000){count[flags[q]]++;const v=M.T[3*q+a[h]];a[h]=v>>2&3;h+=(v&3)-1;q=v>>>4;t++;}
  let e=h+1;while(a[e]<2)e++;const stream=U.stream(E,raw);
  if(q!==M.q||Array.from(a.slice(h+1,e)).join("")!==stream)throw Error("stream");
  const b=Old.run(OM,raw,30000000000);if(b.stream!==stream)throw Error("old");
  out.push({m,t,old:b.t,four:count[1],fourAttempts:count[2],two:count[3],twoAttempts:count[4]});
 }
 return out;
}
module.exports={profile};
if(require.main===module)console.log(JSON.stringify(profile(require("./f038_rex_width_three_short_batch_producer.js"),require("./f038_rex_width_three_shared_deposit_producer.js"),require("./f038_rex_width_three_lazy_interval_ir.js"),require("./f038_tga_normalized_integration.js").engine(),require("./f038_rex_width_three_two_prefix_hard.js"),require("./f038_rex_width_three_direct_extension_audit.js"))));
