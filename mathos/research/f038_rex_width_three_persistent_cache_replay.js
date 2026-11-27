// D6K: original raw-selector lowering and exact quotient/cutoff replay.
const U=require('./f038_rex_width_three_persistent_cache_ir.js'),P=require('./f038_rex_width_three_prefix_order_producer.js'),B=require('./f038_rex_width_three_repair_physical.js'),K=require('./f038_rex_width_three_exit_compiler.js'),Q=require('./f038_rex_width_two_quotient.js'),A=require('./f038_rex_width_three_halt_witness.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),Barrier=require('./f038_rex_width_three_completeness_barrier.js'),Direct=require('./f038_rex_width_three_direct_extension_audit.js');
const mode=process.argv[2]||'bounded',full=mode==='full',fixture=process.argv[3]||'cross-sat',ok=(v,s)=>{if(!v)throw Error(s)};
ok(full||mode==='bounded','mode');
const cases=[
 {name:'empty',m:2,B:[]},
 {name:'empty-domain',m:2,B:[[-1],[-2]]},
 {name:'cross-sat',m:2,B:[[-1,-3]]},
 {name:'two-prefix-unsat',m:2,B:Direct.family(E,2,2,true)},
 {name:'two-prefix-sat',m:2,B:Direct.family(E,2,2,false)},
 {name:'one-prefix-sat',m:2,B:Direct.family(E,2,1,false),...(!full?{t:1968010788,head:47126,span:47941}:{})},
 {name:'one-prefix-unsat',m:2,B:Direct.family(E,2,1,true),...(full?{t:1782816682,head:38293,span:47786}:{})},
 {name:'prefix-pair',m:2,B:[[-1,-3],...Array.from({length:7},(_,i)=>i+2).flatMap(g=>[...E.tup(2,3)].filter(([a,b,c])=>c!==(a+b)%2).map(([a,b,c])=>[-(a+1),-(b+3),-(2*g+c+1)]))]},
 {name:'easy-two-center',m:2,B:Array.from({length:7},(_,i)=>i+2).flatMap(g=>[...E.tup(2,3)].filter(([a,b,c])=>c!==(a+b)%2).map(([a,b,c])=>[-(a+1),-(b+3),-(2*g+c+1)]))},
 {name:'direct-resume',m:2,B:Array.from({length:7},(_,i)=>[-1,-(2*(i+1)+1),-(2*(i+2)+1)])},
 {name:'hard-2-sat',m:2,B:require('./f038_rex_width_three_two_prefix_hard.js').family(E,2,false)},
 {name:'hard-4-sat',m:4,B:require('./f038_rex_width_three_two_prefix_hard.js').family(E,4,false)},
 {name:'hard-3-sat',m:3,B:require('./f038_rex_width_three_two_prefix_hard.js').family(E,3,false)}
];
function expected(f){const raw=E.encode(f.m,Array(f.m).fill(0),f.B),I=[...Array(19).fill(''),U.stream(E,raw)],ref=Barrier.exact(E,raw);return {raw,I,w:ref.bits,ref};}
if(fixture==='fixtures'){
 for(const f of cases.filter(f=>['empty-domain','cross-sat','two-prefix-unsat','two-prefix-sat','prefix-pair','one-prefix-sat','one-prefix-unsat','direct-resume'].includes(f.name))){const a=expected(f);console.log([f.name,19*f.m-7,f.t??30000000000,a.raw,a.w??'-',f.head??'-',f.span??'-'].join(' '));}
}else{
 const J=U.machine(full),M=B.compose(P,J,K.compile(J),0),N=Q.refine(M);
 ok(M.w===4&&M.q===(full?5379480:5381760)&&N.q===(full?3722021:3723744)&&N.stats.quotientBits===(full?294039663:294175780)&&N.stats.transitionChecks===(full?16138440:16145280)&&N.q<2**22,'quotient');
 if(fixture==='descriptor'){
  const C=require('./f038_rex_width_three_compiler.js');
  (async()=>{for(const s of C.descriptorChunks(N))if(!process.stdout.write(s))await require('node:events').once(process.stdout,'drain');})().catch(e=>{console.error(e);process.exitCode=1;});
 }else{
  ok(fixture==='all'||cases.some(f=>f.name===fixture),'fixture');
  for(const f of cases.filter(f=>fixture==='all'||fixture===f.name)){
   const {raw,I,w,ref}=expected(f),n=19*f.m-7,r=A.run(M,raw,n,30000000000),q=A.run(N,raw,n,r.t),cut=A.run(N,raw,n,r.t-1);
   ok(r.status==='HALT'&&r.witness===w&&q.status==='HALT'&&q.t===r.t&&q.head===r.head&&q.span===r.span&&q.witness===w&&q.headSymbol===r.headSymbol&&q.nextSymbol===r.nextSymbol&&cut.status==='TIMEOUT'&&cut.t===r.t-1&&cut.witness===null,'physical '+f.name);
   if(f.t!==undefined)ok(r.t===f.t&&r.head===f.head&&r.span===f.span,'exact ledger');
   if(w!==null){const a=F.count(J,I);ok(E.valid(raw,w)&&r.nextSymbol===2&&a.clock===r.clocks.outputAt-r.clocks.workerAt,'worker');}else ok(r.headSymbol===2,'blank');
   console.log(JSON.stringify({mode,name:f.name,physical:r,classification:ref.status,solutionCount:ref.count,quotient:N.stats}));
  }
 }
}
