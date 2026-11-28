// Independent verification of semijoin certificates. Deliberately uses
// direct row-to-row matching, not the producer's projection hash sets.
function verify(input,output,log){
 const ok=(v,s)=>{if(!v)throw Error(s)},F=input.F.map(f=>({h:f.h.slice(),S:new Set(f.S)}));let comparisons=0,deleted=0;
 const support=(A,t,B)=>{
  const a=t.split(",");for(const u of B.S){comparisons++;const b=u.split(",");if(A.h.every((v,i)=>!B.h.includes(v)||a[i]===b[B.h.indexOf(v)]))return true;}return false;
 };
 for(const e of log){
  ok(Number.isInteger(e.a)&&Number.isInteger(e.b)&&e.a!==e.b&&F[e.a]&&F[e.b]&&F[e.a].h.some(v=>F[e.b].h.includes(v)),"certificate endpoints");
  ok(!F.some(f=>!f.S.size),"certificate after contradiction");
  const A=F[e.a],B=F[e.b],removed=[...A.S].filter(t=>!support(A,t,B));
  ok(removed.length>0&&JSON.stringify(removed)===JSON.stringify(e.removed),"certificate deletion");
  for(const t of removed){A.S.delete(t);deleted++;}
 }
 ok(input.k===output.k&&input.m===output.m&&F.length===output.F.length,"certificate shape");
 for(let i=0;i<F.length;i++)ok(F[i].h.join()===output.F[i].h.join()&&F[i].S.size===output.F[i].S.size&&[...F[i].S].every(t=>output.F[i].S.has(t)),"certificate output");
 const contradiction=F.some(f=>!f.S.size);
 if(!contradiction)for(let a=0;a<F.length;a++)for(let b=0;b<F.length;b++)if(a!==b&&F[a].h.some(v=>F[b].h.includes(v)))for(const t of F[a].S)ok(support(F[a],t,F[b]),"not fixed point");
 return {comparisons,deleted,contradiction};
}
module.exports={verify};
