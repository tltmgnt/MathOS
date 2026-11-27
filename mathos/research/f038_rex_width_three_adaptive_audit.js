// D5H adaptive physical regression and exact quotient cutoff.
function physical(U,V,E,K,P,B,Q,A,F){
 const J=U.machine(true),M=B.compose(P,J,K.compile(J)),N=Q.refine(M),ok=(x,s)=>{if(!x)throw Error(s)},m=2,pins=[0,0],rows=[];
 ok(N.stats.quotientBits===124697764&&N.stats.transitionChecks===6733134,"quotient");
 for(const [name,clauses,z] of [["empty",[],Array(9).fill(0)],["partial",[[-1],[-4],[-2,-4]], [1,0,0,0,0,0,0,0,0]],["conflict",[[-1],[-4],[-2,-3]],null]]){
  const raw=E.encode(m,pins,clauses),n=31,expected=z?E.witness(m,pins,z):null,I=[...Array(15).fill(""),U.stream(E,raw)],r=A.run(M,raw,n,1000000000),q=A.run(N,raw,n,r.t),cut=A.run(N,raw,n,r.t-1),e=V.envelope(m,124697764n);
  ok(r.status==="HALT"&&r.witness===expected&&q.status==="HALT"&&q.t===r.t&&q.head===r.head&&q.span===r.span&&q.witness===r.witness&&q.headSymbol===r.headSymbol&&q.nextSymbol===r.nextSymbol&&cut.status==="TIMEOUT"&&cut.t===r.t-1&&cut.witness===null,"replay "+name);
  if(z){ok(E.valid(raw,r.witness)&&r.nextSymbol===2,"witness");const p=r.clocks.bridgeAt,i=r.clocks.workerAt-p,w=r.clocks.outputAt-r.clocks.workerAt,o=r.t-r.clocks.outputAt;ok(w===F.count(J,I).clock&&BigInt(p)<=e.P&&BigInt(i)<=e.I&&BigInt(w)<=e.W&&BigInt(o)<=e.O,"phase");}else ok(r.headSymbol===2,"refusal");
  ok(BigInt(r.t)<=e.total,"total");rows.push({name,...r});
 }
 return {stats:N.stats,rows};
}
module.exports={physical};
if(require.main===module){const U=require('./f038_rex_width_three_adaptive_ir.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),E=require('./f038_tga_normalized_integration.js').engine(),K=require('./f038_rex_width_three_exit_compiler.js'),P=require('./f038_rex_width_three_bridge_producer.js'),B=require('./f038_rex_width_three_singleton_physical.js'),Q=require('./f038_rex_width_two_quotient.js'),A=require('./f038_rex_width_three_halt_witness.js'),F=require('./f038_rex_width_three_fast_clock.js');console.log(JSON.stringify(physical(U,V,E,K,P,B,Q,A,F)));}
