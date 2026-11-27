// D6D original-format fixed-partition solver replay.
const U=require('./f038_rex_width_three_component_ir.js'),W=require('./f038_rex_width_three_cost_ir.js'),Gap=require('./f038_rex_width_three_persistent_gap_encoder.js'),Direct=require('./f038_rex_width_three_inplace_hybrid_gac_ir.js'),P=require('./f038_rex_width_three_prefix_order_producer.js'),B=require('./f038_rex_width_three_repair_physical.js'),K=require('./f038_rex_width_three_exit_compiler.js'),Q=require('./f038_rex_width_two_quotient.js'),A=require('./f038_rex_width_three_halt_witness.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),Audit=require('./f038_rex_width_three_component_audit.js');
const mode=process.argv[2]||'bounded',full=mode==='full',fixture=process.argv[3]||'triple-2-sat',ok=(v,s)=>{if(!v)throw Error(s)};
ok(full||mode==='bounded','mode');
const J=U.machine(full),M=B.compose(P,J,K.compile(J),0),N=Q.refine(M);
ok(M.w===4&&N.stats.quotientBits===(full?156103624:156234572)&&N.stats.transitionChecks===(full?8606778:8613618)&&N.q<2**21,'quotient');
const Barrier=require('./f038_rex_width_three_completeness_barrier.js');
const Base=require('./f038_rex_width_three_complete_odometer_audit.js');
const Prior=require('./f038_rex_width_three_prefix_order_audit.js');
const DirectAudit=require('./f038_rex_width_three_direct_extension_audit.js');
const cases=[
 {name:'empty',m:2,B:[]},
 {name:'empty-domain',m:2,B:[[-1],[-2]]},
 {name:'triple-2-sat',m:2,B:DirectAudit.family(E,2,3,false),...(!full?{t:957070224,head:46006,span:46819}:{})},
 {name:'triple-2-unsat',m:2,B:DirectAudit.family(E,2,3,true),...(full?{t:950632628,head:38297,span:46664}:{})},
 {name:'triple-3-sat',m:3,B:DirectAudit.family(E,3,3,false)},
 {name:'cross-sat',m:2,B:[[-1,-3]],...(full?{t:103614892,head:38227,span:46143}:{})}
];
function expected(f){
 const pins=Array(f.m).fill(0),raw=E.encode(f.m,pins,f.B),I=[...Array(19).fill(''),U.stream(E,raw)],ref=Barrier.exact(E,raw),admitted=Audit.admitted(E,raw);
 ok(admitted===(f.name!=='cross-sat'),'admission');
 if(!admitted)ok(ref.count>0,'crossing fixture must be SAT outside class');
 return {raw,I,w:admitted?ref.bits:null,ref,admitted};
}
if(fixture==='descriptor'){
 const C=require('./f038_rex_width_three_compiler.js');
 (async()=>{for(const s of C.descriptorChunks(N))if(!process.stdout.write(s))await require('node:events').once(process.stdout,'drain');})().catch(e=>{console.error(e);process.exitCode=1;});
}else if(fixture==='fixtures'){
 for(const f of cases.filter(f=>f.t!==undefined)){const a=expected(f);console.log([f.name,19*f.m-7,f.t,a.raw,a.w??'-',f.head,f.span].join(' '));}
}else{
 for(const f of cases.filter(f=>fixture==='all'||fixture===f.name)){
  const {raw,I,w,ref,admitted}=expected(f),n=19*f.m-7,r=A.run(M,raw,n,30000000000),q=A.run(N,raw,n,r.t),cut=A.run(N,raw,n,r.t-1),e=Audit.envelope(V,f.m,full);
  ok(r.status==='HALT'&&r.witness===w&&q.status==='HALT'&&q.t===r.t&&q.head===r.head&&q.span===r.span&&q.witness===w&&q.headSymbol===r.headSymbol&&q.nextSymbol===r.nextSymbol&&cut.status==='TIMEOUT'&&cut.t===r.t-1&&cut.witness===null,'physical '+f.name);
  if(f.t!==undefined)ok(r.t===f.t&&r.head===f.head&&r.span===f.span,'exact ledger');
  if(w!==null){const a=F.count(J,I);ok(E.valid(raw,w)&&r.nextSymbol===2&&a.clock===r.clocks.outputAt-r.clocks.workerAt&&BigInt(a.clock)<=e.W&&BigInt(a.N)<=e.N&&BigInt(a.steps)<=e.T,'worker');}else ok(r.headSymbol===2,'blank');
  ok(BigInt(r.t)<=e.total,'total');
  console.log(JSON.stringify({mode,name:f.name,physical:r,admitted,classification:!admitted?'OUTSIDE_CLASS':w===null?'UNSAT':'SAT',solutionCount:ref.count,quotient:N.stats}));
 }
 ok(fixture==='all'||cases.some(f=>f.name===fixture),'fixture');
}
