// D7C: independent local axiom and inference verifier; no dependency on producer.
function verify(d,cert){
 const ok=(b)=>{if(!b)throw Error("invalid non-affine certificate");};
 ok(d.m===2&&Number.isSafeInteger(d.k)&&d.k>=1);
 if(cert.kind==="cardinality"){
  const {v,factors}=cert;
  ok(Array.isArray(v)&&v.length===5&&v.every((x,i)=>Number.isSafeInteger(x)&&x>=0&&x<d.k&&(!i||x>v[i-1])));
  ok(Array.isArray(factors)&&factors.length===10);
  let p=0;
  for(let i=0;i<5;i++)for(let j=i+1;j<5;j++)for(let l=j+1;l<5;l++){
   const id=factors[p++];ok(Number.isSafeInteger(id)&&id>=0&&id<d.F.length);
   const f=d.F[id],scope=[v[i],v[j],v[l]];
   ok(f.h.length===3&&scope.every(x=>f.h.includes(x))&&!f.S.has("0,0,0")&&!f.S.has("1,1,1"));
  }
  return true;
 }
 ok(cert.kind==="resolution"&&[3,4].includes(cert.width)&&Array.isArray(cert.nodes)&&cert.nodes.length>0);
 const N=cert.nodes;
 for(let t=0;t<N.length;t++){
  const n=N[t],c=n.c;
  ok(Array.isArray(c)&&c.length<=cert.width&&c.every((x,i)=>Number.isSafeInteger(x)&&x!==0&&Math.abs(x)<=d.k&&(!i||Math.abs(x)>Math.abs(c[i-1]))));
  if(Object.prototype.hasOwnProperty.call(n,"f")){
   ok(Number.isSafeInteger(n.f)&&n.f>=0&&n.f<d.F.length);
   const f=d.F[n.f];
   ok(c.length===f.h.length&&f.h.every(x=>c.some(y=>Math.abs(y)===x+1)));
   // A clause from a factor is valid precisely when its unique falsifying row is absent.
   const row=f.h.map(x=>c.includes(x+1)?0:1).join();
   ok(!f.S.has(row));
  }else{
   ok(Number.isSafeInteger(n.i)&&Number.isSafeInteger(n.j)&&n.i>=0&&n.j>=0&&n.i<t&&n.j<t&&n.i!==n.j);
   const A=N[n.i].c,B=N[n.j].c;
   ok(Number.isSafeInteger(n.p)&&n.p!==0&&A.includes(n.p)&&B.includes(-n.p));
   // Independent literal-membership check, not the producer's union construction.
   for(const x of [...A,...B])if(x!==n.p&&x!==-n.p)ok(c.includes(x));
   for(const x of c)ok(x!==n.p&&x!==-n.p&&(A.includes(x)||B.includes(x)));
  }
 }
 ok(N.at(-1).c.length===0);return true;
}
module.exports={verify};
