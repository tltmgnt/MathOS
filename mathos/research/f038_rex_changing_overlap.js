// REX-017: Boolean nested triple bags with changing ordered pair overlap.
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
 const symbols=["__","0_","1_","L","R","Z","X","C","Y","G","T00","T10","T11"];
 for(let k=0;k<4;k++)for(let p of ["A","H","F"])symbols.push(p+k);
 for(let j=0;j<8;j++)symbols.push("V"+j);
 for(let t of ["00","10","11"])for(let b of [0,1])symbols.push("O"+t+b);
 const projection=Object.fromEntries(symbols.filter(a=>a!=="__").map(a=>[a,a[0]==="O"?a.at(-1):"_"]));
 const defs=new Map(),reg=(s,fn)=>{if(!defs.has(s))defs.set(s,fn);return s;};
 const r=(s,a)=>[s,a,1],l=(s,a)=>[s,a,-1],z=(s,a)=>[s,a,0],bad=()=>z("reject","__"),raw=a=>a==="0_"||a==="1_",T=a=>/^T(00|10|11)$/.test(a),A=a=>/^A[0-3]$/.test(a),H=a=>/^H[0-3]$/.test(a),F=a=>/^F[0-3]$/.test(a),V=a=>/^V[0-7]$/.test(a),data=a=>!["__","L","R"].includes(a);
 const digits=j=>[(j>>2)&1,(j>>1)&1,j&1],pair=(k,j)=>{let d=digits(j),[x,y]=[[0,1],[0,2],[1,2]][k];return 2*d[x]+d[y];};
 function walk(s,d,act){return reg(s,a=>act(a)??(data(a)?(d===1?r(s,a):l(s,a)):bad()));}
 // root and child open headers: tag is physically kept until the two code bits
 // have been read; rewind to tag via temporary H3 (unique during parsing).
 reg("init",a=>a==="1_"?l("left",a):bad());
 reg("left",a=>a==="__"?r("rootOpen","L"):bad());
 reg("rootOpen",a=>a==="1_"?r("rootTag","Z"):bad());
 reg("rootTag",a=>a==="0_"?r(codeZ(1,""),"H3"):bad());
 reg("token",a=>a==="1_"?r("tag","Z"):bad());
 reg("tag",a=>a==="0_"?r(codeZ(0,""),"H3"):a==="1_"?l("closeSeek","X"):bad());
 function codeZ(root,bits){return reg("codeZ"+root+bits,a=>a==="0_"?r(codeBit(root,bits),"Z"):bad());}
 function codeBit(root,bits){return reg("codeBit"+root+bits,a=>{
  if(!raw(a))return bad();let b=bits+a[0];if(b.length===1)return r(codeZ(root,b),a);
  let k=parseInt(b,2);return (root?k===3:k<3)?l(mark(k),a):bad();
 });}
 function mark(k){return walk("mark"+k,-1,a=>a==="H3"?r(headerSkip(k,4),"A"+k):null);}
 function headerSkip(k,n){return reg("headerSkip"+k+"x"+n,a=>a==="Z"||raw(a)?r(n===1?maskZ(0):headerSkip(k,n-1),a):bad());}
 function maskZ(j){return reg("maskZ"+j,a=>a==="0_"?r(maskBit(j),"Z"):bad());}
 function maskBit(j){return reg("maskBit"+j,a=>raw(a)?r(j===7?"token":maskZ(j+1),"T"+a[0]+a[0]):bad());}
 walk("closeSeek",-1,a=>A(a)?z(a==="A3"?"rootFinish":start(+a[1],0),"H"+a[1]):null);
 // For each parent triple j, project its retained pair into child ranks
 // 2*pair and 2*pair+1. Read both feasibility entries, then AND into
 // exactly the parent's j-th entry. No host tables or overlap pointers.
 function start(k,j){return reg("start"+k+"x"+j,a=>a==="H"+k?r(readChild(k,j,2*pair(k,j)),a):bad());}
 function readChild(k,j,n){return walk("readChild"+k+"x"+j+"x"+n,1,a=>T(a)?n?r(readChild(k,j,n-1),a):r(readSecond(k,j,+a[2]),a):null);}
 function readSecond(k,j,h){return reg("readSecond"+k+"x"+j+"x"+h,a=>a==="Z"?r("readSecond"+k+"x"+j+"x"+h,a):T(a)?l(toH(k,j,h||+a[2]),a):bad());}
 function toH(k,j,h){return walk("toH"+k+"x"+j+"x"+h,-1,a=>a==="H"+k?l(toParent(k,j,h),a):null);}
 function toParent(k,j,h){return walk("toParent"+k+"x"+j+"x"+h,-1,a=>A(a)?r(update(k,j,h,j),a):null);}
 function update(k,j,h,n){return walk("update"+k+"x"+j+"x"+h+"x"+n,1,a=>T(a)?n?r(update(k,j,h,n-1),a):r(returnH(k,j),"T"+a[1]+(+a[2]&h)):null);}
 function returnH(k,j){return walk("returnH"+k+"x"+j,1,a=>a==="H"+k?(j===7?r("resume","F"+k):z(start(k,j+1),a)):null);}
 walk("resume",1,a=>a==="X"?r("token","C"):null);
 reg("rootFinish",a=>a==="H3"?r("rootClose","F3"):bad());
 walk("rootClose",1,a=>a==="X"?r("endCheck","C"):null);
 reg("endCheck",a=>a==="__"?l("rootRewind","R"):bad());
 walk("rootRewind",-1,a=>a==="L"?null:null);
 defs.set("rootRewind",a=>a==="L"?r("rootStart",a):data(a)||a==="R"?l("rootRewind",a):bad());
 walk("rootStart",1,a=>a==="F3"?r(rootPick(0),"H3"):null);
 function rootPick(j){return walk("rootPick"+j,1,a=>T(a)?a==="T11"?l(select(3,j),a):j===7?bad():r(rootPick(j+1),a):null);}
 function select(k,j){return walk("select"+k+"x"+j,-1,a=>a==="H"+k?r(emit(k,j,0),"V"+j):null);}
 function emit(k,j,i){return walk("emit"+k+"x"+j+"x"+i,1,a=>T(a)?r(i===(k===3?2:0)?"backScan":emit(k,j,i+1),"O"+a.slice(1)+digits(j)[k===3?i:2]):null);}
 reg("backScan",a=>F(a)?(a==="F3"?bad():l(parentChoice(+a[1]),"H"+a[1])):a==="C"?l("pop","Y"):a==="R"?l("clean",a):data(a)?r("backScan",a):bad());
 function parentChoice(k){return walk("parentChoice"+k,-1,a=>V(a)?r(childStart(k,2*pair(k,+a[1])),a):null);}
 function childStart(k,j){return walk("childStart"+k+"x"+j,1,a=>a==="H"+k?r(childPick(k,j,j),a):null);}
 function childPick(k,j,n){return walk("childPick"+k+"x"+j+"x"+n,1,a=>T(a)?n?r(childPick(k,j,n-1),a):a==="T11"?l(select(k,j),a):r(childSecond(k,j+1),a):null);}
 function childSecond(k,j){return reg("childSecond"+k+"x"+j,a=>a==="Z"?r("childSecond"+k+"x"+j,a):a==="T11"?l(select(k,j),a):bad());}
 walk("pop",-1,a=>V(a)?r("popResume","G"):null);
 walk("popResume",1,a=>a==="Y"?r("backScan","C"):null);
 reg("clean",a=>a==="L"?r("readyAt","__"):data(a)?l("clean",a):bad());
 reg("readyAt",a=>a==="Z"?z("ready",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols){let [t,w,d]=fn(a);if(t!=="reject"||a==="__"||T(a))rules.push([s,a,t,w,d]);}
 return {symbols,projection,rules};
}
function encode(t){let b=x=>"0"+x;return "10"+b(t.k>>1)+b(t.k&1)+t.m.map(b).join("")+t.children.map(encode).join("")+"11";}
function logical(J,raw,limit=2000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a)??["reject","__",0];trace.push([state,head,a]);if(trace.length>10)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}
