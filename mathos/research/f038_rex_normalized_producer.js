// REX-021 host-side normalized F038 producer and exact structural coverage audit.
function plan(n,scopes){
 const G=Array.from({length:n},()=>new Set());
 for(let h of scopes)for(let a of h)for(let b of h)if(a!==b)G[a].add(b);
 let alive=new Set(G.keys()),history=[];
 while(alive.size>3){
  let v=[...alive].find(a=>G[a].size<=2);if(v===undefined)return null;
  let h=[...G[v]].sort((a,b)=>a-b);history.push([v,h]);
  for(let a of h){G[a].delete(v);for(let b of h)if(a!==b)G[a].add(b);}
  alive.delete(v);G[v].clear();
 }
 let root={k:3,scope:[...alive],children:[],factors:[]},bags=[root];
 for(let [v,h] of history.reverse()){
  let parent=bags.find(b=>h.every(a=>b.scope.includes(a)));
  if(!parent)throw Error("fill edge not covered");
  let k=[[0,1],[0,2],[1,2]].findIndex(p=>h.every(a=>p.some(i=>parent.scope[i]===a)));
  if(k<0)throw Error("pair");
  let b={k,scope:[...[[0,1],[0,2],[1,2]][k].map(i=>parent.scope[i]),v],children:[],factors:[]};
  parent.children.push(b);bags.push(b);
 }
 return {root,bags};
}
function produce(D,E){
 let p=plan(9,D.F.map(f=>f.h));if(!p)return null;
 for(let f of D.F){let bs=p.bags.filter(b=>f.h.every(g=>b.scope.includes(g)));if(!bs.length)throw Error("uncovered factor");for(let b of bs)b.factors.push(f);}
 let w=Math.ceil(Math.log2(D.m)),candidates=0,checks=0,rows=0;
 for(let b of p.bags){
  b.rows=[];
  for(let z of E.tup(D.m,3)){
   candidates++;let pass=true;
   for(let f of b.factors){checks++;if(!f.S.has(f.h.map(g=>z[b.scope.indexOf(g)]).join(",")))pass=false;}
   if(pass){b.rows.push([...z.map(a=>a.toString(2).padStart(w,"0")),1]);rows++;}
  }
 }return {...p,candidates,checks,rows};
}
function decodeCertificate(p,out,m){
 let at=0,z=Array(9).fill(-1),seen=0;
 function visit(b){
  let s=out.slice(at,at+b.rows.length);at+=b.rows.length;
  if(s.length!==b.rows.length||!/^[01]+$/.test(s)||s.split("1").length!==2)throw Error("bad row certificate");
  let row=b.rows[s.indexOf("1")];seen++;
  for(let i=0;i<3;i++){let g=b.scope[i],a=parseInt(row[i],2);if(a>=m||z[g]!==-1&&z[g]!==a)throw Error("coordinate conflict");z[g]=a;}
  for(let c of b.children)visit(c);
 }visit(p.root);
 if(at!==out.length||seen!==7||z.some(a=>a<0))throw Error("incomplete certificate");return z;
}
function exactWidth2(n,edges){
 let base=Array(n).fill(0);for(let [a,b] of edges){base[a]|=1<<b;base[b]|=1<<a;}
 function rec(G,S){
  if((S&(S-1))===0)return true;
  for(let v=0;v<n;v++)if(S>>v&1){
   let h=G[v]&S,ns=[];for(let a=0;a<n;a++)if(h>>a&1)ns.push(a);
   if(ns.length>2)continue;
   let H=G.slice();if(ns.length===2){H[ns[0]]|=1<<ns[1];H[ns[1]]|=1<<ns[0];}
   if(rec(H,S^(1<<v)))return true;
  }return false;
 }return rec(base,(1<<n)-1);
}
function checkPlan(n,edges,p){
 let seen=new Set(),scopeEdges=new Set(),count=0;
 function visit(b,parent){
  if(b.scope.length!==3||new Set(b.scope).size!==3)throw Error("bag");
  if(parent){let pair=[[0,1],[0,2],[1,2]][b.k].map(i=>parent.scope[i]);if(pair[0]!==b.scope[0]||pair[1]!==b.scope[1]||seen.has(b.scope[2]))throw Error("fresh");seen.add(b.scope[2]);}
  else for(let a of b.scope)seen.add(a);
  for(let a of b.scope)for(let c of b.scope)if(a<c)scopeEdges.add(a+","+c);count++;
  for(let c of b.children)visit(c,b);
 }visit(p.root,null);
 if(count!==n-2||seen.size!==n||edges.some(e=>!scopeEdges.has(e.join(","))))throw Error("coverage");
}
function audit(E,A){
 const ok=(v,s)=>{if(!v)throw Error(s)},edges=[...E.subsets([...Array(6).keys()],2)];
 let graphs={tested:0,admitted:0,rejected:0,seededNine:0,admittedNine:0};
 for(let mask=0;mask<1<<edges.length;mask++){
  let e=edges.filter((_,i)=>mask>>i&1),p=plan(6,e),truth=exactWidth2(6,e);
  ok(!!p===truth,"graph oracle");if(p)checkPlan(6,e,p);graphs.tested++;graphs.admitted+=+!!p;graphs.rejected+=+!p;
 }
 let seed=0x52455821,rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0,all9=[...E.subsets([...Array(9).keys()],2)];
 for(let i=0;i<256;i++){
  let e=all9.filter(()=>rand()>>>24<(i%8)*32),p=plan(9,e);ok(!!p===exactWidth2(9,e),"nine graph");if(p)checkPlan(9,e,p);graphs.seededNine++;graphs.admittedNine+=+!!p;
 }
 const J=A.worker(),M=A.compile(J.rules,J.symbols,J.projection),counts={normalized:0,admitted:0,rejected:0,sat:0,unsat:0,rejectedSat:0,rejectedUnsat:0,rawBits:0,preparedBits:0,candidates:0,checks:0,rows:0,referenceAssignments:0,logicalCases:0,logical:0,hostOnly:0,physicalCases:0,physicalSteps:0,physicalSat:0,physicalUnsat:0,malformed:0},results=[];
 const mk=(m,h,z)=>h.map((g,i)=>-(g*m+z[i]+1));
 function run(m,name,B,physical=false){
  let pins=Array.from({length:m},(_,i)=>(i+name.length)%2),raw=E.encode(m,pins,B),D=E.decode(raw);ok(D&&D.pins.join()===pins.join(),"raw decode");
  let first=null,count=0;
  for(let z of E.tup(m,9)){counts.referenceAssignments++;if(B.every(c=>!c.every(x=>z[Math.floor((-x-1)/m)]===(-x-1)%m))){count++;if(!first)first=z;}}
  let p=produce(D,E);counts.normalized++;counts.rawBits+=raw.length;
  if(!p){counts.rejected++;counts[count?"rejectedSat":"rejectedUnsat"]++;results.push({m,name,status:"OUTSIDE_WIDTH_TWO",models:count,L:raw.length});return;}
  counts.admitted++;counts[count?"sat":"unsat"]++;
  let N=A.encode(p.root);counts.preparedBits+=N.length;counts.candidates+=p.candidates;counts.checks+=p.checks;counts.rows+=p.rows;
  // Large dense fixtures: verify the produced local predicates directly on every global tuple,
  // rather than treating a bounded physical/logical simulation as complete.
  if(m>2&&!physical){
   let rows=p.bags.map(b=>new Set(b.rows.map(r=>r.slice(0,3).map(s=>parseInt(s,2)).join(","))));
   let verified=0;for(let z of E.tup(m,9)){let truth=B.every(c=>!c.every(x=>z[Math.floor((-x-1)/m)]===(-x-1)%m));let got=p.bags.every((b,i)=>rows[i].has(b.scope.map(g=>z[g]).join(",")));ok(got===truth,"producer exact");verified++;}
   counts.hostOnly++;results.push({m,name,status:"HOST_PRODUCER_ONLY",models:count,L:raw.length,N:N.length,rows:p.rows,verified});return;
  }
  let r=A.logical(J,N,30000000),sat=r.state==="ready";
  ok(r.state===(count?"ready":"reject"),"logical status "+name+":"+r.state);
  counts.logicalCases++;counts.logical+=r.t;
  let z=null;if(sat){z=decodeCertificate(p,r.out,m);ok(E.valid(raw,E.witness(m,D.pins,z)),"original witness");}
  let steps=null;
  if(physical){
   let q=A.physical(M,N,120000000);ok(q.state===M.q&&q.logical===r.t,"physical clock "+m+":"+name+":"+JSON.stringify({steps:q.t,state:q.state,logical:q.logical,expected:r.t}));
   if(sat){let out=Array.from({length:p.rows},(_,i)=>q.tape.get(q.head+i)).join("");ok(q.tape.size===p.rows&&out===r.out&&E.valid(raw,E.witness(m,D.pins,decodeCertificate(p,out,m))),"physical witness");}
   else ok(!q.tape.has(q.head),"physical rejection");
   counts.physicalCases++;counts.physicalSteps+=q.t;counts[sat?"physicalSat":"physicalUnsat"]++;steps=q.t;
  }
  results.push({m,name,status:sat?"SAT":"UNSAT",models:count,L:raw.length,N:N.length,rows:p.rows,logical:r.t,physical:steps,z});
 }
 for(let m of [2,3,4]){
  let path=Array.from({length:7},(_,i)=>[i,i+1,i+2]),star=Array.from({length:7},(_,i)=>[0,1,i+2]),cycle=Array.from({length:9},(_,i)=>[i,(i+1)%9].sort((a,b)=>a-b));
  for(let [name,H] of [["path",path],["star",star],["cycle",cycle],["empty",[]],["K4",[...E.subsets([0,1,2,3],2)]],["K9",all9]])run(m,name,H.map(h=>mk(m,h,h.map(()=>m-1))));
  let forced=[];for(let g=0;g<9;g++)for(let a=0;a<m-1;a++)forced.push(mk(m,[g],[a]));
  run(m,"forced",forced.concat(path.map(h=>mk(m,h,h.map(()=>0)))),true);
  run(m,"forced-unsat",forced.concat([mk(m,[8],[m-1])]),true);
  run(m,"wide-forced",forced.concat(all9.map(h=>mk(m,h,[0,0]))));
 }
 let B=[...E.subsets([0,1,2,3],2)].map(h=>mk(2,h,[0,0])),raw=E.encode(2,[0,1],B);
 ok(E.solveRaw(raw).status==="SAT"&&!produce(E.decode(raw),E),"coverage obstruction");
 let good=E.encode(2,[0,1],[]),j=good.indexOf("0")+2;
 for(let bad of [good.slice(1),good+"0",good.slice(0,-1),good.slice(0,-1)+"2",good.slice(0,j)+"1"+good.slice(j+1),""]){ok(E.decode(bad)===null,"malformed");counts.malformed++;}
 return {graphs,counts,results,descriptorBits:M.desc.length};
}
function solveRaw(raw,E,A,{mode="logical",limit=30000000}={}){
 if(mode!=="logical"&&mode!=="physical")throw Error("mode");
 let D=E.decode(raw);if(!D)return {status:"OUTSIDE_NORMALIZED"};
 let p=produce(D,E);if(!p)return {status:"OUTSIDE_WIDTH_TWO"};
 let N=A.encode(p.root),J=A.worker(),r,output,steps;
 if(mode==="logical"){
  r=A.logical(J,N,limit);steps=r.t;
  if(r.state==="reject")return {status:"UNSAT",preparedBits:N.length,steps,mode};
  if(r.state!=="ready")return {status:"TIMEOUT",preparedBits:N.length,steps,mode};
  output=r.out;
 }else{
  let M=A.compile(J.rules,J.symbols,J.projection);r=A.physical(M,N,limit);steps=r.t;
  if(r.state!==M.q)return {status:"TIMEOUT",preparedBits:N.length,steps,mode};
  if(!r.tape.has(r.head))return {status:"UNSAT",preparedBits:N.length,steps,mode};
  output=Array.from({length:p.rows},(_,i)=>r.tape.get(r.head+i)).join("");
 }
 let z=decodeCertificate(p,output,D.m),bits=E.witness(D.m,D.pins,z);
 if(!E.valid(raw,bits))throw Error("original clause verification");
 return {status:"SAT",preparedBits:N.length,steps,mode,z,bits};
}
module.exports={plan,produce,decodeCertificate,solveRaw,audit};
if(require.main===module){const E=require('./f038_tga_normalized_integration.js').engine();const A=require('./f038_rex_nested_variable_overlap.js');if(process.argv.includes('--solve'))console.log(JSON.stringify(solveRaw(require('fs').readFileSync(0,'utf8'),E,A,{mode:process.argv.includes('--physical')?'physical':'logical'})));else console.log('F038_REX_NORMALIZED_PRODUCER_OK '+JSON.stringify(audit(E,A)));}
