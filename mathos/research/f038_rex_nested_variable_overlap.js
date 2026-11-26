// REX-020: nested sparse introduction trees, child-pivot bounded-sweep refinement.
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
 const symbols=["__","0_","1_","L","R","Z","O","D","J","X","C","Y","P","Q","K","S","W","V","G","B4","T00","T10","T11"];
 for(let k=0;k<4;k++)for(let a of ["A","B","H","F"])symbols.push(a+k);
 for(let k=0;k<3;k++)for(let b=0;b<2;b++)symbols.push("d"+k+b,"u"+k+b);
 const projection=Object.fromEntries(symbols.filter(a=>a!=="__").map(a=>[a,a==="P"?"0":a==="W"?"1":"_"]));
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error(s);defs.set(s,fn)};
 const r=(s,a)=>[s,a,1],l=(s,a)=>[s,a,-1],z=(s,a)=>[s,a,0],bad=()=>z("reject","__"),raw=a=>a==="0_"||a==="1_",data=a=>!["__","L","R"].includes(a),T=a=>/^T(00|10|11)$/.test(a),A=a=>/^A[0-3]$/.test(a),B=a=>/^B[0-4]$/.test(a),H=a=>/^H[0-3]$/.test(a),F=a=>/^F[0-3]$/.test(a),used=a=>/^u[0-2][01]$/.test(a);
 const restore=a=>used(a)?"d"+a.slice(1):a;
 function find(s,p,act){add(s,a=>a==="L"?r(s+"Scan",a):a==="__"?bad():l(s,a));add(s+"Scan",a=>p(a)?act(a):data(a)?r(s+"Scan",a):bad());}
 function walk(s,d,act){add(s,a=>act(a)??(data(a)?(d===1?r(s,a):l(s,a)):bad()));}
 add("init",a=>raw(a)?l("left",a):bad());add("left",a=>a==="__"?r("parseRoot","L"):bad());
 let parse={Root:{"111":["O","rootCode"]},Rows:{"011":["P","First0"],"110":["D","Children"]},Children:{"111":["O","childCode"],"010":["X","closeSeek"]}};
 for(let j=0;j<3;j++){parse["First"+j]={"000":["d"+j+"0","Bits"+j],"001":["d"+j+"1","Bits"+j]};parse["Bits"+j]={...parse["First"+j],"010":["J",j===2?"Mask":"First"+(j+1)]};}
 parse.Mask={"100":["T00","Rows"],"101":["T11","Rows"]};
 for(let [name,table] of Object.entries(parse))for(let n=0;n<3;n++)for(let i=0;i<2**n;i++){
  let b=n?i.toString(2).padStart(n,"0"):"";
  add("parse"+name+b,a=>{if(!raw(a))return bad();let v=b+a[0];if(n<2)return r("parse"+name+v,"Z");let t=table[v];return t?t[1]==="closeSeek"?l("closeSeek","X"):r(["rootCode","childCode"].includes(t[1])?t[1]:"parse"+t[1],t[0]):bad();});
 }
 for(let m of ["root","child"]){
  add(m+"Code",a=>raw(a)?r(m+"Code"+a[0],a):bad());
  for(let b of [0,1])add(m+"Code"+b,a=>{if(!raw(a))return bad();let k=2*b+ +a[0];return (m==="root"?k===3:k<3)?l("mark"+k,a):bad();});
 }
 for(let k=0;k<4;k++)walk("mark"+k,-1,a=>a==="O"?r("skipCode1","A"+k):null);
 add("skipCode1",a=>raw(a)?r("skipCode2",a):bad());add("skipCode2",a=>raw(a)?r("parseRows",a):bad());
 walk("closeSeek",-1,a=>A(a)?a==="A3"?r("rootClose","F3"):l("fParent"+a[1],"H"+a[1]):null);
 walk("rootClose",1,a=>a==="X"?r("endCheck","C"):null);
 add("endCheck",a=>a==="__"?l("rootRewind","R"):bad());
 add("rootRewind",a=>a==="L"?r("rootStart",a):data(a)?l("rootRewind",a):bad());
 walk("rootStart",1,a=>a==="F3"?r("rootRow","H3"):null);
 walk("rootRow",1,a=>a==="P"?r("rootMask","Q"):a==="D"?bad():null);
 walk("rootMask",1,a=>T(a)?z(a==="T11"?"rootPick":"rootDrop",a):null);
 find("rootDrop",a=>a==="Q",a=>r("rootSkip","P"));
 walk("rootSkip",1,a=>T(a)?r("rootRow",a):null);
 find("rootPick",a=>a==="Q",a=>z("rootOpen","W"));
 find("rootOpen",a=>a==="H3",a=>r("backTable","V"));
 walk("backTable",1,a=>a==="D"?r("backScan",a):null);
 walk("backScan",1,a=>F(a)?a==="F3"?bad():l("bParent"+a[1],"H"+a[1]):a==="C"?l("pop","Y"):a==="R"?l("clean",a):null);
 walk("pop",-1,a=>a==="V"?r("popResume","G"):null);
 walk("popResume",1,a=>a==="Y"?r("backScan","C"):null);
 const pairs=[[0,1],[0,2],[1,2]];
 for(let m of ["f","b"])for(let k=0;k<3;k++){
  let h=m+k;
  walk(m+"Parent"+k,-1,a=>m==="f"&&A(a)?z(h+"Child","B"+a[1]):m==="b"&&a==="V"?z(h+"Child","B4"):null);
  find(h+"Child",H,a=>r(h+"Row",a));
  walk(h+"Row",1,a=>a==="P"?r(h+"Mask","Q"):a==="D"?z(m==="f"?"finalize":"badBack",a):null);
  walk(h+"Mask",1,a=>T(a)?z(a==="T11"?h+"Activate":h+"SkipPivot",a):null);
  find(h+"Activate",B,a=>r(h+"ActivateRows",a));
  walk(h+"ActivateRows",1,a=>a==="D"?z(h+"Digit0",a):m==="f"&&a==="P"||m==="b"&&a==="W"?r(h+"ActivateRows","K"):null);
  for(let field=0;field<2;field++){
   let g=h+"d"+field, p=pairs[k][field];
   find(h+"Digit"+field,a=>a==="Q",a=>r(g+"Pivot",a));
   walk(g+"Pivot",1,a=>a==="d"+field+"0"||a==="d"+field+"1"?z(g+"Send"+a[2],"u"+a.slice(1)):T(a)?z(g+"Send2",a):null);
   for(let b=0;b<3;b++){
    let q=g+"x"+b;
    find(g+"Send"+b,B,a=>r(q+"Rows",a));
    walk(q+"Rows",1,a=>a==="K"?r(q+"Compare",a):["P","S","W"].includes(a)?r(q+"Skip",a):a==="D"?z(b===2?(field===0?h+"Digit1":h+"Collect"):h+"Digit"+field,a):null);
    walk(q+"Compare",1,a=>a==="d"+p+"0"||a==="d"+p+"1"?b!==2&&+a[2]===b?r(q+"Skip","u"+a.slice(1)):l(q+"Drop",a):T(a)?b===2?r(q+"Rows",a):l(q+"Drop",a):null);
    walk(q+"Drop",-1,a=>a==="K"?r(q+"Skip",m==="f"?"P":"S"):null);
    walk(q+"Skip",1,a=>T(a)?r(q+"Rows",a):null);
   }
  }
  find(h+"Collect",B,a=>r(h+"Collect0",a));
  for(let hit=0;hit<2;hit++){
   walk(h+"Collect"+hit,1,a=>a==="K"?r(h+"Collect1",m==="f"?"S":"W"):m==="b"&&a==="S"?r(h+"Collect"+hit,"W"):used(a)?r(h+"Collect"+hit,restore(a)):a==="D"?z(h+"Restore"+hit,a):null);
   find(h+"Restore"+hit,a=>a==="Q",a=>r(h+"RestoreFields"+hit,a));
   walk(h+"RestoreFields"+hit,1,a=>used(a)?r(h+"RestoreFields"+hit,restore(a)):T(a)?z(m==="b"&&hit?"bChoose":h+"SkipPivot",a):null);
  }
  find(h+"SkipPivot",a=>a==="Q",a=>r(h+"SkipRow","P"));
  walk(h+"SkipRow",1,a=>T(a)?r(h+"Row",a):null);
 }
 add("badBack",a=>bad());
 find("finalize",B,a=>r("finalRows",a));
 walk("finalRows",1,a=>a==="P"?r("finalMask0",a):a==="S"?r("finalMask1","P"):a==="D"?z("restoreFParent",a):null);
 for(let hit=0;hit<2;hit++)walk("finalMask"+hit,1,a=>T(a)?r("finalRows","T"+a[1]+(+a[2]&hit)):null);
 find("restoreFParent",B,a=>a==="B4"?bad():z("restoreFChild","A"+a[1]));
 find("restoreFChild",H,a=>r("resume","F"+a[1]));
 walk("resume",1,a=>a==="X"?r("parseChildren","C"):null);
 find("bChoose",a=>a==="Q",a=>z("restoreBParent","W"));
 find("restoreBParent",B,a=>z("restoreBChild","V"));
 find("restoreBChild",H,a=>r("backTable","V"));
 add("clean",a=>a==="L"?r("readyAt","__"):data(a)?l("clean",a):bad());
 add("readyAt",a=>a==="Z"?z("ready",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols){let [t,w,d]=fn(a);rules.push([s,a,t,w,d]);}
 return {symbols,projection,rules};
}
function encode(t){
 let row=([a,b,c,v])=>"011"+[a,b,c].map(s=>[...s].map(x=>"00"+x).join("")+"010").join("")+(v?"101":"100");
 return "111"+t.k.toString(2).padStart(2,"0")+t.rows.map(row).join("")+"110"+t.children.map(encode).join("")+"010";
}
function logical(J,raw,limit=10000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a);trace.push([state,head,a]);if(trace.length>12)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}
