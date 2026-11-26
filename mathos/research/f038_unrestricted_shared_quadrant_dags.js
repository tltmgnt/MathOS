// Host semantic audit; not physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 let n={fixtures:0,root:0,child:0,intern:0,hit:0,zero:0,reachable:0,member:0,positive:0,volume:0,full:0,models:0,overflow:0};
 // Zero is implicit at every level. One is the sole nonzero leaf.
 function builder(t){
  let d=Math.log2(t),nodes=Array.from({length:d+1},()=>[null]),dict=nodes.map(()=>new Map());
  function add(j,v){if(j&&v.every(x=>!x)||!j&&!v){n.zero++;return 0;}
   let k=j?v.join(","):"1";if(dict[j].has(k)){n.hit++;return dict[j].get(k);}
   let id=nodes[j].length;dict[j].set(k,id);nodes[j].push(v);n.intern++;return id;}
  function row(j,f,x=0,y=0){if(!j)return add(0,+f(x,y));let u=2**(j-1);return add(j,[row(j-1,f,x,y),row(j-1,f,x,y+u),row(j-1,f,x+u,y),row(j-1,f,x+u,y+u)]);}
  return {d,nodes,add,row};
 }
 function bit(X,id,x,y,j=X.d){if(!id)return false;if(!j)return true;let u=2**(j-1),a=+(x>=u),b=+(y>=u);return bit(X,X.nodes[j][id][2*a+b],x-a*u,y-b*u,j-1);}
 const size=X=>X.nodes.reduce((s,L)=>s+L.length-1,0);
 function root(t,A,f){let X=builder(t),R=[];
  // Source-ordered incremental construction; repeated target rows share a root.
  let seen=new Map();for(let z of A){let k=key([z[0],z[4]]);if(!seen.has(k))seen.set(k,X.row(X.d,(x,y)=>f(z,x,y)));let id=seen.get(k);if(id)R.push({z:z.slice(0,4),id});}
  n.root++;return {...X,R};
 }
 function child(X,d,t){let u=t/2,o=d.map(v=>v*u),J=2*d[4]+d[5],Y=builder(u);
  let R=X.R.filter(r=>r.z.every((v,i)=>v>=o[i]&&v<o[i]+u)).map(r=>({z:r.z.map((v,i)=>v-o[i]),id:X.nodes[X.d][r.id][J]})).filter(r=>r.id);
  let live=Array.from({length:Y.d+1},()=>new Set());for(let r of R)live[Y.d].add(r.id);
  for(let j=Y.d;j>0;j--)for(let id of live[j])for(let v of X.nodes[j][id])if(v)live[j-1].add(v);
  let map=live.map(()=>new Map([[0,0]]));
  for(let j=0;j<=Y.d;j++)for(let id of [...live[j]].sort((a,b)=>a-b)){
   let v=j?X.nodes[j][id].map(v=>map[j-1].get(v)):1;ok(!j||v.every(x=>x!==undefined),"reachable closure");
   map[j].set(id,Y.add(j,v));n.reachable++;
  }
  R=R.map(r=>({...r,id:map[Y.d].get(r.id)}));ok(size(Y)===live.reduce((s,L)=>s+L.size,0),"no duplicate reachable nodes");n.child++;return {...Y,R};
 }
 function make(m,B,C,F,get,center){
  let M=1;while(M<m)M*=2;
  const E=z=>z.every(v=>v<m)&&!F(z[0],z[4],z[5])&&F(get(z),z[4],z[5])&&!F(center(z[0],get(z)),z[4],z[5]);
  let over=[],mass=0,R=0,roots=new Map();
  function build(o,t){let A=[...tup(t,4)].filter(z=>z.every((a,i)=>a+o[i]<m)).map(z=>[...z,get(z.map((a,i)=>a+o[i]))]);return root(t,A,(z,x,y)=>E([...z.slice(0,4),x,y].map((a,i)=>a+o[i])));}
  function tree(X,o,t){
   let D=build(o,t);ok(size(X)===size(D),"exact dictionary size");
   let A=new Map(X.R.map(r=>[key(r.z),r.id]));
   for(let z of tup(t,6)){ok(bit(X,A.get(key(z.slice(0,4)))||0,z[4],z[5])===E(z.map((a,i)=>a+o[i])),"membership");n.member++;}
   ok(!!X.R.length===!!D.R.length,"positivity");n.positive++;
   if(size(X)>C*t**4){n.overflow++;over.push({o,t});mass+=t**6;return {over:true,flag:true};}
   let T={over:false,flag:!!X.R.length,ch:[]};
   if(T.flag&&t>1)for(let d of tup(2,6))T.ch.push(tree(child(X,d,t),o.map((a,i)=>a+d[i]*t/2),t/2));return T;
  }
  for(let q of tup(M/B,6)){let o=q.map(a=>a*B);roots.set(key(q),tree(build(o,B),o,B));}
  const belongs=z=>over.some(r=>z.every((a,i)=>a>=r.o[i]&&a<r.o[i]+r.t));
  let v=0;for(let z of tup(M,6)){let k=over.filter(r=>z.every((a,i)=>a>=r.o[i]&&a<r.o[i]+r.t)).length;ok(k<=1,"disjoint overflow");v+=k;R+=E(z);n.volume++;}ok(v===mass,"volume");
  const orig=z=>z.every(v=>v<m)&&!F(z[0],z[4],z[5])&&z[6]!==z[7]&&z[2]!==z[8];
  let expected=new Set(),got=new Set();
  for(let z of tup(M,9)){n.full++;if(orig(z)&&(E(z.slice(0,6))||belongs(z.slice(0,6))))expected.add(key(z));}
  function go(T,o,t){if(T.over){for(let z of tup(t,9)){let x=z.map((a,i)=>a+o[i]);if(orig(x))got.add(key(x));}return;}if(!T.flag)return;if(t===1){if(orig(o))got.add(key(o));return;}
   for(let d of tup(2,9)){let u=t/2,idx=d.slice(0,6).reduce((v,a)=>2*v+a,0);go(T.ch[idx],o.map((a,i)=>a+d[i]*u),u);}}
  for(let q of tup(M/B,9))go(roots.get(key(q.slice(0,6))),q.map(a=>a*B),B);
  ok(got.size===expected.size&&[...got].every(z=>expected.has(z)),"models");n.models+=got.size;
  return [R,mass,got.size];
 }
 let cases=[];
 for(let m of [2,3])for(let mode=0;mode<5;mode++){
  let F=(a,x,y)=>mode===0?false:mode===1?a===y&&x!==y:mode===2?a===1&&x===y:mode===3?(a+x)%m===y:(a+x+y)%2===0;
  let get=z=>(z[1]+2*z[2]+z[3]+1)%m;
  for(let center of [a=>a,()=>0]){n.fixtures++;cases.push([m,mode,...make(m,2,1,F,get,center)]);}
 }
 // Exhaust all 4x4 strings, including zero; verify exact child DAG extraction.
 let clipChecks=0;
 for(let i=0;i<65536;i++){
  let X=builder(4),id=X.row(2,(x,y)=>!!(i&(1<<(4*x+y))));X.R=id?[{z:[0,0,0,0],id}]:[];
  for(let x of [0,1])for(let y of [0,1]){
   let Y=child(X,[0,0,0,0,x,y],4),j=Y.R[0]?.id||0;
   for(let u=0;u<2;u++)for(let v=0;v<2;v++)ok(bit(Y,j,u,v)===!!(i&(1<<((u+2*x)*4+v+2*y))),"exhaustive clip");clipChecks++;
  }
 }
 // A synthetic projected cube: all 256 map keys have distinct nonzero 4x4 strings.
 // Realizable by one old-zero row per source and 256 target rows in a larger domain;
 // this is a local guard control, not an enumerated full selector.
 let A=[...tup(4,4)].map((z,i)=>[...z,i+1]),X=root(4,A,(z,x,y)=>!!(z[4]&(1<<(4*x+y))));
 ok(size(X)>4**4&&size(X)<=2*4**4,"overflow cap");
 let E=z=>!!((1+z.slice(0,4).reduce((v,a)=>4*v+a,0))&(1<<(4*z[4]+z[5])));
 let fallback=0,exact=0;
 for(let z of tup(4,9))if(z[6]!==z[7]){fallback++;if(E(z))exact++;}
 ok(fallback>exact,"safe enlargement");let childMax=0;
 for(let d of tup(2,6))childMax=Math.max(childMax,size(child(X,d,4)));
 let overflow=[size(X),childMax,fallback,exact];
 // Irregular checkerboard-modulated slab code. Compare dense rows, run records, DAG nodes.
 let controls=[];
 for(let [B,r,N] of [[8,3,4],[16,4,8],[32,5,16],[64,6,16]]){
  if(2*r>N)continue;let S=B/N,q=2**r;
  const f=(b,x,y)=>{let i=Math.floor(x/S);return i<2*r&&i%2===(b>>Math.floor(i/2)&1)&&((x&1)===(y&1));};
  let X=builder(B),ids=new Set(),run=0;
  for(let b=0;b<q;b++){
   ids.add(X.row(X.d,(x,y)=>f(b,x,y)));
   let prev="",w=1;for(let x=0;x<B;x++){let a=Array.from({length:B},(_,y)=>+f(b,x,y)).join("");if(a!==prev&&a.includes("1"))w+=1+(a.match(/1+/g)||[]).length;prev=a;}run+=w;
  }
  ok(ids.size===q,"distinct rows");let max=0,checks=0;
  for(let t=1;t<=B;t*=2)for(let x=0;x<B;x+=t)for(let y=0;y<B;y+=t){
   let Y=builder(t);for(let b=0;b<q;b++)Y.row(Y.d,(u,v)=>f(b,u+x,v+y));
   ok(size(Y)<=q*(2*t/S+2)+2*Math.log2(t)+2,"DAG bound");max=Math.max(max,size(Y)/t**4);checks++;
  }
  controls.push([B,r,N,S,q,size(X),B*run,max,checks]);
 }
 let asym=[];
 for(let d of [64,128,256,512]){
  let b=Math.floor(2*d/3),r=Math.floor(.9*d),l=Math.ceil(Math.log2(2*r*Math.log2(d))),s=b-l;
  ok(3*s>=d&&r-b-d/32+Math.log2(r)-l-1>0,"asymptotic comparison");asym.push([d,b,r,l,s]);
 }
 // Same overflowing 4-cube embedded in a passing 8-cube, in quadrant zero.
 let P=root(8,A,(z,x,y)=>x<4&&y<4&&!!(z[4]&(1<<(4*x+y))));
 let Y=child(P,[0,0,0,0,0,0],8);
 ok(size(P)<=8**4&&size(Y)===size(X)&&size(Y)>4**4,"first child overflow");
 let childOverflow=[size(P),size(Y)];
 // Full greedy positive-round comparison on finite checkerboard slab families.
 const parity=x=>{let v=0;while(x){v^=x&1;x>>=1;}return v;};
 let greedyControls=[];
 for(let [m,r,B,N] of [[32,3,16,8],[64,4,32,16]]){
  let q=2**r,S=B/N,T=a=>a>=m/2&&a<m/2+q;
  let F=(a,x,y)=>{let i=Math.floor((x%B)/S);
   return T(a)?(y<m/4&&i<2*r&&i%2===((a-m/2)>>Math.floor(i/2)&1)&&((x&1)===(y&1)))||(y>=m/4&&y<m/2&&!!(parity(a&x)^(y&1))):y>=m/4&&y<m/2||y>=m/2&&!!(parity(a&x)^(y&1));};
  let D=Array.from({length:m},()=>Array(m).fill(0));
  for(let a=0;a<m;a++)for(let b=0;b<m;b++)for(let x=0;x<m;x++)for(let y=0;y<m;y++)D[a][b]+=!F(a,x,y)&&F(b,x,y);
  let w=m*m*r/(8*N),checks=0,rounds=0,maxCap=0,even=0,odd=0;
  for(let j=0;j<r;j++)if(j%2)odd|=1<<j;else even|=1<<j;
  for(let a=0;a<m;a++)if(!T(a))for(let b=m/2;b<m/2+q;b++){ok(D[a][b]===w,"checkerboard loss");checks++;}
  for(let f=m/2;f<m/2+q;f++){
   const loss=(a,b)=>D[a][b]+m*m*(+(T(a)&&!T(b))+ +((a&even)===(f&even)&&(b&even)!==(f&even))+ +((a&odd)===(f&odd)&&(b&odd)!==(f&odd)));
   let res=Array(m).fill(37*m*m),p=Array(m).fill(-1),C=[],best;
   for(let k=1;k<=m;k++){
    let b=-1,v=Infinity;
    for(let j=0;j<m;j++)if(!C.includes(j)){let u=res.reduce((v,x,a)=>v+Math.min(x,loss(a,j)),0);if(u<v){v=u;b=j;}}
    if(k===1)ok(b===f,"first greedy target");
    C.push(b);for(let a=0;a<m;a++)if(p[a]<0||loss(a,b)<res[a]){p[a]=b;res[a]=loss(a,b);}
    if(!best||k*m*m+v<best.v)best={C:C.slice(),p:p.slice(),v:k*m*m+v};
    rounds++;
   }
   for(let a of best.C)best.p[a]=a;
   ok(best.C.every(T)&&best.p.every((b,a)=>T(a)||b===f),"actual best greedy round outside invariant");
   maxCap=Math.max(maxCap,best.C.length);
  }
  greedyControls.push([m,q,w,checks,rounds,maxCap]);
 }
 return {n,cases,clipChecks,overflow,controls,asym,childOverflow,greedyControls};
}
console.log('F038_SHARED_QUADRANT_DAGS_OK '+JSON.stringify(audit()));
