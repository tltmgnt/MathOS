// Host semantic and arithmetic audit, not physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],K=[1,2,3],P=[0,...K],key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 let totals=Array(12).fill(0),forced=Array(12).fill(0),fixtures=0,comparisons=0,greedyChecks=0,rateChecks=0,thresholds=0,strictFixtures=0;
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  let R=H.map(h=>({h,F:new Set([...tup(m,h.length)].filter(z=>{
   if(mode===0)return false;
   if(mode===1)return h.length===1&&h[0]===8;
   if(mode===2)return h.length===2&&z[0]===z[1];
   if(mode===3)return key(h)==="0,4,5"&&z[0]===z[2]&&z[1]!==z[2];
   if(mode===4)return key(h)==="0,1,4"&&z[0]===1&&z[1]===z[2];
   if(mode===5)return h.length===3&&(h.reduce((s,a)=>s+a,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===6)return h.length===1&&z[0]!==h[0]%m;
   return key(h)==="0,4,5"&&z[1]===0&&z[0]!==z[2]||h.length===2&&h[0]===0&&z[0]===z[1];
  }).map(key))}));
  let S=R.filter(T=>T.h.includes(0)).map(T=>{
   let O=T.h.filter(g=>g!==0&&!K.includes(g)),Q=[...new Set([...T.h,...K])].sort((a,b)=>a-b);
   function lost(a,b,c){return [...tup(m,O.length)].filter(z=>{let x=T.h.map(g=>g===0?a:K.includes(g)?c[K.indexOf(g)]:z[O.indexOf(g)]),y=x.slice();y[0]=b;return !T.F.has(key(x))&&T.F.has(key(y));});}
   return {T,O,Q,lost,wide:O.length===2};
  }),wide=S.filter(s=>s.wide),narrow=S.filter(s=>!s.wide),ell=wide.map(s=>Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>s.lost(a,b,[]).length)));
  let ctx=[...tup(m,3)].map(c=>({c,N:Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>narrow.reduce((v,s)=>v+s.lost(a,b,c).length*m**(2-s.O.length),0)))}));
  let rs=[0];for(let r=1;r<m*m;r*=2)rs.push(r);rs.push(m*m);
  // Exponent 1 here tests scoring mechanics only, not the implementation-dependent production exponent.
  let weight=1+Math.ceil(Math.log2(m));
  function choose(r,force){
   let maps=new Map(),cap=0,heavy=0,loss=0;
   for(let {c,N} of ctx){
    let W=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>ell.some(E=>E[a][b]>r)));
    let D=N.map((row,a)=>row.map((v,b)=>v+(W[a][b]?m*m:0)));
    let C=[],res=Array(m).fill(37*m*m),p=Array(m).fill(-1),best=null,profile=[];
    if(force){let b=(c.reduce((s,v)=>s+v,0)+1)%m;best={C:[b],p:Array(m).fill(b)};}
    else{
     for(let k=1;k<=m;k++){
      let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!C.includes(j)){let f=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(f<v){b=j;v=f;}}
      C.push(b);for(let a=0;a<m;a++)if(p[a]<0||D[a][b]<res[a]){p[a]=b;res[a]=D[a][b];}
      ok(v===res.reduce((s,v)=>s+v,0),"residual");profile.push(v);
      if(!best||k*m*m+v<best.score)best={C:C.slice(),p:p.slice(),score:k*m*m+v};
     }
     for(let mask=1;mask<2**m;mask++){
      let X=Array.from({length:m},(_,a)=>a).filter(a=>mask>>a&1),h=X.length,opt=D.reduce((s,row)=>s+Math.min(...X.map(b=>row[b])),0),prev=37*m**3;
      for(let v of profile){ok(h*(prev-v)>=prev-opt,"marginal gain");prev=v;greedyChecks++;}
      let k=Math.min(m,Math.ceil(h*(1+Math.log(m/h))));
      ok(profile[k-1]<=opt+37*m**3*Math.exp(-k/h)+1e-8,"exponential residual");
      ok(best.score<=m*m*(h*(1+Math.log(m/h))+1)+opt+37*m*m*h/Math.E+1e-8,"entropy comparison");comparisons++;
     }
    }
    let n=0,w=0;for(let a=0;a<m;a++){w+=W[a][best.p[a]];n+=N[a][best.p[a]];}
    if(!force)ok(best.score===(best.C.length+w)*m*m+n,"score identity");
    cap+=best.C.length;heavy+=w;loss+=n;maps.set(key(c),{...best,W});
   }
   return {r,maps,cap,heavy,loss,score:(cap+heavy)*m*m+loss+weight*r*m**4};
  }
  let candidates=rs.map(r=>choose(r,false));thresholds+=rs.length;
  let best=candidates.slice().sort((a,b)=>a.score-b.score||a.r-b.r)[0];ok(candidates.every(v=>v.score>=best.score),"threshold minimum");
  function recover(B){
   let A=new Set(),E=S.map(s=>({s,A:new Set()})),wideMass=0,narrowMass=0,fullWideMass=0,discarded=0;
   for(let c of tup(m,3))for(let a=0;a<m;a++){
    let v=B.maps.get(key(c));if(v.C.includes(a)||v.W[a][v.p[a]])A.add(key([a,...c]));
   }
   ok(A.size===B.cap+B.heavy,"envelope density");
   for(let e of E){
    let {s}=e;
    for(let z of tup(m,s.Q.length)){
     let a=z[0],c=K.map(g=>z[s.Q.indexOf(g)]),v=B.maps.get(key(c)),b=v.p[a],x=s.T.h.map(g=>z[s.Q.indexOf(g)]),y=x.slice();y[0]=b;
     if(!s.T.F.has(key(x))&&s.T.F.has(key(y))){
      if(s.wide){fullWideMass++;if(v.W[a][b]){discarded++;continue;}}
      e.A.add(key(z));
     }
    }
    if(s.wide){wideMass+=e.A.size;ok(e.A.size<=m**4*B.r,"light wide density bound");}
    else narrowMass+=e.A.size*m**(6-s.Q.length);
   }
   ok(narrowMass===B.loss,"narrow loss mass");ok(fullWideMass===discarded+wideMass,"wide partition");
   let orig=z=>R.every(T=>!T.F.has(key(proj(z,T.h)))),models=0,restricted=0,replaced=0,hFail=0,wFail=0,nFail=0,checks=0;
   for(let z of tup(m,9)){
    checks++;if(!orig(z))continue;models++;let c=proj(z,K),a=z[0],v=B.maps.get(key(c)),b=v.p[a],y=z.slice();y[0]=b;
    let env=A.has(key(proj(z,P))),we=E.some(e=>e.s.wide&&e.A.has(key(proj(z,e.s.Q)))),ne=E.some(e=>!e.s.wide&&e.A.has(key(proj(z,e.s.Q))));
    if(env||we||ne)restricted++;
    if(orig(y)){replaced++;ok(A.has(key(proj(y,P))),"representative");}
    else if(v.W[a][b]){hFail++;ok(env,"heavy fallback");}
    else if(wide.some(s=>s.T.F.has(key(proj(y,s.T.h))))){wFail++;ok(we,"exact light exception");}
    else{nFail++;ok(ne,"narrow");}
   }
   ok(!models||restricted,"existence");if(B.r===0)ok(wideMass===0,"zero threshold");
   return [B.cap,B.heavy,wideMass,discarded,models,restricted,replaced,hFail,wFail,nFail,checks,narrowMass];
  }
  recover(best).forEach((v,i)=>totals[i]+=v);
  for(let r of rs){let v=recover(choose(r,true));v.forEach((x,i)=>forced[i]+=x);if(v[7]&&v[8])strictFixtures++;}
  fixtures++;
 }
 // Check threshold comparison and dyadic rounding using exact integer arithmetic for sampled loss masses.
 let rateCases=[];
 for(let m=2;m<=512;m++){
  let M=BigInt(m),l=BigInt(1+Math.ceil(Math.log2(m))),W=l**8n;
  let rs=[0n];for(let r=1n;r<M*M;r*=2n)rs.push(r);rs.push(M*M);
  for(let n of [0n,1n,M,M**2n,M**3n,M**4n,M**5n,M**6n]){
   let delta=Number(n)/m**6,w=Number(W),target=Math.min(1,Math.sqrt(delta/w));
   let r=n===0n?0n:rs.find(r=>r>0n&&r*r*W*M*M>=n)||M*M;
   let tau=Number(r)/m**2;
   if(n===0n)ok(r===0n,"zero comparison");
   else{ok(tau>=target-1e-15,"threshold rounding");ok(tau<=2*Math.max(1/m**2,target)+1e-15,"dyadic factor");ok(delta/tau+w*tau<=3*Math.sqrt(delta*w)+w/m**2+1e-7*Math.max(1,w),"penalty comparison");}
   rateChecks++;
  }
 }
 // Arithmetic control: width-six average loss can be polynomial while capacity/narrow loss decay only logarithmically.
 for(let k of [8,16,32,64,128]){
  let m=2**k,beta=1/Math.log2(k),deltaN=1/Math.log2(k),deltaW=1/m,weighted=deltaW*(1+k)**8;
  rateCases.push([k,beta,deltaN,deltaW,weighted]);
 }
 return {fixtures,totals,forced,comparisons,greedyChecks,thresholds,rateChecks,strictFixtures,rateCases};
}
console.log('F038_MIXED_RATE_RECOVERY_OK '+JSON.stringify(audit()));
