// REX-024D2B — exact logical-state quotient before ternary lowering.
function logicalRefine(M,k){
 const {q,T}=M, n=q+1;
 const reachable=new Uint8Array(n),live=new Uint32Array(n);let count=1;reachable[0]=1;
 for(let i=0;i<count;i++){let s=live[i];if(s===q)continue;for(let a=0;a<k;a++){let t=T[k*s+a]>>>8;if(t>q)throw Error("successor range");if(!reachable[t]){reachable[t]=1;live[count++]=t;}}}
 const reachedHalt=!!reachable[q];if(!reachedHalt)live[count++]=q;
 const cls=new Int32Array(n).fill(-1),begin=new Int32Array(n),end=new Int32Array(n),sizes=new Int32Array(n),pos=new Int32Array(n),perm=new Uint32Array(count);
 const sig=new Map();let blocks=0;
 for(let i=0;i<count;i++){let s=live[i],key=s===q?'HALT':Array.from(T.subarray(k*s,k*s+k),v=>v&255).join(',');if(!sig.has(key))sig.set(key,blocks++);let b=sig.get(key);cls[s]=b;sizes[b]++;}
 let off=0;for(let b=0;b<blocks;b++){begin[b]=end[b]=off;off+=sizes[b];}
 for(let i=0;i<count;i++){let s=live[i],p=end[cls[s]]++;perm[p]=s;pos[s]=p;}
 const initialBlocks=blocks;
 const heads=new Int32Array(k*n).fill(-1),links=new Int32Array(k*n).fill(-1);
 for(let i=0;i<count;i++){let s=live[i];for(let a=0;a<k;a++){let t=s===q?q:T[k*s+a]>>>8;links[a*n+s]=heads[a*n+t];heads[a*n+t]=s;}}
 // Ring queue has at most one pending entry per (block, read symbol).
 const pending=new Uint8Array(k*n),queue=new Uint32Array(k*n+1);let front=0,back=0;
 function enqueue(b,a){let item=k*b+a;if(pending[item])return;pending[item]=1;queue[back]=item;back=(back+1)%queue.length;if(back===front)throw Error("queue capacity");}
 for(let b=0;b<blocks;b++)for(let a=0;a<k;a++)enqueue(b,a);
 const pre=new Uint32Array(count),touched=new Uint32Array(n),hits=new Uint32Array(n);let splits=0,processed=0,predecessors=0;
 while(front!==back){
  let item=queue[front];front=(front+1)%queue.length;pending[item]=0;processed++;let b=Math.floor(item/k),a=item%k,base=a*n,pn=0,tn=0;
  for(let p=begin[b];p<end[b];p++)for(let s=heads[base+perm[p]];s!==-1;s=links[base+s])pre[pn++]=s;
  predecessors+=pn;
  for(let i=0;i<pn;i++){let s=pre[i],c=cls[s],j=hits[c]++;if(j===0)touched[tn++]=c;let p=pos[s],to=begin[c]+j,x=perm[to];perm[p]=x;pos[x]=p;perm[to]=s;pos[s]=to;}
  for(let i=0;i<tn;i++){let c=touched[i],h=hits[c],lo=begin[c],hi=end[c],mid=lo+h;hits[c]=0;if(mid===hi)continue;let d=blocks++;splits++;
   // Keep the larger part's original class ID; relabel only the smaller.
   if(h<=hi-mid){begin[d]=lo;end[d]=mid;begin[c]=mid;}else{begin[d]=mid;end[d]=hi;end[c]=mid;}
   for(let p=begin[d];p<end[d];p++)cls[perm[p]]=d;
   for(let a=0;a<k;a++)enqueue(d,a); // if old splitter pending it stays pending; otherwise only the smaller new part
  }
 }
 const haltClass=cls[q],startClass=cls[0],Q=blocks-1,number=new Int32Array(blocks),representative=new Uint32Array(Q);
 let id=1;number[startClass]=0;number[haltClass]=Q;representative[0]=perm[begin[startClass]];
 for(let b=0;b<blocks;b++)if(b!==haltClass&&b!==startClass){number[b]=id;representative[id++]=perm[begin[b]];}
 if(id!==Q)throw Error("numbering");
 const map=new Int32Array(n).fill(-1);for(let i=0;i<count;i++){let s=live[i];map[s]=number[cls[s]];}
 const rows=new Uint32Array(k*Q);
 for(let i=0;i<Q;i++)for(let a=0;a<k;a++){let v=T[k*representative[i]+a];rows[k*i+a]=(map[v>>>8]<<8)|(v&255);}
 let checks=0;
 for(let i=0;i<count;i++){let s=live[i];if(s===q)continue;for(let a=0;a<k;a++){let v=T[k*s+a];if(rows[k*map[s]+a]!==((map[v>>>8]<<8)|(v&255)))throw Error("unstable quotient");checks++;}}
 if(map[0]!==0||map[q]!==Q)throw Error("initial/halt mapping");
 return {q:Q,T:rows,map,stats:{originalStates:q,reachableStates:count-1,unreachableStates:q-count+1,quotientStates:Q,initialBlocks,splits,processed,predecessors,transitionChecks:checks,reachedHalt}};
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
 // Build reachable logical transition table before ternary expansion.
 const Lnames=[],Lids=new Map(),Lrows=[],symIds=new Map(syms.map((a,i)=>[a,i]));
 function lid(n){if(n==="HALT")return -1;if(!Lids.has(n)){Lids.set(n,Lnames.length);Lnames.push(n);}return Lids.get(n);}
 lid(dest(J.entry));
 for(let i=0;i<Lnames.length;i++)for(let a of syms){
  const [n,v,d]=logical.get(Lnames[i])(a);Lrows.push((lid(n)<<8)|(symIds.get(v)*3+d+1));
 }
 const lq=Lnames.length,LT=Uint32Array.from(Lrows,v=>v<0?(lq<<8)|(v&255):v),Q=logicalRefine({q:lq,T:LT},syms.length);
 function lower(n,sym){const v=Q.T[Number(n)*syms.length+symIds.get(sym)],next=v>>>8,act=v&255;return[next===Q.q?"HALT":String(next),syms[Math.floor(act/3)],act%3-1];}
 const names=[],ids=new Map(),rows=[];
 function id(n){if(n==="HALT")return -1;if(!ids.has(n)){ids.set(n,names.length);names.push(n);}return ids.get(n);}
 id("R:0:");
 function step(s,a){
  let [p,n,c,d,k]=s.split(":");const R=(x,v=a)=>[x,v,1],L=(x,v=a)=>[x,v,-1],Z=(x,v=a)=>[x,v,0];
  if(p==="R"){
   let bits=c+a;if(bits.length<w)return prefixes.has(bits)?R("R:"+n+":"+bits):Z("HALT",2);
   let sym=dec.get(bits);if(!sym)return Z("HALT",2);
   let [next,v,dir]=lower(n,sym),code=codes[v];if(!code)throw Error("symbol "+v);
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
 return{q,T,w,codes,syms,logicalStates:logical.size,logicalQuotient:Q.stats,entry:0};
}

module.exports={compile,logicalRefine};
