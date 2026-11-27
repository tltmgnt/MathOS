// D5G: exact physical replay and original-format quotient audit.
const U=require('./f038_rex_width_three_singleton_ir.js'),B=require('./f038_rex_width_three_singleton_physical.js'),P=require('./f038_rex_width_three_bridge_producer.js'),K=require('./f038_rex_width_three_exit_compiler.js'),Q=require('./f038_rex_width_two_quotient.js'),A=require('./f038_rex_width_three_halt_witness.js'),F=require('./f038_rex_width_three_fast_clock.js'),Ad=require('./f038_rex_width_three_admission.js'),E=require('./f038_tga_normalized_integration.js').engine();
const ok=(x,msg)=>{if(!x)throw Error(msg)},J=U.machine(),M=B.compose(P,J,K.compile(J)),N=Q.refine(M);
const z=Array.from({length:9},(_,i)=>i%2),pins=[0,1],clauses=z.map((a,g)=>[-(2*g+2-a)]),raw=E.encode(2,pins,clauses);
const cases=[{name:'m2-forced',n:31,raw,witness:E.witness(2,pins,z),expected:289549660},...Ad.fixtures(E,'all').map(f=>({...f,expected:f.name==='m3-forced'?2152510163:null,witness:f.name.endsWith('-forced')?f.witness:null}))];
const mode=process.argv[2]||'m2-forced';
if(mode==='descriptor'){
 const {descriptorChunks}=require('./f038_rex_width_three_compiler.js');
 (async()=>{for(const chunk of descriptorChunks(N))if(!process.stdout.write(chunk))await require('node:events').once(process.stdout,'drain');})().catch(e=>{console.error(e);process.exitCode=1;});
}else{
 ok(N.stats.quotientBits===124696396&&N.stats.transitionChecks===6643845,'quotient regression');
 for(const f of cases.filter(f=>mode==='all'||mode===f.name)){
  const input=[...Array(15).fill(''),U.stream(E,f.raw)],ir=U.executeIR(J,input);
  ok((ir.status==='halt')===(f.witness!==null),'IR status '+f.name);
  if(f.witness!==null)ok(ir.tapes[0]===f.witness&&E.valid(f.raw,ir.tapes[0]),'IR witness');
  const r=A.run(M,f.raw,f.n,25000000000);
  ok(r.status==='HALT'&&r.witness===f.witness,'physical result '+f.name+JSON.stringify(r));
  if(f.expected!==null)ok(r.t===f.expected,'exact clock');
  if(f.witness!==null){
   ok(E.valid(f.raw,r.witness)&&r.nextSymbol===2,'raw witness');
   ok(r.clocks.outputAt-r.clocks.workerAt===F.count(J,input).clock,'physical worker clock');
  }else ok(r.headSymbol===2,'blank refusal');
  const q=A.run(N,f.raw,f.n,r.t),cut=A.run(N,f.raw,f.n,r.t-1);
  ok(q.status==='HALT'&&q.t===r.t&&q.head===r.head&&q.span===r.span&&q.witness===r.witness&&q.headSymbol===r.headSymbol&&q.nextSymbol===r.nextSymbol,'quotient replay');
  ok(cut.status==='TIMEOUT'&&cut.t===r.t-1&&cut.witness===null,'one-short cutoff');
  console.log(JSON.stringify({name:f.name,physical:r,quotient:N.stats,slot:f.witness===null?null:Ad.slot(f.n,N.stats.quotientBits,r.t)}));
 }
 ok(mode==='all'||cases.some(f=>f.name===mode),'unknown fixture');
}
