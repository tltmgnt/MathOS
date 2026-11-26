// REX-019: pivot-synchronous bounded-sweep joint alignment; same REX-018 raw grammar.
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
 // Pivot-synchronous refinement: each pivot digit is broadcast to all
 // still-compatible child rows in one bounded sweep. No per-pair global scan.
 for(let m of ["f","b"]){
  find(m+"ChildStart",a=>a==="D",a=>r(m+"Activate",a));
  add(m+"Activate",a=>a==="R"?z(m+"AParent",a):data(a)?r(m+"Activate",a==="H"?"K":a):bad());
  for(let [p,c] of [["A","C"],["B","E"]]){
   find(m+p+"Parent",a=>a==="Q",a=>r(m+p+"Pscan",a));
   scan(m+p+"Pscan",a=>pm(a)?z(m+p+"Broadcast2",a):a===p+"0"||a===p+"1"?z(m+p+"Broadcast"+a[1],"U"+a):null);
   for(let b of [0,1,2]){
    let h=m+p+b;
    find(m+p+"Broadcast"+b,a=>a==="D",a=>r(h+"Next",a));
    add(h+"Next",a=>a==="K"?r(h+"Compare",a):a==="H"?r(h+"Skip",a):a==="R"?z(b===2?(p==="A"?m+"BParent":m+"Collect"):m+p+"Parent",a):data(a)?r(h+"Next",a):bad());
    scan(h+"Compare",a=>{
     if(cm(a))return b===2?r(h+"Next",a):l(h+"Drop",a);
     if(a===c+"0"||a===c+"1")return b!==2&&a[1]===String(b)?r(h+"Skip","U"+a):l(h+"Drop",a);
     return null;
    });
    add(h+"Drop",a=>a==="K"?r(h+"Skip","H"):data(a)?l(h+"Drop",a):bad());
    scan(h+"Skip",a=>cm(a)?r(h+"Next",a):null);
   }
  }
  // Restore every child field and header, retaining a single existence bit.
  find(m+"Collect",a=>a==="D",a=>r(m+"Collect0",a));
  for(let hit of [0,1]){
   add(m+"Collect"+hit,a=>a==="R"?z(m+"RestoreParent"+hit,a):a==="K"||a==="H"?r(m+"CollectRow"+hit+ +(a==="K"),"H"):data(a)?r(m+"Collect"+hit,a):bad());
   for(let active of [0,1]){
    scan(m+"CollectRow"+hit+active,a=>{
     if(/^U[CE][01]$/.test(a))return r(m+"CollectRow"+hit+active,a.slice(1));
     if(cm(a)){let yes=active&&a==="N1";return r(m+"Collect"+ +(hit||yes),m==="b"&&yes&&!hit?"O1":a);}
     return null;
    });
   }
   find(m+"RestoreParent"+hit,a=>a==="Q",a=>r(m+"RestoreFields"+hit,a));
   scan(m+"RestoreFields"+hit,a=>pm(a)?m==="f"?z("finishParent0","T1"+hit):hit?z("bFinish",a):bad():/^U[AB][01]$/.test(a)?r(m+"RestoreFields"+hit,a.slice(1)):null);
  }
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

function physical(M,raw,limit=30000000){
 let tape=new Map([...raw].map((v,i)=>[i,+v])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,forward=null,backward=null;
 const snap=()=>({head,tape:[...tape].sort((a,b)=>a[0]-b[0])});
 while(state!==M.q&&t<limit){
  let name=M.names[state];if(name==="read:selectParent:"&&!forward)forward=snap();if(name==="read:readyAt:")backward=snap();
  ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [q,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=q;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }return {tape,head,state,t,ph,logical,span:hi-lo+1,forward,backward};
}
function oracle(k,P,C){
 const [a,b]=[[0,1],[0,2],[1,2]][k];
 let supports=P.map(p=>p[3]?C.findIndex(c=>c[3]&&p[a]===c[0]&&p[b]===c[1]):-1);
 let i=supports.findIndex(x=>x>=0),j=i<0?-1:supports[i];
 return {flags:supports.map(x=>+(x>=0)),chosen:j,out:supports.map(x=>+(x>=0)).join("")+C.map((_,x)=>+(x===j)).join("")};
}
function audit(){
 const J=worker(),M=compile(J.rules,J.symbols,J.projection),ok=(v,s)=>{if(!v)throw Error(s)},dec=new Map(Object.entries(M.code).map(([a,b])=>[b,a])),pairs=[[0,1],[0,2],[1,2]];
 let counts={logicalCases:0,physicalCases:0,positiveCases:0,negativeCases:0,physicalPositive:0,physicalNegative:0,parentRows:0,childRows:0,physical:0,logical:0,checkpoints:0,physicalParentFlags:0,physicalChildFlags:0,malformed:0,malformedTransitions:0,cutoffs:0},digest=2166136261,physicalDigest=2166136261;
 function check(k,P,C,mode=true,record=true){
  let raw=encode(k,P,C),N=raw.length,w=M.width,want=oracle(k,P,C),ref=logical(J,raw,10000000);
  ok(ref.state==="ready"&&ref.out===want.out,"logical "+JSON.stringify({k,P,C,want,ref}));
  let r=null;
  if(mode){
   r=physical(M,raw);ok(r.state===M.q&&r.logical===ref.t,"physical halt");
   let prep=(w+1)*N*(N+1)+(w+4)*N+3,mid=(3*w-2)*ref.moves+(2*w-1)*(ref.t-ref.moves);
   ok(r.ph[0]===prep&&r.ph[1]===mid,"phase clock");
   let start=-w*N-1;
   function unpack(cp,left){ok(cp&&cp.tape.length===w*(N+1+left)&&cp.tape.every(([p],i)=>p===start-left*w+i),"checkpoint layout");let b=cp.tape.map(x=>x[1]).join(""),v=Array.from({length:N+1+left},(_,i)=>dec.get(b.slice(i*w,(i+1)*w)));ok(!left||v[0]==="L","sentinel");return v.slice(left);}
   let expected=[...raw.slice(0,2)].map(x=>x+"_"),positions=[],childMaskPositions=[];
   const token=a=>{expected.push("Z","Z",a);return expected.length-1;};
   for(let side of ["p","c"]){
    if(side==="c")token("D");
    for(let [i,row] of (side==="p"?P:C).entries()){
     token(side==="p"?"P":"H");
     for(let j=0;j<3;j++){
      let a=side==="p"?(j===pairs[k][0]?"A":j===pairs[k][1]?"B":"X"):["C","E","X"][j];
      for(let bit of row[j])token(a+bit);token("J");
     }
     let p=token(side==="p"?"T"+row[3]+want.flags[i]:"N"+row[3]);positions.push(p);if(side==="c")childMaskPositions.push(p);
    }
   }expected.push("R");
   ok(JSON.stringify(unpack(r.forward,1))===JSON.stringify(expected),"forward tape");
   let back=expected.slice();if(want.chosen>=0)back[childMaskPositions[want.chosen]]="O1";
   ok(JSON.stringify(unpack(r.backward,0))===JSON.stringify(back),"backward tape");
   let H=want.out.length;ok(r.tape.size===H&&[...want.out].every((v,i)=>r.tape.get(r.head+i)===+v),"physical output");
   let body=0,c=0,p=new Set(positions);
   for(let i=N-1;i>=0;i--){let e=+p.has(i);body+=2*w*(i+1)+2*c+2*e+4;c+=e;}
   ok(r.ph[2]===2*w*N+2*w+2+body+H+3&&r.head===-w*N-H-2,"serializer "+JSON.stringify({H,ph:r.ph,head:r.head,expected:-w*N-H-2}));
  }
  if(record){
   let pos=want.chosen>=0;counts.logicalCases++;counts.positiveCases+=+pos;counts.negativeCases+=+!pos;counts.parentRows+=P.length;counts.childRows+=C.length;
   for(let ch of raw+":"+ref.out+";")digest=Math.imul(digest^ch.charCodeAt(0),16777619)>>>0;
   if(mode){counts.physicalCases++;counts.physicalPositive+=+pos;counts.physicalNegative+=+!pos;counts.physical+=r.t;counts.logical+=r.logical;counts.checkpoints+=2;counts.physicalParentFlags+=P.length;counts.physicalChildFlags+=C.length;
    let out=Array.from({length:want.out.length},(_,i)=>r.tape.get(r.head+i)).join("");for(let ch of raw+":"+out+";")physicalDigest=Math.imul(physicalDigest^ch.charCodeAt(0),16777619)>>>0;}
  }return r;
 }
 const labels=["0","1","10","101"];
 for(let k=0;k<3;k++){
  check(k,[],[]);check(k,[["0","1","10",1]],[]);check(k,[],[["0","1","10",1]]);
  // Exhaust all binary parent/child tuple pairs and mask combinations.
  for(let p=0;p<8;p++)for(let c=0;c<8;c++)for(let m=0;m<4;m++){
   let P=[[...p.toString(2).padStart(3,"0"),m&1]],C=[[...c.toString(2).padStart(3,"0"),m>>1]];
   check(k,P,C,(p===5&&c%3===0&&m===3)||(p===0&&c===0&&m!==3));
  }
  // Equality of lengths matters: a prefix does not match a longer rank.
  let P=[["0","10","101",1],["1","10","101",1],["0","10","101",0],["101","1","0",1]];
  let [x,y]=pairs[k],C=[[P[0][x]+"1",P[0][y],"0",1],[P[0][x],P[0][y],"111",0],[P[1][x],P[1][y],"10",1],[P[0][x],P[0][y],"1",1],[P[0][x],P[0][y],"0",1]];
  check(k,P,C);
  check(k,[["0","0","0",1]],[["00","0","0",1],["0","00","0",1]]);
 }
 // Equal and unequal joint relations have identical unary marginals.
 for(let k=0;k<3;k++){
  let [x,y]=pairs[k],p=(a,b,v)=>{let row=["101","101","101",v];row[x]=a;row[y]=b;return row;};
  let P=[p("0","0",1),p("1","1",1)],C=[["0","1","11",1],["1","0","10",1]];
  ok(oracle(k,P,C).out==="0000","joint obstruction");check(k,P,C);
  // Duplicate parent identity is significant; disabled duplicate never becomes true.
  // Two child supports differ in their fresh value; first input support is retained.
  check(k,[p("10","101",0),p("10","101",1),p("10","101",1)],[["10","101","1",0],["10","101","11",1],["10","101","0",1]]);
 }
 let seed=0x52455818;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<36;i++){
  let k=i%3,rows=n=>Array.from({length:n},()=>[...Array.from({length:3},()=>labels[(rand()>>>16)%4]),rand()>>>31]),P=rows(1+i%3),C=rows(1+(i>>2)%3);
  if(i%2){let [x,y]=pairs[k];P[0][3]=1;C[0]=[P[0][x],P[0][y],C[0][2],1];}
  check(k,P,C,i<6);
 }
 let good=encode(0,[["0","1","10",1]],[["0","1","1",1]]),malformed=["","0","11","00111","00011","00110"+"011010","00110"+"110",good.slice(0,-1),good.slice(0,-3),good+"0",good+"110",encode(0,[["","0","1",1]],[]),encode(2,[],[["0","","1",1]])];
 for(let raw of malformed){let r=physical(M,raw);ok(r.state===M.q&&!r.tape.has(r.head),"malformed "+raw);counts.malformed++;counts.malformedTransitions+=r.t;}
 let scaling=[];
 for(let w of [1,2,4,8,16]){
  let x="1".repeat(w),y="0".repeat(w-1)+"1",P=[[x,"0",y,1]],C=[[x,y+"0","0",1],[x,y,"1",1]],raw=encode(1,P,C),r=check(1,P,C,true,false);
  if(w<=2){ok(physical(M,raw,r.t-1).state!==M.q,"cutoff");counts.cutoffs++;}
  scaling.push([w,raw.length,r.t,r.logical,r.span,r.ph]);
 }
 let rowScaling=[];
 for(let n of [1,2,4,8]){
  let P=Array.from({length:n},()=>["101","11","0",1]),C=Array.from({length:n},()=>["101","10","1",1]);
  let raw=encode(0,P,C),r=check(0,P,C,true,false);
  rowScaling.push([n,raw.length,r.t,r.logical,r.span,r.ph]);
 }
 let pos=3;while(M.desc[pos]==="1")pos++;ok(pos-3===M.q&&M.desc[pos++]==="0","header");let b=M.q.toString(2).length;
 for(let [q,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===q&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
 ok(pos===M.desc.length,"descriptor length");
 return {alphabet:J.symbols.length,width:M.width,logicalStates:new Set(J.rules.map(x=>x[0])).size,rules:J.rules.length,states:M.q,bits:M.desc.length,counts,scaling,rowScaling,digest,physicalDigest};
}
if(process.argv.includes('--description')){let j=worker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_RANKED_OVERLAP_OK '+JSON.stringify(audit()));
