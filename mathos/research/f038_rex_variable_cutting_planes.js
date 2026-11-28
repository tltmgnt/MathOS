// D7S: bounded aggregate integer division with independently checked acyclic proofs.
function gcd(a,b){a=a<0n?-a:a;b=b<0n?-b:b;while(b){const r=a%b;a=b;b=r;}return a;}

function floor(a,b){const q=a/b;return a<0n&&a%b!==0n?q-1n:q;}

function discover(J,d,maxNodes=4096){
 if(d.m!==2||!Number.isSafeInteger(maxNodes)||maxNodes<0||maxNodes>100000)throw Error("limits");
 const nodes=[],values=[],groups=new Map(),metrics={factors:d.F.length,scans:0,selected:0,groups:0,sums:0,divisions:0,opposites:0,nodes:0};
 let terminal=null,stopped=false;
 function add(node,a,b){
  if(nodes.length>=maxNodes){stopped=true;return -1;}
  const i=nodes.length;nodes.push(node);values.push({a,b});metrics.nodes++;
  let min=0n;for(const x of a.values())if(x<0n)min+=x;
  if(min>b)terminal={kind:"cutting-conflict",nodes,terminal:i,lower:String(min),rhs:String(b),metrics};
  return i;
 }
 function sum(ids){
  const a=new Map();let b=0n;
  for(const i of ids){const r=values[i];b+=r.b;for(const [x,v] of r.a){const n=(a.get(x)||0n)+v;if(n)a.set(x,n);else a.delete(x);}}
  const i=add({kind:"sum",parents:ids},a,b);if(i>=0)metrics.sums++;return i;
 }
 const ready=[];
 for(let f=0;f<d.F.length&&!stopped&&!terminal;f++){
  const t=d.F[f],rows=J.supports(t);let best=null,gap=0;
  for(const q of rows){metrics.scans++;if(!t.S.size){best=q;break;}if(q.h.length!==t.h.length||q.a.some(x=>Math.abs(x)!==1))continue;
   const v=q.a.filter(x=>x>0).length-q.b;if(v>gap){best=q;gap=v;}}
  if(!best)continue;
  const id=add({kind:"source",row:{...best,f}},new Map(best.h.map((x,i)=>[x,BigInt(best.a[i])])),BigInt(best.b));if(id<0)break;metrics.selected++;
  const key=[t.h.length,t.S.size,gap].join(":");if(!groups.has(key))groups.set(key,[]);groups.get(key).push(id);
 }
 metrics.groups=groups.size;
 if(terminal)return terminal;
 if(!stopped)for(const ids of groups.values()){
  let i=ids.length===1?ids[0]:sum(ids);if(i<0||terminal)break;
  let {a,b}=values[i],g=0n;for(const v of a.values())g=gcd(g,v);
  if(g>1n){i=add({kind:"divide",parent:i,divisor:String(g)},new Map([...a].map(([x,v])=>[x,v/g])),floor(b,g));if(i<0||terminal)break;metrics.divisions++;}
  ready.push(i);
 }
 if(terminal)return terminal;
 const opposite=new Map(),key=(a,s)=>[...a].sort((x,y)=>x[0]-y[0]).map(([x,v])=>x+":"+String(s*v)).join(",");
 if(!stopped)for(const i of ready){
  const r=values[i],j=opposite.get(key(r.a,-1n));
  if(j!==undefined){metrics.opposites++;if(r.b+values[j].b<0n){sum([j,i]);break;}}
  const k=key(r.a,1n),prev=opposite.get(k);if(prev===undefined||values[prev].b>r.b)opposite.set(k,i);
 }
 if(terminal)return terminal;
 return {kind:"unknown",status:stopped?"budget":"portfolio-exhausted",metrics};
}

function reduce(J,V,SV,d,fallback,maxNodes=4096){
 const r=discover(J,d,maxNodes);
 if(r.kind==="unknown")return {...(typeof fallback==="function"?fallback(d):{d,cert:r,contradiction:false,expand:z=>z}),cutting:r};
 if(SV.verify(V,d,r)!==true)throw Error("unverified cutting proof");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:r,cutting:r,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={gcd,floor,discover,reduce};
