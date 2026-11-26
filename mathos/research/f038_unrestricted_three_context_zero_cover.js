// Standalone semantic reference, not physical tape execution.
function audit(){
 const need=(x,s)=>{if(!x)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* sub(A,k,i=0,p=[]){if(p.length===k){yield p;return;}for(let j=i;j<=A.length-k+p.length;j++)yield* sub(A,k,j+1,p.concat(A[j]));}
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const H=[...sub(G,1),...sub(G,2),...sub(G,3)],proj=(z,h)=>h.map(g=>z[g]);
 function greedy(D){
  let m=D.length,U=Array(m).fill(true),C=[],best=null,profile=[];
  for(let k=1;k<=m;k++){
   let b=-1,gain=-1;
   for(let j=0;j<m;j++)if(!C.includes(j)){
    let n=U.reduce((s,u,a)=>s+(u&&D[a][j]===0),0);if(n>gain){gain=n;b=j;}
   }
   C.push(b);U=U.map((u,a)=>u&&D[a][b]!==0);
   let n=U.filter(Boolean).length;profile.push(n);
   if(!best||k+n<best.score)best={C:C.slice(),U:U.slice(),score:k+n};
  }
  for(let mask=1;mask<2**m;mask++){
   let A=Array.from({length:m},(_,a)=>a).filter(a=>mask>>a&1),u=D.filter(row=>A.every(b=>row[b]!==0)).length,prev=m;
   for(let n of profile){need(A.length*(prev-n)>=prev-u,"greedy gain");prev=n;}
  }
  need(best.score<=m,"self-cover");
  return best;
 }
 let factors=0,greedyContexts=0,totals=Array(9).fill(0),forced=Array(3).fill(0);
 for(let m of [2,3])for(let mode=0;mode<7;mode++){
  let g=mode%2?8:0,K=mode%2?[0,3,6]:[1,2,3],P=[g,...K],R=H.map(h=>({h,bad:new Set([...tuples(m,h.length)].filter(z=>{
   if(mode===0)return false;
   if(mode===1)return h.length===1&&h[0]===g;
   if(mode===2)return h.length===2&&z[0]===z[1];
   if(mode===3)return h.length===3&&(h.reduce((s,a)=>s+a,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===4)return h.length===3&&z.some(a=>a!==0);
   if(mode===5)return h.length===1&&z[0]!==h[0]%m;
   return h.includes(g)&&z[h.indexOf(g)]===1&&z.every(a=>a!==0);
  }).map(key))}));
  let sections=R.filter(T=>T.h.includes(g)).map(T=>{
   let J=T.h.filter(i=>K.includes(i)),O=T.h.filter(i=>i!==g&&!K.includes(i)),w=m**(2-O.length),tab=new Map();
   function count(a,b,c){let n=0;for(let z of tuples(m,O.length)){
    let x=T.h.map(i=>i===g?a:J.includes(i)?c[J.indexOf(i)]:z[O.indexOf(i)]),y=x.slice();y[T.h.indexOf(g)]=b;
    n+=(!T.bad.has(key(x))&&T.bad.has(key(y)))*w;
   }return n;}
   if(J.length<2)for(let c of tuples(m,J.length))for(let a=0;a<m;a++)for(let b=0;b<m;b++)tab.set(key([...c,a,b]),count(a,b,c));
   return {T,J,O,tab,count};
  });
  let choices=new Map(),score=0,nrep=0,nun=0;
  for(let c of tuples(m,3)){
   let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>{
    let f=0,d=0;for(let S of sections){let x=S.J.map(i=>c[K.indexOf(i)]);d+=S.count(a,b,x);
     if(S.J.length===2){let z=S.T.h.map(i=>i===g?a:c[K.indexOf(i)]),y=z.slice();y[S.T.h.indexOf(g)]=b;f+=(!S.T.bad.has(key(z))&&S.T.bad.has(key(y)))*m*m;}
     else f+=S.tab.get(key([...x,a,b]));
    }need(d===f,"factorization");factors++;return f;
   }));
   let v=greedy(D);greedyContexts++;score+=v.score;nrep+=v.C.length;nun+=v.U.filter(Boolean).length;choices.set(key(c),{...v,D});
  }
  let A=(a,c)=>{let v=choices.get(key(c));return v.C.includes(a)||v.U[a];};
  let orig=z=>R.every(T=>!T.bad.has(key(proj(z,T.h)))),models=0,recovered=0,replaced=0,uncovered=0,checks=0,forcedFail=0,forcedCovered=0,forcedModels=0;
  for(let z of tuples(m,9)){
   checks++;if(!orig(z))continue;models++;
   let c=proj(z,K),a=z[g],v=choices.get(key(c));
   if(A(a,c))recovered++;
   if(v.U[a]){uncovered++;need(A(a,c),"uncovered envelope");}
   else{let b=v.C.find(b=>v.D[a][b]===0),y=z.slice();y[g]=b;need(orig(y)&&A(b,c),"zero-loss substitution");replaced++;}
   let b=(c.reduce((s,x)=>s+x,0)+1)%m,y=z.slice();y[g]=b;
   if(v.D[a][b]!==0){forcedCovered++;if(!orig(y))forcedFail++;}
   else need(orig(y),"forced safe substitution");
   if(a===b||v.D[a][b]!==0)forcedModels++;
  }
  need(!models||recovered>0,"existence of restricted model");
  need(!models||forcedModels>0,"forced existence");
  // Coarse block membership stream: each real (a,c) must occur exactly once.
  let M=1;while(M<m)M*=2;let b=2,seen=new Set(),roots=0,entries=0;
  for(let cb of tuples(M/b,3)){
   let saved=new Map();
   for(let u of tuples(b,3)){let c=u.map((x,i)=>x+b*cb[i]);if(c.some(x=>x>=m))continue;
    for(let a=0;a<m;a++)saved.set(key([a,...c]),A(a,c));}
   need(saved.size<=m*b**3,"context block capacity");
   for(let ab=0;ab<M/b;ab++){
    let flags=[];for(let z of tuples(b,4)){
     let x=[z[0]+ab*b,...z.slice(1).map((v,i)=>v+cb[i]*b)],valid=x.every(v=>v<m),flag=valid&&saved.get(key(x));
     if(valid){need(!seen.has(key(x)),"disjoint projection blocks");seen.add(key(x));need(flag===A(x[0],x.slice(1)),"block membership");}
     if(flag)entries++;flags.push(+flag);
    }need(flags.some(Boolean)===(flags.reduce((s,v)=>s+v,0)>0),"root flag");roots++;
   }
  }
  need(seen.size===m**4&&entries===score,"exact representative/uncovered disjoint union");
  [nrep,nun,models,recovered,replaced,uncovered,checks,roots,entries].forEach((x,i)=>totals[i]+=x);
  [forcedCovered,forcedFail,forcedModels].forEach((x,i)=>forced[i]+=x);
 }
 const par=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 let controls=[];
 for(let q of [4,8,16,32]){
  let max=0,n=0,min=Infinity;
  for(let c of tuples(q-1,3)){
   let x=c.map(a=>a+1),C=new Map();
   for(let a=1;a<q;a++){let k=key(x.map(v=>par(v&a)));if(!C.has(k))C.set(k,a);
    let b=C.get(k);need(x.every(v=>par(v&a)===par(v&b)),"fiber preservation");
    for(let i=0;i<3;i++)for(let j=i+1;j<3;j++)need(par(a&(x[i]^x[j]))===par(b&(x[i]^x[j])),"main triple preservation");n++;}
   max=Math.max(max,C.size);
  }
  // All distinct nonzero vectors, fixed nonzero context, unconditioned third vector.
  for(let a=1;a<q;a++)for(let b=1;b<q;b++)if(a!==b)for(let c=1;c<q;c++){
   let d=0;for(let x=1;x<q;x++)d+=par(a&(c^x))===0&&par(b&(c^x))===1;min=Math.min(min,d);
  }
  need(min===q/4-1&&max<=8,"two-context obstruction");
  controls.push([q,max,n,min]);
 }
 let allDifferent=[];
 for(let m of [9,12,20]){
  let maxLoss=0;for(let c of tuples(m,3)){let b=Array.from({length:m},(_,i)=>i).find(a=>!c.includes(a));
   for(let a=0;a<m;a++){
    let d=a===b?0:5*m;maxLoss=Math.max(maxLoss,d);
    need((a===b)===(d===0),"distinct source has positive loss");
   }
  }allDifferent.push([m,maxLoss]);
 }
 return {fixtures:14,totals,forced,factors,greedyContexts,controls,allDifferent};
}
console.log('F038_THREE_CONTEXT_ZERO_COVER_OK '+JSON.stringify(audit()));
