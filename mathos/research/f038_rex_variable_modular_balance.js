// D7O: exact integer balance sources and fixed-prime Boolean residue certificates.
function sources(N,L,A,d){
 const extraction=N.discover(L,A,d,true),blocks=extraction.blocks,rows=[],seen=new Set();
 function add(h,c,b,source,rule){
  const key=h.join()+":"+c.join()+":"+b;if(seen.has(key))return;seen.add(key);rows.push({h,c,b,source,rule});
 }
 for(let i=0;i<blocks.length;i++){
  const q=blocks[i];if(q.kind==="tight"&&q.coords.length%2===0)add(q.coords,q.sigma.map(x=>1-2*x),q.coords.length/2-q.sigma.reduce((s,x)=>s+x,0),i,"balance");
 }
 for(const q of extraction.rows){
  if(q.h.length===0&&q.rhs===1)add([],[],1,q.source,"parity");
  if(q.h.length===1)add(q.h,[1],q.rhs,q.source,"parity");
  if(q.h.length===2)add(q.h,[1,q.rhs?1:-1],q.rhs,q.source,"parity");
 }
 return {blocks,rows,discovery:extraction.metrics};
}

function reachable(a,p){
 let r=1;for(const x of a)if(x){const old=r;for(let j=0;j<p;j++)if(old>>j&1)r|=1<<((j+x)%p);}return r;
}

function eliminate(k,rows,p){
 const mod=x=>((x%p)+p)%p,m=rows.length,work=rows.map((q,i)=>{const a=new Uint8Array(k),u=new Uint8Array(m);u[i]=1;for(let j=0;j<q.h.length;j++)a[q.h[j]]=mod(q.c[j]);return {a,b:mod(q.b),u};});
 let rank=0,updates=0,tests=0;
 function test(r){tests++;const residues=reachable(r.a,p);if(!(residues>>r.b&1))return {kind:"modular-conflict",prime:p,coefficients:Array.from(r.a),rhs:r.b,residues,combination:Array.from(r.u).flatMap((v,i)=>v?[[i,v]]:[]),rank,updates,tests};return null;}
 for(const r of work){const c=test(r);if(c)return c;}
 for(let j=0;j<k&&rank<m;j++){
  let i=rank;while(i<m&&!work[i].a[j])i++;if(i===m)continue;
  [work[i],work[rank]]=[work[rank],work[i]];const r=work[rank];let inv=1;while(mod(inv*r.a[j])!==1)inv++;
  for(let t=0;t<k;t++)r.a[t]=mod(r.a[t]*inv);for(let t=0;t<m;t++)r.u[t]=mod(r.u[t]*inv);r.b=mod(r.b*inv);
  rank++;
  for(let t=0;t<m;t++)if(t!==rank-1&&work[t].a[j]){
   const s=work[t],v=s.a[j];for(let l=0;l<k;l++)s.a[l]=mod(s.a[l]-v*r.a[l]);for(let l=0;l<m;l++)s.u[l]=mod(s.u[l]-v*r.u[l]);s.b=mod(s.b-v*r.b);updates++;
  }
 }
 for(const r of work){const c=test(r);if(c)return c;}
 return {kind:"unknown",prime:p,rank,updates,tests};
}

function infer(N,L,A,d){
 const q=sources(N,L,A,d),strict=q.blocks.find(b=>b.kind==="strict");
 if(strict)return {kind:"count-conflict",block:strict,discovery:q.discovery};
 const metrics=[];
 for(const p of [3,5,7,11]){
  const r=eliminate(d.k,q.rows,p);metrics.push({prime:p,rank:r.rank,updates:r.updates,tests:r.tests});
  if(r.kind!=="unknown")return {...r,blocks:q.blocks,rows:q.rows,discovery:q.discovery,metrics};
 }
 return {kind:"unknown",discovery:q.discovery,rows:q.rows.length,metrics};
}

function reduce(N,L,A,NV,OV,d,fallback){
 const r=infer(N,L,A,d);
 if(r.kind==="unknown"){if(typeof fallback!=="function")return {d,cert:r,modular:r,contradiction:false,expand:z=>z};return {...fallback(d),modular:r};}
 if(OV.verify(NV,d,r)!==true)throw Error("unverified modular proof");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:r,modular:r,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={sources,reachable,eliminate,infer,reduce};
