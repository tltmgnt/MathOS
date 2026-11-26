// Standalone semantic and abstract layout audit, not a physical tape simulator.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],P=[0,1,2,3,4,5],key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 let totals=Array(13).fill(0),schedule=Array(9).fill(0),fixtures=0,mixed=0,maxExtent=0;
 for(let m of [2,3])for(let mode=0;mode<6;mode++){
  let M=1;while(M<m)M*=2;let B=2,b0=1;while((2*b0)**2<=m)b0*=2;
  let R=H.map(h=>({h,F:new Set([...tup(m,h.length)].filter(z=>{
   if(mode===0)return false;
   if(mode===1)return key(h)==="0,4,5"&&z[0]===z[2]&&z[1]!==z[2];
   if(mode===2)return key(h)==="0,4,5"&&z[0]===1&&z[1]===z[2]||h.length===1&&h[0]===8&&z[0]===1;
   if(mode===3)return h.length===3&&(h.reduce((s,g)=>s+g,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===4)return h.length===1&&z[0]!==h[0]%m;
   return key(h)==="0,4,5"&&z[0]!==z[2]&&z[1]===0||h.length===2&&h[0]===0&&z[0]===z[1];
  }).map(key))}));
  let T=R.find(s=>key(s.h)==="0,4,5"),p=(a,d,e,t)=>(d+e+t+1)%m;
  const allow=z=>z.every(a=>a<m)&&!T.F.has(key([z[0],z[4],z[5]]))&&T.F.has(key([p(...z.slice(0,4)),z[4],z[5]]));
  let pred=z=>R.every(s=>!s.F.has(key(proj(z,s.h)))),raw=R.flatMap(s=>[...s.F].map(z=>[s.h,z.split(",").map(Number)]));
  for(let g of G)for(let a=m;a<M;a++)raw.push([[g],[a]]);
  let expected=new Set(),got=new Set(),mass=0,models=0,checks=0;
  for(let z of tup(m,6))mass+=allow(z);
  for(let z of tup(m,9)){checks++;if(pred(z)&&allow(z.slice(0,6)))expected.add(key(z));if(pred(z))models++;}
  let stats=Array(9).fill(0),layers=new Map();
  let tiles=[],heavy=0,light=0,split=0,rootMass=0;
  // Forced B=2 on small fixtures to exercise the cap; the production scale is checked separately.
  for(let block of tup(M/B,6)){
   let po=block.map(a=>a*B),r=0;
   for(let z of tup(B,6))r+=allow(z.map((a,i)=>a+po[i]));
   schedule[0]++;schedule[1]+=B**6;rootMass+=r;
   if(B**6*r>m**6){
    heavy++;for(let d of tup(B/b0,6)){tiles.push({po:po.map((a,i)=>a+d[i]*b0),b:b0});split++;}
   }else{light++;tiles.push({po,b:B});}
  }
  ok(rootMass===mass,"root mass");
  ok(heavy*m**6<=mass*B**6,"heavy census bound");
  ok(tiles.reduce((n,x)=>n+x.b**6,0)===M**6,"mixed-scale partition volume");
  ok(split===heavy*(B/b0)**6,"fallback tile count");
  if(heavy&&light)mixed++;
  schedule[2]+=heavy;schedule[3]+=light;schedule[4]+=split;
  let seenProjection=new Set();
  for(let {po,b} of tiles){
   let pos=0;
   for(let z of tup(b,6)){let k=key(z.map((a,i)=>a+po[i]));ok(!seenProjection.has(k),"partition disjointness");seenProjection.add(k);}
   schedule[5]++;
   // Builder cache: only projected block maps and raw rows on the u,v intervals.
   let map=new Map(),bits=new Map();
   for(let z of tup(b,4)){let x=z.map((a,i)=>a+po[i]);if(x.every(a=>a<m))map.set(key(x),p(...x));}
   for(let a=0;a<m;a++)for(let z of tup(b,2)){let x=z.map((v,i)=>v+po[i+4]);if(x.every(v=>v<m))bits.set(key([a,...x]),T.F.has(key([a,...x])));}
   function test(z){let x=z.map((a,i)=>a+po[i]);let v=x.every(a=>a<m)&&!bits.get(key([x[0],x[4],x[5]]))&&bits.get(key([map.get(key(x.slice(0,4))),x[4],x[5]]));ok(v===allow(x),"factorized membership");stats[0]++;return v;}
   function build(t,off){
    let start=pos++,r=0;for(let z of tup(t,6))r+=test(z.map((a,i)=>a+off[i]));
    stats[1]++;
    if(!r){stats[2]++;return {start,end:pos,t,r,cap:0,child:[]};}
    let cap=130*t**3;pos+=cap;let child=[];
    if(t>1){for(let d of tup(2,6))child.push(build(t/2,off.map((a,i)=>a+d[i]*t/2)));
     ok(child.reduce((s,c)=>s+c.r,0)===r,"OR and count");}
    let end=pos;ok(end-start<=10000*t**3*Math.sqrt(r)*(1+Math.log2(t)),"sparse tree extent");
    ok(child.every((c,i)=>c.start>=start+1+cap&&c.end<=end&&(!i||c.start===child[i-1].end)),"preorder");
    stats[3]++;return {start,end,t,r,cap,child,active:false};
   }
   let root=build(b,Array(6).fill(0));stats[4]+=pos;
   ok(b**6*root.r<=m**6,"tree cap");schedule[6]++;
   ok(pos<=10000*m**3*(1+Math.log2(b)),"abstract original-scale extent");
   maxExtent=Math.max(maxExtent,pos);
   if(root.r===0)schedule[7]++;
   for(let q of tup(M/b,3)){
    schedule[8]++;
    let off=[...po,...q.map(a=>a*b)],C=[];
    for(let [h,z] of raw){let v=z.map((a,i)=>a-off[h[i]]);if(v.every(a=>a>=0&&a<b))C.push([h,v]);}
    function visit(node,off,C){
     if(!node.r)return;
     ok(!node.active&&C.length<node.cap,"frame capacity");node.active=true;stats[5]++;
     let t=node.t,v=layers.get(t)||[0,0,0];v[0]++;v[1]+=node.r;v[2]+=Math.sqrt(node.r);layers.set(t,v);
     if(t===1){stats[6]++;let pass=C.length===0;ok(pass===(off.every(a=>a<m)&&pred(off)&&allow(off.slice(0,6))),"exact leaf");
      if(pass){ok(!got.has(key(off)),"disjoint");got.add(key(off));}}
     else for(let d of tup(2,9)){
      let idx=d.slice(0,6).reduce((s,a)=>2*s+a,0),ch=node.child[idx];stats[7]++;
      if(!ch.r)continue;
      let o=d.map(a=>a*t/2),cc=[];
      for(let [h,z] of C){let w=z.map((a,i)=>a-o[h[i]]);if(w.every(a=>a>=0&&a<t/2))cc.push([h,w]);}
      ok((1+C.length+cc.length)*(ch.start-node.start+node.cap+ch.cap)<=100000*t**6*Math.sqrt(node.r)*(1+Math.log2(t)),"abstract shuttle charge");stats[8]++;
      visit(ch,off.map((a,i)=>a+o[i]),cc);ok(!ch.active&&node.active,"exclusive active frames");
     }
     node.active=false;
    }
    visit(root,off,C);
   }
  }
  ok(seenProjection.size===M**6,"complete projected partition");
  ok((layers.get(1)||[0,0,0])[1]===mass*M**3,"leaf mass conservation");
  ok(got.size===expected.size&&[...got].every(x=>expected.has(x)),"exact branch model set");
  for(let [t,[n,s,v]] of layers){
   ok(s<=mass*(M/t)**3,"mass bound across mixed scales");
   ok(n<=Math.min((M/t)**9,mass*(M/t)**3),"positive node bound");
   ok(v*v<=n*s+1e-6*Math.max(1,n*s),"Cauchy bound");
  }
  [mass,models,checks,got.size,...stats].forEach((v,i)=>totals[i]+=v);fixtures++;
 }
 let controls=[];
 for(let m of [3,5,9,17]){
  let R=m**3*(m-1)**2,rare=m**3*(m-1),U=m**3*(m-1)**2;
  // Every retained pair and source sees each representative exactly once.
  let f=0;
  for(let d=0;d<m;d++)for(let e=0;e<m;e++){let N=Array(m).fill(0);for(let t=0;t<m;t++)N[(d+e+t)%m]++;ok(N.every(x=>x===1),"uniform third digit");f++;}
  let count=0;for(let c of tup(m,3))for(let a=0;a<m;a++)if(a!==(c[0]+c[1]+c[2])%m)count+=m-1;
  ok(count===R,"exact width-six mass");controls.push([m,R,U,rare,f]);
 }
 let scaleChecks=0;
 for(let m=2;m<=4096;m++){
  let n=BigInt(m),b0=1n;while((2n*b0)**2n<=n)b0*=2n;
  for(let p of [1,Math.max(1,Math.floor(Math.sqrt(m))),Math.max(1,Math.floor(m/2)),m]){
   // sigma=p/m, so b^16*p<=m^9.
   let b=1n;while((2n*b)**16n*BigInt(p)<=n**9n)b*=2n;
   ok(b>=b0&&b**16n*BigInt(p)<=n**9n&&(2n*b)**16n*BigInt(p)>n**9n,"adaptive dyadic scale");
   ok(b**16n<=n**9n&&b0**12n<=n**6n,"cache and fallback exponents");
   let sig=p/m,w=Number(b);
   ok((w*w/m)**6*sig<=Math.pow(sig,.25)*(1+1e-12),"heavy fraction estimate");
   ok(m*m/(w**4)<=16*Math.pow(sig,.25)*(1+1e-12),"pair regeneration estimate");
   scaleChecks++;
  }
 }
 return {fixtures,totals,schedule,mixed,maxExtent,scaleChecks,controls};
}
console.log('F038_SPACE_CAPPED_WIDTH_SIX_OK '+JSON.stringify(audit()));
