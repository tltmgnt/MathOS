// D7C: fixed-width host resolution and explicit five-coordinate NAE certificates.
function clauses(d){
 const out=[], seen=new Set();
 for(let f=0;f<d.F.length;f++){
  const {h,S}=d.F[f];
  for(let mask=0;mask<2**h.length;mask++){
   const row=h.map((_,i)=>(mask>>i)&1);
   if(S.has(row.join()))continue;
   const c=h.map((v,i)=>row[i]?-(v+1):v+1).sort((a,b)=>Math.abs(a)-Math.abs(b));
   if(!seen.has(c.join())){seen.add(c.join());out.push({c,f});}
  }
 }
 return out;
}

function resolution(d,width=4){
 if(d.m!==2||![3,4].includes(width))throw Error("binary width 3 or 4");
 const nodes=clauses(d), seen=new Set(nodes.map(n=>n.c.join()));
 let pairs=0;
 for(let i=0;i<nodes.length;i++){
  const a=nodes[i].c;
  if(!a.length)return {kind:"resolution",width,nodes:nodes.slice(0,i+1),pairs};
  for(let j=0;j<i;j++){
   const b=nodes[j].c; pairs++;
   const piv=a.filter(x=>b.includes(-x));
   if(piv.length!==1)continue;
   const p=piv[0],c=[...new Set([...a.filter(x=>x!==p),...b.filter(x=>x!==-p)])].sort((x,y)=>Math.abs(x)-Math.abs(y));
   if(c.length>width||seen.has(c.join()))continue;
   seen.add(c.join());nodes.push({c,i,j,p});
   if(!c.length)return {kind:"resolution",width,nodes,pairs};
  }
 }
 return {kind:"unknown",width,clauses:nodes.length,pairs};
}

function cardinality(d){
 if(d.m!==2)throw Error("binary");
 const lookup=new Map();
 for(let f=0;f<d.F.length;f++){
  const {h,S}=d.F[f];
  if(h.length===3&&!S.has("0,0,0")&&!S.has("1,1,1"))lookup.set(h.slice().sort((a,b)=>a-b).join(),f);
 }
 let trials=0;
 for(let a=0;a<d.k;a++)for(let b=a+1;b<d.k;b++)for(let c=b+1;c<d.k;c++)for(let e=c+1;e<d.k;e++)for(let g=e+1;g<d.k;g++){
  trials++;const v=[a,b,c,e,g],factors=[];
  for(let i=0;i<5;i++)for(let j=i+1;j<5;j++)for(let l=j+1;l<5;l++)factors.push(lookup.get([v[i],v[j],v[l]].join()));
  if(factors.every(x=>x!==undefined))return {kind:"cardinality",v,factors,trials};
 }
 return {kind:"unknown",trials};
}

function reduce(d,verify,width=4){
 const C=cardinality(d),cert=C.kind==="unknown"?resolution(d,width):C;
 if(cert.kind==="unknown")return {d,cert,contradiction:false,expand:z=>z};
 if(verify(d,cert)!==true)throw Error("unverified contradiction");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={clauses,resolution,cardinality,reduce};
