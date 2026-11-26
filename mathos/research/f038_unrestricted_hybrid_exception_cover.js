// Host semantic audit; not physical-tape execution.
function audit(){
 const assert=(b,s)=>{if(!b)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* sub(A,k,i=0,p=[]){if(p.length===k){yield p;return;}for(let j=i;j<=A.length-k+p.length;j++)yield* sub(A,k,j+1,p.concat(A[j]));}
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const H=[...sub(G,1),...sub(G,2),...sub(G,3)],proj=(z,h)=>h.map(g=>z[g]),g=0,K=[1,2,3],P=[g,...K];
 let total=Array(10).fill(0),forced=Array(10).fill(0),matrixChecks=0,greedyChecks=0,blockChecks=0;
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  let R=H.map(h=>({h,bad:new Set([...tuples(m,h.length)].filter(z=>{
   if(mode===0)return false;
   if(mode===1)return h.length===1&&h[0]===8;
   if(mode===2)return h.length===2&&z[0]===z[1];
   if(mode===3)return key(h)==="0,4,5"&&z[0]===1&&z[1]===z[2];
   if(mode===4)return key(h)==="0,1,4"&&z[0]===1&&z[1]===z[2];
   if(mode===5)return h.length===3&&(h.reduce((s,a)=>s+a,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===6)return h.length===1&&z[0]!==h[0]%m;
   return h.length===2&&h[0]===0&&h[1]>=4&&z[0]===1&&z[1]===1||key(h)==="0,4,5"&&z[0]===1&&z[1]!==z[2];
  }).map(key))}));
  let S=R.filter(T=>T.h.includes(g)).map(T=>{
   let J=T.h.filter(i=>K.includes(i)),O=T.h.filter(i=>i!==g&&!K.includes(i)),Q=[...new Set([...T.h,...K])].sort((a,b)=>a-b),wide=Q.length===6,cache=new Map();
   function d(a,b,c){let n=0;for(let z of tuples(m,O.length)){
    let x=T.h.map(i=>i===g?a:J.includes(i)?c[J.indexOf(i)]:z[O.indexOf(i)]),y=x.slice();y[0]=b;
    n+=(!T.bad.has(key(x))&&T.bad.has(key(y)))*m**(2-O.length);
   }return n;}
   if(J.length<2)for(let c of tuples(m,J.length))for(let a=0;a<m;a++)for(let b=0;b<m;b++)cache.set(key([...c,b,a]),d(a,b,c));
   return {T,J,O,Q,wide,cache,d};
  });
  let chosen=new Map(),arbitrary=new Map();
  for(let c of tuples(m,3)){
   let D=Array.from({length:m},()=>Array(m).fill(0)),W=Array.from({length:m},()=>Array(m).fill(false)),N=Array.from({length:m},()=>Array(m).fill(0));
   for(let a=0;a<m;a++)for(let b=0;b<m;b++){
    let wide=false,n=0;
    for(let s of S){let j=s.J.map(i=>c[K.indexOf(i)]),v=s.J.length<2?s.cache.get(key([...j,b,a])):m*m*(+(!s.T.bad.has(key(s.T.h.map(i=>i===g?a:c[K.indexOf(i)])))&&s.T.bad.has(key(s.T.h.map(i=>i===g?b:c[K.indexOf(i)])))));
     assert(v===s.d(a,b,j),"factorized section");matrixChecks++;
     if(s.wide)wide ||=v>0;else n+=v;
    }
    W[a][b]=wide;N[a][b]=n;D[a][b]=n+(wide?m*m:0);
   }
   let C=[],res=Array(m).fill(37*m*m),p=Array(m).fill(-1),best=null,profile=[];
   for(let k=1;k<=m;k++){
    let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!C.includes(j)){let f=res.reduce((s,r,a)=>s+Math.min(r,D[a][j]),0);if(f<v){v=f;b=j;}}
    C.push(b);for(let a=0;a<m;a++)if(p[a]<0||D[a][b]<res[a]){res[a]=D[a][b];p[a]=b;}
    profile.push(v);assert(v===res.reduce((s,r)=>s+r,0),"residual");
    if(!best||k*m*m+v<best.score)best={C:C.slice(),p:p.slice(),score:k*m*m+v};
   }
   for(let mask=1;mask<2**m;mask++){
    let A=Array.from({length:m},(_,a)=>a).filter(a=>mask>>a&1),opt=D.reduce((s,r)=>s+Math.min(...A.map(b=>r[b])),0),prev=37*m**3;
    for(let v of profile){assert(A.length*(prev-v)>=prev-opt,"greedy bound");prev=v;greedyChecks++;}
   }
   chosen.set(key(c),{...best,W,N});let b=(c.reduce((s,a)=>s+a,0)+1)%m;arbitrary.set(key(c),{C:[b],p:Array(m).fill(b),W,N});
  }
  const orig=z=>R.every(T=>!T.bad.has(key(proj(z,T.h))));
  function check(M,blocks){
   let A=new Set(),error=0,cap=0,wideCount=0,smallWeighted=0;
   for(let c of tuples(m,3)){let v=M.get(key(c)),u=0,n=0;
    for(let a=0;a<m;a++){
     let b=v.p[a],w=v.W[a][b];u+=w;n+=v.N[a][b];
     if(v.C.includes(a)||w)A.add(key([a,...c]));
    }
    cap+=v.C.length;wideCount+=u;smallWeighted+=n;
    if(v.score!==undefined){assert(v.score===(v.C.length+u)*m*m+n,"hybrid score");assert(v.C.every(a=>!v.W[a][v.p[a]]),"center not wide");}
   }
   let E=S.filter(s=>!s.wide).map(s=>{
    let list=new Set();for(let z of tuples(m,s.Q.length)){let a=z[s.Q.indexOf(g)],c=K.map(i=>z[s.Q.indexOf(i)]),v=M.get(key(c)),x=s.T.h.map(i=>z[s.Q.indexOf(i)]),y=x.slice();y[0]=v.p[a];
     if(!s.T.bad.has(key(x))&&s.T.bad.has(key(y)))list.add(key(z));
    }error+=list.size*m**(6-s.Q.length);return {Q:s.Q,list};
   });
   assert(error===smallWeighted,"exact small loss");
   if(blocks){
    let Mpad=1;while(Mpad<m)Mpad*=2;let b=2;
    for(let Q of [{Q:P,list:A},...E.filter(e=>e.list.size)]){
     let seen=new Set();
     for(let cb of tuples(Mpad/b,3)){
      let saved=new Map();for(let u of tuples(b,3)){let c=u.map((x,i)=>x+cb[i]*b);if(c.every(a=>a<m))saved.set(key(c),M.get(key(c)));}
      assert(saved.size*m<=m*b**3,"context block span");
      let privateP=Q.Q.filter(i=>!K.includes(i));
      for(let qb of tuples(Mpad/b,privateP.length)){
       let off=Q.Q.map(i=>K.includes(i)?cb[K.indexOf(i)]*b:qb[privateP.indexOf(i)]*b);
       for(let u of tuples(b,Q.Q.length)){let z=u.map((a,i)=>a+off[i]);if(z.some(a=>a>=m))continue;
        let a=z[Q.Q.indexOf(g)],c=K.map(i=>z[Q.Q.indexOf(i)]),v=saved.get(key(c));
        let flag;
        if(Q.Q===P)flag=v.C.includes(a)||v.W[a][v.p[a]];
        else{let s=S.find(s=>!s.wide&&s.Q===Q.Q&&E.find(e=>e.Q===s.Q)===Q);assert(!!s,"support identity");let x=s.T.h.map(i=>z[Q.Q.indexOf(i)]),y=x.slice();y[0]=v.p[a];flag=!s.T.bad.has(key(x))&&s.T.bad.has(key(y));}
        assert(flag===Q.list.has(key(z)),"local batch membership");if(flag)seen.add(key(z));blockChecks++;
       }
      }
     }assert(seen.size===Q.list.size,"block union");
    }
   }
   let models=0,restricted=0,replacements=0,wideFailures=0,smallFailures=0,checks=0,overlap=0;
   for(let z of tuples(m,9)){
    checks++;if(!orig(z))continue;models++;let c=proj(z,K),v=M.get(key(c)),a=z[g],b=v.p[a],y=z.slice();y[g]=b;
    let ae=A.has(key(proj(z,P))),ee=E.some(e=>e.list.has(key(proj(z,e.Q))));
    if(ae||ee)restricted++;if(ae&&ee)overlap++;
    if(orig(y)){replacements++;assert(A.has(key(proj(y,P))),"replacement in representative");}
    else{assert(ae||ee,"failed replacement recovered");if(v.W[a][b])wideFailures++;else{assert(ee,"small exception");smallFailures++;}}
   }
   assert(!models||restricted>0,"exact existence");
   return [cap,wideCount,smallWeighted,models,restricted,replacements,wideFailures,smallFailures,overlap,checks];
  }
  check(chosen,true).forEach((v,i)=>total[i]+=v);check(arbitrary,true).forEach((v,i)=>forced[i]+=v);
 }
 // Algebraic three-context control with binary inequality noise.
 const par=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 let controls=[];
 for(let q of [4,8,16,32]){
  let m=q-1,max=0,count=0,loss=0,lower=Infinity;
  for(let c of tuples(m,3)){
   let C=new Map(),x=c.map(v=>v+1);for(let a=1;a<q;a++){
    let k=x.includes(a)?"singleton:"+a:"fiber:"+key(x.map(v=>par(v&a)));if(!C.has(k))C.set(k,a);let b=C.get(k);
    assert(x.every(v=>a===v||b!==v),"conditioned inequality preserved");
    assert(x.every(v=>par(a&v)===par(b&v)),"preserved fibers");
    for(let i=0;i<3;i++)for(let j=i+1;j<3;j++)assert(par(a&(x[i]^x[j]))===par(b&(x[i]^x[j])),"preserved triples");
    if(a!==b){loss+=5*m;assert(b!==a,"positive binary loss");}count++;
   }max=Math.max(max,C.size);
  }
  for(let a=1;a<q;a++)for(let b=1;b<q;b++)if(a!==b){let n=0;for(let x=1;x<q;x++)n+=par(a&x)===0&&a!==x&&(par(b&x)!==0||b===x);lower=Math.min(lower,n);}
  assert(max<=11&&lower>=q/4-1,"control bound");controls.push([q,max,count,loss,lower]);
 }
 return {fixtures:16,total,forced,matrixChecks,greedyChecks,blockChecks,controls};
}
console.log('F038_HYBRID_EXCEPTION_COVER_OK '+JSON.stringify(audit()));
