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
 const symbols=["__","0_","1_","L","R","Z","D","A","IG","G","J","V","P","Q","Q0","Q1","QW","U","UW","BI","BG","BW","W","M0","M1","MW","T0","T1","TW","CM0","CM1","CMW","CT0","CT1","CTW","F0","F1","E0","E1","EP","K0","K1","KV","X","Y"];
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
  find("ivRightRestore"+end,a=>/^Q[01W]$/.test(a),a=>r("ivRightNext"+end,"M"+a[1]));
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
  find(mode+"EdgeFirst",a=>a==="Q"||/^Q[01W]$/.test(a),a=>r(mode+"FirstF",a));
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
    find("bCheckSelected"+hit,a=>/^Q[01W]$/.test(a),a=>z(a==="QW"?"bSelectSource":"bRestoreEP"+hit,a));
    find("bRestoreEP"+hit,a=>a==="X",a=>r("bNextF"+hit,"EP"));
   }
   next(mode+"NextF"+hit,a=>edge(a)?z(mode+"Restore"+hit+"0","K"+a[1]):a==="V"?z(mode+"Restore"+hit+"1","KV"):bad());
   for(let end of [0,1]){
    find(mode+"Restore"+hit+end,cur,a=>r(mode+"SrcNext"+hit+end,a.slice(1)));
    walk(mode+"SrcNext"+hit+end,1,a=>msg(a)?end?bad():z(mode+"Read"+hit,"C"+a):a==="J"?end?z(mode+"PairDone"+hit,a):bad():null);
   }
   find(mode+"PairDone"+hit,a=>a==="Q"||/^Q[01W]$/.test(a),a=>z(mode+"PairFinish"+hit,mode==="f"?"T"+hit:a==="QW"?"TW":a==="Q"?"T0":"T"+a[1]));
   // locate end of this pair using the unique KV marker, then find next pair.
   find(mode+"PairFinish"+hit,a=>a==="KV",a=>r(mode+"DestPairNext","V"));
  }
  next(mode+"DestPairNext",a=>mode==="f"&&a==="P"?z(mode+"GroupAdvance0","Q"):mode==="b"&&/^T[01W]$/.test(a)?z(mode+"GroupAdvance0",a==="TW"?"QW":"Q"+a[1]):a==="J"?z(mode+"GroupAdvance1",a):bad());
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
 next("bPairFirst",a=>/^T[01W]$/.test(a)?z("bSource",a==="TW"?"QW":"Q"+a[1]):bad());
 // At selected predecessor, mark source cell and its group; then stop
 // processing this destination group (dimensions already validated forward).
 find("bSelectSource",cur,a=>a==="CM1"||a==="CT1"?z("bSelectGroup",a==="CM1"?"MW":"TW"):bad());
 find("bSelectGroup",bc,a=>z("bRestoreDest",a==="BI"?"IG":"W"));
 find("bRestoreDest",a=>a==="QW",a=>z("bRestoreMark","T1"));
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

function physical(M,raw,limit=40000000){
 let tape=new Map([...raw].map((v,i)=>[i,+v])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,forward=null,backward=null;
 const snap=()=>({head,tape:[...tape].sort((a,b)=>a[0]-b[0])});
 while(state!==M.q&&t<limit){
  let name=M.names[state];if(name==="read:finalStart:")forward=snap();if(name==="read:readyAt:")backward=snap();
  ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [q,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=q;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }return {tape,head,state,t,ph,logical,span:hi-lo+1,forward,backward};
}
function oracle(initial,stages){
 let sizes=[initial[0].length,initial.length,...stages.map(s=>s.length)],a=Array(sizes.length).fill(0);
 function rec(i){
  if(i<0)return initial[a[1]][a[0]]&&stages.every((s,j)=>s[a[j+2]][a[j+1]][a[j]].every(Boolean))?a.slice():null;
  for(let b=0;b<sizes[i];b++){a[i]=b;let w=rec(i-1);if(w!==null)return w;}return null;
 }return rec(sizes.length-1);
}
function audit(){
 const J=worker(),M=compile(J.rules,J.symbols,J.projection),ok=(x,s)=>{if(!x)throw Error(s)},dec=new Map(Object.entries(M.code).map(([a,b])=>[b,a]));
 let counts={logicalCases:0,physicalCases:0,sat:0,unsat:0,physicalSat:0,physicalUnsat:0,candidates:0,physical:0,logical:0,checkpoints:0,entries:0,predecessors:0,malformed:0,malformedTransitions:0,cutoffs:0},digest=2166136261;
 function check(initial,stages,mode=true,record=true){
  let raw=encode(initial,stages),N=raw.length,w=M.width,a=oracle(initial,stages),want=a?initial.map((col,b)=>col.map((_,j)=>+(b===a[1]&&j===a[0])).join("")).join("")+stages.map((s,i)=>s.map((_,j)=>+(j===a[i+2])).join("")).join(""):null;
  let ref=logical(J,raw,20000000);ok(ref.state===(a?"ready":"reject")&&(!a||ref.out===want),"logical "+JSON.stringify({initial,stages,want,ref:{state:ref.state,out:ref.out,trace:ref.trace}}));
  let expected=[],outPositions=[],chosen=[],stageEnds=[],msg=initial.map(c=>c.slice()),preds=0,entries=msg.reduce((x,c)=>x+c.length,0);
  const token=v=>{expected.push("Z","Z",v);return expected.length-1;};
  for(let b=0;b<initial.length;b++){token("IG");for(let j=0;j<initial[b].length;j++){let p=token("M"+initial[b][j]);outPositions.push(p);if(a&&a[0]===j&&a[1]===b)chosen.push([p,"MW"]);}token("J");}
  stageEnds.push(token("D"));
  for(let i=0;i<stages.length;i++){
   let next=[];
   for(let c=0;c<stages[i].length;c++){
    let p=token("G");outPositions.push(p);if(a&&a[i+2]===c)chosen.push([p,"W"]);let col=[];
    for(let b=0;b<stages[i][c].length;b++){
     let rows=stages[i][c][b],p=rows.findIndex((pair,j)=>msg[b][j]&&pair.every(Boolean));col.push(+(p>=0));preds+=+(p>=0);
     token("T"+ +(p>=0));for(let j=0;j<rows.length;j++){token("F"+rows[j][0]);token(j===p?"EP":"E"+rows[j][1]);}token("V");
    }next.push(col);token("J");
   }msg=next;entries+=msg.reduce((x,c)=>x+c.length,0);stageEnds.push(token("D"));
  }
  expected[stageEnds.at(-1)]="A";expected.push("R");
  let r=null;
  if(mode){
   r=physical(M,raw);ok(r.state===M.q&&r.logical===ref.t,"physical halt");
   let prep=(w+1)*N*(N+1)+(w+4)*N+3,mid=(3*w-2)*ref.moves+(2*w-1)*(ref.t-ref.moves);
   ok(r.ph[0]===prep&&r.ph[1]===mid,"clock");
   let start=-w*N-1;
   function unpack(cp,left){ok(cp&&cp.tape.length===w*(N+1+left)&&cp.tape.every(([p],i)=>p===start-left*w+i),"checkpoint layout");let b=cp.tape.map(x=>x[1]).join(""),v=Array.from({length:N+1+left},(_,i)=>dec.get(b.slice(w*i,w*(i+1))));ok(!left||v[0]==="L","left");return v.slice(left);}
   ok(JSON.stringify(unpack(r.forward,1))===JSON.stringify(expected),"forward "+raw);
   if(a){
    ok(r.tape.size===want.length&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b),"physical output");
    let back=expected.slice();back[stageEnds.at(-1)]="D";back[stageEnds[0]]="A";for(let [p,v] of chosen)back[p]=v;
    ok(JSON.stringify(unpack(r.backward,0))===JSON.stringify(back),"backward "+raw);
    let H=want.length,c=0,body=0,p=new Set(outPositions);
    for(let i=N-1;i>=0;i--){let e=+p.has(i);body+=2*w*(i+1)+2*c+2*e+4;c+=e;}
    ok(r.ph[2]===2*w*N+2*w+2+body+H+3&&r.head===-w*N-H-2,"serializer");
   }else ok(!r.tape.has(r.head)&&r.ph[2]===0&&!r.backward,"rejection");
  }
  if(record){
   counts.logicalCases++;counts.sat+=+(!!a);counts.unsat+=+(!a);counts.candidates+=stages.reduce((x,s)=>x+s.reduce((y,g)=>y+g.reduce((z,c)=>z+c.length,0),0),0);
   if(mode){counts.physicalCases++;counts.physicalSat+=+(!!a);counts.physicalUnsat+=+(!a);counts.physical+=r.t;counts.logical+=r.logical;counts.checkpoints+=1+ +(!!a);counts.entries+=entries;counts.predecessors+=preds;}
   for(let ch of raw+":"+(want??"-")+";")digest=Math.imul(digest^ch.charCodeAt(0),16777619)>>>0;
  }return r;
 }
 const bits=(x,n)=>Array.from({length:n},(_,j)=>(x>>j)&1);
 const tensor=(a,b,c,x,y)=>Array.from({length:c},(_,k)=>Array.from({length:b},(_,j)=>Array.from({length:a},(_,i)=>[(x>>(i+a*(j+b*k)))&1,(y>>(i+a*(j+b*k)))&1])));
 for(let a=1;a<=3;a++)for(let b=1;b<=3;b++)for(let x=0;x<Math.min(2**(a*b),16);x++)check(Array.from({length:b},(_,j)=>bits(x>>>(j*a),a)),[],x<3);
 for(let x=0;x<256;x++)check([[1,1],[1,1]],[tensor(2,2,2,x,255)],x%32===0);
 for(let x=0;x<16;x++)for(let y=0;y<16;y++)check([[1,1],[1,1]],[tensor(2,1,2,x,y)].map(s=>s.map(g=>[...g,...g])),false);
 // Explicit conflicting witnesses and incompatible pair marginals.
 check([[1,1],[1,1]],[tensor(2,2,2,85,170)]);
 let eq=tensor(2,2,2,195,255),neq=tensor(2,2,2,90,255); // masks indexed a+2b+4c: equality unchanged; incoming inequality is mask 102.
 neq=tensor(2,2,2,102,255);
 ok(oracle([[1,1],[1,1]],[eq,neq])===null,"pair obstruction");check([[1,1],[1,1]],[eq,neq]);
 let seed=0x52455815;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<32;i++){
  let g=1+i%3,d=Array.from({length:g+2},()=>1+(rand()>>>28)%3),initial=Array.from({length:d[1]},()=>Array.from({length:d[0]},()=>rand()>>>31)),stages=Array.from({length:g},(_,j)=>Array.from({length:d[j+2]},()=>Array.from({length:d[j+1]},()=>Array.from({length:d[j]},()=>[rand()>>>31,rand()>>>31]))));
  if(i%2){let a=d.map(m=>(rand()>>>16)%m);initial[a[1]][a[0]]=1;for(let j=0;j<g;j++)stages[j][a[j+2]][a[j+1]][a[j]]=[1,1];}
  check(initial,stages,i<12);
 }
 let malformed=["","0","010","010110",encode([[1],[1,0]],[]),encode([[1,1],[1]],[]),encode([[1,1]],[[[[[1,1]]]]]),encode([[1]],[[[[[1,1],[1,1]]]]]),encode([[1],[1]],[[[[[1,1]]]]]),encode([[1]],[[[[[1,1]],[[1,1]]]]]),encode([[0]],[[[[[0,0],[0,0]]]]])];
 let good=encode([[1]],[[[[[1,1]]]]]);malformed.push(good.slice(0,-1),good.slice(0,-3),good+"0",good+"110");
 for(let raw of malformed){let r=physical(M,raw);ok(r.state===M.q&&!r.tape.has(r.head),"malformed "+raw);counts.malformed++;counts.malformedTransitions+=r.t;}
 let scaling=[];
 for(let m of [1,2,3,4]){
  let initial=Array.from({length:m},(_,b)=>Array.from({length:m},(_,a)=>+(a===m-1&&b===m-1))),s=Array.from({length:m},(_,c)=>Array.from({length:m},(_,b)=>Array.from({length:m},(_,a)=>{let x=+(a===m-1&&b===m-1&&c===m-1);return [x,x]}))),raw=encode(initial,[s]),r=check(initial,[s],true,false);
  if(m<=2){ok(physical(M,raw,r.t-1).state!==M.q,"cutoff");counts.cutoffs++;}
  scaling.push([m,raw.length,r.t,r.logical,r.span,r.ph]);
 }
 let pos=3;while(M.desc[pos]==="1")pos++;ok(pos-3===M.q&&M.desc[pos++]==="0","header");let b=M.q.toString(2).length;
 for(let [q,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===q&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
 ok(pos===M.desc.length,"descriptor length");
 return {alphabet:J.symbols.length,width:M.width,states:M.q,bits:M.desc.length,rules:J.rules.length,counts,scaling,digest};
}
if(process.argv.includes('--description')){let j=worker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_VARIABLE_PAIR_OK '+JSON.stringify(audit()));
