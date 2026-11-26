// REX-010 fixed persistent Boolean path solver; compact raw factor tables, no supplied membership flags.
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



function pathWorker(){
 // Input: unary mask for vertex 0, then [edge00,edge01,edge10,edge11,unary0,unary1] for every next vertex.
 const symbols=["__","0_","1_","R","I0","I1","B0","B1"];
 const projection={"0_":"_","1_":"_",I0:"_",I1:"_",B0:"_",B1:"_"};
 for(let u of [0,1]){
  for(let x of [0,1]){symbols.push("W"+u+x);projection["W"+u+x]=String(x);}
  for(let p of [0,1,2]){
   let a="T"+u+p;symbols.push(a);projection[a]="_";
   for(let x of [0,1]){let w="O"+u+p+x;symbols.push(w);projection[w]=String(x);}
  }
 }
 const rules=[],defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error(s);defs.set(s,fn)};
 const raw=a=>a==="0_"||a==="1_",bit=a=>+a[0],go=(s,w,d=1)=>[s,w,d],bad=()=>go("reject","__",0);
 add("init",a=>raw(a)?go("initial"+bit(a),"I"+bit(a)):bad());
 for(let p of [0,1])add("initial"+p,a=>raw(a)?go("edge"+p+bit(a),"B"+bit(a)):bad());
 const pred=(p,q,e0,e1)=>p&&e0?0:q&&e1?1:2;
 for(let p of [0,1])for(let q of [0,1]){
  let prefix="edge"+p+q;
  // Each edge accumulates only four relation bits in finite control.
  // At the boundary choose the least feasible last value, or reject.
  add(prefix,a=>a==="__"?(p||q?go("back"+(p?0:1),"R",-1):bad()):raw(a)?go(prefix+bit(a),a):bad());
  for(let k=1;k<4;k++)for(let mask=0;mask<2**k;mask++){
   let s=prefix+mask.toString(2).padStart(k,"0");
   add(s,a=>raw(a)?go(s+bit(a),a):bad());
  }
  for(let mask=0;mask<16;mask++){
   let e=mask.toString(2).padStart(4,"0").split("").map(Number),s=prefix+e.join("");
   let x=pred(p,q,e[0],e[2]),y=pred(p,q,e[1],e[3]);
   add(s,a=>raw(a)?go("unary"+(bit(a)&&x!==2?1:0)+y,"T"+bit(a)+(bit(a)?x:2)):bad());
  }
 }
 for(let p of [0,1])for(let y of [0,1,2]){
  add("unary"+p+y,a=>raw(a)?go("edge"+p+(bit(a)&&y!==2?1:0),"T"+bit(a)+(bit(a)?y:2)):bad());
 }
 for(let x of [0,1]){
  add("back"+x,a=>{
   if(/^B[01]$/.test(a))return go("finish","W"+a[1]+x,-1);
   if(!/^T[01][012]$/.test(a))return bad();
   if(x===1&&a[2]==="2")return bad();
   return go(x===0?"pred0":"pred1"+a[2],"O"+a.slice(1)+x,-1);
  });
 }
 add("pred0",a=>/^T[01][01]$/.test(a)?go("skip"+a[2]+"4",a,-1):bad());
 for(let p of [0,1]){
  add("pred1"+p,a=>/^T[01][012]$/.test(a)?go("skip"+p+"4",a,-1):bad());
  for(let j=4;j>=1;j--)add("skip"+p+j,a=>raw(a)?go(j===1?"back"+p:"skip"+p+(j-1),a,-1):bad());
 }
 add("finish",a=>/^I[01]$/.test(a)?go("ready",a,0):bad());
 for(let [s,fn] of defs)for(let a of symbols)rules.push([s,a,...fn(a)]);
 return {symbols,projection,rules};
}
function direct(raw){
 if(!/^[01]+$/.test(raw)||raw.length<2||(raw.length-2)%6)return null;
 const n=1+(raw.length-2)/6,valid=a=>{
  if(raw[a[0]]!=="1")return false;
  for(let i=1;i<n;i++){let j=2+6*(i-1);if(raw[j+2*a[i-1]+a[i]]!=="1"||raw[j+4+a[i]]!=="1")return false;}
  return true;
 };
 // For small fixtures enumerate in reverse lexicographic coordinate priority
 // (least final digit, then least predecessor etc.).
 for(let i=0;i<2**n;i++){let a=Array.from({length:n},(_,j)=>(i>>j)&1);if(valid(a))return a.join("");}
 return null;
}
function run(M,J,raw,limit=50000000){
 let tape=new Map([...raw].map((a,i)=>[i,+a])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,forward=null,backward=null;
 const checkpoint=()=>({head,tape:[...tape].sort((a,b)=>a[0]-b[0])});
 while(state!==M.q&&t<limit){
  let name=M.names[state];
  if(!forward&&/^read:back[01]:$/.test(name))forward=checkpoint();
  if(name==="read:finish:")backward=checkpoint();
  ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [s,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=s;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }
 return {tape,head,state,t,ph,logical,span:hi-lo+1,forward,backward};
}
function audit(){
 const J=pathWorker(),M=compile(J.rules,J.symbols,J.projection),ok=(x,s)=>{if(!x)throw Error(s)};
 let counts={valid:0,sat:0,unsat:0,vertices:0,physical:0,logical:0,checkpoints:0,historyEntries:0,malformed:0,malformedTransitions:0,cutoffs:0};
 let digest=2166136261;
 const dec=new Map(Object.entries(M.code).map(([s,c])=>[c,s]));
 function check(raw,want,record=true){
  let r=run(M,J,raw),N=raw.length,w=M.width,n=1+(N-2)/6;
  ok(r.state===M.q,"halt");
  if(want===null){
   ok(!r.tape.has(r.head)&&!r.forward&&!r.backward,"reject "+raw);
   ok(r.logical===N+1&&r.ph[0]===(w+1)*N*(N+1)+(w+4)*N+3&&r.ph[1]===(3*w-2)*N+2*w-1&&r.ph[2]===0,"reject clock");
  }
  else{
   ok(r.tape.size===n&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b),"witness "+raw);
   let start=-w*N-1;
   function decode(cp){
    ok(cp&&cp.tape.length===w*(N+1)&&cp.tape.every(([pos],i)=>pos===start+i),"checkpoint span");
    let bits=cp.tape.map(x=>x[1]).join("");
    let a=Array.from({length:N+1},(_,i)=>dec.get(bits.slice(i*w,(i+1)*w)));ok(a[N]==="R","R");return a;
   }
   let a=decode(r.forward),b=decode(r.backward),msg=[+raw[0],+raw[1]],positions=[1];
   ok(a[0]==="I"+raw[0]&&a[1]==="B"+raw[1],"first mask");
   for(let i=1;i<n;i++){
    let j=2+6*(i-1);ok(a.slice(j,j+4).every((v,k)=>v===raw[j+k]+"_"),"edge preservation");
    let next=[];
    for(let x of [0,1]){
     let p=msg[0]&&raw[j+x]==="1"?0:msg[1]&&raw[j+2+x]==="1"?1:2;
     if(raw[j+4+x]==="0")p=2;
     ok(a[j+4+x]==="T"+raw[j+4+x]+p,"history");
     next.push(+(p!==2));
    }
    msg=next;positions.push(j+5);
   }
   ok(r.forward.head===start+w*(N-1)&&r.backward.head===start,"heads");
   for(let i=0;i<N;i++){
    let j=positions.indexOf(i);
    ok(b[i]===(j<0?a[i]:j===0?"W"+a[i][1]+want[j]:"O"+a[i].slice(1)+want[j]),"backward preservation");
   }
   const prep=(w+1)*N*(N+1)+(w+4)*N+3;
   let body=0,c=0;
   for(let i=N-1;i>=0;i--){let e=+positions.includes(i);body+=2*w*(i+1)+2*c+2*e+4;c+=e;}
   let serial=2*w*N+2*w+2+body+n+3,logical=2*N+1,mid=(3*w-2)*(logical-1)+(2*w-1);
   ok(r.logical===logical&&r.ph[0]===prep&&r.ph[1]===mid&&r.ph[2]===serial,"clock "+JSON.stringify({N,w,r:r.ph,expected:[prep,mid,serial],logical:r.logical}));
   ok(r.head===-w*N-n-2&&r.span===w*N+n+Math.max(N,w-1)+4,"head/span");
   ok(r.t===11*N*N+60*N+6*n*n-n+27,"closed form");
   if(record){counts.checkpoints+=2;counts.historyEntries+=2*(n-1);}
  }
  if(record){let actual=want===null?'-':Array.from({length:n},(_,i)=>r.tape.get(r.head+i)).join('');for(let ch of raw+':'+actual+';')digest=Math.imul(digest^ch.charCodeAt(0),16777619)>>>0;counts.valid++;counts.sat+=+(want!==null);counts.unsat+=+(want===null);counts.vertices+=n;counts.physical+=r.t;counts.logical+=r.logical;}
  return r;
 }
 for(let N of [2,8])for(let i=0;i<2**N;i++){let raw=i.toString(2).padStart(N,"0");check(raw,direct(raw));}
 let seed=0x52455810;
 for(let i=0;i<48;i++){let n=3+i%6,N=2+6*(n-1),raw="";for(let j=0;j<N;j++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;raw+=seed>>>31;}check(raw,direct(raw));}
 // Plant a witness in additional nontrivial random chains.
 for(let i=0;i<32;i++){
  let n=3+i%6,N=2+6*(n-1),a=[],raw=[];
  for(let j=0;j<n;j++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;a.push(seed>>>31);}
  for(let j=0;j<N;j++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;raw.push(String(seed>>>31));}
  raw[a[0]]="1";
  for(let j=1;j<n;j++){let p=2+6*(j-1);raw[p+2*a[j-1]+a[j]]="1";raw[p+4+a[j]]="1";}
  raw=raw.join("");let want=direct(raw);ok(want!==null,"planted witness");check(raw,want);
 }
 let adversarial={individuallyNonemptyEdges:"11"+"100011"+"000111",forcedNonzeroPredecessor:"11"+"001011"};
 ok(direct(adversarial.individuallyNonemptyEdges)===null,"conflicting path oracle");
 check(adversarial.individuallyNonemptyEdges,null);
 ok(direct(adversarial.forcedNonzeroPredecessor)==="10","nonzero predecessor oracle");
 check(adversarial.forcedNonzeroPredecessor,"10");
 let malformed=[];
 for(let n=0;n<=7;n++)if(n!==2)for(let i=0;i<2**n;i++)malformed.push(n?i.toString(2).padStart(n,"0"):"");
 malformed.push("111111111","1111111111");
 for(let raw of malformed){
  let r=run(M,J,raw);ok(r.state===M.q&&!r.tape.has(r.head),"malformed");counts.malformed++;counts.malformedTransitions+=r.t;
 }
 let scaling=[];
 for(let n of [1,2,4,8,16,32,64]){
  let raw="11"+"111111".repeat(n-1),r=check(raw,"0".repeat(n),false);
  ok(run(M,J,raw,r.t-1).state!==M.q,"cutoff");counts.cutoffs++;
  scaling.push([n,raw.length,r.t,r.logical,r.span,r.ph]);
 }
 let pos=3;while(M.desc[pos]==="1")pos++;
 ok(pos-3===M.q&&M.desc[pos++]==="0","header");let b=M.q.toString(2).length;
 for(let [s,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===s&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
 ok(pos===M.desc.length,"length");
 return {alphabet:J.symbols.length,states:M.q,bits:M.desc.length,width:M.width,logicalStates:new Set(J.rules.map(x=>x[0])).size,rules:J.rules.length,counts,scaling,adversarial,digest};
}
if(process.argv.includes('--description')){let j=pathWorker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_PERSISTENT_PATH_OK '+JSON.stringify(audit()));
