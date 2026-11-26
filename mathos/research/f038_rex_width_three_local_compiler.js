// REX-024D3A2: skip unchanged-symbol rewrite sweeps; same virtual semantics, different physical clock.
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
   // The current head is at the last bit of an aligned symbol.
   // If unchanged, no write-back traversal is needed. Shared movement
   // tails return to the target block's first bit.
   if(v===sym){
    if(dir===1)return R(next==="HALT"?"HALT":"R:"+next+":");
    const distance=dir===0?w-1:2*w-1;
    return L(distance===1?(next==="HALT"?"HALT":"R:"+next+":"):"U:"+next+":"+(distance-1));
   }
   return L("W:"+next+":"+code+":"+dir+":"+(w-2),+code[w-1]);
  }
  if(p==="U")return L(+c===1?(n==="HALT"?"HALT":"R:"+n+":"):"U:"+n+":"+(+c-1));
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

module.exports={compile};
