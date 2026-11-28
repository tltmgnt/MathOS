// D7L: exact weighted NAE pair-count bounds, signed selection and independent checking.
function triples(d,signed){
 const parent=Array.from({length:d.k},(_,i)=>i),parity=Array(d.k).fill(0),size=Array(d.k).fill(1),rows=[];
 function find(x){let r=x,p=0;while(parent[r]!==r){p^=parity[r];r=parent[r];}return [r,p];}
 function join(x,y,p){let [a,u]=find(x),[b,v]=find(y);if(a===b)return;if(size[a]<size[b])[a,b]=[b,a];parent[b]=a;parity[b]=u^v^p;size[a]+=size[b];}
 for(let f=0;f<d.F.length;f++){
  const {h,S}=d.F[f];if(h.length!==3)continue;
  for(const b of signed?[[0,0,0],[0,0,1],[0,1,0],[0,1,1]]:[[0,0,0]]){
   if(S.has(b.join())||S.has(b.map(x=>1-x).join()))continue;
   let good=true;
   for(let i=0;i<3;i++)for(let j=0;j<i;j++){const [a,u]=find(h[i]),[c,v]=find(h[j]);if(a===c&&(u^v)!==(b[i]^b[j]))good=false;}
   if(!good)continue;
   join(h[0],h[1],b[0]^b[1]);join(h[0],h[2],b[0]^b[2]);rows.push({f,h});break;
  }
 }
 return {rows,sigma:parent.map((_,i)=>find(i)[1])};
}

function bound(rows){
 const vertices=new Set(),weights=new Map();
 for(const {h} of rows){h.forEach(x=>vertices.add(x));const a=h.slice().sort((x,y)=>x-y);
  for(let i=0;i<3;i++)for(let j=0;j<i;j++){const key=a[j]+","+a[i];weights.set(key,(weights.get(key)||0)+1);}}
 const v=BigInt(vertices.size),pairs=v*(v-1n)/2n,min=pairs-v*v/4n;
 const hist=new Map();for(const w of weights.values())hist.set(w,(hist.get(w)||0)+1);
 let count=pairs-BigInt(weights.size),sum=0n,best=null;
 for(const t of [...hist.keys()].sort((a,b)=>a-b)){
  const deficit=BigInt(t)*count-sum,lower=BigInt(t)*min-deficit;
  if(!best||lower>best.lower)best={threshold:t,lower,deficit};
  const n=BigInt(hist.get(t));count+=n;sum+=n*BigInt(t);
 }
 if(!best)return {threshold:0,lower:"0",deficit:"0",vertices:vertices.size,pairs:weights.size,triples:rows.length};
 return {...best,lower:String(best.lower),deficit:String(best.deficit),vertices:vertices.size,pairs:weights.size,triples:rows.length};
}

function discover(d,maxPeels=64){
 if(d.m!==2||!Number.isSafeInteger(maxPeels)||maxPeels<0||maxPeels>256)throw Error("limits");
 const metrics={orientations:0,eligible:0,components:0,candidates:0,peels:0,weightVisits:0};
 for(const signed of [false,true]){
  const {rows,sigma}=triples(d,signed);metrics.orientations++;metrics.eligible+=rows.length;
  const by=new Map();for(const row of rows)for(const x of row.h){if(!by.has(x))by.set(x,[]);by.get(x).push(row);}
  const seen=new Set(),components=[];
  for(const x of by.keys())if(!seen.has(x)){
   const q=[x],part=new Map();seen.add(x);
   for(let i=0;i<q.length;i++)for(const row of by.get(q[i])){part.set(row.f,row);for(const y of row.h)if(!seen.has(y)){seen.add(y);q.push(y);}}
   components.push([...part.values()]);
  }
  metrics.components+=components.length;
  for(const component of components){
   let curr=component;
   for(let step=0;curr.length&&step<=maxPeels;step++){
    metrics.candidates++;metrics.weightVisits+=3*curr.length;
    const b=bound(curr);
    if(BigInt(b.lower)>BigInt(curr.length))return {kind:"pair-count",factors:curr.map(x=>x.f),sigma,mode:signed?"signed":"unsigned",...b,metrics};
    if(step===maxPeels)break;
    const degree=new Map();for(const row of curr)for(const v of row.h)degree.set(v,(degree.get(v)||0)+1);
    let least=null;for(const [v,n] of degree)if(!least||n<least[1]||n===least[1]&&v<least[0])least=[v,n];
    curr=curr.filter(row=>!row.h.includes(least[0]));metrics.peels++;
   }
  }
 }
 return {kind:"unknown",metrics};
}

function infer(J,N,G,B,H,C,I,P,d,budget=2000000,maxRounds=2*d.k*d.k+1,beam=8){
 const c=discover(d);if(c.kind!=="unknown")return c;
 const p=J.infer(N,G,B,H,C,I,P,d,budget,maxRounds,beam);
 return p.kind==="unknown"?{kind:"unknown",count:c,iterative:p}:{kind:"inherited",proof:p,count:c};
}

function reduce(J,N,G,B,H,C,V,D,T,HV,NV,I,IV,P,PV,JV,LV,d,budget=2000000,maxRounds=2*d.k*d.k+1,beam=8){
 const c=infer(J,N,G,B,H,C,I,P,d,budget,maxRounds,beam);
 if(c.kind==="unknown")return {...D.reduce({...C,cardinality:x=>N.sparseCardinality(C,x)},V,T,d,budget),pairCounting:c};
 if(LV.verify(JV,PV,IV,NV,HV,d,c)!==true)throw Error("unverified counting certificate");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:c,pairCounting:c,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={triples,bound,discover,infer,reduce};
