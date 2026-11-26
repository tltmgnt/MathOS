// REX-006 prepared batched multifactor AND / outgoing OR, same tape.
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
 const T=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((b,i)=>[i,b+"_"]));let state="init",head=0,steps=0,trace=[],lo=0,hi=0,passes=0,moves=0,snapshots=[],copySteps=0,restoreSteps=0,joinSteps=0,joinMoves=0,inJoin=false,compares=0;
 while(!["ready","reject"].includes(state)&&steps<limit){let a=tape.get(head)??"__",rule=T.get(state+":"+a);if(!rule)throw Error("missing "+state+":"+a);trace.push([state,head,a]);if(trace.length>15)trace.shift();let [s,w,d]=rule;if(/^(s[12])?(copy|append|newEnd|back)[01]/.test(state))copySteps++;if(/^(s[12])?(restoreScan|restoreBack|restoreSlot|restoreRight|eraseDest)/.test(state))restoreSteps++;if(state==="joinLeft")inJoin=true;if(inJoin){joinSteps++;joinMoves+=+(d!==0);}if(/^readQuery[012]Scan$/.test(state)&&/^U[012]$/.test(a))compares++;if(/^(s[12])?makeE$/.test(state))passes++;if(/^(s[12])?eraseDest$/.test(state)&&a==="R"){snapshots.push([...tape].filter(([i])=>i>=0&&i<head).sort((a,b)=>a[0]-b[0]).map(([,v])=>v==="M0"?"0":v==="M1"?"1":J.projection[v]??"").join(""));}if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;lo=Math.min(lo,head);hi=Math.max(hi,head);moves+=+(d!==0);state=s;steps++;}
 return {state,head,steps,moves,passes,span:hi-lo+1,trace,snapshots,copySteps,restoreSteps,joinSteps,joinMoves,compares,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"").join("")};
}

function physicalRun(M,raw,limit=50000000){
 let tape=new Map([...raw].map((b,i)=>[i,+b])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,joinPhysical=0,inJoin=false,boundary=null,checkpoints=[];
 while(state!==M.q&&t<limit){
  let name=M.names[state];if(/^read:(r[12]Left|a[12]Left):$/.test(name))checkpoints.push({name,head,words:[...tape.entries()].sort((a,b)=>a[0]-b[0])});if(name==="read:joinLeft:"){inJoin=true;boundary={head,words:[...tape.entries()].sort((a,b)=>a[0]-b[0])};}if(inJoin&&name[0]!=="s")joinPhysical++;ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [s,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=s;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }
 return {tape,head,state,t,span:hi-lo+1,ph,logical,joinPhysical,boundary,checkpoints};
}

function joinedWorker(){
 const J=sortWorker(),extra=["F","Q","V0","V1","V2","U0","U1","U2"];
 const symbols=J.symbols.concat(extra),defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error("duplicate "+s);defs.set(s,fn)};
 const go=(s,w,d=0)=>[s,w,d],r=(s,a)=>go(s,a,1),l=(s,a)=>go(s,a,-1),z=(s,a)=>go(s,a),bad=()=>go("reject","__");
 const data=a=>a!=="__"&&a!=="L"&&a!=="R";
 // The sorter has just removed its left sentinel, with the source intact.
 // Reinstall it and tag the final key digit of each record (the role).
 add("joinLeft",a=>a==="__"?r("joinTag","L"):bad());
 add("joinTag",a=>a==="D"?l("joinTagBack",a):a==="R"?l("joinRewind",a):data(a)?r("joinTag",a):bad());
 add("joinTagBack",a=>a==="A1"?l("joinTagRole",a):bad());
 add("joinTagRole",a=>a==="K0"||a==="K1"?r("joinTagResume","M"+a[1]):bad());
 add("joinTagResume",a=>a==="A1"?r("joinTagSkipD",a):bad());
 add("joinTagSkipD",a=>a==="D"?r("joinTag",a):bad());
 add("joinRewind",a=>a==="L"?r("record0",a):a==="__"?bad():l("joinRewind",a));
 for(let has of [0,1]){
  add("record"+has,a=>a==="A0"?r("role"+has,"H"):a==="R"?l("joinClean",a):bad());
  add("role"+has,a=>a==="M0"?l("factorBack",a):a==="M1"?l("queryBack"+has,a):data(a)?r("role"+has,a):bad());
  add("queryBack"+has,a=>a==="H"?z(has?"queryInit":"flagSeek0","Q"):data(a)?l("queryBack"+has,a):bad());
 }
 // Replace previous factor start with the latest factor's start.
 add("factorBack",a=>a==="H"?l("factorClear",a):data(a)?l("factorBack",a):bad());
 add("factorClear",a=>a==="L"?r("factorFind",a):a==="F"?l("factorClear","A0"):data(a)?l("factorClear",a):bad());
 add("factorFind",a=>a==="H"?r("factorSkip","F"):data(a)?r("factorFind",a):bad());
 add("factorSkip",a=>a==="T"?r("record1",a):data(a)?r("factorSkip",a):bad());
 // Every cursor lookup rewinds to L; bounded full-region scans.
 function find(s,p,act){
  add(s,a=>a==="L"?r(s+"Scan",a):a==="__"?bad():l(s,a));
  add(s+"Scan",a=>p(a)?act(a):data(a)?r(s+"Scan",a):bad());
 }
 const fcur=a=>/^V[012]$/.test(a),qcur=a=>/^U[012]$/.test(a);
 const cv=(a,p)=>a==="K0"||a==="K1"?p+a[1]:a==="M"+(p==="V"?0:1)?p+"2":null;
 const restore=a=>a==="V2"?"M0":a==="U2"?"M1":"K"+a[1];
 add("queryInit",a=>a==="Q"?r("queryFirst",a):bad());
 add("queryFirst",a=>cv(a,"U")?z("factorInit",cv(a,"U")):bad());
 find("factorInit",a=>a==="F",a=>r("factorFirst",a));
 add("factorFirst",a=>cv(a,"V")?z("readFactor",cv(a,"V")):bad());
 find("readFactor",fcur,a=>z("readQuery"+a[1],a));
 for(let b of [0,1,2]){
  find("readQuery"+b,qcur,a=>{
   if(+a[1]!==b)return z("reset0",a);
   if(b===2)return z("reset1",a);
   return r("queryNextA",restore(a));
  });
 }
 add("queryNextA",a=>a==="A0"?r("queryNext",a):bad());
 add("queryNext",a=>cv(a,"U")?z("advanceFactor",cv(a,"U")):bad());
 find("advanceFactor",fcur,a=>r("factorNextA",restore(a)));
 add("factorNextA",a=>a==="A0"?r("factorNext",a):bad());
 add("factorNext",a=>cv(a,"V")?z("readFactor",cv(a,"V")):bad());
 for(let b of [0,1]){
  add("reset"+b,a=>a==="L"?r("resetScan"+b,a):a==="__"?bad():l("reset"+b,a));
  add("resetScan"+b,a=>a==="R"?l("findQuery"+b,a):fcur(a)||qcur(a)?r("resetScan"+b,restore(a)):data(a)?r("resetScan"+b,a):bad());
  add("findQuery"+b,a=>a==="Q"?z("flagSeek"+b,a):data(a)?l("findQuery"+b,a):bad());
  add("flagSeek"+b,a=>a==="Q"?r("flagDivider"+b,"A0"):bad());
  add("flagDivider"+b,a=>a==="D"?r("flagToken"+b,a):data(a)?r("flagDivider"+b,a):bad());
  add("flagToken"+b,a=>a==="A0"?r("flagWrite"+b,a):bad());
  add("flagWrite"+b,a=>a==="P0"||a==="P1"?r(b?"querySkip1":"querySkip0","P"+b):bad());
 }
 // A miss may have a previous factor, so preserve has-factor state separately.
 // Both skip paths recover existence from the retained F marker.
 for(let b of [0,1])add("querySkip"+b,a=>a==="T"?z("queryEnd", "J"):data(a)?r("querySkip"+b,a):bad());
 add("queryEnd",a=>a==="L"?r("hasScan0",a):a==="__"?bad():l("queryEnd",a));
 for(let h of [0,1])add("hasScan"+h,a=>a==="F"?r("hasScan1",a):a==="J"?r("record"+h,"T"):data(a)?r("hasScan"+h,a):bad());
 add("joinClean",a=>a==="L"?r("joinReady","__"):a==="F"?l("joinClean","A0"):a==="M0"||a==="M1"?l("joinClean","K"+a[1]):data(a)?l("joinClean",a):bad());
 add("joinReady",a=>a==="A0"?z("ready",a):bad());
 const rules=J.rules.map(row=>row[0]==="done"&&row[2]==="ready"?[row[0],row[1],"joinLeft",row[3],-1]:row);
 for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection:J.projection,rules};
}

function eliminationWorker(){
 const J=joinedWorker(),symbols=J.symbols, rules=J.rules.map(row=>row[0]==="joinReady"&&row[2]==="ready"?[row[0],row[1],"r1Left",row[3],-1]:row);
 const S=sortWorker(),sortStates=new Set(S.rules.map(x=>x[0]));
 for(let j of [1,2])for(let [s,a,t,w,d] of S.rules){
  if(s==="done"&&t==="ready"){rules.push(["s"+j+s,a,"a"+j+"Left",w,-1]);continue;}
  rules.push(["s"+j+s,a,sortStates.has(t)?"s"+j+t:t,w,d]);
 }
 const defs=new Map(),bad=()=>["reject","__",0],data=a=>a!=="__"&&a!=="L"&&a!=="R";
 for(let stage of [1,2]){
  for(let type of ["r","a"]){
   const p=type+stage;
   const add=(s,fn)=>{if(defs.has(p+s))throw Error(p+s);defs.set(p+s,fn)};
   const go=(s,w,d=0)=>[p+s,w,d],r=(s,a)=>go(s,a,1),l=(s,a)=>go(s,a,-1),z=(s,a)=>go(s,a);
   function find(s,pred,act){
    add(s,a=>a==="L"?r(s+"Scan",a):a==="__"?bad():l(s,a));
    add(s+"Scan",a=>pred(a)?act(a):data(a)?r(s+"Scan",a):bad());
   }
   const K=a=>a==="K0"||a==="K1",P=a=>a==="P0"||a==="P1",V=a=>/^V[012]$/.test(a),U=a=>/^U[012]$/.test(a);
   const restore=a=>a[1]==="2"?"D":"K"+a[1];
   function flagPath(name,offset,action){
    add(name,a=>a==="D"?r(name+"A0",a):data(a)?r(name,a):bad());
    for(let i=0;i<=offset;i++){
     add(name+"A"+i,a=>a==="A0"?r(name+"P"+i,a):bad());
     add(name+"P"+i,a=>P(a)?i===offset?action(a):r(name+"A"+(i+1),a):bad());
    }
   }
   if(type==="r"){
    add("Left",a=>a==="__"?r("Record","L"):bad());
    add("Record",a=>a==="A0"?r("First","H"):a==="R"?l("MarkBack",a):bad());
    add("First",a=>K(a)?r("SeekD","V"+a[1]):bad());
    flagPath("SeekD",2,a=>r(stage===1?"PairA":"SkipA",a));
    if(stage===2){
     add("SkipA",a=>a==="A0"?r("SkipP",a):bad());
     add("SkipP",a=>a==="P0"?r("SkipBitA",a):a==="P1"?r("SkipEndA",a):bad());
     add("SkipBitA",a=>a==="A0"?r("SkipBit",a):bad());
     add("SkipBit",a=>P(a)?r("SkipA",a):bad());
     add("SkipEndA",a=>a==="A0"?r("SkipEnd",a):bad());
     add("SkipEnd",a=>a==="P1"?r("PairA",a):bad());
    }
    add("PairA",a=>a==="A0"?r("PairP",a):bad());
    add("PairP",a=>a==="P0"?r("BitA",a):bad());
    add("BitA",a=>a==="A0"?r("BitP",a):bad());
    add("BitP",a=>P(a)?z("TakeKey","U"+a[1]):bad());
    find("TakeKey",a=>a==="V0"||a==="V1",a=>z("TakePayload"+a[1],a));
    for(let b of [0,1]){
     find("TakePayload"+b,a=>a==="U0"||a==="U1",a=>z("WriteKey"+a[1],"U"+b));
     find("WriteKey"+b,a=>a==="V0"||a==="V1",a=>r("NextKeyA","K"+b));
    }
    add("NextKeyA",a=>a==="A0"?r("NextKey",a):a==="A1"?r("KeyEnd",a):bad());
    add("NextKey",a=>K(a)?z("NextPayload","V"+a[1]):bad());
    add("KeyEnd",a=>a==="D"?z("EndPayload",a):bad());
    find("NextPayload",a=>a==="U0"||a==="U1",a=>r("PairA","P"+a[1]));
    find("EndPayload",a=>a==="U0"||a==="U1",a=>r("EndA","P"+a[1]));
    add("EndA",a=>a==="A0"?r("EndP",a):bad());
    add("EndP",a=>a==="P1"?r("EndA2",a):bad());
    add("EndA2",a=>a==="A0"?r("EndP2",a):bad());
    add("EndP2",a=>a==="P1"?z("RestoreStart",a):bad());
    find("RestoreStart",a=>a==="H",a=>r("SkipRecord","A0"));
    add("SkipRecord",a=>a==="T"?r("Record",a):data(a)?r("SkipRecord",a):bad());
    // All records have been rekeyed. Mark rightmost key digits for next radix sort.
    add("MarkBack",a=>a==="L"?r("Mark",a):data(a)?l("MarkBack",a):bad());
    add("Mark",a=>a==="D"?l("MarkA",a):a==="R"?["s"+stage+"makeE",a,1]:data(a)?r("Mark",a):bad());
    add("MarkA",a=>a==="A1"?l("MarkDigit",a):bad());
    add("MarkDigit",a=>K(a)?r("MarkResume","M"+a[1]):bad());
    add("MarkResume",a=>a==="A1"?r("MarkD",a):bad());
    add("MarkD",a=>a==="D"?r("Mark",a):bad());
   }else{
    add("Left",a=>a==="__"?r("Record0","L"):bad());
    for(let h of [0,1]){
     add("Record"+h,a=>a==="A0"?r("Role"+h,a):a==="R"?l("Clean",a):bad());
     add("Role"+h,a=>a==="K0"?r("Skip"+h,a):a==="K1"?l("MarkQ"+h,a):bad());
     add("Skip"+h,a=>a==="T"?r("Record"+h,a):data(a)?r("Skip"+h,a):bad());
     add("MarkQ"+h,a=>a==="A0"?z(h?"QFirst":"InputNew","Q"):bad());
    }
    add("QFirst",a=>a==="Q"?r("QDigit",a):bad());
    add("QDigit",a=>K(a)?z("FStart","U"+a[1]):bad());
    find("FStart",a=>a==="F",a=>r("FDigit",a));
    add("FDigit",a=>K(a)?z("ReadF","V"+a[1]):bad());
    find("ReadF",V,a=>z("ReadQ"+a[1],a));
    for(let b of [0,1,2])find("ReadQ"+b,U,a=>a[1]!==String(b)?z("Reset0",a):b===2?z("Reset1",a):r("NextQA",restore(a)));
    add("NextQA",a=>a==="A0"?r("NextQD",a):a==="A1"?r("NextQE",a):bad());
    add("NextQD",a=>K(a)?z("AdvanceF","U"+a[1]):bad());
    add("NextQE",a=>a==="D"?z("AdvanceF","U2"):bad());
    find("AdvanceF",V,a=>r("NextFA",restore(a)));
    add("NextFA",a=>a==="A0"?r("NextFD",a):a==="A1"?r("NextFE",a):bad());
    add("NextFD",a=>K(a)?z("ReadF","V"+a[1]):bad());
    add("NextFE",a=>a==="D"?z("ReadF","V2"):bad());
    for(let eq of [0,1]){
     add("Reset"+eq,a=>a==="L"?r("ResetScan"+eq,a):a==="__"?bad():l("Reset"+eq,a));
     add("ResetScan"+eq,a=>a==="R"?z(eq?"Prev":"InputNew",a):V(a)||U(a)?r("ResetScan"+eq,restore(a)):data(a)?r("ResetScan"+eq,a):bad());
    }
    // InputNew may start anywhere; find current Q. Prev reads running
    // reduction at previous record and clears its output flag before advancing.
    find("InputNew",a=>a==="Q",a=>r("Input0",a));
    find("Prev",a=>a==="F",a=>r("PrevFlag",a));
    flagPath("PrevFlag",stage,a=>z("InputWith"+a[1],"P0"));
    for(let v of [0,1]){
     find("InputWith"+v,a=>a==="Q",a=>r("Input"+(v+1),a));
    }
    for(let mode of [0,1,2]){
     flagPath("Input"+mode,stage-1,a=>{
      let b=+a[1],out=mode===0?b:stage===1?b&(mode-1):b|(mode-1);
      return r("OutputA"+out,a);
     });
    }
    for(let b of [0,1]){
     add("OutputA"+b,a=>a==="A0"?r("OutputP"+b,a):bad());
     add("OutputP"+b,a=>P(a)?z("ClearOld","P"+b):bad());
    }
    add("ClearOld",a=>a==="L"?r("FindQ",a):a==="F"?l("ClearOld","A0"):data(a)?l("ClearOld",a):bad());
    add("FindQ",a=>a==="Q"?r("FinishRecord","F"):data(a)?r("FindQ",a):bad());
    add("FinishRecord",a=>a==="T"?r("Record1",a):data(a)?r("FinishRecord",a):bad());
    add("Clean",a=>a==="L"?r("Done","__"):a==="F"?l("Clean","A0"):data(a)?l("Clean",a):bad());
    add("Done",a=>a==="A0"?stage===1?["r2Left",a,-1]:["ready",a,0]:bad());
   }
  }
 }
 for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection:J.projection,rules};
}
function field(s){return [...s].map(b=>"0"+b).join("")+"11";}
function makeRecord(key,role,candidate,group,id,flags="000"){return [key+role,flags+field(candidate)+field(group)+id];}
function refEliminate(rows,trace=null){
 const sort=xs=>xs.slice().sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0);
 const F=new Set(rows.filter(([k])=>k.endsWith("0")).map(([k])=>k.slice(0,-1)));
 let r=sort(rows).map(([k,p])=>[k,k.endsWith("1")?(F.has(k.slice(0,-1))?"1":"0")+p.slice(1):p]);
 if(trace)trace.push(encode(r));
 function swap([k,p],slot){
  let start=3+slot*(2*k.length+2),key="";
  for(let i=0;i<k.length;i++)key+=p[start+2*i+1];
  return [key,p.slice(0,start)+field(k)+p.slice(start+2*k.length+2)];
 }
 for(let stage of [1,2]){
  r=sort(r.map(x=>swap(x,stage-1)));if(trace)trace.push(encode(r));
  for(let i=0;i<r.length;){
   let j=i+1;while(j<r.length&&r[j][0]===r[i][0])j++;
   if(r[i][0].startsWith("1")){
    let out=stage===1?1:0;
    for(let a=i;a<j;a++)out=stage===1?out&+r[a][1][stage-1]:out|+r[a][1][stage-1];
    for(let a=i;a<j;a++)r[a][1]=r[a][1].slice(0,stage)+(a===j-1?out:0)+r[a][1].slice(stage+1);
   }
   i=j;
  }
  if(trace&&stage===1)trace.push(encode(r));
 }
 return r;
}

function audit(){
 const J=eliminationWorker(),M=compile(J.rules,J.symbols,J.projection),ok=(v,s)=>{if(!v)throw Error(s)};
 const counts={physicalCases:0,logicalOnly:0,records:0,requests:0,positiveMembership:0,candidateGroups:0,feasibleCandidates:0,outgoingGroups:0,positiveOutgoing:0,physicalTransitions:0,logicalTransitions:0,radixPasses:0,boundaryChecks:0,cutoffs:0,malformed:0,malformedTransitions:0};
 const decode=new Map(Object.entries(M.code).map(([a,c])=>[c,a]));
 function check(rows,physical=true){
  let raw=encode(rows),N=raw.length,k=rows.length?rows[0][0].length:0,w=M.width,trace=[],expected=refEliminate(rows,trace),want=encode(expected),ref=logicalRun(J,raw,15000000);
  ok(ref.state==="ready"&&ref.out===want,"logical "+JSON.stringify({rows,trace:ref.trace}));
  ok(ref.passes===3*k&&ref.copySteps===3*k*(2*N*N+5*N)&&ref.restoreSteps===3*k*(3*N*N+5*N+2),"three sort clock "+JSON.stringify([N,k,ref.passes,ref.copySteps,ref.restoreSteps]));
  let F=new Set(rows.filter(([k])=>k.endsWith("0")).map(([k])=>k.slice(0,-1))),C=new Map(),G=new Map(),members=0,q=0;
  function readField(p,start){let key="";while(p.slice(start,start+2)!=="11"){key+=p[start+1];start+=2;}return key;}
  for(let [key,p] of rows)if(key.endsWith("1")){
   let c=readField(p,3),g=readField(p,3+2*k+2),b=+F.has(key.slice(0,-1));q++;members+=b;
   if(!C.has(c))C.set(c,{g,b:1});ok(C.get(c).g===g,"fixture group consistency");C.get(c).b &= b;
  }
  for(let {g,b} of C.values())G.set(g,(G.get(g)??0)|b);
  let cq=new Map(),gq=new Map(),mout=0;
  for(let [g,p] of expected)if(g.startsWith("1")){
   let c=readField(p,3+2*k+2);cq.set(c,(cq.get(c)??0)+ +p[1]);gq.set(g,(gq.get(g)??0)+ +p[2]);mout+=+p[0];
  }
  ok(mout===members&&cq.size===C.size&&gq.size===G.size&&[...C].every(([c,x])=>cq.get(c)===x.b)&&[...G].every(([g,b])=>gq.get(g)===b),"independent relational semantics");
  if(!physical){counts.logicalOnly++;return null;}
  let r=physicalRun(M,raw,300000000);
  ok(r.state===M.q&&r.logical===ref.steps&&r.tape.size===want.length&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b)&&(N||!r.tape.has(r.head)),"physical "+JSON.stringify([N,r.t,r.state,M.q]));
  let prep=N?(w+1)*N*(N+1)+(w+4)*N+3:1,serial=N?(w+1)*N*N+(3*w+6)*N+2*w+5:1,mid=(3*w-2)*ref.moves+(2*w-1)*(ref.steps-ref.moves);
  ok(JSON.stringify(r.ph)===JSON.stringify([prep,mid,serial]),"phase clocks");
  ok(r.head===(N?-(w+1)*N-2:0)&&r.span===(N?(2*w+1)*N+2*w+2:w),"head/span");
  if(N){
   ok(r.checkpoints.length===4&&trace.length===4,"checkpoint count");
   for(let i=0;i<4;i++){
    let b=r.checkpoints[i],bits=b.words.map(x=>x[1]).join(""),project="";
    ok(b.head===-w*N-1-w&&b.words.length===w*(N+1),"checkpoint layout");
    for(let j=0;j<N;j++)project+=J.projection[decode.get(bits.slice(w*j,w*(j+1)))];
    ok(bits.slice(-w)===M.code.R&&project===trace[i],"physical boundary "+i);counts.boundaryChecks++;
   }
  }
  counts.physicalCases++;counts.records+=rows.length;counts.requests+=q;counts.positiveMembership+=members;counts.candidateGroups+=C.size;counts.feasibleCandidates+=[...C.values()].reduce((a,x)=>a+x.b,0);counts.outgoingGroups+=G.size;counts.positiveOutgoing+=[...G.values()].reduce((a,b)=>a+b,0);counts.physicalTransitions+=r.t;counts.logicalTransitions+=r.logical;counts.radixPasses+=ref.passes;
  return [N,r.t,r.logical,r.span,r.ph];
 }
 const f=(key,id="")=>makeRecord(key,"0","000","000",id);
 const q=(key,c,g,id="",flags="000")=>makeRecord(key,"1",c,g,id,flags);
 const cases=[[],[makeRecord("","0","0","0","")],[makeRecord("","1","1","1","")],[makeRecord("","0","0","0",""),makeRecord("","1","1","1","")],
 [q("01","100","110","1"),f("00"),q("00","100","110","0"),q("00","101","110","10")],
 [q("01","100","110"),q("00","100","110"),f("00"),f("01")],
 [q("00","100","110"),q("01","100","110")],
 [q("00","100","110","0","111"),q("01","101","111","1","111"),f("00"),q("00","100","110","10","111")]];
 let fixtures=cases.map(x=>check(x));
 for(let i of [0,3]){let raw=encode(cases[i]),clock=fixtures[i][1];ok(physicalRun(M,raw,clock-1).state!==M.q,"one short");counts.cutoffs++;}
 for(let mask=0;mask<4;mask++){
  let rows=[q("00","100","110","0"),q("01","100","110","1"),q("01","101","110","10")];
  if(mask&1)rows.push(f("00"));if(mask&2)rows.push(f("01"));
  for(let j=0;j<rows.length;j++)check(rows.slice(j).concat(rows.slice(0,j)),false);
 }
 for(let raw of ["0","11","0010",encode([["1",""]]),encode([["1","000"]]),encode([["0","000"+field("00")+field("0")]]),encode([["0","000"+field("0")+field("00")]])]){
  let r=physicalRun(M,raw,20000000);ok(r.state===M.q&&!r.tape.has(r.head),"malformed "+raw);counts.malformed++;counts.malformedTransitions+=r.t;
 }
 // TECT-X: independent per-batch OR is unsound if one candidate's
 // factor requests are split across batches. Actual logical worker replay.
 function outgoing(rows){
  let r=logicalRun(J,encode(rows),15000000);ok(r.state==="ready","adversarial worker halt");
  let expected=refEliminate(rows);ok(r.out===encode(expected),"adversarial worker output");
  return expected.filter(([k])=>k.startsWith("1")).reduce((a,[,p])=>a|+p[2],0);
 }
 let left=[f("00"),q("00","100","110")],right=[f("00"),q("01","100","110")];
 let full=[f("00"),q("00","100","110"),q("01","100","110")];
 let split=[outgoing(left),outgoing(right)],whole=outgoing(full);
 ok(split[0]===1&&split[1]===0&&whole===0,"candidate split counterexample");
 // Duplicate requests/factors do not change the existential result.
 check([f("00"),f("00","1"),q("00","100","110","0"),q("00","100","110","1")],false);
 let adversarial={splitBatchFlags:split,incorrectOR:split[0]|split[1],wholeCandidate:whole,missingRequestNotDetected:true};
 let pos=3;while(M.desc[pos]==="1")pos++;ok(pos-3===M.q&&M.desc[pos++]==="0","header");let b=M.q.toString(2).length;
 for(let [s,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===s&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
 ok(pos===M.desc.length,"descriptor length");
 return {alphabet:J.symbols.length,logicalStates:new Set(J.rules.map(r=>r[0])).size,logicalRules:J.rules.length,width:M.width,states:M.q,bits:M.desc.length,counts,fixtures,adversarial};
}
module.exports={compile,eliminationWorker,encode,makeRecord,field,refEliminate,logicalRun,physicalRun,audit};
if(require.main===module) { if(process.argv.includes('--description')){let j=eliminationWorker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_BATCHED_ELIMINATION_OK '+JSON.stringify(audit()));

}
