// REX-018: physical variable-length pair-map alignment kernel; sparse explicit rank rows.
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
 const symbols=["__","0_","1_","L","R","Z","J","D","P","Q","H","K","M0","M1","N0","N1","O1","T00","T10","T11"];
 for(let x of ["A","B","C","E","X","UA","UB","UC","UE"])for(let b of [0,1])symbols.push(x+b);
 const projection=Object.fromEntries(symbols.filter(a=>a!=="__").map(a=>[a,/^T/.test(a)?a[2]:a==="O1"?"1":/^N/.test(a)?"0":"_"]));
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error(s);defs.set(s,fn)};
 const z=(s,a)=>[s,a,0],r=(s,a)=>[s,a,1],l=(s,a)=>[s,a,-1],bad=()=>z("reject","__"),raw=a=>a==="0_"||a==="1_",data=a=>!["__","L","R"].includes(a),pm=a=>/^M[01]$/.test(a)||/^T(00|10|11)$/.test(a),cm=a=>/^N[01]$/.test(a);
 function find(s,p,act){add(s,a=>a==="L"?r(s+"Scan",a):a==="__"?bad():l(s,a));add(s+"Scan",a=>p(a)?act(a):data(a)?r(s+"Scan",a):bad());}
 function scan(s,act){add(s,a=>act(a)??(data(a)?r(s,a):bad()));}
 add("init",a=>raw(a)?l("left",a):bad());add("left",a=>a==="__"?r("code1","L"):bad());
 add("code1",a=>raw(a)?r("code2"+a[0],a):bad());
 for(let b of [0,1])add("code2"+b,a=>raw(a)&&b+a[0]!=="11"?r("parse"+parseInt(b+a[0],2)+"pRow",a):bad());
 const pairs=[[0,1],[0,2],[1,2]];
 // Token 000/001 bit, 010 field end, 011 row start,
 // 100/101 local flag 0/1, 110 table separator. Empty tables legal.
 for(let k=0;k<3;k++)for(let side of ["p","c"]){
  let table={Row:{"011":[side==="p"?"P":"H","First0"]}};
  if(side==="p")table.Row["110"]=["D","child"];
  for(let j=0;j<3;j++){
   let tag=side==="p"?(j===pairs[k][0]?"A":j===pairs[k][1]?"B":"X"):["C","E","X"][j];
   table["First"+j]={"000":[tag+"0","Bits"+j],"001":[tag+"1","Bits"+j]};
   table["Bits"+j]={"000":[tag+"0","Bits"+j],"001":[tag+"1","Bits"+j],"010":["J",j===2?"Mask":"First"+(j+1)]};
  }
  table.Mask={"100":[side==="p"?"M0":"N0","Row"],"101":[side==="p"?"M1":"N1","Row"]};
  for(let [name,t] of Object.entries(table))for(let n=0;n<3;n++)for(let i=0;i<2**n;i++){
   let b=n?i.toString(2).padStart(n,"0"):"",s="parse"+k+side+name+b;
   add(s,a=>{
    if(side==="c"&&name==="Row"&&n===0&&a==="__")return l("begin","R");
    if(!raw(a))return bad();let v=b+a[0];if(n<2)return r("parse"+k+side+name+v,"Z");
    let q=t[v];return q?r(q[1]==="child"?"parse"+k+"cRow":"parse"+k+side+q[1],q[0]):bad();
   });
  }
 }
 find("begin",a=>a==="P"||a==="D",a=>a==="P"?r("fParentMask","Q"):z("selectParent",a));
 scan("fParentMask",a=>a==="M0"?z("finishParent0","T00"):a==="M1"?z("fChildStart",a):null);
 // Scan child table from its start for every positive parent row.
 for(let m of ["f","b"]){
  find(m+"ChildStart",a=>a==="D",a=>r(m+"ChildNext",a));
  add(m+"ChildNext",a=>a==="H"?r(m+"ChildMask","K"):a==="R"?m==="f"?z("finishNo",a):bad():data(a)?r(m+"ChildNext",a):bad());
  scan(m+"ChildMask",a=>a==="N0"?z(m+"restoreNext",a):a==="N1"?z(m+"AParent",a):null);
  for(let [p,c] of [["A","C"],["B","E"]]){
   find(m+p+"Parent",a=>a==="Q",a=>r(m+p+"Pscan",a));
   scan(m+p+"Pscan",a=>/^M[01]$/.test(a)||/^T/.test(a)?z(m+p+"Child2",a):a===p+"0"||a===p+"1"?z(m+p+"Child"+a[1],"U"+a):null);
   for(let b of [0,1,2]){
    find(m+p+"Child"+b,a=>a==="K",a=>r(m+p+"Cscan"+b,a));
    scan(m+p+"Cscan"+b,a=>{
     if(cm(a))return z(b===2?(p==="A"?m+"BParent":m+"restoreYes"):m+"restoreNext",a);
     if(a===c+"0"||a===c+"1")return z(b!==2&&a[1]===String(b)?m+p+"Parent":m+"restoreNext","U"+a);
     return null;
    });
   }
  }
  for(let yes of [0,1]){
   let tag=yes?"Yes":"Next";
   find(m+"restore"+tag,a=>a==="Q",a=>r(m+"rp"+tag,a));
   scan(m+"rp"+tag,a=>pm(a)?z(m+"rc"+tag,a):/^U[AB][01]$/.test(a)?r(m+"rp"+tag,a.slice(1)):null);
   find(m+"rc"+tag,a=>a==="K",a=>r(m+"rscan"+tag,"H"));
   scan(m+"rscan"+tag,a=>{
    if(/^U[CE][01]$/.test(a))return r(m+"rscan"+tag,a.slice(1));
    if(cm(a))return yes?m==="f"?z("finishYes",a):z("bFinish","O1"):r(m+"ChildNext",a);
    return null;
   });
  }
 }
 for(let yes of [0,1]){
  find(yes?"finishYes":"finishNo",a=>a==="Q",a=>r("finishMask"+yes,a));
  scan("finishMask"+yes,a=>a==="M1"?z("finishParent0","T1"+yes):null);
 }
 find("finishParent0",a=>a==="Q",a=>r("parentDone","P"));
 scan("parentDone",a=>/^T/.test(a)?r("parentNext",a):null);
 scan("parentNext",a=>a==="P"?r("fParentMask","Q"):a==="D"?z("selectParent",a):null);
 // Find first feasible parent row; rescan child rows to select first support.
 add("selectParent",a=>a==="L"?r("selectScan",a):a==="__"?bad():l("selectParent",a));
 scan("selectScan",a=>a==="P"?r("selectMask","Q"):a==="D"?z("clean",a):null);
 scan("selectMask",a=>a==="T11"?z("bChildStart",a):/^T/.test(a)?z("selectRestore",a):null);
 find("selectRestore",a=>a==="Q",a=>r("selectSkip","P"));
 scan("selectSkip",a=>/^T/.test(a)?r("selectScan",a):null);
 find("bFinish",a=>a==="Q",a=>z("clean","P"));
 add("clean",a=>a==="L"?r("readyAt","__"):a==="__"?bad():l("clean",a));
 add("readyAt",a=>raw(a)?z("ready",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection,rules};
}
function encode(k,P,C){let row=([a,b,c,v])=>"011"+[a,b,c].map(s=>[...s].map(x=>"00"+x).join("")+"010").join("")+(v?"101":"100");return k.toString(2).padStart(2,"0")+P.map(row).join("")+"110"+C.map(row).join("");}
function logical(J,raw,limit=3000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a);trace.push([state,head,a]);if(trace.length>12)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}
