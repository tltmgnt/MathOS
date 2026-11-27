// D5N original-format replay for each independently compiled run-code mode.
const U=require('./f038_rex_width_three_run_ir.js'),P=require('./f038_rex_width_three_run_producer.js'),B=require('./f038_rex_width_three_repair_physical.js'),K=require('./f038_rex_width_three_exit_compiler.js'),Q=require('./f038_rex_width_two_quotient.js'),A=require('./f038_rex_width_three_halt_witness.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),Audit=require('./f038_rex_width_three_run_audit.js');
const mode=process.argv[2]||'bounded',full=mode==='full',fixture=process.argv[3]||'ternary-chain',ok=(v,s)=>{if(!v)throw Error(s)};
ok(full||mode==='bounded','mode');
const J=U.machine(full),M=B.compose(P,J,K.compile(J),0),N=Q.refine(M);
ok(M.w===4&&N.stats.quotientBits===(full?143724592:143855540)&&N.stats.transitionChecks===(full?7574181:7581021)&&N.q<2**21,'quotient');
const cases=[
 {name:'all-active',m:2,B:[2,3].flatMap(k=>[...E.subsets([0,1,2,3,4,5,6,7,8],k)].map(h=>h.map(g=>-(2*g+2)))),...(full?{t:1248672452,head:51272,span:52301}:{})},
 {name:'ternary-chain',m:2,B:[[-1],[-3],[-2,-4,-5],[-4,-6,-7],[-6,-8,-9]],...(full?{}:{t:369411564,head:45782,span:46811})},
 {name:'reverse-chain-cap',m:2,B:[[-18],...Array.from({length:8},(_,i)=>[-(2*i+2),-(2*(i+1)+1)])]},
 {name:'ternary-empty',m:2,B:[[-1],[-3],[-2,-4,-5],[-2,-4,-6]]},
 {name:'radius-three-refusal',m:2,B:[[-1,-3],[-5,-7],[-9,-11]]},
 {name:'ternary-three-rank',m:3,B:[[-1],[-2],[-4],[-5],[-3,-6,-7],[-3,-6,-8]],}
];
function expected(f){const pins=Array(f.m).fill(0),raw=E.encode(f.m,pins,f.B),I=[...Array(19).fill(''),U.stream(E,raw)],a=require('./f038_rex_width_three_sparse_audit.js').oracle(E,raw,full);return {raw,I,w:a.z?E.witness(f.m,pins,a.z):null,ref:a};}
if(fixture==='descriptor'){
 const C=require('./f038_rex_width_three_compiler.js');
 (async()=>{for(const s of C.descriptorChunks(N))if(!process.stdout.write(s))await require('node:events').once(process.stdout,'drain');})().catch(e=>{console.error(e);process.exitCode=1;});
}else if(fixture==='fixtures'){
 for(const f of cases.filter(f=>f.t!==undefined)){const a=expected(f);console.log([f.name,19*f.m-7,f.t,a.raw,a.w??'-',f.head,f.span].join(' '));}
}else{
 for(const f of cases.filter(f=>fixture==='all'||fixture===f.name)){
  const {raw,I,w,ref}=expected(f),n=19*f.m-7,r=A.run(M,raw,n,30000000000),q=A.run(N,raw,n,r.t),cut=A.run(N,raw,n,r.t-1),e=Audit.envelope(V,f.m,full);
  ok(r.status==='HALT'&&r.witness===w&&q.status==='HALT'&&q.t===r.t&&q.head===r.head&&q.span===r.span&&q.witness===w&&q.headSymbol===r.headSymbol&&q.nextSymbol===r.nextSymbol&&cut.status==='TIMEOUT'&&cut.t===r.t-1&&cut.witness===null,'physical '+f.name);
  if(f.t!==undefined)ok(r.t===f.t&&r.head===f.head&&r.span===f.span,'exact ledger');
  if(w!==null){const a=F.count(J,I);ok(E.valid(raw,w)&&r.nextSymbol===2&&a.clock===r.clocks.outputAt-r.clocks.workerAt&&BigInt(a.clock)<=e.W&&BigInt(a.N)<=e.N&&BigInt(a.steps)<=e.T,'worker');}else ok(r.headSymbol===2,'blank');
  ok(BigInt(r.t)<=e.total,'total');
  console.log(JSON.stringify({mode,name:f.name,physical:r,rounds:ref.rounds,stable:ref.stable,quotient:N.stats}));
 }
 ok(fixture==='all'||cases.some(f=>f.name===fixture),'fixture');
}
