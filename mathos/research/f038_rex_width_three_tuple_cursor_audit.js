// Independent original-factor oracle plus observation of every candidate's mask-head invariant.
function audit(A,P,K,L,E,suite="physical"){
 const J0=A.machine(),J=P.compact(J0),M=suite==="physical"||suite==="physical3"?K.compile(J):null,ok=(v,s)=>{if(!v)throw Error(s)},V=[0,1,2,3,4,5,6,7,8],scopes=[1,2,3].flatMap(k=>[...E.subsets(V,k)]),rows=[];
 function reference(J,inputs,watch){
  const T=inputs.map(s=>["L",...s,"_"]),h=inputs.map(()=>0);let pc=J.entry,steps=0;
  while(true){if(watch&&pc===J.tupleEntry)watch(T,h);
   let a=J.ins[pc],k=a.t,x=T[k][h[k]]??"_";if(a.op==="jump"){pc=a.next;continue;}
   if(a.op==="halt"||a.op==="reject")return{status:a.op==="halt"?"COMPLETE":"REJECT",steps,tapes:T.map(t=>t.slice(1).join("").replace(/_+$/,"")),heads:h};
   steps++;if(a.op==="read"){pc=a.next[J.alphabet.indexOf(x)];continue;}
   if(a.op==="write"){ok(x!=="L","sentinel");T[k][h[k]]=a.next.v;}
   else{h[k]+=a.next.dir;ok(h[k]>=0,"left boundary");if(h[k]===T[k].length)T[k].push("_");}
   pc=a.next.d;
  }
 }
 const word=(z,w)=>z.toString(2).padStart(w,"0"),encode=(z,w)=>z.map(x=>word(x,w)).join(",")+";";
 function check(name,m,bag,owner,masks,direct,physical=!!M){
  const ns=bag.filter(v=>v!==owner),[a,b,c]=ns,slots=[[owner],[owner,a],[owner,b],[owner,c],[owner,a,b],[owner,a,c],[owner,b,c]];
  const ids=slots.map(h=>h.includes(undefined)?255:scopes.findIndex(s=>s.join()===h.slice().sort((a,b)=>a-b).join()));
  const proj=slots.map((h,i)=>ids[i]===255?"0000":bag.map(g=>+h.includes(g)).join("").padEnd(4,"0"));
  const streams=ids.map(i=>i===255?"":masks[i]),w=Math.ceil(Math.log2(m)),I=[word(m-1,w).split("").reverse().join(""),"1".repeat(bag.length),proj.join(""),...streams,...Array(9).fill("")];
  ok(I.length===19&&ids.every(i=>i>=0),"input routing");
  const all=[...E.tup(m,bag.length)],expected=all.filter(z=>direct(z)).map(z=>encode(z,w)).join("");
  let count=0,cursorChecks=0,backward=0,previous=null;
  const r=reference(J0,I,(T,h)=>{
   const z=all[count];ok(!!z,"candidate count");
   for(let i=0;i<4;i++)ok(T[10+i].slice(1,1+w).join("")===word(z[i]??0,w).split("").reverse().join(""),"odometer");
   for(let i=0;i<7;i++){
    let index=ids[i]===255?0:z.reduce((a,v,j)=>proj[i][j]==="1"?a*m+v:a,0);
    ok(h[3+i]===index+1,"cursor invariant "+name+" "+count+" "+i);cursorChecks++;
    if(previous&&h[3+i]<previous[i])backward++;
   }previous=h.slice(3,10);count++;
  }),q=reference(J,I);
  ok(r.status==="COMPLETE"&&JSON.stringify(r)===JSON.stringify(q)&&r.tapes[17]===expected&&count===all.length,"IR and oracle "+name);
  ok(r.tapes.slice(0,10).join("|")===I.slice(0,10).join("|"),"mask and config preservation");
  let t=null,span=null;
  if(physical){let p=K.run(M,K.encode(M,J,I),1000000000);ok(p.status==="COMPLETE"&&p.tapes.join("|")===r.tapes.join("|")&&p.heads.join()===r.heads.join(),"physical "+name+" "+p.status);t=p.t;span=p.span;}
  rows.push({name,m,arity:bag.length,owner,ids,candidates:count,allowed:expected.split(";").length-1,cursorChecks,backward,primitives:r.steps,t,span});
  return{I,r,t};
 }
 // Genuine D2C checkpoints: host extracts the actual stream fields and
 // the C1 bag headers, routes the seven scopes; independent original
 // clauses, not the mask streams, determine the expected output.
 function actual(name,m,pins,B,physical){
  const C=L.compile(),D={...L.decode(C.desc),loaderEntry:C.loaderEntry,plannerEntry:C.plannerEntry,pushEntry:C.pushEntry,popEntry:C.popEntry};
  const raw=E.encode(m,pins,B),p=L.run(D,raw,5000000000),d=E.decode(raw);ok(p.status==="MASK_STREAM_LOADED","loader");
  let begin=rows.length;
  for(let f of p.checkpoint.frames.slice(0,9)){
   const bag=[f.choice,...f.neighbors.filter(v=>v!==9)].sort((a,b)=>a-b),factors=d.F.filter(x=>x.h.includes(f.choice)&&x.h.every(v=>bag.includes(v)));
   check(name+"-owner"+f.choice,m,bag,f.choice,p.fields.slice(2),z=>factors.every(f=>f.S.has(f.h.map(g=>z[bag.indexOf(g)]).join())),physical);
  }
  return {name,m,producer:p.t,rows:rows.length-begin};
 }
 const runs=[];
 if(suite==="physical"){
  const B=[[-1,-3,-5],[-2,-4,-7],[-1,-6,-8],[-3,-5,-7],[-2],[-1,-4]];
  runs.push(actual("four-bag-triples",2,[1,0],B,true));
  const H=[[0,1],[0,2],[0,6],[1,3],[1,8],[2,5],[2,7],[3,6],[3,7],[3,8],[4,6],[5,8],[6,7],[7,8]];
  runs.push(actual("greedy-trap",2,[0,1],H.map(h=>h.map(v=>-(2*v+1))),true));
 }else if(suite==="physical3"){
  runs.push(actual("m3-mixed",3,[1,0,1],[[-1,-4,-7],[-2,-6,-10],[-3,-8,-11],[-4,-7,-10],[-1],[-5,-9]],true));
 }else if(suite==="larger"){
  runs.push(actual("m3-mixed",3,[1,0,1],[[-1,-4,-7],[-2,-6,-10],[-3,-8,-11],[-4,-7,-10],[-1],[-5,-9]],false));
  // Every owner position and arity, domains 2,3,4,5, with nontrivial masks.
  for(let m of [2,3,4,5])for(let r=1;r<=4;r++)for(let j=0;j<r;j++){
   const bag=[0,2,5,8].slice(0,r),owner=bag[j],masks=scopes.map(h=>[...E.tup(m,h.length)].map(z=>+((h.reduce((a,b)=>a+b,0)+z.reduce((a,b,i)=>a+(i+1)*b,0))%7===0)).join(""));
   check("synthetic-"+m+"-"+r+"-"+j,m,bag,owner,masks,z=>scopes.filter(h=>h.includes(owner)&&h.every(v=>bag.includes(v))).every(h=>(h.reduce((a,b)=>a+b,0)+h.reduce((a,v,i)=>a+(i+1)*z[bag.indexOf(v)],0))%7!==0),false);
  }
 }else throw Error("suite");
 return{suite,ir:J.stats,q:M?.q??null,logical:M?.logicalStates??null,bits:M?4+M.q+3*M.q*(M.q.toString(2).length+4):null,runs,rows,totals:rows.reduce((a,r)=>({candidates:a.candidates+r.candidates,allowed:a.allowed+r.allowed,cursorChecks:a.cursorChecks+r.cursorChecks,backward:a.backward+r.backward,primitives:a.primitives+r.primitives,transitions:a.transitions+(r.t??0)}),{candidates:0,allowed:0,cursorChecks:0,backward:0,primitives:0,transitions:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_TUPLE_CURSOR_OK '+JSON.stringify(audit(require('./f038_rex_width_three_tuple_cursor.js'),require('./f038_rex_width_three_projection.js'),require('./f038_rex_width_three_compiler.js'),require('./f038_rex_width_three_direct_loader.js'),require('./f038_tga_normalized_integration.js').engine(),process.argv[2]||'physical')));
