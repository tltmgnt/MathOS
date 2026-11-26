// REX-014: fixed Boolean sliding triple bags, pair separators, two factor masks per candidate.
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
 const symbols=["__","0_","1_","R"];
 const projection={"0_":"_","1_":"_"};
 for(let b of [0,1]){
  for(let v of [0,1]){symbols.push("I"+b+v);projection["I"+b+v]=String(v);}
  for(let p of [0,1,2]){
   symbols.push("H"+b+p);projection["H"+b+p]="_";
   if(p!==2)for(let c of [0,1]){symbols.push("O"+b+p+c);projection["O"+b+p+c]=String(c);}
  }
 }
 const defs=new Map(),reg=(s,fn)=>{if(!defs.has(s))defs.set(s,fn);return s;};
 const raw=a=>a==="0_"||a==="1_",hist=a=>/^H[01][012]$/.test(a),bad=()=>["reject","__",0],r=(s,a)=>[s,a,1],l=(s,a)=>[s,a,-1],z=(s,a)=>[s,a,0];
 function initial(bits){
  return reg(bits?"init"+bits:"init",a=>raw(a)?r(bits.length===3?boundary(bits+a[0]):initial(bits+a[0]),a):bad());
 }
 function boundary(mask){
  return reg("boundary"+mask,a=>a==="__"?l(choose(mask),"R"):raw(a)?first(mask,"",a):bad());
 }
 function canon(mask,j){return j>=2?"0"+mask[1]+"0"+mask[3]:mask;}
 function first(mask,out,a){return raw(a)?r(col(mask,out,1,a[0],0),a):bad();}
 function col(mask,out,phase,bit,hit){
  let j=out.length;mask=canon(mask,j);
  return reg("col"+mask+"x"+out+"x"+phase+bit+hit,a=>{
   if(!raw(a))return bad();
   let b=j>>1,v=+a[0];
   if(phase===1)return r(col(mask,out,2,0,+(mask[b]==="1"&&bit==="1"&&v)),a);
   if(phase===2)return r(col(mask,out,3,a[0],hit),a);
   let p=hit?0:mask[2+b]==="1"&&bit==="1"&&v?1:2;
   let next=out+ +(p!==2);
   return r(next.length===4?boundary(next):reg("first"+canon(mask,next.length)+"x"+next,a=>first(canon(mask,next.length),next,a)),"H"+a[0]+p);
  });
 }
 function choose(mask){
  return reg("choose"+mask,a=>{
   let j=[0,2,1,3].find(j=>mask[j]==="1");
   return j===undefined?bad():z(backAt(j),a);
  });
 }
 function backAt(j){
  return reg("backAt"+j,a=>hist(a)?z(scan(j,15),a):raw(a)?l(initialOut(j>>1),"I"+a[0]+(j&1)):bad());
 }
 function initialOut(a){
  return reg("initialOut"+a,s=>raw(s)?l("finish1","I"+s[0]+a):bad());
 }
 function scan(j,pos){
  return reg("scan"+j+"x"+pos,a=>{
   if(pos===4*j+3){
    if(!hist(a)||a[2]==="2")return bad();
    return l(skip(2*+a[2]+(j>>1),pos-1),"O"+a.slice(1)+(j&1));
   }
   return (pos%4===3?hist(a):raw(a))?l(scan(j,pos-1),a):bad();
  });
 }
 function skip(j,pos){
  return reg("skip"+j+"x"+pos,a=>(pos%4===3?hist(a):raw(a))?l(pos===0?backAt(j):skip(j,pos-1),a):bad());
 }
 reg("finish1",a=>raw(a)?l("finish0",a):bad());
 reg("finish0",a=>raw(a)?z("ready",a):bad());
 initial("");
 const rules=[];
 // Build only reachable finite-control states, with sparse symbol rules.
 for(let [s,fn] of defs)for(let a of symbols){
  let [t,w,d]=fn(a);
  if(t!=="reject"||a==="__"||raw(a))rules.push([s,a,t,w,d]);
 }
 return {symbols,projection,rules};
}
function encode(initial,stages){return initial.join("")+stages.map(s=>s.flat(2).join("")).join("");}
function oracle(initial,stages){
 let n=stages.length+2,a=Array(n).fill(0);
 function rec(i){
  if(i<0)return initial[2*a[0]+a[1]]&&stages.every((s,j)=>s[2*a[j+1]+a[j+2]][a[j]].every(Boolean))?a.join(""):null;
  for(let b=0;b<2;b++){a[i]=b;let w=rec(i-1);if(w!==null)return w;}return null;
 }
 return rec(n-1);
}
function logical(J,raw,limit=2000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a)??["reject","__",0];trace.push([state,head,a]);if(trace.length>12)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}
