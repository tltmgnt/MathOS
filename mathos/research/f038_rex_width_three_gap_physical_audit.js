// D5T verify actual physical segmented gap encoder/decoder and header setup.
function gapAudit(U,I,K,F,R){
 const J=[U.machine(false),U.machine(true)],M=J.map(K.compile),ok=(x,s)=>{if(!x)throw Error(s)},run=(j,s)=>I.executeIR(j,["","","","",s]);
 const gamma=n=>{const b=n.toString(2);return "0".repeat(b.length-1)+b;};
 let patterns=0,sparse=0,dense=0,physical=0,malformed=0,maxPrimitiveRatio=0,maxStorageRatio=0;const rows=[];
 function actual(j,m,s){
  const inputs=["","","","",s],a=F.count(j,inputs),raw=["G",...inputs.flatMap((v,k)=>["hL",...[...v].map(x=>"u"+x),"u_",k===4?"E":"D"])].map(x=>m.codes[x]).join("");
  let T=new Uint8Array(Math.max(raw.length,a.encoded.length)+512);T.fill(2);T.set([...raw].map(Number),100);let h=100,pc=0,t=0;
  while(pc<m.q&&t<=a.clock){const v=m.T[3*pc+T[h]];T[h]=v>>2&3;h+=(v&3)-1;pc=v>>>4;t++;}
  ok(pc===m.q+1&&t===a.clock&&h===100&&Array.from(T.slice(100,100+a.encoded.length)).join("")===a.encoded&&T.slice(100+a.encoded.length).every(x=>x===2),"physical clock/layout");
  physical++;return {clock:t,N:a.N,steps:a.steps};
 }
 function test(s,phys=false){
  const n=s.length,h=gamma(n+1),c=R.encode(s),want=h+c,e=run(J[0],s),d=run(J[1],want);
  ok(e.status==="halt"&&e.tapes[0]===want&&d.status==="halt"&&d.tapes[0]===s,"roundtrip "+s);
  ok(want.length<=n+1+h.length,"metadata bound");patterns++;if(c[0]==="1")sparse++;else dense++;
  const b=Math.ceil(Math.log2(n+2)),steps=512*(n+1)*(b+1);
  ok(e.steps<=steps&&d.steps<=steps,"primitive envelope");maxPrimitiveRatio=Math.max(maxPrimitiveRatio,e.steps/steps,d.steps/steps);
  if(phys){const a=actual(J[0],M[0],s),z=actual(J[1],M[1],want),storage=8*(n+1)+32*(b+1);ok(a.N<=storage&&z.N<=storage,"storage envelope");maxStorageRatio=Math.max(maxStorageRatio,a.N/storage,z.N/storage);rows.push({n,forbidden:s.split("1").length-1,mode:c[0],encoded:want.length,encode:a,decode:z});}
 }
 for(let n=0;n<=12;n++)for(let v=0;v<2**n;v++)test(n?v.toString(2).padStart(n,"0"):"");
 let seed=0xD5A5;for(let n of [16,64,256,1024])for(let d of [0,1,5,25,50,100]){let s="";for(let i=0;i<n;i++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;s+=seed%100<d?"1":"0";}test(s);}
 for(const s of ["","0","1","00000001","11111111","0010000100000010","0101010101010101","0".repeat(63)+"1"])test(s,true);
 for(const c of ["","0","00","1","010","0100","010000","01010","010100","0101011","0110011","01110"]){const d=run(J[1],c);if(d.status==="reject")malformed++;else throw Error("malformed accepted "+c);}
 return {patterns,sparse,dense,physical,malformed,maxPrimitiveRatio,maxStorageRatio,states:M.map(m=>m.q),rows};
}
function headerAudit(P){
 const C=P.compile(true),M=P.decode(C.desc),stop=C.names.findIndex(([x,f])=>x==="class1"&&f===0),ok=(x,s)=>{if(!x)throw Error(s)};
 let valid=0,invalid=0,maxSteps=0,maxWidth=0;
 for(let n=0;n<=19*130-7;n++){
  const raw="1".repeat(n)+"0"+"101001",origin=256,T=new Uint8Array(origin+raw.length+256);T.fill(2);T.set([...raw].map(Number),origin);let h=origin,q=0,t=0;
  while(q!==stop&&q!==M.q&&t<1000000){const v=M.T[3*q+T[h]];T[h]=v>>2&3;h+=(v&3)-1;q=v>>>4;t++;}
  const m=(n+7)/19,isValid=Number.isInteger(m)&&m>=2;
  if(!isValid){ok(q===M.q&&T[h]===0,"header refusal "+n);invalid++;continue;}
  ok(q===stop&&h===origin+n&&T[h]===2,"entry "+n);let left=h-1;while(T[left]<2)left--;
  const w=(h-left-1-15)/5,ws=Array.from(T.slice(left+1,h)).join(""),lanes=Array.from({length:5},(_,i)=>parseInt(Array.from({length:w},(_,j)=>ws[5*j+i]).join(""),2));
  ok(w===m.toString(2).length&&lanes.join()===`${m-1},${m-2},0,0,0`&&ws.slice(5*w)==="0".repeat(15),"registers "+n);
  ok(T.slice(0,left+1).every(x=>x===2)&&Array.from(T.slice(h+1,h+7)).join("")==="101001","boundaries "+n);
  ok(t<=128*(n+1)*(w+1),"header budget");maxSteps=Math.max(maxSteps,t);maxWidth=Math.max(maxWidth,w);valid++;
 }
 return {valid,invalid,maxSteps,maxWidth};
}
module.exports={gapAudit,headerAudit};
if(require.main===module){const U=require('./f038_rex_width_three_gap_ir.js'),I=require('./f038_rex_width_three_cost_ir.js'),K=require('./f038_rex_width_three_exit_compiler.js'),F=require('./f038_rex_width_three_fast_clock.js'),R=require('./f038_rex_width_three_gap_reference.js'),P=require('./f038_rex_width_three_fifo_producer.js');console.log(JSON.stringify({gap:gapAudit(U,I,K,F,R),header:headerAudit(P)}));}
