// REX-024D5A: exact whole-machine quotient, original descriptor streaming and stage ledger.
function slot(n,ell,t){
 const N=BigInt(n),L=N+1n+2n*N*N+8n*N*(N-1n)*(N-2n)/6n;
 const log=x=>(x-1n).toString(2).length; // inputs strictly greater than one
 const b=log(L),s3=3*b,c=t===null?null:t===1?0:log(BigInt(t)),s=c===null?null:ell+c;
 return{n,L:Number(L),b,s3,ell,clock:t,slot:s,minK:s===null?null:Math.ceil(s/b),listedAt3:ell<=s3,builtinSlot:n+3,builtinAt3:n+3<=s3};
}
function build(A,B,P,W,F,R,C,V,K,Q){
 const J=V.compact(W.machine(F,R,C,V)),M=A.compose(B,P,J,K.compile(J)),N=Q.refine(M);
 return{q:N.q,T:N.T,stats:N.stats};
}
function fixtures(E,suite){
 const a=[
  {name:"empty",m:2,pins:[0,0],B:[],clock:825112955,head:57932,span:58961,witness:"1010101010101010101111111110000"},
  {name:"edge-SAT",m:2,pins:[0,1],B:[[-1,-3]],clock:1297519076,head:58877,span:59907,witness:"0110101010101010101111111110100"},
  {name:"edge-UNSAT",m:2,pins:[1,0],B:[[-1],[-2],[-1,-3]],clock:665681141,head:57907,span:58907,witness:null},
  {name:"K5-refusal",m:2,pins:[1,1],B:[...E.subsets([0,1,2,3,4],2)].map(h=>h.map(v=>-(2*v+1))),clock:27879501,head:37913,span:39346,witness:null}
 ];
 const z=[2,1,0,2,0,1,2,1,0],B=z.flatMap((a,g)=>[0,1,2].filter(i=>i!==a).map(i=>[-(3*g+i+1)]));
 B.push(...[...E.subsets([0,3,6,8],2)].map(h=>h.map(v=>-(3*v+1))));
 a.push({name:"m3-forced",m:3,pins:[1,0,1],B,clock:72540199790,head:229473,span:232294,witness:E.witness(3,[1,0,1],z)});
 return a.filter(x=>suite==="all"||x.name===suite).map(x=>({...x,n:19*x.m-7,raw:E.encode(x.m,x.pins,x.B)}));
}
function replay(A,M,E,suite){
 const rows=[];
 for(let f of fixtures(E,suite)){
  const limit=f.clock??50000000000,r=A.run(M,f.raw,f.n,limit);
  if(r.status!=="HALT"||r.witness!==f.witness||(f.clock!==null&&(r.t!==f.clock||r.head!==f.head||r.span!==f.span))||(r.witness!==null&&(!E.valid(f.raw,r.witness)||r.nextSymbol!==2))||(r.witness===null&&r.headSymbol!==2))throw Error("replay "+f.name+" "+JSON.stringify(r));
  rows.push({name:f.name,m:f.m,...r,admission:r.witness===null?null:slot(f.n,M.stats.quotientBits,r.t)});
 }
 if(!rows.length)throw Error("suite");
 return{stats:M.stats,rows};
}
function dependencies(){
 const A=require('./f038_rex_width_three_halt_witness.js'),B=require('./f038_rex_width_three_physical_bridge.js'),P=require('./f038_rex_width_three_bridge_producer.js'),W=require('./f038_rex_width_three_witness_ir.js'),F=require('./f038_rex_width_three_forest_ir.js'),R=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),V=require('./f038_rex_width_three_projection.js'),K=require('./f038_rex_width_three_exit_compiler.js'),Q=require('./f038_rex_width_two_quotient.js'),E=require('./f038_tga_normalized_integration.js').engine();
 return{A,B,P,W,F,R,C,V,K,Q,E};
}
async function main(){
 const d=dependencies(),mode=process.argv[2]||"empty";
 if(mode==="fixtures"){
  for(let f of fixtures(d.E,"all"))console.log([f.name,f.n,f.clock??50000000000,f.raw,f.witness??"-",f.head??"-",f.span??"-"].join(" "));
  return;
 }
 const M=build(d.A,d.B,d.P,d.W,d.F,d.R,d.C,d.V,d.K,d.Q);
 if(mode==="descriptor"){
  const {descriptorChunks}=require('./f038_rex_width_three_compiler.js'),{once}=require('node:events');
  for(let chunk of descriptorChunks(M))if(!process.stdout.write(chunk))await once(process.stdout,'drain');
  process.stderr.write(JSON.stringify(M.stats)+"\n");return;
 }
 console.log("F038_REX_WIDTH_THREE_ADMISSION_OK "+JSON.stringify(replay(d.A,M,d.E,mode)));
}
module.exports={slot,build,fixtures,replay};
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
