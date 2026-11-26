// REX-016: common pair separator with independent private children.
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
 const symbols=["__","0_","1_","L","R","Z","IG","BI","G","U","J","A","D","H","B","X","V","KV","P","P0","P1","Q","Q0","Q1","T00","T10","T11","W","QT00","QT10","QT11","QW","U0","U1","UW","CU0","CU1","CUW","F0","F1","E0","E1","EP","K0","K1","I","Y","C0","C1"];
 const projection=Object.fromEntries(symbols.filter(a=>a!=="__").map(a=>[a,["W","UW"].includes(a)?"1":/^T|^U[01]$/.test(a)?"0":"_"]));
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error("duplicate "+s);defs.set(s,fn)};
 const z=(s,a)=>[s,a,0],r=(s,a)=>[s,a,1],l=(s,a)=>[s,a,-1],bad=()=>z("reject","__"),raw=a=>a==="0_"||a==="1_",data=a=>!["__","L","R"].includes(a);
 const T=a=>/^T(00|10|11)$/.test(a),QT=a=>/^QT(00|10|11)$/.test(a)||a==="QW",U=a=>/^U[01W]$/.test(a),CU=a=>/^CU[01W]$/.test(a),F=a=>/^F[01]$/.test(a),E=a=>/^E[01P]$/.test(a);
 const qtag=a=>a==="W"?"QW":"Q"+a,qrestore=a=>a==="QW"?"W":a.slice(1),ctag=a=>"C"+a,crest=a=>a.slice(1);
 function find(s,p,act){add(s,a=>a==="L"?r(s+"Scan",a):a==="__"?bad():l(s,a));add(s+"Scan",a=>p(a)?act(a):data(a)?r(s+"Scan",a):bad());}
 function next(s,act){add(s,a=>a==="Z"?r(s,a):act(a));}
 function walk(s,d,act){add(s,a=>act(a)??(data(a)?(d===1?r(s,a):l(s,a)):bad()));}
 add("init",a=>raw(a)?l("left",a):bad());add("left",a=>a==="__"?r("parseRoot","L"):bad());
 const parse={
  Root:{"010":["IG","RootFirst"]},RootFirst:{"000":["T00","RootVals"],"001":["T11","RootVals"]},
  RootVals:{"000":["T00","RootVals"],"001":["T11","RootVals"],"101":["J","RootAfter"]},
  RootAfter:{"010":["IG","RootFirst"],"110":["A","Child"]},
  Child:{"000":["U0","Private"],"001":["U1","Private"]},
  Private:{"000":["U0","Private"],"001":["U1","Private"],"111":["H","Groups"]},
  Groups:{"010":["G","PairFirst"]},PairFirst:{"011":["P","FirstF"]},
  FirstF:{"000":["F0","Second"],"001":["F1","Second"]},Second:{"000":["E0","AfterE"],"001":["E1","AfterE"]},
  AfterE:{"000":["F0","Second"],"001":["F1","Second"],"100":["V","AfterPair"]},
  AfterPair:{"011":["P","FirstF"],"101":["J","AfterGroup"]},
  AfterGroup:{"010":["G","PairFirst"],"110":["D","Child"]}
 };
 for(let [name,table] of Object.entries(parse))for(let k=0;k<3;k++)for(let i=0;i<2**k;i++){
  let b=k?i.toString(2).padStart(k,"0"):"";
  add("parse"+name+b,a=>{
   if(k===0&&name==="Child"&&a==="__")return l("ivStart","R");
   if(!raw(a))return bad();let v=b+a[0];if(k<2)return r("parse"+name+v,"Z");
   let t=table[v];return t?r("parse"+t[1],t[0]):bad();
  });
 }
 // Compare adjacent root row lengths, retaining all bits.
 find("ivStart",a=>a==="IG",a=>r("ivFirst","BI"));
 next("ivFirst",a=>T(a)?z("ivRight","Q"+a):bad());
 find("ivRight",a=>a==="BI",a=>r("ivSeekEnd",a));
 walk("ivSeekEnd",1,a=>a==="J"?r("ivRightStart",a):null);
 next("ivRightStart",a=>a==="A"?z("ivLast",a):a==="IG"?r("ivRightFirst","U"):bad());
 next("ivRightFirst",a=>T(a)?z("ivLeftRestore","C"+a[2]):bad());
 find("ivLeftRestore",QT,a=>r("ivLeftNext",qrestore(a)));
 next("ivLeftNext",a=>T(a)?z("ivRightRestore0","Q"+a):a==="J"?z("ivRightRestore1",a):bad());
 for(let end of [0,1]){
  find("ivRightRestore"+end,a=>/^C[01]$/.test(a),a=>r("ivRightNext"+end,"T"+a[1]+a[1]));
  next("ivRightNext"+end,a=>T(a)?end?bad():z("ivLeftRestore","C"+a[2]):a==="J"?end?z("ivAdvance",a):bad():bad());
 }
 find("ivAdvance",a=>a==="BI",a=>z("ivNew","IG"));
 find("ivNew",a=>a==="U",a=>r("ivFirst","BI"));
 find("ivLast",QT,a=>z("ivLastGroup",qrestore(a)));
 find("ivLastGroup",a=>a==="BI",a=>z("fBegin","IG"));
 // Forward and backward both scan children in original order. The root pair
 // grid is not shifted. Private cursor is tied to the active header B.
 for(let mode of ["f","b"]){
  const rt=a=>T(a)||mode==="b"&&a==="W",pv=a=>/^U[01]$/.test(a)||mode==="b"&&a==="UW",pair=a=>mode==="f"?a==="P":/^P[01]$/.test(a);
  find(mode+"Begin",a=>a==="A",a=>r(mode+"Child",a));
  next(mode+"Child",a=>pv(a)?r(mode+"Header",a):a==="R"?z(mode==="f"?"selectRoot":"clean",a):bad());
  walk(mode+"Header",1,a=>a==="H"?r(mode+"DestGroup","B"):null);
  next(mode+"DestGroup",a=>a==="G"?r(mode+"DestPair","U"):bad());
  next(mode+"DestPair",a=>pair(a)?z(mode+"RootFirst",mode==="f"?"Q":"Q"+a[1]):bad());
  find(mode+"RootFirst",a=>a==="IG",a=>r(mode+"RootVal","BI"));
  next(mode+"RootVal",a=>rt(a)?z(mode+"PrivateFirst",qtag(a)):bad());
  find(mode+"PrivateFirst",a=>a==="B",a=>l(mode+"PrivateStart",a));
  walk(mode+"PrivateStart",-1,a=>a==="A"||a==="D"?r(mode+"PrivateVal",a):null);
  next(mode+"PrivateVal",a=>pv(a)?z(mode+"CandidateFirst",ctag(a)):bad());
  find(mode+"CandidateFirst",a=>mode==="f"?a==="Q":/^Q[01]$/.test(a),a=>r(mode+"FirstF",a));
  next(mode+"FirstF",a=>F(a)?z(mode+"Read0","K"+a[1]):bad());
  for(let hit of [0,1]){
   find(mode+"Read"+hit,CU,a=>z(mode+"ReadF"+hit+(a==="CU0"?0:1),a));
   for(let u of [0,1]){
    find(mode+"ReadF"+hit+u,a=>/^K[01]$/.test(a),a=>r(mode+"ReadE"+hit+u+a[1],"F"+a[1]));
    for(let f of [0,1]){
     next(mode+"ReadE"+hit+u+f,a=>{
      if(!E(a))return bad();
      if(mode==="f"){let yes=!hit&&u&&f&&a==="E1";return r("fNextF"+ +(hit||yes),yes?"EP":a);}
      return a==="EP"?z("bCheck"+hit,"I"):r("bNextF"+hit,a);
     });
    }
   }
   if(mode==="b"){
    find("bCheck"+hit,QT,a=>z(a==="QW"?"bMark"+hit:"bResume"+hit,a));
    find("bMark"+hit,CU,a=>a==="CU1"?z("bResume1","CUW"):bad());
    find("bResume"+hit,a=>a==="I",a=>r("bNextF"+hit,"EP"));
   }
   next(mode+"NextF"+hit,a=>F(a)?z(mode+"Restore"+hit+"0","K"+a[1]):a==="V"?z(mode+"Restore"+hit+"1","KV"):bad());
   for(let end of [0,1]){
    find(mode+"Restore"+hit+end,CU,a=>r(mode+"PrivNext"+hit+end,crest(a)));
    next(mode+"PrivNext"+hit+end,a=>pv(a)?end?bad():z(mode+"Read"+hit,ctag(a)):a==="B"?end?z(mode+"Update"+hit,a):bad():bad());
   }
   find(mode+"Update"+hit,QT,a=>{
    if(mode==="b")return a==="QW"&&!hit?bad():r(mode+"RootNextZ",qrestore(a));
    return a==="QW"?bad():r("fRootNextZ","T"+a[2]+(+a[3]&hit));
   });
   // Update pair-local feasibility marker, preserving prior feasibility in backward mode.
   // root next state must carry the hit to update Q; use separate state families below.
  }
  // Replace Update rules to remember hit until pair tag restored.
  for(let hit of [0,1]){
   defs.set(mode+"Update"+hit+"Scan",a=>QT(a)?(mode==="b"?(a==="QW"&&!hit?bad():r("bRootNext"+hit,qrestore(a))):a==="QW"?bad():r("fRootNext"+hit,"T"+a[2]+(+a[3]&hit))):data(a)?r(mode+"Update"+hit+"Scan",a):bad());
   next(mode+"RootNext"+hit,a=>rt(a)?z(mode+"PairRestore"+hit+"0",qtag(a)):a==="J"?z(mode+"PairRestore"+hit+"1",a):bad());
   for(let end of [0,1]){
    find(mode+"PairRestore"+hit+end,a=>mode==="f"?a==="Q":/^Q[01]$/.test(a),a=>z(mode+"FindEnd"+end,mode==="f"?"P"+hit:"P"+a[1]));
   }
  }
  for(let end of [0,1]){
   find(mode+"FindEnd"+end,a=>a==="KV",a=>r(mode+"NextPair"+end,"V"));
   next(mode+"NextPair"+end,a=>pair(a)?end?bad():z(mode+"PrivateFirst",mode==="f"?"Q":"Q"+a[1]):a==="J"?end?z(mode+"RootGroupAdvance",a):bad():bad());
  }
  find(mode+"RootGroupAdvance",a=>a==="BI",a=>r(mode+"RootGroupEnd","IG"));
  walk(mode+"RootGroupEnd",1,a=>a==="J"?r(mode+"RootGroupNext",a):null);
  for(let end of [0,1]){
   find(mode+"DestGroupRestore"+end,a=>a==="U",a=>r(mode+"DestGroupEnd"+end,"G"));
   walk(mode+"DestGroupEnd"+end,1,a=>a==="J"?r(mode+"DestGroupNext"+end,a):null);
   next(mode+"DestGroupNext"+end,a=>a==="G"?end?bad():r(mode+"DestPairNextGroup","U"):a==="D"?end?z(mode+"StageRestore","X"):bad():bad());
  }
  next(mode+"RootGroupNext",a=>a==="IG"?z(mode+"DestGroupRestore0","BI"):a==="A"?z(mode+"DestGroupRestore1",a):bad());
  next(mode+"DestPairNextGroup",a=>pair(a)?z(mode+"FindRootGroup",mode==="f"?"Q":"Q"+a[1]):bad());
  find(mode+"FindRootGroup",a=>a==="BI",a=>r(mode+"RootVal",a));
  find(mode+"StageRestore",a=>a==="B",a=>z(mode+"StageEnd","H"));
  find(mode+"StageEnd",a=>a==="X",a=>r(mode+"Child","D"));
 }
 find("selectRoot",a=>a==="IG",a=>r("selectScan",a));
 walk("selectScan",1,a=>a==="T11"?z("bBegin","W"):a==="A"?bad():null);
 add("clean",a=>a==="L"?r("readyAt","__"):a==="__"?bad():l("clean",a));
 add("readyAt",a=>a==="Z"?z("ready",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection,rules};
}
function encode(root,children){
 const b=x=>x?"001":"000";
 return root.map(g=>"010"+g.map(b).join("")+"101").join("")+"110"+children.map(c=>c.u.map(b).join("")+"111"+c.t.map(g=>"010"+g.map(p=>"011"+p.map(row=>row.map(b).join("")).join("")+"100").join("")+"101").join("")+"110").join("");
}
function logical(J,raw,limit=3000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a);trace.push([state,head,a]);if(trace.length>16)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,tape:[...tape].sort((a,b)=>a[0]-b[0]),out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}
