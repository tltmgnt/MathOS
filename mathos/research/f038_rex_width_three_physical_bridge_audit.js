// REX-024D4A: exact bridge and in-place worker differential audit.
function audit(B,P,W,F,R,C,V,K,L,E,suite,replay=true){
 const J=V.compact(W.machine(F,R,C,V)),worker=suite==="bridge"?null:K.compile(J),M=B.compose(P,J,worker),G=L.compile(),D={...L.decode(G.desc),loaderEntry:G.loaderEntry,plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry},ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 function decode(word){const inv=Object.fromEntries(Object.entries(M.codes).map(([s,c])=>[c,s])),out=[],heads=[];let buf="",head=null,cell=0;
  ok(word.slice(0,M.w)===M.codes.G,"global sentinel");
  for(let i=M.w;i<word.length;i+=M.w){let x=inv[word.slice(i,i+M.w)];
   if(x==="D"||x==="E"){ok(head!==null,"head marker");out.push(buf.replace(/_+$/,""));heads.push(head);buf="";head=null;cell=0;if(x==="E"){ok(i+M.w===word.length,"end boundary");break;}continue;}
   ok(x&&/^[uh]/.test(x),"symbol");if(x[0]==="h"){ok(head===null,"one head");head=cell;}
   if(cell===0)ok(x.slice(1)==="L","sentinel");else buf+=x.slice(1);cell++;
  }ok(out.length===J.tapes,"tape count");return{out,heads};
 }
 function check(name,m,pins,clauses,accepted=true,want=true){
  let raw=E.encode(m,pins,clauses),p=L.run(D,raw,5000000000,null,true),r=B.run(M,raw,10000000000);
  if(!accepted){ok(r.status==="REFUSAL"&&r.t===p.t&&r.bridgeClock===null,"refusal");rows.push({name,m,producer:p.t,t:r.t,status:r.status});return{raw,r};}
  ok(p.status==="MASK_STREAM_LOADED"&&r.status==="COMPLETE"&&r.bridgeClock===p.t,"producer clock");
  const h=p.snapshot.indexOf("H"),suffix=p.snapshot.slice(h,h+851).replaceAll("_","b"),stream=p.stream,source=p.snapshot.slice(0,h+851+stream.length);
  ok(r.source.replace(/^_+/,"")===source.replace(/^_+/,""),"preserved literal checkpoint "+name);
  const I=[...Array(19).fill(""),suffix,stream,...Array(40).fill("")],expected=K.encode(M,J,I);
  let witness=null,decision=null;
  if(!worker)ok(r.encoded===expected,"exact physical initialization");
  else{
   const a=decode(r.encoded);
   ok(a.out[19]===suffix&&a.out[20]===stream,"input preservation");
   // Independently execute the exact worker on host-encoded initial
   // tapes only as a differential oracle; not part of composed execution.
   if(replay){const v=K.run(worker,expected,10000000000);
   ok(v.status==="COMPLETE"&&v.t===r.t-r.workerClock&&v.tapes.join("|")===a.out.join("|")&&v.heads.join()===a.heads.join(),"worker exact replay");}
   const clocks={"empty":672161844,"nonempty-child-edge":1144561610,"empty-child-edge":512737138};
   ok(r.t-r.workerClock===clocks[name],"prior exact standalone clock");
   decision=a.out[44];ok(decision===String(+want),"decision");
   if(want){witness=a.out[57];ok(witness.length===19*m-7&&E.valid(raw,witness)&&a.heads[57]===1,"witness");}else ok(a.out[57]==="","no witness");
  }
  rows.push({name,m,producer:p.t,t:r.t,bridge:r.workerClock-r.bridgeClock,worker:r.t-r.workerClock,span:r.span,initialBits:expected.length,head:r.head,decision,witness,status:r.status});return{raw,r};
 }
 const triples=[[-1,-3,-5],[-2,-4,-7],[-1,-6,-8],[-3,-5,-7],[-2],[-1,-4]];
 if(suite==="bridge"){
  let a=check("empty",2,[1,0],[]);
  check("triples",2,[1,0],triples);
  check("K5-refusal",2,[1,1],[...E.subsets([0,1,2,3,4],2)].map(h=>h.map(v=>-(2*v+1))),false);
  const cutoffs=[0,1,100,a.r.bridgeClock-1,a.r.bridgeClock,a.r.t-1];
  for(let t of cutoffs){let r=B.run(M,a.raw,t);ok(r.status==="TIMEOUT"&&r.t===t&&!r.encoded,"cutoff");}
  ok(B.run(M,a.raw,a.r.t).encoded===a.r.encoded,"exact budget");
  return{suite,q:M.q,bridgeStates:M.bridgeStates,producerStates:M.producerStates,rows,cutoffs};
 }
 if(suite==="empty")check("empty",2,[0,0],[]);
 else if(suite==="sat")check("nonempty-child-edge",2,[0,1],[[-1,-3]]);
 else if(suite==="unsat")check("empty-child-edge",2,[1,0],[[-1],[-2],[-1,-3]],true,false);
 else throw Error("suite");
 return{suite,q:M.q,bridgeStates:M.bridgeStates,producerStates:M.producerStates,workerStates:M.workerStates,replay,rows};
}
module.exports={audit};
if(require.main===module){const B=require('./f038_rex_width_three_physical_bridge.js'),P=require('./f038_rex_width_three_bridge_producer.js'),W=require('./f038_rex_width_three_witness_ir.js'),F=require('./f038_rex_width_three_forest_ir.js'),R=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),V=require('./f038_rex_width_three_projection.js'),K={...require('./f038_rex_width_three_compiler.js'),...require('./f038_rex_width_three_row_compiler.js')},L=require('./f038_rex_width_three_direct_loader.js'),E=require('./f038_tga_normalized_integration.js').engine();console.log('F038_REX_WIDTH_THREE_PHYSICAL_BRIDGE_OK '+JSON.stringify(audit(B,P,W,F,R,C,V,K,L,E,process.argv[2]||'bridge')));}
