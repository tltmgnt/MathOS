// FV-09: actual affine producer, independent certificate replay, local
// materialization, exhaustive small-image oracle and large sparse support.
const U=require('./f038_rex_variable_rank_reduction.js');
const A=require('./f038_rex_variable_affine_closure.js');
const V=require('./f038_rex_variable_affine_certificate.js');
const L=require('./f038_rex_fv09_local.js');
const ok=(b,s)=>{if(!b)throw Error("FV09: "+s);};
const f=(h,rows)=>({h,S:new Set(rows)});
const d=(k,F)=>({k,m:2,F});
const model=(d,z)=>d.F.every(f=>f.S.has(f.h.map(i=>z[i]).join()));
const clone=r=>({...r,d:{...r.d,F:r.d.F.map(f=>({h:f.h.slice(),S:new Set(f.S)}))}});
const parity=f=>f.join();
function checkImage(input,r){
 const m=r.a.free.length,image=new Set();
 for(const z of U.tuples(2,r.d.k)){
  if(!model(r.d,z))continue;
  const x=r.expand(z);
  ok(model(input,x),"false residual witness");
  image.add(x.join());
 }
 for(const x of U.tuples(2,input.k))ok(model(input,x)===image.has(x.join()),"missing image");
}
function audit(){
 let seed=73459;
 const rnd=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;};
 let accepted=0,unsupported=0,localRows=0,exhaustive=0,rejected=0;
 for(let t=0;t<128;t++){
  const k=1+t%5,fs=[];
  for(let j=0;j<1+t%7;j++){
   const width=1+rnd(Math.min(k,3)),h=[];
   while(h.length<width){const v=rnd(k);if(!h.includes(v))h.push(v);}
   h.sort((a,b)=>a-b);
   fs.push(f(h,[...U.tuples(2,width)].filter(()=>rnd(5)>0).map(parity)));
  }
  const input=d(k,fs),r=A.reduce(U,input);
  if(r.kind!=="narrow"){ok(L.replay(input,r)===null,"unsupported kind accepted");unsupported++;continue;}
  V.verify(input,r.a);
  const a=L.replay(input,r);
  ok(a,"narrow replay");localRows+=a.rows;accepted++;
  checkImage(input,r);exhaustive++;
 }
 const eq=["0,0","1,1"],non=["0,0","0,1","1,0"],odd=["0,1","1,0","1,1"];
 const large=d(64,[f([0,1],eq),f([2,3],non),f([2,3],odd),f([60,61,63],["0,0,0","0,0,1","1,1,0"])]);
 const r=A.reduce(U,large);
 ok(r.kind==="narrow","large narrow");V.verify(large,r.a);
 const a=L.replay(large,r);
 ok(a&&a.free>10&&a.maxWidth<=3,"large local replay");
 ok(a.rows<=large.F.length*8,"local row ceiling");
 const bad=clone(r);bad.d.F[0].S.add("1,1");
 for(const [input,b,cap] of [
  [large,bad,8],[large,{...r,d:{...r.d,F:[]}},8],[large,r,1],
  [large,{...r,kind:"wide-fallback"},8],
  [large,{...r,a:{...r.a,forms:r.a.forms.map((f,i)=>i?f:{...f,mask:1n<<64n})}},8]
 ]){ok(L.replay(input,b,cap)===null,"corrupt accepted");rejected++;}
 const forced=d(1,[f([0],["1"])]),fr=A.reduce(U,forced);
 V.verify(forced,fr.a);ok(L.replay(forced,fr)&&fr.a.free.length===0,"zero-free padding");checkImage(forced,fr);
 const even=["0,0,0","0,1,1","1,0,1","1,1,0"];
 const wide=d(8,[f([0,1,2],even),f([2,3,4],even),f([4,5,6],even),f([6,7],non)]);
 const wr=A.reduce(U,wide);
 ok(wr.kind==="wide-fallback"&&L.replay(wide,wr)===null,"actual wide fallback");
 return {small:128,accepted,unsupported,localRows,exhaustive,rejected,large:{source:large.k,free:a.free,rows:a.rows,maxWidth:a.maxWidth},zeroFree:true,wideFallback:true};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit()));
