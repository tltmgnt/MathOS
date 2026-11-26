// Standalone semantic audit, not a physical tape simulator.
function audit(){
 const ok=(x,s)=>{if(!x)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(A,k,i=0,p=[]){if(p.length===k){yield p;return;}for(let j=i;j<=A.length-k+p.length;j++)yield* sub(A,k,j+1,p.concat(A[j]));}
 const H=[...sub(G,1),...sub(G,2),...sub(G,3)],proj=(z,h)=>h.map(g=>z[g]),K=[1,2,3],P=[0,...K];
 let totals=Array(10).fill(0),forced=Array(10).fill(0),frequencyChecks=0,unionChecks=0,boundChecks=0,fixtures=0;
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  let R=H.map(h=>({h,F:new Set([...tup(m,h.length)].filter(z=>{
   if(mode===0)return false;
   if(mode===1)return h.length===1&&h[0]===8;
   if(mode===2)return h.length===2&&z[0]===z[1];
   if(mode===3)return key(h)==="0,4,5"&&z[0]===z[2]&&z[0]!==z[1];
   if(mode===4)return key(h)==="0,1,4"&&z[0]===1&&z[1]===z[2];
   if(mode===5)return h.length===3&&(h.reduce((s,a)=>s+a,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===6)return h.length===1&&z[0]!==h[0]%m;
   return key(h)==="0,4,5"&&z[1]===0&&z[0]!==z[2]||h.length===2&&h[0]===0&&z[0]===z[1];
  }).map(key))}));
  let sections=R.filter(T=>T.h.includes(0)).map(T=>{
   let O=T.h.filter(g=>g!==0&&!K.includes(g)),Q=[...new Set([...T.h,...K])].sort((a,b)=>a-b);
   function lost(a,b,c){return [...tup(m,O.length)].filter(z=>{let x=T.h.map(g=>g===0?a:K.includes(g)?c[K.indexOf(g)]:z[O.indexOf(g)]),y=x.slice();y[0]=b;return !T.F.has(key(x))&&T.F.has(key(y));});}
   return {T,O,Q,lost,wide:O.length===2};
  }),wide=sections.filter(s=>s.wide),narrow=sections.filter(s=>!s.wide);
  let ell=wide.map(s=>Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>s.lost(a,b,[]).length)));
  function make(policy){
   let maps=new Map(),cap=0,loss=0;
   for(let c of tup(m,3)){
    let C=Array.from({length:m},(_,a)=>a).filter(a=>policy===0||policy===1&&Math.floor(a/2)===Math.floor(c[0]/2)||policy===2&&a===(c.reduce((s,x)=>s+x,0)+1)%m);
    let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>narrow.reduce((v,s)=>v+s.lost(a,b,c).length*m**(2-s.O.length),0)+ell.reduce((v,E)=>v+E[a][b],0)));
    if(policy===0){
     let used=[],res=Array(m).fill(37*m*m),best=null;
     for(let k=1;k<=m;k++){let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!used.includes(j)){let n=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(n<v){v=n;b=j;}}used.push(b);res=res.map((x,a)=>Math.min(x,D[a][b]));if(!best||k*m*m+v<best.score)best={C:used.slice(),score:k*m*m+v};}C=best.C;
    }
    let p=Array.from({length:m},(_,a)=>C.reduce((b,j)=>D[a][j]<D[a][b]?j:b,C[0]));
    maps.set(key(c),{C,p});cap+=C.length;
    for(let a=0;a<m;a++)loss+=narrow.reduce((v,s)=>v+s.lost(a,p[a],c).length*m**(2-s.O.length),0);
   }
   return {maps,cap,loss};
  }
  function evaluate(B,f){
   let N=Array.from({length:m},()=>Array.from({length:m},()=>Array(m).fill(0)));
   for(let c of tup(m,3))for(let a=0;a<m;a++)N[c[0]][a][B.maps.get(key(c)).p[a]]++;
   for(let d=0;d<m;d++)for(let a=0;a<m;a++){ok(N[d][a].reduce((s,x)=>s+x,0)===m*m,"frequency mass");frequencyChecks++;}
   let U=wide.map((s,i)=>{
    let A=new Set();
    for(let d=0;d<m;d++)for(let a=0;a<m;a++)for(let b=0;b<m;b++)if(N[d][a][b]>=f)for(let z of s.lost(a,b,[]))A.add(key([d,a,...z]));
    let w=0;for(let [d,a,u,v] of tup(m,4)){let x=false;for(let b=0;b<m;b++)if(N[d][a][b]>=f&&s.lost(a,b,[]).some(z=>z[0]===u&&z[1]===v))x=true;ok(x===A.has(key([d,a,u,v])),"exact frequency union");unionChecks++;}
    for(let d=0;d<m;d++)for(let a=0;a<m;a++)for(let b=0;b<m;b++)w+=N[d][a][b]*ell[i][a][b];
    ok(A.size*f<=w,"frequency weighted bound");boundChecks++;return A;
   });
   let A=new Set(),rare=0,E=narrow.map(s=>({s,A:new Set()}));
   for(let c of tup(m,3))for(let a=0;a<m;a++){let {C,p}=B.maps.get(key(c)),b=p[a],r=N[c[0]][a][b]<f&&ell.some(E=>E[a][b]>0);rare+=r;if(r||C.includes(a))A.add(key([a,...c]));}
   for(let e of E)for(let z of tup(m,e.s.Q.length)){let c=K.map(g=>z[e.s.Q.indexOf(g)]),a=z[0],b=B.maps.get(key(c)).p[a],x=e.s.T.h.map(g=>z[e.s.Q.indexOf(g)]),y=x.slice();y[0]=b;if(!e.s.T.F.has(key(x))&&e.s.T.F.has(key(y)))e.A.add(key(z));}
   ok(E.reduce((v,e)=>v+e.A.size*m**(6-e.s.Q.length),0)===B.loss,"narrow mass");
   ok(A.size===(B.cap+rare),"envelope density");
   return {...B,N,U,A,E,rare,f,score:(B.cap+rare+U.reduce((s,u)=>s+u.size,0))*m*m+B.loss};
  }
  function recover(B){
   let orig=z=>R.every(T=>!T.F.has(key(proj(z,T.h)))),models=0,restricted=0,replaced=0,rareFail=0,unionFail=0,narrowFail=0,checks=0;
   for(let z of tup(m,9)){checks++;if(!orig(z))continue;models++;let c=proj(z,K),a=z[0],b=B.maps.get(key(c)).p[a],y=z.slice();y[0]=b;
    let A=B.A.has(key(proj(z,P))),U=wide.some((s,i)=>B.U[i].has(key([c[0],a,...proj(z,s.O)]))),E=B.E.some(e=>e.A.has(key(proj(z,e.s.Q))));
    if(A||U||E)restricted++;
    if(orig(y)){replaced++;ok(B.A.has(key(proj(y,P))),"representative recovery");}
    else if(B.N[c[0]][a][b]<B.f&&ell.some(e=>e[a][b]>0)){rareFail++;ok(A,"rare recovery");}
    else if(wide.some(s=>s.T.F.has(key(proj(y,s.T.h))))){unionFail++;ok(U,"frequent recovery");}
    else{narrowFail++;ok(E,"narrow recovery");}
   }
   ok(!models||restricted,"exact existence");
   return [B.cap,B.rare,B.U.reduce((s,u)=>s+u.size,0),models,restricted,replaced,rareFail,unionFail,narrowFail,checks];
  }
  let fs=[1];while(fs.at(-1)*2<m*m)fs.push(fs.at(-1)*2);if(fs.at(-1)!==m*m)fs.push(m*m);
  let choices=[];for(let p of [0,1]){let B=make(p);for(let f of fs)choices.push(evaluate(B,f));}
  choices.sort((a,b)=>a.score-b.score);recover(choices[0]).forEach((v,i)=>totals[i]+=v);
  let B=make(2);for(let f of [1,m*m])recover(evaluate(B,f)).forEach((v,i)=>forced[i]+=v);
  fixtures++;
 }
 const parity=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 let controls=[];
 for(let q of [8,16,32,64]){
  let m=q-1,s=2**Math.floor(Math.log2(q)/2),bad=0,good=0,checks=0,union=0;
  for(let c of tup(m,3)){
   let v=c.map(a=>a+1),start=Math.floor(v[0]/s)*s,C=Array.from({length:s},(_,i)=>start+i).filter(a=>a>0);
   let fiber=a=>key(v.map(x=>parity(a&x))),all=new Set(Array.from({length:m},(_,a)=>fiber(a+1))),part=new Set(C.map(fiber));
   if([...all].every(x=>part.has(x))){good++;for(let x of all){ok(part.has(x),"palette fibers");checks++;}}else bad++;
  }
  for(let d=1;d<q;d++)for(let a=1;a<q;a++){let C=Array.from({length:s},(_,i)=>Math.floor(d/s)*s+i).filter(b=>b>0&&b!==a);union+=C.length*(m-1);}
  ok(union<=m**3*s,"palette union bound");
  // Pair loss m-1; global union has (m-1)^2 entries per row.
  let n=0;for(let a=1;a<q;a++)for(let u=1;u<q;u++)for(let v=1;v<q;v++)if(v!==a&&u!==v)n++;
  ok(n===m*(m-1)**2,"dense context-free union");
  controls.push([m,s,good,bad,checks,union,n]);
 }
 return {fixtures,totals,forced,frequencyChecks,unionChecks,boundChecks,controls};
}
console.log('F038_FREQUENCY_UNIONS_OK '+JSON.stringify(audit()));
