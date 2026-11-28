// D7I predecessor residual and constant contradiction physical replay.
const assert=require('node:assert/strict');
const req=n=>require('./f038_rex_'+n+'.js');
const [U,Q,R,A,AV,C,V,D,T,H,HV,B,G,N,NV,IV,I,P,K,F,Min]=[
 "variable_rank_reduction","variable_rank_quotient","variable_relational_closure","variable_affine_closure","variable_affine_certificate","variable_resolution_closure","variable_resolution_certificate","variable_adaptive_inference","variable_adaptive_certificate","variable_hall_inference","variable_hall_certificate","variable_conflict_cliques","variable_disjunction_alternatives","variable_polarity_normalization","variable_polarity_certificate","variable_implied_certificate","variable_implied_conflicts","variable_rank_worker","width_three_local_motion_compiler","width_three_local_motion_clock","width_two_quotient"].map(req);
const {split}=req("variable_implied_audit");
const d=split(D.php(U,6)),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);
AV.verify(p.d,a.a);
assert(!p.contradiction);assert.equal(a.a.free.length,189);assert.equal(a.a.rows.length,0);
const r=I.reduce(N,G,B,H,C,V,D,T,HV,NV,a.d);
assert(r.contradiction&&r.cert.kind==="implied-hall"&&IV.verify(NV,HV,a.d,r.cert));
const J=P.machine(),M=P.singleExit(K.compile(J)),N0=Min.refine(M),min={...M,...N0};
const ns=P.stream(U,r.d),b=P.run(M,ns,300000000),c=P.run(min,ns,b.t),cut=P.run(min,ns,b.t-1),clock=F.count(J,["",ns],M.codes);
assert.deepEqual(b,c);assert.equal(b.status,"UNSAT");assert.equal(b.z,null);assert.equal(b.t,clock.clock);assert.equal(b.encoded,clock.encoded);
assert.equal(cut.status,"TIMEOUT");assert.equal(cut.t,b.t-1);assert.equal(cut.z,null);
console.log(JSON.stringify({k:d.k,factors:d.F.length,free:a.a.free.length,equations:a.a.rows.length,paths:r.cert.paths.length,work:r.cert.work,status:b.status,transitions:b.t,stream:ns.length,cutoff:cut.t,states:N0.stats.quotientStates,bits:N0.stats.quotientBits}));
