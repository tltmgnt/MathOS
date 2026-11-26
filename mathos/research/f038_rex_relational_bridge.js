// REX-008: cross-language semantic bridge; host rank encoding, actual prepared worker.
const R=require('./f038_rex_batched_elimination.js'),A=require('./f038_rex_candidate_complete.js');
function bridge(R,A){
 const fixtures=[
  {name:"physical_shared_witness",mode:"physical",domains:{a:[-3,7]},order:["a"],eliminate:"a",nextOrder:[],cap:2,factors:[{scope:["a"],rows:[[-3]]}]},
  {name:"physical_conflicting_witness",mode:"physical",domains:{a:[-3,7]},order:["a"],eliminate:"a",nextOrder:[],cap:2,factors:[{scope:["a"],rows:[[-3]]},{scope:["a"],rows:[[7]]}]},
  {name:"physical_split_outgoing_group",mode:"physical",domains:{a:[-3,7]},order:["a"],eliminate:"a",nextOrder:[],cap:1,factors:[{scope:["a"],rows:[[7]]}]},
  {name:"logical_binary_projection",mode:"logical",domains:{a:[-3,7],k:[2,9]},order:["a","k"],eliminate:"a",nextOrder:["k"],cap:3,factors:[{scope:["k","a"],rows:[[2,-3],[9,7]]},{scope:["a"],rows:[[7]]}]},
  {name:"host_reordered_projection",mode:"host",domains:{a:[-3,7],b:[2,9],c:[-5,4]},order:["b","a","c"],eliminate:"a",nextOrder:["c","b"],cap:3,factors:[{scope:["c","a"],rows:[[-5,-3],[4,7]]},{scope:["a","b"],rows:[[-3,9],[7,2]]}]},
  {name:"logical_empty_bucket",mode:"logical",domains:{a:[-3,7]},order:["a"],eliminate:"a",nextOrder:[],cap:1,factors:[]}
 ];
 const modes=Object.fromEntries(["physical","logical","host"].map(m=>[m,A.makeAdapter(R,m)]));
 const cases=fixtures.map(c=>{
  const names=c.order,idx=v=>names.indexOf(v),v=idx(c.eliminate),h=c.nextOrder.map(idx),m=c.domains[c.eliminate].length;
  if(!names.every(n=>c.domains[n].length===m))throw Error("uniform rank domain required");
  const F=c.factors.map(f=>({h:f.scope.map(idx),S:new Set(f.rows.map(row=>row.map((x,i)=>c.domains[f.scope[i]].indexOf(x)).join(",")))}));
  const rankTuple=q=>q===""?[]:q.split(",").map(Number);
  const got=modes[c.mode].bag(m,F,v,h,c.cap);
  const decode=q=>rankTuple(q).map((x,i)=>c.domains[c.nextOrder[i]][x]);
  const witnesses=[...got.witness].map(([q,a])=>[decode(q),c.domains[c.eliminate][a]]).sort((x,y)=>{for(let i=0;i<x[0].length;i++)if(x[0][i]!==y[0][i])return x[0][i]-y[0][i];return 0;});
  if(got.S.size!==witnesses.length||[...got.S].some(q=>!got.witness.has(q)))throw Error("witness coverage");
  return {...c,outgoingRows:witnesses.map(x=>x[0]),witnesses};
 });
 return {cases,stats:Object.fromEntries(Object.entries(modes).map(([k,v])=>[k,v.stats]))};
}
if(require.main===module)console.log(JSON.stringify(bridge(R,A)));
module.exports={bridge};
