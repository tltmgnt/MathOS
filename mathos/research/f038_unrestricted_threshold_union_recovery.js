// Standalone semantic regression; no physical tape measurements.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(A,k,i=0,p=[]){if(p.length===k){yield p;return;}for(let j=i;j<=A.length-k+p.length;j++)yield* sub(A,k,j+1,p.concat(A[j]));}
 const H=[...sub(G,1),...sub(G,2),...sub(G,3)],proj=(z,h)=>h.map(g=>z[g]),g=0,K=[1,2,3],P=[g,...K];
 let fixtures=0,totals=Array(11).fill(0),forced=Array(11).fill(0),unionChecks=0,greedyChecks=0,thresholdChecks=0;
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  let R=H.map(h=>({h,bad:new Set([...tuples(m,h.length)].filter(z=>{
   if(mode===0)return false;
   if(mode===1)return h.length===1&&h[0]===8;
   if(mode===2)return h.length===2&&z[0]===z[1];
   if(mode===3)return key(h)==="0,4,5"&&z[0]===z[1]&&z[1]===z[2];
   if(mode===4)return key(h)==="0,1,4"&&z[0]===1&&z[1]===z[2];
   if(mode===5)return h.length===3&&(h.reduce((s,a)=>s+a,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===6)return h.length===1&&z[0]!==h[0]%m;
   return key(h)==="0,4,5"&&z[1]===0&&z[0]!==z[2]||h.length===2&&h[0]===0&&z[0]===z[1];
  }).map(key))}));
  let sections=R.filter(T=>T.h.includes(g)).map(T=>{
   let J=T.h.filter(i=>K.includes(i)),O=T.h.filter(i=>i!==g&&!K.includes(i)),wide=O.length===2,Q=[...new Set([...T.h,...K])].sort((a,b)=>a-b);
   function loss(a,b,c){let A=[];for(let z of tuples(m,O.length)){let x=T.h.map(i=>i===g?a:J.includes(i)?c[K.indexOf(i)]:z[O.indexOf(i)]),y=x.slice();y[0]=b;if(!T.bad.has(key(x))&&T.bad.has(key(y)))A.push(z);}return A;}
   return {T,J,O,wide,Q,loss};
  });
  let wide=sections.filter(s=>s.wide),narrow=sections.filter(s=>!s.wide);
  let levels=[0];for(let r=1;r<m*m;r*=2)levels.push(r);levels.push(m*m);
  const union=(s,r)=>{
   let U=new Set();for(let a=0;a<m;a++)for(let b=0;b<m;b++){let Z=s.loss(a,b,[]);if(Z.length<=r)for(let z of Z)U.add(key([a,...z]));}
   for(let [a,u,v] of tuples(m,3)){let flag=false;for(let b=0;b<m;b++){let Z=s.loss(a,b,[]);flag ||=Z.length<=r&&Z.some(z=>z[0]===u&&z[1]===v);}
    ok(flag===U.has(key([a,u,v])),"exact row union");unionChecks++;}
   ok(U.size<=Math.min(m**3,m*m*r),"union bound");return U;
  };
  let candidates=levels.map(r=>({r,U:wide.map(s=>union(s,r))}));
  function choose({r,U},arbitrary){
   let maps=new Map(),score=U.reduce((s,A)=>s+A.size,0)*m**3,rep=0,heavy=0,loss=0;
   for(let c of tuples(m,3)){
    let W=Array.from({length:m},()=>Array(m).fill(false)),N=Array.from({length:m},()=>Array(m).fill(0)),D=Array.from({length:m},()=>Array(m).fill(0));
    for(let a=0;a<m;a++)for(let b=0;b<m;b++){
     W[a][b]=wide.some(s=>s.loss(a,b,[]).length>r);
     N[a][b]=narrow.reduce((v,s)=>v+s.loss(a,b,c).length*m**(2-s.O.length),0);D[a][b]=N[a][b]+(W[a][b]?m*m:0);
    }
    let best=null;
    if(arbitrary){let b=(c.reduce((s,a)=>s+a,0)+1)%m;best={C:[b],p:Array(m).fill(b)};}
    else{
     let C=[],p=Array(m).fill(-1),res=Array(m).fill(37*m*m),profile=[];
     for(let k=1;k<=m;k++){
      let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!C.includes(j)){let n=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(n<v){v=n;b=j;}}
      C.push(b);for(let a=0;a<m;a++)if(p[a]<0||D[a][b]<res[a]){res[a]=D[a][b];p[a]=b;}
      profile.push(v);if(!best||k*m*m+v<best.score)best={C:C.slice(),p:p.slice(),score:k*m*m+v};
     }
     for(let mask=1;mask<2**m;mask++){
      let C=Array.from({length:m},(_,a)=>a).filter(a=>mask>>a&1),opt=D.reduce((s,row)=>s+Math.min(...C.map(b=>row[b])),0),prev=37*m**3;
      for(let v of profile){ok(C.length*(prev-v)>=prev-opt,"greedy");prev=v;greedyChecks++;}
     }
    }
    let h=0,l=0;for(let a=0;a<m;a++){h+=W[a][best.p[a]];l+=N[a][best.p[a]];}
    if(!arbitrary)ok(best.score===(best.C.length+h)*m*m+l,"score identity");
    rep+=best.C.length;heavy+=h;loss+=l;score+=(best.C.length+h)*m*m+l;maps.set(key(c),{...best,W,N});
   }
   return {r,U,maps,score,rep,heavy,loss};
  }
  let chosen=candidates.map(x=>choose(x,false)).sort((a,b)=>a.score-b.score||a.r-b.r)[0];
  function recover(B){
   let orig=z=>R.every(T=>!T.bad.has(key(proj(z,T.h)))),A=new Set(),E=narrow.map(s=>({s,A:new Set()}));
   for(let c of tuples(m,3))for(let a=0;a<m;a++){let v=B.maps.get(key(c)),b=v.p[a];if(v.C.includes(a)||v.W[a][b])A.add(key([a,...c]));}
   for(let {s,A} of E)for(let z of tuples(m,s.Q.length)){
    let c=K.map(i=>z[s.Q.indexOf(i)]),a=z[s.Q.indexOf(g)],b=B.maps.get(key(c)).p[a],x=s.T.h.map(i=>z[s.Q.indexOf(i)]),y=x.slice();y[0]=b;
    if(!s.T.bad.has(key(x))&&s.T.bad.has(key(y)))A.add(key(z));
   }
   ok(E.reduce((s,x)=>s+x.A.size*m**(6-x.s.Q.length),0)===B.loss,"narrow mass");
   let model=0,restricted=0,replaced=0,failHeavy=0,failUnion=0,failNarrow=0,checks=0;
   for(let z of tuples(m,9)){
    checks++;if(!orig(z))continue;model++;let c=proj(z,K),a=z[g],v=B.maps.get(key(c)),b=v.p[a],y=z.slice();y[g]=b;
    let env=A.has(key(proj(z,P))),u=wide.some((s,i)=>B.U[i].has(key(proj(z,s.T.h)))),e=E.some(x=>x.A.has(key(proj(z,x.s.Q))));
    if(env||u||e)restricted++;
    if(orig(y)){replaced++;ok(A.has(key(proj(y,P))),"representative branch");}
    else if(v.W[a][b]){failHeavy++;ok(env,"heavy envelope");}
    else{
     let w=wide.some(s=>s.T.bad.has(key(proj(y,s.T.h))));if(w){failUnion++;ok(u,"projected union");}
     else{failNarrow++;ok(e,"narrow recovery");}
    }
   }ok(!model||restricted,"exact existence");
   return [B.rep,B.heavy,B.loss,B.U.reduce((s,A)=>s+A.size,0),model,restricted,replaced,failHeavy,failUnion,failNarrow,checks];
  }
  recover(chosen).forEach((v,i)=>totals[i]+=v);
  // Exercise threshold zero and maximum, not merely zero-loss adaptive small fixtures.
  for(let T of [candidates[0],candidates.at(-1)])recover(choose(T,true)).forEach((v,i)=>forced[i]+=v);
  fixtures++;
  for(let r of levels){ok(r>=0&&r<=m*m,"threshold range");thresholdChecks++;}
 }
 const par=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 let controls=[];
 for(let q of [8,16,32,64]){
  let m=q-1,s=Math.floor(Math.sqrt(q)),min=Infinity,max=0,entries=0;
  for(let a=1;a<q;a++){
   let U=new Set();for(let b=1;b<q;b++)if(a!==b){
    let Z=0;for(let u=1;u<=s;u++)for(let v=1;v<q;v++)if(!par(a&v)&&par(b&v)){Z++;U.add(key([u,v]));}
    min=Math.min(min,Z);max=Math.max(max,Z);ok(Z===s*q/4,"large individual loss");
   }entries+=U.size;ok(U.size===s*(q/2-1),"exact union row");
  }
  ok(entries===m*s*(q/2-1),"union density");
  controls.push([m,s,min,max,entries]);
 }
 return {fixtures,totals,forced,unionChecks,greedyChecks,thresholdChecks,controls};
}
console.log('F038_THRESHOLD_UNION_RECOVERY_OK '+JSON.stringify(audit()));
