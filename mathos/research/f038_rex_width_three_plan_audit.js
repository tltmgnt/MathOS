// REX-024B exact physical plan audit against independent subset-torso DP.
function audit(P,E,suite="small"){
 const C=P.compile(),M={...P.decode(C.desc),plannerEntry:C.plannerEntry,pushEntry:C.pushEntry,popEntry:C.popEntry},ok=(v,s)=>{if(!v)throw Error(s)},V=[...Array(9).keys()],edges=V.flatMap(a=>V.filter(b=>b>a).map(b=>[a,b])),rows=[];
 const key=(a,b)=>`${Math.min(a,b)},${Math.max(a,b)}`;
 const make=(m,H)=>H.map(h=>h.map(v=>-(m*v+1)));
 const clique=vs=>edges.filter(h=>h.every(v=>vs.includes(v)));
 const bip=(a,b)=>a.flatMap(x=>b.map(y=>[x,y]));
 const adversarial=[[0,1],[0,2],[0,6],[1,3],[1,8],[2,5],[2,7],[3,6],[3,7],[3,8],[4,6],[5,8],[6,7],[7,8]];
 function check(name,m,pins,B,want,backtrack=false){
  const raw=E.encode(m,pins,B),D=E.decode(raw),r=P.run(M,raw,2000000000),p=r.checkpoint;
  ok(D&&p&&r.status===(want?"WIDTH_THREE_PLAN":"OUTSIDE_WIDTH_THREE"),name+" "+r.status);
  const graph=new Set();for(let f of D.F)for(let [a,b] of E.subsets(f.h,2))graph.add(key(a,b));
  const N=V.map(v=>V.filter(u=>graph.has(key(v,u))));
  // Independent subset-torso oracle: do not replay the physical fill algorithm.
  // Surviving neighbors are original paths through eliminated vertices.
  const memo=new Map(),cache=new Map();
  function neighbors(v,S){
   let k=S*9+v;if(cache.has(k))return cache.get(k);
   let seen=1<<v,queue=[v],result=0;
   for(let i=0;i<queue.length;i++)for(let u of N[queue[i]])if(!(seen>>u&1)){seen|=1<<u;if(S>>u&1)queue.push(u);else result|=1<<u;}
   const ns=V.filter(u=>result>>u&1);cache.set(k,ns);return ns;
  }
  function order(S){
   if(S===511)return [];if(memo.has(S))return memo.get(S);
   for(let v of V)if(!(S>>v&1)&&neighbors(v,S).length<=3){let tail=order(S|1<<v);if(tail){let a=[v,...tail];memo.set(S,a);return a;}}
   memo.set(S,null);return null;
  }
  const expected=order(0);
  ok(Boolean(expected)===want,"independent exact width oracle "+name);
  ok(p.graph.join("")===edges.map(([a,b])=>+graph.has(key(a,b))).join("")&&p.selector===raw.slice(19*m-6)&&p.pins===pins.join("")&&p.m===m&&p.ranks.join()==="0,0,0","preserved input");
  ok(Number.isInteger(r.plannerAt)&&r.plannerAt<r.t&&p.head===raw.length-1,"planner entry/head");
  ok(r.pushes-r.pops===(want?9:0),"physical stack conservation");
  let bags=[],S=0;
  for(let i=0;i<p.frames.length;i++){
   let f=p.frames[i],eligible=V.filter(v=>!(S>>v&1)&&neighbors(v,S).length<=3),choice=want&&i<9?expected[i]:null;
   ok(f.active===V.map(v=>+(!(S>>v&1))).join(""),"active "+name);
   ok(f.graph===edges.map(([a,b])=>+(!(S>>a&1)&&!(S>>b&1)&&neighbors(a,S).includes(b))).join(""),"torso "+name);
   let tried=eligible.filter(v=>choice===null?!want:v<=choice);
   ok(f.tried===V.map(v=>+tried.includes(v)).join(""),"tried bitmap "+name);
   if(choice!==null){ok(f.choice===choice,"exact lex first successful order");bags.push([choice,...neighbors(choice,S)]);S|=1<<choice;}
   else ok(f.choice===(tried.at(-1)??9),"terminal choice");
  }
  let parents=[];
  if(want){
   ok(S===511&&p.order.join()===expected.join(),"complete order");
   parents=bags.map((h,i)=>h.length===1?9:Math.min(...h.slice(1).map(v=>bags.findIndex(b=>b[0]===v))));
   for(let i=0;i<9;i++)if(parents[i]!==9)ok(parents[i]>i&&bags[i].slice(1).every(v=>bags[parents[i]].includes(v)),"separator");
   for(let f of D.F)ok(bags.some(h=>f.h.every(v=>h.includes(v))),"factor coverage");
   for(let v of V){let nodes=bags.map((h,i)=>h.includes(v)?i:-1).filter(i=>i>=0),seen=new Set([nodes[0]]);
    for(let k=0;k<9;k++)for(let i of nodes)if(nodes.includes(parents[i])&&(seen.has(i)||seen.has(parents[i]))){seen.add(i);seen.add(parents[i]);}
    ok(seen.size===nodes.length,"running intersection");
   }
  }else ok(p.order===null&&p.frames.length===1,"refusal stack");
  let greedy=[],G=0;while(G!==511){let v=V.find(v=>!(G>>v&1)&&neighbors(v,G).length<=3);if(v===undefined)break;greedy.push(v);G|=1<<v;}
  if(backtrack)ok(want&&greedy.length<9&&r.pops>0&&p.order[0]!==greedy[0],"greedy counterexample");
  rows.push({name,m,L:raw.length,edges:graph.size,status:r.status,t:r.t,planner:r.t-r.plannerAt,pushes:r.pushes,pops:r.pops,order:p.order,greedy,width:want?Math.max(...bags.map(h=>h.length-1)):null,parents,span:r.span});
  return{raw,r};
 }
 if(suite==="small"){
  check("empty",2,[0,0],[],true);
  check("K4",2,[1,0],make(2,clique([0,1,2,3])),true);
  check("K3_6",2,[0,1],make(2,bip([0,4,8],[1,2,3,5,6,7])),true);
  check("3x3-grid",2,[1,1],make(2,edges.filter(([a,b])=>b-a===3||b-a===1&&Math.floor(a/3)===Math.floor(b/3))),true);
  check("two-triples",2,[1,0],make(2,[[0,4,8],[1,3,7]]),true);
  check("greedy-trap",2,[0,1],make(2,adversarial),true,true);
  check("K5",2,[1,1],make(2,clique([0,1,2,3,4])),false);
  check("subdivided-K5",2,[1,0],make(2,clique([0,1,2,3,4]).filter(h=>h.join()!=="0,1").concat([[0,5],[1,5]])),false);
  check("K4_5",2,[0,0],make(2,bip([0,1,2,3],[4,5,6,7,8])),false);
  let x=check("complete-SAT-refusal",2,[0,1],make(2,edges),false);ok(E.valid(x.raw,E.witness(2,[0,1],Array(9).fill(1))),"refused original SAT");
  let u=check("unary-UNSAT-plan",2,[1,0],[[-1],[-2]],true);ok([...E.tup(2,9)].every(z=>!E.valid(u.raw,E.witness(2,[1,0],z))),"accepted structural UNSAT");
 }else if(suite==="larger"){
  check("m3-greedy-trap",3,[1,0,1],make(3,adversarial),true,true);
  check("m3-K5",3,[0,1,1],make(3,clique([0,2,4,6,8])),false);
  check("m4-K4",4,[1,0,0,1],make(4,clique([0,3,6,8])),true);
 }else if(suite==="controls"){
  let raw=E.encode(2,[0,1],make(2,adversarial)),r=P.run(M,raw,100000000),cutoffs=[];
  for(let k of [0,1,100,r.plannerAt-1,r.plannerAt,r.t-1]){let a=P.run(M,raw,k);ok(a.status==="TIMEOUT"&&a.t===k,"cutoff");cutoffs.push(k);}
  ok(P.run(M,raw,r.t).status==="WIDTH_THREE_PLAN","exact completion");
  let n=31,pos=new Map(),at=n+1;for(let c of E.pool(n))pos.set(c.join(),at++);
  const flip=(s,i)=>s.slice(0,i)+(s[i]==="1"?"0":"1")+s.slice(i+1),rejects=[];
  for(let [name,s] of [["empty",""],["n1","1000"],["header","1".repeat(32)+"0"],["mandatory",flip(raw,pos.get("-31"))],["late-pin",flip(raw,pos.get("-28,-30,-31"))],["truncated",raw.slice(0,-1)],["extra",raw+"1"],["invalid-positive",flip(raw,pos.get("1,17"))]]){
   let a=P.run(M,s,100000000);ok(a.status==="OUTSIDE_NORMALIZED"&&E.decode(s)===null,"malformed "+name);rejects.push({name,t:a.t});
  }
  return{suite,q:C.q,descriptorBits:C.desc.length,plannerEntry:C.plannerEntry,pushEntry:C.pushEntry,popEntry:C.popEntry,cutoffs,rejects,exactBudget:r.t};
 }else throw Error("suite");
 return{suite,q:C.q,descriptorBits:C.desc.length,plannerEntry:C.plannerEntry,pushEntry:C.pushEntry,popEntry:C.popEntry,rows,totals:rows.reduce((a,r)=>({rawBits:a.rawBits+r.L,transitions:a.transitions+r.t,planner:a.planner+r.planner,pushes:a.pushes+r.pushes,pops:a.pops+r.pops,accepted:a.accepted+ +(r.status==="WIDTH_THREE_PLAN"),refused:a.refused+ +(r.status==="OUTSIDE_WIDTH_THREE")}),{rawBits:0,transitions:0,planner:0,pushes:0,pops:0,accepted:0,refused:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_PLAN_OK '+JSON.stringify(audit(require('./f038_rex_width_three_plan.js'),require('./f038_tga_normalized_integration.js').engine(),process.argv[2]||'small')));
