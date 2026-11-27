// D6E original-format automatic component/fallback solver replay.
const U=require('./f038_rex_width_three_component_fallback_ir.js'),W=require('./f038_rex_width_three_cost_ir.js'),Gap=require('./f038_rex_width_three_persistent_gap_encoder.js'),Direct=require('./f038_rex_width_three_inplace_hybrid_gac_ir.js'),P=require('./f038_rex_width_three_prefix_order_producer.js'),B=require('./f038_rex_width_three_repair_physical.js'),K=require('./f038_rex_width_three_exit_compiler.js'),Q=require('./f038_rex_width_two_quotient.js'),A=require('./f038_rex_width_three_halt_witness.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),Audit=require('./f038_rex_width_three_component_fallback_audit.js');
const mode=process.argv[2]||'bounded',full=mode==='full',fixture=process.argv[3]||'cross-sat',ok=(v,s)=>{if(!v)throw Error(s)};
ok(full||mode==='bounded','mode');
const J=U.machine(full),M=B.compose(P,J,K.compile(J),0),N=Q.refine(M);
ok(M.w===4&&N.stats.quotientBits===(full?173070123:173206240)&&N.stats.transitionChecks===(full?9381096:9387936)&&N.q>=2**21&&N.q<2**22,'quotient');
const Barrier=require('./f038_rex_width_three_completeness_barrier.js');
const Base=require('./f038_rex_width_three_complete_odometer_audit.js');
const Prior=require('./f038_rex_width_three_prefix_order_audit.js');
const DirectAudit=require('./f038_rex_width_three_direct_extension_audit.js');
const Component=require('./f038_rex_width_three_component_audit.js');
const cases=Audit.fixtures(E,Barrier,DirectAudit,Base).map(f=>f.name==='cross-sat'?{...f,t:233530292,head:45652,span:46443}:f.name==='triple-2-sat'&&!full?{...f,t:965915186,head:46010,span:46823}:f.name==='barrier-unsat'&&full?{...f,t:281941536,head:38293,span:46650}:f);
function expected(f){
 const pins=Array(f.m).fill(0),raw=E.encode(f.m,pins,f.B),I=[...Array(19).fill(''),U.stream(E,raw)],ref=Barrier.exact(E,raw),special=Component.admitted(E,raw);
 return {raw,I,w:ref.bits,ref,special};
}
if(fixture==='descriptor'){
 const C=require('./f038_rex_width_three_compiler.js');
 (async()=>{for(const s of C.descriptorChunks(N))if(!process.stdout.write(s))await require('node:events').once(process.stdout,'drain');})().catch(e=>{console.error(e);process.exitCode=1;});
}else if(fixture==='fixtures'){
 for(const f of cases.filter(f=>f.t!==undefined)){const a=expected(f);console.log([f.name,19*f.m-7,f.t,a.raw,a.w??'-',f.head,f.span].join(' '));}
}else{
 for(const f of cases.filter(f=>fixture==='all'||fixture===f.name)){
  const {raw,I,w,ref,special}=expected(f),n=19*f.m-7,r=A.run(M,raw,n,30000000000),q=A.run(N,raw,n,r.t),cut=A.run(N,raw,n,r.t-1),e=Audit.envelope(V,f.m,full,special);
  ok(r.status==='HALT'&&r.witness===w&&q.status==='HALT'&&q.t===r.t&&q.head===r.head&&q.span===r.span&&q.witness===w&&q.headSymbol===r.headSymbol&&q.nextSymbol===r.nextSymbol&&cut.status==='TIMEOUT'&&cut.t===r.t-1&&cut.witness===null,'physical '+f.name);
  if(f.t!==undefined)ok(r.t===f.t&&r.head===f.head&&r.span===f.span,'exact ledger');
  if(w!==null){const a=F.count(J,I);ok(E.valid(raw,w)&&r.nextSymbol===2&&a.clock===r.clocks.outputAt-r.clocks.workerAt&&BigInt(a.clock)<=e.W&&BigInt(a.N)<=e.N&&BigInt(a.steps)<=e.T,'worker');}else ok(r.headSymbol===2,'blank');
  ok(BigInt(r.t)<=e.total,'total');
  console.log(JSON.stringify({mode,name:f.name,physical:r,route:special?'components':'general',classification:w===null?'UNSAT':'SAT',solutionCount:ref.count,quotient:N.stats}));
 }
 ok(fixture==='all'||cases.some(f=>f.name===fixture),'fixture');
}
