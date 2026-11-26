// REX-003 development worker, fixed sorted membership.
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

function joinWorker(){
 const symbols=["__","0_","1_","L","R","Z","qD0","qD1"];
 for(let side of ["f","q"])for(let b of side==="f"?["0","1","D","S"]:["0","1","D"])for(let m of ["n","s","c","b"])symbols.push(side+b+m);
 const projection={Z:"_",qD0:"0",qD1:"1"};
 for(let a of symbols)if(/^[fq][01DS][nscb]$/.test(a))projection[a]="_";
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error("duplicate "+s);defs.set(s,fn)};
 const next=(t,w,d=0)=>[t,w,d],keep=(t,a,d=0)=>next(t,a,d),reject=()=>next("reject","__");
 const tok=a=>/^[fq][01DS][nscb]$/.test(a),is=(a,side,mark)=>tok(a)&&a[0]===side&&mark.includes(a[2]);
 const start=a=>a.slice(0,2)+"s",both=a=>a.slice(0,2)+"b",uncur=a=>a.slice(0,2)+(a[2]==="b"?"s":"n"),unmark=a=>a.slice(0,2)+"n";
 function go(name,pred,act){
  add(name,a=>a==="L"?keep(name+"Scan",a,1):a==="__"?reject():keep(name,a,-1));
  add(name+"Scan",a=>pred(a)?act(a):a==="R"||a==="__"?reject():keep(name+"Scan",a,1));
 }
 add("init",a=>a==="0_"||a==="1_"?keep("left",a,-1):reject());
 add("left",a=>a==="__"?next("parsef0","L",1):reject());
 for(let side of ["f","q"])for(let inrec of [0,1]){
  add("parse"+side+inrec,a=>a==="0_"||a==="1_"?next("pair"+side+inrec+a[0],"Z",1):a==="__"&&side==="q"&&!inrec?next("firstF","R"):reject());
  for(let b of ["0","1"])add("pair"+side+inrec+b,a=>{
   if(a!=="0_"&&a!=="1_")return reject();
   let t=b+a[0];
   if(t==="11")return side==="f"&&!inrec?next("parseq0","fSn",1):reject();
   if(t==="10")return next("parse"+side+"0",side+"Dn",1);
   return next("parse"+side+"1",side+a[0]+"n",1);
  });
 }
 go("firstF",a=>is(a,"f","n"),a=>next("firstQ",start(a)));
 go("firstQ",a=>is(a,"q","n")||a==="R",a=>a==="R"?keep("clean",a,-1):next("beginF",start(a)));
 const rank={D:0,0:1,1:2,S:3};
 for(let b of ["0","1","D","S"]){
  function compare(a){
   let q=a[1];
   if(b===q&&b!=="D")return next("advanceQcur",uncur(a),1);
   let action=rank[b]<rank[q]?"F":b===q?"Q1":"Q0";
   return keep("reset"+action,a);
  }
  go("beginQ"+b,a=>is(a,"q","s"),a=>compare(both(a)));
  go("readQ"+b,a=>is(a,"q","cb"),compare);
 }
 go("beginF",a=>is(a,"f","s"),a=>next("beginQ"+a[1],both(a)));
 add("advanceQcur",a=>a==="Z"?keep("advanceQcur",a,1):is(a,"q","n")?next("findFcur",a.slice(0,2)+"c"):reject());
 go("findFcur",a=>is(a,"f","cb"),a=>next("advanceFcur",uncur(a),1));
 add("advanceFcur",a=>a==="Z"?keep("advanceFcur",a,1):is(a,"f","n")?next("readQ"+a[1],a.slice(0,2)+"c"):reject());
 for(let action of ["F","Q0","Q1"]){
  add("reset"+action,a=>a==="L"?keep("resetScan"+action,a,1):a==="__"?reject():keep("reset"+action,a,-1));
  add("resetScan"+action,a=>a==="R"?keep("find"+action,a):a==="__"?reject():tok(a)&&"cb".includes(a[2])?next("resetScan"+action,uncur(a),1):keep("resetScan"+action,a,1));
  let side=action==="F"?"f":"q";
  const advance=a=>a[1]==="D"?next("next"+action,side==="q"?"qD"+action[1]:unmark(a),1):next("through"+action,unmark(a),1);
  go("find"+action,a=>is(a,side,"s"),advance);
  add("through"+action,a=>a==="Z"?keep("through"+action,a,1):is(a,side,"n")?advance(a):reject());
  add("next"+action,a=>a==="Z"?keep("next"+action,a,1):is(a,side,"n")?next("beginF",start(a)):side==="q"&&a==="R"?keep("clean",a,-1):reject());
 }
 add("clean",a=>a==="L"?next("done","__",1):a==="__"?reject():tok(a)?next("clean",unmark(a),-1):keep("clean",a,-1));
 add("done",a=>keep("ready",a));
 const rules=[];
 for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection,rules};
}
function encode(f,q){return f.map(k=>[...k].map(b=>"0"+b).join("")+"10").join("")+"11"+q.map(k=>[...k].map(b=>"0"+b).join("")+"10").join("");}
function logicalRun(J,raw,limit=1000000){
 const T=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((b,i)=>[i,b+"_"]));let state="init",head=0,steps=0,trace=[];
 while(!["ready","reject"].includes(state)&&steps<limit){let a=tape.get(head)??"__",r=T.get(state+":"+a);if(!r)throw Error("missing "+state+":"+a);trace.push([state,head,a]);if(trace.length>20)trace.shift();let [s,w,d]=r;if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;state=s;steps++;}
 return {state,head,steps,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"").filter(x=>x==="0"||x==="1").join("")};
}

function physicalRun(M,raw,limit=20000000){
 let tape=new Map([...raw].map((b,i)=>[i,+b])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,trace=[];
 while(state!==M.q&&t<limit){
  let name=M.names[state];ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":")){logical++;trace.push([name,head]);if(trace.length>12)trace.shift();}
  let [s,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=s;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }
 return {tape,head,state,t,span:hi-lo+1,ph,logical,trace};
}

function audit(){
 const J=joinWorker(),M=compile(J.rules,J.symbols,J.projection),ok=(v,s)=>{if(!v)throw Error(s)};
 let counts={cases:0,queries:0,positive:0,transitions:0,logical:0,cutoffs:0,malformed:0,malformedTransitions:0};
 function check(f,q,record=true){
  let raw=encode(f,q),want=q.map(k=>+f.includes(k)),r=physicalRun(M,raw),N=raw.length,h=q.length,w=M.width;
  ok(r.state===M.q&&r.tape.size===want.length&&want.every((b,i)=>r.tape.get(r.head+i)===b)&&(!want.length?!r.tape.has(r.head):true),"join "+JSON.stringify({f,q,head:r.head,phase:r.ph,trace:r.trace}));
  let ref=logicalRun(J,raw,2000000);
  ok(ref.state==="ready"&&ref.out===want.join("")&&ref.steps===r.logical,"logical reference");
  let prep=(1+w)*N*(N+1)+(w+4)*N+3;
  // Original serializer generalized to w; there are N nonblank cells, with
  // one output at every query delimiter's second token bit.
  let emitted=0,body=0,marks=[];
  let pos=encode(f,[]).length;
  for(let k of q){pos+=2*k.length+2;marks.push(pos-1);}
  for(let i=N-1;i>=0;i--){let e=+marks.includes(i);body+=2*w*(i+1)+2*emitted+2*e+4;emitted+=e;}
  let serial=2*w*N+2*w+2+body+h+3;
  ok(r.ph[0]===prep&&r.ph[2]===serial,"physical phase clocks "+JSON.stringify({N,h,ph:r.ph,prep,serial}));
  ok(r.ph[1]<=(3*w-2)*r.logical&&r.ph[1]>=(2*w-1)*r.logical,"logical cost");
  if(record){counts.cases++;counts.queries+=q.length;counts.positive+=want.reduce((a,b)=>a+b,0);counts.transitions+=r.t;counts.logical+=r.logical;}
  return r;
 }
 const keys=["","0","00","01","1","10","11"];
 for(let mask=0;mask<128;mask++)check(keys.filter((_,i)=>mask>>i&1),keys.flatMap(k=>[k,k]));
 for(let [f,q] of [[[],[]],[[""],[]],[[],[""]],[["","0","0","01"],["","0","0","00","01","1"]],[["00000000000000000000000000000001","1"],["00000000000000000000000000000000","00000000000000000000000000000001","1"]]]){
  let r=check(f,q);ok(physicalRun(M,encode(f,q),r.t-1).state!==M.q,"cutoff");counts.cutoffs++;
 }
 for(let raw of ["","0","00","10","0011","1100","1111","110","00101100","1110100"]){
  let r=physicalRun(M,raw,200000);ok(r.state===M.q&&!r.tape.has(r.head),"malformed "+raw+" "+JSON.stringify(r.trace));counts.malformed++;counts.malformedTransitions+=r.t;
 }
 let unsorted=physicalRun(M,encode(["1","0"],["0"]));ok(unsorted.state===M.q&&unsorted.tape.get(unsorted.head)===0,"unsorted assumption counterexample");
 let scaling=[];
 for(let n of [4,8,16]){
  let k=Math.ceil(Math.log2(n*2)),f=Array.from({length:n},(_,i)=>(2*i).toString(2).padStart(k,"0")),q=Array.from({length:2*n},(_,i)=>i.toString(2).padStart(k,"0"));
  let r=check(f,q,false);scaling.push([n,encode(f,q).length,r.t,r.logical,r.span,r.ph]);
 }
 let pos=3;while(M.desc[pos]==="1")pos++;
 ok(pos-3===M.q&&M.desc[pos++]==="0","header");const b=M.q.toString(2).length;
 for(let [s,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===s&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
 ok(pos===M.desc.length,"descriptor length");
 return {alphabet:J.symbols.length,logicalStates:new Set(J.rules.map(r=>r[0])).size,logicalRules:J.rules.length,width:M.width,states:M.q,bits:M.desc.length,counts,scaling,unsortedCounterexample:true};
}
if(process.argv.includes('--description')){let j=joinWorker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_FACTOR_MEMBERSHIP_OK '+JSON.stringify(audit()));
