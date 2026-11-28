// D7D: budgeted host inference, fixed-width subsumption closure and tree certificates.
function indexed(C,d,width=4,budget=2000000){
 if(d.m!==2||![3,4].includes(width)||!Number.isSafeInteger(budget)||budget<0)throw Error("parameters");
 const nodes=[],keys=new Map(),idx=new Map(),literal=new Map(),active=[];
 let work=0,pairs=0,postings=0,probes=0;const stop={};
 function charge(){if(work>=budget)throw stop;work++;}
 function* subsets(a){for(let m=0;m<2**a.length;m++)yield a.filter((_,i)=>m>>i&1).join();}
 function* sig(a,p,r){const t=a.filter(x=>x!==p);if(!r)yield "";if(r===1)for(const x of t)yield String(x);if(r===2)for(let i=0;i<t.length;i++)for(let j=i+1;j<t.length;j++)yield t[i]+","+t[j];}
 function add(n){
  const a=n.c;
  for(const s of subsets(a)){charge();if(keys.has(s))return false;}
  const i=nodes.length;nodes.push(n);active.push(true);keys.set(a.join(),i);
  if(a.length)for(const j of literal.get(a[0])||[]){charge();if(active[j]&&a.every(x=>nodes[j].c.includes(x))){active[j]=false;keys.delete(nodes[j].c.join());}}
  for(const p of a){
   charge();if(!literal.has(p))literal.set(p,[]);literal.get(p).push(i);
   for(let r=0;r<=2;r++)for(const s of sig(a,p,r)){charge();const key=a.length+"|"+p+"|"+s;if(!idx.has(key))idx.set(key,[]);idx.get(key).push(i);}
  }return true;
 }
 const info=()=>({width,work,pairs,postings,probes,generated:nodes.length});
 try{
  for(const n of C.clauses(d)){charge();if(add(n)&&!n.c.length)return {kind:"resolution",nodes,...info()};}
  for(let i=0;i<nodes.length;i++){charge();if(!active[i])continue;
   const a=nodes[i].c,cand=new Set();
   for(const p of a)for(let l=1;l<=width;l++){
    const r=Math.max(0,a.length+l-2-width);
    for(const s of sig(a,p,r)){charge();probes++;for(const j of idx.get(l+"|"+(-p)+"|"+s)||[]){charge();postings++;if(j<i&&active[j])cand.add(j);}}
   }
   for(const j of [...cand].sort((x,y)=>x-y)){
    charge();if(!active[i])break;if(!active[j])continue;pairs++;
    const b=nodes[j].c,piv=a.filter(x=>b.includes(-x));if(piv.length!==1)continue;
    const p=piv[0],c=[...new Set([...a.filter(x=>x!==p),...b.filter(x=>x!==-p)])].sort((x,y)=>Math.abs(x)-Math.abs(y));
    if(c.length<=width&&add({c,i,j,p})&&!c.length)return {kind:"resolution",nodes,...info()};
   }
  }
  return {kind:"unknown",reason:"saturated",closure:[...keys.values()].map(i=>nodes[i].c),...info()};
 }catch(e){if(e!==stop)throw e;return {kind:"unknown",reason:"budget",...info()};}
}

function tree(C,d,budget=2000000){
 if(d.m!==2||!Number.isSafeInteger(budget)||budget<0)throw Error("parameters");
 const clauses=C.clauses(d),z=Array(d.k).fill(-1),stop={},sat={};let work=0,nodes=0,leaves=0,splits=0,units=0;
 function charge(){if(work>=budget)throw stop;work++;}
 const value=x=>z[Math.abs(x)-1]<0?-1:+(z[Math.abs(x)-1]===+(x>0));
 function go(){
  charge();nodes++;
  let best=null;
  for(const {c,f} of clauses){charge();if(c.some(x=>value(x)===1))continue;const open=c.filter(x=>value(x)===-1);
   if(!open.length){leaves++;return {type:"conflict",c,f};}
   if(!best||open.length<best.open.length)best={c,f,open};if(open.length===1)break;
  }
  if(!best)throw sat;
  const {c,f,open}=best,p=open[0],v=Math.abs(p)-1;
  if(open.length===1){units++;z[v]=+(p>0);const child=go();z[v]=-1;return {type:"unit",c,f,p,child};}
  splits++;z[v]=0;const zero=go();z[v]=1;const one=go();z[v]=-1;return {type:"split",v,zero,one};
 }
 try{return {kind:"tree",root:go(),work,nodes,leaves,splits,units};}
 catch(e){if(e!==stop&&e!==sat)throw e;return {kind:"unknown",reason:e===stop?"budget":"model-found",work,nodes,leaves,splits,units};}
}

function php(U,n){
 if(!Number.isSafeInteger(n)||n<3)throw Error("holes");
 let k=n*(n+1),cs=[];
 for(let i=0;i<=n;i++){
  const v=Array.from({length:n},(_,j)=>i*n+j+1);let left=v[0];
  for(let j=1;j<n-2;j++){const x=++k;cs.push([left,v[j],x]);left=-x;}
  cs.push([left,v[n-2],v[n-1]]);
  for(let j=0;j<n;j++)for(let l=i+1;l<=n;l++)cs.push([-v[j],-(l*n+j+1)]);
 }
 return {k,m:2,F:cs.map(c=>{const h=c.map(x=>Math.abs(x)-1);return {h,S:new Set([...U.tuples(2,h.length)].filter(z=>c.some((x,i)=>x>0?z[i]:!z[i])).map(z=>z.join()))}})};
}

function reduce(C,V,T,d,budget=2000000){
 const card=C.cardinality(d);
 let cert=card.kind==="unknown"?indexed(C,d,4,budget):card;
 const first=cert;
 if(cert.kind==="unknown")cert=tree(C,d,budget);
 if(cert.kind==="unknown")return {d,cert,first,contradiction:false,expand:z=>z};
 if((cert.kind==="tree"?T.verifyTree(d,cert):V.verify(d,cert))!==true)throw Error("unverified");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert,first,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={indexed,tree,php,reduce};
