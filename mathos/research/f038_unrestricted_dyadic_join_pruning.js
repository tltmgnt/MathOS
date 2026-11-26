// Semantic reference; not an original-tape implementation.
function audit(){
 const need=(b,msg)=>{if(!b)throw Error(msg)};
 const G=[0,1,2,3,4,5,6,7,8];
 function* subsets(a,k,start=0,p=[]){if(p.length===k){yield p;return;}for(let i=start;i<=a.length-k+p.length;i++)yield* subsets(a,k,i+1,p.concat(a[i]));}
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const H=[...subsets(G,1),...subsets(G,2),...subsets(G,3)];
 const key=z=>z.join(","),sub=(h,P)=>h.every(g=>P.includes(g));
 function pred(P,records){
  let by=new Map();for(let [h,z] of records){let k=key(h);if(!by.has(k))by.set(k,[h.map(g=>P.indexOf(g)),new Set()]);by.get(k)[1].add(key(z));}
  return z=>{for(let [ix,A] of by.values())if(A.has(key(ix.map(i=>z[i]))))return false;return true;};
 }
 function fixture(m,mode){
  let records=[];
  for(let h of H)for(let z of tuples(m,h.length)){
   let bad=false;
   if(mode===1)bad=h.length===1&&h[0]===0;
   if(mode===2)bad=h.length===1&&z[0]!==h[0]%m;
   if(mode===3)bad=h.length===3&&(z.reduce((s,a,i)=>s+(i+2)*a,0)+h.reduce((s,g)=>s+g,0))%5===0;
   if(mode===4)bad=h.length===2&&h[1]===h[0]+1&&z[0]!==z[1];
   if(mode===5)bad=key(h)==="0,1,2"&&z[0]%2===0&&z[2]!==z[1]||key(h)==="0,3,4"&&z[0]%2===1&&z[2]!==z[1];
   if(bad)records.push([h,z]);
  }return records;
 }
 function run(m,k,mode,all){
  let records=fixture(m,mode),M=1;while(M<m)M*=2;
  let P=G.slice(0,k),tests=all?[...subsets(G,k)]:[P],orig=pred(G,records),ref=new Set();
  if(m===5){need(mode===2,"large unique control");let z=G.map(g=>g%m);need(orig(z),"planted");ref.add(key(z));}
  else for(let z of tuples(m,9))if(orig(z))ref.add(key(z));
  let jp=pred(P,records.filter(([h])=>sub(h,P))),R=0;
  for(let z of tuples(m,k))if(jp(z))R++;
  let root=records.slice();for(let g of G)for(let a=m;a<M;a++)root.push([[g],[a]]);
  let visited=[],positive=[],got=new Set(),stats=[0,0,0,0,0,0,0];
  function dfs(t,off,C,depth){
   visited[depth]=(visited[depth]||0)+1;stats[0]++;stats[6]=Math.max(stats[6],depth+1);
   if(t===1){stats[4]++;let z=off;let ok=pred(G,C)(Array(9).fill(0));need(ok===(z.every(a=>a<m)&&orig(z)),"leaf predicate");if(ok){need(!got.has(key(z)),"duplicate leaf");got.add(key(z));}return;}
   for(let Q of tests){stats[1]++;let p=pred(Q,C.filter(([h])=>sub(h,Q))),ok=false;for(let z of tuples(t,k)){stats[2]++;if(p(z)){ok=true;break;}}
    if(!ok){stats[3]++;return;}
   }
   positive[depth]=(positive[depth]||0)+1;
   let b=t/2;
   for(let d of tuples(2,9)){
    let o=d.map(a=>a*b),child=[];
    for(let [h,z] of C){let q=z.map((a,i)=>a-o[h[i]]);if(q.every(a=>a>=0&&a<b)){child.push([h,q]);stats[5]++;}}
    need(child.length<=9*b+36*b*b+84*b**3,"capacity");
    dfs(b,off.map((a,i)=>a+o[i]),child,depth+1);
   }
  }
  dfs(M,Array(9).fill(0),root,0);
  need(got.size===ref.size&&[...got].every(z=>ref.has(z)),"exact model set");
  for(let d=0;d<visited.length;d++){
   let t=M/2**d;
   if(d===0)need(visited[d]===1,"root");
   else need(visited[d]<=512*Math.min((M/(2*t))**9,R*(M/(2*t))**(9-k)),"visited bound");
   need((positive[d]||0)<=Math.min((M/t)**9,R*(M/t)**(9-k)),"positive bound");
  }
  return [m,k,mode,+all,R,ref.size,...stats];
 }
 let rows=[];
 for(let m of [2,3])for(let k of [5,6,7,8])for(let mode of [0,1,2,3,4,5])rows.push(run(m,k,mode,false));
 rows.push(run(3,5,2,true),run(3,8,2,true),run(5,5,2,false));
 // Dense individual four-way joins, but a sparse five-way join.
 let dense=[];
 for(let m of [8,16,24]){
  let records=[];
  for(let h of H)for(let z of tuples(m,h.length)){
   let d=(z[1]-z[0]+m)%m;
   if(h.length===2&&d>=m/4&&d<m/2||key(h)==="0,1,2"&&z[0]%2===0&&z[2]!==z[1]||key(h)==="0,3,4"&&z[0]%2===1&&z[2]!==z[1])records.push([h,z]);
  }
  let min4=m**4;
  // Constraints are invariant under the choice of unconstrained labels only up to pair ordering;
  // check all four-supports, including both special triple types.
  for(let Q of subsets(G,4)){let p=pred(Q,records.filter(([h])=>sub(h,Q))),n=0;for(let z of tuples(m,4))if(p(z))n++;min4=Math.min(min4,n);}
  let Q=G.slice(0,5),p=pred(Q,records.filter(([h])=>sub(h,Q))),R=0;for(let z of tuples(m,5))if(p(z))R++;
  need(R<=m**4&&R>0&&min4>=Math.floor(m/8)**4/4,"five-way separation");
  dense.push([m,min4,R]);
 }
 // e = max(6,k)+1/2; positive rational slack at density exponent one.
 let slack=[5,6,7,8].map(k=>[k,18-(2*Math.max(6,k)+1),2*k]);
 return {fixtures:rows.length,sums:rows.reduce((a,r)=>a.map((v,i)=>v+r[i+4]),Array(9).fill(0)),dense,slack,deep:rows.at(-1)};
}
console.log('F038_DYADIC_JOIN_PRUNING_OK '+JSON.stringify(audit()));
