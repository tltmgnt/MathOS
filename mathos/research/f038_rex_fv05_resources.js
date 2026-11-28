// FV-05: explicit logical word/bit accounting for the D7I projection payload.
// Width is determined by the external original instance dimensions k and f.
// This is not JS object memory, JSON size, nor a physical tape encoding.
function bounds(k,f){
 if(!Number.isSafeInteger(k)||k<0||!Number.isSafeInteger(f)||f<0)throw Error("dimensions");
 const v=2n*BigInt(k),F=BigInt(f),e=8n*F,pairs=v*v,steps=pairs*v;
 const max=[v,F,pairs,1n].reduce((a,b)=>a>b?a:b);
 const width=max.toString(2).length;
 return {v,e,pairs,steps,work:v*e+pairs+steps,width,words:2n+F+3n*pairs+3n*steps,bits:BigInt(width)*(2n+F+3n*pairs+3n*steps)};
}
function encodeProjection(k,f,p){
 const {width}=bounds(k,f),chunks=[];
 const word=x=>{if(!Number.isSafeInteger(x)||x<0||BigInt(x)>=2n**BigInt(width))throw Error("word");chunks.push(x.toString(2).padStart(width,"0"));};
 const lit=l=>{if(!Number.isSafeInteger(l)||l===0||Math.abs(l)>k)throw Error("literal");word(2*(Math.abs(l)-1)+ +(l<0));};
 const factor=i=>{if(!Number.isSafeInteger(i)||i<0||i>=f)throw Error("factor");word(i);};
 word(p.nonbinary.length);word(p.paths.length);
 for(const i of p.nonbinary)factor(i);
 for(const q of p.paths){
  lit(q.x);lit(q.y);word(q.edges.length);
  for(const e of q.edges){lit(e.from);lit(e.to);factor(e.f);}
 }
 return chunks.join("");
}
function decodeProjection(k,f,bits){
 const {width,v,pairs}=bounds(k,f);let at=0;
 if(typeof bits!=="string"||/[^01]/.test(bits)||bits.length%width)throw Error("bits");
 const word=()=>{if(at+width>bits.length)throw Error("truncated");const x=BigInt("0b"+bits.slice(at,at+width));at+=width;if(x>BigInt(Number.MAX_SAFE_INTEGER))throw Error("integer");return Number(x);};
 const lit=()=>{const x=word();if(BigInt(x)>=v)throw Error("literal");return (Math.floor(x/2)+1)*(x%2?-1:1);};
 const factor=()=>{const i=word();if(i>=f)throw Error("factor");return i;};
 const nr=word(),np=word();if(nr>f||BigInt(np)>pairs)throw Error("header");
 const nonbinary=[];for(let i=0;i<nr;i++)nonbinary.push(factor());
 const paths=[];for(let i=0;i<np;i++){
  const x=lit(),y=lit(),n=word(),edges=[];
  if(n<1||BigInt(n)>=v)throw Error("path length");
  for(let j=0;j<n;j++)edges.push({from:lit(),to:lit(),f:factor()});
  paths.push({x,y,edges});
 }
 if(at!==bits.length)throw Error("trailing bits");
 return {nonbinary,paths};
}
function verifyCounts(d,r,limit){
 const m=r.metrics,b=bounds(d.k,d.F.length),ok=(x,s)=>{if(!x)throw Error("resource: "+s);};
 for(const x of Object.values(m))ok(Number.isSafeInteger(x)&&x>=0,"natural count");
 ok(m.vertices===2*d.k&&BigInt(m.edges)<=b.e&&m.options<=m.vertices&&m.starts<=m.options,"graph");
 ok(m.edgeScans<=m.starts*m.edges&&m.pairTests<=m.starts*m.vertices&&m.pathSteps<=m.pairTests*m.vertices&&m.emitted<=m.pairTests,"local");
 ok(m.peakQueue<=m.vertices&&m.peakPredecessors<=m.vertices,"space");
 ok(r.work===m.edgeScans+m.pairTests+m.pathSteps&&r.work<=limit&&BigInt(r.work)<=b.work,"work");
 if(r.kind==="unknown"){ok(r.reason==="budget"&&r.work===limit&&!Object.hasOwn(r,"paths"),"cutoff");return null;}
 ok(r.kind==="projection"&&m.starts===m.options&&m.pairTests===m.options*(m.options-1)/2&&m.emitted===r.paths.length,"complete");
 const steps=r.paths.reduce((n,p)=>n+p.edges.length,0);
 ok(steps===m.pathSteps&&r.paths.every(p=>p.edges.length>0&&p.edges.length<m.vertices),"path lengths");
 const words=2+r.nonbinary.length+3*r.paths.length+3*steps,bits=encodeProjection(d.k,d.F.length,r);
 ok(bits.length===b.width*words&&BigInt(bits.length)<=b.bits,"bits");
 const q=decodeProjection(d.k,d.F.length,bits);
 ok(JSON.stringify(q)===JSON.stringify({nonbinary:r.nonbinary,paths:r.paths}),"round trip");
 return {words,bits:bits.length,width:b.width,workBound:b.work.toString(),bitBound:b.bits.toString()};
}
module.exports={bounds,encodeProjection,decodeProjection,verifyCounts};
