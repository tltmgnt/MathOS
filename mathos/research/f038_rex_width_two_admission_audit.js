// REX-024A exact compressed witness replay and selector budget ledger.
function audit(P,Q,S,E,W,suite="small"){
 const ok=(v,s)=>{if(!v)throw Error(s)},M=P.compile({packed:true}),C=Q.refine(M),desc=Q.encode(C),D=P.decode(desc);
 ok(desc.length===C.stats.quotientBits&&D.q===C.q&&D.T.every((v,i)=>v===C.T[i]),"exact quotient codec");
 // A representative class may contain several original program entry
 // states, so never use mapped state IDs as phase-entry observations.
 function run(raw,limit=Infinity){
  const origin=3*raw.length+1024;let tape=new Uint8Array(origin+raw.length+1024);tape.fill(2);
  for(let i=0;i<raw.length;i++)tape[origin+i]=+raw[i];let h=origin,lo=h,hi=h,s=0,t=0;
  while(s!==D.q&&t<limit){let v=D.T[3*s+tape[h]];tape[h]=(v>>2)&3;h+=(v&3)-1;s=v>>>4;t++;if(h<0)throw Error("left buffer");if(h>=tape.length){let a=new Uint8Array(tape.length*2);a.fill(2);a.set(tape);tape=a;}if(h<lo)lo=h;if(h>hi)hi=h;}
  if(s!==D.q)return{status:"TIMEOUT",t,head:h-origin,span:hi-lo+1,bits:null};
  let bits=null;if(tape[h]!==2){let e=h;while(tape[e]!==2)e++;bits=Array.from(tape.subarray(h,e)).join("");}
  return{status:bits===null?"BLANK":"WITNESS",t,head:h-origin,span:hi-lo+1,bits};
 }
 const rows=[],equality=(m,a,b)=>[...E.tup(m,2)].filter(([x,y])=>x!==y).map(([x,y])=>[-(m*a+x+1),-(m*b+y+1)]);
 function check(name,m,pins,B,clock,head,span,z=null,kind="unsat"){
  let raw=E.encode(m,pins,B),r=run(raw,clock??3000000000);
  ok(r.status===(z===null?"BLANK":"WITNESS"),name+" status "+JSON.stringify(r));
  if(clock!==null)ok(r.t===clock&&r.head===head&&r.span===span,"exact inherited clock/head/span "+name);
  if(z!==null)ok(r.bits===E.witness(m,pins,z)&&r.bits.length===19*m-7&&E.valid(raw,r.bits),"original witness "+name);
  else {let D=E.decode(raw),model=null;for(let v of E.tup(m,9))if(D.F.every(f=>f.S.has(f.h.map(g=>v[g]).join()))){model=v;break;}ok((model!==null)===(kind==="refusal"),"blank scope");}
  let original=S.slot(C.stats.originalBits,r.t,raw.length),reduced=S.slot(desc.length,r.t,raw.length),n=19*m-7;
  rows.push({name,m,n,L:raw.length,...r,meaning:z!==null?"verified_witness_slot":kind==="refusal"?"structural_refusal_no_witness":"unsat_halt_no_witness",original,reduced,exhaustiveBudgetStage:n+3,exhaustiveEligible3:n+3<=reduced.stage3});
  return {raw,r};
 }
 if(suite==="small"){
  check("empty",2,[0,0],[],30003260,38460,39491,Array(9).fill(0));
  let a=check("outside-triple",2,[1,0],[[-1,-9,-17]],34911962,38652,39686,[1,0,0,0,0,0,0,0,0]);
  check("nonmonotone-star",2,[1,1],[[-1,-3],[-2,-5],[-1,-7],[-2,-9],[-1,-11],[-2,-13],[-1,-15],[-2,-17],[-4]],40288500,38724,39763,[1,0,1,0,1,0,1,0,1]);
  check("nonfirst-chain",2,[0,1],[...equality(2,0,4),...equality(2,4,8),[-17]],31626203,38472,39505,[1,0,0,0,1,0,0,0,1]);
  let B=[...E.tup(2,3)].filter(z=>z[0]!==z[2]).map(z=>[0,1,8].map((v,i)=>-(2*v+z[i]+1)));for(let v=2;v<=7;v++)B.push([-1,-(2*v+1)],[-(2*v+1),-17]);B.push([-1],[-17]);
  check("middle-owner-joint-sat",2,[1,1],B,58956884,39102,40148,[1,0,0,0,0,0,0,0,1]);
  check("nonempty-inconsistent",2,[0,1],[...equality(2,0,4),...equality(2,4,8),[-2],[-17]],30968165,37913,39399);
  let pair=[...E.tup(2,3)].filter(z=>z[1]!==z[2]).map(z=>[0,4,8].map((v,i)=>-(2*v+z[i]+1)));pair.push([-9,-17],[-10,-18]);check("joint-pair-inconsistent",2,[1,0],pair,34465372,37913,39490);
  check("disconnected-unsat",2,[0,0],[[-1,-7,-17],[-3],[-4],[-5,-13]],35143066,37913,39605);
  check("unary-unsat",2,[0,1],[[-1],[-2]],29496152,37913,39379);
  check("K4-SAT-refusal",2,[1,1],[...E.subsets([0,1,2,3],2)].map(h=>h.map(v=>-(2*v+1))),26655850,37913,39024,null,"refusal");
  for(let t of [0,1,100,a.r.t-1])ok(run(a.raw,t).status==="TIMEOUT","cutoff "+t);
  let n=31,pos=new Map(),at=n+1;for(let c of E.pool(n))pos.set(c.join(),at++);
  const flip=(s,i)=>s.slice(0,i)+(s[i]==="1"?"0":"1")+s.slice(i+1);
  const reject=[["",235],["1000",328],["110"+"0".repeat(8),427],["1".repeat(32)+"0",3156],[flip(a.raw,pos.get("-31")),100767],[flip(a.raw,pos.get("-28,-30,-31")),23900297],[a.raw.slice(0,-1),23980569],[a.raw+"1",23981538],[flip(a.raw,pos.get("1,17")),120563]];
  for(let [raw,t] of reject){let r=run(raw,t);ok(r.status==="BLANK"&&r.t===t,"exact malformed refusal");}
 }else if(suite==="larger"){
  let seed=0x52455823;const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0,H=[[0,4,8],[1,4,8],[2,5,6],[3,7],[0],[8],[4,8]];
  check("m3-mixed",3,[1,0,1],H.flatMap(h=>[...E.tup(3,h.length)].filter(()=>rnd()>>>24<100).map(z=>h.map((g,i)=>-(3*g+z[i]+1)))),483345064,164050,166876,[1,1,0,0,1,0,0,0,0]);
 }else if(suite==="ranktwo"){
  const z=[2,1,0,2,0,1,2,1,0],B=z.flatMap((a,g)=>[0,1,2].filter(i=>i!==a).map(i=>[-(3*g+i+1)]));B.push([-1,-13,-25]);check("m3-rank-two",3,[0,1,1],B,338108760,162682,165502,z);
 }else if(suite==="four"){
  let z=[3,2,1,0,3,2,1,0,3],B=z.flatMap((a,g)=>[0,1,2,3].filter(i=>i!==a).map(i=>[-(4*g+i+1)]));B.push([-1,-17,-33]);check("m4-forced-mixed",4,[1,0,1,0],B,null,null,null,z);
 }else if(suite==="four-bounded"){
  let z=[3,2,1,0,3,2,1,0,3],B=z.flatMap((a,g)=>[0,1,2,3].filter(i=>i!==a).map(i=>[-(4*g+i+1)]));B.push([-1,-17,-33]);let raw=E.encode(4,[1,0,1,0],B),r=run(raw,300000000);ok(r.status==="TIMEOUT"&&r.t===300000000,"bounded m4");return{suite,stats:C.stats,L:raw.length,...r};
 }else throw Error("suite");
 return{suite,stats:C.stats,rows,transitions:rows.reduce((a,r)=>a+r.t,0),cutoffs:suite==="small"?4:0,refusalControls:suite==="small"?9:0};
}
function controls(P,Q,old){
 const ok=(v,s)=>{if(!v)throw Error(s)};let seed=0x52455824,rand=n=>(seed=(Math.imul(seed,1664525)+1013904223)>>>0)%n;
 for(let i=0;i<256;i++){
  let q=1+rand(48),T=new Uint32Array(3*q);for(let j=0;j<T.length;j++)T[j]=(rand(q+1)<<4)|(rand(3)<<2)|rand(3);
  if(i%4===0)for(let j=0;j<T.length;j++)T[j]=((T[j]>>>4)%q<<4)|(T[j]&15); // unreachable halt
  if(i%4===1)T.fill((q<<4)|9); // immediately halt; unreachable states
  if(i%4===2)T.fill(1); // identical self-loop states
  let M={q,T},d=Q.encode(M),C=Q.refine(M),B=old.quotient(P,d);
  ok(C.q===B.q&&C.stats.reachableStates===B.stats.reachableStates,"reference quotient size "+i);
  // Cross-check partitions up to arbitrary renumbering, including halt.
  let f=new Map(),g=new Map();for(let j=0;j<=q;j++){let x=C.map[j],y=B.map[j];ok((x<0)===(y<0),"reachability");if(x<0)continue;if(f.has(x))ok(f.get(x)===y,"class split");if(g.has(y))ok(g.get(y)===x,"class merge");f.set(x,y);g.set(y,x);}
 }
 return{randomMachines:256,agreement:true};
}
module.exports={audit,controls};
if(require.main===module){const P=require('./f038_rex_width_two_witness.js'),Q=require('./f038_rex_width_two_quotient.js'),S=require('./f038_rex_stage_audit.js'),E=require('./f038_tga_normalized_integration.js').engine();if(process.argv.includes('--descriptor'))process.stdout.write(Q.encode(Q.refine(P.compile({packed:true}))));else if(process.argv[2]==='controls')console.log('F038_REX_WIDTH_TWO_ADMISSION_CONTROLS '+JSON.stringify(controls(P,Q,require('./f038_rex_stage_quotient.js'))));else console.log('F038_REX_WIDTH_TWO_ADMISSION_OK '+JSON.stringify(audit(P,Q,S,E,null,process.argv[2]||'small')));}
