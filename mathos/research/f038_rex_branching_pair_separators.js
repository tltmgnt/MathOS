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

function physical(M,raw,limit=50000000){
 let tape=new Map([...raw].map((v,i)=>[i,+v])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,forward=null,backward=null;
 const snap=()=>({head,tape:[...tape].sort((a,b)=>a[0]-b[0])});
 while(state!==M.q&&t<limit){
  let name=M.names[state];if(name==="read:selectRoot:")forward=snap();if(name==="read:readyAt:")backward=snap();
  ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [q,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=q;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }return {tape,head,state,t,ph,logical,span:hi-lo+1,forward,backward};
}
function oracle(root,children){
 for(let c=0;c<root.length;c++)for(let b=0;b<root[c].length;b++){
  if(!root[c][b])continue;
  let a=[];
  function rec(i){
   if(i===children.length)return [b,c,...a];
   let ch=children[i];
   for(let j=0;j<ch.u.length;j++)if(ch.u[j]&&ch.t[c][b][j][0]&&ch.t[c][b][j][1]){a.push(j);let z=rec(i+1);if(z)return z;a.pop();}
   return null;
  }
  let z=rec(0);if(z)return z;
 }return null;
}
function audit(){
 const J=worker(),M=compile(J.rules,J.symbols,J.projection),ok=(x,s)=>{if(!x)throw Error(s)},dec=new Map(Object.entries(M.code).map(([a,b])=>[b,a]));
 let counts={logicalCases:0,physicalCases:0,sat:0,unsat:0,physicalSat:0,physicalUnsat:0,candidates:0,physical:0,logical:0,checkpoints:0,rootEntries:0,childEntries:0,predecessors:0,malformed:0,malformedTransitions:0,cutoffs:0},digest=2166136261,physicalDigest=2166136261;
 function check(root,children,mode=true,record=true){
  let raw=encode(root,children),N=raw.length,w=M.width,a=oracle(root,children),want=a?root.map((g,c)=>g.map((_,b)=>+(b===a[0]&&c===a[1])).join("")).join("")+children.map((ch,i)=>ch.u.map((_,j)=>+(j===a[i+2])).join("")).join(""):null;
  let ref=logical(J,raw,30000000);ok(ref.state===(a?"ready":"reject")&&(!a||ref.out===want),"logical "+JSON.stringify({root,children,want,ref:{state:ref.state,out:ref.out,trace:ref.trace}}));
  let expected=[],positions=[],selected=[],preds=0,childEntries=0,rootEntries=0;
  const token=v=>{expected.push("Z","Z",v);return expected.length-1;};
  let msg=root.map((g,c)=>g.map((x,b)=>+(x&&children.every(ch=>ch.u.some((u,j)=>u&&ch.t[c][b][j].every(Boolean))))));
  for(let c=0;c<root.length;c++){
   token("IG");
   for(let b=0;b<root[c].length;b++){let p=token("T"+root[c][b]+msg[c][b]);positions.push(p);if(a&&b===a[0]&&c===a[1])selected.push([p,"W"]);rootEntries++;}
   token("J");
  }token("A");
  for(let i=0;i<children.length;i++){
   let ch=children[i];
   for(let j=0;j<ch.u.length;j++){let p=token("U"+ch.u[j]);positions.push(p);if(a&&j===a[i+2])selected.push([p,"UW"]);}
   token("H");
   for(let c=0;c<root.length;c++){
    token("G");
    for(let b=0;b<root[c].length;b++){
     let p=ch.u.findIndex((u,j)=>u&&ch.t[c][b][j].every(Boolean));preds+=+(p>=0);childEntries++;token("P"+ +(p>=0));
     for(let j=0;j<ch.u.length;j++){token("F"+ch.t[c][b][j][0]);token(j===p?"EP":"E"+ch.t[c][b][j][1]);}token("V");
    }token("J");
   }token("D");
  }expected.push("R");
  let r=null;
  if(mode){
   r=physical(M,raw);ok(r.state===M.q&&r.logical===ref.t,"physical halt");
   let prep=(w+1)*N*(N+1)+(w+4)*N+3,mid=(3*w-2)*ref.moves+(2*w-1)*(ref.t-ref.moves);
   ok(r.ph[0]===prep&&r.ph[1]===mid,"phase clock");
   let start=-w*N-1;
   function unpack(cp,left){ok(cp&&cp.tape.length===w*(N+1+left)&&cp.tape.every(([p],i)=>p===start-left*w+i),"checkpoint layout");let b=cp.tape.map(x=>x[1]).join(""),v=Array.from({length:N+1+left},(_,i)=>dec.get(b.slice(w*i,w*(i+1))));ok(!left||v[0]==="L","left");return v.slice(left);}
   ok(JSON.stringify(unpack(r.forward,1))===JSON.stringify(expected),"forward "+raw);
   if(a){
    ok(r.tape.size===want.length&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b),"physical output");
    let back=expected.slice();for(let [p,v] of selected)back[p]=v;
    ok(JSON.stringify(unpack(r.backward,0))===JSON.stringify(back),"backward "+raw);
    let H=want.length,c=0,body=0,p=new Set(positions);
    for(let i=N-1;i>=0;i--){let e=+p.has(i);body+=2*w*(i+1)+2*c+2*e+4;c+=e;}
    ok(r.ph[2]===2*w*N+2*w+2+body+H+3&&r.head===-w*N-H-2,"serializer");
   }else ok(!r.tape.has(r.head)&&r.ph[2]===0&&!r.backward,"rejection");
  }
  if(record){
   counts.logicalCases++;counts.sat+=+(!!a);counts.unsat+=+(!a);counts.candidates+=children.reduce((x,ch)=>x+root.length*root[0].length*ch.u.length,0);
   if(mode){counts.physicalCases++;counts.physicalSat+=+(!!a);counts.physicalUnsat+=+(!a);counts.physical+=r.t;counts.logical+=r.logical;counts.checkpoints+=1+ +(!!a);counts.rootEntries+=rootEntries;counts.childEntries+=childEntries;counts.predecessors+=preds;}
   for(let ch of raw+":"+(a?ref.out:"-")+";")digest=Math.imul(digest^ch.charCodeAt(0),16777619)>>>0;
   if(mode){let out=a?Array.from({length:want.length},(_,i)=>r.tape.get(r.head+i)).join(""):"-";for(let ch of raw+":"+out+";")physicalDigest=Math.imul(physicalDigest^ch.charCodeAt(0),16777619)>>>0;}
  }return r;
 }
 const bits=(x,n)=>Array.from({length:n},(_,j)=>(x>>j)&1),root=(b,c,x)=>Array.from({length:c},(_,j)=>bits(x>>>(j*b),b));
 const child=(b,c,u,x,y)=>({u,t:Array.from({length:c},(_,k)=>Array.from({length:b},(_,j)=>Array.from({length:u.length},(_,i)=>[(x>>>(i+u.length*(j+b*k)))&1,(y>>>(i+u.length*(j+b*k)))&1])))});
 for(let b=1;b<=3;b++)for(let c=1;c<=3;c++)for(let x=0;x<Math.min(16,2**(b*c));x++)check(root(b,c,x),[],x<2);
 for(let x=0;x<16;x++)for(let y=0;y<16;y++)check(root(2,2,15),[child(2,2,[1],x,y)],x===y&&x%3===0);
 // All ordered pairs of child messages, preserving a shared two-coordinate tuple.
 for(let x=0;x<16;x++)for(let y=0;y<16;y++)check(root(2,2,15),[child(2,2,[1],x,15),child(2,2,[1],y,15)],x===y&&x%5===0);
 // Contradictory pair marginals and incompatible private witnesses.
 check(root(2,2,15),[child(2,2,[1],9,15),child(2,2,[1],6,15)]);
 check(root(2,2,15),[child(2,2,[1,1],85,170)]);
 let seed=0x52455816;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<36;i++){
  let b=1+(rand()>>>28)%3,c=1+(rand()>>>28)%3,g=1+i%3,rootMask=Array.from({length:c},()=>Array.from({length:b},()=>rand()>>>31)),children=[];
  for(let j=0;j<g;j++){let m=1+(rand()>>>28)%4,u=Array.from({length:m},()=>rand()>>>31),t=Array.from({length:c},()=>Array.from({length:b},()=>Array.from({length:m},()=>[rand()>>>31,rand()>>>31])));children.push({u,t});}
  if(i%2){let B=(rand()>>>16)%b,C=(rand()>>>16)%c;rootMask[C][B]=1;for(let ch of children){let a=(rand()>>>16)%ch.u.length;ch.u[a]=1;ch.t[C][B][a]=[1,1];}}
  check(rootMask,children,i<8);
 }
 let forcedRoot=root(2,3,32),forced=[1,3,2],forcedChildren=forced.map((a,i)=>({u:Array.from({length:[2,4,3][i]},()=>1),t:Array.from({length:3},(_,c)=>Array.from({length:2},(_,b)=>Array.from({length:[2,4,3][i]},(_,j)=>{let x=+(b===1&&c===2&&j===a);return [x,x];})))}));
 check(forcedRoot,forcedChildren);
 let good=encode([[1]],[child(1,1,[1],1,1)]),malformed=["","0","010","010110",encode([[1],[1,0]],[]),encode([[1,1],[1]],[]),encode([[1]],[child(1,1,[],0,0)]),encode([[1]],[{u:[1],t:[[[[1,1],[1,1]]]]}]),encode([[1]],[{u:[1,1],t:[[[[1,1]]]]}]),encode([[1,1]],[child(1,1,[1],1,1)]),encode([[1],[1]],[child(1,1,[1],1,1)]),encode([[1]],[child(2,1,[1],3,3)]),encode([[1]],[child(1,2,[1],3,3)]),encode([[0]],[child(1,1,[1],0,0),child(2,1,[1],3,3)]),good.slice(0,-1),good.slice(0,-3),good+"0",good+"110"];
 for(let raw of malformed){let r=physical(M,raw);ok(r.state===M.q&&!r.tape.has(r.head),"malformed "+raw);counts.malformed++;counts.malformedTransitions+=r.t;}
 let scaling=[];
 for(let m of [1,2,3,4]){
  let R=root(m,m,0);R[m-1][m-1]=1;
  let children=Array.from({length:2},()=>({u:Array(m).fill(1),t:Array.from({length:m},(_,c)=>Array.from({length:m},(_,b)=>Array.from({length:m},(_,a)=>{let x=+(a===m-1&&b===m-1&&c===m-1);return [x,x];})))})),raw=encode(R,children),r=check(R,children,true,false);
  if(m<=2){ok(physical(M,raw,r.t-1).state!==M.q,"cutoff");counts.cutoffs++;}
  scaling.push([m,raw.length,r.t,r.logical,r.span,r.ph]);
 }
 let pos=3;while(M.desc[pos]==="1")pos++;ok(pos-3===M.q&&M.desc[pos++]==="0","header");let b=M.q.toString(2).length;
 for(let [q,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===q&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
 ok(pos===M.desc.length,"descriptor length");
 return {alphabet:J.symbols.length,width:M.width,logicalStates:new Set(J.rules.map(x=>x[0])).size,rules:J.rules.length,states:M.q,bits:M.desc.length,counts,scaling,digest,physicalDigest};
}
if(process.argv.includes('--description')){let j=worker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_BRANCHING_PAIR_OK '+JSON.stringify(audit()));
