// Standalone semantic reference; host arrays are not physical tape operations.
function audit(){
 const ok=(x,s)=>{if(!x)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],P=[0,1,2,3,4,5],key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(i=>z[i]);
 const inside=(z,o,t)=>z.every((a,i)=>a>=o[i]&&a<o[i]+t);
 function cover(M,F){
  function rec(o,t){let n=0;for(let z of tup(t,3))n+=F(z.map((a,i)=>a+o[i]));
   if(!n)return [];
   if(n===t**3)return [{o,t}];
   ok(t>1,"mixed leaf");
   return [...tup(2,3)].flatMap(d=>rec(o.map((a,i)=>a+d[i]*t/2),t/2));
  }
  return rec([0,0,0],M);
 }
 function clip(r,o,t){
  if(r.o.some((a,i)=>a>=o[i]+t||o[i]>=a+r.t))return null;
  if(r.t>=t){ok(inside(o,r.o,r.t),"nested larger");return {h:r.h,o:Array(o.length).fill(0),t};}
  ok(inside(r.o,o,t),"nested smaller");return {h:r.h,o:r.o.map((a,i)=>a-o[i]),t:r.t};
 }
 const hierarchical=z=>{let x=z.reduce((a,b)=>a^b,0);return x!==0&&(31-Math.clz32(x))%2===0;};
 let stats=Array(13).fill(0),fixtures=0;
 for(let m of [2,3])for(let mode=0;mode<7;mode++){
  let M=1;while(M<m)M*=2;let b=2;
  let R=H.map(h=>({h,F:new Set([...tup(m,h.length)].filter(z=>{
   if(key(h)==="0,4,5")return mode!==0&&(mode===1?z[0]===z[2]&&z[1]!==z[2]:z[0]===1&&z[1]===z[2]);
   if(mode===2&&key(h)==="6,7,8")return hierarchical(z);
   if(mode===3&&key(h)==="6,7,8")return (z[0]^z[1])!==z[2];
   if(mode===4)return h.length===3&&(z[0]+z[1])%m===z[2];
   if(mode===5)return h.length===1&&z[0]!==h[0]%m;
   if(mode===6&&key(h)==="6,7,8")return true;
   return false;
  }).map(key))}));
  let T=R.find(s=>key(s.h)==="0,4,5"),p=(a,d,e,t)=>(d+e+t+1)%m;
  let A=R.filter(s=>s.h.every(g=>P.includes(g))),B=R.filter(s=>!s.h.every(g=>P.includes(g)));
  const guard=z=>z.every(a=>a<m)&&!T.F.has(key([z[0],z[4],z[5]]))&&T.F.has(key([p(...z.slice(0,4)),z[4],z[5]]))&&A.every(s=>!s.F.has(key(proj(z,s.h))));
  const orig=z=>R.every(s=>!s.F.has(key(proj(z,s.h))));
  let raw=[];
  for(let s of B){
   let C=s.h.length===3?cover(M,z=>s.F.has(key(z))):[...s.F].map(z=>({o:z.split(",").map(Number),t:1}));
   stats[0]+=s.F.size;stats[1]+=C.length;
   for(let z of tup(M,s.h.length)){ok(C.filter(r=>inside(z,r.o,r.t)).length===+s.F.has(key(z)),"exact disjoint cover");stats[2]++;}
   if(s.h.length===3)for(let t=1;t<=M;t*=2)for(let q of tup(M/t,3)){
    let o=q.map(a=>a*t),D=C.map(r=>clip({...r,h:s.h},o,t)).filter(Boolean);
    let n=0;for(let z of tup(t,3)){let f=s.F.has(key(z.map((a,i)=>a+o[i])));n+=f;ok(D.filter(r=>inside(z,r.o,r.t)).length===+f,"clipped cube");stats[3]++;}
    ok(D.length<=n&&D.length<=2*t*t,"fixture cap");stats[4]++;
   }
   raw.push(...C.map(r=>({...r,h:s.h})));
  }
  for(let g of G.filter(g=>!P.includes(g)))for(let a=m;a<M;a++)raw.push({h:[g],o:[a],t:1});
  let expected=new Set(),got=new Set();
  for(let z of tup(m,9)){stats[5]++;if(orig(z)&&guard(z.slice(0,6)))expected.add(key(z));}
  function node(t,off,C){
   let r=0;for(let z of tup(t,6))r+=guard(z.map((a,i)=>a+off[i]));
   if(!r)return;
   stats[6]++;ok(C.length<=260*t*t,"local frame cap");
   if(t===1){stats[7]++;let pass=C.length===0;ok(pass===(off.every(a=>a<m)&&orig(off)&&guard(off.slice(0,6))),"exact leaf");
    if(pass){ok(!got.has(key(off)),"disjoint models");got.add(key(off));}return;}
   for(let d of tup(2,9)){
    let u=t/2,o=d.map(a=>a*u),cc=C.map(r=>clip(r,proj(o,r.h),u)).filter(Boolean);
    for(let r of cc)ok(r.t<=u&&r.o.every(a=>a>=0&&a+r.t<=u),"local record");
    stats[8]+=cc.length;stats[9]++;
    node(u,off.map((a,i)=>a+o[i]),cc);
   }
  }
  for(let q of tup(M/b,9)){
   let o=q.map(a=>a*b),C=raw.map(r=>clip(r,proj(o,r.h),b)).filter(Boolean);
   stats[10]++;node(b,o,C);
  }
  ok(expected.size===got.size&&[...got].every(z=>expected.has(z)),"exact restricted models");stats[11]+=got.size;stats[12]+=expected.size;fixtures++;
 }
 let controls=[];
 for(let m of [4,8,16,32,64]){
  let C=cover(m,hierarchical),n=0,max=0,cubes=0,mixed=0;
  for(let t=1;t<=m;t*=2)for(let q of tup(m/t,3)){
   let o=q.map(a=>a*t),D=C.map(r=>clip({...r,h:[0,1,2]},o,t)).filter(Boolean);
   let mass=D.reduce((a,r)=>a+r.t**3,0);ok(D.length<=2*t*t,"hierarchy cover cap");max=Math.max(max,D.length/(t*t));cubes++;mixed+=mass>0&&mass<t**3;if(t===m)n=mass;
  }
  let count=0;for(let z of tup(m,3))count+=hierarchical(z);ok(count===n&&!hierarchical([3,3,3]),"hierarchical control mass and SAT");
  ok(n>=m**3/4&&n<=3*m**3/4,"dense both polarities");
  controls.push([m,n,C.length,max,cubes,mixed]);
 }
 return {fixtures,stats,controls};
}
console.log('F038_DYADIC_RESIDUAL_COVER_OK '+JSON.stringify(audit()));
