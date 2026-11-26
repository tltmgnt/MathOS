// REX-012 fixed Boolean rooted ordered tree worker, persistent child-message conjunction and witness recovery.
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





function treeWorker(){
 const symbols=["__","0_","1_","L","R","Z","A","F","X","C","H","V0","V1","W0","W1","Y","T00","T10","T11","E0","E1"];
 const projection=Object.fromEntries(symbols.filter(x=>x!=="__").map(x=>[x,x==="W0"?"0":x==="W1"?"1":"_"]));
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error(s);defs.set(s,fn)};
 const go=(s,w,d=0)=>[s,w,d],r=(s,a)=>go(s,a,1),l=(s,a)=>go(s,a,-1),z=(s,a)=>go(s,a),bad=()=>z("reject","__"),raw=a=>a==="0_"||a==="1_",data=a=>a!=="__"&&a!=="L"&&a!=="R",T=a=>/^T(00|10|11)$/.test(a);
 add("init",a=>a==="1_"?l("left",a):bad());
 add("left",a=>a==="__"?r("token","L"):bad());
 add("token",a=>a==="1_"?r("tag","Z"):bad());
 add("tag",a=>a==="0_"?r("header0","A"):a==="1_"?l("closeSeek","X"):bad());
 for(let j=0;j<6;j++){
  add("header"+j,a=>a==="0_"?r("value"+j,"Z"):bad());
  add("value"+j,a=>raw(a)?r(j===5?"token":"header"+(j+1),j<2?"T"+a[0]+a[0]:"E"+a[0]):bad());
 }
 add("closeSeek",a=>a==="A"?r("readf0","A"):data(a)?l("closeSeek",a):bad());
 // Read final feasibility and original edge in fixed finite control.
 // Only six bits are held, independently of tree size.
 for(let mode of ["f","b0","b1","root"]){
  for(let j=0;j<6;j++)for(let x=0;x<2**j;x++){
   let bits=j?x.toString(2).padStart(j,"0"):"",name=mode+j+bits;
   add("read"+name,a=>a==="Z"?r("digit"+name,a):bad());
   add("digit"+name,a=>{
    if(j<2?!T(a):!/^E[01]$/.test(a))return bad();
    let b=a.at(-1),next=bits+b;
    if(j<5)return r("read"+mode+(j+1)+next,a);
    let m=next.slice(0,2).split("").map(Number),e=next.slice(2).split("").map(Number);
    if(mode==="f"){
     let p=[0,1].map(k=>+(m[0]&&e[k]||m[1]&&e[2+k]));
     return l("finish"+p.join(""),a);
    }
    let pick=mode==="root"?m.findIndex(Boolean):m.findIndex((v,k)=>v&&e[2*k+Number(mode[1])]);
    return pick<0?bad():l("choose"+pick,a);
   });
  }
 }
 for(let p of ["00","01","10","11"]){
  add("finish"+p,a=>a==="A"?l("parent"+p,"F"):data(a)?l("finish"+p,a):bad());
  add("parent"+p,a=>a==="A"?r("upFirst"+p,a):a==="L"?r("rootEnd",a):data(a)?l("parent"+p,a):bad());
  add("upFirst"+p,a=>a==="Z"?r("upValue"+p,a):bad());
  add("upValue"+p,a=>T(a)?r("upSecond"+p,"T"+a[1]+(+a[2]&+p[0])):bad());
  add("upSecond"+p,a=>a==="Z"?r("upValue2"+p,a):bad());
  add("upValue2"+p,a=>T(a)?r("resume","T"+a[1]+(+a[2]&+p[1])):bad());
 }
 add("resume",a=>a==="X"?r("token","C"):data(a)?r("resume",a):bad());
 add("rootEnd",a=>a==="X"?r("endCheck","C"):data(a)?r("rootEnd",a):bad());
 add("endCheck",a=>a==="__"?l("rootRewind","R"):bad());
 add("rootRewind",a=>a==="L"?r("rootOpen",a):data(a)?l("rootRewind",a):bad());
 add("rootOpen",a=>a==="Z"?r("rootTag",a):bad());
 add("rootTag",a=>a==="F"?r("readroot0","H"):bad());
 for(let b of [0,1]){
  add("choose"+b,a=>a==="H"?r("backScan","V"+b):data(a)?l("choose"+b,a):bad());
  add("seekChild"+b,a=>a==="H"?r("readb"+b+"0",a):data(a)?r("seekChild"+b,a):bad());
 }
 add("backScan",a=>a==="F"?l("seekChosenParent","H"):a==="C"?l("pop","Y"):a==="R"?l("cleanup",a):data(a)?r("backScan",a):bad());
 add("seekChosenParent",a=>a==="V0"||a==="V1"?r("seekChild"+a[1],a):data(a)?l("seekChosenParent",a):bad());
 add("pop",a=>a==="V0"||a==="V1"?r("popResume","W"+a[1]):data(a)?l("pop",a):bad());
 add("popResume",a=>a==="Y"?r("backScan","C"):data(a)?r("popResume",a):bad());
 add("cleanup",a=>a==="L"?r("readyAt","__"):data(a)&&!/^V|^H$/.test(a)?l("cleanup",a):bad());
 add("readyAt",a=>a==="Z"?z("ready",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection,rules};
}
function encode(t){return "10"+[...t.u,...t.e].map(b=>"0"+b).join("")+t.children.map(encode).join("")+"11";}
function logical(J,raw,limit=2000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a);trace.push([state,head,a]);if(trace.length>12)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}

function physical(M,raw,limit=30000000){
 let tape=new Map([...raw].map((v,i)=>[i,+v])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,forward=null,backward=null;
 const snap=()=>({head,tape:[...tape].sort((a,b)=>a[0]-b[0])});
 while(state!==M.q&&t<limit){
  let name=M.names[state];if(name==="read:rootRewind:")forward=snap();if(name==="read:readyAt:")backward=snap();
  ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [q,w,d]=M.T[3*state+(tape.get(head)??2)];
  if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=q;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }
 return {tape,head,state,t,ph,logical,span:hi-lo+1,forward,backward};
}
function flatten(t){let nodes=[];function visit(t,p){let i=nodes.length;nodes.push({u:t.u,e:t.e,p});for(let c of t.children)visit(c,i);}visit(t,-1);return nodes;}
function oracle(t){
 let nodes=flatten(t),n=nodes.length;
 for(let i=0;i<2**n;i++){let bits=i.toString(2).padStart(n,"0").split("").map(Number);
  if(nodes.every((v,j)=>v.u[bits[j]]&&(v.p===-1||v.e[2*bits[j]+bits[v.p]])))return bits.join("");
 }return null;
}
function audit(){
 const J=treeWorker(),M=compile(J.rules,J.symbols,J.projection),ok=(v,s)=>{if(!v)throw Error(s)},dec=new Map(Object.entries(M.code).map(([a,b])=>[b,a]));
 const counts={valid:0,sat:0,unsat:0,nodes:0,branches:0,physical:0,logical:0,checkpoints:0,messageEntries:0,malformed:0,malformedTransitions:0,cutoffs:0};let digest=2166136261;
 function check(t,record=true,known=undefined){
  let raw=encode(t),N=raw.length,w=M.width,n=N/16,want=known===undefined?oracle(t):known,ref=logical(J,raw),r=physical(M,raw);
  ok(r.state===M.q&&ref.state===(want===null?"reject":"ready")&&r.logical===ref.t,"termination "+JSON.stringify({raw,ref,t:r.t}));
  let prep=(w+1)*N*(N+1)+(w+4)*N+3,mid=(3*w-2)*ref.moves+(2*w-1)*(ref.t-ref.moves);
  ok(r.ph[0]===prep&&r.ph[1]===mid,"phase clocks");
  let start=-w*N-1;
  function unpack(cp,left){
   ok(cp&&cp.tape.length===w*(N+1+left),"checkpoint size");
   let bits=cp.tape.map(x=>x[1]).join(""),a=Array.from({length:N+1+left},(_,i)=>dec.get(bits.slice(i*w,(i+1)*w)));
   ok(cp.tape.every(([pos],i)=>pos===start-left*w+i)&&a.at(-1)==="R"&&(!left||a[0]==="L"),"checkpoint layout");
   return a.slice(left);
  }
  let expected=[],positions=[];
  function expectedNode(t){
   let m=t.u.map((u,b)=>+(u&&t.children.every(c=>{let a=message(c);return a[0]&&c.e[b]||a[1]&&c.e[2+b];})));
   positions.push(expected.length+1);expected.push("Z","F","Z","T"+t.u[0]+m[0],"Z","T"+t.u[1]+m[1]);
   for(let e of t.e)expected.push("Z","E"+e);
   for(let c of t.children)expectedNode(c);
   expected.push("Z","C");
  }
  function message(t){return t.u.map((u,b)=>+(u&&t.children.every(c=>{let a=message(c);return a[0]&&c.e[b]||a[1]&&c.e[2+b];})));}
  expectedNode(t);expected.push("R");
  ok(JSON.stringify(unpack(r.forward,1))===JSON.stringify(expected),"forward messages and factor preservation");
  if(want!==null){
   ok(r.tape.size===n&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b)&&ref.out===want,"output "+raw);
   let back=expected.slice();for(let i=0;i<n;i++)back[positions[i]]="W"+want[i];
   ok(JSON.stringify(unpack(r.backward,0))===JSON.stringify(back),"backward checkpoint");
   let body=0,c=0,p=new Set(positions);
   for(let i=N-1;i>=0;i--){let emit=+p.has(i);body+=2*w*(i+1)+2*c+2*emit+4;c+=emit;}
   ok(r.ph[2]===2*w*N+2*w+2+body+n+3&&r.head===-w*N-n-2,"serializer");
  }else ok(!r.tape.has(r.head)&&r.ph[2]===0&&!r.backward,"rejection");
  if(record){
   let actual=want===null?"-":Array.from({length:n},(_,i)=>r.tape.get(r.head+i)).join("");
   for(let ch of raw+":"+actual+";")digest=Math.imul(digest^ch.charCodeAt(0),16777619)>>>0;
   counts.valid++;counts.sat+=+(want!==null);counts.unsat+=+(want===null);counts.nodes+=n;counts.branches+=+(flatten(t).some((_,i,a)=>a.filter(x=>x.p===i).length>=2));counts.physical+=r.t;counts.logical+=r.logical;counts.checkpoints+=1+ +(want!==null);counts.messageEntries+=2*n;
  }
  return r;
 }
 const bits=(x,n)=>Array.from({length:n},(_,i)=>(x>>i)&1),leaf=(u,e)=>({u,e,children:[]}),root=(u,children)=>({u,e:[1,1,1,1],children});
 for(let u=0;u<4;u++)check(root(bits(u,2),[]));
 for(let u=0;u<4;u++)for(let v=0;v<4;v++)for(let e=0;e<16;e++)check(root(bits(u,2),[leaf(bits(v,2),bits(e,4))]));
 for(let a=0;a<16;a++)for(let b=0;b<16;b++)check(root([1,1],[leaf([1,1],bits(a,4)),leaf([1,1],bits(b,4))]));
 let seed=0x52455812;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<64;i++){
  let n=3+i%6,nodes=Array.from({length:n},()=>leaf(bits(rand()>>>16,2),bits(rand()>>>16,4))),parents=[-1];
  for(let j=1;j<n;j++){let p=(rand()>>>16)%j;parents.push(p);nodes[p].children.push(nodes[j]);}
  if(i%2){let a=nodes.map(()=>rand()>>>31);for(let j=0;j<n;j++){nodes[j].u[a[j]]=1;if(j)nodes[j].e[2*a[j]+a[parents[j]]]=1;}}
  check(nodes[0]);
 }
 let conflict=root([1,1],[leaf([1,0],[1,0,0,0]),leaf([0,1],[0,0,0,1])]),forced=root([1,1],[leaf([1,0],[0,1,0,0]),leaf([0,1],[0,0,0,1])]);
 ok(oracle(conflict)===null&&oracle(forced)==="101","adversarial oracle");check(conflict);check(forced);
 let malformed=[];for(let n=0;n<=6;n++)for(let x=0;x<2**n;x++)malformed.push(n?x.toString(2).padStart(n,"0"):"");
 let good=encode(root([1,1],[]));malformed.push(good.slice(0,-1),good.slice(0,-2),good+"0",good+good,"11"+good,good.slice(0,2)+"10"+good.slice(4),good.slice(0,-2)+good,encode(forced).slice(0,-2));
 for(let raw of malformed){let r=physical(M,raw);ok(r.state===M.q&&!r.tape.has(r.head),"malformed "+raw);counts.malformed++;counts.malformedTransitions+=r.t;}
 let scaling=[];
 for(let n of [2,4,8,16,32]){
  for(let shape of ["star","chain"]){
   let nodes=Array.from({length:n},()=>leaf([0,1],[0,0,0,1]));for(let j=1;j<n;j++)nodes[shape==="star"?0:j-1].children.push(nodes[j]);
   let r=check(nodes[0],false,"1".repeat(n));if(n<=8){ok(physical(M,encode(nodes[0]),r.t-1).state!==M.q,"cutoff");counts.cutoffs++;}
   scaling.push([shape,n,16*n,r.t,r.logical,r.span,r.ph]);
  }
 }
 let pos=3;while(M.desc[pos]==="1")pos++;ok(pos-3===M.q&&M.desc[pos++]==="0","header");let b=M.q.toString(2).length;
 for(let [q,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===q&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
 ok(pos===M.desc.length,"length");
 return {alphabet:J.symbols.length,width:M.width,logicalStates:new Set(J.rules.map(x=>x[0])).size,rules:J.rules.length,states:M.q,bits:M.desc.length,counts,scaling,digest};
}
if(process.argv.includes('--description')){let j=treeWorker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_BRANCHING_TREE_OK '+JSON.stringify(audit()));
