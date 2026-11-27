// D6V phase counters from executed producer rows, not source estimates.
function profile(P,U,E,H){
 const C=P.compile(true),M=P.decode(C.desc),raw=E.encode(4,[0,0,0,0],H.family(E,4,false)),o=3*raw.length+1024,a=new Uint8Array(6*raw.length+4096);
 a.fill(2);for(let i=0;i<raw.length;i++)a[o+i]=+raw[i];
 const cats=["deposit-traversal","deposit-mask","batch-traversal","batch-mask","batch-probe","fit","normalization","load","compact"],category=C.names.map(([n])=>/^deposit.*(Work|Prefix)$/.test(n)?0:n.startsWith("deposit")?1:/^(covered.*Fast(Work|Prefix)|fastBackPrefix|fastBackWork)$/.test(n)?2:/^(fastShift|fastFlush|fastReturn|covered.*Fast(Seek|Fix|Probe|Begin))/.test(n)?3:/^covered.*(Try4|Fast(Check|Fail|GoodBack))/.test(n)?4:/^class3(R|W|Back|W[0-9])/.test(n)?5:/^(load|trim|bridgeReady)/.test(n)?7:/^compact/.test(n)?8:6);
 const entries=C.names.map(([n])=>+(n==="fastConsume0")),tries=C.names.map(([n])=>+n.endsWith("Try4")),counts=new Float64Array(cats.length);
 let q=0,h=o,t=0,batches=0,attempts=0;
 while(q!==M.q&&t<30000000000){counts[category[q]]++;batches+=entries[q];attempts+=tries[q];const v=M.T[3*q+a[h]];a[h]=v>>2&3;h+=(v&3)-1;q=v>>>4;t++;}
 let e=h+1;while(a[e]<2)e++;if(q!==M.q||Array.from(a.slice(h+1,e)).join("")!==U.stream(E,raw))throw Error("stream");
 return {t,batches,attempts,rowsBatched:4*batches,avoidedShuttles:3*batches,counts:Object.fromEntries(cats.map((x,i)=>[x,counts[i]]))};
}
function mixed(P,U,E){
 const C=P.compile(),M={...P.decode(C.desc),bridgeReady:C.bridgeReady},m=5,B=[[-1,-6,-11],[-1,-6,-12],[-1,-7,-14],[-2,-8,-15],[-3,-9,-13]],raw=E.encode(m,[0,1,0,1,0],B),r=P.run(M,raw,30000000000);
 if(r.status!=="MASK_STREAM_LOADED"||r.stream!==U.stream(E,raw))throw Error("m5 mixed");
 return {m,raw:raw.length,t:r.t,head:r.head,span:r.span,stream:r.stream.length};
}
module.exports={profile,mixed};
if(require.main===module){
 const P=require("./f038_rex_width_three_batched_deposit_producer.js"),U=require("./f038_rex_width_three_lazy_interval_ir.js"),E=require("./f038_tga_normalized_integration.js").engine(),H=require("./f038_rex_width_three_two_prefix_hard.js");
 console.log(JSON.stringify(process.argv.includes("--mixed")?mixed(P,U,E):profile(P,U,E,H)));
}
