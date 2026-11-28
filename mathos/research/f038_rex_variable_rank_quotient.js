// D6Z: exact permutation-factor quotient on variable-coordinate CSPs.
function quotient(U,d){
 const {m,k}=d,edges=Array.from({length:k},()=>[]),stats={permutationFactors:0,cycleChecks:0,cycleDeleted:0,rewrittenRows:0,intersections:0};
 const identity=()=>Array.from({length:m},(_,i)=>i);
 for(const f of d.F)if(f.h.length===2&&f.S.size===m){
  const p=Array(m).fill(-1),q=Array(m).fill(-1);let good=true;
  for(const t of f.S){const [a,b]=t.split(",").map(Number);if(p[a]!==-1||q[b]!==-1){good=false;break;}p[a]=b;q[b]=a;}
  if(!good||p.includes(-1)||q.includes(-1))continue;
  const [a,b]=f.h;edges[a].push([b,p]);edges[b].push([a,q]);stats.permutationFactors++;
 }
 const group=Array(k).fill(-1),maps=Array(k),roots=[],domains=[];
 for(let v=0;v<k;v++)if(group[v]===-1){
  const g=roots.length;roots.push(v);group[v]=g;maps[v]=identity();
  const D=new Set(identity()),queue=[v];domains.push(D);
  for(let i=0;i<queue.length;i++){const a=queue[i];for(const [b,p] of edges[a]){
   const candidate=maps[a].map(x=>p[x]);
   if(group[b]===-1){group[b]=g;maps[b]=candidate;queue.push(b);}
   else{if(group[b]!==g)throw Error("component");for(const r of [...D]){stats.cycleChecks++;if(candidate[r]!==maps[b][r]){D.delete(r);stats.cycleDeleted++;}}}
  }}
 }
 const factors=new Map();
 function add(h,S){const id=h.join();if(factors.has(id)){const prev=factors.get(id);for(const t of [...prev.S])if(!S.has(t))prev.S.delete(t);stats.intersections++;}else factors.set(id,{h,S});}
 for(let g=0;g<roots.length;g++)if(domains[g].size!==m)add([g],new Set([...domains[g]].map(String)));
 for(const f of d.F){
  const h=[...new Set(f.h.map(v=>group[v]))].sort((a,b)=>a-b),S=new Set();
  for(const z of U.tuples(m,h.length)){
   stats.rewrittenRows++;if(f.S.has(f.h.map(v=>maps[v][z[h.indexOf(group[v])]]).join()))S.add(z.join());
  }
  if(S.size!==m**h.length)add(h,S);
 }
 return {d:{k:roots.length,m,F:[...factors.values()]},roots,group,maps,stats,expand:z=>group.map((g,v)=>maps[v][z[g]])};
}
function solve(U,d){
 let current=d,rounds=[],maps=[];
 for(;;){
  const q=quotient(U,current);rounds.push({before:current.k,after:q.d.k,...q.stats});maps.push(q.expand);current=q.d;
  if(q.d.F.some(f=>f.S.size===0))return {status:"UNSAT",z:null,used:0n,ceiling:0n,k:current.k,rounds,reason:"empty-relation"};
  if(rounds.at(-1).before===current.k)break;
 }
 const r=U.solve(current);let z=r.z;
 if(z){for(const expand of maps.reverse())z=expand(z);if(!d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))throw Error("expanded witness");}
 return {...r,z,k:current.k,rounds,reason:"enumeration"};
}
module.exports={quotient,solve};
