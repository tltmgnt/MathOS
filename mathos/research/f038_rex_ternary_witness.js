// F038-REX-022B6 — fixed raw-selector to original Boolean witness descriptor.
function compile(P,H,A){
 const J=A.worker(),projection=Object.fromEntries(J.symbols.filter(x=>x!=="__").map(x=>[x,/^u[0-2][01]$/.test(x)?"0"+x[2]:x==="X"?"11":"_"])),W=A.compile(J.rules,J.symbols,projection);
 const B=H.compile(P,{worker:()=>J,compile:()=>W}),D=P.decode(B.desc),defs=new Map(),names=[],ids=new Map();
 const add=(n,f)=>{if(defs.has(n))throw Error("duplicate "+n);defs.set(n,f);ids.set(n,names.length);names.push(n);return n;};
 const r=(n,a)=>[n,a,1],l=(n,a)=>[n,a,-1],z=(n,a)=>[n,a,0],bad=()=>z("HALT",2);
 const back=(n,dest)=>add(n,a=>a===2?z(dest,a):r(n,a));
 const left=(n,dest)=>add(n,a=>a===2?z(dest,a):l(n,a));
 function walk(n,d,count,dest){for(let i=1;i<=count;i++)add(n+i,a=>a===2?bad():(d===1?r:l)(i===1?dest:n+(i-1),a));return count?n+count:dest;}
 // Mark only root's three fields and the third field of each selected child.
 // Product region is a contiguous word of six-cell logical symbols at ready.
 const rev=new Map(Object.entries(W.code).map(([s,c])=>[c,s])),seen=new Set(),w=W.width;
 function mark(root,chosen,field,prefix=""){
  const n="mark_"+root+"_"+chosen+"_"+field+"_"+prefix;if(seen.has(n))return n;seen.add(n);
  add(n,a=>{
   if(a===2)return bad();const c=prefix+a;if(c.length<w)return r(mark(root,chosen,field,c),a);
   const sym=rev.get(c);if(!sym||sym==="__")return bad();
   if(sym==="R")return l("markRewind",a);
   let rr=root,cc=chosen,ff=field,out=sym;
   if(sym==="G"){rr=root===0?1:2;cc=0;ff=0;}
   else if(sym==="W"){cc=1;ff=0;}
   else if(sym==="P"){cc=0;ff=0;}
   else if(/^d[0-2][01]$/.test(sym)){ff=+sym[1];if(chosen&&(root===1||ff===2))out="u"+sym.slice(1);}
   else if(sym==="J"&&chosen&&(root===1||field===2))out="X";
   else if(/^T(00|10|11)$/.test(sym))cc=0;
   const dest=mark(rr,cc,ff),word=W.code[out];
   if(out===sym)return r(dest,a);
   const tag="markWrite_"+dest+"_"+word;
   if(!defs.has(tag+"L"+(w-2))){
    for(let i=w-2;i>=0;i--)add(tag+"L"+i,a=>a===2?bad():i?l(tag+"L"+(i-1),+word[i]):r(tag+"R1",+word[0]));
    for(let i=1;i<w;i++)add(tag+"R"+i,a=>a===2?bad():r(i===w-1?dest:tag+"R"+(i+1),a));
   }
   return l(tag+"L"+(w-2),+word[w-1]);
  });return n;
 }
 const markEntry=mark(0,0,0);
 add("markRewind",a=>a===2?r("PROJECT",a):l("markRewind",a));
 // Move compact rank-token word left across the isolated blank gap.
 add("relocate",a=>a===2?bad():l("relGap",a));
 add("relGap",a=>a===2?l("relPeek",a):bad());
 add("relPeek",a=>a===2?r("relShift",a):r("group0Read",a));
 add("relShift",a=>a===2?r("relRead",a):bad());
 add("relRead",a=>a===2?l("relEnd",a):l("relPut"+a,2));
 for(let b of [0,1])add("relPut"+b,a=>a===2?r("relStep",b):bad());
 add("relStep",a=>a===2?r("relRead",a):bad());
 add("relEnd",a=>a===2?l("relBack",a):bad());
 add("relBack",a=>a===2?r("relocate",a):l("relBack",a));
 // Five interleaved binary lanes M,Y,A,B,C, 15 fixed group bits.
 function scan(name,init,fn,finish,readonly=false){
  const seen=new Set(),returns=new Map();
  function ret(dest){if(!returns.has(dest))returns.set(dest,back(name+"Back"+returns.size,dest));return returns.get(dest);}
  function st(acc,prefix){
   const s=name+"R"+acc+"_"+prefix;if(seen.has(s))return s;seen.add(s);
   add(s,a=>{
    if(a===2)return prefix.length?bad():r(ret(finish(acc)),2);
    if(prefix.length<4)return l(st(acc,prefix+a),a);
    let b=[a,...prefix.split("").reverse().map(Number)],v=fn(acc,b),dest=st(v.next,"");
    if(readonly)return l(dest,a);
    const t=name+"W"+v.next+"_"+v.out.join("");
    if(!defs.has(t+"1")){
     for(let i=1;i<5;i++)add(t+i,a=>i===4?l(t+"B1",v.out[i]):r(t+(i+1),v.out[i]));
     for(let i=1;i<5;i++)add(t+"B"+i,a=>l(i===4?dest:t+"B"+(i+1),a));
    }
    return r(t+"1",v.out[0]);
   });return s;
  }
  const entry=walk(name+"Skip",-1,15,st(init,""));return add(name,a=>a===2?l(entry,a):bad());
 }
 function inc(n,i,dest){return scan(n,1,(c,b)=>{let t=b[i]+c;b[i]=t&1;return{out:b,next:t>>1};},c=>c?"HALT":dest);}
 function clear(n,i,dest){return scan(n,0,(c,b)=>{b[i]=0;return{out:b,next:0};},()=>dest);}
 function eq(n,i,j,yes,no){return scan(n,1,(c,b)=>({out:b,next:+(c&&b[i]===b[j])}),c=>c?yes:no,true);}
 function zero(n,i,yes,no){return scan(n,1,(c,b)=>({out:b,next:+(c&&!b[i])}),c=>c?yes:no,true);}
 function le(n,i,j,yes,no){return scan(n,0,(c,b)=>({out:b,next:b[i]===b[j]?c:b[i]<b[j]?1:2}),c=>c===2?no:yes,true);}
 function digit(n,b,dest){return scan(n,b,(c,v)=>{let t=v[2];v[2]=c;return{out:v,next:t};},c=>c?"HALT":dest);}
 // Consume one token bit by shifting the workspace, retaining the bit in
 // the existing selector prefix. The suffix and all output blocks stay fixed.
 function consume(n,bit,dest){
  add(n,a=>a===2?l(n+"Gap",a):bad());
  add(n+"Gap",a=>a===2?l(n+"Read",a):bad());
  add(n+"Read",a=>a===2?r(n+"Clear",bit):r(n+"Write"+a,a));
  for(let b of [0,1])add(n+"Write"+b,a=>l(n+"Skip",b));
  add(n+"Skip",a=>l(n+"Read",a));add(n+"Clear",a=>r(n+"Return",2));back(n+"Return",dest);
  return n;
 }
 // Append to X or Y block to right of the remaining rank-token stream.
 function emit(n,block,bit,dest){
  add(n,a=>a===2?r(n+"Rank",a):bad());
  add(n+"Rank",a=>a===2?r(n+"X",a):r(n+"Rank",a));
  if(block==="X"){
   add(n+"X",a=>a===2?r(n+"Insert",bit):r(n+"X",a));
   add(n+"Insert",a=>a===2?r(n+"End",2):r(n+"Carry"+a,2));
   for(let b of [0,1])add(n+"Carry"+b,a=>a===2?r(n+"End",b):r(n+"Carry"+a,b));
   add(n+"End",a=>a===2?l(n+"BackY",a):bad());
  }else{
   add(n+"X",a=>a===2?r(n+"Y",a):r(n+"X",a));
   add(n+"Y",a=>a===2?r(n+"End",bit):r(n+"Y",a));
   add(n+"End",a=>a===2?l(n+"BackY",a):bad());
  }
  add(n+"BackY",a=>a===2?l(n+"BackX",a):l(n+"BackY",a));
  add(n+"BackX",a=>a===2?l(n+"BackRank",a):l(n+"BackX",a));
  left(n+"BackRank",dest);return n;
 }
 for(let g=0;g<9;g++){
  const n="group"+g,read=n+"Read",loop=n+"Loop",next=g===8?"pinRead":"group"+(g+1)+"Read";
  add(read,a=>a===2?r(n+"First",a):bad());
  for(let b of [0,1]){
   consume(n+"ConsumeFirst"+b,b,n+"Second"+b);
   add(n+"Second"+b,a=>a===2?r(n+"SecondRaw"+b,a):bad());
  }
  add(n+"First",a=>a===2?bad():z(n+"ConsumeFirst"+a,2));
  for(let b of [0,1]){
   add(n+"SecondRaw"+b,a=>a===2||b===1&&a===0?bad():z(n+"Consume"+b+a,2));
   for(let c of [0,1])if(!(b===1&&c===0)){
    consume(n+"Consume"+b+c,c,b===1?loop:n+"Digit"+c);
    if(b===0)digit(n+"Digit"+c,c,read);
   }
  }
  eq(loop,2,3,n+"X1",n+"X0");
  emit(n+"X0","X",0,n+"YTest");emit(n+"X1","X",1,n+"YTest");
  zero(n+"YTest",3,n+"Advance",n+"YCompare");
  le(n+"YCompare",2,3,n+"Y1",n+"Y0");
  emit(n+"Y0","Y",0,n+"Advance");emit(n+"Y1","Y",1,n+"Advance");
  eq(n+"Advance",3,0,n+"ClearB",n+"Inc");inc(n+"Inc",3,loop);
  clear(n+"ClearB",3,n+"ClearA");clear(n+"ClearA",2,next);
 }
 // Read/rotate pin block 49 using the same delimiter-counted physical access.
 function pinAccess(n,rotate,yes,no){
  add(n,a=>a===2?l(n+"Work",a):bad());
  add(n+"Work",a=>a===2?l(n+"Prefix",a):l(n+"Work",a));
  add(n+"Prefix",a=>a===2?l(n+"Seek0",a):l(n+"Prefix",a));
  for(let j=0;j<49;j++)add(n+"Seek"+j,a=>a===2?l(n+"Seek"+(j+1),a):l(n+"Seek"+j,a));
  function ret(tag,dest){
   for(let j=49;j>=0;j--)add(tag+j,a=>a===2?r(j===0?tag+"Prefix":tag+(j-1),a):r(tag+j,a));
   add(tag+"Prefix",a=>a===2?r(tag+"Work",a):r(tag+"Prefix",a));back(tag+"Work",dest);return tag+49;
  }
  const q0=ret(n+"R",yes);
  if(!rotate){const q1=ret(n+"T",no);add(n+"Seek49",a=>a===2?bad():r(a?q1:q0,a));}
  else{
   add(n+"Seek49",a=>a===2?bad():l(n+"Find"+a,a));
   for(let b of [0,1]){
    add(n+"Find"+b,a=>a===2?r(n+"Carry"+b,a):l(n+"Find"+b,a));
    add(n+"Carry"+b,a=>a===2?r(n+"R48",a):r(n+"Carry"+a,b));
   }
  }
 }
 pinAccess("pinRead",false,"pin0","pin1");emit("pin0","Y",0,"pinRotate");emit("pin1","Y",1,"pinRotate");
 pinAccess("pinRotate",true,"pinAdvance");eq("pinAdvance",3,0,"guard0","pinInc");inc("pinInc",3,"pinRead");
 emit("guard0","Y",0,"guard1");emit("guard1","Y",0,"joinStart");
 // At end the rank stream is empty. Join X and Y by shifting Y left one
 // cell. The original verifier reads exactly n consecutive bits at halt.
 add("joinStart",a=>a===2?r("joinRankEnd",a):bad());
 add("joinRankEnd",a=>a===2?r("joinX",a):bad());
 add("joinX",a=>a===2?r("joinRead",a):r("joinX",a));
 add("joinRead",a=>a===2?l("joinEnd",a):l("joinPut"+a,2));
 for(let b of [0,1])add("joinPut"+b,a=>a===2?r("joinStep",b):bad());
 add("joinStep",a=>a===2?r("joinRead",a):bad());
 add("joinEnd",a=>a===2?l("joinBack",a):bad());
 add("joinBack",a=>a===2?r("HALT",a):l("joinBack",a));
 // Mark states are generated lazily. Materialize their closure before
 // assigning the final halt index; preserve all existing B5 state numbers.
 const rows=[];
 for(let i=0;i<names.length;i++)for(let a=0;a<3;a++){let [s,b,d]=defs.get(names[i])(a);rows.push([s,b,d]);}
 const q=B.q+names.length,idx=s=>s==="HALT"?q:s==="PROJECT"?B.workerEntry+W.names.indexOf("sBegin"):B.q+ids.get(s);
 const T=[];let markEdges=0,projectionEdges=0;
 for(let i=0;i<D.T.length;i++){
  let v=D.T[i],a=v>>>4,b=(v>>2)&3,d=(v&3)-1,oldState=Math.floor(i/3);
  if(oldState>=B.workerEntry&&a===B.workerEntry+W.names.indexOf("sBegin")){a=idx(markEntry);markEdges++;}
  else if(a===B.q){
   if(oldState>=B.workerEntry&&W.names[oldState-B.workerEntry]==="sFinish"&&i%3===2){a=idx("relocate");projectionEdges++;}
   else {a=q;if(oldState<B.producerStates)b=2;}
  }
  T.push([a,b,d]);
 }
 if(!markEdges||projectionEdges!==1)throw Error("splice edges "+markEdges+"/"+projectionEdges);
 for(let [s,b,d] of rows){let a=idx(s);if(!Number.isInteger(a)||a<0||a>q)throw Error("target "+s);T.push([a,b,d]);}
 const width=q.toString(2).length,desc="111"+"1".repeat(q)+"0"+T.map(([a,b,d])=>a.toString(2).padStart(width,"0")+b.toString(2).padStart(2,"0")+(d+1).toString(2).padStart(2,"0")).join("");
 return{q,desc,producerStates:B.producerStates,bridgeStates:B.bridgeStates,workerStates:W.q,extensionStates:names.length,bridgeEntry:B.bridgeEntry,workerEntry:B.workerEntry,markEntry:idx(markEntry),rankEntry:idx("relocate"),translateEntry:idx("group0Read"),joinEntry:idx("joinStart"),markEdges,projectionEdges};
}
function run(P,M,raw,limit=Infinity,observe=false){
 if(!/^[01]*$/.test(raw))throw Error("binary input required");
 if(limit!==Infinity&&(!Number.isSafeInteger(limit)||limit<0))throw Error("invalid limit");
 const {q,T}=P.decode(M.desc),origin=3*raw.length+512;let tape=new Uint8Array(origin+raw.length+512);tape.fill(2);
 for(let i=0;i<raw.length;i++)tape[origin+i]=+raw[i];
 let h=origin,state=0,t=0,lo=h,hi=h,bridgeAt=null,workerAt=null,markAt=null,rankAt=null,translateAt=null,joinAt=null,rankTokens=null,protectedBefore=null,separator=null,protectedLeft=null,protectedUnchanged=null,trace=[];
 while(state!==q&&t<limit){
  if(state===M.bridgeEntry&&bridgeAt===null){bridgeAt=t;if(observe){separator=h;protectedLeft=lo;protectedBefore=tape.slice(lo,h);}}
  if(state===M.workerEntry&&workerAt===null)workerAt=t;
  if(state===M.markEntry&&markAt===null)markAt=t;
  if(state===M.rankEntry&&rankAt===null){rankAt=t;if(observe){let e=h;while(tape[e]!==2)e++;rankTokens=Array.from(tape.subarray(h,e)).join("");protectedUnchanged=protectedBefore.every((a,i)=>tape[protectedLeft+i]===a)&&tape[separator]===2;}}
  if(state===M.translateEntry&&translateAt===null)translateAt=t;
  if(state===M.joinEntry&&joinAt===null)joinAt=t;
  if(observe&&rankAt!==null&&t%1000===0)trace.push([t,state,h-origin]);
  let v=T[3*state+tape[h]];tape[h]=(v>>2)&3;h+=(v&3)-1;state=v>>>4;t++;
  if(h<0)throw Error("left buffer");if(h>=tape.length){let g=new Uint8Array(tape.length*2);g.fill(2);g.set(tape);tape=g;}if(h<lo)lo=h;if(h>hi)hi=h;
 }
 let status=state!==q?"TIMEOUT":tape[h]===2?(rankAt!==null?"RECOVERY_REJECT":workerAt!==null?"UNSAT":"OUTSIDE"):"SAT";
 let bits=null;if(status==="SAT"){let e=h;while(tape[e]!==2)e++;bits=Array.from(tape.subarray(h,e)).join("");}
 return{status,t,head:h-origin,span:hi-lo+1,bits,bridgeAt,workerAt,markAt,rankAt,translateAt,joinAt,rankTokens,protectedUnchanged,...(status==="RECOVERY_REJECT"&&observe?{trace:trace.slice(-10)}:{})};
}
module.exports={compile,run};
if(require.main===module){const P=require('./f038_rex_ternary_bags.js'),H=require('./f038_rex_ternary_handoff.js'),A=require('./f038_rex_nested_variable_overlap.js'),M=compile(P,H,A);if(process.argv.includes('--descriptor'))process.stdout.write(M.desc);else console.log(JSON.stringify(run(P,M,require('fs').readFileSync(0,'utf8'))));}
