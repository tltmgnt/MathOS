// REX-011 variable-domain path, raw factor masks, persistent physical messages and predecessor marks.
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
 const symbols=["__","0_","1_","L","R","Z","A","S","B","D","U0","U1","E0","E1","P","K0","K1","K2","Q0","Q1","W","T00","T01","T10","T11","C00","C01","C10","C11"];
 const projection=Object.fromEntries(symbols.filter(a=>a!=="__").map(a=>[a,a==="W"?"1":/^T/.test(a)?"0":"_"]));
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error(s);defs.set(s,fn)},go=(s,w,d=0)=>[s,w,d],r=(s,a)=>go(s,a,1),l=(s,a)=>go(s,a,-1),z=(s,a)=>go(s,a),bad=()=>z("reject","__");
 const raw=a=>a==="0_"||a==="1_",data=a=>a!=="__"&&a!=="L"&&a!=="R",T=a=>/^T[01][01]$/.test(a),C=a=>/^C[01][01]$/.test(a),K=a=>/^K[012]$/.test(a);
 function find(s,pred,act){
  add(s,a=>a==="L"?r(s+"Scan",a):a==="__"?bad():l(s,a));
  add(s+"Scan",a=>pred(a)?act(a):data(a)?r(s+"Scan",a):bad());
 }
 add("init",a=>raw(a)?l("left",a):bad());
 add("left",a=>a==="__"?r("initialFirst","L"):bad());
 add("initialFirst",a=>a==="0_"?r("initialBit","Z"):bad());
 add("initialBit",a=>raw(a)?r("initialNext","T"+a[0]+a[0]):bad());
 add("initialNext",a=>a==="0_"?r("initialBit","Z"):a==="1_"?r("initialEnd","Z"):bad());
 add("initialEnd",a=>a==="1_"?r("stageStart","A"):bad());
 add("stageStart",a=>a==="__"?l("rewind","R"):a==="0_"?r("unaryBit","Z"):bad());
 add("unaryBit",a=>raw(a)?r("edgeFirst","U"+a[0]):bad());
 add("edgeFirst",a=>a==="0_"?r("edgeBit","Z"):bad());
 add("edgeBit",a=>raw(a)?r("edgeNext","E"+a[0]):bad());
 add("edgeNext",a=>a==="0_"?r("edgeBit","Z"):a==="1_"?r("columnEnd","Z"):bad());
 add("columnEnd",a=>a==="0_"?r("columnNext","D"):bad());
 add("columnNext",a=>a==="0_"?r("unaryBit","Z"):a==="1_"?r("stageEnd","Z"):bad());
 add("stageEnd",a=>a==="1_"?r("stageStart","S"):bad());
 add("rewind",a=>a==="L"?r("startScan",a):a==="__"?bad():l("rewind",a));
 add("startScan",a=>a==="A"?r("forward",a):data(a)?r("startScan",a):bad());
 add("forward",a=>a==="Z"?r("forward",a):a==="U0"||a==="U1"?r("fFirst"+a[1],"Q"+a[1]):a==="S"?z("shiftOld","B"):a==="R"?z("lastBoundary",a):bad());
 find("shiftOld",a=>a==="A",a=>z("shiftNew","S"));
 find("shiftNew",a=>a==="B",a=>r("forward","A"));
 for(let u of [0,1]){
  add("fFirst"+u,a=>a==="Z"?r("fFirst"+u,a):a==="E0"||a==="E1"?z("fSource"+u,"K"+a[1]):bad());
  find("fSource"+u,a=>a==="A",a=>l("fStart"+u,a));
  add("fStart"+u,a=>a==="S"||a==="L"?r("fSrcFirst"+u,a):a==="__"?bad():l("fStart"+u,a));
  add("fSrcFirst"+u,a=>T(a)?z("fRead"+u+"0","C"+a.slice(1)):data(a)&&a!=="A"?r("fSrcFirst"+u,a):bad());
  for(let hit of [0,1]){
   let h=""+u+hit;
   find("fRead"+h,C,a=>z("fEdge"+h+a[2],a));
   for(let m of [0,1]){
    find("fEdge"+h+m,a=>a==="K0"||a==="K1",a=>{
     let yes=u&&m&&a==="K1"&&!hit;
     return r("fNextEdge"+u+(hit||yes?1:0),yes?"P":"E"+a[1]);
    });
   }
   add("fNextEdge"+h,a=>a==="Z"?r("fNextEdge"+h,a):a==="E0"||a==="E1"?z("fRestore"+h+"0","K"+a[1]):a==="D"?z("fRestore"+h+"1",a):bad());
   for(let end of [0,1]){
    find("fRestore"+h+end,C,a=>r("fNextSource"+h+end,"T"+a.slice(1)));
    add("fNextSource"+h+end,a=>T(a)?end?bad():z("fRead"+h,"C"+a.slice(1)):a==="A"?end?z("fDone"+h,a):bad():data(a)?r("fNextSource"+h+end,a):bad());
   }
   find("fDone"+h,a=>a==="Q"+u,a=>r("fSkip","T"+h));
  }
 }
 add("fSkip",a=>a==="D"?r("forward",a):data(a)?r("fSkip",a):bad());
 // Final feasibility and selection: A is the boundary following the last vertex.
 find("lastBoundary",a=>a==="A",a=>l("lastStart",a));
 add("lastStart",a=>a==="L"?r("selectInitial",a):a==="S"?r("selectLast","B"):a==="__"?bad():l("lastStart",a));
 add("selectInitial",a=>a==="T11"?z("clean","W"):data(a)&&a!=="A"?r("selectInitial",a):bad());
 add("selectLast",a=>a==="T11"?z("backClear","Q1"):data(a)&&a!=="A"?r("selectLast",a):bad());
 // Move active boundary from end of selected vertex to its start.
 find("backClear",a=>a==="A",a=>z("backSet","S"));
 find("backSet",a=>a==="B",a=>z("backChosen","A"));
 find("backChosen",a=>a==="Q1",a=>r("backFirst","W"));
 add("backFirst",a=>a==="Z"?r("backFirst",a):a==="E0"||a==="E1"||a==="P"?z("backSource",a==="P"?"K2":"K"+a[1]):bad());
 find("backSource",a=>a==="A",a=>l("backStart",a));
 add("backStart",a=>a==="S"||a==="L"?r("backSrcFirst",a):a==="__"?bad():l("backStart",a));
 add("backSrcFirst",a=>T(a)?z("backEdge","C"+a.slice(1)):data(a)&&a!=="A"?r("backSrcFirst",a):bad());
 find("backEdge",K,a=>a==="K2"?z("backPick","P"):r("backNextEdge","E"+a[1]));
 add("backNextEdge",a=>a==="Z"?r("backNextEdge",a):a==="E0"||a==="E1"||a==="P"?z("backRestore",a==="P"?"K2":"K"+a[1]):bad());
 find("backRestore",C,a=>r("backNextSource","T"+a.slice(1)));
 add("backNextSource",a=>T(a)?z("backEdge","C"+a.slice(1)):data(a)&&a!=="A"?r("backNextSource",a):bad());
 find("backPick",a=>a==="C11",a=>z("backPrev","Q1"));
 find("backPrev",a=>a==="A",a=>l("backPrevStart","S"));
 add("backPrevStart",a=>a==="S"?z("backChosen","A"):a==="L"?r("backFinish",a):a==="__"?bad():l("backPrevStart",a));
 add("backFinish",a=>a==="Q1"?z("clean","W"):data(a)?r("backFinish",a):bad());
 add("clean",a=>a==="L"?r("readyAt","__"):a==="__"?bad():l("clean",a));
 add("readyAt",a=>data(a)?z("ready",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection,rules};
}
function encode(U,E){
 const b=v=>"0"+v;return U[0].map(b).join("")+"11"+E.map((e,i)=>U[i+1].map((u,c)=>b(u)+e.map(row=>b(row[c])).join("")+"10").join("")+"11").join("");
}
function logical(J,raw,limit=2000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a);trace.push([state,head,a]);if(trace.length>12)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}

function physical(M,raw,limit=20000000){
 let tape=new Map([...raw].map((v,i)=>[i,+v])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,forward=null,backward=null;
 const snap=()=>({head,tape:[...tape].sort((a,b)=>a[0]-b[0])});
 while(state!==M.q&&t<limit){
  let name=M.names[state];if(name==="read:lastBoundary:")forward=snap();if(name==="read:readyAt:")backward=snap();
  ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [q,w,d]=M.T[3*state+(tape.get(head)??2)];
  if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=q;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }
 return {tape,head,state,t,ph,logical,span:hi-lo+1,forward,backward};
}
function oracle(U,E){
 let best=null,a=[];
 function visit(i){
  if(i===U.length){if(!best||a.slice().reverse().some((v,j)=>v!==best[best.length-1-j]&&a.slice(a.length-j).every((x,k)=>x===best[best.length-j+k])&&v<best[best.length-1-j]))best=a.slice();return;}
  for(let b=0;b<U[i].length;b++)if(U[i][b]&&(i===0||E[i-1][a[i-1]][b])){a.push(b);visit(i+1);a.pop();}
 }
 // Enumerate in reverse coordinate order, using a separate full-predicate test.
 let z=Array(U.length).fill(0);
 function reverse(i){
  if(i<0){return U.every((u,j)=>u[z[j]])&&E.every((e,j)=>e[z[j]][z[j+1]])?z.slice():null;}
  for(let b=0;b<U[i].length;b++){z[i]=b;let r=reverse(i-1);if(r)return r;}return null;
 }
 return reverse(U.length-1);
}
function audit(){
 const J=worker(),M=compile(J.rules,J.symbols,J.projection),ok=(x,s)=>{if(!x)throw Error(s)},dec=new Map(Object.entries(M.code).map(([a,b])=>[b,a]));
 const counts={valid:0,sat:0,unsat:0,vertices:0,domainValues:0,edgeEntries:0,physical:0,logical:0,checkpoints:0,historyEntries:0,malformed:0,malformedTransitions:0,cutoffs:0};
 let digest=2166136261;
 function check(U,E,record=true){
  let raw=encode(U,E),N=raw.length,w=M.width,a=oracle(U,E),want=a?U.map((u,i)=>u.map((_,j)=>+(j===a[i])).join("")).join(""):null,H=U.reduce((x,u)=>x+u.length,0);
  let ref=logical(J,raw,20000000),r=physical(M,raw,30000000);
  ok(r.state===M.q&&ref.state===(a?"ready":"reject")&&r.logical===ref.t,"termination/reference "+JSON.stringify({U,E,ref,physical:r.t}));
  let prep=(w+1)*N*(N+1)+(w+4)*N+3,mid=(3*w-2)*ref.moves+(2*w-1)*(ref.t-ref.moves);
  ok(r.ph[0]===prep&&r.ph[1]===mid,"phase clock");
  let start=-w*N-1;
  function unpack(cp,left){
   ok(cp&&cp.tape.length===w*(N+1+left),"checkpoint size");
   let bits=cp.tape.map(x=>x[1]).join(""),symbols=Array.from({length:N+1+left},(_,i)=>dec.get(bits.slice(i*w,(i+1)*w)));
   ok(cp.tape.every(([pos],i)=>pos===start-left*w+i)&&symbols.at(-1)==="R"&&(!left||symbols[0]==="L"),"checkpoint layout");
   return symbols.slice(left);
  }
  let f=unpack(r.forward,1),expected=[],positions=[],msg=U[0].slice(),preds=0;
  function cell(v){expected.push("Z",v);}
  for(let b of U[0]){positions.push(expected.length+1);cell("T"+b+b);}cell(E.length?"S":"A");
  for(let i=0;i<E.length;i++){
   let next=[];
   for(let j=0;j<U[i+1].length;j++){
    let u=U[i+1][j],p=msg.findIndex((v,k)=>v&&u&&E[i][k][j]);next.push(+(p>=0));positions.push(expected.length+1);cell("T"+u+ +(p>=0));
    for(let k=0;k<msg.length;k++)cell(k===p?"P":"E"+E[i][k][j]);
    cell("D");preds+=+(p>=0);
   }
   msg=next;cell(i===E.length-1?"A":"S");
  }
  expected.push("R");ok(JSON.stringify(f)===JSON.stringify(expected),"forward tape");
  if(a){
   ok(r.tape.size===H&&[...want].every((v,i)=>r.tape.get(r.head+i)===+v)&&ref.out===want,"output");
   let b=unpack(r.backward,0),expectedBack=expected.slice();
   for(let i=0;i<N;i++)if(expectedBack[i]==="A")expectedBack[i]="S";
   if(E.length===0)expectedBack[expectedBack.length-2]="A";
   let offset=0;for(let i=0;i<U.length;i++){expectedBack[positions[offset+a[i]]]="W";offset+=U[i].length;}
   ok(JSON.stringify(b)===JSON.stringify(expectedBack),"backward tape "+JSON.stringify([b,expectedBack]));
   let body=0,c=0;
   for(let i=N-1;i>=0;i--){let emit=+positions.includes(i);body+=2*w*(i+1)+2*c+2*emit+4;c+=emit;}
   let serial=2*w*N+2*w+2+body+H+3;
   ok(r.ph[2]===serial&&r.head===-w*N-H-2,"output clock");
  }else ok(!r.tape.has(r.head)&&r.ph[2]===0&&!r.backward,"unsat");
  if(record){
   let out=a?Array.from({length:H},(_,i)=>r.tape.get(r.head+i)).join(""):"-";
   for(let ch of raw+":"+out+";")digest=Math.imul(digest^ch.charCodeAt(0),16777619)>>>0;
   counts.valid++;counts.sat+=+(!!a);counts.unsat+=+(!a);counts.vertices+=U.length;counts.domainValues+=H;counts.edgeEntries+=E.reduce((x,e)=>x+e.length*e[0].length,0);counts.physical+=r.t;counts.logical+=r.logical;counts.checkpoints+=1+ +(!!a);counts.historyEntries+=preds;
  }
  return r;
 }
 function bits(x,n){return Array.from({length:n},(_,i)=>(x>>i)&1);}
 for(let m=1;m<=5;m++)for(let x=0;x<2**m;x++)check([bits(x,m)],[]);
 for(let [m,n] of [[1,1],[1,2],[2,1],[2,2],[1,3],[3,1]])for(let x=0;x<2**(m+n+m*n);x++){
  let b=bits(x,m+n+m*n);check([b.slice(0,m),b.slice(m,m+n)],[Array.from({length:m},(_,i)=>b.slice(m+n+i*n,m+n+(i+1)*n))]);
 }
 let seed=0x52455811;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;};
 for(let i=0;i<40;i++){
  let n=3+i%3,sizes=Array.from({length:n},()=>1+(rand()>>>28)%4),U=sizes.map(m=>Array.from({length:m},()=>rand()>>>31)),E=sizes.slice(1).map((m,j)=>Array.from({length:sizes[j]},()=>Array.from({length:m},()=>rand()>>>31)));
  if(i%2){let a=sizes.map(m=>(rand()>>>16)%m);for(let j=0;j<n;j++)U[j][a[j]]=1;for(let j=0;j<n-1;j++)E[j][a[j]][a[j+1]]=1;}
  check(U,E);
 }
 check([[1,1],[1,1],[1,1]],[[[1,0],[0,0]],[[0,0],[0,1]]]);
 check([[0,1,0],[1,1,1,1],[1,1]],[[[0,0,0,0],[0,0,0,1],[0,0,0,0]],[[0,0],[0,0],[0,0],[0,1]]]);
 let malformed=[];
 for(let n=0;n<=5;n++)for(let x=0;x<2**n;x++){
  let raw=n?x.toString(2).padStart(n,"0"):"";
  if(raw!=="0011"&&raw!=="0111")malformed.push(raw);
 }
 // First domain has size 2, subsequent columns supply too few or too many rows.
 malformed.push("010111"+"01011011","010111"+"010101011011","011111","010111010110","0101110111");
 for(let raw of malformed){let r=physical(M,raw);ok(r.state===M.q&&!r.tape.has(r.head),"malformed "+raw);counts.malformed++;counts.malformedTransitions+=r.t;}
 let scaling=[];
 for(let m of [2,3,4,8,16]){
  let U=[Array(m).fill(1),Array(m).fill(1)],E=[Array.from({length:m},(_,i)=>Array.from({length:m},(_,j)=>+(i===m-1&&j===m-1)))],r=check(U,E,false);
  if(m<=8){ok(physical(M,encode(U,E),r.t-1).state!==M.q,"cutoff");counts.cutoffs++;}
  scaling.push([m,encode(U,E).length,r.t,r.logical,r.span,r.ph]);
 }
 let pos=3;while(M.desc[pos]==="1")pos++;ok(pos-3===M.q&&M.desc[pos++]==="0","header");let b=M.q.toString(2).length;
 for(let [q,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===q&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
 ok(pos===M.desc.length,"length");
 return {alphabet:J.symbols.length,width:M.width,logicalStates:new Set(J.rules.map(x=>x[0])).size,rules:J.rules.length,states:M.q,bits:M.desc.length,counts,scaling,digest};
}
if(process.argv.includes('--description')){let j=worker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_VARIABLE_DOMAIN_PATH_OK '+JSON.stringify(audit()));
