// D7A: exact overlap semijoin closure, with optional replayable deletion log.
// Valid explicit factors only; host preprocessing, not physical execution.
const proj=(h,t,I)=>{const z=t.split(",");return I.map(v=>z[h.indexOf(v)]).join();};
function close(d,certificate=false){
 const F=d.F.map(f=>({h:f.h.slice(),S:new Set(f.S)})),pairs=[],log=[];
 const stats={passes:0,pairs:0,projectionRows:0,testedRows:0,deleted:0,derived:0};
 for(let a=0;a<F.length;a++)for(let b=0;b<F.length;b++)if(a!==b){
  const I=F[a].h.filter(v=>F[b].h.includes(v));if(I.length)pairs.push([a,b,I]);
 }
 function finish(){return {d:{...d,F},stats,log,contradiction:F.some(f=>!f.S.size)};}
 if(F.some(f=>!f.S.size))return finish();
 for(;;){
  let changed=false;stats.passes++;
  for(const [a,b,I] of pairs){
   stats.pairs++;const A=F[a],B=F[b],P=new Set();
   for(const t of B.S){P.add(proj(B.h,t,I));stats.projectionRows++;}
   const removed=[];for(const t of A.S){stats.testedRows++;if(!P.has(proj(A.h,t,I))){A.S.delete(t);removed.push(t);stats.deleted++;}}
   if(removed.length){changed=true;if(certificate)log.push({a,b,removed});if(!A.S.size)return finish();}
  }
  if(!changed)break;
 }
 return finish();
}
function permutation(S,m){
 if(S.size!==m)return false;const a=new Set(),b=new Set();
 for(const t of S){const [x,y]=t.split(",");a.add(x);b.add(y);}
 return a.size===m&&b.size===m;
}
function derivedPairs(U,d){
 const byScope=new Map(d.F.filter(f=>f.h.length===2).map(f=>[f.h.join(),f])),out=[];
 for(const f of d.F)if(f.h.length===3)for(const h of U.subsets(f.h,2)){
  const key=h.join();if(byScope.has(key))continue;
  const S=new Set([...f.S].map(t=>proj(f.h,t,h)));
  if(permutation(S,d.m)){const g={h,S};byScope.set(key,g);out.push(g);}
 }
 return out;
}
function reduce(U,Q,d,certificate=false){
 let current=d,expansions=[],rounds=[];
 const expand=z=>{for(let i=expansions.length-1;i>=0;i--)z=expansions[i](z);return z;};
 for(;;){
  const q=Q.reduce(U,current);expansions.push(q.expand);
  const c=close(q.d,certificate),round={before:current.k,after:q.d.k,quotient:q.rounds,closure:c.stats};
  if(certificate){round.closureInput=q.d;round.log=c.log;}
  rounds.push(round);current=c.d;
  if(c.contradiction){
   // Once certified UNSAT, use a constant genuine contradiction stream.
   // Expansion is deliberately unavailable for this case.
   return {d:{k:1,m:d.m,F:[{h:[0],S:new Set()}]},rounds,contradiction:true,expand:()=>{throw Error("UNSAT has no witness");}};
  }
  const extra=derivedPairs(U,current);round.closure.derived=extra.length;
  if(extra.length)current={...current,F:[...current.F,...extra]};
  if(!current.F.some(f=>f.h.length===2&&permutation(f.S,current.m)))return {d:current,rounds,contradiction:false,expand};
  // Next Q.reduce strictly contracts at least one pair, so at most k rounds.
 }
}
function solve(U,Q,d){
 const r=reduce(U,Q,d);
 if(r.contradiction)return {status:"UNSAT",z:null,used:0n,ceiling:0n,k:r.d.k,rounds:r.rounds,reason:"empty-relation"};
 const s=U.solve(r.d),z=s.z?r.expand(s.z):null;
 if(z&&!d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))throw Error("expanded witness");
 return {...s,z,k:r.d.k,rounds:r.rounds,reason:"enumeration"};
}
function residualBarrier(U,k){
 if(k<6)throw Error("k>=6");const odd="0,1,2";
 return {k,m:2,F:[...U.subsets(Array.from({length:k},(_,i)=>i),3)].map(h=>({h,S:new Set([...U.tuples(2,3)].filter(z=>(z[0]^z[1]^z[2])===+(h.join()===odd)).map(z=>z.join()))}))};
}
module.exports={close,derivedPairs,reduce,solve,residualBarrier};
