// Semantic reference; not a physical tape simulator.
function audit(){
 const need=(v,s)=>{if(!v)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 function run(m,b,mode){
  let M=1;while(M<m)M*=2;
  const g=0,h=8,base=[0,2,3],P=mode===0||mode===1?[g,h]:mode===2?[g,2,h]:[g,2,3,h];
  let R=H.map(H=>({h:H,bad:new Set([...tuples(m,H.length)].filter(z=>{
   if(mode===0)return false;
   if(mode===1)return H.length===1&&H[0]===1;
   if(mode===2)return H.length===2&&H[0]===g&&H[1]===2&&z[0]===z[1];
   if(mode===3)return key(H)===key(base)&&z[0]===1&&z[1]===z[2];
   if(mode===4)return H.length===3&&(H.reduce((s,a)=>s+a,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===5)return H.length===3&&z.some(a=>a!==0);
   return H.length===1&&z[0]!==H[0]%m;
  }).map(key))}));
  let raw=R.flatMap(T=>[...T.bad].map(s=>[T.h,s.split(",").map(Number)]));
  let pred=z=>R.every(T=>!T.bad.has(key(proj(z,T.h))));
  let map=Array.from({length:m},(_,c)=>Array.from({length:m},()=> (c+1)%m));
  let H0=mode===2?[g,2]:base,T=R.find(T=>key(T.h)===key(H0));
  function allowed(z){
   if(z.some(a=>a>=m))return false;
   if(mode===0)return true;
   if(mode===1)return false;
   if(mode===6)return z.every((a,i)=>a===P[i]%m);
   let x=H0.map(i=>z[P.indexOf(i)]),y=x.slice();y[0]=map[z[P.indexOf(h)]][x[0]];
   return !T.bad.has(key(x))&&T.bad.has(key(y));
  }
  let A=[...tuples(m,P.length)].filter(allowed),expect=new Set(),actual=new Set();
  if(mode===6){let z=G.map(g=>g%m);need(pred(z)&&allowed(proj(z,P)),"known unique");expect.add(key(z));}
  else for(let z of tuples(m,9))if(allowed(proj(z,P))&&pred(z))expect.add(key(z));
  for(let g of G)for(let a=m;a<M;a++)raw.push([[g],[a]]);
  const layers=new Map(),stats=Array(9).fill(0);
  // Reference batch query merge: independently reconstruct the allowed projection list.
  function extract(off){
   let candidates=[...tuples(b,P.length)].map(z=>z.map((a,i)=>a+off[P[i]])),out=[];
   if(mode<=1||mode===6)out=candidates.filter(allowed);
   else{
    let queries=[];
    for(let id=0;id<candidates.length;id++){
     let z=candidates[id];if(z.some(a=>a>=m))continue;
     let x=H0.map(i=>z[P.indexOf(i)]),y=x.slice();y[0]=map[z[P.indexOf(h)]][x[0]];
     queries.push([key(x),id,0],[key(y),id,1]);
    }
    queries.sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0);
    let stream=[...T.bad].sort(),pos=0,flags=Array.from({length:candidates.length},()=>[0,0]);
    for(let [q,id,side] of queries){while(pos<stream.length&&stream[pos]<q)pos++;flags[id][side]=+(stream[pos]===q);stats[0]++;}
    out=candidates.filter((z,i)=>flags[i][0]===0&&flags[i][1]===1);
   }
   need(out.map(key).join("|")===candidates.filter(allowed).map(key).join("|"),"batch membership");
   return out.map(z=>z.map((a,i)=>a-off[P[i]]));
  }
  function dfs(t,off,C,A){
   let v=layers.get(t)||[0,0];v[0]++;layers.set(t,v);stats[2]++;
   need(C.length<=9*t+36*t*t+84*t**3,"raw list capacity");
   need(A.length<=t**P.length,"allowed list capacity");
   if(!A.length){stats[3]++;return;}
   v[1]++;stats[4]++;
   if(t===1){stats[5]++;need(A.length===1,"leaf relation");let ok=C.length===0;
    need(ok===(off.every(a=>a<m)&&allowed(proj(off,P))&&pred(off)),"leaf exactness");
    if(ok){need(!actual.has(key(off)),"disjoint tiles");actual.add(key(off));}return;}
   let u=t/2;
   for(let d of tuples(2,9)){
    let o=d.map(a=>a*u),cc=[],aa=[];
    for(let [h,z] of C){let q=z.map((a,i)=>a-o[h[i]]);if(q.every(a=>a>=0&&a<u)){cc.push([h,q]);stats[6]++;}}
    for(let z of A){let q=z.map((a,i)=>a-o[P[i]]);if(q.every(a=>a>=0&&a<u)){aa.push(q);stats[7]++;}}
    dfs(u,off.map((a,i)=>a+o[i]),cc,aa);
   }
  }
  for(let block of tuples(M/b,9)){
   let off=block.map(a=>a*b),C=[];
   for(let [h,z] of raw){let q=z.map((a,i)=>a-off[h[i]]);if(q.every(a=>a>=0&&a<b))C.push([h,q]);}
   let allowedLocal=extract(off);stats[1]++;dfs(b,off,C,allowedLocal);
  }
  need(actual.size===expect.size&&[...actual].every(z=>expect.has(z)),"complete branch models");
  for(let [t,[v,p]] of layers){
   let cap=Math.min((M/t)**9,A.length*(M/t)**(9-P.length));
   need(p<=cap,"passing count");
   if(t<b){let upper=512*Math.min((M/(2*t))**9,A.length*(M/(2*t))**(9-P.length));need(v<=upper,"visited count");}
   else need(v===(M/b)**9,"coarse roots");
   stats[8]++;
  }
  return [m,b,mode,P.length,A.length,expect.size,...stats];
 }
 let rows=[];for(let m of [2,3])for(let mode=0;mode<6;mode++)rows.push(run(m,2,mode));
 rows.push(run(4,4,6));
 // Finite check of scale selection and weighted crossover. No timing claims.
 let scaleChecks=0,seriesChecks=0,maxRatio=0;
 for(let m=2;m<=4096;m++){let b=1;while((2*b)**4<=m**3)b*=2;need(b**4<=m**3&&(2*b)**4>m**3,"coarse width");scaleChecks++;}
 for(let p=1;p<=20;p++)for(let k of [2,3,4])for(let r of [0,1,Math.floor(k*p/3),Math.floor(k*p/2),k*p]){
  let logt=p-r/k,sum=0;for(let j=0;j<=p;j++)sum+=Math.min(2**(-j),2**(r-k*p+(k-1)*j))*(j+1)**3;
  let bound=2**(-logt)*(1+logt)**3,ratio=sum/bound;need(ratio<10000,"local log crossover");maxRatio=Math.max(maxRatio,ratio);seriesChecks++;
 }
 return {fixtures:rows.length,totals:rows.reduce((s,r)=>s.map((v,i)=>v+r[i+4]),Array(11).fill(0)),rows,scaleChecks,seriesChecks,maxRatio:Math.round(maxRatio*1e6)/1e6};
}
console.log('F038_LOCAL_EXCEPTION_PRUNING_OK '+JSON.stringify(audit()));
