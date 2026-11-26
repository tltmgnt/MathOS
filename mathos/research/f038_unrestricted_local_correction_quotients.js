// Host semantic audit; not physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const n={fixtures:0,passes:0,rootBuilds:0,childBuilds:0,internChecks:0,zeroRows:0,mergedRows:0,overflowRoots:0,overflowChildren:0,membership:0,positivity:0,fullChecks:0,successful:0,narrow:0,wide:0,correction:0,fullRoots:0,fullChildren:0,models:0,abandonedModels:0,greedy:0,overflowMassChecks:0};
 function make(m,F,get,center,C,B){
  let M=1;while(M<m)M*=2;
  const valid=z=>z.every(a=>a<m);
  const E=z=>valid(z)&&!F(z[0],z[4],z[5])&&F(get(z),z[4],z[5])&&!F(center(z[0],get(z)),z[4],z[5]);
  function intern(D,A,t,root){
   let used=new Set(A.map(r=>key([r.z[0],r.j]))),by=new Map(),ids=new Map(),cnt=new Map(),out=[];
   for(let r of D){let k=key([r.a,r.j]);if(!used.has(k))continue;
    if(!r.R.some(Boolean)){by.set(k,null);n.zeroRows++;continue;}
    let p=key([r.a,r.R.join("")]);
    if(!ids.has(p)){let j=cnt.get(r.a)||0;cnt.set(r.a,j+1);ids.set(p,j);out.push({a:r.a,j,R:r.R});}
    else n.mergedRows++;
    by.set(k,ids.get(p));
   }
   let overflow=[...cnt.values()].some(v=>v>C*t);
   if(overflow)n[root?"overflowRoots":"overflowChildren"]++;
   return {overflow,D:overflow?[]:out,A:overflow?[]:A.filter(r=>by.get(key([r.z[0],r.j]))!==null).map(r=>{let j=by.get(key([r.z[0],r.j]));ok(j!==undefined,"row reference");n.internChecks++;return {...r,j};})};
  }
  function root(o,t){let D=[],A=[],seen=new Set();
   for(let z of tup(t,4)){let x=z.map((a,i)=>a+o[i]);if(!valid(x))continue;let b=get(x),k=key([z[0],b]);
    if(!seen.has(k)){seen.add(k);D.push({a:z[0],j:b,R:[...tup(t,2)].map(([u,v])=>+E([...x,u+o[4],v+o[5]]))});}
    A.push({z,j:b});
   }n.rootBuilds++;return intern(D,A,t,true);
  }
  function child(X,d,t){let u=t/2,o=d.map(a=>a*u);
   let D=X.D.filter(r=>r.a>=o[0]&&r.a<o[0]+u).map(r=>({...r,a:r.a-o[0],R:[...tup(u,2)].map(([x,y])=>r.R[(x+o[4])*t+y+o[5]])}));
   let A=X.A.filter(r=>r.z.every((a,i)=>a>=o[i]&&a<o[i]+u)).map(r=>({z:r.z.map((a,i)=>a-o[i]),j:r.j}));
   n.childBuilds++;return intern(D,A,u,false);
  }
  function direct(o,t){let S=Array.from({length:t},()=>new Set());
   for(let z of tup(t,4)){let R=[...tup(t,2)].map(([x,y])=>+E([...z,x,y].map((v,i)=>v+o[i]))).join("");if(R.includes("1"))S[z[0]].add(R);}
   return S;
  }
  let over=[],mass=0,roots=new Map();
  function tree(X,o,t){
   let S=direct(o,t),over0=S.some(s=>s.size>C*t);
   ok(X.overflow===over0,"exact overflow census");
   if(over0){over.push({o,t});mass+=t**6;return {overflow:true,flag:true};}
   let D=new Map(X.D.map(r=>[key([r.a,r.j]),r.R])),A=new Map(X.A.map(r=>[key(r.z),r.j]));
   for(let a=0;a<t;a++){let rows=X.D.filter(r=>r.a===a).map(r=>r.R.join(""));ok(rows.length===S[a].size&&rows.every(r=>S[a].has(r)),"exact local quotient");}
   let flag=false;
   for(let z of tup(t,6)){let R=D.get(key([z[0],A.get(key(z.slice(0,4)))])),v=!!(R&&R[z[4]*t+z[5]]);
    ok(v===E(z.map((a,i)=>a+o[i])),"local membership");n.membership++;flag ||=v;
   }
   ok(flag===S.some(s=>s.size>0),"exact positivity");n.positivity++;
   let T={overflow:false,flag,ch:[]};
   if(flag&&t>1)for(let d of tup(2,6))T.ch.push(tree(child(X,d,t),o.map((a,i)=>a+d[i]*t/2),t/2));
   return T;
  }
  for(let q of tup(M/B,6)){let o=q.map(a=>a*B);roots.set(key(q),tree(root(o,B),o,B));}
  let belongs=z=>over.some(r=>z.every((a,i)=>a>=r.o[i]&&a<r.o[i]+r.t));
  // Check disjoint first-overflow cubes and their expanded mass by exact enumeration.
  let count=0,R=0;for(let z of tup(M,6)){let k=0;for(let r of over)if(z.every((a,i)=>a>=r.o[i]&&a<r.o[i]+r.t))k++;
   ok(k<=1,"disjoint first overflow");count+=k;R+=E(z);n.overflowMassChecks++;
  }ok(count===mass,"overflow mass");
  return {M,E,roots,over,mass,R,belongs};
 }
 for(let m of [2,3])for(let mode=0;mode<6;mode++){
  n.fixtures++;let B=2,ctx=[...tup(m,3)],cols=[...tup(m,2)];
  const F=(a,x,y)=>mode===0?false:mode===1?a===y&&x!==y:mode===2?a===1&&x===y:(a+x)%m===y;
  const N=(a,c,x)=>mode===2&&a===1&&c===x,priv=z=>mode===3&&!!((z[6]^z[7]^z[8])&1)||mode===4&&z[2]===z[8]||mode===5&&z[6]===z[0];
  const orig=z=>z.every(a=>a<m)&&!F(z[0],z[4],z[5])&&!N(z[0],z[1],z[4])&&!priv(z);
  for(let force of [false,true]){
   n.passes++;let maps=new Map();
   for(let c of ctx){let C,p;
    if(force){let b=(c[0]+c[1]+c[2]+1)%m;C=[b];p=Array(m).fill(b);}
    else{let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>cols.reduce((v,[x,y])=>v+(!F(a,x,y)&&F(b,x,y))+(!N(a,c[0],x)&&N(b,c[0],x)),0))),res=Array(m).fill(37*m*m),cur=Array(m).fill(-1),A=[],best;
     for(let k=1;k<=m;k++){let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!A.includes(j)){let u=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(u<v){v=u;b=j;}}A.push(b);for(let a=0;a<m;a++)if(cur[a]<0||D[a][b]<res[a]){cur[a]=b;res[a]=D[a][b];}ok(res.reduce((s,x)=>s+x,0)===v,"greedy");n.greedy++;if(!best||k*m*m+v<best.v)best={C:A.slice(),p:cur.slice(),v:k*m*m+v};}
     C=best.C;p=best.p;for(let a of C)p[a]=a;
    }maps.set(key(c),{C,p});
   }
   const get=z=>maps.get(key(z.slice(1,4))).p[z[0]];
   for(let mode2 of [0,1]){
    // center=a is exact directed guard; center=0 is a prescribed correction template.
    const center=(a,b)=>mode2===0?a:0,X=make(m,F,get,center,1,B),{M}=X;
    let expected=new Set(),got=new Set();
    for(let z of tup(m,9)){n.fullChecks++;if(!orig(z))continue;
     let y=z.slice();y[0]=get(z);
     if(orig(y)){if(!maps.get(key(z.slice(1,4))).C.includes(y[0]))throw Error("representative");n.successful++;}
     else if(N(y[0],z[1],z[4]))n.narrow++;
     else if(!F(y[0],z[4],z[5])){ok(mode===5&&y[0]===z[6],"private g-containing failure");}
     else{ok(X.E(z.slice(0,6))||F(center(z[0],y[0]),z[4],z[5]),"template or correction recovery");n[mode2?"correction":"wide"]++;}
     if(X.E(z.slice(0,6))||X.belongs(z.slice(0,6)))expected.add(key(z));
    }
    function visit(T,o,t){
     if(T.overflow){for(let z of tup(t,9)){let x=z.map((a,i)=>a+o[i]);if(orig(x)){got.add(key(x));n.abandonedModels++;}}return;}
     if(!T.flag)return;
     if(t===1){if(orig(o))got.add(key(o));return;}
     for(let d of tup(2,9)){let u=t/2,idx=d.slice(0,6).reduce((v,x)=>2*v+x,0);n.fullChildren++;visit(T.ch[idx],o.map((a,i)=>a+d[i]*u),u);}
    }
    for(let q of tup(M/B,9)){let T=X.roots.get(key(q.slice(0,6)));n.fullRoots++;visit(T,q.map(a=>a*B),B);}
    ok(got.size===expected.size&&[...got].every(k=>expected.has(k)),"exact enlarged branch models");n.models+=got.size;
   }
  }
 }
 // Root overflow (three distinct nonzero rows in a side-two context/free cube).
 const F=(a,x,y)=>a>=1&&a<=3&&x===0&&y===0? a!==2 : a>=1&&a<=3&&x===0&&y===1? a!==1:false;
 // Here row 1={00}, row 2={01}, row 3={00,01}.
 const get=z=>z[0]===0?1+(z[1]+2*z[2]+4*z[3])%3:z[0],center=a=>a;
 let A=make(4,F,get,center,1,2),B=make(4,F,get,center,1,4);
 ok(A.over.some(r=>r.t===2)&&B.over.some(r=>r.t===2)&&!B.over.some(r=>r.t===4),"root and child overflow");
 let overflowWitness=0;
 for(let z of tup(4,6))if(A.belongs(z)&&!A.E(z)&&!F(z[0],z[4],z[5]))overflowWitness++;
 ok(overflowWitness>0,"abandonment enlargement");
 // Finite interval-permutation controls: exact traces and wide pair loss.
 let controls=[];
 for(let [m,b,j] of [[16,4,2],[32,8,2],[64,16,4]]){
  let state=0x5a17,rand=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state;};
  let P=Array.from({length:m/b},()=>{let a=Array.from({length:m},(_,i)=>i);for(let k=m-1;k>0;k--){let i=rand()%(k+1);[a[k],a[i]]=[a[i],a[k]];}return a;});
  let raw=(a,x,y)=>((y-P[Math.floor(x/b)][a]+m)%m)<j;
  let maxTrace=0,traceChecks=0,minLoss=m*m,uniform=0;
  for(let t=1;t<=b;t*=2)for(let x=0;x<m;x+=t)for(let y=0;y<m;y+=t){
   let rows=new Set(Array.from({length:m},(_,a)=>Array.from({length:t},(_,v)=>+raw(a,x,y+v)).join("")));
   ok(rows.size<=2*t+1,"interval trace cap");maxTrace=Math.max(maxTrace,rows.size/t);traceChecks++;
  }
  let sums=Array(m).fill(0);
  for(let a=0;a<m;a++)for(let b0=0;b0<m;b0++){
   let v=0;for(let x=0;x<m;x+=b)for(let y=0;y<m;y++)v+=b*(!raw(a,x,y)&&raw(b0,x,y));
   ok(v<=m*j,"pair upper");if(a!==b0)minLoss=Math.min(minLoss,v);sums[b0]+=v;
  }
  ok(sums.every(x=>x===sums[0]),"uniform total directed loss");
  for(let a=0;a<m;a++)for(let x=0;x<m;x+=b)for(let y=0;y<m;y++){ok(Array.from({length:m},(_,b)=>raw(b,x,y)).some(Boolean),"full union");uniform++;}
  controls.push([m,b,j,traceChecks,maxTrace,minLoss,sums[0],uniform]);
 }
 return {n,overflow:[A.over.length,A.mass,B.over.length,B.mass,overflowWitness],controls};
}
console.log('F038_LOCAL_CORRECTION_QUOTIENTS_OK '+JSON.stringify(audit()));
