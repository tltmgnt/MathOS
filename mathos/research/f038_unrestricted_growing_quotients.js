// Standalone semantic audit, not physical tape timing.
function audit(){
 const need=(x,s)=>{if(!x)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* cart(D,p=[]){if(p.length===D.length){yield p;return;}for(let a of D[p.length])yield* cart(D,p.concat(a));}
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 const H=[...sub(1),...sub(2),...sub(3)],project=(z,h)=>h.map(g=>z[g]);
 let totals=Array(9).fill(0);
 for(let m of [2,3])for(let B of [1,2,m])for(let mode=0;mode<6;mode++){
  let L=G.map(g=>Array.from({length:m},(_,a)=>(a+g)%B)),D=G.map(g=>Array.from({length:B},(_,c)=>Array.from({length:m},(_,a)=>a).filter(a=>L[g][a]===c)));
  let tables=H.map(h=>{
   let F=new Set(),C=new Map();
   for(let z of tuples(m,h.length)){
    let bad=mode===1&&h.length===1&&h[0]===0||mode===2&&h.length===2&&h[1]===h[0]+1&&z[0]!==z[1]||mode===3&&h.length===3&&(z.reduce((s,a,i)=>s+(i+2)*a,0)+h.reduce((s,a)=>s+a,0))%5===0||mode===4&&h.length===3&&z.some(a=>a!==0)||mode===5&&h.length===2&&z[0]===1&&z[1]===1;
    let k=key(z.map((a,i)=>L[h[i]][a]));if(!C.has(k))C.set(k,[0,0]);let v=C.get(k);v[1]++;if(bad){v[0]++;F.add(key(z));}
   }
   let E=new Set(),err=0;
   for(let z of tuples(m,h.length)){let [f,n]=C.get(key(z.map((a,i)=>L[h[i]][a]))),q=2*f>n,x=F.has(key(z));if(q!==x)err++;if(q&&!x)E.add(key(z));}
   return {h,F,C,E,err};
  });
  let deltaN=tables.reduce((s,T)=>s+T.err*m**(9-T.h.length),0);
  let mass=0,viol=0,light=0,heavy=0,boxes=0;
  for(let c of tuples(B,9)){
   let n=c.reduce((p,a,g)=>p*D[g][a].length,1);
   let cells=tables.map(T=>T.C.get(key(project(c,T.h))));
   if(cells.some(([f,d])=>2*f>d))continue;
   boxes++;mass+=n;
   let v=cells.reduce((s,[f,d])=>s+f*(n/d),0);viol+=v;
   if(v<n)light++;else heavy++;
  }
  need(viol<=deltaN,"aggregate violation mass");
  if(!light)need(mass<=deltaN,"no-light mass");
  let models=0,exceptions=0,aug=0,checks=0;
  for(let z of tuples(m,9)){
   let orig=tables.every(T=>!T.F.has(key(project(z,T.h))));
   let e=tables.some(T=>T.E.has(key(project(z,T.h))));
   let c=z.map((a,g)=>L[g][a]);
   let q=tables.every(T=>{let [f,n]=T.C.get(key(project(c,T.h)));return 2*f<=n;});
   let x=orig&&e,y=orig&&q;need(orig===(x||y),"exact exception-augmented union");need(!(x&&y),"union split");
   models+=orig;exceptions+=x;aug+=y;checks++;
  }
  // Verify class-contiguous tile occupancy bound with a coarse quotient-only necessary test.
  let M=1;while(M<m)M*=2;
  let order=D.map(A=>A.flat());
  for(let t=1;t<=M;t*=2){
   let q=M/t,bad=G.map(g=>Array.from({length:q},(_,j)=>{let a=order[g].slice(j*t,(j+1)*t);return a.length!==t||new Set(a.map(x=>L[g][x])).size!==1;}));
   let pass=0;
   for(let z of tuples(q,9)){
    if(z.some((j,g)=>j*t>=m))continue;
    if(z.some((j,g)=>bad[g][j])){pass++;continue;}
    let c=z.map((j,g)=>L[g][order[g][j*t]]);
    if(tables.every(T=>{let [f,n]=T.C.get(key(project(c,T.h)));return 2*f<=n;}))pass++;
   }
   need(pass*t**9<=mass+9*(B+1)*t*M**8,"boundary occupancy");
   totals[8]++;
  }
  [models,exceptions,aug,checks,boxes,light,heavy,+!light].forEach((v,i)=>totals[i]+=v);
 }
 const cyc=(i,j)=>j-i===1||i===0&&j===8,par=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 let controls=[];
 for(let q of [2,4,8,16]){
  let m=4*q*q+1;
  const label=a=>(a-1)>>1,ty=a=>(a-1)&1,c=a=>label(a)%2?Math.floor(label(a)/2)%q:0;
  const allow=(i,j,a,b)=>!a||!b?(!cyc(i,j)||a===b):cyc(i,j)?ty(a)!==ty(b)&&label(a)!==label(b):par(c(a)&c(b))===0&&a!==b;
  const approx=(i,j,a,b)=>!a||!b?(!cyc(i,j)||a===b):cyc(i,j)?ty(a)!==ty(b):par(c(a)&c(b))===0;
  let errs=0,min=Infinity,rows=[];
  for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)for(let a=0;a<m;a++)for(let b=0;b<m;b++)errs+=allow(i,j,a,b)!==approx(i,j,a,b);
  for(let x=0;x<q;x++)rows.push(Array.from({length:m},(_,b)=>+allow(0,2,1+2*(2*x+1),b)));
  for(let x=0;x<q;x++)for(let y=x+1;y<q;y++){let d=rows[x].reduce((s,a,i)=>s+(a!==rows[y][i]),0);min=Math.min(min,d);need(d>=q*q-2,"separated signatures");}
  need(errs<=36*m,"approximation errors");
  // All-zero is feasible; nonzero status and type constraints prove uniqueness.
  need(G.every(i=>G.slice(i+1).every(j=>allow(i,j,0,0))),"zero witness");
  controls.push([q,m,errs,min]);
 }
 return {fixtures:36,totals,controls};
}
console.log('F038_GROWING_QUOTIENTS_OK '+JSON.stringify(audit()));
