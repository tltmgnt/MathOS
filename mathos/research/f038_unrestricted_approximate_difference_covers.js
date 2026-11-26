// Host semantic audit; not physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const n={fixtures:0,passes:0,candidates:0,radiusChecks:0,partitionChecks:0,tailChecks:0,capChecks:0,full:0,success:0,heavy:0,narrow:0,template:0,correction:0,union:0,exact:0,templateModels:0,correctionModels:0,unionModels:0,local:0,membership:0,children:0,relabels:0,greedy:0},selected={};
 const id=r=>key([r.a,...r.c]);
 function census(m,F,r){
  let J=Array.from({length:m},()=>Array(m)),W=Array.from({length:m},()=>Array(m)),U=Array.from({length:m},()=>Array(m*m).fill(0));
  for(let a=0;a<m;a++){
   let D=Array.from({length:m},(_,b)=>[...tup(m,2)].map(([x,y])=>+(!F(a,x,y)&&F(b,x,y))));
   for(let j of [a,...Array.from({length:m},(_,b)=>b).filter(b=>b!==a)]){
    if(J[a][j]!==undefined)continue;
    for(let b=0;b<m;b++)if(J[a][b]===undefined){
     let dist=D[b].reduce((v,x,i)=>v+(x!==D[j][i]),0);if(dist<=r)J[a][b]=j;
    }
   }
   ok(J[a][a]===a,"self null");
   for(let b=0;b<m;b++){
    let j=J[a][b],T=D[j],E=D[b].map((x,i)=>+(x&&!T[i])),A=T.map((x,i)=>+(x&&!D[b][i]));
    let tw=T.reduce((v,x)=>v+x,0),miss=E.reduce((v,x)=>v+x,0),extra=A.reduce((v,x)=>v+x,0),w=D[b].reduce((v,x)=>v+x,0);
    ok(miss+extra<=r&&w===tw+miss-extra,"radius and weight");n.radiusChecks++;
    ok(D[b].every((x,i)=>x===+(!!((T[i]&&!A[i])||E[i]))&&(!x||T[i]||E[i])),"exact residual identity and cover");n.partitionChecks+=m*m;
    W[a][b]={tw,miss,w};E.forEach((x,i)=>U[a][i]|=x);
   }
  }
  return {J,W,U,eta:U.reduce((v,R)=>v+R.reduce((w,x)=>w+x,0),0)};
 }
 function trim(A,B,C,alpha,Qs){
  let live=A.slice();const cap=t=>Math.floor(C*t**alpha+1e-9);
  for(let Q of Qs)for(let t=B;t>=1;t/=2){
   function groups(L){let G=new Map();for(let r of L){if(!Q.W[r.a][r.b].tw)continue;let k=key([r.a,...r.c.map(x=>Math.floor(x/t))]);if(!G.has(k))G.set(k,[]);G.get(k).push(r);}return G;}
   function top(L){let f=new Map();for(let r of L){let j=Q.J[r.a][r.b];f.set(j,(f.get(j)||0)+1);}return new Set([...f].sort((a,b)=>b[1]-a[1]||a[0]-b[0]).slice(0,cap(t)).map(x=>x[0]));}
   let bound=0,drop=new Set();for(let L of groups(A).values()){let K=top(L);bound+=L.filter(r=>!K.has(Q.J[r.a][r.b])).length;}
   for(let L of groups(live).values()){let K=top(L);for(let r of L)if(!K.has(Q.J[r.a][r.b]))drop.add(id(r));}
   ok(drop.size<=bound,"tail bound");n.tailChecks++;live=live.filter(r=>!drop.has(id(r)));
  }
  for(let Q of Qs)for(let t=B;t>=1;t/=2){let G=new Map();for(let r of live)if(Q.W[r.a][r.b].tw){let k=key([r.a,...r.c.map(x=>Math.floor(x/t))]);if(!G.has(k))G.set(k,new Set());G.get(k).add(Q.J[r.a][r.b]);}
   for(let L of G.values()){ok(L.size<=cap(t),"template cap");n.capChecks++;}
  }return {live,removed:A.length-live.length};
 }
 for(let m of [2,3])for(let mode=0;mode<6;mode++){
  n.fixtures++;let M=1;while(M<m)M*=2;let B=2,ctx=[...tup(m,3)],cols=[...tup(m,2)];
  let F=[{h:[0,4,5],f:(a,x,y)=>mode===0?false:mode===1?a===y&&x!==y:mode===2?a===1&&x===y:(a+x)%m===y},
   {h:[0,6,7],f:(a,x,y)=>mode===5&&(a+y)%m===x}];
  let narrow=(a,c,x)=>mode===2&&a===1&&c===x,priv=z=>mode===3&&!!((z[6]^z[7]^z[8])&1)||mode===4&&z[2]===z[8];
  let orig=z=>z.every(a=>a<m)&&F.every(s=>!s.f(z[0],z[s.h[1]],z[s.h[2]]))&&!narrow(z[0],z[1],z[4])&&!priv(z);
  let censusBy=[0,1,2].map(r=>F.map(s=>census(m,s.f,r))),Q0=censusBy[0];
  for(let force of [false,true]){
   n.passes++;let maps=new Map(),A=[],cap=0,dn=0;
   function nd(a,b,c){return m*cols.filter(([x,y])=>y===0&&!narrow(a,c[0],x)&&narrow(b,c[0],x)).length;}
   for(let c of ctx){
    let C,p;
    if(force){let b=(c[0]+c[1]+c[2]+1)%m;C=[b];p=Array(m).fill(b);}
    else{let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>nd(a,b,c)+Q0.reduce((v,Q)=>v+Q.W[a][b].w,0))),res=Array(m).fill(37*m*m),cur=Array(m).fill(-1),S=[],best;
     for(let k=1;k<=m;k++){let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!S.includes(j)){let w=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(w<v){v=w;b=j;}}S.push(b);for(let a=0;a<m;a++)if(cur[a]<0||D[a][b]<res[a]){cur[a]=b;res[a]=D[a][b];}ok(res.reduce((v,x)=>v+x,0)===v,"greedy");n.greedy++;if(!best||k*m*m+v<best.v)best={C:S.slice(),p:cur.slice(),v:k*m*m+v};}
     C=best.C;p=best.p;for(let a of C)p[a]=a;ok(best.v===C.length*m*m+p.reduce((v,b,a)=>v+D[a][b],0),"self ties");
    }
    maps.set(key(c),{C,p});cap+=C.length;for(let a=0;a<m;a++){A.push({a,c,b:p[a]});dn+=nd(a,p[a],c);}
   }
   let cand=[];
   for(let r of [0,1,2])for(let C of [1,2]){
    let Qs=censusBy[r],X=trim(A,B,C,1,Qs),tw=X.live.reduce((v,x)=>v+Qs.reduce((w,Q)=>w+Q.W[x.a][x.b].tw,0),0);
    let miss=Qs.map(Q=>A.reduce((v,x)=>v+Q.W[x.a][x.b].miss,0)),cost=Qs.map((Q,i)=>Math.min(Q.eta*m**3,4*miss[i])),routes=Qs.map((Q,i)=>Q.eta*m**3<=4*miss[i]?"union":"exact");
    let score=BigInt((cap+X.removed)*m*m+dn)+BigInt(C)**13n*BigInt(tw)+BigInt(cost.reduce((v,x)=>v+x,0));cand.push({...X,Qs,r,C,tw,miss,routes,score});n.candidates++;
   }
   let best=force?cand[4]:cand.reduce((a,b)=>a.score<=b.score?a:b);
   if(!force){ok(cand.every(x=>x.score>=best.score),"minimum");ok(best.score<=cand[0].score,"exact-radius portfolio");}
   let tag=best.r+","+best.C;selected[tag]=(selected[tag]||0)+1;
   let live=new Set(best.live.map(id)),get=z=>maps.get(key(z.slice(1,4))).p[z[0]],valid=z=>z.every(a=>a<m);
   const actual=(i,z)=>valid(z)&&!F[i].f(z[0],z[F[i].h[1]],z[F[i].h[2]])&&F[i].f(get(z),z[F[i].h[1]],z[F[i].h[2]]);
   const temp=(i,z)=>valid(z)&&live.has(key(z.slice(0,4)))&&!F[i].f(z[0],z[F[i].h[1]],z[F[i].h[2]])&&F[i].f(best.Qs[i].J[z[0]][get(z)],z[F[i].h[1]],z[F[i].h[2]]);
   const err=(i,z)=>actual(i,z)&&!F[i].f(best.Qs[i].J[z[0]][get(z)],z[F[i].h[1]],z[F[i].h[2]]);
   const uni=(i,z)=>valid(z)&&!!best.Qs[i].U[z[0]][z[F[i].h[1]]*m+z[F[i].h[2]]];
   for(let z of tup(m,9)){
    n.full++;if(!orig(z))continue;let y=z.slice();y[0]=get(z);
    for(let i=0;i<2;i++){if(temp(i,z))n.templateModels++;if(err(i,z))n.correctionModels++;if(uni(i,z))n.unionModels++;ok(!err(i,z)||uni(i,z),"union covers correction");}
    if(orig(y)){ok(maps.get(key(z.slice(1,4))).C.includes(y[0]),"rep");n.success++;}
    else if(!live.has(key(z.slice(0,4)))){ok(z[0]!==y[0],"heavy");n.heavy++;}
    else if(!narrow(z[0],z[1],z[4])&&narrow(y[0],z[1],z[4]))n.narrow++;
    else if(F.some((s,i)=>temp(i,z)))n.template++;
    else{let i=F.findIndex((s,i)=>err(i,z));ok(i>=0,"exact correction recovery");n.correction++;if(best.routes[i]==="union"){ok(uni(i,z),"selected union");n.union++;}else n.exact++;}
   }
   for(let i=0;i<2;i++){
    let P=[0,1,2,3,...F[i].h.slice(1)],Q=best.Qs[i];
    const expand=z=>{let x=Array(9).fill(0);P.forEach((g,j)=>x[g]=z[j]);return x;};
    function compact(D,A){let by=new Map(),cnt=new Map(),R=[],used=new Set(A.map(r=>key([r.z[0],r.j])));
     for(let r of D){let k=key([r.a,r.j]);if(!used.has(k))continue;let j=cnt.get(r.a)||0;cnt.set(r.a,j+1);by.set(k,j);R.push({...r,j});}
     return {D:R,A:A.map(r=>{let j=by.get(key([r.z[0],r.j]));ok(j!==undefined,"slot");n.relabels++;return {...r,j};})};
    }
    function root(o,t){let D=[],A=[],by=new Map(),cnt=new Map();
     for(let z of tup(t,4)){let x=z.map((v,j)=>v+o[j]);if(!valid(x)||!live.has(key(x)))continue;let a=x[0],b=get(x),j=Q.J[a][b];if(!Q.W[a][b].tw)continue;let k=key([z[0],j]);
      if(!by.has(k)){let u=cnt.get(z[0])||0;cnt.set(z[0],u+1);by.set(k,u);D.push({a:z[0],j:u,R:[...tup(t,2)].map(([x,y])=>+(x+o[4]<m&&y+o[5]<m&&!F[i].f(a,x+o[4],y+o[5])&&F[i].f(j,x+o[4],y+o[5]))) });}
      A.push({z,j:by.get(k)});
     }return {D,A};
    }
    function visit(X,o,t){let D=new Map(X.D.map(r=>[key([r.a,r.j]),r.R])),A=new Map(X.A.map(r=>[key(r.z),r.j]));let pos=false,corr=0,un=0;
     for(let a=0;a<t;a++)ok(X.D.filter(r=>r.a===a).length<=best.C*t,"local cap");
     for(let z of tup(t,6)){let x=expand(z.map((a,j)=>a+o[j])),R=D.get(key([z[0],A.get(key(z.slice(0,4)))])),v=!!(R&&R[z[4]*t+z[5]]);
      ok(v===temp(i,x),"template clipping");ok(!err(i,x)||uni(i,x),"local correction inclusion");n.membership++;pos ||=v;corr+=err(i,x);un+=uni(i,x);}
     ok(pos===X.A.some(r=>D.get(key([r.z[0],r.j])).some(Boolean)),"positivity");n.local++;
     if(t===1)return [corr,un];
     let tot=[0,0];for(let d of tup(2,6)){let u=t/2,off=d.map(a=>a*u),D=X.D.filter(r=>r.a>=off[0]&&r.a<off[0]+u).map(r=>({...r,a:r.a-off[0],R:[...tup(u,2)].map(([x,y])=>r.R[(x+off[4])*t+y+off[5]])})),A=X.A.filter(r=>r.z.every((a,j)=>a>=off[j]&&a<off[j]+u)).map(r=>({z:r.z.map((a,j)=>a-off[j]),j:r.j}));
      n.children++;let s=visit(compact(D,A),o.map((a,j)=>a+off[j]),u);tot=tot.map((v,j)=>v+s[j]);}
     ok(tot[0]===corr&&tot[1]===un,"correction mass clipping");return tot;
    }
    let sum=[0,0];for(let q of tup(M/B,6)){let o=q.map(a=>a*B),s=visit(root(o,B),o,B);sum=sum.map((v,j)=>v+s[j]);}
    ok(sum[0]===best.miss[i]&&sum[1]===Q.eta*m**3,"exact expanded masses");
   }
  }
 }
 const parity=x=>{let v=0;while(x){v^=x&1;x>>=1;}return v;};let controls=[];
 for(let m of [16,32,64]){
  let q=m/2,J=m/16,T=a=>a>=m/2&&a<m/2+q;
  const F=(a,x,y)=>T(a)?y<J||(y===J&&x===a-m/2)||(y>=m/4&&y<m/2&&!!(parity(a&x)^(y&1))):y>=m/4&&y<m/2||y>=m/2&&!!(parity(a&x)^(y&1));
  let Q=census(m,F,2),Q0=census(m,F,0),checks=0,greedy=0,un=0;
  for(let a=0;a<m/2;a++){
   let b=Array.from({length:q},(_,i)=>i+m/2);ok(new Set(b.map(x=>Q0.J[a][x])).size===q,"exact distinct");ok(new Set(b.map(x=>Q.J[a][x])).size===1,"approx collapse");
   for(let x of b){ok(Q.W[a][x].w===m*J+1&&Q.W[a][x].miss<=1,"marker correction");checks++;}
   ok(Q.U[a].reduce((v,x)=>v+x,0)===q-1,"outside union markers");un+=q-1;
  }
  let d=Math.log2(m),r=d-1,even=0,odd=0;for(let j=0;j<r;j++)if(j%2)odd|=1<<j;else even|=1<<j;
  for(let f=m/2;f<m;f++){
   let D=(a,b)=>Q.W[a][b].w+m*m*(+(T(a)&&!T(b))+ +((a&even)===(f&even)&&(b&even)!==(f&even))+ +((a&odd)===(f&odd)&&(b&odd)!==(f&odd)));
   let s=Array.from({length:m},(_,b)=>Array.from({length:m},(_,a)=>D(a,b)).reduce((v,x)=>v+x,0));ok(s.every((v,b)=>b===f||v>s[f]),"unique target");
   for(let b=0;b<m;b++)if(b!==f){let gain=0;for(let a=0;a<m;a++)gain+=Math.max(0,D(a,f)-D(a,b));ok(gain<m*m,"stop");greedy++;}
  }
  controls.push([m,q,checks,un,greedy,Q.eta]);
 }
 // Independent false-positive template, one-sided correction, and route normalization controls.
 let Q=census(4,(a,x,y)=>a>0&&x===a&&y===0,2);
 ok(Q.J[0][1]===0&&Q.W[0][1].miss===1,"null template corrected");
 let correctionControl=[Q.W[0][1].miss,Q.eta];
 return {n,selected,controls,correctionControl};
}
console.log('F038_APPROXIMATE_DIFFERENCE_COVERS_OK '+JSON.stringify(audit()));
