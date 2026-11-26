// REX-015: variable-domain sliding triple factors, joint pair frontier.
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
 const symbols=["__","0_","1_","L","R","Z","D","A","IG","G","J","V","P","Q","Q0","Q1","U","UW","BI","BG","BW","W","M0","M1","MW","T0","T1","TW","CM0","CM1","CT0","CT1","CTW","F0","F1","E0","E1","EP","K0","K1","KV","X","Y"];
 const projection=Object.fromEntries(symbols.filter(a=>a!=="__").map(a=>[a,a==="MW"||a==="W"?"1":a==="M0"||a==="M1"||a==="G"?"0":"_"]));
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error("duplicate "+s);defs.set(s,fn)};
 const z=(s,a)=>[s,a,0],r=(s,a)=>[s,a,1],l=(s,a)=>[s,a,-1],bad=()=>z("reject","__");
 const raw=a=>a==="0_"||a==="1_",data=a=>!["__","L","R"].includes(a),msg=a=>/^[MT][01W]$/.test(a),cur=a=>/^C[MT][01W]$/.test(a),group=a=>["IG","G","W"].includes(a),bc=a=>["BI","BG","BW"].includes(a),edge=a=>/^F[01]$/.test(a);
 const btag=a=>a==="IG"?"BI":a==="W"?"BW":"BG",brestore=a=>a==="BI"?"IG":a==="BW"?"W":"G";
 function find(s,p,act){add(s,a=>a==="L"?r(s+"Scan",a):a==="__"?bad():l(s,a));add(s+"Scan",a=>p(a)?act(a):data(a)?r(s+"Scan",a):bad());}
 function next(s,act){add(s,a=>a==="Z"?r(s,a):act(a));}
 function walk(s,dir,act){add(s,a=>{let q=act(a);return q??(data(a)?(dir===1?r(s,a):l(s,a)):bad());});}
 // Token codes 000,001 bits; 010 group; 011 pair; 100 pair end; 101 group end; 110 stage end.
 // Parsing first establishes an entirely tagged contiguous region.
 add("init",a=>raw(a)?l("left",a):bad());add("left",a=>a==="__"?r("parseInitial", "L"):bad());
 const parse={
  Initial:{"010":["IG","IFirst"]},IFirst:{"000":["M0","IValues"],"001":["M1","IValues"]},
  IValues:{"000":["M0","IValues"],"001":["M1","IValues"],"101":["J","IAfter"]},
  IAfter:{"010":["IG","IFirst"],"110":["A","Stage"]},
  Stage:{"010":["G","GFirst"]},GFirst:{"011":["P","FBit"]},FBit:{"000":["F0","EBit"],"001":["F1","EBit"]},
  EBit:{"000":["E0","AfterE"],"001":["E1","AfterE"]},
  AfterE:{"000":["F0","EBit"],"001":["F1","EBit"],"100":["V","AfterP"]},
  AfterP:{"011":["P","FBit"],"101":["J","AfterG"]},
  AfterG:{"010":["G","GFirst"],"110":["D","Stage"]}
 };
 for(let [name,table] of Object.entries(parse)){
  for(let k=0;k<3;k++)for(let i=0;i<2**k;i++){
   let b=k?i.toString(2).padStart(k,"0"):"";
   add("parse"+name+b,a=>{
    if(k===0&&name==="Stage"&&a==="__")return l("initValidateStart","R");
    if(!raw(a))return bad();let v=b+a[0];
    if(k<2)return r("parse"+name+v,"Z");
    let q=table[v];return q?r("parse"+q[1],q[0]):bad();
   });
  }
 }
 // Check initial rectangularity by comparing each adjacent pair of groups.
 find("initValidateStart",a=>a==="IG",a=>r("ivLeftFirst","BI"));
 next("ivLeftFirst",a=>msg(a)?z("ivFindRight","C"+a):bad());
 find("ivFindRight",a=>a==="BI",a=>r("ivRightSeek",a));
 walk("ivRightSeek",1,a=>a==="J"?r("ivRightStart",a):null);
 next("ivRightStart",a=>a==="A"?z("ivDone",a):a==="IG"?r("ivRightFirst","U"):bad());
 next("ivRightFirst",a=>/^M[01]$/.test(a)?z("ivLeftRestore","Q"+a[1]):bad());
 find("ivLeftRestore",cur,a=>r("ivLeftNext",a.slice(1)));
 next("ivLeftNext",a=>/^M[01]$/.test(a)?z("ivRightRestore0","C"+a):a==="J"?z("ivRightRestore1",a):bad());
 for(let end of [0,1]){
  find("ivRightRestore"+end,a=>/^Q[01]$/.test(a),a=>r("ivRightNext"+end,"M"+a[1]));
  next("ivRightNext"+end,a=>/^M[01]$/.test(a)?end?bad():z("ivLeftRestore","Q"+a[1]):a==="J"?end?z("ivAdvance",a):bad():bad());
 }
 find("ivAdvance",a=>a==="BI",a=>z("ivNew","IG"));
 find("ivNew",a=>a==="U",a=>r("ivLeftFirst","BI"));
 find("ivDone",cur,a=>z("ivDoneGroup",a.slice(1)));
 find("ivDoneGroup",a=>a==="BI",a=>z("startForward","IG"));
 // Select source stage by unique A, then locate its first group to the left.
 find("startForward",a=>a==="A",a=>r("fDestFirst",a));
 next("fDestFirst",a=>a==="G"?r("fPairFirst","U"):a==="R"?z("finalStart",a):bad());
 next("fPairFirst",a=>a==="P"?z("fSource","Q"):bad());
 for(let mode of ["f","b"]){
  find(mode+"Source",a=>a==="A",a=>l(mode+"SourceStart",a));
  walk(mode+"SourceStart",-1,a=>a==="D"||a==="L"?r(mode+"SourceGroup",a):null);
  next(mode+"SourceGroup",a=>group(a)?r(mode+"SourceFirst",btag(a)):bad());
  next(mode+"SourceFirst",a=>msg(a)?z(mode+"EdgeFirst","C"+a):bad());
  // Backward traverses just the chosen destination group, all its pairs,
  // selecting a source entry only at its selected pair's EP marker.
  find(mode+"EdgeFirst",a=>a==="Q"||/^Q[01]$/.test(a),a=>r(mode+"FirstF",a));
  next(mode+"FirstF",a=>edge(a)?z(mode+"Read0","K"+a[1]):bad());
  for(let hit of [0,1]){
   find(mode+"Read"+hit,cur,a=>z(mode+"ReadK"+hit+(a.endsWith("1")||a.endsWith("W")?1:0),a));
   for(let feasible of [0,1]){
    find(mode+"ReadK"+hit+feasible,a=>/^K[01]$/.test(a),a=>r(mode+"ReadE"+hit+feasible+a[1],"F"+a[1]));
    for(let first of [0,1]){
     next(mode+"ReadE"+hit+feasible+first,a=>{
      if(!/^E[01P]$/.test(a))return bad();
      if(mode==="f"){
       let yes=!hit&&feasible&&first&&a==="E1";return r("fNextF"+ +(hit||yes),yes?"EP":a);
      }
      // Use a unique temporary mark at the predecessor, only if current Q1.
      return a==="EP"?z("bCheckSelected"+hit,"X"):r("bNextF"+hit,a);
     });
    }
   }
   if(mode==="b"){
    find("bCheckSelected"+hit,a=>/^Q[01]$/.test(a),a=>z(a==="Q1"?"bSelectSource":"bRestoreEP"+hit,a));
    find("bRestoreEP"+hit,a=>a==="X",a=>r("bNextF"+hit,"EP"));
   }
   next(mode+"NextF"+hit,a=>edge(a)?z(mode+"Restore"+hit+"0","K"+a[1]):a==="V"?z(mode+"Restore"+hit+"1","KV"):bad());
   for(let end of [0,1]){
    find(mode+"Restore"+hit+end,cur,a=>r(mode+"SrcNext"+hit+end,a.slice(1)));
    walk(mode+"SrcNext"+hit+end,1,a=>msg(a)?end?bad():z(mode+"Read"+hit,"C"+a):a==="J"?end?z(mode+"PairDone"+hit,a):bad():null);
   }
   find(mode+"PairDone"+hit,a=>a==="Q"||/^Q[01]$/.test(a),a=>z(mode+"PairFinish"+hit,mode==="f"?"T"+hit:a==="Q1"?"TW":"T"+a[1]));
   // locate end of this pair using the unique KV marker, then find next pair.
   find(mode+"PairFinish"+hit,a=>a==="KV",a=>r(mode+"DestPairNext","V"));
  }
  next(mode+"DestPairNext",a=>mode==="f"&&a==="P"?z(mode+"GroupAdvance0","Q"):mode==="b"&&/^T[01W]$/.test(a)?z(mode+"GroupAdvance0",a==="TW"?"Q1":"Q0"):a==="J"?z(mode+"GroupAdvance1",a):bad());
  for(let end of [0,1]){
   find(mode+"GroupAdvance"+end,bc,a=>r(mode+"SourceGroupEnd"+end,brestore(a)));
   walk(mode+"SourceGroupEnd"+end,1,a=>a==="J"?r(mode+"SourceGroupNext"+end,a):null);
   next(mode+"SourceGroupNext"+end,a=>group(a)?end?bad():r(mode+"SourceFirst",btag(a)):a==="A"?end?z(mode+"GroupDone",a):bad():bad());
  }
 }
 // Forward: new group repeats full previous pair grid; end of stage moves A right.
 find("fGroupDone",a=>a==="U",a=>r("fGroupEnd","G"));
 walk("fGroupEnd",1,a=>a==="J"?r("fGroupNext",a):null);
 next("fGroupNext",a=>a==="G"?r("fPairFirst","U"):a==="D"?z("fShiftMark","Y"):bad());
 find("fShiftMark",a=>a==="A",a=>z("fShiftNew","D"));
 find("fShiftNew",a=>a==="Y",a=>r("fDestFirst","A"));
 // Final scan: least feasible pair ordered by second then first coordinate.
 find("finalStart",a=>a==="A",a=>l("finalLeft",a));
 walk("finalLeft",-1,a=>a==="D"||a==="L"?r("finalScan",a):null);
 walk("finalScan",1,a=>a==="M1"||a==="T1"?z("finalMark",a==="M1"?"MW":"TW"):a==="A"?bad():null);
 add("finalMark",a=>a==="MW"?z("clean",a):a==="TW"?l("finalGroup",a):bad());
 walk("finalGroup",-1,a=>a==="G"?z("bStart","W"):null);
 // Begin backtrack at chosen group in latest stage; shift boundary left.
 find("bStart",a=>a==="A",a=>l("bBoundary","D"));
 walk("bBoundary",-1,a=>a==="D"?z("bFindGroup","A"):a==="L"?bad():null);
 // W is not globally unique (already selected later stages); select first W
 // after A, not by a global scan.
 add("bFindGroup",a=>a==="A"?r("bFindSelected",a):bad());
 walk("bFindSelected",1,a=>a==="W"?r("bPairFirst","UW"):a==="D"?bad():null);
 next("bPairFirst",a=>/^T[01W]$/.test(a)?z("bSource",a==="TW"?"Q1":"Q0"):bad());
 // At selected predecessor, mark source cell and its group; then stop
 // processing this destination group (dimensions already validated forward).
 find("bSelectSource",cur,a=>a==="CM1"||a==="CT1"?z("bSelectGroup",a==="CM1"?"MW":"TW"):bad());
 find("bSelectGroup",bc,a=>z("bRestoreDest",a==="BI"?"IG":"W"));
 find("bRestoreDest",a=>a==="Q1",a=>z("bRestoreMark","T1"));
 find("bRestoreMark",a=>a==="X",a=>z("bRestoreGroup","EP"));
 find("bRestoreGroup",a=>a==="UW",a=>z("bAfterGroup","W"));
 find("bAfterGroup",a=>a==="A",a=>l("bPrevCheck",a));
 walk("bPrevCheck",-1,a=>a==="D"?z("bStart",a):a==="L"?r("clean",a):null);
 // bGroupDone is unreachable on a valid selected pair.
 add("bGroupDone",a=>bad());
 find("clean",a=>a==="L",a=>bad()); // overwritten below: remove left sentinel, ready at first block
 defs.set("clean",a=>a==="L"?r("readyAt","__"):a==="__"?bad():l("clean",a));
 defs.delete("cleanScan");
 add("readyAt",a=>a==="Z"?z("ready",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection,rules};
}
function encode(initial,stages){
 const b=x=>x?"001":"000";
 return initial.map(col=>"010"+col.map(b).join("")+"101").join("")+"110"+
 stages.map(s=>s.map(g=>"010"+g.map(col=>"011"+col.map(pair=>pair.map(b).join("")).join("")+"100").join("")+"101").join("")+"110").join("");
}
function logical(J,raw,limit=2000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let rule=rules.get(state+":"+a);if(!rule)throw Error("missing "+state+":"+a);let [s,w,d]=rule;trace.push([state,head,a]);if(trace.length>15)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,tape:[...tape].sort((a,b)=>a[0]-b[0]),out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}
