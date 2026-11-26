// Host semantic audit; not physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const n={fixtures:0,roots:0,children:0,rows:0,zeroRows:0,merges:0,clipped:0,canonical:0,member:0,positive:0,overflow:0,volumes:0,full:0,models:0,overflowModels:0};
 // Canonical nonempty maximal x-slabs, each containing maximal y-runs.
 function encode(t,f){
  let A=[];
  for(let x=0;x<t;x++){let R=[];for(let y=0;y<t;){if(!f(x,y)){y++;continue;}let l=y;while(y<t&&f(x,y))y++;R.push([l,y]);}
   if(!R.length)continue;let p=A[A.length-1];
   if(p&&p.h===x&&JSON.stringify(p.R)===JSON.stringify(R))p.h++;
   else A.push({l:x,h:x+1,R});
  }return A;
 }
 const bit=(A,x,y)=>A.some(s=>s.l<=x&&x<s.h&&s.R.some(([l,h])=>l<=y&&y<h));
 const weight=A=>1+A.reduce((v,s)=>v+1+s.R.length,0);
 function clip(A,ox,oy,u){
  let out=[];
  for(let s of A){let l=Math.max(s.l,ox)-ox,h=Math.min(s.h,ox+u)-ox;if(l>=h)continue;
   let R=s.R.map(([a,b])=>[Math.max(a,oy)-oy,Math.min(b,oy+u)-oy]).filter(([a,b])=>a<b);if(!R.length)continue;
   let p=out[out.length-1];if(p&&p.h===l&&JSON.stringify(p.R)===JSON.stringify(R))p.h=h;else out.push({l,h,R});
  }return out;
 }
 function make(m,B,C,F,get,center,original,full){
  let M=1;while(M<m)M*=2;
  const E=z=>z.every(a=>a<m)&&!F(z[0],z[4],z[5])&&F(get(z),z[4],z[5])&&!F(center(z[0],get(z)),z[4],z[5]);
  function intern(D,A,t){
   let used=new Set(A.map(r=>key([r.z[0],r.j]))),ids=new Map(),by=new Map(),cnt=new Map(),out=[];
   for(let r of D){let k=key([r.a,r.j]);if(!used.has(k))continue;n.rows++;
    if(!r.R.length){by.set(k,null);n.zeroRows++;continue;}
    let p=key([r.a,JSON.stringify(r.R)]);
    if(!ids.has(p)){let j=cnt.get(r.a)||0;cnt.set(r.a,j+1);ids.set(p,j);out.push({a:r.a,j,R:r.R});}else n.merges++;
    by.set(k,ids.get(p));
   }
   let w=out.reduce((v,r)=>v+weight(r.R),0),over=w>C*t**4;
   if(over){n.overflow++;return {over,w,D:[],A:[]};}
   return {over,w,D:out,A:A.filter(r=>by.get(key([r.z[0],r.j]))!==null).map(r=>{let j=by.get(key([r.z[0],r.j]));ok(j!==undefined,"ref");return {...r,j};})};
  }
  function root(o,t){let D=[],A=[],seen=new Set();
   for(let z of tup(t,4)){let x=z.map((a,i)=>a+o[i]);if(x.some(a=>a>=m))continue;let b=get(x),k=key([z[0],b]);
    if(!seen.has(k)){seen.add(k);D.push({a:z[0],j:b,R:encode(t,(u,v)=>E([...x,u+o[4],v+o[5]]))});}
    A.push({z,j:b});
   }n.roots++;return intern(D,A,t);
  }
  function child(X,d,t){let u=t/2,o=d.map(a=>a*u);
   let D=X.D.filter(r=>r.a>=o[0]&&r.a<o[0]+u).map(r=>{let R=clip(r.R,o[4],o[5],u);
    ok(JSON.stringify(R)===JSON.stringify(encode(u,(x,y)=>bit(r.R,x+o[4],y+o[5]))),"canonical clipping");n.clipped++;return {...r,a:r.a-o[0],R};});
   let A=X.A.filter(r=>r.z.every((a,i)=>a>=o[i]&&a<o[i]+u)).map(r=>({z:r.z.map((a,i)=>a-o[i]),j:r.j}));
   n.children++;return intern(D,A,u);
  }
  let over=[],mass=0,roots=new Map();
  function tree(X,o,t){
   let S=Array.from({length:t},()=>new Map());
   for(let z of tup(t,4)){let R=encode(t,(x,y)=>E([...z,x,y].map((a,i)=>a+o[i])));if(R.length)S[z[0]].set(JSON.stringify(R),R);}
   let w=S.reduce((v,s)=>v+[...s.values()].reduce((u,R)=>u+weight(R),0),0);ok(w===X.w&&X.over===(w>C*t**4),"exact weight");
   if(X.over){over.push({o,t});mass+=t**6;return {over:true,flag:true};}
   let D=new Map(X.D.map(r=>[key([r.a,r.j]),r.R])),A=new Map(X.A.map(r=>[key(r.z),r.j]));
   for(let r of X.D){ok(S[r.a].has(JSON.stringify(r.R)),"canonical dictionary");n.canonical++;}
   let flag=false;
   for(let z of tup(t,6)){let R=D.get(key([z[0],A.get(key(z.slice(0,4)))])),v=!!R&&bit(R,z[4],z[5]);ok(v===E(z.map((a,i)=>a+o[i])),"member");n.member++;flag ||=v;}
   ok(flag===S.some(s=>s.size),"positive");n.positive++;
   let T={over:false,flag,ch:[]};if(flag&&t>1)for(let d of tup(2,6))T.ch.push(tree(child(X,d,t),o.map((a,i)=>a+d[i]*t/2),t/2));return T;
  }
  for(let q of tup(M/B,6)){let o=q.map(a=>a*B);roots.set(key(q),tree(root(o,B),o,B));}
  const belongs=z=>over.some(r=>z.every((a,i)=>a>=r.o[i]&&a<r.o[i]+r.t));
  let R=0,count=0;for(let z of tup(M,6)){let k=over.filter(r=>z.every((a,i)=>a>=r.o[i]&&a<r.o[i]+r.t)).length;ok(k<=1,"disjoint");count+=k;R+=E(z);n.volumes++;}
  ok(count===mass,"volume exact");
  if(full){let expected=new Set(),got=new Set();
   for(let z of tup(M,9)){n.full++;if(original(z)&&(E(z.slice(0,6))||belongs(z.slice(0,6))))expected.add(key(z));}
   function go(T,o,t){if(T.over){for(let z of tup(t,9)){let x=z.map((a,i)=>a+o[i]);if(original(x)){got.add(key(x));n.overflowModels++;}}return;}
    if(!T.flag)return;if(t===1){if(original(o))got.add(key(o));return;}
    for(let d of tup(2,9)){let u=t/2,idx=d.slice(0,6).reduce((v,x)=>2*v+x,0);go(T.ch[idx],o.map((a,i)=>a+d[i]*u),u);}
   }
   for(let q of tup(M/B,9))go(roots.get(key(q.slice(0,6))),q.map(a=>a*B),B);
   ok(got.size===expected.size&&[...got].every(k=>expected.has(k)),"full models");n.models+=got.size;
  }
  return {R,mass,over:over.length};
 }
 let cases=[];
 for(let m of [2,3])for(let mode=0;mode<5;mode++){
  let F=(a,x,y)=>mode===0?false:mode===1?a===y&&x!==y:mode===2?a===1&&x===y:mode===3?(a+x)%m===y:(a+x+y)%2===0;
  let get=z=>(z[1]+2*z[2]+z[3]+1)%m,original=z=>z.every(a=>a<m)&&!F(z[0],z[4],z[5])&&z[6]!==z[7]&&z[2]!==z[8];
  for(let center of [(a,b)=>a,(a,b)=>0]){n.fixtures++;let A=make(m,2,1,F,get,center,original,true);cases.push([m,mode,A.R,A.mass,A.over]);}
 }
 // exhaustive clipping of every 4x4 binary row, four aligned quadrants.
 let clips=0;
 for(let i=0;i<65536;i++){let A=encode(4,(x,y)=>!!(i&(1<<(x*4+y))));
  for(let x of [0,2])for(let y of [0,2]){let Q=clip(A,x,y,2);ok(JSON.stringify(Q)===JSON.stringify(encode(2,(u,v)=>!!(i&(1<<((u+x)*4+v+y))))),"exhaustive clip");clips++;}
 }
 // Root/child overflow and zero overflow with the same guard.
 const F=(a,x,y)=>a===1?(x+y)%2===0:a===2?x===y:a===3?(x+y)%3===0:false;
 const get=z=>z[0]===0?1+(z[1]+2*z[2]+z[3])%3:z[0],original=z=>!F(z[0],z[4],z[5])&&z[6]!==z[7];
 let overflow=[];
 for(let B of [2,4])for(let C of [1,4]){let X=make(4,B,C,F,get,a=>a,original,true);overflow.push([B,C,X.R,X.mass,X.over]);}
 // Small-scale slab-code controls: all targets equal weight, distinct traces,
 // exact greedy first facility and nonself outside labels cannot improve.
 let controls=[];
 const parity=x=>{let v=0;while(x){v^=x&1;x>>=1;}return v;};
 for(let [m,r,B,N] of [[32,3,16,8],[64,4,32,16],[128,5,32,16]]){
  let q=2**r,S=B/N,T=a=>a>=m/2&&a<m/2+q;
  const raw=(a,x,y)=>{let i=Math.floor((x%B)/S);
   return T(a)?(y<m/4&&i<2*r&&i%2===((a-m/2)>>Math.floor(i/2)&1))||(y>=m/4&&y<m/2&&!!(parity(a&x)^(y&1))):y>=m/4&&y<m/2||y>=m/2&&!!(parity(a&x)^(y&1));};
  let D=Array.from({length:m},()=>Array(m).fill(0));
  for(let a=0;a<m;a++)for(let b=0;b<m;b++)for(let x=0;x<m;x++)for(let y=0;y<m;y++)D[a][b]+=!raw(a,x,y)&&raw(b,x,y);
  let w=m*m*r/(4*N),sum=0,greedy=0;
  for(let b=m/2;b<m/2+q;b++){let total=0;for(let a=0;a<m;a++){total+=D[a][b];if(!T(a))ok(D[a][b]===w,"outside loss");}
   if(b===m/2)sum=total;else ok(sum===total,"constant target sum");}
  let even=0,odd=0;for(let j=0;j<r;j++)if(j%2)odd|=1<<j;else even|=1<<j;
  for(let f=m/2;f<m/2+q;f++){
   const loss=(a,b)=>D[a][b]+m*m*(+(T(a)&&!T(b))+ +((a&even)===(f&even)&&(b&even)!==(f&even))+ +((a&odd)===(f&odd)&&(b&odd)!==(f&odd)));
   let v=Array.from({length:m},(_,b)=>Array.from({length:m},(_,a)=>loss(a,b)).reduce((u,x)=>u+x,0));
   ok(v.every((x,b)=>b===f||x>v[f]),"first facility");
   for(let b=0;b<m;b++)if(!T(b)){let gain=0;for(let a=0;a<m;a++)gain+=Math.max(0,loss(a,f)-loss(a,b));ok(gain<=w&&gain<m*m,"outside marginal");greedy++;}
   for(let a=0;a<m;a++)if(!T(a))for(let b=m/2;b<m/2+q;b++)ok(loss(a,b)>=loss(a,f),"outside stays first");
  }
  let rows=new Set();for(let b=m/2;b<m/2+q;b++)rows.add(JSON.stringify(encode(B,(x,y)=>!raw(0,x,y)&&raw(b,x,y))));ok(rows.size===q,"distinct coarse rows");
  let max=0;
  for(let t=1;t<=B;t*=2)for(let x=0;x<m;x+=t)for(let y=0;y<m;y+=t){
   let A=new Map();for(let b=m/2;b<m/2+q;b++){let R=encode(t,(u,v)=>!raw(0,u+x,v+y)&&raw(b,u+x,v+y));if(R.length)A.set(JSON.stringify(R),R);}
   let W=[...A.values()].reduce((v,R)=>v+weight(R),0);max=Math.max(max,W/t**3);
   for(let R of A.values())ok(R.length<=Math.max(1,t/S)&&R.every(s=>s.R.length===1),"slab count");
  }
  controls.push([m,q,B,S,w,rows.size,max,greedy]);
 }
 let asym=[];
 for(let d of [64,128,256,512]){let r=Math.floor(.9*d),b=Math.floor(2*d/3),l=Math.ceil(Math.log2(2*r*Math.log2(d))),s=b-l;ok(r>b+d/32&&3*s>=d,"asymptotic exponents");asym.push([d,r,b,l,s]);}
 return {n,cases,clips,overflow,controls,asym};
}
console.log('F038_RUN_CODED_OVERFLOW_OK '+JSON.stringify(audit()));
