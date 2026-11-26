// REX-014: fixed Boolean sliding triple bags, pair separators, two factor masks per candidate.
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
 const symbols=["__","0_","1_","R"];
 const projection={"0_":"_","1_":"_"};
 for(let b of [0,1]){
  for(let v of [0,1]){symbols.push("I"+b+v);projection["I"+b+v]=String(v);}
  for(let p of [0,1,2]){
   symbols.push("H"+b+p);projection["H"+b+p]="_";
   if(p!==2)for(let c of [0,1]){symbols.push("O"+b+p+c);projection["O"+b+p+c]=String(c);}
  }
 }
 const defs=new Map(),reg=(s,fn)=>{if(!defs.has(s))defs.set(s,fn);return s;};
 const raw=a=>a==="0_"||a==="1_",hist=a=>/^H[01][012]$/.test(a),bad=()=>["reject","__",0],r=(s,a)=>[s,a,1],l=(s,a)=>[s,a,-1],z=(s,a)=>[s,a,0];
 function initial(bits){
  return reg(bits?"init"+bits:"init",a=>raw(a)?r(bits.length===3?boundary(bits+a[0]):initial(bits+a[0]),a):bad());
 }
 function boundary(mask){
  return reg("boundary"+mask,a=>a==="__"?l(choose(mask),"R"):raw(a)?first(mask,"",a):bad());
 }
 function canon(mask,j){return j>=2?"0"+mask[1]+"0"+mask[3]:mask;}
 function first(mask,out,a){return raw(a)?r(col(mask,out,1,a[0],0),a):bad();}
 function col(mask,out,phase,bit,hit){
  let j=out.length;mask=canon(mask,j);
  return reg("col"+mask+"x"+out+"x"+phase+bit+hit,a=>{
   if(!raw(a))return bad();
   let b=j>>1,v=+a[0];
   if(phase===1)return r(col(mask,out,2,0,+(mask[b]==="1"&&bit==="1"&&v)),a);
   if(phase===2)return r(col(mask,out,3,a[0],hit),a);
   let p=hit?0:mask[2+b]==="1"&&bit==="1"&&v?1:2;
   let next=out+ +(p!==2);
   return r(next.length===4?boundary(next):reg("first"+canon(mask,next.length)+"x"+next,a=>first(canon(mask,next.length),next,a)),"H"+a[0]+p);
  });
 }
 function choose(mask){
  return reg("choose"+mask,a=>{
   let j=[0,2,1,3].find(j=>mask[j]==="1");
   return j===undefined?bad():z(backAt(j),a);
  });
 }
 function backAt(j){
  return reg("backAt"+j,a=>hist(a)?z(scan(j,15),a):raw(a)?l(initialOut(j>>1),"I"+a[0]+(j&1)):bad());
 }
 function initialOut(a){
  return reg("initialOut"+a,s=>raw(s)?l("finish1","I"+s[0]+a):bad());
 }
 function scan(j,pos){
  return reg("scan"+j+"x"+pos,a=>{
   if(pos===4*j+3){
    if(!hist(a)||a[2]==="2")return bad();
    return l(skip(2*+a[2]+(j>>1),pos-1),"O"+a.slice(1)+(j&1));
   }
   return (pos%4===3?hist(a):raw(a))?l(scan(j,pos-1),a):bad();
  });
 }
 function skip(j,pos){
  return reg("skip"+j+"x"+pos,a=>(pos%4===3?hist(a):raw(a))?l(pos===0?backAt(j):skip(j,pos-1),a):bad());
 }
 reg("finish1",a=>raw(a)?l("finish0",a):bad());
 reg("finish0",a=>raw(a)?z("ready",a):bad());
 initial("");
 const rules=[];
 // Build only reachable finite-control states, with total symbol rules, including explicit aligned rejection.
 for(let [s,fn] of defs)for(let a of symbols){
  let [t,w,d]=fn(a);
  rules.push([s,a,t,w,d]);
 }
 return {symbols,projection,rules};
}
function encode(initial,stages){return initial.join("")+stages.map(s=>s.flat(2).join("")).join("");}
function oracle(initial,stages){
 let n=stages.length+2,a=Array(n).fill(0);
 function rec(i){
  if(i<0)return initial[2*a[0]+a[1]]&&stages.every((s,j)=>s[2*a[j+1]+a[j+2]][a[j]].every(Boolean))?a.join(""):null;
  for(let b=0;b<2;b++){a[i]=b;let w=rec(i-1);if(w!==null)return w;}return null;
 }
 return rec(n-1);
}
function logical(J,raw,limit=2000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a)??["reject","__",0];trace.push([state,head,a]);if(trace.length>12)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}

function physical(M,raw,limit=30000000){
 let tape=new Map([...raw].map((v,i)=>[i,+v])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,forward=null,backward=null;
 const snap=()=>({head,tape:[...tape].sort((a,b)=>a[0]-b[0])});
 while(state!==M.q&&t<limit){
  let name=M.names[state];if(/^read:choose[01]{4}:$/.test(name))forward={...snap(),mask:name.slice(11,15)};if(name==="read:finish0:")backward=snap();
  ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [q,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);
  head+=d;state=q;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }return {tape,head,state,t,ph,logical,span:hi-lo+1,forward,backward};
}
function audit(){
 const J=worker(),M=compile(J.rules,J.symbols,J.projection),ok=(x,s)=>{if(!x)throw Error(s)},dec=new Map(Object.entries(M.code).map(([a,b])=>[b,a]));
 let counts={valid:0,sat:0,unsat:0,variables:0,bags:0,candidates:0,physical:0,logical:0,checkpoints:0,messageEntries:0,predecessors:0,malformed:0,malformedTransitions:0,cutoffs:0},digest=2166136261;
 const bits=(x,n)=>Array.from({length:n},(_,i)=>(x>>i)&1),all=[1,1,1,1],stage=(x,y)=>Array.from({length:4},(_,j)=>Array.from({length:2},(_,a)=>[(x>>(2*j+a))&1,(y>>(2*j+a))&1]));
 function check(initial,stages,record=true,known=undefined){
  let raw=encode(initial,stages),N=raw.length,w=M.width,g=stages.length,n=g+2,want=known===undefined?oracle(initial,stages):known,ref=logical(J,raw),r=physical(M,raw);
  ok(r.state===M.q&&ref.state===(want===null?"reject":"ready")&&r.logical===ref.t,"halt "+JSON.stringify({raw,ref,t:r.t}));
  let prep=(w+1)*N*(N+1)+(w+4)*N+3,mid=(3*w-2)*ref.moves+(2*w-1)*(ref.t-ref.moves);
  ok(r.ph[0]===prep&&r.ph[1]===mid,"phase clock "+JSON.stringify({raw,ph:r.ph,prep,mid}));
  let start=-w*N-1;
  function unpack(cp){
   ok(cp&&cp.tape.length===w*(N+1)&&cp.tape.every(([p],i)=>p===start+i),"checkpoint layout");
   let b=cp.tape.map(x=>x[1]).join("");return Array.from({length:N+1},(_,i)=>dec.get(b.slice(w*i,w*(i+1))));
  }
  let expected=[...raw].map(b=>b+"_"),msg=initial.slice(),preds=0;
  for(let i=0;i<g;i++){
   let next=[];
   for(let j=0;j<4;j++){
    let p=[0,1].find(a=>msg[2*a+(j>>1)]&&stages[i][j][a].every(Boolean));
    if(p===undefined)p=2;next.push(+(p!==2));preds+=+(p!==2);
    let pos=4+16*i+4*j+3;expected[pos]="H"+raw[pos]+p;
   }msg=next;
  }expected.push("R");
  ok(JSON.stringify(unpack(r.forward))===JSON.stringify(expected)&&r.forward.mask===msg.join("")&&r.forward.head===start+w*(N-1),"forward checkpoint "+JSON.stringify({raw,mask:r.forward?.mask,msg}));
  if(want!==null){
   ok(r.tape.size===n&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b)&&ref.out===want,"output");
   let b=expected.slice(),positions=new Set([2,3]);b[2]="I"+raw[2]+want[0];b[3]="I"+raw[3]+want[1];
   for(let i=0;i<g;i++){let j=2*+want[i+1]+ +want[i+2],p=4+16*i+4*j+3;positions.add(p);ok(expected[p][2]===want[i],"predecessor provenance");b[p]="O"+expected[p].slice(1)+want[i+2];}
   ok(JSON.stringify(unpack(r.backward))===JSON.stringify(b)&&r.backward.head===start,"backward checkpoint");
   let body=0,c=0;for(let i=N-1;i>=0;i--){let e=+positions.has(i);body+=2*w*(i+1)+2*c+2*e+4;c+=e;}
   ok(r.ph[2]===2*w*N+2*w+2+body+n+3&&r.head===-w*N-n-2,"serializer");
   ok(ref.t===2*N+g+2&&ref.moves===2*N,"logical success clock");
  }else{
   ok(!r.tape.has(r.head)&&r.ph[2]===0&&!r.backward,"reject");
   ok(ref.t===N+2&&ref.moves===N+1,"logical reject clock");
  }
  if(record){
   let out=want===null?"-":Array.from({length:n},(_,i)=>r.tape.get(r.head+i)).join("");for(let ch of raw+":"+out+";")digest=Math.imul(digest^ch.charCodeAt(0),16777619)>>>0;
   counts.valid++;counts.sat+=+(want!==null);counts.unsat+=+(want===null);counts.variables+=n;counts.bags+=g;counts.candidates+=8*g;counts.physical+=r.t;counts.logical+=r.logical;counts.checkpoints+=1+ +(want!==null);counts.messageEntries+=4*(g+1);counts.predecessors+=preds;
  }return r;
 }
 for(let x=0;x<16;x++)check(bits(x,4),[]);
 for(let x=0;x<256;x++)check(all,[stage(x,255)]);
 for(let x=0;x<16;x++)for(let y=0;y<16;y++)check(all,[stage(17*x,17*y)]);
 let conflict=stage(85,170);ok(oracle(all,[conflict])===null,"factor obstruction");check(all,[conflict]);
 let eq=stage(195,255),neq=stage(90,255);
 ok(oracle(all,[eq])!==null&&oracle(all,[neq])!==null&&oracle(all,[eq,neq])===null,"pair obstruction fixture");
 check(all,[eq,neq]);
 let seed=0x52455814;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<64;i++){
  let g=1+i%6,initial=bits(rand()>>>16,4),stages=Array.from({length:g},()=>stage(rand()>>>16,rand()>>>16));
  if(i%2){let a=Array.from({length:g+2},()=>rand()>>>31);initial[2*a[0]+a[1]]=1;for(let j=0;j<g;j++)stages[j][2*a[j+1]+a[j+2]][a[j]]=[1,1];}
  check(initial,stages);
 }
 let malformed=[];for(let n=0;n<4;n++)for(let x=0;x<2**n;x++)malformed.push(n?x.toString(2).padStart(n,"0"):"");
 for(let g of [0,1])for(let r=1;r<16;r++)malformed.push("1".repeat(4+16*g+r));
 for(let raw of malformed){let r=physical(M,raw);ok(r.state===M.q&&!r.tape.has(r.head),"malformed "+raw);counts.malformed++;counts.malformedTransitions+=r.t;}
 let scaling=[];
 for(let g of [1,2,4,8,16,32]){
  let stages=Array.from({length:g},()=>stage(128,128)),initial=[0,0,0,1],raw=encode(initial,stages),r=check(initial,stages,false,"1".repeat(g+2));
  if(g<=8){ok(physical(M,raw,r.t-1).state!==M.q,"cutoff");counts.cutoffs++;}
  scaling.push([g+2,raw.length,r.t,r.logical,r.span,r.ph]);
 }
 let pos=3;while(M.desc[pos]==="1")pos++;ok(pos-3===M.q&&M.desc[pos++]==="0","header");let b=M.q.toString(2).length;
 for(let [q,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===q&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor");pos+=b+4;}
 ok(pos===M.desc.length,"descriptor length");
 return {alphabet:J.symbols.length,width:M.width,logicalStates:new Set(J.rules.map(x=>x[0])).size,rules:J.rules.length,states:M.q,bits:M.desc.length,counts,scaling,digest};
}
if(process.argv.includes('--description')){let j=worker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_PAIR_SEPARATORS_OK '+JSON.stringify(audit()));
