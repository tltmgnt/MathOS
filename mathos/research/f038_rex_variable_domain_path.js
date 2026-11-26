// REX-011 variable-domain path, raw factor masks, persistent physical messages and predecessor marks.
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




function worker(){
 const symbols=["__","0_","1_","L","R","Z","A","S","B","D","U0","U1","E0","E1","P","K0","K1","K2","Q0","Q1","W","T00","T01","T10","T11","C00","C01","C10","C11"];
 const projection=Object.fromEntries(symbols.filter(a=>a!=="__").map(a=>[a,a==="W"?"1":/^T/.test(a)?"0":"_"]));
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error(s);defs.set(s,fn)},go=(s,w,d=0)=>[s,w,d],r=(s,a)=>go(s,a,1),l=(s,a)=>go(s,a,-1),z=(s,a)=>go(s,a),bad=()=>z("reject","__");
 const raw=a=>a==="0_"||a==="1_",data=a=>a!=="__"&&a!=="L"&&a!=="R",T=a=>/^T[01][01]$/.test(a),C=a=>/^C[01][01]$/.test(a),K=a=>/^K[012]$/.test(a);
 function find(s,pred,act){
  add(s,a=>a==="L"?r(s+"Scan",a):a==="__"?bad():l(s,a));
  add(s+"Scan",a=>pred(a)?act(a):data(a)?r(s+"Scan",a):bad());
 }
 add("init",a=>raw(a)?l("left",a):bad());
 add("left",a=>a==="__"?r("initialFirst","L"):bad());
 add("initialFirst",a=>a==="0_"?r("initialBit","Z"):bad());
 add("initialBit",a=>raw(a)?r("initialNext","T"+a[0]+a[0]):bad());
 add("initialNext",a=>a==="0_"?r("initialBit","Z"):a==="1_"?r("initialEnd","Z"):bad());
 add("initialEnd",a=>a==="1_"?r("stageStart","A"):bad());
 add("stageStart",a=>a==="__"?l("rewind","R"):a==="0_"?r("unaryBit","Z"):bad());
 add("unaryBit",a=>raw(a)?r("edgeFirst","U"+a[0]):bad());
 add("edgeFirst",a=>a==="0_"?r("edgeBit","Z"):bad());
 add("edgeBit",a=>raw(a)?r("edgeNext","E"+a[0]):bad());
 add("edgeNext",a=>a==="0_"?r("edgeBit","Z"):a==="1_"?r("columnEnd","Z"):bad());
 add("columnEnd",a=>a==="0_"?r("columnNext","D"):bad());
 add("columnNext",a=>a==="0_"?r("unaryBit","Z"):a==="1_"?r("stageEnd","Z"):bad());
 add("stageEnd",a=>a==="1_"?r("stageStart","S"):bad());
 add("rewind",a=>a==="L"?r("startScan",a):a==="__"?bad():l("rewind",a));
 add("startScan",a=>a==="A"?r("forward",a):data(a)?r("startScan",a):bad());
 add("forward",a=>a==="Z"?r("forward",a):a==="U0"||a==="U1"?r("fFirst"+a[1],"Q"+a[1]):a==="S"?z("shiftOld","B"):a==="R"?z("lastBoundary",a):bad());
 find("shiftOld",a=>a==="A",a=>z("shiftNew","S"));
 find("shiftNew",a=>a==="B",a=>r("forward","A"));
 for(let u of [0,1]){
  add("fFirst"+u,a=>a==="Z"?r("fFirst"+u,a):a==="E0"||a==="E1"?z("fSource"+u,"K"+a[1]):bad());
  find("fSource"+u,a=>a==="A",a=>l("fStart"+u,a));
  add("fStart"+u,a=>a==="S"||a==="L"?r("fSrcFirst"+u,a):a==="__"?bad():l("fStart"+u,a));
  add("fSrcFirst"+u,a=>T(a)?z("fRead"+u+"0","C"+a.slice(1)):data(a)&&a!=="A"?r("fSrcFirst"+u,a):bad());
  for(let hit of [0,1]){
   let h=""+u+hit;
   find("fRead"+h,C,a=>z("fEdge"+h+a[2],a));
   for(let m of [0,1]){
    find("fEdge"+h+m,a=>a==="K0"||a==="K1",a=>{
     let yes=u&&m&&a==="K1"&&!hit;
     return r("fNextEdge"+u+(hit||yes?1:0),yes?"P":"E"+a[1]);
    });
   }
   add("fNextEdge"+h,a=>a==="Z"?r("fNextEdge"+h,a):a==="E0"||a==="E1"?z("fRestore"+h+"0","K"+a[1]):a==="D"?z("fRestore"+h+"1",a):bad());
   for(let end of [0,1]){
    find("fRestore"+h+end,C,a=>r("fNextSource"+h+end,"T"+a.slice(1)));
    add("fNextSource"+h+end,a=>T(a)?end?bad():z("fRead"+h,"C"+a.slice(1)):a==="A"?end?z("fDone"+h,a):bad():data(a)?r("fNextSource"+h+end,a):bad());
   }
   find("fDone"+h,a=>a==="Q"+u,a=>r("fSkip","T"+h));
  }
 }
 add("fSkip",a=>a==="D"?r("forward",a):data(a)?r("fSkip",a):bad());
 // Final feasibility and selection: A is the boundary following the last vertex.
 find("lastBoundary",a=>a==="A",a=>l("lastStart",a));
 add("lastStart",a=>a==="L"?r("selectInitial",a):a==="S"?r("selectLast","B"):a==="__"?bad():l("lastStart",a));
 add("selectInitial",a=>a==="T11"?z("clean","W"):data(a)&&a!=="A"?r("selectInitial",a):bad());
 add("selectLast",a=>a==="T11"?z("backClear","Q1"):data(a)&&a!=="A"?r("selectLast",a):bad());
 // Move active boundary from end of selected vertex to its start.
 find("backClear",a=>a==="A",a=>z("backSet","S"));
 find("backSet",a=>a==="B",a=>z("backChosen","A"));
 find("backChosen",a=>a==="Q1",a=>r("backFirst","W"));
 add("backFirst",a=>a==="Z"?r("backFirst",a):a==="E0"||a==="E1"||a==="P"?z("backSource",a==="P"?"K2":"K"+a[1]):bad());
 find("backSource",a=>a==="A",a=>l("backStart",a));
 add("backStart",a=>a==="S"||a==="L"?r("backSrcFirst",a):a==="__"?bad():l("backStart",a));
 add("backSrcFirst",a=>T(a)?z("backEdge","C"+a.slice(1)):data(a)&&a!=="A"?r("backSrcFirst",a):bad());
 find("backEdge",K,a=>a==="K2"?z("backPick","P"):r("backNextEdge","E"+a[1]));
 add("backNextEdge",a=>a==="Z"?r("backNextEdge",a):a==="E0"||a==="E1"||a==="P"?z("backRestore",a==="P"?"K2":"K"+a[1]):bad());
 find("backRestore",C,a=>r("backNextSource","T"+a.slice(1)));
 add("backNextSource",a=>T(a)?z("backEdge","C"+a.slice(1)):data(a)&&a!=="A"?r("backNextSource",a):bad());
 find("backPick",a=>a==="C11",a=>z("backPrev","Q1"));
 find("backPrev",a=>a==="A",a=>l("backPrevStart","S"));
 add("backPrevStart",a=>a==="S"?z("backChosen","A"):a==="L"?r("backFinish",a):a==="__"?bad():l("backPrevStart",a));
 add("backFinish",a=>a==="Q1"?z("clean","W"):data(a)?r("backFinish",a):bad());
 add("clean",a=>a==="L"?r("readyAt","__"):a==="__"?bad():l("clean",a));
 add("readyAt",a=>data(a)?z("ready",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection,rules};
}
function encode(U,E){
 const b=v=>"0"+v;return U[0].map(b).join("")+"11"+E.map((e,i)=>U[i+1].map((u,c)=>b(u)+e.map(row=>b(row[c])).join("")+"10").join("")+"11").join("");
}
function logical(J,raw,limit=2000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a);trace.push([state,head,a]);if(trace.length>12)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;state=s;t++;}
 return {state,head,t,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}
