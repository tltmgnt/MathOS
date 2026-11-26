// Standalone semantic/abstract-layout audit, not physical tape timings.
function audit(){
 const need=(x,s)=>{if(!x)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* sub(A,k,i=0,p=[]){if(p.length===k){yield p;return;}for(let j=i;j<=A.length-k+p.length;j++)yield* sub(A,k,j+1,p.concat(A[j]));}
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const H=[...sub(G,1),...sub(G,2),...sub(G,3)],proj=(z,h)=>h.map(g=>z[g]);
 function records(m,mode){return H.map(h=>({h,bad:new Set([...tuples(m,h.length)].filter(z=>{
  if(mode===0)return false;
  if(mode===1)return h.length===1&&h[0]===1;
  if(mode===2)return h.length===1&&h[0]===0&&z[0]===1;
  if(mode===3)return key(h)==="0,3"&&z[0]===z[1];
  if(mode===4)return key(h)==="0,3,4"&&z[0]===1&&z[1]===z[2];
  if(mode===5)return h.length===3&&(h.reduce((s,a)=>s+a,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
  return h.length===1&&z[0]!==h[0]%m;
 }).map(key))}));}
 let factorChecks=0;
 function matrixAudit(m,R){
  // Store no-context and one-context tables; both-context term evaluated from its bit vector.
  let g=0,K=[1,2],sections=R.filter(T=>T.h.includes(g)).map(T=>{
   let inside=T.h.filter(i=>K.includes(i)),outside=T.h.filter(i=>i!==g&&!K.includes(i)),w=m**(2-outside.length),tab=new Map();
   function entry(a,b,c){let n=0;for(let z of tuples(m,outside.length)){
    let x=T.h.map(i=>i===g?a:inside.includes(i)?c[inside.indexOf(i)]:z[outside.indexOf(i)]),y=x.slice();y[T.h.indexOf(g)]=b;
    n+=(!T.bad.has(key(x))&&T.bad.has(key(y)))*w;
   }return n;}
   if(inside.length<2)for(let c of tuples(m,inside.length))for(let a=0;a<m;a++)for(let b=0;b<m;b++)tab.set(key([...c,a,b]),entry(a,b,c));
   return {T,inside,outside,w,tab,entry};
  });
  for(let c of tuples(m,2))for(let a=0;a<m;a++)for(let b=0;b<m;b++){
   let direct=0,fast=0;
   for(let S of sections){let x=S.inside.map(i=>c[K.indexOf(i)]);direct+=S.entry(a,b,x);
    if(S.inside.length===2){let z=S.T.h.map(i=>i===g?a:c[K.indexOf(i)]),y=z.slice();y[S.T.h.indexOf(g)]=b;fast+=(!S.T.bad.has(key(z))&&S.T.bad.has(key(y)))*m*m;}
    else fast+=S.tab.get(key([...x,a,b]));
   }
   need(direct===fast,"factorized contextual distance");factorChecks++;
  }
 }
 function run(m,b,mode){
  let M=1;while(M<m)M*=2;
  let R=records(m,mode),raw=R.flatMap(T=>[...T.bad].map(s=>[T.h,s.split(",").map(Number)])),g=0,K=[1,2],P=mode<=2?[0,1,2]:mode===3?[0,1,2,3]:[0,1,2,3,4],rest=G.filter(i=>!P.includes(i)),k=P.length;
  let H0=mode===2?[0]:mode===3?[0,3]:[0,3,4],T=R.find(T=>key(T.h)===key(H0)),rep=(a,c,d)=>(c+d+1)%m;
  const allowed=z=>{if(z.some(a=>a>=m))return false;if(mode===0)return true;if(mode===1)return false;if(mode===6)return z.every((a,i)=>a===P[i]%m);
   let x=H0.map(i=>z[P.indexOf(i)]),y=x.slice();y[0]=rep(x[0],z[1],z[2]);return !T.bad.has(key(x))&&T.bad.has(key(y));};
  let A=[...tuples(m,k)].filter(allowed),pred=z=>R.every(T=>!T.bad.has(key(proj(z,T.h)))),expected=new Set(),got=new Set();
  if(mode===6){let z=G.map(g=>g%m);need(pred(z)&&allowed(proj(z,P)),"unique");expected.add(key(z));}
  else for(let z of tuples(m,9))if(allowed(proj(z,P))&&pred(z))expected.add(key(z));
  for(let i of G)for(let a=m;a<M;a++)raw.push([[i],[a]]);
  let stats=Array(10).fill(0),layers=new Map();
  for(let pp of tuples(M/b,k)){
   let po=pp.map(a=>a*b),pos=0;
   // Stationary preorder tree: header + reserved abstract record slots, then disjoint child subtrees.
   function tree(t,off){
    let start=pos,cap=130*t**3+1;pos+=cap;let child=[],n=0;
    if(t===1)n=+allowed(off.map((a,i)=>a+po[i]));
    else for(let d of tuples(2,k)){let c=tree(t/2,off.map((a,i)=>a+d[i]*t/2));child.push(c);n+=c.n;}
    let end=pos;need(child.every((c,i)=>c.start>start&&c.end<=end&&(!i||child[i-1].end===c.start)),"disjoint physical subregions");
    need(end-start<=10000*t**Math.max(3,k)*(1+Math.log2(t)),"subtree extent");stats[0]++;
    return {start,end,cap,child,n,t,active:false};
   }
   let root=tree(b,Array(k).fill(0));stats[1]++;stats[2]+=pos;
   let want=0;for(let z of tuples(b,k))want+=allowed(z.map((a,i)=>a+po[i]));need(root.n===want,"stationary restriction census");
   for(let rr of tuples(M/b,rest.length)){
    let off=G.map(i=>P.includes(i)?po[P.indexOf(i)]:rr[rest.indexOf(i)]*b),C=[];
    for(let [h,z] of raw){let x=z.map((a,i)=>a-off[h[i]]);if(x.every(a=>a>=0&&a<b))C.push([h,x]);}
    stats[3]++;
    function dfs(node,off,C){
     let t=node.t,layer=layers.get(t)||[0,0];layer[0]++;layers.set(t,layer);stats[4]++;
     need(!node.active&&C.length<node.cap,"exclusive reusable frame");node.active=true;
     if(!node.n){stats[5]++;node.active=false;return;}
     layer[1]++;if(t===1){stats[6]++;let ok=!C.length;need(ok===(off.every(a=>a<m)&&pred(off)&&allowed(proj(off,P))),"exact leaf");if(ok){need(!got.has(key(off)),"disjoint full tile");got.add(key(off));}node.active=false;return;}
     for(let d of tuples(2,9)){
      let u=t/2,o=d.map(a=>a*u),cc=[],idx=proj(d,P).reduce((s,a)=>2*s+a,0),child=node.child[idx];
      for(let [h,z] of C){let x=z.map((a,i)=>a-o[h[i]]);if(x.every(a=>a>=0&&a<u))cc.push([h,x]);}
      need(child.start>node.start+node.cap-1&&child.end<=node.end,"child location");
      let charge=(1+C.length+cc.length)*(child.start-node.start+child.cap+node.cap);
      need(charge<=10000*t**(3+Math.max(3,k))*(1+Math.log2(t)),"shuttle bound in abstract units");
      stats[7]+=cc.length;stats[8]++;
      dfs(child,off.map((a,i)=>a+o[i]),cc);need(!child.active&&node.active,"pop preserves parent");
     }node.active=false;
    }
    dfs(root,off,C);need(!root.active,"root reusable");
   }
  }
  need(got.size===expected.size&&[...got].every(z=>expected.has(z)),"exact restricted model set");
  for(let [t,[v,p]] of layers){need(p<=Math.min((M/t)**9,A.length*(M/t)**(9-k)),"passing bound");if(t<b)need(v<=512*Math.min((M/(2*t))**9,A.length*(M/(2*t))**(9-k)),"visited bound");stats[9]++;}
  return [m,b,mode,k,A.length,got.size,...stats];
 }
 let rows=[];
 for(let m of [2,3])for(let mode=0;mode<=5;mode++){matrixAudit(m,records(m,mode));rows.push(run(m,2,mode));}
 rows.push(run(4,4,6));
 // Algebraic separation: nonzero vectors, all choices of a,b,c,d.
 const par=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 let controls=[];
 for(let q of [4,8,16,32]){
  let min=Infinity,uncond=Infinity,repMax=0,repTotal=0;
  for(let c=1;c<q;c++)for(let d=1;d<q;d++){
   let C=new Map();for(let a=1;a<q;a++){let x=2*par(a&c)+par(a&d);if(!C.has(x))C.set(x,a);let b=C.get(x);need(par((c^d)&a)===par((c^d)&b)&&par(c&a)===par(c&b)&&par(d&a)===par(d&b),"two-context zero loss");}
   repMax=Math.max(repMax,C.size);repTotal+=C.size;
  }
  for(let a=1;a<q;a++)for(let b=1;b<q;b++)if(a!==b){let total=0;for(let c=1;c<q;c++){let n=0;for(let d=1;d<q;d++)n+=par(a&(c^d))===0&&par(b&(c^d))===1;min=Math.min(min,n);total+=n;}uncond=Math.min(uncond,total);}
  need(min>=q/4-1&&uncond===q*(q-2)/4&&repMax<=4,"separation");
  controls.push([q,repMax,repTotal,min,uncond]);
 }
 return {fixtures:rows.length,totals:rows.reduce((s,r)=>s.map((v,i)=>v+r[i+4]),Array(12).fill(0)),factorChecks,controls};
}
console.log('F038_STATIONARY_RESTRICTION_TREE_OK '+JSON.stringify(audit()));
