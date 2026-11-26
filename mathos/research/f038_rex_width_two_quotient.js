// REX-024A: linear-storage exact reachable Mealy quotient.
function refine(M){
 const {q,T}=M, n=q+1;
 const reachable=new Uint8Array(n),live=new Uint32Array(n);let count=1;reachable[0]=1;
 for(let i=0;i<count;i++){let s=live[i];if(s===q)continue;for(let a=0;a<3;a++){let t=T[3*s+a]>>>4;if(t>q)throw Error("successor range");if(!reachable[t]){reachable[t]=1;live[count++]=t;}}}
 const reachedHalt=!!reachable[q];if(!reachedHalt)live[count++]=q;
 const cls=new Int32Array(n).fill(-1),begin=new Int32Array(n),end=new Int32Array(n),sizes=new Int32Array(n),pos=new Int32Array(n),perm=new Uint32Array(count);
 const sig=new Map();let blocks=0;
 for(let i=0;i<count;i++){let s=live[i],key=s===q?4096:((T[3*s]&15)<<8)|((T[3*s+1]&15)<<4)|(T[3*s+2]&15);if(!sig.has(key))sig.set(key,blocks++);let b=sig.get(key);cls[s]=b;sizes[b]++;}
 let off=0;for(let b=0;b<blocks;b++){begin[b]=end[b]=off;off+=sizes[b];}
 for(let i=0;i<count;i++){let s=live[i],p=end[cls[s]]++;perm[p]=s;pos[s]=p;}
 const initialBlocks=blocks;
 const heads=new Int32Array(3*n).fill(-1),links=new Int32Array(3*n).fill(-1);
 for(let i=0;i<count;i++){let s=live[i];for(let a=0;a<3;a++){let t=s===q?q:T[3*s+a]>>>4;links[a*n+s]=heads[a*n+t];heads[a*n+t]=s;}}
 // Ring queue has at most one pending entry per (block, read symbol).
 const pending=new Uint8Array(3*n),queue=new Uint32Array(3*n+1);let front=0,back=0;
 function enqueue(b,a){let k=3*b+a;if(pending[k])return;pending[k]=1;queue[back]=k;back=(back+1)%queue.length;if(back===front)throw Error("queue capacity");}
 for(let b=0;b<blocks;b++)for(let a=0;a<3;a++)enqueue(b,a);
 const pre=new Uint32Array(count),touched=new Uint32Array(n),hits=new Uint32Array(n);let splits=0,processed=0,predecessors=0;
 while(front!==back){
  let k=queue[front];front=(front+1)%queue.length;pending[k]=0;processed++;let b=Math.floor(k/3),a=k%3,base=a*n,pn=0,tn=0;
  for(let p=begin[b];p<end[b];p++)for(let s=heads[base+perm[p]];s!==-1;s=links[base+s])pre[pn++]=s;
  predecessors+=pn;
  for(let i=0;i<pn;i++){let s=pre[i],c=cls[s],j=hits[c]++;if(j===0)touched[tn++]=c;let p=pos[s],to=begin[c]+j,x=perm[to];perm[p]=x;pos[x]=p;perm[to]=s;pos[s]=to;}
  for(let i=0;i<tn;i++){let c=touched[i],h=hits[c],lo=begin[c],hi=end[c],mid=lo+h;hits[c]=0;if(mid===hi)continue;let d=blocks++;splits++;
   // Keep the larger part's original class ID; relabel only the smaller.
   if(h<=hi-mid){begin[d]=lo;end[d]=mid;begin[c]=mid;}else{begin[d]=mid;end[d]=hi;end[c]=mid;}
   for(let p=begin[d];p<end[d];p++)cls[perm[p]]=d;
   for(let a=0;a<3;a++)enqueue(d,a); // if old splitter pending it stays pending; otherwise only the smaller new part
  }
 }
 const haltClass=cls[q],startClass=cls[0],Q=blocks-1,number=new Int32Array(blocks),representative=new Uint32Array(Q);
 let id=1;number[startClass]=0;number[haltClass]=Q;representative[0]=perm[begin[startClass]];
 for(let b=0;b<blocks;b++)if(b!==haltClass&&b!==startClass){number[b]=id;representative[id++]=perm[begin[b]];}
 if(id!==Q)throw Error("numbering");
 const map=new Int32Array(n).fill(-1);for(let i=0;i<count;i++){let s=live[i];map[s]=number[cls[s]];}
 const rows=new Uint32Array(3*Q);
 for(let i=0;i<Q;i++)for(let a=0;a<3;a++){let v=T[3*representative[i]+a];rows[3*i+a]=(map[v>>>4]<<4)|(v&15);}
 let checks=0;
 for(let i=0;i<count;i++){let s=live[i];if(s===q)continue;for(let a=0;a<3;a++){let v=T[3*s+a];if(rows[3*map[s]+a]!==((map[v>>>4]<<4)|(v&15)))throw Error("unstable quotient");checks++;}}
 if(map[0]!==0||map[q]!==Q)throw Error("initial/halt mapping");
 return {q:Q,T:rows,map,stats:{originalStates:q,reachableStates:count-1,unreachableStates:q-count+1,quotientStates:Q,initialBlocks,splits,processed,predecessors,transitionChecks:checks,originalBits:4+q+3*q*(q.toString(2).length+4),quotientBits:4+Q+3*Q*(Q.toString(2).length+4),reachedHalt}};
}
function encode(M){
 const w=M.q.toString(2).length,chunks=["111"+"1".repeat(M.q)+"0"];
 for(let i=0;i<M.T.length;i+=8192)chunks.push(Array.from(M.T.subarray(i,i+8192),v=>(v>>>4).toString(2).padStart(w,"0")+((v>>2)&3).toString(2).padStart(2,"0")+(v&3).toString(2).padStart(2,"0")).join(""));
 return chunks.join("");
}
module.exports={refine,encode};
