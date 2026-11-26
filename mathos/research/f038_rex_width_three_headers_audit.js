// Independent metadata and canonical scope oracle on actual C1 snapshots; suffix handoff only.
function audit(H,P,K,C,E,suite="physical"){
 const J0=H.machine(),J=P.compact(J0),M=suite==="physical"?K.compile(J):null,G=C.compile(),producer={...C.decode(G.desc),plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry};
 const ok=(v,s)=>{if(!v)throw Error(s)},V=[...Array(9).keys()],scopes=[1,2,3].flatMap(k=>[...E.subsets(V,k)]),rows=[],bin=(v,n=4)=>v.toString(2).padStart(n,"0"),bitmap=h=>V.map(v=>+h.includes(v)).join("");
 function ref(J,input){
  const tapes=[["L",...input,"_"],...Array.from({length:8},()=>["L","_"])],heads=Array(9).fill(0);
  let pc=J.entry,steps=0;
  while(true){
   let I=J.ins[pc],k=I.t,a=tapes[k][heads[k]]??"_";
   if(I.op==="halt"||I.op==="reject")return{status:I.op==="halt"?"COMPLETE":"REJECT",steps,tapes:tapes.map(t=>t.slice(1).join("").replace(/_+$/,"")),heads};
   if(I.op==="jump"){pc=I.next;continue;}
   steps++;
   if(I.op==="read"){pc=I.next[J.alphabet.indexOf(a)];continue;}
   if(I.op==="write"){ok(a!=="L"&&I.next.v!=="L","sentinel write");tapes[k][heads[k]]=I.next.v;}
   else if(I.op==="move"){heads[k]+=I.next.dir;ok(heads[k]>=0,"left boundary");if(heads[k]===tapes[k].length)tapes[k].push("_");}
   else throw Error("opcode");
   pc=I.next.d;
  }
 }
 const equal=(a,b)=>a.status===b.status&&(a.status==="REJECT"||a.tapes.join("\n")===b.tapes.join("\n")&&a.heads.join()===b.heads.join());
 const make=(m,H)=>H.map(h=>h.map(v=>-(m*v+1))),clique=vs=>[...E.subsets(vs,2)];
 const trap=[[0,1],[0,2],[0,6],[1,3],[1,8],[2,5],[2,7],[3,6],[3,7],[3,8],[4,6],[5,8],[6,7],[7,8]];
 function check(name,m,pins,B,admitted=true){
  const raw=E.encode(m,pins,B),p=C.run(producer,raw,3000000000,null,true),D=E.decode(raw);
  ok(p.status===(admitted?"WIDTH_THREE_FACTORS":"OUTSIDE_WIDTH_THREE"),"producer "+name);
  // Only copy the contiguous right-of-halt suffix, changing blank glyphs.
  // No host-created fields, tuple records, masks, or scope IDs enter IR.
  const input=p.snapshot.slice(p.snapshot.indexOf("H")).replaceAll("_","b");
  const a=ref(J0,input),b=ref(J,input);
  ok(equal(a,b)&&a.steps===b.steps,"exact IR quotient "+name);
  ok(b.status===(admitted?"COMPLETE":"REJECT"),"IR status "+name);
  let t=null,span=null;
  if(M){let r=K.run(M,K.encode(M,J,[input,...Array(8).fill("")]),3000000000);ok(equal(b,r),"physical terminal configuration "+name+" "+r.status);t=r.t;span=r.span;}
  let owned=0,edges=0,headers="",routes="",ids="",table="";
  if(admitted){
   let frames=p.checkpoint.frames.slice(0,9),order=frames.map(f=>f.choice),bags=frames.map(f=>[f.choice,...f.neighbors.filter(v=>v!==9)].sort((a,b)=>a-b));
   const ownerByScope=new Map();
   for(let i=0;i<9;i++){
    let f=frames[i],h=bags[i],sep=f.neighbors.filter(v=>v!==9),v=f.choice,[a,b,c]=f.neighbors,slots=[[v],[v,a],[v,b],[v,c],[v,a,b],[v,a,c],[v,b,c]];
    headers+=bin(v)+f.neighbors.map(n=>bin(n)).join("")+bin(f.parent)+f.owned+bitmap(h)+bitmap(sep);
    let child=h.map(g=>+sep.includes(g)).join(""),parent="";
    if(f.parent!==9){let j=order.indexOf(f.parent);ok(j>i&&sep.every(g=>bags[j].includes(g)),"parent coverage");parent=bags[j].map(g=>+sep.includes(g)).join("");edges++;}
    routes+=bin(v)+bin(f.parent)+child+":"+parent+";";
    for(let slot=0;slot<7;slot++){
     let g=slots[slot].slice().sort((a,b)=>a-b),id=g.includes(9)?255:scopes.findIndex(s=>s.join()===g.join());
     ok((id!==255)===Boolean(+f.owned[slot])&&id>=0,"slot grammar");ids+=bin(id,8);
     if(id!==255){owned++;ok(!ownerByScope.has(id),"duplicate owner");ownerByScope.set(id,i);}
    }
   }
   for(let v of V)table+=bitmap(bags[order.indexOf(v)]);
   for(let f of D.F){let id=scopes.findIndex(h=>h.join()===f.h.join());ok(ownerByScope.get(id)===Math.min(...f.h.map(v=>order.indexOf(v))),"original exact factor ownership");}
   ok(b.tapes[1]===headers&&b.tapes[4]===table&&b.tapes[6]===routes&&b.tapes[7]===ids&&b.tapes[0]===input,"physical metadata streams "+name);
  }
  rows.push({name,m,producer:p.t,inputSymbols:input.length,primitives:b.steps,t,span,status:b.status,owned,edges,routeBits:routes.length,scopeBits:ids.length});
  return{input,b};
 }
 let cutoffs=[],malformed=[];
 if(suite==="physical"){
  const a=check("greedy-trap",2,[0,1],make(2,trap));
  check("empty",2,[0,0],[]);
  check("K5-refusal",2,[1,1],make(2,clique([0,1,2,3,4])),false);
  let raw=K.encode(M,J,[a.input,...Array(8).fill("")]);
  for(let n of [0,1,100,500000000]){let r=K.run(M,raw,n);ok(r.status==="TIMEOUT"&&r.t===n,"cutoff");cutoffs.push(n);}
 }else if(suite==="ir"){
  check("K4",2,[1,0],make(2,clique([0,1,2,3])));
  check("nonconsecutive-triples",2,[1,1],[[-1,-9,-17],[-3,-7,-15]]);
  let a=check("m3-greedy-trap",3,[1,0,1],make(3,trap));
  check("subdivided-K5",2,[1,0],make(2,clique([0,1,2,3,4]).filter(h=>h.join()!=="0,1").concat([[0,5],[1,5]])),false);
  for(let input of ["",a.input.replace("H","b"),a.input.slice(0,55),a.input.slice(0,84)+"1"+a.input.slice(85),a.input.slice(0,85)+"0"+a.input.slice(86)]){
   let r=ref(J,input);ok(r.status==="REJECT","malformed");malformed.push(r.steps);
  }
 }else throw Error("suite");
 return{suite,ir:J.stats,q:M?.q??null,logical:M?.logicalStates??null,bits:M?4+M.q+3*M.q*(M.q.toString(2).length+4):null,rows,cutoffs,malformed,totals:rows.reduce((a,r)=>({producer:a.producer+r.producer,primitives:a.primitives+r.primitives,transitions:a.transitions+(r.t??0),owned:a.owned+r.owned,edges:a.edges+r.edges}),{producer:0,primitives:0,transitions:0,owned:0,edges:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_HEADERS_OK '+JSON.stringify(audit(require('./f038_rex_width_three_headers.js'),require('./f038_rex_width_three_projection.js'),require('./f038_rex_width_three_compiler.js'),require('./f038_rex_width_three_factors.js'),require('./f038_tga_normalized_integration.js').engine(),process.argv[2]||'physical')));
