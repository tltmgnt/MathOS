// D7Q: bounded-arity exact integer affine hull and shared modular certificates.
function rank(rows,n){
 const a=rows.map(r=>r.slice());let r=0;
 for(let j=0;j<n&&r<a.length;j++){
  let i=r;while(i<a.length&&!a[i][j])i++;if(i===a.length)continue;
  [a[r],a[i]]=[a[i],a[r]];
  for(let t=r+1;t<a.length;t++)if(a[t][j]){const v=a[t][j],u=a[r][j];for(let l=j;l<n;l++)a[t][l]=u*a[t][l]-v*a[r][l];}
  r++;
 }return r;
}

function hull(f){
 const n=f.h.length;if(n>3)throw Error("bounded arity");
 const z=[...f.S].map(s=>n?s.split(",").map(Number):[]);if(!z.length)return [{c:Array(n).fill(0),b:1}];
 const dif=z.slice(1).map(v=>v.map((x,i)=>x-z[0][i])),target=n-rank(dif,n),basis=[];
 // For n<=3, primitive nullspace basis vectors can be obtained from minors of order <=2, bounded by 2.
 for(let m=0;m<5**n&&basis.length<target;m++){
  const c=Array.from({length:n},(_,i)=>Math.floor(m/5**i)%5-2);
  if(c.find(x=>x!==0)<=0||!c.some(x=>Math.abs(x)===1))continue;
  if(dif.some(v=>v.reduce((s,x,i)=>s+x*c[i],0)!==0))continue;
  if(rank([...basis,c],n)>basis.length)basis.push(c);
 }
 if(basis.length!==target)throw Error("incomplete local hull");
 return basis.map(c=>({c,b:c.reduce((s,x,i)=>s+x*z[0][i],0)}));
}

function sources(O,N,L,A,d){
 const s=O.sources(N,L,A,d),blocks=s.blocks.slice(),rows=s.rows.slice(),seen=new Set(rows.map(q=>q.h.join()+":"+q.c.join()+":"+q.b));let local=0,added=0,full=0;
 for(let i=0;i<d.F.length;i++){
  const f=d.F[i],order=f.h.map((x,j)=>[x,j]).sort((a,b)=>a[0]-b[0]);
  const basis=hull(f);if(!basis.length)full++;
  for(const q of basis){
   local++;const h=order.map(x=>x[0]),c=order.map(x=>q.c[x[1]]);let b=q.b;
   if(c.find(x=>x!==0)<0){for(let j=0;j<c.length;j++)c[j]=-c[j];b=-b;}
   const hc=h.filter((_,j)=>c[j]!==0),cc=c.filter(x=>x!==0),key=hc.join()+":"+cc.join()+":"+b;
   if(seen.has(key))continue;seen.add(key);
   const source=blocks.length;blocks.push({kind:"integer-local",factor:i,h:hc,c:cc,b});rows.push({h:hc,c:cc,b,source,rule:"integer-local"});added++;
  }
 }
 return {blocks,rows,discovery:{...s.discovery,integerHull:{local,added,full,rows:rows.length}}};
}

function discover(P,O,N,L,A,d,maxProbes=4096,maxWork=200000000){
 return P.discover({...O,sources:(N,L,A,d)=>sources(O,N,L,A,d)},N,L,A,d,maxProbes,maxWork);
}

function infer(P,O,N,L,A,d,structural,maxProbes=4096,maxWork=200000000){
 return P.infer({...O,sources:(N,L,A,d)=>sources(O,N,L,A,d)},N,L,A,d,structural,maxProbes,maxWork);
}

function reduce(P,O,N,L,A,NV,PV,QV,IV,PNV,HV,d,structural,fallback,maxProbes=4096,maxWork=200000000){
 const p=infer(P,O,N,L,A,d,structural,maxProbes,maxWork);
 if(p.kind==="unknown")return {...(typeof fallback==="function"?fallback(d):{d,cert:p,contradiction:false,expand:z=>z}),integerHull:p};
 if(QV.verify(NV,PV,IV,PNV,HV,d,p)!==true)throw Error("unverified integer hull proof");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:p,integerHull:p,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={rank,hull,sources,discover,infer,reduce};
