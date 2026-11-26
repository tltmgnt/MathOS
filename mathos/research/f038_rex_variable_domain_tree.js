// REX-013: variable-rank ordered tree worker, physical rectangular alignment and nested stack.
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
 const symbols=["__","0_","1_","L","R","Z","A","F","X","D","J","S","E0","E1","P","T00","T10","T11","B","H","Q00","Q10","Q11","QW","C00","C10","C11","CW","K0","K1","KP","V","G","Y","W","M","I","C"];
 const projection=Object.fromEntries(symbols.filter(x=>x!=="__").map(x=>[x,x==="W"?"1":/^T/.test(x)?"0":"_"]));
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error(s);defs.set(s,fn)};
 const go=(s,w,d=0)=>[s,w,d],r=(s,a)=>go(s,a,1),l=(s,a)=>go(s,a,-1),z=(s,a)=>go(s,a),bad=()=>z("reject","__"),raw=a=>a==="0_"||a==="1_",data=a=>a!=="__"&&a!=="L"&&a!=="R",T=a=>/^T(00|10|11)$/.test(a),Q=a=>/^Q(00|10|11|W)$/.test(a),C=a=>/^C(00|10|11|W)$/.test(a),K=a=>/^K[01P]$/.test(a),edge=a=>/^E[01]$/.test(a)||a==="P";
 const tag=(a,p)=>a==="W"?p+"W":p+a.slice(1),restore=a=>a.endsWith("W")?"W":"T"+a.slice(1),ek=a=>a==="P"?"KP":"K"+a[1],er=a=>a==="KP"?"P":"E"+a[1];
 function find(s,pred,act){
  add(s,a=>a==="L"?r(s+"Scan",a):a==="__"?bad():l(s,a));
  add(s+"Scan",a=>pred(a)?act(a):data(a)?r(s+"Scan",a):bad());
 }
 add("init",a=>a==="1_"?l("left",a):bad());
 add("left",a=>a==="__"?r("token","L"):bad());
 add("token",a=>a==="1_"?r("tag","Z"):bad());
 add("tag",a=>a==="0_"?r("unaryFirst","A"):a==="1_"?l("closeSeek","X"):bad());
 add("unaryFirst",a=>a==="0_"?r("unaryBit","Z"):bad());
 add("unaryBit",a=>raw(a)?r("unaryNext","T"+a[0]+a[0]):bad());
 add("unaryNext",a=>a==="0_"?r("unaryBit","Z"):a==="1_"?r("unaryEnd","Z"):bad());
 add("unaryEnd",a=>a==="1_"?r("edgeStart","D"):bad());
 add("edgeStart",a=>a==="0_"?r("edgeBit","Z"):a==="1_"?r("edgeEnd","Z"):bad());
 add("edgeBit",a=>raw(a)?r("edgeNext","E"+a[0]):bad());
 add("edgeNext",a=>a==="0_"?r("edgeBit","Z"):a==="1_"?r("colEnd","Z"):bad());
 add("colEnd",a=>a==="0_"?r("edgeStart","J"):bad());
 add("edgeEnd",a=>a==="1_"?r("token","S"):bad());
 add("closeSeek",a=>a==="A"?l("parent","H"):data(a)?l("closeSeek",a):bad());
 add("parent",a=>a==="A"?r("fParentFirst","B"):a==="L"?r("rootFind",a):data(a)?l("parent",a):bad());
 add("rootFind",a=>a==="H"?r("rootHeader","F"):data(a)?r("rootFind",a):bad());
 add("rootHeader",a=>a==="D"?r("rootEdgeZ",a):data(a)?r("rootHeader",a):bad());
 add("rootEdgeZ",a=>a==="Z"?r("rootEdgeEnd",a):bad());
 add("rootEdgeEnd",a=>a==="S"?r("rootClose",a):bad());
 add("rootClose",a=>a==="X"?r("endCheck","C"):data(a)?r("rootClose",a):bad());
 add("endCheck",a=>a==="__"?l("rootRewind","R"):bad());
 add("rootRewind",a=>a==="L"?r("rootOpen",a):data(a)?l("rootRewind",a):bad());
 add("rootOpen",a=>a==="Z"?r("rootTag",a):bad());
 add("rootTag",a=>a==="F"?r("rootChoose","V"):bad());
 add("rootChoose",a=>a==="T11"?r("backScan","W"):a==="Z"||T(a)?r("rootChoose",a):bad());
 add("backScan",a=>a==="F"?l("backParent","H"):a==="C"?l("pop","Y"):a==="R"?l("clean",a):data(a)?r("backScan",a):bad());
 add("backParent",a=>a==="V"?r("bParentFirst","B"):data(a)?l("backParent",a):bad());
 add("pop",a=>a==="V"?r("popResume","G"):data(a)?l("pop",a):bad());
 add("popResume",a=>a==="Y"?r("backScan","C"):data(a)?r("popResume",a):bad());
 add("clean",a=>a==="L"?r("readyAt","__"):data(a)&&!["V","H","B"].includes(a)?l("clean",a):bad());
 add("readyAt",a=>a==="Z"?z("ready",a):bad());
 for(let m of ["f","b"]){
  const p=m,eligible=a=>T(a)||m==="b"&&a==="W";
  add(p+"ParentFirst",a=>a==="Z"?r(p+"ParentVal",a):bad());
  add(p+"ParentVal",a=>eligible(a)?z(p+"ChildStart",tag(a,"Q")):bad());
  find(p+"ChildStart",a=>a==="H",a=>r(p+"ChildHeader",a));
  add(p+"ChildHeader",a=>a==="D"?r(p+"EdgeZ",a):a==="Z"||T(a)?r(p+"ChildHeader",a):bad());
  add(p+"EdgeZ",a=>a==="Z"?r(p+"EdgeFirst",a):bad());
  add(p+"EdgeFirst",a=>edge(a)?z(p+"Select",ek(a)):bad());
  find(p+"Select",Q,a=>z(p+"Source"+(m==="b"&&a==="QW"?1:0),a));
  for(let sel of [0,1]){
   let h=p+sel;
   find(p+"Source"+sel,a=>a==="H",a=>r(h+"SrcZ",a));
   add(h+"SrcZ",a=>a==="Z"?r(h+"SrcVal",a):bad());
   add(h+"SrcVal",a=>eligible(a)?z(h+"Read0",tag(a,"C")):bad());
   for(let hit of [0,1]){
    let g=h+hit;
    find(h+"Read"+hit,C,a=>z(g+"Edge"+ +(a==="C11"||a==="CW"),a));
    for(let feasible of [0,1]){
     find(g+"Edge"+feasible,K,a=>{
      let yes=m==="f"?(!hit&&feasible&&a==="K1"):(sel&&!hit&&feasible&&a==="KP");
      if(m==="b"&&yes)return z(g+"Pick","I");
      return r(h+"NextEdge"+ +(hit||yes),yes?"P":er(a));
     });
    }
    if(m==="b"){
     find(g+"Pick",a=>a==="C11",a=>z(g+"ResumePick","CW"));
     find(g+"ResumePick",a=>a==="I",a=>r(h+"NextEdge1","P"));
    }
    add(h+"NextEdge"+hit,a=>a==="Z"?r(g+"EdgeVal",a):bad());
    add(g+"EdgeVal",a=>edge(a)?z(g+"Restore0",ek(a)):a==="J"?z(g+"Restore1","M"):bad());
    for(let end of [0,1]){
     find(g+"Restore"+end,C,a=>r(g+"SrcNextZ"+end,restore(a)));
     add(g+"SrcNextZ"+end,a=>a==="Z"?r(g+"SrcNextVal"+end,a):bad());
     add(g+"SrcNextVal"+end,a=>eligible(a)?end?bad():z(h+"Read"+hit,tag(a,"C")):a==="D"?end?(m==="b"&&sel&&!hit?bad():z(g+"Update",a)):bad():bad());
    }
    find(g+"Update",Q,a=>m==="f"&&a==="QW"?bad():r(p+"NextParentZ",m==="f"?"T"+a[1]+(+a[2]&hit):restore(a)));
   }
  }
  add(p+"NextParentZ",a=>a==="Z"?r(p+"NextParentVal",a):bad());
  add(p+"NextParentVal",a=>eligible(a)?z(p+"FindCol0",tag(a,"Q")):a==="D"?z(p+"FindCol1",a):bad());
  for(let end of [0,1]){
   find(p+"FindCol"+end,a=>a==="M",a=>r(p+"ColZ"+end,"J"));
   add(p+"ColZ"+end,a=>a==="Z"?r(p+"ColVal"+end,a):bad());
   add(p+"ColVal"+end,a=>edge(a)?end?bad():z(p+"Select",ek(a)):a==="S"?end?z(p+"RestoreParent",a):bad():bad());
  }
  find(p+"RestoreParent",a=>a==="B",a=>z(p+"RestoreChild",m==="f"?"A":"V"));
  find(p+"RestoreChild",a=>a==="H",a=>r(m==="f"?"resume":"backScan",m==="f"?"F":"V"));
 }
 add("resume",a=>a==="X"?r("token","C"):data(a)?r("resume",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection,rules};
}
function encode(t){let b=x=>"0"+x;return "10"+t.u.map(b).join("")+"11"+t.e.map(c=>c.map(b).join("")+"10").join("")+"11"+t.children.map(encode).join("")+"11";}
function logical(J,raw,limit=2000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let row=rules.get(state+":"+a);if(!row)throw Error(state+":"+a);let [s,w,d]=row;trace.push([state,head,a]);if(trace.length>16)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}

function physical(M,raw,limit=40000000){
 let tape=new Map([...raw].map((v,i)=>[i,+v])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,forward=null,backward=null;
 const snap=()=>({head,tape:[...tape].sort((a,b)=>a[0]-b[0])});
 while(state!==M.q&&t<limit){
  let name=M.names[state];if(name==="read:rootRewind:")forward=snap();if(name==="read:readyAt:")backward=snap();
  ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [q,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=q;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }return {tape,head,state,t,ph,logical,span:hi-lo+1,forward,backward};
}
function flatten(t){let nodes=[];function visit(t,p){let i=nodes.length;nodes.push({u:t.u,e:t.e,p});for(let c of t.children)visit(c,i);}visit(t,-1);return nodes;}
function oracle(t){
 let nodes=flatten(t),a=[];
 function search(i){
  if(i===nodes.length)return a.slice();
  let v=nodes[i];for(let j=0;j<v.u.length;j++)if(v.u[j]&&(v.p<0||v.e[a[v.p]][j])){a.push(j);let r=search(i+1);if(r)return r;a.pop();}return null;
 }return search(0);
}
function audit(){
 const J=worker(),M=compile(J.rules,J.symbols,J.projection),ok=(x,s)=>{if(!x)throw Error(s)},dec=new Map(Object.entries(M.code).map(([a,b])=>[b,a]));
 let counts={valid:0,sat:0,unsat:0,nodes:0,branching:0,domainValues:0,edgeEntries:0,physical:0,logical:0,checkpoints:0,messageEntries:0,predecessors:0,malformed:0,malformedTransitions:0,cutoffs:0};
 let digest=2166136261;
 function check(t,record=true){
  let raw=encode(t),N=raw.length,w=M.width,nodes=flatten(t),a=oracle(t),H=nodes.reduce((x,v)=>x+v.u.length,0),want=a?nodes.map((v,i)=>v.u.map((_,j)=>+(j===a[i])).join("")).join(""):null;
  let ref=logical(J,raw,30000000),r=physical(M,raw);
  ok(r.state===M.q&&ref.state===(a?"ready":"reject")&&r.logical===ref.t,"termination "+JSON.stringify({raw,ref,t:r.t}));
  let prep=(w+1)*N*(N+1)+(w+4)*N+3,mid=(3*w-2)*ref.moves+(2*w-1)*(ref.t-ref.moves);
  ok(r.ph[0]===prep&&r.ph[1]===mid,"phase clocks");
  let start=-w*N-1;
  function unpack(cp,left){
   ok(cp&&cp.tape.length===w*(N+1+left),"checkpoint size");let bits=cp.tape.map(x=>x[1]).join(""),v=Array.from({length:N+1+left},(_,i)=>dec.get(bits.slice(i*w,(i+1)*w)));
   ok(cp.tape.every(([pos],i)=>pos===start-left*w+i)&&v.at(-1)==="R"&&(!left||v[0]==="L"),"checkpoint layout");return v.slice(left);
  }
  function msg(t){return t.u.map((u,b)=>+(u&&t.children.every(c=>msg(c).some((m,j)=>m&&c.e[b][j]))));}
  let expected=[],positions=[],openings=[],preds=0,selected=[],idx=0;
  function node(t){
   let m=msg(t),i=idx++;openings.push(expected.length+1);expected.push("Z","F");
   for(let j=0;j<t.u.length;j++){positions.push(expected.length+1);if(a&&j===a[i])selected.push(expected.length+1);expected.push("Z","T"+t.u[j]+m[j]);}
   expected.push("Z","D");
   for(let col of t.e){
    let p=m.findIndex((v,j)=>v&&col[j]);preds+=+(p>=0);
    for(let j=0;j<col.length;j++)expected.push("Z",j===p?"P":"E"+col[j]);expected.push("Z","J");
   }expected.push("Z","S");for(let c of t.children)node(c);expected.push("Z","C");
  }
  node(t);expected.push("R");
  ok(JSON.stringify(unpack(r.forward,1))===JSON.stringify(expected),"forward checkpoint "+raw);
  if(a){
   ok(r.tape.size===H&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b)&&ref.out===want,"physical output "+raw);
   let b=expected.slice();for(let i of openings)b[i]="G";for(let i of selected)b[i]="W";
   ok(JSON.stringify(unpack(r.backward,0))===JSON.stringify(b),"backward checkpoint "+raw);
   let body=0,c=0,p=new Set(positions);
   for(let i=N-1;i>=0;i--){let e=+p.has(i);body+=2*w*(i+1)+2*c+2*e+4;c+=e;}
   ok(r.ph[2]===2*w*N+2*w+2+body+H+3&&r.head===-w*N-H-2,"serializer");
  }else ok(!r.tape.has(r.head)&&r.ph[2]===0&&!r.backward,"rejection");
  if(record){
   let out=a?Array.from({length:H},(_,i)=>r.tape.get(r.head+i)).join(""):"-";for(let ch of raw+":"+out+";")digest=Math.imul(digest^ch.charCodeAt(0),16777619)>>>0;
   counts.valid++;counts.sat+=+(!!a);counts.unsat+=+(!a);counts.nodes+=nodes.length;counts.branching+=+(nodes.some((_,i)=>nodes.filter(v=>v.p===i).length>1));counts.domainValues+=H;counts.edgeEntries+=nodes.reduce((x,v)=>x+v.e.reduce((y,c)=>y+c.length,0),0);counts.physical+=r.t;counts.logical+=r.logical;counts.checkpoints+=1+ +(!!a);counts.messageEntries+=H;counts.predecessors+=preds;
  }return r;
 }
 const bits=(x,n)=>Array.from({length:n},(_,i)=>(x>>i)&1),leaf=(u,e)=>({u,e,children:[]}),root=(u,children)=>({u,e:[],children});
 for(let m=1;m<=4;m++)for(let x=0;x<2**m;x++)check(root(bits(x,m),[]));
 for(let [m,n] of [[1,1],[1,2],[2,1],[1,3],[3,1],[2,2]])for(let x=0;x<2**(m+n+m*n);x++){
  let b=bits(x,m+n+m*n);check(root(b.slice(0,m),[leaf(b.slice(m,m+n),Array.from({length:m},(_,j)=>b.slice(m+n+j*n,m+n+(j+1)*n)))]));
 }
 // All child-message combinations at a three-rank parent, with singleton children.
 for(let x=0;x<8;x++)for(let y=0;y<8;y++)check(root([1,1,1],[leaf([1],bits(x,3).map(b=>[b])),leaf([1],bits(y,3).map(b=>[b]))]));
 let seed=0x52455813;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<32;i++){
  let n=3+i%4,nodes=[],parents=[-1];
  for(let j=0;j<n;j++){
   let d=1+(rand()>>>28)%3,u=Array.from({length:d},()=>rand()>>>31),p=j?(rand()>>>16)%j:-1; if(j)parents.push(p);
   let e=p<0?[]:nodes[p].u.map(()=>Array.from({length:d},()=>rand()>>>31));nodes.push(leaf(u,e));if(j)nodes[p].children.push(nodes[j]);
  }
  if(i%2){let a=nodes.map(v=>(rand()>>>16)%v.u.length);for(let j=0;j<n;j++){nodes[j].u[a[j]]=1;if(j)nodes[j].e[a[parents[j]]][a[j]]=1;}}
  check(nodes[0]);
 }
 check(root([1,1],[leaf([1],[[1],[0]]),leaf([1],[[0],[1]])]));
 check(root([1,1,1],[{u:[1,1],e:[[0,0],[0,0],[0,1]],children:[leaf([0,0,1],[[0,0,0],[0,0,1]])]},leaf([1],[[0],[0],[1]])]));
 let malformed=[];for(let n=0;n<=5;n++)for(let x=0;x<2**n;x++)malformed.push(n?x.toString(2).padStart(n,"0"):"");
 let good=encode(root([1],[]));malformed.push(good.slice(0,-1),good.slice(0,-2),good+good,good+"0",encode(leaf([1],[[1]])),encode(root([1],[leaf([1],[])])),encode(root([1],[leaf([1],[[1,0]])])),encode(root([1],[leaf([1,1],[[1]])])),encode(root([1,1],[leaf([1],[[1]])])),encode(root([1],[leaf([1],[[1],[1]])])),encode(root([],[])),encode(root([0],[leaf([0,0],[[0]])])));
 for(let raw of malformed){let r=physical(M,raw);ok(r.state===M.q&&!r.tape.has(r.head),"malformed "+raw);counts.malformed++;counts.malformedTransitions+=r.t;}
 let scaling=[];
 for(let m of [2,3,4,8]){
  let u=Array(m).fill(1),e=Array.from({length:m},(_,j)=>Array.from({length:m},(_,k)=>+(j===m-1&&k===m-1))),t=root(u,[leaf(u,e),leaf(u,e)]),r=check(t,false);
  if(m<=4){ok(physical(M,encode(t),r.t-1).state!==M.q,"cutoff");counts.cutoffs++;}
  scaling.push([m,encode(t).length,r.t,r.logical,r.span,r.ph]);
 }
 let pos=3;while(M.desc[pos]==="1")pos++;ok(pos-3===M.q&&M.desc[pos++]==="0","descriptor header");let b=M.q.toString(2).length;
 for(let [q,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===q&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
 ok(pos===M.desc.length,"descriptor length");return {alphabet:J.symbols.length,width:M.width,logicalStates:new Set(J.rules.map(x=>x[0])).size,rules:J.rules.length,states:M.q,bits:M.desc.length,counts,scaling,digest};
}
if(process.argv.includes('--description')){let j=worker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_VARIABLE_DOMAIN_TREE_OK '+JSON.stringify(audit()));
