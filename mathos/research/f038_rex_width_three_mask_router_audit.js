// Independent original-factor/config oracle: literal D2C stream and header suffix only.
function audit(A,C,P,K,L,E,suite="ir"){
 const J0=A.machine(C),J=P.compact(J0),M=suite==="ir"?null:K.compile(J),G=L.compile(),D={...L.decode(G.desc),loaderEntry:G.loaderEntry,plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry};
 const ok=(v,s)=>{if(!v)throw Error(s)},V=[0,1,2,3,4,5,6,7,8],scopes=[1,2,3].flatMap(k=>[...E.subsets(V,k)]),rows=[],runs=[];
 function reference(J,inputs){
  const T=inputs.map(s=>["L",...s,"_"]),h=inputs.map(()=>0);let pc=J.entry,steps=0;
  while(steps<100000000){let a=J.ins[pc],k=a.t,x=T[k][h[k]]??"_";
   if(a.op==="jump"){pc=a.next;continue;}if(a.op==="halt"||a.op==="reject")return{status:a.op==="halt"?"COMPLETE":"REJECT",steps,tapes:T.map(t=>t.slice(1).join("").replace(/_+$/,"")),heads:h};
   steps++;if(a.op==="read"){pc=a.next[J.alphabet.indexOf(x)];continue;}
   if(a.op==="write"){ok(x!=="L","sentinel");T[k][h[k]]=a.next.v;}
   else if(a.op==="move"){h[k]+=a.next.dir;ok(h[k]>=0,"left boundary");if(h[k]===T[k].length)T[k].push("_");}else throw Error("opcode");pc=a.next.d;
  }throw Error("IR timeout");
 }
 const trap=[[0,1],[0,2],[0,6],[1,3],[1,8],[2,5],[2,7],[3,6],[3,7],[3,8],[4,6],[5,8],[6,7],[7,8]];
 function check(name,m,pins,clauses,physicalIndices){
  const raw=E.encode(m,pins,clauses),p=L.run(D,raw,5000000000,null,true),d=E.decode(raw);ok(p.status==="MASK_STREAM_LOADED","producer "+name);
  const h=p.snapshot.indexOf("H"),suffix=p.snapshot.slice(h,h+851).replaceAll("_","b"),stream=p.snapshot.slice(h+851,h+851+p.stream.length);
  ok(stream===p.stream&&suffix.length===851,"literal source");
  const masks=scopes.map(s=>{const f=d.F.find(f=>f.h.join()===s.join());return [...E.tup(m,s.length)].map(z=>+(!!f&&!f.S.has(z.join()))).join("");});
  const w=Math.ceil(Math.log2(m));let begin=rows.length;
  for(let i=0;i<9;i++){
   if(M&&!physicalIndices.includes(i))continue;
   const f=p.checkpoint.frames[i],v=f.choice,ns=f.neighbors.filter(x=>x!==9),bag=[v,...ns].sort((a,b)=>a-b),[a,b,c]=ns,slots=[[v],[v,a],[v,b],[v,c],[v,a,b],[v,a,c],[v,b,c]];
   const ids=slots.map(s=>s.includes(undefined)?255:scopes.findIndex(h=>h.join()===s.slice().sort((a,b)=>a-b).join()));
   const config=[(m-1).toString(2).split("").reverse().join(""),"1".repeat(bag.length),slots.map((s,j)=>ids[j]===255?"0000":bag.map(g=>+s.includes(g)).join("").padEnd(4,"0")).join(""),...ids.map(k=>k===255?"":masks[k])];
   const direct=d.F.filter(f=>f.h.includes(v)&&f.h.every(g=>bag.includes(g)));
   const allowed=[...E.tup(m,bag.length)].filter(z=>direct.every(f=>f.S.has(f.h.map(g=>z[bag.indexOf(g)]).join()))),output=allowed.map(z=>z.map(x=>x.toString(2).padStart(w,"0")).join(",")+";").join("");
   // Only the literal header suffix, literal encoded mask stream, and
   // bag ordinal enter the machine. No derived config enters it.
   const input=[...Array(19).fill(""),suffix,stream,"1".repeat(i)];
   const a0=reference(J0,input),b0=reference(J,input);
   ok(a0.status==="COMPLETE"&&JSON.stringify(a0)===JSON.stringify(b0),"exact IR quotient "+name+":"+i);
   ok(b0.tapes.slice(0,10).join("|")===config.join("|")&&b0.tapes[17]===output&&b0.tapes.slice(19).join("|")===input.slice(19).join("|"),"exact route/tuples "+name+":"+i);
   let t=null,span=null;
   if(M){
    const r=K.run(M,K.encode(M,J,input),3000000000);
    ok(r.status==="COMPLETE"&&r.tapes.join("|")===b0.tapes.join("|")&&r.heads.join()===b0.heads.join(),"physical "+name+":"+i+" "+JSON.stringify({status:r.status,t:r.t}));t=r.t;span=r.span;
   }
   rows.push({name,m,i,owner:v,arity:bag.length,ids,maskBits:config.slice(3).join("").length,candidates:m**bag.length,allowed:allowed.length,primitives:b0.steps,t,span});
  }
  runs.push({name,producer:p.t,rows:rows.length-begin});
  return{suffix,stream};
 }
 const B=[[-1,-3,-5],[-2,-4,-7],[-1,-6,-8],[-3,-5,-7],[-2],[-1,-4]];
 if(suite==="physical")check("four-bag-triples",2,[1,0],B,[0,8]);
 else if(suite==="physicalTrap")check("greedy-trap",2,[0,1],trap.map(h=>h.map(v=>-(2*v+1))),[3]);
 else if(suite==="physical3")check("m3-mixed",3,[1,0,1],[[-1,-4,-7],[-2,-6,-10],[-3,-8,-11],[-4,-7,-10],[-1],[-5,-9]],[0]);
 else if(suite==="ir"){
  const a=check("four-bag-triples",2,[1,0],B,[]);
  check("greedy-trap",2,[0,1],trap.map(h=>h.map(v=>-(2*v+1))),[]);
  check("m3-mixed",3,[1,0,1],[[-1,-4,-7],[-2,-6,-10],[-3,-8,-11],[-4,-7,-10],[-1],[-5,-9]],[]);
  const bad=[["",a.stream,""],[a.suffix,"11",""],[a.suffix,a.stream,"111111111"],[a.suffix.slice(0,59),a.stream,""],[a.suffix.slice(0,60)+"0"+a.suffix.slice(61),a.stream,""]];
  for(let [h,q,k] of bad)ok(reference(J,[...Array(19).fill(""),h,q,k]).status==="REJECT","malformed control");
 }else throw Error("suite");
 return{suite,ir:J.stats,q:M?.q??null,logical:M?.logicalStates??null,bits:M?4+M.q+3*M.q*(M.q.toString(2).length+4):null,runs,rows,totals:rows.reduce((a,r)=>({maskBits:a.maskBits+r.maskBits,candidates:a.candidates+r.candidates,allowed:a.allowed+r.allowed,primitives:a.primitives+r.primitives,transitions:a.transitions+(r.t??0)}),{maskBits:0,candidates:0,allowed:0,primitives:0,transitions:0})};
}
module.exports={audit};
if(require.main===module){const A=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),P=require('./f038_rex_width_three_projection.js'),K={...require('./f038_rex_width_three_compiler.js'),...require('./f038_rex_width_three_local_compiler.js')},L=require('./f038_rex_width_three_direct_loader.js'),E=require('./f038_tga_normalized_integration.js').engine();console.log('F038_REX_WIDTH_THREE_MASK_ROUTER_OK '+JSON.stringify(audit(A,C,P,K,L,E,process.argv[2]||'ir')));}
