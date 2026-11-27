// REX-024D3B1: typed-array row interning for memory-bounded ternary lowering.
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

 // Intern physical continuation rows directly, not string-named physical
 // states. Logical roots are reserved first, so cycles need no recursion.
 const roots=[],rootId=new Map(),logicalRows=[],symbolIds=new Map(syms.map((x,i)=>[x,i]));
 const H=0xfffffff,pack=(n,v,d)=>((n<<4)|(v<<2)|(d+1))>>>0;
 function root(n){if(n==="HALT")return H;if(!rootId.has(n)){rootId.set(n,roots.length);roots.push(n);}return rootId.get(n);}
 root(dest(J.entry));
 for(let i=0;i<roots.length;i++)for(let a of syms){let [n,v,d]=logical.get(roots[i])(a);logicalRows.push(pack(root(n),0,0));logicalRows.push(3*symbolIds.get(v)+d+1);}
 const rootCount=roots.length,CH=1<<18,chunks=[];let q=rootCount;
 function slot(i){let k=Math.floor(i/CH);while(chunks.length<=k)chunks.push(new Uint32Array(3*CH));return [chunks[k],3*(i%CH)];}
 function get(i,a){let [t,j]=slot(i);return t[j+a];}
 function put(i,a,b,c){let [t,j]=slot(i);t[j]=a;t[j+1]=b;t[j+2]=c;}
 let hashTable=new Uint32Array(1<<20),used=0;
 function hash(a,b,c){let x=Math.imul(a^0x9e3779b9,0x85ebca6b)^Math.imul(b^0x7f4a7c15,0xc2b2ae35)^Math.imul(c^0x165667b1,0x27d4eb2d);return (x^(x>>>16))>>>0;}
 function grow(){let old=hashTable;hashTable=new Uint32Array(old.length*2);let mask=hashTable.length-1;for(let e of old)if(e){let i=e-1,j=hash(get(i,0),get(i,1),get(i,2))&mask;while(hashTable[j])j=(j+1)&mask;hashTable[j]=e;}}
 function intern(a,b,c){if(used*10>=hashTable.length*7)grow();let mask=hashTable.length-1,j=hash(a,b,c)&mask;
  while(hashTable[j]){let i=hashTable[j]-1;if(get(i,0)===a&&get(i,1)===b&&get(i,2)===c)return i;j=(j+1)&mask;}
  if(q>=H)throw Error("packed state capacity");let i=q++;put(i,a,b,c);hashTable[j]=i+1;used++;return i;
 }
 function moveTail(n,dir,k){for(let i=0;i<k;i++)n=intern(pack(n,0,dir),pack(n,1,dir),pack(n,2,dir));return n;}
 function writeTail(n,code,dir,k){
  let next=dir===0?n:moveTail(n,dir,w-1),a=pack(next,+code[0],dir);
  next=intern(a,a,a);
  for(let i=1;i<=k;i++){a=pack(next,+code[i],-1);next=intern(a,a,a);}
  return next;
 }
 const invalid=pack(H,2,0);
 function transition(i,p,a){
  const bits=p+a;
  if(bits.length<w)return prefixes.has(bits)?pack(node(i,bits),a,1):invalid;
  const sym=dec.get(bits);if(!sym)return invalid;
  let j=2*(i*syms.length+symbolIds.get(sym)),n=logicalRows[j]>>>4,act=logicalRows[j+1],v=syms[Math.floor(act/3)],dir=act%3-1;
  if(v===sym){
   if(dir===1)return pack(n,a,1);
   let distance=dir===0?w-1:2*w-1;return pack(moveTail(n,-1,distance-1),a,-1);
  }
  const code=codes[v];return pack(writeTail(n,code,dir,w-2),+code[w-1],-1);
 }
 function node(i,p){return intern(transition(i,p,0),transition(i,p,1),transition(i,p,2));}
 for(let i=0;i<rootCount;i++)put(i,transition(i,"",0),transition(i,"",1),transition(i,"",2));
 const T=new Uint32Array(3*q);for(let i=0;i<q;i++)for(let a=0;a<3;a++){let v=get(i,a);T[3*i+a]=(v>>>4)===H?pack(q,(v>>>2)&3,(v&3)-1):v;}
 return{q,T,w,codes,syms,logicalStates:logical.size,logicalRoots:rootCount,interned:used,entry:0};
}
module.exports={compile};
