// REX-012 fixed Boolean rooted ordered tree worker, persistent child-message conjunction and witness recovery.
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





function treeWorker(){
 const symbols=["__","0_","1_","L","R","Z","A","F","X","C","H","V0","V1","W0","W1","Y","T00","T10","T11","E0","E1"];
 const projection=Object.fromEntries(symbols.filter(x=>x!=="__").map(x=>[x,x==="W0"?"0":x==="W1"?"1":"_"]));
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error(s);defs.set(s,fn)};
 const go=(s,w,d=0)=>[s,w,d],r=(s,a)=>go(s,a,1),l=(s,a)=>go(s,a,-1),z=(s,a)=>go(s,a),bad=()=>z("reject","__"),raw=a=>a==="0_"||a==="1_",data=a=>a!=="__"&&a!=="L"&&a!=="R",T=a=>/^T(00|10|11)$/.test(a);
 add("init",a=>a==="1_"?l("left",a):bad());
 add("left",a=>a==="__"?r("token","L"):bad());
 add("token",a=>a==="1_"?r("tag","Z"):bad());
 add("tag",a=>a==="0_"?r("header0","A"):a==="1_"?l("closeSeek","X"):bad());
 for(let j=0;j<6;j++){
  add("header"+j,a=>a==="0_"?r("value"+j,"Z"):bad());
  add("value"+j,a=>raw(a)?r(j===5?"token":"header"+(j+1),j<2?"T"+a[0]+a[0]:"E"+a[0]):bad());
 }
 add("closeSeek",a=>a==="A"?r("readf0","A"):data(a)?l("closeSeek",a):bad());
 // Read final feasibility and original edge in fixed finite control.
 // Only six bits are held, independently of tree size.
 for(let mode of ["f","b0","b1","root"]){
  for(let j=0;j<6;j++)for(let x=0;x<2**j;x++){
   let bits=j?x.toString(2).padStart(j,"0"):"",name=mode+j+bits;
   add("read"+name,a=>a==="Z"?r("digit"+name,a):bad());
   add("digit"+name,a=>{
    if(j<2?!T(a):!/^E[01]$/.test(a))return bad();
    let b=a.at(-1),next=bits+b;
    if(j<5)return r("read"+mode+(j+1)+next,a);
    let m=next.slice(0,2).split("").map(Number),e=next.slice(2).split("").map(Number);
    if(mode==="f"){
     let p=[0,1].map(k=>+(m[0]&&e[k]||m[1]&&e[2+k]));
     return l("finish"+p.join(""),a);
    }
    let pick=mode==="root"?m.findIndex(Boolean):m.findIndex((v,k)=>v&&e[2*k+Number(mode[1])]);
    return pick<0?bad():l("choose"+pick,a);
   });
  }
 }
 for(let p of ["00","01","10","11"]){
  add("finish"+p,a=>a==="A"?l("parent"+p,"F"):data(a)?l("finish"+p,a):bad());
  add("parent"+p,a=>a==="A"?r("upFirst"+p,a):a==="L"?r("rootEnd",a):data(a)?l("parent"+p,a):bad());
  add("upFirst"+p,a=>a==="Z"?r("upValue"+p,a):bad());
  add("upValue"+p,a=>T(a)?r("upSecond"+p,"T"+a[1]+(+a[2]&+p[0])):bad());
  add("upSecond"+p,a=>a==="Z"?r("upValue2"+p,a):bad());
  add("upValue2"+p,a=>T(a)?r("resume","T"+a[1]+(+a[2]&+p[1])):bad());
 }
 add("resume",a=>a==="X"?r("token","C"):data(a)?r("resume",a):bad());
 add("rootEnd",a=>a==="X"?r("endCheck","C"):data(a)?r("rootEnd",a):bad());
 add("endCheck",a=>a==="__"?l("rootRewind","R"):bad());
 add("rootRewind",a=>a==="L"?r("rootOpen",a):data(a)?l("rootRewind",a):bad());
 add("rootOpen",a=>a==="Z"?r("rootTag",a):bad());
 add("rootTag",a=>a==="F"?r("readroot0","H"):bad());
 for(let b of [0,1]){
  add("choose"+b,a=>a==="H"?r("backScan","V"+b):data(a)?l("choose"+b,a):bad());
  add("seekChild"+b,a=>a==="H"?r("readb"+b+"0",a):data(a)?r("seekChild"+b,a):bad());
 }
 add("backScan",a=>a==="F"?l("seekChosenParent","H"):a==="C"?l("pop","Y"):a==="R"?l("cleanup",a):data(a)?r("backScan",a):bad());
 add("seekChosenParent",a=>a==="V0"||a==="V1"?r("seekChild"+a[1],a):data(a)?l("seekChosenParent",a):bad());
 add("pop",a=>a==="V0"||a==="V1"?r("popResume","W"+a[1]):data(a)?l("pop",a):bad());
 add("popResume",a=>a==="Y"?r("backScan","C"):data(a)?r("popResume",a):bad());
 add("cleanup",a=>a==="L"?r("readyAt","__"):data(a)&&!/^V|^H$/.test(a)?l("cleanup",a):bad());
 add("readyAt",a=>a==="Z"?z("ready",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection,rules};
}
function encode(t){return "10"+[...t.u,...t.e].map(b=>"0"+b).join("")+t.children.map(encode).join("")+"11";}
function logical(J,raw,limit=2000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a);trace.push([state,head,a]);if(trace.length>12)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}
