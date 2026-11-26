// Exact pair-major union semantic audit; not a compiled joint feasibility machine.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 let seed=0x003f038;function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;}
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 let counts={rectangles:0,oldMiss:0,exactMiss:0,localKeys:0,localPairs:0,matchingRecords:0,coveredPairs:0,nesting:0,duplicates:0,strictOld:0};
 // Pair-major union count. Multiple matching supports/duplicate records count once.
 function covered(X,Y,rows,z){
  let old=null,hit=false,N=0;
  for(let r of rows){
   let k=key([r.x,r.y]);
   if(k!==old){if(hit)N++;old=k;hit=false;}
   if(X.has(r.x)&&Y.has(r.y)&&(r.a===-1||z[r.a]===r.v)){hit=true;counts.matchingRecords++;}
  }
  if(hit)N++;return N;
 }
 for(let X of [[0],[1],[0,1]])for(let Y of [[0],[1],[0,1]])for(let a=0;a<16;a++)for(let b=0;b<16;b++){
  let P=X.flatMap(x=>Y.map(y=>[x,y])),rows=[];
  for(let x=0;x<2;x++)for(let y=0;y<2;y++){
   let v=1<<(2*x+y);if(a&v)rows.push({x,y,a:-1});if(b&v)rows.push({x,y,a:0,v:0});
  }
  let N=covered(new Set(X),new Set(Y),rows,[0]),exact=P.some(([x,y])=>!((a|b)&(1<<(2*x+y))));
  let old=!P.every(([x,y])=>a&(1<<(2*x+y)))&&!P.every(([x,y])=>b&(1<<(2*x+y)))&&(Math.min(X.length,Y.length)>1||exact);
  ok((N<P.length)===exact,"exact rectangle");
  counts.rectangles++;if(old&&!exact)counts.oldMiss++;if((N<P.length)!==exact)counts.exactMiss++;
 }
 // Full six-coordinate local original predicate, including padding and actual key.
 for(let m of [2,3,4])for(let mode=0;mode<4;mode++){
  let M=m===2?2:4;
  let supports=[[0,1,2],[1,3],[0,1,4],[2,4],[3,5],[0,2,5],[4],[5],[4,5],...[0,1,2,3].map(a=>[a,4,5])];
  let F=supports.map(h=>({h,F:new Set([...tup(m,h.length)].filter(v=>(rand()>>>24)<(mode+1)*30).map(key))}));
  const bad=(s,z)=>s.F.has(key(s.h.map(a=>z[a]))),real=z=>z.every(v=>v<m);
  let pair=[];
  for(let s of F)if(s.h.includes(4)&&s.h.includes(5))for(let v of s.F){
   let z=v.split(",").map(Number),a=s.h.find(a=>a<4)??-1;
   let r={x:z[s.h.indexOf(4)],y:z[s.h.indexOf(5)],a,v:a<0?0:z[s.h.indexOf(a)]};
   pair.push(r);if((rand()>>>28)<3){pair.push({...r});counts.duplicates++;}
  }
  pair.sort((a,b)=>a.x-b.x||a.y-b.y);
  function filter(z,ox,oy,t){
   let X=new Set(),Y=new Set();
   if(!real(z)||F.some(s=>s.h.every(a=>a<4)&&bad(s,z)))return false;
   for(let x=ox;x<Math.min(m,ox+t);x++)if(!F.some(s=>s.h.every(a=>a<4||a===4)&&bad(s,[...z,x,0])))X.add(x);
   for(let y=oy;y<Math.min(m,oy+t);y++)if(!F.some(s=>s.h.every(a=>a<4||a===5)&&bad(s,[...z,0,y])))Y.add(y);
   let N=covered(X,Y,pair,z);counts.coveredPairs+=N;
   ok(N<=X.size*Y.size,"count bound");
   return N<X.size*Y.size;
  }
  for(let t=1;t<=M;t*=2)for(let ox=0;ox<M;ox+=t)for(let oy=0;oy<M;oy+=t)for(let z of tup(M,4)){
   let truth=false,indX=false,indY=false;
   if(real(z)){
    for(let x=ox;x<Math.min(m,ox+t);x++)for(let y=oy;y<Math.min(m,oy+t);y++){
     let v=[...z,x,y];truth ||= F.every(s=>!bad(s,v));counts.localPairs++;
    }
    indX=[...Array(Math.min(t,Math.max(0,m-ox))).keys()].some(i=>F.filter(s=>s.h.every(a=>a<4||a===4)).every(s=>!bad(s,[...z,ox+i,0])));
    indY=[...Array(Math.min(t,Math.max(0,m-oy))).keys()].some(i=>F.filter(s=>s.h.every(a=>a<4||a===5)).every(s=>!bad(s,[...z,0,oy+i])));
   }
   let got=filter(z,ox,oy,t);ok(got===truth,"local exact join");counts.localKeys++;
   if(indX&&indY&&!truth)counts.strictOld++;
   if(got&&t<M){ok(filter(z,Math.floor(ox/(2*t))*2*t,Math.floor(oy/(2*t))*2*t,2*t),"nested");counts.nesting++;}
  }
 }
 ok(counts.oldMiss===50&&counts.exactMiss===0&&counts.strictOld>0,"expected failures");
 let fields=[];
 for(let [m,poly,B] of [[16,19,4],[32,37,8],[64,67,16]]){
  function mul(a,b){let r=0;while(b){if(b&1)r^=a;b>>=1;a<<=1;if(a&m)a^=poly;}return r;}
  let q=m/2,J=m/4,D=J*(m-J),raw,attempts=0;
  do{
   let P=Array.from({length:m*m},(_,i)=>i);
   for(let i=P.length-1;i>0;i--){let j=(rand()>>>0)%(i+1);[P[i],P[j]]=[P[j],P[i]];}
   raw=Array.from({length:m},(_,a)=>Uint8Array.from(P,i=>+( (mul(a,Math.floor(i/m))^(i%m))<J)));
   attempts++;
   ok(attempts<=100,"finite escape selection");
  }while(!raw.every(r=>{for(let x=0;x<m;x+=B)for(let y=0;y<m;y+=B){let any=false;for(let v=y;v<y+B;v++)any ||= !r[x*m+v];if(!any)return false;}return true;}));
  let pairChecks=0,rawMass=0,realMass=0,rootKeys=0,first=0,marginal=0,even=0,odd=0;
  for(let j=0;j<Math.log2(m)-1;j++)if(j%2)odd|=1<<j;else even|=1<<j;
  for(let a=0;a<m;a++)for(let b=0;b<m;b++)if(a!==b){
   let n=0,v=0;for(let x=0;x<m;x++)for(let y=0;y<m;y++){let e=+(!raw[a][x*m+y]&&raw[b][x*m+y]);n+=e;if(x%B===0)v+=e;}
   ok(n===D,"pair invariance");pairChecks++;
   if(b>=q){rawMass+=n;realMass+=v;for(let x=0;x<m;x+=B)for(let y=0;y<m;y+=B){ok(raw[a].slice(x*m+y,x*m+y+B).some(v=>v===0),"joint root feasible");rootKeys++;}}
  }
  let gate=m*(m-m/B);
  for(let f=q;f<m;f++){
   const loss=(a,b)=>(a===b?0:D)+gate*(+(a>=q&&b<q)+ +((a&even)===(f&even)&&(b&even)!==(f&even))+ +((a&odd)===(f&odd)&&(b&odd)!==(f&odd)));
   let sums=Array(m).fill(0);for(let a=0;a<m;a++)for(let b=0;b<m;b++)sums[b]+=loss(a,b);
   ok(sums.every((v,b)=>b===f||v>sums[f]),"first target");first++;
   for(let b=0;b<m;b++)if(b!==f){let g=0;for(let a=0;a<m;a++)g+=Math.max(0,loss(a,f)-loss(a,b));ok(g<=D&&g<m*m,"marginal");marginal++;}
  }
  ok(realMass>0&&realMass<rawMass,"nontrivial actual corrections");
  let multiplicity=m**3/q;
  fields.push([m,B,attempts,pairChecks,rootKeys,rawMass*multiplicity,rawMass*multiplicity,realMass*multiplicity,first,marginal]);
 }
 return {counts,fields};
}
console.log('F038_FAR_PAIR_UNION_OK '+JSON.stringify(audit()));
