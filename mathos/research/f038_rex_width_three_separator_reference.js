// D6F host-only separator reference. Not a physical controller or admission rule.
function residual(d,vertices,S){
 const rem=vertices.filter(v=>!S.includes(v)),adj=new Map(rem.map(v=>[v,new Set()]));
 for(const f of d.F){const h=f.h.filter(v=>adj.has(v));for(const a of h)for(const b of h)if(a!==b)adj.get(a).add(b);}
 const out=[],seen=new Set();for(const v of rem)if(!seen.has(v)){const c=[v];seen.add(v);for(let i=0;i<c.length;i++)for(const a of adj.get(c[i]))if(!seen.has(a)){seen.add(a);c.push(a);}out.push(c.sort((a,b)=>a-b));}return out;
}
function plan(d,c){
 const m=BigInt(d.m),base=m**BigInt(c.length);
 let best={S:[],blocks:[c],bound:base,baseline:base};
 for(let mask=1;mask<(1<<c.length);mask++){
  const S=c.filter((_,i)=>mask>>i&1);if(S.length>2)continue;
  const blocks=residual(d,c,S);if(blocks.length<2)continue;
  const bound=m**BigInt(S.length)*(1n+blocks.reduce((n,b)=>n+m**BigInt(b.length),0n));
  if(bound<best.bound)best={S,blocks,bound,baseline:base};
 }
 return best;
}
function solve(E,raw){
 const d=E.decode(raw);if(!d)return {status:"OUTSIDE_NORMALIZED"};
 const z=Array(9).fill(0),plans=[],stats={separatorAssignments:0,localCandidates:0,checks:0};let bound=0n;
 const cs=residual(d,Array.from({length:9},(_,i)=>i),[]);
 const lexLess=(a,b)=>{if(!b)return true;for(let i=0;i<a.length;i++){if(a[i]!==b[i])return a[i]<b[i];}return false;};
 let ceiling=0n;for(const c of cs)ceiling+=plan(d,c).bound;
 for(const c of cs){
  const p=plan(d,c),fs=d.F.filter(f=>c.includes(f.h[0])),pass=f=>f.S.has(f.h.map(v=>z[v]).join());
  plans.push({component:c,S:p.S,blocks:p.blocks,bound:String(p.bound),baseline:String(p.baseline)});
  let best=null,used=0n;
  if(!p.S.length){
   for(const q of E.tup(d.m,c.length)){c.forEach((v,i)=>z[v]=q[i]);stats.localCandidates++;used++;if(fs.every(pass)){best=q;break;}}
  }else{
   const sepOnly=fs.filter(f=>f.h.every(v=>p.S.includes(v)));
   const local=p.blocks.map(b=>fs.filter(f=>f.h.some(v=>b.includes(v))));
   for(const a of E.tup(d.m,p.S.length)){
    stats.separatorAssignments++;used++;p.S.forEach((v,i)=>z[v]=a[i]);
    if(!sepOnly.every(pass))continue;
    let good=true;
    for(let j=0;j<p.blocks.length;j++){
     const b=p.blocks[j];let found=false;
     for(const q of E.tup(d.m,b.length)){b.forEach((v,i)=>z[v]=q[i]);stats.localCandidates++;used++;if(local[j].every(pass)){found=true;break;}}
     if(!found){good=false;break;}
    }
    if(good){const cand=c.map(v=>z[v]);if(lexLess(cand,best))best=cand;}
   }
  }
  if(used>p.bound)throw Error("candidate ceiling");bound+=used;
  if(!best)return {status:"UNSAT",bits:null,plans,stats,used:String(bound),ceiling:String(ceiling)};
  c.forEach((v,i)=>z[v]=best[i]);
 }
 const bits=E.witness(d.m,d.pins,z);if(!E.valid(raw,bits))throw Error("original witness");
 return {status:"SAT",bits,z,plans,stats,used:String(bound),ceiling:String(ceiling)};
}
function audit(E,Barrier,Direct,Fixtures){
 const fs=Fixtures.fixtures(E,Direct);
 const trap=[];for(let g=0;g<8;g++)for(const [a,b] of [[0,0],[1,1]])trap.push([-(2*g+a+1),-(16+b+1)]);
 fs.push({name:"lex-trap",m:2,B:trap});
 for(const m of [2,3]){const B=[];for(let g=2;g<9;g++)for(const [a,b,c] of E.tup(m,3))if(c!==(a+b)%m)B.push([-(a+1),-(m+b+1),-(g*m+c+1)]);fs.push({name:"two-center-"+m,m,B});}
 let sat=0,unsat=0,selected=0,one=0,two=0,assignments=0,candidates=0;const rows=[];
 for(const f of fs){const raw=E.encode(f.m,Array(f.m).fill(0),f.B),ref=Barrier.exact(E,raw),r=solve(E,raw);
  if(r.status!==ref.status||r.bits!==ref.bits||BigInt(r.used)>BigInt(r.ceiling))throw Error("separator oracle "+f.name);
  if(r.status==="SAT")sat++;else unsat++;
  for(const p of r.plans){if(p.S.length){selected++;if(p.S.length===1)one++;else two++;}}
  assignments+=r.stats.separatorAssignments;candidates+=r.stats.localCandidates;
  if(f.name==="lex-trap"||f.name.startsWith("two-center")||f.name.startsWith("family-1-")||f.name.startsWith("family-2-"))rows.push({name:f.name,status:r.status,z:r.z??null,plans:r.plans,used:r.used,ceiling:r.ceiling});
 }
 const t=rows.find(x=>x.name==="lex-trap");if(t.z[0]!==0||t.z[8]!==1||t.plans[0].S.join()!=="8")throw Error("lex trap");
 return {cases:fs.length,sat,unsat,selected,one,two,assignments,candidates,rows};
}
module.exports={residual,plan,solve,audit};
if(require.main===module){const p="./f038_rex_width_three_";console.log(JSON.stringify(audit(require("./f038_tga_normalized_integration.js").engine(),require(p+"completeness_barrier.js"),require(p+"direct_extension_audit.js"),require(p+"auto_component_audit.js"))));}
