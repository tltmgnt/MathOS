// D5R storage codec, physical producer comparison, conditional envelope.
function envelope(V,m,full=false){
 const e=V.envelope(m),S=e.S,k=BigInt(m),N=S+35n*k+1479n,T=49152n*S*(full?k:1n),W=(20n*N+12n)*T+6n,P=4n*e.P+32n*e.L,total=P+128n*S*S+W+256n*S*S,ell=full?148737704n:148868652n;
 if(N>2n*S||W>2097152n*S*S*(full?k:1n)||total>262144n*e.L*e.L*(full?k:1n))throw Error("bound");
 return {N,T,W,total,H0:full?(3n*(ell+14n)+1n)/2n:ell+18n};
}
function audit(U,E,V,Batch,Joint,P,Pack){
 const models=[Batch,Joint,P].map(P=>{const C=P.compile();return {P,M:{...P.decode(C.desc),bridgeReady:C.bridgeReady}};});let arithmetic=0,patterns=0,maxOverhead=0,cases=0,malformed=0,batchGain=0,batchLoss=0,jointGain=0,jointLoss=0;const rows=[];
 for(let n=0;n<=12;n++)for(let v=0;v<2**n;v++){
  const word=n?v.toString(2).padStart(n,"0"):"",packed=Pack.pack(word),i=word.indexOf("1"),z=i<0?n:i,K=Math.floor(z/4);
  let out="",j=0;while(j<packed.length-1){if(packed[j]==="0"){out+="0";j++;}else if(packed.slice(j,j+3)==="101"){out+="0000";j+=3;}else if(packed.slice(j,j+2)==="11"){out+="1"+packed.slice(j+2,-1);j=packed.length-1;}else throw Error("codec");}
  if(out!==word||packed.at(-1)!==String(+(i>=0))||packed.length!==n-K+(i<0?1:2)||packed.length>n+2)throw Error("pack "+word);
  maxOverhead=Math.max(maxOverhead,packed.length-n);patterns++;
 }
 for(let m=2;m<=10000;m++)for(const f of [false,true]){envelope(V,m,f);arithmetic++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n])for(const f of [false,true]){envelope(V,(1n<<k)+d,f);arithmetic++;}
 function test(name,m,c){
  const raw=E.encode(m,Array.from({length:m},(_,i)=>i%2),c),expected=U.stream(E,raw),out=models.map(({P,M})=>P.run(M,raw,3000000000));
  if(out.some(p=>p.status!=="MASK_STREAM_LOADED"||p.stream!==expected))throw Error(name+" stream");
  cases++;if(out[2].t<out[0].t)batchGain++;else if(out[2].t>out[0].t)batchLoss++;if(out[2].t<out[1].t)jointGain++;else if(out[2].t>out[1].t)jointLoss++;
  rows.push({name,m,stream:expected.length,batch:out[0].t,joint:out[1].t,adaptive:out[2].t,spans:out.map(p=>p.span)});
 }
 test("empty",2,[]);test("chain",2,[[-1],[-3],[-2,-4,-5],[-4,-6,-7],[-6,-8,-9]]);test("third",3,[[-1],[-2],[-4],[-5],[-3,-6,-7],[-3,-6,-8]]);test("all-active",2,[2,3].flatMap(k=>[...E.subsets([0,1,2,3,4,5,6,7,8],k)].map(h=>h.map(g=>-(2*g+2)))));
 for(const mask of [1,255])test("mask-"+mask,2,Array.from({length:8},(_,i)=>i).filter(i=>mask>>i&1).map(i=>[-(1+(i>>2)),-(3+((i>>1)&1)),-(5+(i&1))]));
 test("last-scope-dense",2,Array.from({length:8},(_,i)=>[-(13+(i>>2)),-(15+((i>>1)&1)),-(17+(i&1))]));
 const raw=E.encode(2,[0,0],[]),bad=[raw.slice(0,-1),raw+"0",raw.slice(0,31)+"1"+raw.slice(32)];
 for(const i of [32,33,raw.length-2]){const x=raw.slice(0,i)+(raw[i]==="0"?"1":"0")+raw.slice(i+1);if(!E.decode(x))bad.push(x);}
 for(const x of new Set(bad)){if(P.run(models[2].M,x,3000000000).status!=="REFUSAL")throw Error("malformed");malformed++;}
 return {patterns,maxOverhead,arithmetic,cases,malformed,batchGain,batchLoss,jointGain,jointLoss,thresholds:[false,true].map(f=>String(envelope(V,2,f).H0)),rows};
}
module.exports={envelope,audit};
if(require.main===module){const U=require('./f038_rex_width_three_cost_ir.js'),E=require('./f038_tga_normalized_integration.js').engine(),V=require('./f038_rex_width_three_singleton_envelope.js'),Batch=require('./f038_rex_width_three_compact_batch_producer.js'),Joint=require('./f038_rex_width_three_joint_producer.js'),P=require('./f038_rex_width_three_adaptive_producer.js'),Pack=require('./f038_rex_width_three_adaptive_macro_audit.js');console.log(JSON.stringify(audit(U,E,V,Batch,Joint,P,Pack)));}
