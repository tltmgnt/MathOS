// Complete forest differential audit, independent original-factor recurrence; observation only.
function audit(F,R,C,P,K,L,E,suite="ir"){
 const J0=F.machine(R,C,P),J=P.compact(J0),M=suite==="ir"||suite==="larger"?null:K.compile(J),G=L.compile(),D={...L.decode(G.desc),loaderEntry:G.loaderEntry,plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry};
 const ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 function reference(J,inputs,watch=null,limit=100000000){
  const T=inputs.map(s=>["L",...s,"_"]),h=inputs.map(()=>0);let pc=J.entry,steps=0,span=T.map(t=>t.length);
  const words=()=>T.map(t=>t.slice(1).join("").replace(/_+$/,""));
  for(;;){if(watch)watch(pc,T,h,steps);
   let a=J.ins[pc],k=a.t,x=T[k][h[k]]??"_";
   if(a.op==="jump"){pc=a.next;continue;}
   if(a.op==="halt"||a.op==="reject")return{status:a.op==="halt"?"COMPLETE":"REJECT",steps,tapes:words(),heads:h,span:span.reduce((a,b)=>a+b,0)};
   if(steps===limit)return{status:"TIMEOUT",steps};
   steps++;
   if(a.op==="read"){pc=a.next[J.alphabet.indexOf(x)];continue;}
   if(a.op==="write"){ok(x!=="L","sentinel");T[k][h[k]]=a.next.v;}
   else if(a.op==="move"){h[k]+=a.next.dir;ok(h[k]>=0,"left boundary");if(h[k]===T[k].length)T[k].push("_");span[k]=Math.max(span[k],h[k]+1);}
   else throw Error("opcode");pc=a.next.d;
  }
 }
 const trap=[[0,1],[0,2],[0,6],[1,3],[1,8],[2,5],[2,7],[3,6],[3,7],[3,8],[4,6],[5,8],[6,7],[7,8]],V=[0,1,2,3,4,5,6,7,8],bin=x=>x.toString(2).padStart(4,"0"),bitmap=h=>V.map(v=>+h.includes(v)).join("");
 function parity(consistent){
  let B=[];for(let [x,a,b] of E.tup(2,3))if(x!==(a^b))B.push([-(x+1),-(6+a+1),-(10+b+1)]);
  for(let [x,c] of E.tup(2,2))if(x!==c)B.push([-(x+1),-(16+c+1)]);
  for(let [a,b,c] of E.tup(2,3))if((a^b^c)!==(consistent?0:1))B.push([-(6+a+1),-(10+b+1),-(16+c+1)]);
  return B;
 }
 function check(name,m,pins,B,want){
  const raw=E.encode(m,pins,B),p=L.run(D,raw,5000000000,null,true),d=E.decode(raw);
  ok(p.status==="MASK_STREAM_LOADED","producer "+name);
  const at=p.snapshot.indexOf("H"),suffix=p.snapshot.slice(at,at+851).replaceAll("_","b"),stream=p.snapshot.slice(at+851,at+851+p.stream.length);
  ok(stream===p.stream,"literal stream");
  const input=[...Array(19).fill(""),suffix,stream,...Array(24).fill("")],w=Math.ceil(Math.log2(m)),encode=z=>z.map(x=>x.toString(2).padStart(w,"0")).join(",")+";",word=rows=>rows.map(encode).join("");
  const frames=p.checkpoint.frames.slice(0,9),order=frames.map(f=>f.choice),bags=frames.map((f,i)=>{
   const sep=f.neighbors.filter(v=>v!==9),h=[f.choice,...sep].sort((a,b)=>a-b),owned=d.F.filter(f=>Math.min(...f.h.map(g=>order.indexOf(g)))===i);
   ok(owned.every(f=>f.h.every(v=>h.includes(v))),"owner coverage");
   const local=[...E.tup(m,h.length)].filter(z=>owned.every(f=>f.S.has(f.h.map(g=>z[h.indexOf(g)]).join())));
   return{v:f.choice,h,sep,parent:f.parent,local,live:local.slice()};
  });
  const expectedMeta=frames.map(f=>bin(f.choice)+f.neighbors.map(bin).join("")+bin(f.parent)).join(""),expectedTable=V.map(v=>bitmap(bags[order.indexOf(v)].h)).join("");
  let local=0,edges=0,edgeRows=[],lastLocal=0,lastJoin=0,loopCount=0;
  const text=t=>t.slice(1).join("").replace(/_+$/,"");
  const a=reference(J0,input,(pc,T,heads,steps)=>{
   if(pc===J0.localDone){
    const bag=bags[local];ok(bag&&text(T[17])===word(bag.local)&&text(T[33])===bin(bag.v),"local output "+name+":"+local);
    local++;lastLocal=steps;
   }
   if(pc===J0.edge)loopCount++;
   if(pc===J0.afterJoin){
    const i=bags.findIndex(b=>b.v===parseInt(text(T[10]).slice(0,4),2)),b=bags[i],j=order.indexOf(b.parent),par=bags[j];
    ok(j>i,"edge order");const proj=(h,z)=>b.sep.map(v=>z[h.indexOf(v)]).join(),support=new Set(b.live.map(z=>proj(b.h,z)));
    const pm=par.h.map(g=>+b.sep.includes(g)).join(""),cm=b.h.map(g=>+b.sep.includes(g)).join("");
    ok(text(T[41])===pm&&text(T[42])===cm,"joint masks");
    par.live=par.live.filter(z=>support.has(proj(par.h,z))).sort((a,b0)=>{for(let g of b.sep){let delta=a[par.h.indexOf(g)]-b0[par.h.indexOf(g)];if(delta)return delta;}return 0;});
    ok(text(T[43])===word(par.live),"retained output "+name+":"+i);
    ok(text(T[22+b.v])===word(b.live),"child preservation");
    edgeRows.push({child:b.v,parent:b.parent,separator:b.sep.length,keys:support.size,retained:par.live.length});
    edges++;lastJoin=steps;
   }
  });
  const b=reference(J,input);
  ok(a.status==="COMPLETE"&&JSON.stringify(a)===JSON.stringify(b),"exact compact IR "+name);
  ok(local===9&&edges===bags.filter(b=>b.parent!==9).length&&loopCount===10,"complete forest traversal");
  ok(b.tapes[31]===expectedMeta&&b.tapes[32]===expectedTable&&b.tapes[21]==="111111111","metadata/order");
  ok(bags.every(x=>b.tapes[22+x.v]===word(x.live)),"final retained relations");
  ok(b.tapes[19]===suffix&&b.tapes[20]===stream,"literal sources preserved");
  let models=0;for(let z of E.tup(m,9))if(d.F.every(f=>f.S.has(f.h.map(g=>z[g]).join())))models++;
  ok(b.tapes[44]===String(+want)&&want===(models>0)&&want===bags.filter(b=>b.parent===9).every(b=>b.live.length>0),"root decision "+name);
  let t=null,span=null;
  if(M){
   let r=K.run(M,K.encode(M,J,input),10000000000);
   ok(r.status==="COMPLETE"&&r.tapes.join("|")===b.tapes.join("|")&&r.heads.join()===b.heads.join(),"physical "+name+" "+JSON.stringify({status:r.status,t:r.t}));t=r.t;span=r.span;
  }
  rows.push({name,m,producer:p.t,models,decision:b.tapes[44],primitives:b.steps,virtualSpan:b.span,localEnd:lastLocal,lastJoin,edges,candidates:bags.reduce((n,x)=>n+m**x.h.length,0),localRows:bags.reduce((n,x)=>n+x.local.length,0),liveRows:bags.reduce((n,x)=>n+x.live.length,0),t,span,edgeRows});
  return{input,b};
 }
 const B=[[-1,-3,-5],[-2,-4,-7],[-1,-6,-8],[-3,-5,-7],[-2],[-1,-4]];
 if(suite==="ir"){
  check("empty",2,[0,0],[],true);
  check("four-bag-triples",2,[1,0],B,true);
  check("greedy-trap",2,[0,1],trap.map(h=>h.map(v=>-(2*v+1))),true);
  let a=check("joint-three-UNSAT",2,[0,1],parity(false),false);
  ok(rows.at(-1).edgeRows[0].separator===3&&rows.at(-1).edgeRows[0].keys===4&&rows.at(-1).edgeRows[0].retained===0,"parity obstruction");
  check("joint-three-SAT",2,[1,0],parity(true),true);
  check("disconnected-UNSAT",2,[0,0],parity(true).concat([[-3],[-4]]),false);
  check("unary-UNSAT",2,[1,1],[[-1],[-2]],false);
  const bad=[a.input.map((s,i)=>i===19?"":s),a.input.map((s,i)=>i===20?"11":s)];
  for(let input of bad)ok(reference(J,input).status==="REJECT","malformed");
  for(let k of [0,1,100,a.b.steps-1])ok(reference(J,a.input,null,k).status==="TIMEOUT","IR cutoff");
 }else if(suite==="larger"){
  check("m3-mixed",3,[1,0,1],[[-1,-4,-7],[-2,-6,-10],[-3,-8,-11],[-4,-7,-10],[-1],[-5,-9]],true);
  check("m3-greedy-trap",3,[1,1,0],trap.map(h=>h.map(v=>-(3*v+1))),true);
 }else if(suite==="physicalEmpty")check("empty",2,[0,0],[],true);
 else if(suite==="physicalEdge")check("empty-child-edge",2,[1,0],[[-1],[-2],[-1,-3]],false);
 else if(suite==="physicalEdgeSAT")check("nonempty-child-edge",2,[0,1],[[-1,-3]],true);
 else if(suite==="physicalParity")check("joint-three-UNSAT",2,[0,1],parity(false),false);
 else if(suite==="physicalSAT")check("four-bag-triples",2,[1,0],B,true);
 else throw Error("suite");
 return{suite,ir:J.stats,q:M?.q??null,logical:M?.logicalStates??null,roots:M?.logicalRoots??null,interned:M?.interned??null,bits:M?4+M.q+3*M.q*(M.q.toString(2).length+4):null,rows,totals:rows.reduce((a,r)=>({producer:a.producer+r.producer,primitives:a.primitives+r.primitives,edges:a.edges+r.edges,candidates:a.candidates+r.candidates,localRows:a.localRows+r.localRows,liveRows:a.liveRows+r.liveRows,transitions:a.transitions+(r.t??0)}),{producer:0,primitives:0,edges:0,candidates:0,localRows:0,liveRows:0,transitions:0})};
}
module.exports={audit};
if(require.main===module){const F=require('./f038_rex_width_three_forest_ir.js'),R=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),P=require('./f038_rex_width_three_projection.js'),K={...require('./f038_rex_width_three_compiler.js'),...require('./f038_rex_width_three_row_compiler.js')},L=require('./f038_rex_width_three_direct_loader.js'),E=require('./f038_tga_normalized_integration.js').engine();console.log('F038_REX_WIDTH_THREE_FOREST_OK '+JSON.stringify(audit(F,R,C,P,K,L,E,process.argv[2]||'ir')));}
