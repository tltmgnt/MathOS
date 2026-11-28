// D7G: oracle, alternate chains, beam limit, signed representation obstruction and physical replay.
function audit(U,Q,R,A,AV,C,V,D,T,H,HV,B,G,P,K,F,Min){
 const ok=(b,s)=>{if(!b)throw Error(s);},stats={cases:0,models:0,sat:0,unsat:0,oldHall:0,newHall:0,addedHall:0,localMasks:0,cleanGraphs:0,ambiguousGraphs:0,tamperRejected:0};
 const factor=(h,mask)=>({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((a,b,i)=>a+(b<<i),0))&1).map(z=>z.join()))});
 const excl=h=>({h,S:new Set(["0,0","0,1","1,0"])}),imp=(u,x)=>({h:[u,x],S:new Set(["0,0","0,1","1,1"])});
 const models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join()))).map(z=>z.join());
 function check(d){
  const m=models(d),old=B.robust(H,C,d),h=G.alternative(B,H,C,d);
  stats.cases++;stats.models+=m.length;stats[m.length?"sat":"unsat"]++;
  if(old.kind==="hall"){stats.oldHall++;ok(h.kind==="hall"&&HV.verify(d,old),"baseline");}
  if(h.kind==="hall"){ok(!m.length&&HV.verify(d,h),"soundness");stats.newHall++;if(old.kind!=="hall")stats.addedHall++;}
  return h;
 }
 for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){check({k:n,m:2,F:[factor(Array.from({length:n},(_,i)=>i),mask)]});stats.localMasks++;}
 for(let k of [2,3])for(let mask=0;mask<256;mask++){
  const F=[];
  if(k===2){const scopes=[[0],[0],[1],[1],[0,1],[0,1],[0,1],[0,1]];for(let j=0;j<8;j++)if(mask>>j&1)F.push(factor(scopes[j],((1<<(2**scopes[j].length))-1)^(1<<(j<4?j%2:j-4))));}
  else for(let j=0;j<8;j++)if(mask>>j&1)F.push(factor([0,1,2],255^(1<<j)));
  check({k,m:2,F});
 }
 let seed=0xd7a024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let t=0;t<128;t++){const k=3+t%4,F=[];for(let j=0;j<2+t%11;j++){const h=[...new Set(Array.from({length:1+rand()%3},()=>rand()%k))].sort((a,b)=>a-b);F.push(factor(h,rand()>>>16));}check({k,m:2,F});}
 function graph(E,amb=0){
  let k=0;const opts=E.map(row=>row.map(h=>({h,x:k++}))),F=[];
  for(let i=0;i<opts.length;i++){const h=opts[i].map(a=>a.x);if((amb>>i&1)&&h.length===2){const u=k++;F.push(factor([h[0],u],14),imp(u,h[1]),imp(u,h[0]));}else F.push(factor(h,(1<<(2**h.length))-2));}
  for(let i=0;i<opts.length;i++)for(let j=0;j<i;j++)for(const x of opts[i])for(const y of opts[j])if(x.h===y.h)F.push(excl([y.x,x.x]));
  return {k,m:2,F};
 }
 for(let mask=0;mask<512;mask++){
  const E=Array.from({length:3},(_,i)=>[0,1,2].filter(j=>mask>>(3*i+j)&1));if(E.some(x=>!x.length))continue;
  const d=graph(E),h=check(d);ok((h.kind==="hall")===!models(d).length,"clean graphs");stats.cleanGraphs++;
 }
 const cross=[];for(let i=0;i<6;i++)for(let j=i+1;j<6;j++)if((i>>1)!==(j>>1)&&i%2!==j%2)cross.push([i,j]);
 for(let mask=0;mask<64;mask++)for(let amb=0;amb<8;amb++){
  const d=graph([[0,1],[0,1],[0,1]],amb);for(let i=0;i<6;i++)if(mask>>i&1)d.F.push(excl(cross[i]));
  const h=check(d);ok(h.kind==="hall","ambiguous noisy UNSAT");stats.ambiguousGraphs++;
 }
 for(let amb=0;amb<4;amb++)for(let mask=0;mask<4;mask++){
  const d=graph([[0,1],[0,1]],amb);if(mask&1)d.F.push(excl([0,3]));if(mask&2)d.F.push(excl([1,2]));check(d);stats.ambiguousGraphs++;
 }
 const flip=(d,vars)=>({...d,F:d.F.map(f=>({h:f.h.slice(),S:new Set([...f.S].map(t=>t.split(",").map((x,i)=>vars.has(f.h[i])?1-Number(x):Number(x)).join()))}))});
 const small=graph([[0,1],[0,1],[0,1]],7),negative=check(flip(small,new Set(Array.from({length:small.k},(_,i)=>i))));ok(negative.kind==="hall"&&negative.sign===-1,"negative polarity");
 function fixture(n,type){
  const d=D.php(U,n),base=n*(n+1);
  if(type==="single")d.F.push(imp(base,2));
  if(type==="multi"||type==="mixed-noise")for(let i=0;i<=n;i++)d.F.push(imp(base+i*(n-3),i*n+2));
  if(type==="wide")d.F.push(imp(base,n));
  if(type==="mixed-noise")d.F.push(excl([0,n+1]));
  if(type==="polarity")return flip(d,new Set(Array.from({length:n+1},(_,i)=>i*n)));
  return d;
 }
 const rows=[];
 for(const [n,type] of [[4,"single"],[5,"single"],[6,"single"],[6,"multi"],[6,"mixed-noise"],[6,"wide"],[8,"multi"],[12,"multi"],[20,"multi"]]){
  const d=fixture(n,type),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);
  const old=B.robust(H,C,a.d),h=G.alternative(B,H,C,a.d);
  ok(!p.contradiction&&a.a.rows.length===0&&a.a.free.length===d.k&&old.kind==="unknown"&&h.kind==="hall"&&HV.verify(a.d,h),"large ambiguous");
  rows.push({n,type,k:d.k,factors:d.F.length,groupStrategy:h.groupStrategy,partition:h.strategy,groups:h.groups.length,holes:h.holes.length,proof:h.groups.reduce((s,g)=>s+g.proof.length,0),exclusions:h.exclusions.length,extraction:h.extraction});
 }
 const limited=G.alternative(B,H,C,fixture(6,"wide"),1);ok(limited.extraction.beamDropped>0&&limited.kind==="unknown","beam limit");
 let relabelled=0;
 for(let t=0;t<32;t++){
  const d=fixture(6,"single"),perm=Array.from({length:d.k},(_,i)=>i);
  for(let i=perm.length-1;i>0;i--){const j=rand()%(i+1);[perm[i],perm[j]]=[perm[j],perm[i]];}
  const e={...d,F:d.F.map(f=>({h:f.h.map(x=>perm[x]).reverse(),S:new Set([...f.S].map(s=>s.split(",").reverse().join()))})).reverse()};
  const h=G.alternative(B,H,C,e);ok(h.kind==="hall"&&HV.verify(e,h),"relabel");relabelled++;
 }
 const cert=G.alternative(B,H,C,small);
 function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
 reject(()=>HV.verify(small,{...cert,holes:cert.holes.map((h,i)=>i?h:h.slice(1))}));
 reject(()=>HV.verify(small,{...cert,exclusions:cert.exclusions.slice(1)}));
 reject(()=>HV.verify(small,{...cert,groups:cert.groups.map((g,i)=>i?g:{...g,proof:g.proof.slice(0,-1)})}));
 reject(()=>HV.verify(small,{...cert,groups:cert.groups.map((g,i)=>i?g:{...g,options:[...g.options,999]})}));
 const J=P.machine(),M=P.singleExit(K.compile(J)),N0=Min.refine(M),N={...M,...N0},physical=[];
 const sat=graph([[0,1],[0,1]],1);
 for(const [name,d,compare] of [["ambiguous-small",small,true],["ambiguous-sat",sat,true],["PHP6-single",fixture(6,"single"),false],["PHP20-multi",fixture(20,"multi"),false]]){
  const p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=G.reduce(B,H,C,V,D,T,HV,a.d,2000000);
  const ns=P.stream(U,r.d),b=P.run(M,ns,300000000),c=P.run(N,ns,b.t),cut=P.run(N,ns,b.t-1),clock=F.count(J,["",ns],M.codes);
  ok(JSON.stringify(b)===JSON.stringify(c)&&b.t===clock.clock&&b.encoded===clock.encoded&&cut.status==="TIMEOUT"&&cut.t===b.t-1&&cut.z===null,"physical");
  const row={name,status:b.status,kind:r.cert.kind,newPhysical:b.t,stream:ns.length};
  if(compare){const os=P.stream(U,a.d),old=P.run(N,os,300000000),oc=F.count(J,["",os],M.codes),m=models(d),x=old.z?p.expand(a.expand(old.z)):null,y=b.z?p.expand(a.expand(r.expand(b.z))):null;
   ok(old.status===b.status&&b.status===(m.length?"SAT":"UNSAT")&&(x?.join()??null)===(m[0]??null)&&(y?.join()??null)===(m[0]??null)&&old.t===oc.clock&&old.encoded===oc.encoded,"physical compare");row.oldPhysical=old.t;}
  else ok(b.status==="UNSAT"&&b.z===null&&r.cert.kind==="hall","large physical");
  physical.push(row);
 }
 const barrier=fixture(6,"polarity"),p=R.reduce(U,Q,barrier),a=A.reduce(U,p.d);AV.verify(p.d,a.a);
 const r=G.reduce(B,H,C,V,D,T,HV,a.d,2000000);
 ok(!p.contradiction&&p.d.k===63&&a.a.free.length===63&&a.a.rows.length===0&&r.hall.kind==="unknown"&&r.first.reason==="budget"&&r.cert.reason==="budget"&&!r.contradiction&&r.d===a.d,"barrier");
 return {stats,rows,relabelled,limited:{kind:limited.kind,beamDropped:limited.extraction.beamDropped},physical,barrier:{k:barrier.k,factors:barrier.F.length,free:a.a.free.length,equations:a.a.rows.length,hall:r.hall,first:r.first,final:r.cert},resources:{states:N0.stats.quotientStates,bits:N0.stats.quotientBits,clockChecks:6,cutoffs:4}};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_hall_certificate.js'),require('./f038_rex_variable_conflict_cliques.js'),require('./f038_rex_variable_disjunction_alternatives.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'))));
