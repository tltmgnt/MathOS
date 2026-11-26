// Semantic occupancy regression; no physical-tape timings.
function audit(){
 const need=(b,msg)=>{if(!b)throw Error(msg)};
 const G=Array.from({length:9},(_,i)=>i), pairs=[];
 for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)pairs.push([i,j]);
 function* subsets(a,k,start=0,p=[]){if(p.length===k){yield p;return;}for(let i=start;i<=a.length-k+p.length;i++)yield* subsets(a,k,i+1,p.concat(a[i]));}
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const cycle=(i,j)=>j-i===1||i===0&&j===8;
 const power=m=>{let M=1;while(M<m)M*=2;return M;};
 function relation(m,i,j,a,b){
  if(a>=m||b>=m)return false;
  if(!a||!b)return cycle(i,j)?a===b:true;
  let h=(m-1)/2,ta=Math.floor((a-1)/h),tb=Math.floor((b-1)/h),x=(a-1)%h,y=(b-1)%h,d=(y-x+h)%h;
  return (!cycle(i,j)||ta!==tb)&&!(d>=Math.floor(h/4)&&d<Math.floor(h/2));
 }
 function coloring(Q){
  let c=new Map();
  for(let g of Q)if(!c.has(g)){
   c.set(g,0);let todo=[g];
   while(todo.length){let u=todo.pop();for(let v of Q)if(u!==v&&cycle(Math.min(u,v),Math.max(u,v))){
    if(c.has(v))need(c.get(v)!==c.get(u),"proper path coloring");
    else{c.set(v,1-c.get(u));todo.push(v);}
   }}
  }return c;
 }
 function compatible(m,t,allowed,unary){
  let M=power(m),q=M/t;
  let U=Array.from({length:9},(_,g)=>Array.from({length:q},(_,x)=>{
   for(let a=x*t;a<(x+1)*t;a++)if(a<m&&unary(g,a))return true;return false;
  }));
  let A=pairs.map(([i,j])=>Array.from({length:q},(_,x)=>Array.from({length:q},(_,y)=>{
   for(let a=x*t;a<(x+1)*t;a++)for(let b=y*t;b<(y+1)*t;b++)if(a<m&&b<m&&unary(i,a)&&unary(j,b)&&allowed(i,j,a,b))return true;return false;
  })));
  // Pair tests include the local unary constraints.
  let idx=Array.from({length:9},()=>Array(9).fill(-1));pairs.forEach(([i,j],k)=>idx[i][j]=k);
  return {q,U,A,idx,pass(z){return z.every((x,i)=>U[i][x])&&pairs.every(([i,j],k)=>A[k][z[i]][z[j]]);}};
 }
 function count(m,t,allowed,unary){
  const {q,U,A,idx}=compatible(m,t,allowed,unary);
  let n=0,partial=0,cur=[];
  function rec(g){if(g===9){n++;return;}for(let x=0;x<q;x++){partial++;if(U[g][x]&&cur.every((a,i)=>A[idx[i][g]][a][x])){cur.push(x);rec(g+1);cur.pop();}}}
  rec(0);return [n,partial];
 }
 let fixtures=[],checks=0,leaves=0,models=0;
 for(let m of [2,3,4])for(let mode=0;mode<6;mode++){
  let U=(g,a)=>mode!==1||g!==0, A=(i,j,a,b)=>mode===2&&j===i+1?a===b:mode===3?(a+b+i+j)%5!==0:mode===4?!(i===0&&j===8&&a===b):true;
  let T=z=>mode!==5||z[0]===z[1]&&z[1]===z[2];
  let M=power(m),levels=[],actual=new Set(),ref=new Set(),localLeaves=0;
  for(let z of tuples(m,9))if(z.every((a,g)=>U(g,a))&&pairs.every(([i,j])=>A(i,j,z[i],z[j]))&&T(z))ref.add(z.join(","));
  function dfs(t,off){
   let h=Math.log2(M/t);if(!levels[h])levels[h]=[0,0];levels[h][0]++;
   if(t===1){localLeaves++;let z=off;if(z.every((a,g)=>a<m&&U(g,a))&&pairs.every(([i,j])=>A(i,j,z[i],z[j]))&&T(z))actual.add(z.join(","));return;}
   let C=compatible(m,t,A,U),x=off.map(a=>a/t);
   if(!C.pass(x))return;levels[h][1]++;
   let b=t/2;for(let d of tuples(2,9))dfs(b,off.map((a,i)=>a+b*d[i]));
  }
  // Cache each scale's compatibility table (host reference only).
  const table=new Map();for(let t=M;t>=2;t/=2)table.set(t,compatible(m,t,A,U));
  function walk(t,off){
   let h=Math.log2(M/t);if(!levels[h])levels[h]=[0,0];levels[h][0]++;
   if(t===1){localLeaves++;let z=off;if(z.every((a,g)=>a<m&&U(g,a))&&pairs.every(([i,j])=>A(i,j,z[i],z[j]))&&T(z))actual.add(z.join(","));return;}
   if(!table.get(t).pass(off.map(a=>a/t)))return;
   levels[h][1]++;let b=t/2;for(let d of tuples(2,9))walk(b,off.map((a,i)=>a+b*d[i]));
  }
  walk(M,Array(9).fill(0));
  need(actual.size===ref.size&&[...actual].every(z=>ref.has(z)),"exact search");
  for(let t=M;t>=2;t/=2){
   let h=Math.log2(M/t),[n]=count(m,t,A,U),q=M/t;
   need((levels[h]?.[1]||0)===n,"all passing boxes reached");
   for(let j=h+1;j<levels.length;j++){need(levels[j][0]<=n*512**(j-h),"descendant bound");checks++;}
   need(n<=q**9,"box count");checks++;
  }
  fixtures.push([m,mode,ref.size,localLeaves]);leaves+=localLeaves;models+=ref.size;
 }
 let controls=[],supportChecks=0,rowChecks=0,properChecks=0,occupancyChecks=0;
 for(let m of [17,33,65,129]){
  let h=(m-1)/2,I=h/8,M=power(m),U=()=>true,A=(i,j,a,b)=>relation(m,i,j,a,b);
  need(G.every(()=>true)&&pairs.every(([i,j])=>A(i,j,0,0)),"zero witness");
  for(let k=2;k<=8;k++)for(let Q of subsets(G,k)){
   let c=coloring(Q);let z=Q.map(g=>1+c.get(g)*h);
   for(let [i,j] of pairs)if(Q.includes(i)&&Q.includes(j)){
    need(A(i,j,z[Q.indexOf(i)],z[Q.indexOf(j)]),"proper support type coloring");
    // Every pair of labels in I is compatible, certifying I^k assignments.
    for(let x=0;x<I;x++)for(let y=0;y<I;y++)need(A(i,j,1+c.get(i)*h+x,1+c.get(j)*h+y),"dense proper join");
   }properChecks++;
  }
  for(let k=1;k<=3;k++)for(let Q of subsets(G,k)){
   let c=coloring(Q);
   for(let g of Q)for(let a=0;a<m;a++){
    let z=Q.map(v=>a===0?0:1+(c.get(v)^c.get(g)^Math.floor((a-1)/h))*h+(a-1)%h);
    need(z[Q.indexOf(g)]===a&&pairs.every(([i,j])=>!Q.includes(i)||!Q.includes(j)||A(i,j,z[Q.indexOf(i)],z[Q.indexOf(j)])),"full local support");
    supportChecks++;
   }
  }
  for(let [i,j] of pairs)for(let reverse of [false,true]){
   let rows=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>+(reverse?A(i,j,b,a):A(i,j,a,b))).join(""));
   need(new Set(rows.slice(1,1+h)).size===h&&rows.slice(1,1+h).every(r=>r.includes("1")&&r.split("0").length-1>=h/4),"high color/forbidden degree");
   if(cycle(i,j)){
    need(new Set(rows).size===m&&rows[0]==="1"+"0".repeat(m-1),"cycle rows");
    for(let a=1;a<m;a++){need(rows[a][0]==="0","zero incomparable");for(let b=a+1;b<m;b++)need(rows[a].includes("1")&&rows[a].split("1").length===rows[b].split("1").length&&rows[a]!==rows[b],"equal-size antichain");}
   }
   rowChecks++;
  }
  let counts=[];
  for(let t of [M/2,M/4,M/8]){
   let q=M/t,[n,partial]=count(m,t,A,U);
   let exceptional=0;
   for(let x=0;x<q;x++){let types=new Set();for(let a=x*t;a<(x+1)*t;a++)if(a<m)types.add(a===0?-1:Math.floor((a-1)/h));if(types.has(-1)||types.size>1)exceptional++;}
   need(n<=9*exceptional*q**8&&exceptional<=2,"exceptional box bound");occupancyChecks++;
   counts.push([t,n,q**9,exceptional,partial]);
  }
  controls.push([m,counts]);
 }
 for(let m of [3,5,9]){
  let [n]=count(m,1,(i,j,a,b)=>relation(m,i,j,a,b),()=>true);
  need(n===1,"unique exact pair CSP");
 }
 // Numerical sanity checks of the local-log crossover bound, not a proof.
 let maxRatio=0,crossChecks=0;
 for(let p=1;p<=24;p++)for(let k of [5,6,7,8])for(let r of [0,1,Math.floor(k*p/3),Math.floor(k*p/2),k*p]){
  let e=Math.max(6,k)+.5,logt=p-r/k,total=0;
  for(let j=0;j<=p;j++)total+=Math.min(2**((e-9)*j),2**(r-k*p+(e-9+k)*j))*(j+1)**3;
  let bound=2**(-(9-e)*logt)*(1+logt)**3;
  let ratio=total/bound;need(ratio<10000,"crossover sanity");maxRatio=Math.max(maxRatio,ratio);crossChecks++;
 }
 return {fixtures:fixtures.length,models,leaves,descendantChecks:checks,properChecks,supportChecks,rowChecks,occupancyChecks,controls,crossChecks,maxRatio:Math.round(maxRatio*1e6)/1e6};
}
console.log('F038_VANISHING_OCCUPANCY_OK '+JSON.stringify(audit()));
