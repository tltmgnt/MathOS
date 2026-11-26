// REX-024D1A — standalone finite-control keyed merge compiler; preencoded input, no bridge.
function machine(){
 const alphabet=["L","0","1",":",";","|","_"],ins=[];
 const add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const halt=add("halt",0,0),reject=add("reject",0,0);
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d});
 const test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),bit=x=>x==="0"||x==="1",data=x=>bit(x)||x===":"||x===";";
 const seq=(...fs)=>d=>fs.reduceRight((n,f)=>f(n),d),move=(t,d)=>n=>mv(t,d,n),put=(t,v)=>n=>wr(t,v,n),app=(t,v)=>seq(put(t,v),move(t,1));
 const loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const clear=(t,d)=>start(t,loop(n=>test(t,x=>x==="_",start(t,d),seq(put(t,"_"),move(t,1))(n))));
 const copyAll=(a,b,d)=>loop(n=>rd(a,x=>x==="_"?d:x==="L"?reject:seq(app(b,x),move(a,1))(n)));
 const copyRecord=(a,b,d)=>loop(n=>rd(a,x=>data(x)?seq(app(b,x),move(a,1))(x===";"?d:n):reject));
 const skip=(t,d)=>loop(n=>rd(t,x=>data(x)?mv(t,1,x===";"?d:n):reject));
 const back=(t,d)=>mv(t,-1,loop(n=>test(t,x=>["L",";","|"].includes(x),mv(t,1,d),mv(t,-1,n))));
 const at=(t,y,n)=>test(t,x=>x!=="_"&&x!=="|",y,n);
 function compare(a,b,lt,eq,gt){
  const ret=[lt,eq,gt].map(d=>back(a,back(b,d)));
  return loop(n=>rd(a,x=>rd(b,y=>{
   if(!bit(x)&&x!==":"||!bit(y)&&y!==":")return reject;
   if(x===y)return x===":"?ret[1]:seq(move(a,1),move(b,1))(n);
   return ret[x===":"||y!==":"&&x==="0"?0:2];
  })));
 }
 const P=0,C=1,A=2,B=3,S=4,K=5,O=6;
 function sort(W,dest){
  // pass states preserve only finite flags for alternation and run count.
  const pass=label();
  const merge=[label(),label(),label()]; // 0,1,>=2 output runs
  for(let k=0;k<3;k++){
   let next=seq(app(W,"|"))(merge[Math.min(k+1,2)]);
   const finishB=loop(n=>rd(B,x=>x==="|"?mv(B,1,next):x==="_"?next:copyRecord(B,W,n)));
   const drainA=loop(n=>rd(A,x=>x==="|"?mv(A,1,finishB):x==="_"?finishB:copyRecord(A,W,n)));
   const pair=loop(n=>at(A,at(B,compare(A,B,copyRecord(A,W,n),copyRecord(A,W,n),copyRecord(B,W,n)),drainA),drainA));
   bind(merge[k],test(A,x=>x==="_",test(B,x=>x==="_",k===2?pass:dest,pair),pair));
  }
  const split=[label(),label()];
  for(let k=0;k<2;k++){
   const t=k===0?A:B;
   bind(split[k],test(W,x=>x==="_",clear(W,start(A,start(B,merge[0]))),loop(n=>test(W,x=>x==="|",seq(app(t,"|"),move(W,1))(split[1-k]),copyRecord(W,t,n)))));
  }
  bind(pass,clear(A,clear(B,start(W,split[0]))));
  const single=[label(),label(),label()];
  for(let k=0;k<3;k++){
   let next=seq(app(A,";"),app(A,"|"),move(W,1))(single[Math.min(k+1,2)]);
   const payload=loop(n=>rd(W,x=>bit(x)?seq(app(A,x),move(W,1))(n):x===";"?next:reject));
   const key=loop(n=>rd(W,x=>bit(x)?seq(app(A,x),move(W,1))(n):x===":"?seq(app(A,":"),move(W,1))(payload):reject));
   bind(single[k],test(W,x=>x==="_",clear(W,start(A,copyAll(A,W,k===2?pass:dest))),key));
  }
  return start(W,clear(A,single[0]));
 }
 const join=loop(n=>at(P,at(S,compare(P,S,skip(P,n),copyRecord(P,O,n),skip(S,n)),halt),halt));
 const joinStart=start(P,start(S,start(O,join)));
 const emitKey=(src,dst,d)=>loop(n=>rd(src,x=>bit(x)?seq(app(dst,x),move(src,1))(n):x===":"?seq(app(dst,":"),app(dst,";"))(d):reject));
 const dedup=[label(),label()];
 for(let k=0;k<2;k++){
  let advance=skip(C,dedup[1]),fresh=clear(K,emitKey(C,K,back(C,emitKey(C,S,back(C,start(K,advance))))));
  bind(dedup[k],at(C,k===0?fresh:compare(C,K,fresh,advance,fresh),joinStart));
 }
 const entry=sort(P,sort(C,start(C,start(S,dedup[0]))));
 return{alphabet,tapes:7,ins,entry};
}
function compile(J){
 const {alphabet,ins,tapes}=J,syms=["G","D","E","~",...alphabet.flatMap(x=>["u"+x,"h"+x])],w=Math.ceil(Math.log2(syms.length-1)),blank="~";
 const codes=Object.fromEntries(syms.filter(s=>s!==blank).map((s,i)=>[s,i.toString(2).padStart(w,"0")]));codes[blank]="2".repeat(w);
 const dec=new Map(Object.entries(codes).map(([s,c])=>[c,s])),prefixes=new Set(Object.values(codes).flatMap(c=>Array.from({length:w-1},(_,i)=>c.slice(0,i+1))));
 const logical=new Map(),add=(n,f)=>{if(logical.has(n))throw Error(n);logical.set(n,f);},r=(n,a)=>[n,a,1],l=(n,a)=>[n,a,-1],z=(n,a)=>[n,a,0],bad=()=>z("HALT",blank);
 function resolve(i){let k=0;while(ins[i].op==="jump"){i=ins[i].next;if(++k>ins.length||i<0)throw Error("jump cycle");}return i;}
 const dest=i=>"i"+resolve(i);
 for(let i=0;i<ins.length;i++){
  const I=ins[i],n="i"+i;if(I.op==="jump")continue;
  if(I.op==="halt"||I.op==="reject"){add(n,a=>a==="G"?z("HALT",I.op==="halt"?a:blank):bad());continue;}
  add(n,a=>a==="G"?r(n+"s"+I.t,a):bad());
  for(let t=I.t;t>=0;t--)add(n+"s"+t,a=>a==="D"&&t>0?r(n+"s"+(t-1),a):a.startsWith("h")&&t===0?z(n+"act",a):a==="E"||a===blank?bad():r(n+"s"+t,a));
  function ret(d){const s="ret"+resolve(d);if(!logical.has(s))add(s,a=>a==="G"?z(dest(d),a):a===blank?bad():l(s,a));return s;}
  if(I.op==="read")add(n+"act",a=>a.startsWith("h")?l(ret(I.next[alphabet.indexOf(a.slice(1))]),a):bad());
  else if(I.op==="write")add(n+"act",a=>a.startsWith("h")&&a!=="hL"&&I.next.v!=="L"?l(ret(I.next.d),"h"+I.next.v):bad());
  else if(I.op==="move"){
   const next=ret(I.next.d),dir=I.next.dir;
   add(n+"act",a=>a.startsWith("h")&&(dir===1||a!=="hL")?(dir===1?r:l)(n+"mark","u"+a.slice(1)):bad());
   add(n+"mark",a=>a.startsWith("u")?l(next,"h"+a.slice(1)):dir===1&&(a==="D"||a==="E")?r(n+"carry"+syms.indexOf(a),"h_"):bad());
   if(dir===1)for(let c of syms.filter(x=>x!=="G"&&x!==blank))add(n+"carry"+syms.indexOf(c),a=>c==="E"?a===blank?l(next,"E"):bad():a===blank||a==="G"?bad():r(n+"carry"+syms.indexOf(a),c));
  }else throw Error("opcode");
 }
 const names=[],ids=new Map(),rows=[];
 function id(n){if(n==="HALT")return -1;if(!ids.has(n)){ids.set(n,names.length);names.push(n);}return ids.get(n);}
 id("R:"+dest(J.entry)+":");
 function step(s,a){
  let [p,n,c,d,k]=s.split(":");const R=(x,v=a)=>[x,v,1],L=(x,v=a)=>[x,v,-1],Z=(x,v=a)=>[x,v,0];
  if(p==="R"){
   let bits=c+a;if(bits.length<w)return prefixes.has(bits)?R("R:"+n+":"+bits):Z("HALT",2);
   let sym=dec.get(bits),f=logical.get(n);if(!sym||!f)return Z("HALT",2);
   let [next,v,dir]=f(sym),code=codes[v];if(!code)throw Error("symbol "+v);
   return L("W:"+next+":"+code+":"+dir+":"+(w-2),+code[w-1]);
  }
  if(p==="W"){
   let j=+k;if(j>0)return L("W:"+n+":"+c+":"+d+":"+(j-1),+c[j]);
   if(+d===0)return Z(n==="HALT"?"HALT":"R:"+n+":",+c[0]);
   return (+d===1?R:L)("M:"+n+":"+ (w-1)+":"+d,+c[0]);
  }
  if(p==="M")return (+d===1?R:L)(+c===1?"R:"+n+":":"M:"+n+":"+(+c-1)+":"+d);
  throw Error(s);
 }
 for(let i=0;i<names.length;i++)for(let a=0;a<3;a++){let [n,v,d]=step(names[i],a);rows.push((id(n)<<4)|(v<<2)|(d+1));}
 const q=names.length,T=Uint32Array.from(rows,v=>v<0?(q<<4)|(v&15):v);
 return{q,T,w,codes,syms,logicalStates:logical.size,entry:0};
}
function encode(M,J,inputs){
 if(inputs.length!==J.tapes||inputs.some(s=>[...s].some(x=>!J.alphabet.includes(x)||x==="L"||x==="_")))throw Error("input");
 return ["G",...inputs.flatMap((s,i)=>["hL",...[...s].map(x=>"u"+x),"u_",i===inputs.length-1?"E":"D"])].map(x=>M.codes[x]).join("");
}
function* descriptorChunks(M){
 const w=M.q.toString(2).length;
 yield "111"+"1".repeat(M.q)+"0";
 for(let i=0;i<M.T.length;i+=8192)yield Array.from(M.T.subarray(i,i+8192),v=>(v>>>4).toString(2).padStart(w,"0")+((v>>2)&3).toString(2).padStart(2,"0")+(v&3).toString(2).padStart(2,"0")).join("");
}
function descriptor(M){return Array.from(descriptorChunks(M)).join("");}
function run(M,raw,limit=Infinity){
 let t=0,h=0,s=0,tape=new Uint8Array(raw.length+1024);tape.fill(2);for(let i=0;i<raw.length;i++)tape[i]=+raw[i];let hi=raw.length-1;
 while(s!==M.q&&t<limit){let v=M.T[3*s+tape[h]];tape[h]=(v>>2)&3;h+=(v&3)-1;s=v>>>4;t++;if(h<0)throw Error("left boundary");if(h===tape.length){let a=new Uint8Array(tape.length*2);a.fill(2);a.set(tape);tape=a;}hi=Math.max(h,hi);}
 if(s!==M.q)return{status:"TIMEOUT",t,head:h,span:hi+1};
 let inv=new Map(Object.entries(M.codes).map(([s,c])=>[c,s])),out=[],heads=[],word="",head=null,cell=0;
 for(let i=0;i<=hi;i+=M.w){let x=inv.get(Array.from(tape.subarray(i,i+M.w)).join(""));if(i===0){if(x!=="G")return{status:"REJECT",t,head:h,span:hi+1};continue;}
  if(x==="D"||x==="E"){if(head===null)throw Error("no head");out.push(word.replace(/_+$/,""));heads.push(head);if(x==="E")return{status:"COMPLETE",t,head:h,span:hi+1,tapes:out,heads};word="";head=null;cell=0;continue;}
  if(!x||!["u","h"].includes(x[0]))throw Error("physical grammar "+i+" "+x);if(x[0]==="h"){if(head!==null)throw Error("duplicate head");head=cell;}if(cell===0&&x.slice(1)!=="L")throw Error("sentinel");if(cell>0)word+=x.slice(1);cell++;
 }throw Error("missing end");
}
module.exports={machine,compile,encode,descriptor,descriptorChunks,run};
