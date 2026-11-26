// Standalone semantic audit; not a physical-tape simulator.
function audit(){
 const need=(x,s)=>{if(!x)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 function records(m,mode){return H.map(h=>({h,bad:new Set([...tuples(m,h.length)].filter(z=>{
  if(mode===0)return false;
  if(mode===1)return h.length===1&&h[0]===0;
  if(mode===2)return h.length===2&&h[1]===h[0]+1&&z[0]!==z[1];
  if(mode===3)return h.length===3&&(h.reduce((s,g)=>s+g,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
  if(mode===4)return h.length===3&&z.some(a=>a!==0);
  if(mode===5)return h.length===2&&z[0]===1&&z[1]===1;
  if(mode===6)return h.length===3&&h[0]===0&&z[0]%2!==z[1]%2;
  return h.length===1&&z[0]!==h[0]%m;
 }).map(key))}));}
 function signatures(m,R){
  return G.map(g=>Array.from({length:m},(_,a)=>{
   let row=[];for(let {h,bad} of R)if(h.includes(g))for(let z of tuples(m,h.length-1)){
    let q=z.slice();q.splice(h.indexOf(g),0,a);row.push([+bad.has(key(q)),m**(3-h.length)]);
   }return row;
  }));
 }
 const dist=(a,b)=>a.reduce((s,[x,w],i)=>s+(x!==b[i][0]?w:0),0);
 function hierarchy(rows){
  let centers=[0],D=rows.map(a=>dist(a,rows[0])),lab=rows.map(()=>0),out=[];
  for(let B=1;B<=rows.length;B++){
   out.push({r:Math.max(...D),lab:lab.slice()});
   if(B===rows.length||!out.at(-1).r)continue;
   let a=D.indexOf(out.at(-1).r),c=centers.length;centers.push(a);
   for(let i=0;i<rows.length;i++){let d=dist(rows[i],rows[a]);if(d<D[i]){D[i]=d;lab[i]=c;}}
  }return out;
 }
 function counted(m,R,L){
  return R.map(({h,bad})=>{
   let M=new Map(),err=0,E=new Set();
   for(let z of tuples(m,h.length)){let k=key(z.map((a,i)=>L[h[i]][a])),v=M.get(k)||[0,0];v[1]++;v[0]+=bad.has(key(z));M.set(k,v);}
   for(let z of tuples(m,h.length)){let [f,n]=M.get(key(z.map((a,i)=>L[h[i]][a]))),q=2*f>n,x=bad.has(key(z));err+=q!==x;if(q&&!x)E.add(key(z));}
   return {h,bad,M,err,E};
  });
 }
 function repair(m,R,S,L){
  let C=counted(m,R,L),err=C.reduce((s,T)=>s+T.err*m**(3-T.h.length),0),threshold=Math.ceil(Math.sqrt(err*m)),badCount=0;
  // err/m^3 = Delta. threshold = ceil(sqrt(Delta)*m^2).
  let labs=G.map(g=>{
   let out=L[g].slice(),next=1+Math.max(...out);
   for(let a=0;a<m;a++){
    let e=0;for(let T of C)if(T.h.includes(g))for(let z of tuples(m,T.h.length-1)){
     let x=z.slice();x.splice(T.h.indexOf(g),0,a);
     let [f,n]=T.M.get(key(x.map((v,i)=>L[T.h[i]][v])));
     if((2*f>n)!==T.bad.has(key(x)))e+=m**(3-T.h.length);
    }
    if(e>threshold){out[a]=next++;badCount++;}
   }
   for(let a=0;a<m;a++)for(let b=0;b<a;b++)if(out[a]===out[b])need(dist(S[g][a],S[g][b])<=2*threshold,"repaired diameter");
   need(next-1-Math.max(...L[g])<=Math.floor(err/Math.max(1,threshold)),"outlier count");
   return out;
  });
  return {err,badCount,labs};
 }
 function walkCount(m,B,L,C){
  let W=G.map(g=>Array.from({length:B},(_,c)=>L[g].filter(a=>a===c).length)),Q=1;while(Q<B)Q*=2;
  let list=[];
  for(let T of C)for(let [k,[f,n]] of T.M)list.push({h:T.h,z:k.split(",").map(Number),f,n});
  for(let g of G)for(let a=0;a<Q;a++)if(!W[g][a])list.push({h:[g],z:[a],f:1,n:1,pad:true});
  let stats=[0,0,0,0,0,0],layers=new Map(),got=[];
  function dfs(t,off,A){
   stats[0]++;let X=Math.max(0,...G.flatMap(g=>W[g].slice(off[g],off[g]+t))),layer=layers.get(t)||[0,0];layer[0]++;layer[1]+=X;layers.set(t,layer);
   for(let r of A){need(r.n<=Math.max(1,X)**r.h.length,"local payload bound");stats[1]++;}
   if(t===1){
    stats[2]++;if(A.some(r=>r.pad||2*r.f>r.n))return;
    let n=G.reduce((p,g)=>p*W[g][off[g]],1),v=A.reduce((p,r)=>p+r.f*(n/r.n),0);
    stats[3]++;stats[4]+=n;stats[5]+=v;if(v<n)got.push(key(off));return;
   }
   let b=t/2;for(let d of tuples(2,9)){
    let o=d.map(a=>a*b),R=[];for(let r of A){let z=r.z.map((x,i)=>x-o[r.h[i]]);if(z.every(a=>a>=0&&a<b))R.push({...r,z});}
    dfs(b,off.map((x,i)=>x+o[i]),R);
   }
  }
  dfs(Q,G.map(()=>0),list);
  for(let [t,[n,s]] of layers){need(n===(Q/t)**9,"node census");need(s*Q<=9*t*m*n,"mean max weight");}
  let direct=[];for(let c of tuples(B,9)){
   let n=G.reduce((p,g)=>p*W[g][c[g]],1);if(!n)continue;
   let a=C.map(T=>T.M.get(key(proj(c,T.h))));if(a.some(([f,n])=>2*f>n))continue;
   if(a.reduce((s,[f,d])=>s+f*(n/d),0)<n)direct.push(key(c));
  }
  need(got.length===direct.length&&got.every(x=>direct.includes(x)),"exact light boxes");
  return [stats,layers.size,got.length];
 }
 let totals=Array(12).fill(0),fixtures=0;
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  let R=records(m,mode),S=signatures(m,R),hs=S.map(hierarchy),scores=Array.from({length:m},(_,i)=>(i+1)*m+Math.max(...hs.map(h=>h[i].r))),B=1+scores.indexOf(Math.min(...scores)),L=hs.map(h=>h[B-1].lab),C=counted(m,R,L);
  let err=C.reduce((s,T)=>s+T.err*m**(3-T.h.length),0),r=Math.max(...hs.map(h=>h[B-1].r));
  need(err<=2*H.reduce((s,h)=>s+h.length,0)*r*m,"majority bound");
  let [stats,depth,light]=walkCount(m,B,L,C);
  let repairCount=0;
  for(let b=1;b<=m;b++){let A=G.map(g=>Array.from({length:m},(_,a)=>(a+g)%b)),rep=repair(m,R,S,A);repairCount+=rep.badCount;
   let k=Math.max(...rep.labs.map(a=>new Set(a).size)),diam=Math.max(0,...G.flatMap(g=>S[g].flatMap((x,a)=>S[g].map((y,b)=>rep.labs[g][a]===rep.labs[g][b]?dist(x,y):0))));
   need(Math.max(...hs.map(h=>h[k-1].r))<=diam,"farthest-first packing");
   need(scores[B-1]<=k*m+diam,"adaptive score");
  }
  [B,err,r,...stats,depth,light,repairCount].forEach((x,i)=>totals[i]+=x);fixtures++;
 }
 // Nonuniform class weights: exhaust all scale maxima for small synthetic class layouts.
 let weightsChecks=0;
 for(let Q of [2,4])for(let m of [Q,2*Q+1,10*Q]){
  let W=G.map(g=>Array.from({length:Q},(_,i)=>i==g%Q?m-Q+1:1));
  for(let t=1;t<=Q;t*=2){
   let n=0,sum=0;for(let z of tuples(Q/t,9)){let X=Math.max(...G.flatMap(g=>W[g].slice(z[g]*t,(z[g]+1)*t)));sum+=X;n++;}
   need(sum*Q<=9*t*m*n,"nonuniform mean max");weightsChecks++;
  }
 }
 // Near-linear type count: one noncycle pair, explicit row separation and all pair disagreement counts.
 const cyc=(i,j)=>j-i===1||i===0&&j===8,par=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 let controls=[];
 for(let d of [2,3,4,5,6]){
  let q=2**d,m=4*q*d+1,label=a=>(a-1)>>1,ty=a=>(a-1)&1,c=a=>label(a)%2?Math.floor(label(a)/2)%q:0;
  const A=(cy,a,b)=>!a||!b?(!cy||a===b):cy?ty(a)!==ty(b)&&label(a)!==label(b):par(c(a)&c(b))===0&&a!==b;
  const P=(cy,a,b)=>!a||!b?(!cy||a===b):cy?ty(a)!==ty(b):par(c(a)&c(b))===0;
  let ec=0,en=0;for(let a=0;a<m;a++)for(let b=0;b<m;b++){ec+=A(true,a,b)!==P(true,a,b);en+=A(false,a,b)!==P(false,a,b);}
  let min=m;for(let x=0;x<q;x++)for(let y=x+1;y<q;y++){let a=1+2*(2*x+1),b=1+2*(2*y+1),n=0;for(let j=1;j<m;j++)if(label(j)%2)n+=A(false,a,j)!==A(false,b,j);min=Math.min(min,n);}
  need(min>=q*d-2,"separation");need(9*ec+27*en<=36*m,"explicit errors");controls.push([d,q,m,2*q+1,9*ec+27*en,min]);
 }
 return {fixtures,totals,weightsChecks,controls};
}
console.log('F038_ADAPTIVE_QUOTIENTS_OK '+JSON.stringify(audit()));
