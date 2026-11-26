// REX-023D1: physical row-flag and global decision differential oracle.
function audit(P,E,suite="small"){
 const C=P.compile(),M={...P.decode(C.desc),workerEntry:C.workerEntry},ok=(v,s)=>{if(!v)throw Error(s)},V=[...Array(9).keys()],scopes=[],rows=[];
 for(let k=1;k<=3;k++)for(let h of E.subsets(V,k))scopes.push(h);
 const edges=scopes.filter(h=>h.length===2);
 function check(name,m,pins,B,want){
  const raw=E.encode(m,pins,B),D=E.decode(raw),r=P.run(M,raw,2000000000),p=r.checkpoint;
  ok(D&&p&&r.status===want,name+" status "+r.status);
  const expected=scopes.map(h=>{let f=D.F.find(f=>f.h.join()===h.join());return [...E.tup(m,h.length)].map(z=>f&&!f.S.has(z.join())?"1":"0").join("");});
  ok(p.masks.length===129&&p.masks.every((b,i)=>b===expected[i]),"restored masks "+name);
  ok(p.selector===raw.slice(19*m-6)&&p.pins===pins.join("")&&p.m===m&&p.ranks.join()==="0,0,0"&&p.groups.join()==="19,20,20","checkpoint");
  let G=V.map(()=>new Set()),active=new Set(V);
  for(let f of D.F)for(let [a,b] of E.subsets(f.h,2)){G[a].add(b);G[b].add(a);}
  ok(p.graph.join("")===edges.map(([a,b])=>+G[a].has(b)).join(""),"graph");
  let bags=[];
  for(let [v,a,b] of p.plan){
   let choices=V.filter(x=>active.has(x)&&G[x].size<=2);ok(v===choices[0],"greedy");
   let ns=[...G[v]].sort((x,y)=>x-y);ok([a,b].join()===[ns[0]??9,ns[1]??9].join(),"neighbors");
   bags.push({owner:v,h:[v,...ns].sort((a,b)=>a-b),sep:ns});if(ns.length===2){G[a].add(b);G[b].add(a);}
   active.delete(v);for(let x of ns)G[x].delete(v);G[v].clear();
  }
  ok(p.active===V.map(v=>+active.has(v)).join("")&&p.residual===edges.map(([a,b])=>+G[a].has(b)).join(""),"residual");
  let models=0;for(let z of E.tup(m,9))if(D.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))models++;
  let local=[],live=[],roots=[],checks=0,sepCounts=[0,0,0],word="";
  if(want==="OUTSIDE_WIDTH_TWO"){
   ok(active.size&&[...active].every(v=>G[v].size>=3)&&r.workerAt===null&&p.relations===null,"structural refusal");
  }else{
   ok(!active.size&&p.parents.length===9&&Number.isInteger(r.workerAt)&&r.workerAt<r.t,"worker entry");
   for(let i=0;i<9;i++){
    let b=bags[i],parent=b.sep.length?Math.min(...b.sep.map(v=>bags.findIndex(x=>x.owner===v))):9;
    ok(p.parents[i]===parent,"parent");if(parent===9)roots.push(i);
    else ok(parent>i&&b.sep.every(v=>bags[parent].h.includes(v)),"separator");
    const F=D.F.filter(f=>f.h.includes(b.owner)&&f.h.every(v=>b.h.includes(v)));
    b.rows=[...E.tup(m,b.h.length)].filter(z=>F.every(f=>f.S.has(f.h.map(v=>z[b.h.indexOf(v)]).join()))).map(z=>({z,live:true}));
    local.push(b.rows.length);
   }
   // Independent oracle: compute bottom-up supports as sets of separator
   // tuples, then compare EVERY physical row flag, not just final SAT.
   for(let i=0;i<9;i++){
    let b=bags[i],j=p.parents[i];sepCounts[b.sep.length]++;
    if(j===9)continue;
    const support=new Set(b.rows.filter(x=>x.live).map(x=>b.sep.map(v=>x.z[b.h.indexOf(v)]).join()));
    let parent=bags[j];
    for(let row of parent.rows){checks++;row.live &&= support.has(b.sep.map(v=>row.z[parent.h.indexOf(v)]).join());}
   }
   for(let b of bags){
    word+="11111";for(let {z,live:flag} of b.rows)word+="011"+z.map(v=>v.toString(2).padStart(Math.ceil(Math.log2(m)),"0").split("").map(x=>"00"+x).join("")+"010").join("")+(flag?"101":"100");word+="110";
    live.push(b.rows.filter(x=>x.live).length);
   }
   const sat=roots.every(i=>live[i]>0);
   ok(sat===(models>0)&&sat===(want==="FOREST_SAT")&&p.decision===+sat,"decision oracle");
   ok(p.relations===word&&p.word.slice(190,202)==="0".repeat(12),"all physical flags "+name);
  }
  rows.push({name,m,L:raw.length,t:r.t,worker:r.workerAt===null?0:r.t-r.workerAt,status:r.status,models,local,live,roots,sepCounts,checks,relationBits:word.length,span:r.span});
  return{raw,r};
 }
 const equality=(m,a,b)=>[...E.tup(m,2)].filter(([x,y])=>x!==y).map(([x,y])=>[-(m*a+x+1),-(m*b+y+1)]);
 const clique=vs=>edges.filter(h=>h.every(v=>vs.includes(v))).map(h=>h.map(v=>-(2*v+1)));
 if(suite==="small"){
  check("empty",2,[0,0],[],"FOREST_SAT");
  check("outside-triple",2,[1,0],[[-1,-9,-17]],"FOREST_SAT");
  check("nonmonotone-star",2,[1,1],[[-1,-3],[-2,-5],[-1,-7],[-2,-9],[-1,-11],[-2,-13],[-1,-15],[-2,-17],[-4]],"FOREST_SAT");
  let c=check("nonempty-inconsistent",2,[0,1],[...equality(2,0,4),...equality(2,4,8),[-2],[-17]],"FOREST_UNSAT");ok(rows.at(-1).local.every(x=>x>0),"nonempty local");
  let pair=[...E.tup(2,3)].filter(z=>z[1]!==z[2]).map(z=>[0,4,8].map((v,i)=>-(2*v+z[i]+1)));
  pair.push([-9,-17],[-10,-18]);let p=check("joint-pair-inconsistent",2,[1,0],pair,"FOREST_UNSAT");ok(rows.at(-1).local.every(x=>x>0),"joint nonempty");
  check("disconnected-unsat",2,[0,0],[[-1,-7,-17],[-3],[-4],[-5,-13]],"FOREST_UNSAT");
  check("unary-unsat",2,[0,1],[[-1],[-2]],"FOREST_UNSAT");
  check("K4-SAT-refusal",2,[1,1],clique([0,1,2,3]),"OUTSIDE_WIDTH_TWO");ok(rows.at(-1).models>0,"refused SAT");
 }else if(suite==="joint"){
  // Centers 0,8 are not initially eligible. Leaf 1 owns a ternary bag
  // with the owner in its middle field; both separator fields are
  // nonadjacent in the sorted row layout. Later center bag owns inequality.
  const B=[...E.tup(2,3)].filter(z=>z[0]!==z[2]).map(z=>[0,1,8].map((v,i)=>-(2*v+z[i]+1)));
  for(let v=2;v<=7;v++)B.push([-1,-(2*v+1)],[-(2*v+1),-17]);
  B.push([-1,-17],[-2,-18]);
  const r=check("middle-owner-joint-unsat",2,[1,1],B,"FOREST_UNSAT");ok(rows.at(-1).local.every(x=>x>0)&&r.r.checkpoint.plan[0].join()==="1,0,8","middle owner nonempty local");
 }else if(suite==="larger"){
  let seed=0x52455823;const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  let H=[[0,4,8],[1,4,8],[2,5,6],[3,7],[0],[8],[4,8]];
  check("m3-mixed",3,[1,0,1],H.flatMap(h=>[...E.tup(3,h.length)].filter(()=>rnd()>>>24<100).map(z=>h.map((g,i)=>-(3*g+z[i]+1)))),"FOREST_SAT");
 }else if(suite==="controls"){
  let raw=E.encode(2,[1,0],[[-1,-9,-17]]),r=P.run(M,raw,100000000),controls=[];
  for(let k of [0,1,100,r.workerAt-1,r.workerAt,r.workerAt+1,r.t-1]){let x=P.run(M,raw,k);ok(x.status==="TIMEOUT"&&x.t===k,"cutoff");controls.push(k);}
  ok(P.run(M,raw,r.t).status==="FOREST_SAT","exact budget");
  let n=31,pos=new Map(),at=n+1;for(let c of E.pool(n))pos.set(c.join(),at++);
  const flip=(s,i)=>s.slice(0,i)+(s[i]==="1"?"0":"1")+s.slice(i+1),rejects=[];
  for(let [name,s] of [["empty",""],["header","1".repeat(32)+"0"],["mandatory",flip(raw,pos.get("-31"))],["late-pin",flip(raw,pos.get("-28,-30,-31"))],["truncated",raw.slice(0,-1)],["extra",raw+"1"],["invalid-positive",flip(raw,pos.get("1,17"))]]){
   let v=P.run(M,s,100000000);ok(v.status==="OUTSIDE_NORMALIZED"&&E.decode(s)===null,"refusal "+name);rejects.push({name,t:v.t});
  }
  return{suite,q:C.q,descriptorBits:C.desc.length,workerEntry:C.workerEntry,controls,rejects,exactBudget:r.t,workerAt:r.workerAt};
 }else throw Error("suite");
 return{suite,q:C.q,descriptorBits:C.desc.length,workerEntry:C.workerEntry,rows,totals:rows.reduce((a,r)=>({rawBits:a.rawBits+r.L,transitions:a.transitions+r.t,worker:a.worker+r.worker,relationBits:a.relationBits+r.relationBits,localRows:a.localRows+r.local.reduce((s,v)=>s+v,0),liveRows:a.liveRows+r.live.reduce((s,v)=>s+v,0),checks:a.checks+r.checks,sat:a.sat+ +(r.status==="FOREST_SAT"),unsat:a.unsat+ +(r.status==="FOREST_UNSAT"),refused:a.refused+ +(r.status==="OUTSIDE_WIDTH_TWO")}),{rawBits:0,transitions:0,worker:0,relationBits:0,localRows:0,liveRows:0,checks:0,sat:0,unsat:0,refused:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_TWO_ELIMINATION_OK '+JSON.stringify(audit(require('./f038_rex_width_two_elimination.js'),require('./f038_tga_normalized_integration.js').engine(),process.argv[2]||'small')));
