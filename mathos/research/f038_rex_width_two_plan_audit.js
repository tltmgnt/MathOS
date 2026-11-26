// Physical width-two planner / independent subset-torso oracle.
function audit(P,E,suite="small"){
 const C=P.compile(),M=P.decode(C.desc),ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 const V=Array.from({length:9},(_,i)=>i),edges=[];for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)edges.push([i,j]);
 const key=(i,j)=>`${Math.min(i,j)},${Math.max(i,j)}`;
 function oracle(graph){
  // Subset DP over eliminated vertices. Adjacency of remaining vertices
  // is reachability through paths with internal vertices in the subset.
  const memo=new Map(),N=V.map(i=>V.filter(j=>graph.has(key(i,j))));
  function neighbors(v,S){
   let seen=1<<v,queue=[v],result=0;
   for(let i=0;i<queue.length;i++)for(let u of N[queue[i]])if(!(seen>>u&1)){seen|=1<<u;if(S>>u&1)queue.push(u);else result|=1<<u;}
   return V.filter(u=>result>>u&1);
  }
  function possible(S){
   if(S===511)return true;if(memo.has(S))return memo.get(S);
   let b=V.some(v=>!(S>>v&1)&&neighbors(v,S).length<=2&&possible(S|1<<v));memo.set(S,b);return b;
  }
  return{possible:possible(0),neighbors};
 }
 function check(name,m,pins,B,want){
  const raw=E.encode(m,pins,B),D=E.decode(raw);ok(D,"fixture normalized");
  const graph=new Set();for(let f of D.F)for(let [a,b] of E.subsets(f.h,2))graph.add(key(a,b));
  const O=oracle(graph),r=P.run(M,raw,200000000),p=r.checkpoint;
  ok(O.possible===want&&r.status===(want?"WIDTH_TWO_PLAN":"OUTSIDE_WIDTH_TWO"),name+" status "+r.status);
  ok(p.graph.join("")===edges.map(([a,b])=>+graph.has(key(a,b))).join(""),"original graph "+name);
  ok(p.pins===pins.join("")&&p.selector===raw.slice(19*m-6)&&p.m===m&&p.ranks.join()==="0,0,0","preserved data");
  let S=0,max=0;const bags=[];
  for(let [v,a,b] of p.plan){
   let candidates=V.filter(u=>!(S>>u&1)&&O.neighbors(u,S).length<=2);
   ok(candidates.length&&v===candidates[0],"lexicographic elimination");
   let ns=O.neighbors(v,S);ok([a,b].join()===[ns[0]??9,ns[1]??9].join(),"exact residual neighborhood");
   max=Math.max(max,ns.length);bags.push([v,...ns]);S|=1<<v;
  }
  ok(p.active===V.map(v=>+( !(S>>v&1))).join(""),"active flags");
  ok(p.residual===edges.map(([a,b])=>+(!(S>>a&1)&&!(S>>b&1)&&O.neighbors(a,S).includes(b))).join(""),"filled residual");
  let parents=[];
  if(want){
   ok(S===511&&bags.length===9,"complete order");
   parents=bags.map((h,i)=>h.length===1?-1:Math.min(...h.slice(1).map(v=>bags.findIndex(b=>b[0]===v))));
   for(let i=0;i<9;i++)if(parents[i]>=0)ok(parents[i]>i&&bags[i].slice(1).every(v=>bags[parents[i]].includes(v)),"separator");
   for(let f of D.F)ok(bags.some(b=>f.h.every(v=>b.includes(v))),"factor coverage");
   // Every variable's containing bags must induce a connected subtree.
   for(let v of V){let nodes=bags.map((b,i)=>b.includes(v)?i:-1).filter(i=>i>=0),seen=new Set([nodes[0]]);
    for(let i=0;i<9;i++)for(let j of nodes)if(seen.has(j)||seen.has(parents[j])){seen.add(j);if(nodes.includes(parents[j]))seen.add(parents[j]);}
    ok(seen.size===nodes.length,"running intersection");
   }
  }else ok(S!==511&&V.filter(v=>!(S>>v&1)).every(v=>O.neighbors(v,S).length>=3),"stuck core");
  rows.push({name,m,L:raw.length,edges:graph.size,selectedScopes:D.F.length,status:r.status,t:r.t,span:r.span,plan:p.plan,parents,width:max,residualVertices:9-p.plan.length,pins:p.pins});
  return {raw,r};
 }
 const clauses=(m,H)=>H.map(h=>h.map(g=>-(g*m+1)));
 const clique=vs=>edges.filter(e=>e.every(v=>vs.includes(v)));
 const bip=(a,b)=>a.flatMap(x=>b.map(y=>[x,y]));
 if(suite==="small"){
  const fixtures=[
   ["empty",[],true],["outside-edge",[[0,8]],true],["outside-triple",[[0,4,8]],true],
   ["star",V.slice(1).map(v=>[0,v]),true],["cycle",V.map(v=>[v,(v+1)%9]),true],
   ["K2_7",bip([0,8],[1,2,3,4,5,6,7]),true],
   ["two-triangles",[[0,3,8],[1,5,7]],true],
   ["K4",clique([0,1,2,3]),false],
   ["K3_3",bip([0,1,2],[3,4,5]),false],
   ["subdivided-K4",[[0,4],[4,1],[0,5],[5,2],[0,6],[6,3],[1,7],[7,2],[1,8],[8,3],[2,3]],false],
   ["complete",edges,false],
  ];
  for(let i=0;i<fixtures.length;i++){let [name,H,want]=fixtures[i],v=check(name,2,[i&1,(i>>1)&1],clauses(2,H),want);if(name==="outside-edge"||name==="outside-triple"||name==="K4"||name==="complete")ok(E.valid(v.raw,E.witness(2,[i&1,(i>>1)&1],Array(9).fill(1))),"explicit SAT despite structural category");}
  // All ranks selected on a single pair must still deposit only one graph edge.
  check("duplicate-support",2,[1,1],[...E.tup(2,2)].map(z=>[-(z[0]+1),-(16+z[1]+1)]),true);
  // Contradictory unary clauses do not add an edge, and do not turn planning into SAT.
  const u=check("unary-unsat",2,[0,0],[[-1],[-2]],true);ok([...E.tup(2,9)].every(z=>!E.valid(u.raw,E.witness(2,[0,0],z))),"unary UNSAT despite complete plan");
 }else if(suite==="larger"){
  check("m3-mixed-scopes",3,[1,0,1],clauses(3,[[0,8,4],[0,8],[1,8,4],[1,4],[2,6],[2,5,6],[3,7]]),true);
  check("m3-K4",3,[0,1,1],clauses(3,clique([0,3,6,8])),false);
  check("m4-outside-star",4,[1,0,0,1],clauses(4,V.slice(1).map(v=>[0,v])),true);
 }else if(suite==="controls"){
  let raw=E.encode(2,[1,0],[[-1,-17]]),n=31,pos=new Map(),at=n+1;for(let c of E.pool(n))pos.set(c.join(","),at++);
  const flip=(s,i)=>s.slice(0,i)+(s[i]==="1"?"0":"1")+s.slice(i+1),controls=[];
  for(let [name,s] of [["empty",""],["header","1".repeat(32)+"0"],["mandatory",flip(raw,pos.get("-31"))],["late-pin",flip(raw,pos.get("-28,-30,-31"))],["truncated",raw.slice(0,-1)],["extra",raw+"1"],["invalid-positive",flip(raw,pos.get("1,17"))]]){
   let r=P.run(M,s,30000000);ok(r.status==="OUTSIDE_NORMALIZED"&&E.decode(s)===null,"refusal "+name);controls.push({name,t:r.t});
  }
  let r=P.run(M,raw,30000000);for(let t of [0,1,100,r.t-1])ok(P.run(M,raw,t).status==="TIMEOUT","cutoff");ok(P.run(M,raw,r.t).status==="WIDTH_TWO_PLAN","exact halt");
  return{suite,q:C.q,descriptorBits:C.desc.length,controls,cutoffs:4,exactBudget:r.t};
 }else throw Error("suite");
 return{suite,q:C.q,descriptorBits:C.desc.length,rows,totals:rows.reduce((a,r)=>({rawBits:a.rawBits+r.L,transitions:a.transitions+r.t,edges:a.edges+r.edges,records:a.records+r.plan.length,accepted:a.accepted+ +(r.status==="WIDTH_TWO_PLAN"),refused:a.refused+ +(r.status==="OUTSIDE_WIDTH_TWO")}),{rawBits:0,transitions:0,edges:0,records:0,accepted:0,refused:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_TWO_PLAN_OK '+JSON.stringify(audit(require('./f038_rex_width_two_plan.js'),require('./f038_tga_normalized_integration.js').engine(),process.argv[2]||'small')));
