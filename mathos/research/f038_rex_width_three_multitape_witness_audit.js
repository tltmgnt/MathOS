// Independent original-factor and exact ordered relation oracle; snapshot handoff only.
function audit(P,K,T,E,suite="small"){
 const C=P.compile(),M={...P.decode(C.desc),plannerEntry:C.plannerEntry,pushEntry:C.pushEntry,popEntry:C.popEntry},ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 const V=[...Array(9).keys()],edges=V.flatMap(a=>V.filter(b=>b>a).map(b=>[a,b])),clique=vs=>edges.filter(h=>h.every(v=>vs.includes(v))),make=(m,H)=>H.map(h=>h.map(v=>-(m*v+1)));
 function parity(consistent){
  let B=[];for(let [x,a,b] of E.tup(2,3))if(x!==(a^b))B.push([-(x+1),-(6+a+1),-(10+b+1)]);
  for(let [x,c] of E.tup(2,2))if(x!==c)B.push([-(x+1),-(16+c+1)]);
  for(let [a,b,c] of E.tup(2,3))if((a^b^c)!==(consistent?0:1))B.push([-(6+a+1),-(10+b+1),-(16+c+1)]);
  return B;
 }
 const trap=[[0,1],[0,2],[0,6],[1,3],[1,8],[2,5],[2,7],[3,6],[3,7],[3,8],[4,6],[5,8],[6,7],[7,8]];
 function check(name,m,pins,B,want){
  const raw=E.encode(m,pins,B),D=E.decode(raw),p=P.run(M,raw,3000000000,null,true);
  ok(p.status===(want===null?"OUTSIDE_WIDTH_THREE":"WIDTH_THREE_FACTORS"),"producer "+name);
  ok(p.snapshot.length===p.span+2&&p.snapshot.split("H").length===2,"literal snapshot");
  let r=K.controller(p.snapshot,T.mergeTapes,Infinity,true);
  let models=0;for(let z of E.tup(m,9))if(D.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))models++;
  ok(r.tapes===176&&Object.values(r.ledger).reduce((a,b)=>a+b,0)===r.steps,"ledger");
  if(want===null){ok(r.status==="STRUCTURAL_REFUSAL"&&r.decision===null&&r.witness===null&&models>0,"structural refusal");rows.push({name,m,L:raw.length,producer:p.t,steps:r.steps,status:r.status,models,span:r.span,edges:0,candidates:0,localRows:0,liveRows:0});return {p,r};}
  ok(r.status==="COMPLETE"&&r.decision===String(+want)&&want===(models>0),"decision "+name);
  const w=Math.ceil(Math.log2(m)),encode=z=>z.map(x=>x.toString(2).padStart(w,"0")).join(",")+";";
  const order=p.checkpoint.order,bags=p.checkpoint.frames.slice(0,9).map((f,i)=>{
   const h=[f.choice,...f.neighbors.filter(x=>x!==9)].sort((a,b)=>a-b),sep=f.neighbors.filter(x=>x!==9),parent=f.parent;
   const owned=D.F.filter(f=>Math.min(...f.h.map(v=>order.indexOf(v)))===i);
   const local=[...E.tup(m,h.length)].filter(z=>owned.every(f=>f.S.has(f.h.map(v=>z[h.indexOf(v)]).join())));
   ok(r.headers[i].v===f.choice&&r.headers[i].parent===parent&&r.headers[i].h.join()===h.join()&&r.headers[i].sep.join()===sep.join(),"header");
   ok(r.local[i]===local.map(encode).join(""),"exact local "+name+":"+i);
   return{h,sep,parent,local,live:local.slice()};
  });
  let edges=0;
  for(let i=0;i<9;i++){
   const b=bags[i];if(b.parent===9)continue;const j=order.indexOf(b.parent),par=bags[j],project=(h,z)=>b.sep.map(v=>z[h.indexOf(v)]).join();
   const support=new Set(b.live.map(z=>project(b.h,z)));
   // Stable numeric lex key order is equivalent to the fixed-width
   // binary field encoding. Compare the exact retained stream order.
   par.live=par.live.filter(z=>support.has(project(par.h,z))).sort((a,b)=>{for(let v of bags[i].sep){let d=a[par.h.indexOf(v)]-b[par.h.indexOf(v)];if(d)return d;}return 0;});
   edges++;
  }
  ok(r.edges===edges&&bags.every((b,i)=>r.relations[i]===b.live.map(encode).join("")),"exact retained streams "+name);
  let ranks=null;
  if(want){
   ranks=Array(9).fill(-1);
   for(let i=8;i>=0;i--){
    const b=bags[i],row=b.live.find(z=>b.sep.every(g=>z[b.h.indexOf(g)]===ranks[g]));
    ok(row&&r.selected[i]===encode(row),"selected row "+name+":"+i);
    const g=order[i];ranks[g]=row[b.h.indexOf(g)];
   }
   ok(r.chosen.join()===ranks.map(x=>x.toString(2).padStart(w,"0")).join(),"original order ranks");
   ok(r.witness===E.witness(m,pins,ranks)&&r.witness.length===19*m-7&&E.valid(raw,r.witness),"original witness "+name);
  }else ok(r.witness===null&&r.chosen===null&&r.selected===null&&r.ledger.select===0&&r.ledger.translate===0,"no UNSAT witness");
  const localRows=bags.reduce((a,b)=>a+b.local.length,0),liveRows=bags.reduce((a,b)=>a+b.live.length,0);
  rows.push({name,m,L:raw.length,producer:p.t,steps:r.steps,status:r.status,models,decision:r.decision,span:r.span,edges,candidates:bags.reduce((a,b)=>a+m**b.h.length,0),localRows,liveRows,passes:r.passes,ledger:r.ledger,ranks,witness:r.witness});
  return{p,r};
 }
 if(suite==="small"){
  check("empty",2,[0,0],[],true);check("K4",2,[1,0],make(2,clique([0,1,2,3])),true);
  check("greedy-trap",2,[1,1],make(2,trap),true);
  let x=check("joint-three-UNSAT",2,[0,1],parity(false),false);ok(x.r.local.every(s=>s.length>0)&&x.r.relations.some(s=>!s),"joint obstruction");
  check("joint-three-SAT",2,[1,0],parity(true),true);
  check("disconnected-UNSAT",2,[0,0],parity(true).concat([[-3],[-4]]),false);
  check("unary-UNSAT",2,[1,0],[[-1],[-2]],false);
  check("K5-SAT-refusal",2,[1,1],make(2,clique([0,1,2,3,4])),null);
 }else if(suite==="larger"){
  check("m3-greedy-trap",3,[1,0,1],make(3,trap),true);
  const z=[2,1,0,2,0,1,2,1,0],B=z.flatMap((a,g)=>[0,1,2].filter(i=>i!==a).map(i=>[-(3*g+i+1)]));
  check("m3-forced-four",3,[0,1,1],B.concat(make(3,clique([0,3,6,8]))),true);
 }else if(suite==="four"){
  const z=[3,2,1,0,3,2,1,0,3],B=z.flatMap((a,g)=>[0,1,2,3].filter(i=>i!==a).map(i=>[-(4*g+i+1)]));
  check("m4-forced-four",4,[1,0,1,0],B.concat(make(4,clique([0,3,6,8]))),true);
 }else if(suite==="controls"){
  const {p,r}=check("joint-three-SAT",2,[1,0],parity(true),true),cutoffs=[0,1,100,r.ledger.load-1,r.ledger.load,r.steps-r.ledger.translate-r.ledger.select,r.steps-r.ledger.translate,r.steps-1];
  for(let k of cutoffs){const x=K.controller(p.snapshot,T.mergeTapes,k,true);ok(x.status==="TIMEOUT"&&x.steps===k&&x.decision===null&&x.witness===null,"cutoff");}
  ok(K.controller(p.snapshot,T.mergeTapes,r.steps).witness===r.witness,"exact budget");
  const h=p.snapshot.indexOf("H"),bad=["",p.snapshot.replace("H","_"),p.snapshot.slice(0,h+60),p.snapshot.slice(0,h+77)+"2"+p.snapshot.slice(h+78)];
  for(let s of bad)ok(K.controller(s,T.mergeTapes).status==="MALFORMED_CHECKPOINT","bad checkpoint");
  return{suite,cutoffs,malformed:bad.length,exactBudget:r.steps};
 }else throw Error("suite");
 return{suite,rows,totals:rows.reduce((a,r)=>({rawBits:a.rawBits+r.L,witnessBits:a.witnessBits+(r.witness?.length??0),select:a.select+(r.ledger?.select??0),translate:a.translate+(r.ledger?.translate??0),producer:a.producer+r.producer,steps:a.steps+r.steps,edges:a.edges+r.edges,candidates:a.candidates+r.candidates,localRows:a.localRows+r.localRows,liveRows:a.liveRows+r.liveRows}),{rawBits:0,witnessBits:0,select:0,translate:0,producer:0,steps:0,edges:0,candidates:0,localRows:0,liveRows:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_MULTITAPE_WITNESS_OK '+JSON.stringify(audit(require('./f038_rex_width_three_factors.js'),require('./f038_rex_width_three_multitape_witness.js'),require('./f038_rex_width_three_merge_tapes.js'),require('./f038_tga_normalized_integration.js').engine(),process.argv[2]||'small')));
