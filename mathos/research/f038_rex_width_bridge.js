// REX-009: planner-guided prepared-worker lifecycle with host transfers.
const R=require('./f038_rex_batched_elimination.js'),A=require('./f038_rex_candidate_complete.js');
function bridge(R,A,fixture){
 const {domains,plan}=fixture, names=Object.keys(domains), ok=(x,s)=>{if(!x)throw Error(s)};
 const modes={physical:A.makeAdapter(R,"physical"),logical:A.makeAdapter(R,"logical")};
 let factors=fixture.factors.map(f=>({scope:f.scope.slice(),rows:f.rows.map(r=>r.slice())})),outgoing=[],hist=[],active=names.slice(),runs=[];
 for(let i=0;i<plan.steps.length;i++){
  const s=plan.steps[i],v=s.variable,h=s.outgoing_scope,mode=i===1?"logical":"physical",m=domains[v].length;
  ok(s.scope.every(n=>domains[n].length===m)&&m>=2,"equal rank domains");
  let touched=factors.filter(f=>f.scope.includes(v));
  let actual=active.filter(n=>n===v||touched.some(f=>f.scope.includes(n)));
  ok(JSON.stringify(actual)===JSON.stringify(s.scope),"scope certificate");
  const F=touched.map(f=>({h:f.scope.map(n=>names.indexOf(n)),S:new Set(f.rows.map(r=>r.map((x,j)=>domains[f.scope[j]].indexOf(x)).join(",")))}));
  const adapter=modes[mode],before={...adapter.stats};
  const got=adapter.bag(m,F,names.indexOf(v),h.map(n=>names.indexOf(n)),plan.cap);
  ok(adapter.stats.candidates-before.candidates===s.candidates&&adapter.stats.batches-before.batches===s.batches,"candidate certificate");
  const decode=k=>k===""?[]:k.split(",").map((x,j)=>domains[h[j]][+x]);
  const rows=[...got.S].map(decode).sort((a,b)=>{for(let j=0;j<a.length;j++)if(a[j]!==b[j])return a[j]-b[j];return 0;});
  ok(rows.length<=s.outgoing_bound,"output bound");
  const w=new Map([...got.witness].map(([k,a])=>[JSON.stringify(decode(k)),domains[v][a]]));
  ok(rows.length===w.size&&rows.every(r=>w.has(JSON.stringify(r))),"witness coverage");
  outgoing.push(rows);hist.push({v,h,w});
  factors=factors.filter(f=>!f.scope.includes(v));factors.push({scope:h,rows});active=active.filter(n=>n!==v);
  runs.push({variable:v,mode,candidates:s.candidates,batches:s.batches,physicalTransitions:adapter.stats.physicalTransitions-before.physicalTransitions,logicalTransitions:adapter.stats.logicalTransitions-before.logicalTransitions,outgoing:rows});
 }
 ok(active.length===0&&factors.every(f=>f.scope.length===0&&f.rows.length===1),"final true");
 let assignment={};
 for(let {v,h,w} of hist.reverse()){const a=w.get(JSON.stringify(h.map(n=>assignment[n])));ok(a!==undefined,"backtrack");assignment[v]=a;}
 ok(fixture.factors.every(f=>f.rows.some(r=>r.every((x,j)=>x===assignment[f.scope[j]]))),"original witness");
 return {plan,outgoing,runs,witness:assignment,stats:Object.fromEntries(Object.entries(modes).map(([k,v])=>[k,v.stats]))};
}
if(require.main===module){const f=JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));console.log(JSON.stringify(bridge(R,A,f.fixture??f)));}
module.exports={bridge};
