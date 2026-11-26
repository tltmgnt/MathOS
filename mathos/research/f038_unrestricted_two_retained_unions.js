// Standalone semantic audit; not physical tape execution.
function audit(){
 const ok=(x,s)=>{if(!x)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(A,k,i=0,p=[]){if(p.length===k){yield p;return;}for(let j=i;j<=A.length-k+p.length;j++)yield* sub(A,k,j+1,p.concat(A[j]));}
 const H=[...sub(G,1),...sub(G,2),...sub(G,3)],proj=(z,h)=>h.map(g=>z[g]),K=[1,2,3],P=[0,...K];
 let totals=Array(10).fill(0),forced=Array(10).fill(0),frequencyChecks=0,unionChecks=0,boundChecks=0,blockChecks=0,greedyChecks=0,pairBuilds=0,fixtures=0;
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
  let S=R.filter(T=>T.h.includes(0)).map(T=>{
   let O=T.h.filter(g=>g!==0&&!K.includes(g)),Q=[...new Set([...T.h,...K])].sort((a,b)=>a-b);
   function lost(a,b,c){return [...tup(m,O.length)].filter(z=>{let x=T.h.map(g=>g===0?a:K.includes(g)?c[K.indexOf(g)]:z[O.indexOf(g)]),y=x.slice();y[0]=b;return !T.F.has(key(x))&&T.F.has(key(y));});}
   return {T,O,Q,lost,wide:O.length===2};
  }),wide=S.filter(s=>s.wide),narrow=S.filter(s=>!s.wide),ell=wide.map(s=>Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>s.lost(a,b,[]).length)));
  function context(c,policy){
   let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>narrow.reduce((v,s)=>v+s.lost(a,b,c).length*m**(2-s.O.length),0)+ell.reduce((v,E)=>v+E[a][b],0)));
   let C;
   if(policy===0){
    let used=[],R=Array(m).fill(37*m*m),best=null,profile=[];
    for(let k=1;k<=m;k++){
     let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!used.includes(j)){let n=0;for(let a=0;a<m;a++)n+=Math.min(R[a],D[a][j]);if(n<v){v=n;b=j;}}
     used.push(b);for(let a=0;a<m;a++)R[a]=Math.min(R[a],D[a][b]);profile.push(v);
     ok(R.reduce((s,x)=>s+x,0)===v,"candidate scan");greedyChecks++;
     if(!best||k*m*m+v<best.score)best={C:used.slice(),score:k*m*m+v};
    }C=best.C;
   }else if(policy===1){let d=(c[0]+c[1])%m;C=Array.from({length:m},(_,a)=>a).filter(a=>Math.floor((a+1)/2)===Math.floor((d+1)/2));}
   else C=[(c[0]+c[1]+c[2]+1)%m];
   let p=Array.from({length:m},(_,a)=>C.reduce((b,j)=>D[a][j]<D[a][b]?j:b,C[0]));
   return {C,p};
  }
  function pair(d,e,policy){
   let maps=Array.from({length:m},(_,t)=>context([d,e,t],policy)),N=Array.from({length:m},()=>Array(m).fill(0));
   for(let t=0;t<m;t++)for(let a=0;a<m;a++)N[a][maps[t].p[a]]++;
   pairBuilds++;
   return {maps,N};
  }
  function evaluate(policy,f){
   let maps=new Map(),N=new Map(),cap=0,loss=0,rare=0,A=new Set(),U=wide.map(()=>new Set()),E=narrow.map(s=>({s,A:new Set()}));
   for(let [d,e] of tup(m,2)){
    let v=pair(d,e,policy);N.set(key([d,e]),v.N);
    for(let a=0;a<m;a++){ok(v.N[a].reduce((s,x)=>s+x,0)===m,"frequency mass");frequencyChecks++;}
    for(let t=0;t<m;t++){
     let c=[d,e,t],{C,p}=v.maps[t];maps.set(key(c),{C,p});cap+=C.length;
     for(let a=0;a<m;a++){let b=p[a],r=v.N[a][b]<f&&ell.some(E=>E[a][b]>0);rare+=r;if(C.includes(a)||r)A.add(key([a,...c]));
      loss+=narrow.reduce((z,s)=>z+s.lost(a,b,c).length*m**(2-s.O.length),0);}
    }
    for(let i=0;i<wide.length;i++){
     let s=wide[i],weighted=0,local=0;
     for(let a=0;a<m;a++){
      let row=new Set();for(let b=0;b<m;b++){weighted+=v.N[a][b]*ell[i][a][b];if(v.N[a][b]>=f)for(let z of s.lost(a,b,[]))row.add(key(z));}
      for(let z of tup(m,2)){let expected=false;for(let b=0;b<m;b++)if(v.N[a][b]>=f&&s.lost(a,b,[]).some(x=>key(x)===key(z)))expected=true;
       ok(expected===row.has(key(z)),"row union");unionChecks++;if(expected){U[i].add(key([d,e,a,...z]));local++;}}
     }ok(f*local<=weighted,"weighted bound");boundChecks++;
    }
   }
   for(let e of E)for(let z of tup(m,e.s.Q.length)){let c=K.map(g=>z[e.s.Q.indexOf(g)]),a=z[0],b=maps.get(key(c)).p[a],x=e.s.T.h.map(g=>z[e.s.Q.indexOf(g)]),y=x.slice();y[0]=b;if(!e.s.T.F.has(key(x))&&e.s.T.F.has(key(y)))e.A.add(key(z));}
   ok(E.reduce((v,e)=>v+e.A.size*m**(6-e.s.Q.length),0)===loss,"narrow mass");ok(A.size===cap+rare,"envelope");
   return {policy,f,maps,N,A,U,E,cap,rare,loss,score:(cap+rare)*m*m+loss+U.reduce((s,u)=>s+u.size,0)*m};
  }
  function blocks(B){
   let M=1;while(M<m)M*=2;let b=2;
   // Rebuild each pair independently inside every projected block, retaining only local flags.
   for(let i=0;i<wide.length;i++){
    let seen=new Set(),s=wide[i];
    for(let J of tup(M/b,5)){
     for(let [d0,e0] of tup(b,2)){
      let d=J[0]*b+d0,e=J[1]*b+e0;if(d>=m||e>=m)continue;
      let v=pair(d,e,B.policy);ok(key(v.N.flat())===key(B.N.get(key([d,e])).flat()),"regenerated slice");
      for(let a0=0;a0<b;a0++){
       let a=J[2]*b+a0;if(a>=m)continue;
       let row=new Set();for(let r=0;r<m;r++)if(v.N[a][r]>=B.f)for(let z of s.lost(a,r,[]))row.add(key(z));
       for(let z0 of tup(b,2)){let z=z0.map((x,j)=>x+b*J[j+3]);if(z.some(x=>x>=m))continue;let k=key([d,e,a,...z]),flag=row.has(key(z));
        ok(flag===B.U[i].has(k),"coarse flags");blockChecks++;if(flag){ok(!seen.has(k),"disjoint blocks");seen.add(k);}}
      }
     }
    }ok(seen.size===B.U[i].size,"coarse union");
   }
  }
  function recover(B){
   let orig=z=>R.every(T=>!T.F.has(key(proj(z,T.h)))),models=0,restricted=0,replaced=0,rareFail=0,unionFail=0,narrowFail=0,checks=0;
   for(let z of tup(m,9)){checks++;if(!orig(z))continue;models++;let c=proj(z,K),a=z[0],b=B.maps.get(key(c)).p[a],y=z.slice();y[0]=b;
    let A=B.A.has(key(proj(z,P))),U=wide.some((s,i)=>B.U[i].has(key([c[0],c[1],a,...proj(z,s.O)]))),E=B.E.some(e=>e.A.has(key(proj(z,e.s.Q))));
    if(A||U||E)restricted++;
    if(orig(y)){replaced++;ok(B.A.has(key(proj(y,P))),"representative");}
    else if(B.N.get(key(c.slice(0,2)))[a][b]<B.f&&ell.some(e=>e[a][b]>0)){rareFail++;ok(A,"rare");}
    else if(wide.some(s=>s.T.F.has(key(proj(y,s.T.h))))){unionFail++;ok(U,"wide");}
    else{narrowFail++;ok(E,"narrow");}
   }ok(!models||restricted,"existence");
   return [B.cap,B.rare,B.U.reduce((s,u)=>s+u.size,0),models,restricted,replaced,rareFail,unionFail,narrowFail,checks];
  }
  let fs=[1];while(fs.at(-1)*2<m)fs.push(fs.at(-1)*2);if(fs.at(-1)!==m)fs.push(m);
  let choices=[];for(let policy of [0,1])for(let f of fs)choices.push(evaluate(policy,f));
  choices.sort((a,b)=>a.score-b.score);blocks(choices[0]);recover(choices[0]).forEach((v,i)=>totals[i]+=v);
  for(let f of [1,m]){let B=evaluate(2,f);if(f===1)blocks(B);recover(B).forEach((v,i)=>forced[i]+=v);}
  fixtures++;
 }
 let controls=[];
 for(let m of [3,5,9,17]){
  // p_c(a)=c1+c2 mod m. All wide loss sets are disjoint in representative v.
  let one=0,two=0,rare=0;
  for(let [d,a] of tup(m,2)){let N=Array(m).fill(0);for(let [e,t] of tup(m,2))N[(d+e)%m]++;
   ok(N.every(n=>n===m),"one retained uniform");
   for(let b=0;b<m;b++)if(a!==b){one+=m-1;rare+=N[b];}}
  for(let [d,e,a] of tup(m,3)){let b=(d+e)%m;if(a!==b)two+=m-1;}
  ok(one===m*m*(m-1)**2&&two===m*m*(m-1)**2,"projection cardinalities");
  ok(rare===m*m*m*(m-1),"rare count");
  controls.push([m,one,two,rare]);
 }
 return {fixtures,totals,forced,frequencyChecks,unionChecks,boundChecks,blockChecks,greedyChecks,pairBuilds,controls};
}
console.log('F038_TWO_RETAINED_UNIONS_OK '+JSON.stringify(audit()));
