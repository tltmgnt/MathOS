// REX-023C2: physical masks, parent indices and physically serialized relation differential oracle.
function audit(P,E,suite="small"){
 const C=P.compile(),M=P.decode(C.desc),ok=(v,s)=>{if(!v)throw Error(s)},V=[...Array(9).keys()],scopes=[],rows=[];
 for(let k=1;k<=3;k++)for(let h of E.subsets(V,k))scopes.push(h);
 const index=new Map(scopes.map((h,i)=>[h.join(),i])),edges=scopes.filter(h=>h.length===2);
 function check(name,m,pins,B,want){
  const raw=E.encode(m,pins,B),D=E.decode(raw),r=P.run(M,raw,3000000000),p=r.checkpoint;
  ok(D&&p&&r.status===(want?"RELATIONS_PREPARED":"OUTSIDE_WIDTH_TWO"),name+" "+r.status);
  const expected=scopes.map(h=>{let f=D.F.find(f=>f.h.join()===h.join());return [...E.tup(m,h.length)].map(z=>f&&!f.S.has(z.join())?"1":"0").join("");});
  ok(p.masks.length===129&&p.masks.every((b,i)=>b===expected[i]),"mask mismatch "+name);
  ok(p.selector===raw.slice(19*m-6)&&p.pins===pins.join("")&&p.m===m&&p.ranks.join()==="0,0,0","checkpoint "+name);
  let G=V.map(()=>new Set()),active=new Set(V);
  for(let f of D.F)for(let [a,b] of E.subsets(f.h,2)){G[a].add(b);G[b].add(a);}
  ok(p.graph.join("")===edges.map(([a,b])=>+G[a].has(b)).join(""),"graph");
  let bags=[];
  for(let [v,a,b] of p.plan){
   let choices=V.filter(x=>active.has(x)&&G[x].size<=2);ok(v===choices[0],"greedy");
   let ns=[...G[v]].sort((x,y)=>x-y);ok([a,b].join()===[ns[0]??9,ns[1]??9].join(),"neighbors");
   bags.push([v,...ns]);if(ns.length===2){G[a].add(b);G[b].add(a);}
   active.delete(v);for(let x of ns)G[x].delete(v);G[v].clear();
  }
  ok(p.active===V.map(v=>+active.has(v)).join("")&&p.residual===edges.map(([a,b])=>+G[a].has(b)).join(""),"residual");
  let relations=[],expectedWord="";
  if(want){
   ok(!active.size&&p.parents.length===9,"complete");
   for(let i=0;i<9;i++){
    let h=bags[i],parent=h.length===1?9:Math.min(...h.slice(1).map(v=>bags.findIndex(b=>b[0]===v)));
    ok(p.parents[i]===parent,"physical parent "+name+":"+i);
    if(parent!==9)ok(parent>i&&h.slice(1).every(v=>bags[parent].includes(v)),"parent overlap");
    // Host-only relation oracle from the actual physical masks. Assign each
    // selected factor to the earliest-eliminated vertex in its scope.
    let owned=scopes.filter(s=>s.includes(h[0])&&s.every(v=>h.includes(v)));
    h=h.slice().sort((a,b)=>a-b);expectedWord+="11111";
    let allowed=0;
    for(let z of E.tup(m,h.length)){
     let physical=owned.every(s=>{let j=s.reduce((a,v)=>a*m+z[h.indexOf(v)],0);return p.masks[index.get(s.join())][j]==="0";});
     let direct=D.F.filter(f=>owned.some(s=>s.join()===f.h.join())).every(f=>f.S.has(f.h.map(v=>z[h.indexOf(v)]).join()));
     ok(physical===direct,"mask relation oracle");allowed+=+physical;if(direct)expectedWord+="011"+z.map(v=>v.toString(2).padStart(Math.ceil(Math.log2(m)),"0").split("").map(b=>"00"+b).join("")+"010").join("")+"101";
    }
    relations.push({scope:h,rows:allowed,candidates:m**h.length});expectedWord+="110";
   }
   ok(p.relations===expectedWord&&p.word.slice(190,202)==="0".repeat(12)&&p.groups.join()==="19,20,20","exact physical row grammar "+name);for(let f of D.F)ok(bags.some(h=>f.h.every(v=>h.includes(v))),"scope coverage");
   for(let v of V){let nodes=bags.map((b,i)=>b.includes(v)?i:-1).filter(i=>i>=0),seen=new Set([nodes[0]]);
    for(let k=0;k<9;k++)for(let i of nodes)if(nodes.includes(p.parents[i])&&(seen.has(i)||seen.has(p.parents[i]))){seen.add(i);seen.add(p.parents[i]);}
    ok(seen.size===nodes.length,"running intersection");
   }
  }else ok(active.size&&[...active].every(v=>G[v].size>=3)&&!p.parents.length&&p.relations===null,"structural refusal");
  const maskBits=p.masks.reduce((a,b)=>a+b.length,0),ones=p.masks.reduce((a,b)=>a+[...b].filter(x=>x==="1").length,0);
  ok(maskBits===9*m+36*m*m+84*m**3&&ones===new Set(B.map(c=>c.slice().sort((x,y)=>Math.abs(x)-Math.abs(y)).join())).size,"mask bits and unique ones");
  rows.push({name,m,L:raw.length,t:r.t,status:r.status,maskBits,ones,relationBits:expectedWord.length,plan:p.plan,parents:p.parents,relations,span:r.span});
  return{raw,r};
 }
 const make=(m,H)=>H.map(h=>h.map(g=>-(g*m+1)));
 const clique=vs=>edges.filter(h=>h.every(v=>vs.includes(v)));
 if(suite==="small"){
  check("empty",2,[0,0],[],true);
  check("outside-triple",2,[1,0],[[-1,-9,-17]],true);
  check("star",2,[0,1],make(2,V.slice(1).map(v=>[0,v])),true);
  check("cycle",2,[1,1],make(2,V.map(v=>[v,(v+1)%9])),true);
  check("two-triangles",2,[0,1],make(2,[[0,3,8],[1,5,7]]),true);
  check("K4",2,[1,1],make(2,clique([0,1,2,3])),false);
  check("unary-unsat",2,[0,0],[[-1],[-2]],true);
  check("owned-nonmonotone",2,[1,1],[[-1,-3],[-2,-5],[-1,-7],[-2,-9],[-1,-11],[-2,-13],[-1,-15],[-2,-17],[-4],[-6]],true);
  check("dense-all-scopes",2,[1,0],scopes.flatMap(h=>[...E.tup(2,h.length)].map(z=>h.map((g,i)=>-(2*g+z[i]+1)))),false);
 }else if(suite==="larger"){
  let seed=0x52455823;const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  let H=[[0,4,8],[1,4,8],[2,5,6],[3,7],[0],[8],[4,8]];
  check("m3-mixed",3,[1,0,1],H.flatMap(h=>[...E.tup(3,h.length)].filter(()=>rnd()>>>24<100).map(z=>h.map((g,i)=>-(3*g+z[i]+1)))),true);
 }else if(suite==="controls"){
  let raw=E.encode(2,[1,0],[[-1,-9,-17]]),n=31,pos=new Map(),at=n+1;for(let c of E.pool(n))pos.set(c.join(),at++);
  const flip=(s,i)=>s.slice(0,i)+(s[i]==="1"?"0":"1")+s.slice(i+1),controls=[];
  for(let [name,s] of [["empty",""],["header","1".repeat(32)+"0"],["mandatory",flip(raw,pos.get("-31"))],["late-pin",flip(raw,pos.get("-28,-30,-31"))],["truncated",raw.slice(0,-1)],["extra",raw+"1"],["invalid-positive",flip(raw,pos.get("1,17"))]]){
   let v=P.run(M,s,100000000);ok(v.status==="OUTSIDE_NORMALIZED"&&E.decode(s)===null,"malformed "+name);controls.push({name,t:v.t});
  }
  const t=34283828;for(let k of [0,1,100,t-1])ok(P.run(M,raw,k).status==="TIMEOUT","cutoff");ok(P.run(M,raw,t).status==="RELATIONS_PREPARED","exact halt");
  return{suite,q:C.q,descriptorBits:C.desc.length,controls,cutoffs:4,exactBudget:t};
 }else throw Error("suite");
 return{suite,q:C.q,descriptorBits:C.desc.length,rows,totals:rows.reduce((a,r)=>({rawBits:a.rawBits+r.L,transitions:a.transitions+r.t,maskBits:a.maskBits+r.maskBits,ones:a.ones+r.ones,parents:a.parents+r.parents.length,relations:a.relations+r.relations.length,relationBits:a.relationBits+r.relationBits,candidates:a.candidates+r.relations.reduce((s,x)=>s+x.candidates,0),accepted:a.accepted+ +(r.status==="RELATIONS_PREPARED")}),{rawBits:0,transitions:0,maskBits:0,ones:0,parents:0,relations:0,relationBits:0,candidates:0,accepted:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_TWO_RELATIONS_OK '+JSON.stringify(audit(require('./f038_rex_width_two_relations.js'),require('./f038_tga_normalized_integration.js').engine(),process.argv[2]||'small')));
