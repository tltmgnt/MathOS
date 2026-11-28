// D6Y independent source-CNF, original pool, witness and separator audit.
function audit(U,E){
 const ok=(v,s)=>{if(!v)throw Error(s)},stats={formulas:0,sat:0,unsat:0,sourceAssignments:0,rawWitnessChecks:0,rawExtensionChecks:0,uniqueExtensions:0,separatorChecks:0,gacModelChecks:0,legacyChecks:0,malformed:0},rows=[];
 // Independent tuple counter based on numeric indices (small audit sizes).
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const truth=(C,z)=>C.every(c=>c.some(x=>z[Math.abs(x)-1]===(x>0?1:0)));
 function selected(raw,n){let i=n+1;const C=[];for(const c of E.pool(n)){if(raw[i++]==="1")C.push(c);}ok(i===raw.length,"pool length");return C;}
 function check(k,C,allExtensions=false){
  const R=U.lift(k,C),d=U.decode(k,2,R.raw),n=3*k+4;ok(d&&d.n===n&&d.pins.join()==="0,0"&&BigInt(R.raw.length)===U.length(n),"decode");
  const rawC=selected(R.raw,n),G=U.gac(d),models=new Map();let first=null;
  for(const z of tup(2,k)){
   const expected=truth(C,z),w=U.witness(k,2,[0,0],z),actual=truth(rawC,w.split("").map(Number));
   ok(expected===actual&&expected===d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())),"source/raw/table");ok(U.project(k,w).join()===z.join(),"projection");
   stats.sourceAssignments++;stats.rawWitnessChecks++;
   if(expected){models.set(w,1);if(!first)first=z;ok(z.every((a,i)=>G.D[i].has(a)),"GAC preserves model");stats.gacModelChecks++;}
  }
  if(allExtensions){let count=0;for(const z of tup(2,n)){stats.rawExtensionChecks++;if(truth(rawC,z)){ok(models.has(z.join("")),"unexpected raw extension");count++;}}ok(count===models.size,"unique extension");stats.uniqueExtensions++;}
  const s=U.solve(d);ok(s.status===(first?"SAT":"UNSAT")&&JSON.stringify(s.z)===JSON.stringify(first)&&s.used<=s.ceiling,"separator oracle");stats.separatorChecks++;
  stats.formulas++;stats[first?"sat":"unsat"]++;
 }
 const c2=[[1],[-1],[2],[-2],[1,2],[1,-2],[-1,2],[-1,-2]];
 for(let i=0;i<256;i++)check(2,c2.filter((_,j)=>i>>j&1),i%16===0);
 const c3=[...tup(2,3)].map(z=>z.map((a,i)=>a?i+1:-i-1));
 for(let i=0;i<256;i++)check(3,c3.filter((_,j)=>i>>j&1),i%64===0);
 for(const C of [[],[[]],[[1]],[[1,1]],[[1,-1]],[[1],[-1]],[[1,1,-1]]])check(1,C,true);
 let seed=0xD6F00D;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<80;i++){const k=1+i%7,C=[];for(let j=0;j<1+i%19;j++){const c=[];for(let t=0;t<1+rand()%3;t++){const v=1+rand()%k;c.push(rand()>>>31?v:-v);}C.push(c);}check(k,C);}
 // Exact k=9 backwards compatibility, including the original raw witness.
 for(const m of [2,3,4]){const pins=Array.from({length:m},(_,i)=>i%2),B=[[-1],[-m,-(m+1)],[-1,-(2*m+1),-(8*m+1)]],raw=U.encode(9,m,pins,B),a=U.decode(9,m,raw),b=E.decode(raw);
  ok(raw===E.encode(m,pins,B)&&a.pins.join()===b.pins.join(),"legacy raw");
  const sig=d=>d.F.map(f=>f.h.join()+":"+[...f.S].sort().join(";")).sort().join("|");ok(sig(a)===sig(b),"legacy masks");
  for(const z of [Array(9).fill(0),Array(9).fill(m-1),Array.from({length:9},(_,i)=>i%m)]){ok(U.witness(9,m,pins,z)===E.witness(m,pins,z),"legacy witness");stats.legacyChecks++;}
 }
 // Rejection paths, checked independently from pool coordinates.
 {const k=3,m=2,n=U.dims(k,m),raw=U.encode(k,m,[0,0],[]),C=[...E.pool(n)];
  const edit=(c,b)=>{const i=C.findIndex(x=>x.join()===c.join());ok(i>=0,"edit index");return raw.slice(0,n+1+i)+b+raw.slice(n+2+i);};
  for(const s of ["0"+raw.slice(1),raw.slice(0,-1),raw+"0",edit([-1,-2],"0"),edit([1],"1"),edit([-(n-3),-(n-1),-n],"0")]){ok(U.decode(k,m,s)===null,"malformed");stats.malformed++;}
 }
 function structural(name,k,m,B){
  const raw=U.encode(k,m,Array(m).fill(0),B),d=U.decode(k,m,raw),G=U.gac(d),s=U.solve(d);let first=null,count=0;
  // Independent rank oracle evaluates forbidden optional tuples directly.
  for(const z of tup(m,k))if(B.every(c=>!c.every(x=>z[Math.floor((-x-1)/m)]===(-x-1)%m))){if(!first)first=z;count++;ok(z.every((a,i)=>G.D[i].has(a)),"structural GAC");}
  ok(JSON.stringify(first)===JSON.stringify(s.z)&&s.status===(first?"SAT":"UNSAT")&&s.used<=s.ceiling,"structural oracle");
  const r={name,k,m,raw:raw.length,models:count,status:s.status,z:s.z,gacPasses:G.passes,deletions:G.deletions,used:String(s.used),ceiling:String(s.ceiling),separators:s.plans.map(p=>p.S),blocks:s.plans.map(p=>p.blocks.map(b=>b.length)),trials:s.plans.reduce((n,p)=>n+p.trials,0)};rows.push(r);return r;
 }
 for(const k of [4,6,8,10,12,16]){
  const r=structural("dense-equality-barrier",k,2,U.denseBarrier(k,2));ok(!r.models&&!r.deletions&&r.gacPasses===1&&r.separators[0].length===0&&BigInt(r.used)===2n**BigInt(k),"dense barrier");
 }
 for(const m of [2,3]){const k=8,B=[];for(let g=0;g<k-1;g++)for(let a=0;a<m;a++)for(let b=0;b<m;b++)if(a===b)B.push([-(g*m+a+1),-((k-1)*m+b+1)]);
  const r=structural("late-center-lex",k,m,B);ok(r.separators[0].join()==="7"&&r.z.join()===Array(k-1).fill(0).concat(1).join(),"late lex");
 }
 {const k=10,m=2,B=[];for(let g=2;g<k;g++)for(const [a,b,c] of tup(m,3))if(c!==(a+b)%m)B.push([-(a+1),-(m+b+1),-(g*m+c+1)]);
  const r=structural("two-center-parity",k,m,B);ok(r.separators[0].join()==="0,1"&&r.models===4,"two center");
 }
 return {...stats,structuralCases:rows.length,rows};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require("./f038_rex_variable_rank_reduction.js"),require("./f038_tga_normalized_integration.js").engine())));
