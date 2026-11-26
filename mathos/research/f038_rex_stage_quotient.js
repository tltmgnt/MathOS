// F038-REX-023A: reachability and exact Mealy transition quotient (halt separate).
function quotient(P,desc){
 const {q,T}=P.decode(desc),halt=q,reach=new Uint8Array(q+1),live=[0];reach[0]=1;
 for(let i=0;i<live.length;i++){let s=live[i];if(s===q)continue;for(let a=0;a<3;a++){let t=T[3*s+a]>>>4;if(!reach[t]){reach[t]=1;live.push(t);}}}
 if(!reach[q]){live.push(q);reach[q]=1;}
 // Initialize by observable write/move signatures, with a separate halt.
 const cls=new Int32Array(q+1);cls.fill(-1);
 const blocks=[],sig=new Map();
 for(let s of live){let key=s===q?"halt":[0,1,2].map(a=>T[3*s+a]&15).join(",");if(!sig.has(key)){sig.set(key,blocks.length);blocks.push([]);}let b=sig.get(key);cls[s]=b;blocks[b].push(s);}
 const initialBlocks=blocks.length,pos=new Int32Array(q+1);
 for(let B of blocks)B.forEach((s,i)=>pos[s]=i);
 // Inverse adjacency: each source has one successor for each read symbol.
 const heads=Array.from({length:3},()=>new Int32Array(q+1).fill(-1)),links=Array.from({length:3},()=>new Int32Array(q+1).fill(-1));
 for(let s of live)for(let a=0;a<3;a++){let t=s===q?q:T[3*s+a]>>>4;links[a][s]=heads[a][t];heads[a][t]=s;}
 const pending=new Uint8Array(3*(q+1)),work=[];
 function enqueue(b,a){let k=3*b+a;if(!pending[k]){pending[k]=1;work.push(k);}}
 for(let b=0;b<blocks.length;b++)for(let a=0;a<3;a++)enqueue(b,a);
 const count=new Int32Array(q+1);let splits=0,processed=0;
 for(let j=0;j<work.length;j++){
  let k=work[j],b=Math.floor(k/3),a=k%3;pending[k]=0;processed++;
  // Collect preimage before mutating any splitter block.
  const pre=[];for(let t of blocks[b])for(let s=heads[a][t];s!==-1;s=links[a][s])pre.push(s);
  const touched=[];
  for(let s of pre){let c=cls[s],B=blocks[c],i=count[c]++;if(i===0)touched.push(c);let p=pos[s],x=B[i];B[p]=x;pos[x]=p;B[i]=s;pos[s]=i;}
  for(let c of touched){let n=count[c],B=blocks[c];count[c]=0;if(n===B.length)continue;
   const newId=blocks.length,other=B.splice(n);blocks.push(other);other.forEach((s,i)=>{cls[s]=newId;pos[s]=i;});splits++;
   for(let a=0;a<3;a++){if(pending[3*c+a])enqueue(newId,a);else enqueue(B.length<=other.length?c:newId,a);}
  }
 }
 // Number initial class zero and halt class last. Validate the homomorphism
 // for EVERY reachable state and all three reads, not just fixture paths.
 const h=cls[q],start=cls[0],order=[start,...blocks.keys()].filter((b,i)=>b!==h&&(i===0||b!==start));
 const Q=order.length,number=new Int32Array(blocks.length);order.forEach((b,i)=>number[b]=i);number[h]=Q;
 const map=new Int32Array(q+1);map.fill(-1);for(let s of live)map[s]=number[cls[s]];
 const rows=new Uint32Array(3*Q);
 for(let i=0;i<Q;i++){let s=blocks[order[i]][0];for(let a=0;a<3;a++){let v=T[3*s+a];rows[3*i+a]=(map[v>>>4]<<4)|(v&15);}}
 let checks=0;for(let s of live){if(s===q)continue;for(let a=0;a<3;a++){let v=T[3*s+a];if(rows[3*map[s]+a]!==((map[v>>>4]<<4)|(v&15)))throw Error("unstable partition");checks++;}}
 if(map[0]!==0||map[q]!==Q)throw Error("initial/halt mapping");
 const w=Q.toString(2).length,description="111"+"1".repeat(Q)+"0"+Array.from(rows,v=>(v>>>4).toString(2).padStart(w,"0")+((v>>2)&3).toString(2).padStart(2,"0")+(v&3).toString(2).padStart(2,"0")).join("");
 const decoded=P.decode(description);if(decoded.q!==Q||decoded.T.some((v,i)=>v!==rows[i]))throw Error("quotient codec");
 return{q:Q,desc:description,map,stats:{originalStates:q,reachableStates:live.length-1,unreachableStates:q-live.length+1,quotientStates:Q,initialBlocks,splits,processed,transitionChecks:checks,originalBits:desc.length,quotientBits:description.length}};
}
module.exports={quotient};
