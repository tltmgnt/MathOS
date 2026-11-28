// D7U: complete signed components, quadratic-size prefix cuts and inherited small-clique partition.
function discover(S,d,maxNodes=4096,maxChecks=2000000){
 if(d.m!==2||!Number.isSafeInteger(maxNodes)||maxNodes<0||maxNodes>100000||!Number.isSafeInteger(maxChecks)||maxChecks<0)throw Error("limits");
 const nodes=[],values=[],metrics={factors:d.F.length,edges:0,vertices:0,checks:0,components:0,complete:0,largest:0,componentPairs:0,cliques:{1:0,2:0,3:0,4:0},lowerSources:0,groups:0,sums:0,divisions:0,nodes:0};
 const stop={},win={};let result=null;
 function add(node,a,b){
  if(nodes.length>=maxNodes)throw stop;
  const i=nodes.length;nodes.push(node);values.push({a,b});metrics.nodes++;
  let min=0n;for(const v of a.values())if(v<0n)min+=v;
  if(min>b){result={kind:"cutting-conflict",nodes,terminal:i,lower:String(min),rhs:String(b),metrics};throw win;}
  return i;
 }
 function source(row){return add({kind:"source",row},new Map(row.h.map((x,i)=>[x,BigInt(row.a[i])])),BigInt(row.b));}
 function sum(ids){
  const a=new Map();let b=0n;for(const i of ids){const r=values[i];b+=r.b;for(const [x,v] of r.a){const q=(a.get(x)||0n)+v;if(q)a.set(x,q);else a.delete(x);}}
  metrics.sums++;return add({kind:"sum",parents:ids},a,b);
 }
 function divide(i,g){
  if(g<=1n)return i;const r=values[i];metrics.divisions++;return add({kind:"divide",parent:i,divisor:String(g)},new Map([...r.a].map(([x,v])=>[x,v/g])),S.floor(r.b,g));
 }
 function aggregate(ids){let i=ids.length===1?ids[0]:sum(ids),g=0n;for(const v of values[i].a.values())g=S.gcd(g,v);return divide(i,g);}
 const adj=new Map(),edges=new Map(),cache=new Map(),used=new Set(),orientation=new Map();
 const cmp=(x,y)=>Math.abs(x)-Math.abs(y)||y-x,key=(x,y)=>[x,y].sort(cmp).join(":");
 const coord=x=>Math.abs(x)-1,sign=x=>x>0?1:-1;
 function charge(){if(metrics.checks>=maxChecks)throw stop;metrics.checks++;}
 function edge(x,y){charge();return adj.get(x)?.has(y)===true;}
 function row(vs,b,f){const v=vs.slice().sort(cmp);return {h:v.map(coord),a:v.map(sign),b,f};}
 function exclusion(x,y){const k=key(x,y);if(!cache.has(k))cache.set(k,source(row([x,y],1-+(x<0)-+(y<0),edges.get(k))));return cache.get(k);}
 function subsets(v,n){const out=[];function rec(i,a){if(a.length===n){out.push(a);return;}for(let j=i;j<=v.length-(n-a.length);j++)rec(j+1,[...a,v[j]]);}rec(0,[]);return out;}
 function triangle(v){return divide(sum(subsets(v,2).map(([x,y])=>exclusion(x,y))),2n);}
 function cut(v){
  if(v.length===1){const x=v[0],y=adj.get(x).values().next().value;return source(row(v,1-+(x<0),edges.get(key(x,y))));}
  if(v.length===2)return exclusion(...v);
  if(v.length===3)return triangle(v);
  // Prefix cut: (j-1) copies of old bound plus j edges to new vertex,
  // then divide by j. In occupancy coordinates RHS is 2j-1.
  let id=exclusion(v[0],v[1]);
  for(let j=2;j<v.length;j++){
   const ids=Array(j-1).fill(id);
   for(let i=0;i<j;i++)ids.push(exclusion(v[i],v[j]));
   id=divide(sum(ids),BigInt(j));
  }
  return id;
 }
 try{
  for(let f=0;f<d.F.length;f++){
   const t=d.F[f];if(!t.S.size)source({h:[],a:[],b:-1,f});
   if(t.h.length!==2)continue;
   for(let a=0;a<2;a++)for(let b=0;b<2;b++)if(!t.S.has([a,b].join())){
    const x=(t.h[0]+1)*(a?1:-1),y=(t.h[1]+1)*(b?1:-1),k=key(x,y);
    if(edges.has(k))continue;edges.set(k,f);
    if(!adj.has(x))adj.set(x,new Set());if(!adj.has(y))adj.set(y,new Set());adj.get(x).add(y);adj.get(y).add(x);
   }
  }
  metrics.edges=edges.size;metrics.vertices=adj.size;
  const upper=[],visited=new Set(),parts=[];
  for(const x of [...adj.keys()].sort(cmp))if(!visited.has(x)){
   const q=[x];visited.add(x);
   for(let j=0;j<q.length;j++)for(const y of adj.get(q[j]))if(!visited.has(y)){visited.add(y);q.push(y);}
   parts.push(q.sort(cmp));
  }
  metrics.components=parts.length;
  for(const v of parts){
   if(new Set(v.map(coord)).size!==v.length||v.some(x=>used.has(coord(x))||adj.get(x).size!==v.length-1))continue;
   let complete=true;
   for(let i=0;i<v.length;i++)for(let j=0;j<i;j++){if(!edge(v[i],v[j]))complete=false;metrics.componentPairs++;}
   if(!complete)continue;
   for(const x of v){used.add(coord(x));orientation.set(coord(x),x);}
   metrics.complete++;metrics.largest=Math.max(metrics.largest,v.length);metrics.cliques[v.length]=(metrics.cliques[v.length]||0)+1;
   upper.push(cut(v));
  }
  for(const x of [...adj.keys()].sort(cmp)){
   if(used.has(coord(x)))continue;
   const ns=[...adj.get(x)].filter(y=>!used.has(coord(y))).sort(cmp);let best=ns.length?[x,ns[0]]:[x];
   search:for(let i=0;i<ns.length;i++)for(let j=i+1;j<ns.length;j++){
    const y=ns[i],z=ns[j];if(!edge(y,z))continue;if(best.length<3)best=[x,y,z];
    for(let l=j+1;l<ns.length;l++){const w=ns[l];if(edge(y,w)&&edge(z,w)){best=[x,y,z,w];break search;}}
   }
   for(const v of best){used.add(coord(v));orientation.set(coord(v),v);}
   metrics.cliques[best.length]++;upper.push(cut(best));
  }
  if(upper.length){
   const u=aggregate(upper),groups=new Map();
   for(let f=0;f<d.F.length;f++){
    const t=d.F[f];if(!t.h.length||!t.h.every(x=>orientation.has(x)))continue;
    const vs=t.h.map(x=>orientation.get(x)),l=Math.min(...[...t.S].map(s=>s.split(",").reduce((a,b,j)=>a+ +(Number(b)===(vs[j]>0?1:0)),0)));
    if(l<=0)continue;
    const id=source(row(vs.map(x=>-x),vs.filter(x=>x<0).length-l,f));metrics.lowerSources++;
    const k=t.h.length+":"+l;if(!groups.has(k))groups.set(k,[]);groups.get(k).push(id);
   }
   metrics.groups=groups.size;
   for(const ids of groups.values())sum([u,aggregate(ids)]);
   if(groups.size>1)sum([u,aggregate([...groups.values()].flat())]);
  }
 }catch(e){if(e===win)return result;if(e===stop)return {kind:"unknown",status:"budget",metrics};throw e;}
 return {kind:"unknown",status:"portfolio-exhausted",metrics};
}

function reduce(JV,S,SV,d,fallback,maxNodes=4096,maxChecks=2000000){
 const r=discover(S,d,maxNodes,maxChecks);
 if(r.kind==="unknown")return {...(typeof fallback==="function"?fallback(d):{d,cert:r,contradiction:false,expand:z=>z}),completeComponents:r};
 if(SV.verify(JV,d,r)!==true)throw Error("unverified component cut");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:r,completeComponents:r,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={discover,reduce};
