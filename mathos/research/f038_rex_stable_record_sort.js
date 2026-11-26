// REX-004: stable fixed-width binary record radix sorter, physical compiler adapted from REX-003.
function compile(worker,symbols,projection){
 const blank="__",width=Math.ceil(Math.log2(symbols.length-1)),code={ [blank]:"2".repeat(width) };
 symbols.filter(s=>s!==blank).forEach((s,i)=>code[s]=i.toString(2).padStart(width,"0"));
 const decode=new Map(Object.entries(code).map(([s,c])=>[c,s]));
 const prefixes=new Set(Object.values(code).flatMap(c=>Array.from({length:width-1},(_,i)=>c.slice(0,i+1))));
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
   if(c.length<width)return prefixes.has(c)?r("read:"+b+":"+c):fail();
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
   if(!sym||!Object.hasOwn(projection,sym))return fail();
   return l("sCross:"+projection[sym],2);
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


function sortWorker(){
 const data=["A0","A1","K0","K1","M0","M1","D","P0","P1","T"];
 const symbols=["__","0_","1_","L","R","E","X","Y","H","J","C",...data];
 const projection={A0:"0",A1:"1",K0:"0",K1:"1",P0:"0",P1:"1",D:"0",T:"1"};
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error("duplicate "+s);defs.set(s,fn)};
 const go=(s,w,d=0)=>[s,w,d],stay=(s,a)=>go(s,a),r=(s,a)=>go(s,a,1),l=(s,a)=>go(s,a,-1);
 const rej=()=>go("reject","__"),raw=a=>a==="0_"||a==="1_",isData=a=>data.includes(a);
 add("init",a=>a==="__"?stay("ready",a):raw(a)?l("left",a):rej());
 add("left",a=>a==="__"?r("first", "L"):rej());
 add("first",a=>a==="0_"?r("keyDigit","A0"):a==="__"?r("makeE","R"):rej());
 add("keyDigit",a=>raw(a)?r("keyMore","K"+a[0]):rej());
 add("keyMore",a=>a==="0_"?r("keyDigit","A0"):a==="1_"?r("divider","A1"):rej());
 add("divider",a=>a==="0_"?l("markBack","D"):rej());
 add("markBack",a=>a==="A1"?l("markLast",a):rej());
 add("markLast",a=>a==="K0"||a==="K1"?r("markReturn","M"+a[1]):rej());
 add("markReturn",a=>a==="A1"?r("markReturn2",a):rej());
 add("markReturn2",a=>a==="D"?r("payload",a):rej());
 add("payload",a=>a==="0_"?r("payloadDigit","A0"):a==="1_"?r("endRecord","A1"):rej());
 add("payloadDigit",a=>raw(a)?r("payload","P"+a[0]):rej());
 add("endRecord",a=>a==="1_"?r("first","T"):rej());
 add("makeE",a=>a==="__"?l("rewind0","E"):rej());
 for(let b of [0,1]){
  add("rewind"+b,a=>a==="L"?r("find"+b,a):a==="__"?rej():l("rewind"+b,a));
  add("find"+b,a=>a==="X"?r("find"+b,a):a===(b?"J":"A0")?r("seek"+b,"H"):a==="R"?(b?r("restoreScan",a):l("rewind1",a)):rej());
  add("seek"+b,a=>a==="M"+b?l("return"+b,a):a==="M"+(1-b)?(b?rej():l("skipReturn",a)):isData(a)?r("seek"+b,a):rej());
  add("return"+b,a=>a==="H"?stay("copy"+b,"A0"):isData(a)?l("return"+b,a):rej());
  add("copy"+b,a=>isData(a)?r("append"+b+a,"C"):rej());
  for(let x of data){
   add("append"+b+x,a=>a==="E"?r("newEnd"+b+x,x):a==="__"?rej():r("append"+b+x,a));
   add("newEnd"+b+x,a=>a==="__"?l("back"+b+x,"E"):rej());
   add("back"+b+x,a=>a==="C"?r(x==="T"?"find"+b:"copy"+b,"X"):a==="__"?rej():l("back"+b+x,a));
  }
 }
 add("skipReturn",a=>a==="H"?r("skip","J"):isData(a)?l("skipReturn",a):rej());
 add("skip",a=>a==="T"?r("find0",a):isData(a)?r("skip",a):rej());
 add("restoreScan",a=>a==="Y"?r("restoreScan",a):a==="E"?l("eraseDest","__"):isData(a)?l("restoreBack"+a,"Y"):rej());
 for(let x of data){
  add("restoreBack"+x,a=>a==="L"?r("restoreSlot"+x,a):a==="__"?rej():l("restoreBack"+x,a));
  add("restoreSlot"+x,a=>a==="X"?r("restoreRight",x):isData(a)?r("restoreSlot"+x,a):rej());
 }
 add("restoreRight",a=>a==="R"?r("restoreScan",a):a==="__"?rej():r("restoreRight",a));
 add("eraseDest",a=>a==="R"?l("rewindUpdate",a):a==="Y"?l("eraseDest","__"):rej());
 add("rewindUpdate",a=>a==="L"?r("update0",a):a==="__"?rej():l("rewindUpdate",a));
 // flags 0 none, 1 continuing, 2 finished. Mixed lengths reject.
 for(let flag of [0,1,2]){
  add("update"+flag,a=>a==="M0"||a==="M1"?l("previous"+flag,"K"+a[1]):a==="R"?(flag===1?r("makeE",a):l("finalBack",a)):isData(a)?r("update"+flag,a):rej());
  add("previous"+flag,a=>a==="A0"?l("previousBit"+flag,a):rej());
  add("previousBit"+flag,a=>{
   if(a==="K0"||a==="K1")return flag===2?rej():r("resumeA1","M"+a[1]);
   if(a==="L"||a==="T")return flag===1?rej():r("resumeA2",a);
   return rej();
  });
 }
 for(let flag of [1,2]){
  add("resumeA"+flag,a=>a==="A0"?r("resumeB"+flag,a):rej());
  add("resumeB"+flag,a=>a==="K0"||a==="K1"?r("update"+flag,a):rej());
 }
 add("finalBack",a=>a==="L"?r("done","__"):a==="__"?rej():l("finalBack",a));
 add("done",a=>isData(a)?stay("ready",a):rej());
 const rules=[];
 for(let [s,fn] of defs)for(let a of symbols){const t=fn(a);if(t[0]!=="reject")rules.push([s,a,...t]);else rules.push([s,a,"reject","__",0]);}
 return {symbols,projection,rules};
}
function encode(records){return records.map(([k,p])=>[...k].map(b=>"0"+b).join("")+"10"+[...p].map(b=>"0"+b).join("")+"11").join("");}
function logicalRun(J,raw,limit=1000000){
 const T=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((b,i)=>[i,b+"_"]));let state="init",head=0,steps=0,trace=[],lo=0,hi=0,passes=0,moves=0,snapshots=[],copySteps=0,restoreSteps=0;
 while(!["ready","reject"].includes(state)&&steps<limit){let a=tape.get(head)??"__",rule=T.get(state+":"+a);if(!rule)throw Error("missing "+state+":"+a);trace.push([state,head,a]);if(trace.length>15)trace.shift();let [s,w,d]=rule;if(/^(copy|append|newEnd|back)[01]/.test(state))copySteps++;if(/^(restoreScan|restoreBack|restoreSlot|restoreRight|eraseDest)/.test(state))restoreSteps++;if(state==="makeE")passes++;if(state==="eraseDest"&&a==="R"){snapshots.push([...tape].filter(([i])=>i>=0&&i<head).sort((a,b)=>a[0]-b[0]).map(([,v])=>v==="M0"?"0":v==="M1"?"1":J.projection[v]??"").join(""));}if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;lo=Math.min(lo,head);hi=Math.max(hi,head);moves+=+(d!==0);state=s;steps++;}
 return {state,head,steps,moves,passes,span:hi-lo+1,trace,snapshots,copySteps,restoreSteps,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"").join("")};
}

function physicalRun(M,raw,limit=50000000){
 let tape=new Map([...raw].map((b,i)=>[i,+b])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0;
 while(state!==M.q&&t<limit){
  let name=M.names[state];ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [s,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=s;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }
 return {tape,head,state,t,span:hi-lo+1,ph,logical};
}
function audit(){
 const J=sortWorker(),M=compile(J.rules,J.symbols,J.projection),ok=(v,s)=>{if(!v)throw Error(s)};
 let counts={cases:0,records:0,rawBits:0,transitions:0,logical:0,passes:0,suffixChecks:0,copySteps:0,restoreSteps:0,cutoffs:0,malformed:0,malformedTransitions:0};
 let cmp=(a,b)=>a<b?-1:a>b?1:0;
 function check(rows,record=true){
  let raw=encode(rows),N=raw.length,w=M.width,want=encode(rows.slice().sort((a,b)=>cmp(a[0],b[0]))),r=physicalRun(M,raw),ref=logicalRun(J,raw,5000000);
  ok(r.state===M.q&&r.tape.size===want.length&&[...want].every((v,i)=>r.tape.get(r.head+i)===+v)&&(want.length||!r.tape.has(r.head)),"sort "+JSON.stringify({rows,head:r.head,t:r.t,ref:ref.trace}));
  ok(ref.state==="ready"&&ref.out===want&&ref.steps===r.logical,"logical reference");
  let k=rows.length?rows[0][0].length:0;
  ok(ref.passes===k&&ref.snapshots.length===k,"pass count");
  ok(ref.copySteps===k*(2*N*N+5*N)&&ref.restoreSteps===k*(3*N*N+5*N+2),"transfer clock "+JSON.stringify({N,k,copy:ref.copySteps,restore:ref.restoreSteps}));
  for(let j=1;j<=k;j++){
   let expected=encode(rows.slice().sort((a,b)=>cmp(a[0].slice(-j),b[0].slice(-j))));
   ok(ref.snapshots[j-1]===expected,"stable suffix pass");
  }
  let prep=N?(w+1)*N*(N+1)+(w+4)*N+3:1;
  let serial=N?(w+1)*N*N+(3*w+6)*N+2*w+5:1;
  let mid=(3*w-2)*ref.moves+(2*w-1)*(ref.steps-ref.moves);
  ok(JSON.stringify(r.ph)===JSON.stringify([prep,mid,serial]),"phase "+JSON.stringify({N,r:r.ph,expected:[prep,mid,serial]}));
  ok(r.head===(N?-(w+1)*N-2:0),"head");
  ok(r.span===(N?(2*w+1)*N+2*w+2:w),"span "+JSON.stringify({N,span:r.span}));
  if(record){counts.cases++;counts.records+=rows.length;counts.rawBits+=N;counts.transitions+=r.t;counts.logical+=r.logical;counts.passes+=k;counts.suffixChecks+=k;counts.copySteps+=ref.copySteps;counts.restoreSteps+=ref.restoreSteps;}
  return r;
 }
 let cases=[[],[["0",""]],[["1","10"],["0","1"],["1","0"]],[["11",""],["00","1"],["10","0"],["01","11"]],[["1",""],["1","0"],["1","01"],["1","1"]]];
 for(let rows of cases){let r=check(rows);ok(physicalRun(M,encode(rows),r.t-1).state!==M.q,"cutoff");counts.cutoffs++;}
 // Exhaust every ordered sequence of up to four one-bit keys and up to three
 // two-bit keys, with distinct payload IDs, verifying duplicate-key stability.
 for(let k of [1,2])for(let n=1;n<=(k===1?4:3);n++)for(let j=0;j<2**(k*n);j++){
  let word=j.toString(2).padStart(k*n,"0"),rows=Array.from({length:n},(_,i)=>[word.slice(k*i,k*(i+1)),i.toString(2)]);
  check(rows);
 }
 // Seeded variable-size payloads, multi-bit keys and long common prefixes.
 let seed=0x52455804;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let j=0;j<12;j++){
  let k=3+j%3,n=2+j%4,rows=Array.from({length:n},()=>[(rand()%2**k).toString(2).padStart(k,"0"),(rand()%16).toString(2)]);
  check(rows);
 }
 check([["000000000001","101"],["000000000000","0"],["000000000001","11"]]);
 // Distinct key widths, empty key, malformed token stream or incomplete record.
 for(let raw of ["0","00","10","11","0010","0010110","001010","001001","00101111",encode([["0",""],["00",""]]),encode([["11","1"],["1","0"]]),encode([["00",""],["00",""],["1",""]])]){
  let r=physicalRun(M,raw,2000000),ref=logicalRun(J,raw);
  ok(r.state===M.q&&!r.tape.has(r.head)&&ref.state==="reject","reject "+raw);counts.malformed++;counts.malformedTransitions+=r.t;
 }
 let scaling=[];
 for(let n of [4,8,16]){
  let k=Math.ceil(Math.log2(n)),rows=Array.from({length:n},(_,i)=>[(n-1-i).toString(2).padStart(k,"0"),i.toString(2).padStart(k,"0")]);
  let r=check(rows,false);scaling.push([n,k,encode(rows).length,r.t,r.logical,r.span,r.ph]);
 }
 // Exhaust short raw strings against a separate grammar parser.
 let grammar={cases:0,valid:0,rejected:0,transitions:0};
 function parse(raw){
  if(raw.length%2)return null;
  let records=[],k="",p="",keyMode=true;
  for(let i=0;i<raw.length;i+=2){
   let t=raw.slice(i,i+2);
   if(t[0]==="0"){if(keyMode)k+=t[1];else p+=t[1];}
   else if(t==="10"){if(!keyMode||!k)return null;keyMode=false;}
   else {if(keyMode)return null;records.push([k,p]);k="";p="";keyMode=true;}
  }
  return keyMode&&!k&&records.every(([k])=>k.length===records[0][0].length)?records:null;
 }
 for(let n=0;n<=8;n++)for(let i=0;i<2**n;i++){
  let raw=n?i.toString(2).padStart(n,"0"):"",r=physicalRun(M,raw),rows=parse(raw);
  ok(r.state===M.q,"grammar halt");grammar.cases++;grammar.transitions+=r.t;
  if(rows===null){ok(!r.tape.has(r.head),"grammar rejection");grammar.rejected++;}
  else {let want=encode(rows.slice().sort((a,b)=>cmp(a[0],b[0])));ok(r.tape.size===want.length&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b),"grammar output");grammar.valid++;}
 }
 let pos=3;while(M.desc[pos]==="1")pos++;
 ok(pos-3===M.q&&M.desc[pos++]==="0","header");let b=M.q.toString(2).length,decoded=[];
 for(let [s,w,d] of M.T){let row=[parseInt(M.desc.slice(pos,pos+b),2),parseInt(M.desc.slice(pos+b,pos+b+2),2),parseInt(M.desc.slice(pos+b+2,pos+b+4),2)-1];ok(row[0]===s&&row[1]===w&&row[2]===d,"descriptor");decoded.push(row);pos+=b+4;}
 ok(pos===M.desc.length,"length");
 // Original small selector format is not the record-sort format.
 // Replay using the emitted description's decoded transition entries.
 let U={selectorInputs:0,noCandidate:0};
 for(let n of [1,2])for(let p=0;p<2**(n===1?2:8);p++){
  let raw="1".repeat(n)+"0"+Array.from({length:n===1?2:8},(_,i)=>(p>>i)&1).join("");
  let tape=new Map([...raw].map((v,i)=>[i,+v])),head=0,state=0;
  for(let t=0;t<10000&&state!==M.q;t++){
   let [a,w,d]=decoded[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);head+=d;state=a;
  }
  ok(state===M.q&&!tape.has(head),"selector non-solver control");U.selectorInputs++;U.noCandidate++;
 }
 return {alphabet:J.symbols.length,logicalStates:new Set(J.rules.map(r=>r[0])).size,logicalRules:J.rules.length,width:M.width,states:M.q,bits:M.desc.length,counts,scaling,grammar,U};
}
if(process.argv.includes('--description')){let j=sortWorker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_STABLE_RECORD_SORT_OK '+JSON.stringify(audit()));
