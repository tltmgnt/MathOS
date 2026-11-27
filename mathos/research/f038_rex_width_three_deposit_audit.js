// D5P online packed-deposit invariant, actual producer regression, conditional resource arithmetic.
function envelope(V,m,packed=false,full=false){
 const e=V.envelope(m),S=e.S,k=BigInt(m),N=S+35n*k+1479n,T=49152n*S*(full?k:1n),W=(20n*N+12n)*T+6n,P=packed?4n*e.P+32n*e.L:e.P+16n*e.L,total=P+128n*S*S+W+256n*S*S,ell=packed?(full?152233704n:152364652n):(full?147954904n:148085852n),c=packed?18n:16n;
 if(N>2n*S||W>2097152n*S*S*(full?k:1n)||total>(1n<<c)*e.L*e.L*(full?k:1n))throw Error("bound");
 return {N,T,W,total,H0:full?(3n*(ell+c-4n)+1n)/2n:ell+c};
}

function audit(U,E,V,Old,Batch,Packed){
 const models=[Old,Batch,Packed].map(P=>{const C=P.compile();return {P,M:{...P.decode(C.desc),bridgeReady:C.bridgeReady}};});
 let patterns=0,folds=0,expansion=0,maxRatio=0,arithmetic=0,cases=0,malformed=0,batchGain=0,packedGain=0,packedLoss=0,packedEqual=0;const rows=[];
 // Online packed deposition invariant. Code is prefix- and suffix-free:
 // zero=0, one=11, four zeros=101. Fold only three terminal literal zeros.
 for(let n=1;n<=12;n++)for(let v=0;v<2**n;v++){
  const bits=v.toString(2).padStart(n,"0");let p="",k=0;
  for(const b of bits){if(b==="1"){p+="11";k=0;}else if(k===3){p=p.slice(0,-3)+"101";k=0;folds++;}else{p+="0";k++;}}
  let decoded="",canonical="";for(let i=0;i<p.length;){if(p[i]==="0"){decoded+="0";canonical+="00";i++;}else if(p.slice(i,i+2)==="11"){decoded+="1";canonical+="01";i+=2;}else if(p.slice(i,i+3)==="101"){decoded+="0000";canonical+="11";i+=3;}else throw Error("code");}
  let expected="";for(let i=0;i<bits.length;){if(bits.slice(i,i+4)==="0000"){expected+="11";i+=4;}else expected+="0"+bits[i++];}
  if(decoded!==bits||canonical!==expected||p.length>2*n||p.length!==n+bits.split("1").length-1-(2*n-expected.length)/6)throw Error("packing");
  patterns++;if(p.length>n)expansion++;maxRatio=Math.max(maxRatio,p.length/n);
 }
 for(let m=2;m<=10000;m++)for(const p of [false,true])for(const f of [false,true]){envelope(V,m,p,f);arithmetic++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n])for(const p of [false,true])for(const f of [false,true]){envelope(V,(1n<<k)+d,p,f);arithmetic++;}
 function test(name,m,c){
  const raw=E.encode(m,Array.from({length:m},(_,i)=>i%2),c),expected=U.stream(E,raw),out=models.map(({P,M})=>P.run(M,raw,3000000000));
  if(out.some(p=>p.status!=="MASK_STREAM_LOADED"||p.stream!==expected))throw Error(name+" stream");if(out[1].t>=out[0].t)throw Error("batch regression "+name);batchGain++;
  if(out[2].t<out[1].t)packedGain++;else if(out[2].t>out[1].t)packedLoss++;else packedEqual++;
  cases++;rows.push({name,m,stream:expected.length,prior:out[0].t,batch:out[1].t,packed:out[2].t,span:out.map(p=>p.span)});
 }
 test("empty",2,[]);test("chain",2,[[-1],[-3],[-2,-4,-5],[-4,-6,-7],[-6,-8,-9]]);test("third",3,[[-1],[-2],[-4],[-5],[-3,-6,-7],[-3,-6,-8]]);
 test("all-active",2,[2,3].flatMap(k=>[...E.subsets([0,1,2,3,4,5,6,7,8],k)].map(h=>h.map(g=>-(2*g+2)))));
 for(const mask of [1,3,15,85,127,255])test("mask-"+mask,2,Array.from({length:8},(_,i)=>i).filter(i=>mask>>i&1).map(i=>[-(1+(i>>2)),-(3+((i>>1)&1)),-(5+(i&1))]));
 const raw=E.encode(2,[0,0],[]),bad=[raw.slice(0,-1),raw+"0",raw.slice(0,31)+"1"+raw.slice(32)];
 // Find additional actually malformed one-bit flips using original decoder.
 for(const i of [32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,raw.length-2,raw.length-3,raw.length-4]){const x=raw.slice(0,i)+(raw[i]==="0"?"1":"0")+raw.slice(i+1);if(!E.decode(x))bad.push(x);}
 for(const x of new Set(bad)){for(const {P,M} of models)if(P.run(M,x,3000000000).status!=="REFUSAL")throw Error("malformed");malformed++;}
 return {patterns,folds,expansion,maxRatio,arithmetic,cases,malformed,batchGain,packedGain,packedLoss,packedEqual,thresholds:[false,true].flatMap(p=>[false,true].map(f=>String(envelope(V,2,p,f).H0))),rows};
}
module.exports={envelope,audit};
if(require.main===module){const U=require('./f038_rex_width_three_cost_ir.js'),E=require('./f038_tga_normalized_integration.js').engine(),V=require('./f038_rex_width_three_singleton_envelope.js'),Old=require('./f038_rex_width_three_cost_producer.js'),Batch=require('./f038_rex_width_three_batch_producer.js'),Packed=require('./f038_rex_width_three_packed_producer.js');console.log(JSON.stringify(audit(U,E,V,Old,Batch,Packed)));}
