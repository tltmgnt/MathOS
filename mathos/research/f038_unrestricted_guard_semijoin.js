// Standalone semantic reference; host arrays are not physical tape operations.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],P=[0,1,2,3,4,5],key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(A,k,i=0,p=[]){if(p.length===k){yield p;return;}for(let j=i;j<=A.length-k+p.length;j++)yield* sub(A,k,j+1,p.concat(A[j]));}
 const H=[...sub(G,1),...sub(G,2),...sub(G,3)],I=[[],...sub(P,1),...sub(P,2)],proj=(z,h)=>h.map(i=>z[i]);
 const contains=(z,o,t)=>z.every((a,i)=>a>=o[i]&&a<o[i]+t);
 function cover(M,k,F){
  function rec(o,t){let n=0;for(let z of tup(t,k))n+=F(z.map((a,i)=>a+o[i]));if(!n)return [];if(n===t**k)return [{o,t}];return [...tup(2,k)].flatMap(d=>rec(o.map((a,i)=>a+d[i]*t/2),t/2));}
  return rec(Array(k).fill(0),M);
 }
 function clip(r,o,t){
  if(r.o.some((a,i)=>a>=o[i]+t||o[i]>=a+r.t))return null;
  if(r.t>=t){ok(contains(o,r.o,r.t),"aligned containment");return {...r,o:Array(o.length).fill(0),t};}
  ok(contains(r.o,o,t),"aligned reverse containment");return {...r,o:r.o.map((a,i)=>a-o[i])};
 }
 let totals=Array(16).fill(0),fixtures=0,empty=0,wideOnly=0;
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  let M=1;while(M<m)M*=2;let b=2;
  let R=H.map(h=>({h,F:new Set([...tup(m,h.length)].filter(z=>{
   if(key(h)==="0,4,5"){
    if(mode===0)return false;
    if(mode===1)return z[0]===z[2]&&z[1]!==z[2];
    if(mode===3)return z[0]===1&&z[1]===0;
    return z[0]===1&&z[1]===z[2];
   }
   if(mode===2&&key(h)==="1,2")return z[0]===z[1];
   if(mode===2&&key(h)==="1,2,6")return z[0]===z[1]&&z[2]%2===1;
   if(mode===3&&key(h)==="4,6,7")return z[0]!==0&&z[1]!==z[2];
   if(mode===4&&key(h)==="0")return z[0]!==1;
   if(mode===5&&key(h)==="1,2")return true;
   if(mode===6)return h.length===3&&(z[0]+z[1])%m===z[2];
   if(mode===7)return h.length===3&&(h.reduce((s,x)=>s+x,0)+z.reduce((s,x,i)=>s+(i+2)*x,0))%5===0;
   return false;
  }).map(key))}));
  let T=R.find(s=>key(s.h)==="0,4,5"),A=R.filter(s=>s.h.every(g=>P.includes(g))),B=R.filter(s=>!s.h.every(g=>P.includes(g)));
  let W=new Set();
  for(let [a,u,v] of tup(m,3)){
   let old=T.F.has(key([a,u,v])),any=false;for(let j=0;j<m;j++)any ||=T.F.has(key([j,u,v]));
   if(!old&&any)W.add(key([a,u,v]));totals[0]++;
  }
  const feasible=z=>z.every(a=>a<m)&&A.every(s=>!s.F.has(key(proj(z,s.h))));
  const possible=z=>feasible(z)&&W.has(key([z[0],z[4],z[5]]));
  let mask=new Map(I.map(h=>[key(h),new Set()])),prior=new Map(I.map(h=>[key(h),new Set()])),ref=new Map(I.map(h=>[key(h),new Set()]));
  for(let z of tup(m,6)){
   let g=feasible(z),v=possible(z),exact=g&&Array.from({length:m},(_,a)=>a).some(a=>!T.F.has(key([z[0],z[4],z[5]]))&&T.F.has(key([a,z[4],z[5]])));
   ok(v===exact,"map independent guard");totals[1]++;
   for(let h of I){if(g)prior.get(key(h)).add(key(proj(z,h)));if(v)ref.get(key(h)).add(key(proj(z,h)));}
  }
  for(let q of tup(M/b,6)){
   let o=q.map(a=>a*b),local=new Map(I.map(h=>[key(h),new Set()]));
   for(let z of tup(b,6)){
    let x=z.map((a,i)=>a+o[i]);if(possible(x))for(let h of I)local.get(key(h)).add(key(proj(z,h)));
    totals[2]++;
   }
   for(let h of I)for(let k of local.get(key(h))){let z=h.length?k.split(",").map(Number):[];mask.get(key(h)).add(key(z.map((a,i)=>a+o[h[i]])));totals[3]++;}
  }
  for(let h of I)for(let z of tup(m,h.length)){
   ok(mask.get(key(h)).has(key(z))===ref.get(key(h)).has(key(z)),"exact mask");totals[4]++;
  }
  if(!mask.get("").size)empty++;
  let filtered=B.map(s=>{
   let h=s.h.filter(g=>P.includes(g)),F=new Set();
   for(let k of s.F){let z=k.split(",").map(Number),v=key(h.map(g=>z[s.h.indexOf(g)]));totals[5]++;
    if(mask.get(key(h)).has(v))F.add(k);else{totals[6]++;if(prior.get(key(h)).has(v)){wideOnly++;}}
   }
   return {...s,F};
  });
  let raw=[];
  for(let s of filtered){
   let C=s.h.length===3?cover(M,3,z=>s.F.has(key(z))):[...s.F].map(k=>({o:k.split(",").map(Number),t:1}));
   totals[7]+=C.length;
   for(let z of tup(M,s.h.length)){ok(C.filter(r=>contains(z,r.o,r.t)).length===+s.F.has(key(z)),"filtered cover");totals[8]++;}
   raw.push(...C.map(r=>({...r,h:s.h})));
  }
  for(let g of G.filter(g=>!P.includes(g)))for(let a=m;a<M;a++)raw.push({h:[g],o:[a],t:1});
  let orig=z=>R.every(s=>!s.F.has(key(proj(z,s.h))));
  for(let policy of [0,1]){
   const p=z=>policy===0?(z[1]+z[2]+z[3]+1)%m:1%m;
   const guard=z=>feasible(z)&&!T.F.has(key([z[0],z[4],z[5]]))&&T.F.has(key([p(z),z[4],z[5]]));
   let expected=new Set(),got=new Set();
   for(let z of tup(m,9)){
    totals[9]++;if(!guard(z.slice(0,6)))continue;
    ok(possible(z.slice(0,6)),"actual guard subset");
    ok(B.every(s=>!s.F.has(key(proj(z,s.h))))===filtered.every(s=>!s.F.has(key(proj(z,s.h)))),"exact semijoin");
    totals[10]++;if(orig(z))expected.add(key(z));
   }
   function visit(t,o,C){
    let flag=false;for(let z of tup(t,6))if(guard(z.map((a,i)=>a+o[i]))){flag=true;break;}if(!flag)return;
    totals[11]++;
    if(t===1){totals[12]++;let pass=C.length===0;ok(pass===(o.every(a=>a<m)&&orig(o)&&guard(o.slice(0,6))),"leaf");if(pass)got.add(key(o));return;}
    for(let d of tup(2,9)){let u=t/2,x=d.map(a=>a*u),D=C.map(r=>clip(r,proj(x,r.h),u)).filter(Boolean);totals[13]++;visit(u,o.map((a,i)=>a+x[i]),D);}
   }
   for(let q of tup(M/b,9)){let o=q.map(a=>a*b),C=raw.map(r=>clip(r,proj(o,r.h),b)).filter(Boolean);visit(b,o,C);}
   ok(got.size===expected.size&&[...got].every(k=>expected.has(k)),"exact restricted models");totals[14]+=got.size;totals[15]+=expected.size;
  }
  fixtures++;
 }
 const parity=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 let controls=[];
 for(let m of [4,8,16,32,64]){
  let F=z=>parity(z[0]&z[1])===1&&z[2]%2===1,mask=(a,b)=>parity(a&b)===0;
  let C=cover(m,3,F),D=cover(m,3,z=>F(z)&&mask(z[0],z[1])),n=0;
  for(let z of tup(m,3)){n+=F(z);ok(!(F(z)&&mask(z[0],z[1])),"redundant dense support");}
  ok(n===m*m*(m-1)/4&&C.length===n&&D.length===0,"dense singleton cover separation");controls.push([m,n,C.length,D.length]);
 }
 ok(empty>0&&wideOnly>0,"empty and wide-only mask effects exercised");
 return {fixtures,totals,empty,wideOnly,controls};
}
console.log('F038_GUARD_SEMIJOIN_OK '+JSON.stringify(audit()));
