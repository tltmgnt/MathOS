// Original halt-head semantics and exact phase clock regression.
function audit(A,B,P,W,F,R,C,V,K,Legacy,E,suite){
 const J=V.compact(W.machine(F,R,C,V)),ok=(v,s)=>{if(!v)throw Error(s)};
 if(suite==="projection"){
  const M=B.bridge(J),O=A.projector(M),rows=[];
  for(let word of ["","1","0","1010101010101010101111111110000","00101010000110001000101010001111101111101111110100"]){
   let I=Array(61).fill("");I[57]=word;let raw=Legacy.encode(M,J,I),r=A.run(O,raw,word.length||1);
   ok(r.status==="HALT"&&r.witness===(word||null)&&r.nextSymbol===2&&r.head===raw.length+1,"projection "+word);
   rows.push({word,t:r.t,head:r.head});
   for(let t of [0,1,r.t-1])ok(A.run(O,raw,word.length||1,t).status==="TIMEOUT","projection cutoff");
  }return{suite,q:O.q,rows};
 }
 const M=A.compose(B,P,J,K.compile(J)),rows=[];
 function check(name,raw,n,clock,expected,phases){
  let r=A.run(M,raw,n,2000000000);
  ok(r.status==="HALT"&&r.witness===expected,"halt result "+name+" "+JSON.stringify(r));
  if(clock!==null)ok(r.t===clock,"clock "+name);
  if(expected===null)ok(r.headSymbol===2,"blank head");else ok(r.nextSymbol===2&&E.valid(raw,r.witness),"original verifier");
  if(phases)ok(r.clocks.bridgeAt===phases[0]&&r.clocks.workerAt===phases[1]&&r.clocks.outputAt===phases[2],"prior clocks");
  rows.push({name,...r});return r;
 }
 if(suite==="empty")check("empty",E.encode(2,[0,0],[]),31,825112955,"1010101010101010101111111110000",[104551138,152921385,825083229]);
 else if(suite==="sat")check("nonempty-edge",E.encode(2,[0,1],[[-1,-3]]),31,null,"0110101010101010101111111110100",[104556548,152926795,1297488405]);
 else if(suite==="unsat")check("empty-edge",E.encode(2,[1,0],[[-1],[-2],[-1,-3]]),31,665681141,null,[104556548,152926795,665663933]);
 else if(suite==="refusal"){
  for(let [name,raw,n,clock] of [["empty-raw","",1,236],["small-malformed","1000",1,329],["wrong-domain","1".repeat(32)+"0",32,3157],["K5-refusal",E.encode(2,[1,1],[...E.subsets([0,1,2,3,4],2)].map(h=>h.map(v=>-(2*v+1)))),31,27879501]]){
   let r=check(name,raw,n,clock,null,null);ok(r.clocks.blankAt===clock-1&&r.clocks.bridgeAt===undefined,"refusal bypass");
  }
 }else if(suite==="codec"){
  // Stream the exact original unary header and fixed-width rule fields.
  // Independent chunk parser validates every serialized entry.
  const stream=Legacy.descriptorChunks(M),header=stream.next().value;
  ok(header.startsWith("111")&&header.endsWith("0")&&!header.slice(3,-1).includes("0"),"header");
  let q=header.length-4,b=q.toString(2).length,j=0,bits=header.length;
  for(let chunk of stream){ok(chunk.length%(b+4)===0,"alignment");bits+=chunk.length;
   for(let i=0;i<chunk.length;i+=b+4){
    let s=parseInt(chunk.slice(i,i+b),2),v=parseInt(chunk.slice(i+b,i+b+2),2),d=parseInt(chunk.slice(i+b+2,i+b+4),2);
    ok(s<=q&&v<=2&&d<=2&&M.T[j++]===((s<<4)|(v<<2)|d),"codec entry");
   }
  }ok(q===M.q&&j===3*q&&bits===4+q+3*q*(b+4),"codec size");
  return{suite,q,bits,entries:j};
 }else throw Error("suite");
 return{suite,q:M.q,worker:M.workerStates,output:M.outputStates,bits:4+M.q+3*M.q*(M.q.toString(2).length+4),rows};
}
module.exports={audit};
if(require.main===module){const A=require('./f038_rex_width_three_halt_witness.js'),B=require('./f038_rex_width_three_physical_bridge.js'),P=require('./f038_rex_width_three_bridge_producer.js'),W=require('./f038_rex_width_three_witness_ir.js'),F=require('./f038_rex_width_three_forest_ir.js'),R=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),V=require('./f038_rex_width_three_projection.js'),K=require('./f038_rex_width_three_exit_compiler.js'),Legacy=require('./f038_rex_width_three_compiler.js'),E=require('./f038_tga_normalized_integration.js').engine();console.log('F038_REX_WIDTH_THREE_HALT_WITNESS_OK '+JSON.stringify(audit(A,B,P,W,F,R,C,V,K,Legacy,E,process.argv[2]||'projection')));}
