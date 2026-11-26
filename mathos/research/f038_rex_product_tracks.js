// RE-X-002 full two-track product alphabet, configurable fixed logical table; not a SAT solver.
function compile(worker){
 const digits=["_","0","1"],symbols=digits.flatMap(a=>digits.map(b=>a+b)).concat(["L","R","X"]);
 const blank="__",width=4,code={ [blank]:"2222" };
 symbols.filter(s=>s!==blank).forEach((s,i)=>code[s]=i.toString(2).padStart(width,"0"));
 const decode=new Map(Object.entries(code).map(([s,c])=>[c,s]));
 const rules=new Map();
 for(const row of worker){
  if(!Array.isArray(row)||row.length!==5)throw Error("rule arity");
  let [s,a,t,w,d]=row;
  if(!/^[a-zA-Z0-9]+$/.test(s)||!/^[a-zA-Z0-9]+$/.test(t)||["ready","reject"].includes(s)||!symbols.includes(a)||!symbols.includes(w)||![-1,0,1].includes(d)||(["ready","reject"].includes(t)&&d!==0)||(t==="reject"&&w!==blank))throw Error("invalid logical rule");
  let k=s+":"+a;if(rules.has(k))throw Error("nondeterministic rule");rules.set(k,[t,w,d]);
 }
 const names=[],ids=new Map(),T=[];
 function id(s){if(s==="HALT")return -1;if(!ids.has(s)){ids.set(s,names.length);names.push(s)}return ids.get(s);}
 id("pBegin");
 function step(s,a){
  const [p,b,j,k]=s.split(":");
  const l=(n,w=a)=>[n,w,-1],r=(n,w=a)=>[n,w,1],z=(n,w=a)=>[n,w,0],fail=()=>z("HALT",2);
  if(p==="pBegin"||p==="pSeek"||p==="pNext"){
   if(a<2)return r("pSeek");
   if(p==="pBegin")return z("read:init:");
   return l(p==="pNext"?"pFinishGap":"pRead");
  }
  if(p==="pRead")return a<2?l("pCross:"+a,2):fail();
  if(p==="pCross")return a<2?l(s):l("pOut:"+b);
  if(p==="pOut")return a<2?l(s):l("pWrite:"+b+":"+(width-2),+code[b+"_"][width-1]);
  if(p==="pWrite")return a===2?l(+j===0?"pTurn":"pWrite:"+b+":"+(+j-1),+code[b+"_"][+j]):fail();
  if(p==="pTurn")return a===2?r("pReturn"):fail();
  if(p==="pReturn")return a<2?r(s):r("pNext");
  if(p==="pFinishGap")return a===2?l("pFinish"):fail();
  if(p==="pFinish")return a<2?l(s):r("read:init:");
  // Aligned logical transition: decode, rewrite backwards, move to aligned next head.
  if(p==="read"){
   const c=(j??"")+a;
   if(c.length<width)return r("read:"+b+":"+c);
   const sym=decode.get(c),rule=rules.get(b+":"+sym);
   if(!rule)return fail();
   const [ns,w,d]=rule;
   return l("write:"+ns+":"+code[w]+":"+d+":"+(width-2),+code[w][width-1]);
  }
  if(p==="write"){
   const i=+s.split(":")[4],d=+k;
   if(i>0)return l("write:"+b+":"+j+":"+k+":"+(i-1),+j[i]);
   if(d===0)return z(b==="ready"?"sBegin":b==="reject"?"HALT":"read:"+b+":",+j[0]);
   return d===1?r("move:"+b+":"+(width-1)+":1",+j[0]):l("move:"+b+":"+(width-1)+":-1",+j[0]);
  }
  if(p==="move"){
   const next=+j===1?"read:"+b+":":"move:"+b+":"+(+j-1)+":"+k;
   return +k===1?r(next):l(next);
  }
  // Output contract: a contiguous nonblank product region followed by R,
  // head at its first block; project witness track, skipping witness blanks.
  if(p==="sBegin")return a===2?z("HALT"):r("sSeek");
  if(p==="sSeek")return a<2?r(s):l("sEnd:"+ (width-1));
  if(p==="sEnd")return a===+code.R[+b]?l(+b===0?"sBack":"sEnd:"+(+b-1),2):fail();
  if(p==="sBack")return a<2?l(s):r("sStart");
  if(p==="sStart"||p==="sNext"||p==="sScan"){
   if(a<2)return r("sScan");
   if(p==="sStart")return z("HALT");
   return l(p==="sNext"?"sFinishGap":"sRead:");
  }
  if(p==="sRead"){
   if(a===2)return fail();
   let c=a+(b??"");
   if(c.length<width)return l("sRead:"+c,2);
   const sym=decode.get(c);
   if(!sym||sym.length!==2||sym===blank)return fail();
   return l("sCross:"+sym[1],2);
  }
  if(p==="sCross")return a<2?l(s):l("sOut:"+b);
  if(p==="sOut"){
   if(a<2)return l(s);
   if(b==="_")return r("sReturn"); // turn immediately; no output bit.
   return l("sTurn",+b);
  }
  if(p==="sTurn")return a===2?r("sReturn"):fail();
  if(p==="sReturn")return a<2?r(s):r("sNext");
  if(p==="sFinishGap")return a===2?l("sFinish"):fail();
  if(p==="sFinish")return a<2?l(s):r("HALT");
  return fail();
 }
 // Include every declared logical state so microstep audit can check unreachable rules too.
 for(const [s] of worker)id("read:"+s+":");
 for(let i=0;i<names.length;i++)for(let a=0;a<3;a++){let [s,w,d]=step(names[i],a);T.push([id(s),w,d]);}
 const q=names.length;
 for(const t of T)if(t[0]===-1)t[0]=q;
 const b=q.toString(2).length,desc="111"+"1".repeat(q)+"0"+T.map(([s,w,d])=>s.toString(2).padStart(b,"0")+w.toString(2).padStart(2,"0")+(d+1).toString(2).padStart(2,"0")).join("");
 return {q,T,desc,names,code,symbols,width,worker};
}
function worker(mode){
 const R=[],add=(s,a,t,w,d)=>R.push([s,a,t,w,d]);
 if(!["prefixOr","groupOr"].includes(mode))throw Error("mode");
 add("init","__","ready","__",0);
 for(let a of ["0_","1_"])add("init",a,"left",a,-1);
 add("left","__",mode==="prefixOr"?"p0":"g0","L",1);
 if(mode==="prefixOr"){
  for(let p=0;p<2;p++){
   for(let b=0;b<2;b++){let x=p|b;add("p"+p,b+"_","p"+x,""+b+x,1);}
   add("p"+p,"__","back","R",-1);
  }
 }else{
  // Tokens 00=false, 01=true, 10=end group; 11 reserved invalid.
  // No output on data tokens. At each group end emit OR on its second cell.
  // g0,g1: accumulator; e0,e1: no pending group; d0,d1: first token bit 0;
  // t0,t1: first token bit 1. Require explicit end for every nonempty tail.
  // Empty input valid. Empty groups are permitted.
  for(let p=0;p<2;p++){
   for(let b=0;b<2;b++){
    add("g"+p,b+"_",(b?"t":"d")+p,b+"_",1);
    add("d"+p,b+"_","g"+(p|b),b+"_",1);
   }
   add("t"+p,"0_","e0","0"+p,1);
   add("t"+p,"1_","reject","__",0);
   add("d"+p,"__","reject","__",0);
   add("t"+p,"__","reject","__",0);
   add("g"+p,"__","reject","__",0);
  }
  for(let b=0;b<2;b++)add("e0",b+"_",b?"t0":"d0",b+"_",1);
  add("e0","__","back","R",-1);
 }
 for(let a of ["0_","1_","00","01","10","11"])add("back",a,"back",a,-1);
 add("back","L","done","__",1);
 for(let a of ["0_","1_","00","01","10","11"])add("done",a,"ready",a,0);
 return R;
}
function audit(){
 const ok=(x,s)=>{if(!x)throw Error(s)};
 function run(M,input,limit=Infinity){
  let tape=new Map([...input].map((s,i)=>[i,+s])),state=0,head=0,steps=0,lo=0,hi=0,ph=[0,0,0],snap=[];
  while(state!==M.q&&steps<limit){
   let name=M.names[state],p=name[0]==="p"?0:name[0]==="s"?2:1;
   if(name==="read:init:"||name==="sBegin")snap.push([name,head,[...tape].sort((a,b)=>a[0]-b[0])]);
   let [s,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);
   state=s;head+=d;steps++;ph[p]++;lo=Math.min(lo,head);hi=Math.max(hi,head);
   if(steps>1e7)throw Error("runaway");
  }
  return {tape,state,head,steps,ph,snap,span:hi-lo+1};
 }
 function reference(s,mode){
  if(mode==="prefixOr"){let p=0;return {out:[...s].map(b=>String(p|=+b)).join(""),marks:[...s].map((_,i)=>i)};}
  let p=0,out="",marks=[];
  if(s.length%2)return null;
  for(let i=0;i<s.length;i+=2){
   let t=s.slice(i,i+2);
   if(t==="11")return null;
   if(t==="10"){out+=p;marks.push(i+1);p=0;}
   else p|=+(t==="01");
  }
  if(s.length&&!s.endsWith("10"))return null;
  return {out,marks};
 }
 const results=[];
 for(let mode of ["prefixOr","groupOr"]){
  let M=compile(worker(mode));
  let n={cases:0,valid:0,rejected:0,transitions:0,validTransitions:0,cutoffs:0,skippedCells:0,outputBits:0},scaling=[];
  let q=M.q,b=q.toString(2).length,pos=3;while(M.desc[pos]==="1")pos++;
  ok(pos-3===q&&M.desc[pos++]==="0","descriptor header");
  for(let [s,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===s&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
  ok(pos===M.desc.length,"descriptor end");
  function check(s,record=true){
   let N=s.length,r=run(M,s),ref=reference(s,mode);
   ok(r.state===M.q,"halt");
   if(record){n.cases++;n.transitions+=r.steps;}
   if(!ref){ok(!r.tape.has(r.head),"fail blank "+s);if(record)n.rejected++;return r;}
   let {out,marks}=ref;
   ok(r.tape.size===out.length&&[...out].every((b,i)=>r.tape.get(r.head+i)===+b)&& (out.length||!r.tape.has(r.head)),"output "+s);
   ok(r.snap.length===2,"phase");
   let prep=[...s].map(b=>M.code[b+"_"]).join("");
   ok(r.snap[0][2].map(x=>x[1]).join("")===prep,"raw prep");
   let j=0,logical=[...s].map((b,i)=>M.code[b+(marks.includes(i)?out[j++]:"_")]).join("")+(N?M.code.R:"");
   ok(r.snap[1][2].map(x=>x[1]).join("")===logical,"product track preservation");
   // Serializer: initial marker sweep + reverse-word iteration, counts
   // depend on number of already emitted bits and whether current emits.
   let emitted=0,body=0;
   for(let i=N-1;i>=0;i--){let emit=+marks.includes(i);body+=8*(i+1)+2*emitted+2*emit+4;emitted+=emit;}
   let prepT=N?5*N*(N+1)+8*N+3:1;
   let logicT=N?10*(2*N+4)+7:7;
   let serialT=N?8*N+10+body+out.length+3:1;
   ok(JSON.stringify(r.ph)===JSON.stringify([prepT,logicT,serialT]),"clock "+JSON.stringify({s,ph:r.ph,expected:[prepT,logicT,serialT]}));
   ok(r.head===(N?-4*N-out.length-2:0),"head");
   ok(r.span===(N?4*N+Math.max(N,3)+Math.max(out.length+3,5)+1:4),"span");
   if(record){n.valid++;n.validTransitions+=r.steps;n.skippedCells+=N-out.length;n.outputBits+=out.length;}
   return r;
  }
  for(let len=0;len<=8;len++)for(let i=0;i<2**len;i++){
   let s=len?i.toString(2).padStart(len,"0"):"",r=check(s);
   if(i===0||reference(s,mode)&&i===2**len-1){ok(run(M,s,r.steps-1).state!==M.q,"cutoff");n.cutoffs++;}
  }
  for(let len of [16,32,64,128]){
   let s=mode==="prefixOr"?"0011".repeat(len/4):"00011010".repeat(len/8),r=check(s,false);
   scaling.push([len,r.steps,r.ph,r.span,reference(s,mode).out.length]);
  }
  results.push({mode,states:M.q,descriptionBits:M.desc.length,n,scaling});
 }
 // Complete local microstep product: every symbol, write symbol, direction,
 // using a fixed table per write/direction and all possible reads.
 let micro=0,microTransitions=0,invalidCodes=0;
 const all=compile(worker("prefixOr")).symbols;
 for(let w of all)for(let d of [-1,0,1]){
  let M=compile(all.map(a=>["init",a,"next",w,d]));
  for(let a of all){
   let head=0,state=M.names.indexOf("read:init:"),tape=new Map();
   for(let [off,sym] of [[-4,"01"],[0,a],[4,"10"]])for(let i=0;i<4;i++)if(M.code[sym][i]!=="2")tape.set(off+i,+M.code[sym][i]);
   let expected=new Map(tape);for(let i=0;i<4;i++){let x=+M.code[w][i];if(x===2)expected.delete(i);else expected.set(i,x);}
   let count=d?10:7;
   for(let i=0;i<count;i++){let [s,v,m]=M.T[3*state+(tape.get(head)??2)];if(v===2)tape.delete(head);else tape.set(head,v);head+=m;state=s;}
   ok(head===4*d&&M.names[state]==="read:next:"&&tape.size===expected.size&&[...expected].every(([i,v])=>tape.get(i)===v),"microstep");
   micro++;microTransitions+=count;
  }
 }
 let M=compile(all.map(a=>["init",a,"next",a,0]));
 for(let i=0;i<81;i++){let word=i.toString(3).padStart(4,"0");if(Object.values(M.code).includes(word))continue;
  let state=M.names.indexOf("read:init:"),head=0,tape=new Map([...word].map((a,i)=>[i,+a]));for(let j=0;j<4;j++){let [s,w,d]=M.T[3*state+(tape.get(head)??2)];tape.set(head,w);head+=d;state=s;}
  ok(state===M.q&&tape.get(head)===2,"invalid code");invalidCodes++;
 }
 // Prepared exact existential bag reductions: one OR group per outgoing key.
 // Membership flags are generated by the host, not by this physical worker.
 let bags=[],bagRows=0,bagOutputs=0,bagTransitions=0;
 let G=compile(worker("groupOr"));
 for(let m of [2,3])for(let width of [0,1,2,3]){
  let raw="",want="";
  for(let j=0;j<m**width;j++){
   let key=Array.from({length:width},(_,i)=>Math.floor(j/m**(width-i-1))%m),hit=false;
   for(let a=0;a<m;a++){
    let b=key.every((x,i)=>(x+a+i)%m!==m-1)&&((a+j)%m!==0);
    raw+=b?"01":"00";hit ||= b;bagRows++;
   }
   raw+="10";want+=+hit;bagOutputs++;
  }
  let r=run(G,raw);
  ok(r.state===G.q&&r.tape.size===want.length&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b),"bag existential OR");
  bagTransitions+=r.steps;bags.push([m,width,raw.length,want.length,[...want].filter(x=>x==="1").length,r.steps]);
 }
 // Generic table may emit witness-only symbols, or emit no bits at all.
 let generic={cases:0,transitions:0,invalidRules:0};
 for(let mode of ["emptyProjection","sparseProjection"]){
  let W=[["init","__","ready","__",0],["init","0_","left","0_",-1],["init","1_","left","1_",-1],["left","__","even","L",1]];
  for(let b of ["0","1"]){
   W.push(["even",b+"_","odd",mode==="sparseProjection"?"_"+b:b+"_",1],["odd",b+"_","even",b+"_",1]);
  }
  for(let q of ["even","odd"])W.push([q,"__","back","R",-1]);
  for(let a of ["0_","1_","_0","_1"])W.push(["back",a,"back",a,-1],["done",a,"ready",a,0]);
  W.push(["back","L","done","__",1]);
  let P=compile(W);
  for(let len=0;len<=6;len++)for(let i=0;i<2**len;i++){
   let raw=len?i.toString(2).padStart(len,"0"):"",want=mode==="emptyProjection"?"":[...raw].filter((_,j)=>j%2===0).join(""),r=run(P,raw);
   ok(r.state===P.q&&r.tape.size===want.length&&[...want].every((b,j)=>r.tape.get(r.head+j)===+b)&&(want.length||!r.tape.has(r.head)),"generic projection");
   ok(r.head===(len?-4*len-want.length-2:0),"generic projection head");generic.cases++;generic.transitions+=r.steps;
  }
 }
 for(let rules of [
  [["init","0_","next","0_",2]],
  [["init","0_","ready","0_",1]],
  [["init","0_","reject","0_",0]],
  [["init","0_","next","0_",0],["init","0_","next","1_",0]],
  [["init","bogus","next","0_",0]],
  [["ready","0_","next","0_",0]]
 ]){
  let rejected=false;try{compile(rules)}catch(e){rejected=true;}
  ok(rejected,"invalid rules");generic.invalidRules++;
 }
 // Independent original-selector acceptance-contract replay. Mirror the retrieved
 // Python decode_tm/tape_run/valid semantics, starting from the emitted descriptor.
 // Actual Python module imports are separately exercised by the Proctor workflow.
 function decodeDesc(desc){
  let j=3;while(j<desc.length&&desc[j]==="1")j++;
  let q=j-3,b=q.toString(2).length;ok(desc.startsWith("111")&&q>0&&desc[j++]==="0"&&desc.length-j===3*q*(b+4),"U decoder");
  let T=[];
  for(let i=0;i<3*q;i++){let a=parseInt(desc.slice(j,j+b),2),w=parseInt(desc.slice(j+b,j+b+2),2),d=parseInt(desc.slice(j+b+2,j+b+4),2);j+=b+4;ok(a<=q&&w<=2&&d<=2,"U transition");T.push([a,w,d-1]);}
  return {q,T};
 }
 function pool(n){
  let C=[];for(let i=1;i<=n;i++)for(let s of [-1,1])C.push([i*s]);
  for(let i=1;i<=n;i++)for(let j=i+1;j<=n;j++)for(let s of [-1,1])for(let t of [-1,1])C.push([i*s,j*t]);return C;
 }
 function tapeRun(M,raw,n,budget){
  let tape=new Map([...raw].map((v,i)=>[i,+v])),state=0,head=0;
  for(let i=0;i<budget;i++){
   let [a,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);head+=d;state=a;
   if(state===M.q){let bits=Array.from({length:n},(_,j)=>tape.get(head+j)??2);return bits.every(v=>v<2)?bits.reduce((s,v,j)=>s+(v<<j),0):null;}
  }return null;
 }
 const P=decodeDesc(compile(worker("prefixOr")).desc),Q=decodeDesc(G.desc);
 let selector={selector_inputs:0,prefix_valid:0,prefix_timeouts:0,group_valid:0,group_blank:0};
 for(let n of [1,2]){
  let C=pool(n);
  for(let p=0;p<2**C.length;p++){
   let raw="1".repeat(n)+"0"+C.map((_,j)=>(p>>j)&1).join(""),N=raw.length,clock=10*N*N+51*N+63;
   let valid=x=>Number.isInteger(x)&&x>=0&&x<2**n&&C.every((c,j)=>!(p>>j&1)||c.some(l=>!!(x>>(Math.abs(l)-1)&1)===(l>0)));
   ok(tapeRun(P,raw,n,clock-1)===null,"original prefix cutoff");selector.prefix_timeouts++;
   let x=tapeRun(P,raw,n,clock);ok(x===2**n-1,"original prefix result");selector.prefix_valid+=+valid(x);
   let y=tapeRun(Q,raw,n,clock);
   if(n===1&&p===1){ok(y===0&&valid(y),"group accidental witness");selector.group_valid++;}
   else {ok(y===null,"group blank");selector.group_blank++;}
   selector.selector_inputs++;
  }
 }
 ok(JSON.stringify(selector)===JSON.stringify({selector_inputs:260,prefix_valid:34,prefix_timeouts:260,group_valid:1,group_blank:259}),"original acceptance totals");
 return {results,micro,microTransitions,invalidCodes,bags,bagRows,bagOutputs,bagTransitions,generic,selector};
}
if(process.argv.includes('--description'))console.log(compile(worker(process.argv.includes('--group-or')?'groupOr':'prefixOr')).desc);else console.log('F038_REX_PRODUCT_TRACKS_OK '+JSON.stringify(audit()));
