// Standalone quotient semantics; no physical tape timing claims.
function audit(){
 const need=(x,s)=>{if(!x)throw Error(s)},G=[0,1,2,3,4,5,6,7,8];
 function* subsets(a,k,start=0,p=[]){if(p.length===k){yield p;return;}for(let i=start;i<=a.length-k+p.length;i++)yield* subsets(a,k,i+1,p.concat(a[i]));}
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* cart(D,p=[]){if(p.length===D.length){yield p;return;}for(let a of D[p.length])yield* cart(D,p.concat(a));}
 const H=[...subsets(G,1),...subsets(G,2),...subsets(G,3)],key=z=>z.join(","),proj=(z,h)=>h.map(g=>z[g]);
 function make(m,rule){let rel=[];for(let h of H){let bad=new Set();for(let z of tuples(m,h.length))if(rule(h,z))bad.add(key(z));if(bad.size)rel.push({h,bad});}return rel;}
 function clusters(m,B,rel){
  let labs=[],classes=[],radius=0;
  for(let g of G){
   let rows=Array.from({length:m},()=>[]);
   for(let {h,bad} of rel)if(h.includes(g)){
    let i=h.indexOf(g),w=m**(3-h.length);
    for(let a=0;a<m;a++)for(let z of tuples(m,h.length-1)){let x=z.slice();x.splice(i,0,a);rows[a].push([+bad.has(key(x)),w]);}
   }
   function dist(a,b){let d=0;for(let i=0;i<rows[a].length;i++)if(rows[a][i][0]!==rows[b][i][0])d+=rows[a][i][1];return d;}
   let centers=[0],D=rows.map((_,a)=>dist(a,0));
   while(centers.length<Math.min(m,B)){
    let best=0;for(let a=1;a<m;a++)if(D[a]>D[best])best=a;
    if(!D[best])break;centers.push(best);D=D.map((d,a)=>Math.min(d,dist(a,best)));
   }
   let L=rows.map((_,a)=>{let j=0;for(let i=1;i<centers.length;i++)if(dist(a,centers[i])<dist(a,centers[j]))j=i;return j;});
   let C=centers.map(()=>[]);for(let a=0;a<m;a++)C[L[a]].push(a);
   need(C.every(c=>c.length>0),"nonempty classes");labs.push(L);classes.push(C);radius=Math.max(radius,...D);
  }return {labs,classes,radius};
 }
 function quotient(m,rel,C){
  let delta=0,out=[];
  for(let {h,bad} of rel){
   let counts=new Map(),sizes=new Map(),Q=new Set(),E=new Set(),err=0;
   for(let z of tuples(m,h.length)){
    let k=key(z.map((a,i)=>C.labs[h[i]][a]));sizes.set(k,(sizes.get(k)||0)+1);if(bad.has(key(z)))counts.set(k,(counts.get(k)||0)+1);
   }
   for(let [k,n] of sizes)if(2*(counts.get(k)||0)>n)Q.add(k);
   for(let z of tuples(m,h.length)){
    let x=bad.has(key(z)),y=Q.has(key(z.map((a,i)=>C.labs[h[i]][a])));
    if(x!==y)err++;if(!x&&y)E.add(key(z));
   }
   need(err*m*m<=2*h.length*C.radius*m**h.length,"weighted radius error bound");
   delta+=err/m**h.length;out.push({h,bad,Q,E,err});
  }return {delta,out};
 }
 function potential(D,rel){
  let n=D.reduce((p,a)=>p*a.length,1),v=0;
  for(let {h,bad} of rel){let d=h.reduce((p,g)=>p*D[g].length,1),f=0;for(let z of cart(h.map(g=>D[g])))if(bad.has(key(z)))f++;v+=f*(n/d);}
  return [v,n];
 }
 function conditional(D,rel){
  D=D.map(a=>a.slice());let old=potential(D,rel);need(old[0]<old[1],"initial potential");
  for(let g of G){let best=null,bp=null;for(let a of D[g]){
   let E=D.slice();E[g]=[a];let p=potential(E,rel);
   if(!bp||p[0]*bp[1]<bp[0]*p[1]){best=a;bp=p;}
  }need(bp[0]*old[1]<=old[0]*bp[1],"conditional expectation");D[g]=[best];old=bp;}
  need(old[0]===0,"zero violations");return D.map(a=>a[0]);
 }
 function run(m,B,mode){
  let rel=make(m,(h,z)=>{
   if(mode===0)return false;
   if(mode===1)return h.length===1&&h[0]===0;
   if(mode===2)return h.length===1&&z[0]!==h[0]%m;
   if(mode===3)return h.length===2&&h[1]===h[0]+1&&z[0]!==z[1];
   if(mode===4)return h.length===3&&(h.reduce((s,g)=>s+g,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===5)return h.length===3&&z.some(a=>a!==0);
   if(mode===6)return h.length===2&&z[0]===1&&z[1]===1;
   return h.length===2&&h[0]===0&&h[1]===8&&z[0]!==0&&z[1]!==0;
  });
  let C=clusters(m,B,rel),{delta,out}=quotient(m,rel,C),pass=z=>out.every(({h,bad})=>!bad.has(key(proj(z,h))));
  let expected=new Set(),recovered=new Set(),exceptionModels=0,exceptions=0,boxes=0,cheap=0,heavy=0,conditionalChecks=0;
  for(let z of tuples(m,9))if(pass(z))expected.add(key(z));
  for(let {h,E} of out)if(E.size){exceptions++;for(let z of tuples(m,9))if(E.has(key(proj(z,h)))&&pass(z)){recovered.add(key(z));exceptionModels++;}}
  for(let Q of cart(C.classes.map(A=>A.map((_,i)=>i)))){
   if(out.some(({h,Q:S})=>S.has(key(proj(Q,h)))))continue;boxes++;
   let D=Q.map((c,g)=>C.classes[g][c]),[v,n]=potential(D,rel),p=Math.min(...D.map(a=>a.length))/m;
   if(v<n){cheap++;let w=conditional(D,rel);need(pass(w)&&w.every((a,g)=>D[g].includes(a)),"conditional witness");conditionalChecks+=9;}
   else{heavy++;need(p**3<=delta+1e-12,"heavy box sparse");}
   for(let z of cart(D))if(pass(z))recovered.add(key(z));
  }
  need(expected.size===recovered.size&&[...expected].every(z=>recovered.has(z)),"complete model union");
  return [m,B,mode,C.radius,expected.size,exceptions,exceptionModels,boxes,cheap,heavy,conditionalChecks];
 }
 let rows=[];for(let m of [2,3])for(let mode=0;mode<8;mode++)for(let B of [1,2])rows.push(run(m,B,mode));
 const cycle=(i,j)=>j-i===1||i===0&&j===8;
 function rule(m,i,j,a,b){
  let h=(m-1)/2;if(!a||!b)return !cycle(i,j)||a===b;
  let x=(a-1)>>1,y=(b-1)>>1,ta=(a-1)&1,tb=(b-1)&1;
  return cycle(i,j)?ta!==tb&&x!==y:!(x>=h/2&&y>=h/2)&&a!==b;
 }
 function types(Q){
  let C=new Map();for(let g of Q)if(!C.has(g)){C.set(g,0);let S=[g];while(S.length){let u=S.pop();for(let v of Q)if(u!==v&&cycle(Math.min(u,v),Math.max(u,v))){if(C.has(v))need(C.get(u)!==C.get(v),"proper coloring");else{C.set(v,1-C.get(u));S.push(v);}}}}return C;
 }
 let controls=[],properChecks=0,occupancyChecks=0;
 for(let m of [33,65,129]){
  let rel=[];for(let h of subsets(G,2)){let bad=new Set();for(let [a,b] of tuples(m,2))if(!rule(m,...h,a,b))bad.add(key([a,b]));rel.push({h,bad});}
  let C=clusters(m,5,rel),{delta,out}=quotient(m,rel,C);
  need(C.radius<=32*m,"linear radius");
  let zero=G.map(()=>0);need(out.every(({h,bad})=>!bad.has(key(proj(zero,h)))),"zero witness");
  let h=(m-1)/2;
  for(let k=2;k<=8;k++)for(let Q of subsets(G,k)){
   let c=types(Q),z=Q.map((g,i)=>1+2*i+c.get(g));
   need(z.every(a=>a<=h)&&[...subsets(Q,2)].every(([i,j])=>rule(m,i,j,z[Q.indexOf(i)],z[Q.indexOf(j)])),"proper join control");properChecks++;
  }
  let M=1;while(M<m)M*=2;
  for(let t=32;t<=M;t*=2){
   let safe=[];for(let j=0;j<M/t;j++)if(j*t>=1&&(j+1)*t-1<=h)safe.push(j);
   if(t<=h/4)need(safe.length>=M/(8*t),"safe occupancy fraction");
   else need(M/t<16||M/t===16,"coarse occupancy fraction");
   for(let j of safe)for(let ty of [0,1])need(Array.from({length:t},(_,a)=>j*t+a).filter(a=>((a-1)&1)===ty).length>=9,"distinct labels");
   occupancyChecks++;
  }
  controls.push([m,C.radius,out.reduce((s,r)=>s+r.err,0),Math.round(delta*1e6)/1e6,C.classes.map(a=>a.length)]);
 }
 let unique=0;for(let m of [5,9]){let z=[];function rec(g){if(g===9){unique++;return;}for(let a=0;a<m;a++)if(z.every((b,i)=>rule(m,i,g,b,a))){z.push(a);rec(g+1);z.pop();}}rec(0);}
 need(unique===2,"unique small controls");
 return {fixtures:rows.length,sums:rows.reduce((a,r)=>a.map((v,i)=>v+r[i+3]),Array(8).fill(0)),controls,properChecks,occupancyChecks,unique};
}
console.log('F038_APPROXIMATE_QUOTIENTS_OK '+JSON.stringify(audit()));
