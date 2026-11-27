// D5I exact original-format replay and conservative ten-attempt envelope.
const U=require('./f038_rex_width_three_repair_ir.js'),P=require('./f038_rex_width_three_repair_producer.js'),B=require('./f038_rex_width_three_repair_physical.js'),K=require('./f038_rex_width_three_exit_compiler.js'),Q=require('./f038_rex_width_two_quotient.js'),A=require('./f038_rex_width_three_halt_witness.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),Ad=require('./f038_rex_width_three_admission.js');
const J=U.machine(),M=B.compose(P,J,K.compile(J),0),N=Q.refine(M),ok=(v,s)=>{if(!v)throw Error(s)};
ok(N.stats.quotientBits===122349668&&N.stats.transitionChecks===7214703,'quotient');
const f3=Ad.fixtures(E,'m3-forced')[0],f4=Ad.fixtures(E,'m4-forced')[0];
const cases=[{name:'empty',m:2,pins:[0,0],B:[],t:288362787,head:52347,span:53376},{name:'repair',m:2,pins:[0,0],B:[[-1],[-2,-3]],t:292851589,head:52347,span:53376},{name:'K5-safe',m:2,pins:[0,0],B:[...E.subsets([0,1,2,3,4],2)].map(h=>h.map(g=>-(2*g+2))),t:288362787,head:52347,span:53376},{...Ad.fixtures(E,'K5-refusal')[0],t:191269332,head:39851,span:53184},{...f3,t:2142202580,head:197888,span:200703},{...f4,t:null,head:null,span:null}];
const mode=process.argv[2]||'repair';
function expected(f){const raw=E.encode(f.m,f.pins,f.B),I=[...Array(16).fill(''),U.stream(E,raw)],a=U.executeIR(J,I);return {raw,I,w:a.status==='halt'?a.tapes[0]:null};}
function bound(m){
 const e=V.envelope(m),S=e.S,N=S+32n*BigInt(m)+499n,T=1400n*S,W=(26n*N+16n)*T+8n;
 ok(N<=2n*S&&W<=131072n*S*S,'worker bound');
 const total=e.P+128n*S*S+W+256n*S*S;
 ok(total<=65536n*e.L*e.L,'quadratic');return {N,T,W,total,H0:122349684n};
}
if(mode==='descriptor'){
 const C=require('./f038_rex_width_three_compiler.js');
 (async()=>{for(const s of C.descriptorChunks(N))if(!process.stdout.write(s))await require('node:events').once(process.stdout,'drain');})().catch(e=>{console.error(e);process.exitCode=1;});
}else if(mode==='fixtures'){
 for(const f of cases.filter(f=>f.t!==null&&f.m===2)){const a=expected(f);console.log([f.name,19*f.m-7,f.t,a.raw,a.w??'-',f.head,f.span].join(' '));}
}else{
 for(let m=2;m<=10000;m++)bound(m);
 for(const f of cases.filter(f=>mode==='all'||mode===f.name)){
  const {raw,I,w}=expected(f),n=19*f.m-7,r=A.run(M,raw,n,30000000000),q=A.run(N,raw,n,r.t),cut=A.run(N,raw,n,r.t-1),e=bound(f.m);
  ok(r.status==='HALT'&&r.witness===w&&q.status==='HALT'&&q.t===r.t&&q.head===r.head&&q.span===r.span&&q.witness===w&&q.headSymbol===r.headSymbol&&q.nextSymbol===r.nextSymbol&&cut.status==='TIMEOUT'&&cut.t===r.t-1&&cut.witness===null,'physical '+f.name);
  if(f.t!==null)ok(r.t===f.t&&r.head===f.head&&r.span===f.span,'exact ledger');
  if(w!==null){const a=F.count(J,I);ok(E.valid(raw,w)&&r.nextSymbol===2&&a.clock===r.clocks.outputAt-r.clocks.workerAt&&BigInt(a.clock)<=e.W&&BigInt(a.N)<=e.N&&BigInt(a.steps)<=e.T,'worker');}else ok(r.headSymbol===2,'blank');
  ok(BigInt(r.t)<=e.total,'total');
  console.log(JSON.stringify({name:f.name,physical:r,quotient:N.stats,slot:w===null?null:Ad.slot(n,N.stats.quotientBits,r.t)}));
 }
 ok(mode==='all'||cases.some(f=>f.name===mode),'fixture');
}
