// F038-REX-022B5 — fixed original-input producer / isolated physical worker composition.
function compile(P,A){
 const B=P.compile(),D=P.decode(B.desc),J=A.worker(),W=A.compile(J.rules,J.symbols,J.projection),K=W.width+4;
 // Check the inherited logical boundary contract, including writes.
 for(let [s,a,t,w,d] of J.rules){
  if(t==="reject"){if(d!==0||w!=="__")throw Error("reject boundary");continue;}
  if(a==="L"&&!(d>=0&&(w==="L"||s==="clean"&&w==="__")))throw Error("left sentinel "+s);
  if(a==="R"&&!(d<=0&&w==="R"))throw Error("right sentinel "+s);
  if(a==="__"&&!(s==="left"&&w==="L"&&d===1||s==="endCheck"&&w==="R"&&d===-1))throw Error("blank boundary "+s);
 }
 const rules=new Map(),names=[],ids=new Map(),add=(n,f)=>{if(rules.has(n))throw Error("duplicate "+n);rules.set(n,f);ids.set(n,names.length);names.push(n);};
 const r=(n,a)=>[n,a,1],l=(n,a)=>[n,a,-1],z=(n,a)=>[n,a,0],bad=()=>z("HALT",2);
 // Source word lies to the right of the retained producer separator h.
 add("start",a=>a===2?r("scanSource",a):bad());
 add("scanSource",a=>a===2?z("pop",a):r("scanSource",a));
 add("pop",a=>a===2?l("readLast",a):bad());
 add("readLast",a=>a===2?r("finishSeparator",a):r("grow"+a,2));
 // Source separator moves left one cell; gap grows by that cell plus K shifts.
 for(let b of [0,1]){
  add("grow"+b,a=>a===2?r("findGap"+b,0):bad());
  add("findGap"+b,a=>a===2?z("shift"+b+"_0",a):r("findGap"+b,a));
  for(let j=0;j<K;j++){
   const tag="S"+b+"_"+j,next=j===K-1?"prepend"+b:"shift"+b+"_"+(j+1);
   add("shift"+b+"_"+j,a=>a===2?r(tag+"First",0):bad());
   add(tag+"First",a=>a===2?z(next,2):r(tag+"Carry"+a,2));
   for(let x of [0,1])add(tag+"Carry"+x,a=>a===2?l(tag+"Return",x):r(tag+"Carry"+a,x));
   add(tag+"Return",a=>a===2?z(next,a):l(tag+"Return",a));
  }
  add("prepend"+b,a=>a===2?r("copy"+b,a):bad());
 }
 for(let x of [0,1])add("copy"+x,a=>a===2?l("returnDest",x):r("copy"+a,x));
 add("returnDest",a=>a===2?l("returnGap",a):l("returnDest",a));
 add("returnGap",a=>a===2?z("pop",a):l("returnGap",a));
 add("finishSeparator",a=>a===2?r("eraseGap",a):bad());
 add("eraseGap",a=>a===2?r("WORKER",a):a===0?r("eraseGap",2):bad());
 const H=names.length,workerEntry=B.q+H,q=workerEntry+W.q,halt=q;
 const T=[];
 for(let i=0;i<D.T.length;i++){
  let v=D.T[i],a=v>>>4,w=(v>>2)&3,d=(v&3)-1;
  if(i===3*B.successState+2){if(a!==B.q||w!==2||d!==0)throw Error("producer success rule");a=B.q;}
  else if(a===B.q)a=halt;
  T.push([a,w,d]);
 }
 for(let n of names)for(let a=0;a<3;a++){
  let [s,w,d]=rules.get(n)(a),t=s==="HALT"?halt:s==="WORKER"?workerEntry:B.q+ids.get(s);
  if(!Number.isInteger(t)||t<0||t>q)throw Error("bridge target "+s);
  T.push([t,w,d]);
 }
 for(let [a,w,d] of W.T)T.push([a===W.q?halt:workerEntry+a,w,d]);
 const width=q.toString(2).length,desc="111"+"1".repeat(q)+"0"+T.map(([a,w,d])=>a.toString(2).padStart(width,"0")+w.toString(2).padStart(2,"0")+(d+1).toString(2).padStart(2,"0")).join("");
 return{q,desc,producerStates:B.q,bridgeStates:H,workerStates:W.q,workerWidth:W.width,shiftCount:K,bridgeEntry:B.q,workerEntry,serializationEntry:B.serializationEntry};
}
function run(P,M,raw,limit=Infinity,observe=false){
 if(!/^[01]*$/.test(raw))throw Error("binary raw required");
 if(limit!==Infinity&&(!Number.isSafeInteger(limit)||limit<0))throw Error("invalid limit");
 const {q,T}=P.decode(M.desc),origin=3*raw.length+512;
 let tape=new Uint8Array(origin+raw.length+512);tape.fill(2);
 for(let i=0;i<raw.length;i++)tape[origin+i]=+raw[i];
 let h=origin,state=0,t=0,lo=h,hi=h,bridgeAt=null,workerAt=null,workerOrigin=null,workerLo=null,workerHi=null,entry=null,protectedBefore=null;
 while(state!==q&&t<limit){
  if(state===M.bridgeEntry&&bridgeAt===null){
   bridgeAt=t;if(observe){protectedBefore=tape.slice(lo,h);let p=h+1;while(tape[p]!==2)p++;entry={head:h-origin,left:lo-origin,prepared:Array.from(tape.subarray(h+1,p)).join("")};}
  }
  if(state===M.workerEntry&&workerAt===null){
   workerAt=t;workerOrigin=h-origin;workerLo=workerHi=h;
   if(observe){let p=h;while(tape[p]!==2)p++;entry.workerInput=Array.from(tape.subarray(h,p)).join("");entry.isolated=tape.subarray(origin+entry.head,h).every(a=>a===2);}
  }
  let v=T[3*state+tape[h]];tape[h]=(v>>2)&3;h+=(v&3)-1;state=v>>>4;t++;
  if(h<0)throw Error("left simulation buffer");
  if(h>=tape.length){let grown=new Uint8Array(tape.length*2);grown.fill(2);grown.set(tape);tape=grown;}
  if(h<lo)lo=h;if(h>hi)hi=h;
  if(workerAt!==null){if(h<workerLo)workerLo=h;if(h>workerHi)workerHi=h;}
 }
 const out={status:"TIMEOUT",t,span:hi-lo+1,bridgeAt,workerAt,workerOrigin,head:h-origin};
 if(state!==q)return out;
 if(workerAt===null){
  let count=0;for(let a of tape)if(a!==2)count++;
  if(bridgeAt!==null||count!==1||tape[h]===2)throw Error("noncanonical producer rejection");
  return{...out,status:tape[h]?"OUTSIDE_FIXED_PATH":"OUTSIDE_NORMALIZED"};
 }
 out.status=tape[h]===2?"WORKER_UNSAT":"WORKER_SAT";out.producerTransitions=bridgeAt;out.handoffTransitions=workerAt-bridgeAt;out.workerTransitions=t-workerAt;
 out.workerMin=workerLo-origin;out.workerMax=workerHi-origin;
 if(observe){
  const ph=origin+entry.head,left=origin+entry.left;
  out.protectedUnchanged=protectedBefore.every((a,i)=>tape[left+i]===a)&&tape[ph]===2;
  out.workerTape=[];for(let i=ph+1;i<=hi;i++)if(tape[i]!==2)out.workerTape.push([i-origin-workerOrigin,tape[i]]);
  out.entry=entry;
  // Observer reads the certificate only after the descriptor halts.
  out.certificate="";if(out.status==="WORKER_SAT"){let i=h;while(tape[i]!==2)out.certificate+=tape[i++];}
 }
 return out;
}
module.exports={compile,run};
if(require.main===module){const P=require('./f038_rex_ternary_bags.js'),A=require('./f038_rex_nested_variable_overlap.js'),M=compile(P,A);if(process.argv.includes('--descriptor'))process.stdout.write(M.desc);else console.log(JSON.stringify(run(P,M,require('fs').readFileSync(0,'utf8'))));}
