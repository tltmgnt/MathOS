// Independent original-factor oracle for finite-IR mask loading.
function audit(L,P,C,E){
 const G=C.compile(),producer={...C.decode(G.desc),plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry},J0=L.machine(),J=P.compact(J0),ok=(v,s)=>{if(!v)throw Error(s)};
 function run(J,input){
  const tapes=[["L",...input,"_"],...Array.from({length:3},()=>["L","_"])],heads=Array(4).fill(0);
  let pc=J.entry,steps=0;
  while(true){
   const I=J.ins[pc],k=I.t,a=tapes[k][heads[k]]??"_";
   if(I.op==="halt"||I.op==="reject")return{status:I.op==="halt"?"COMPLETE":"REJECT",steps,tapes:tapes.map(t=>t.slice(1).join("").replace(/_+$/,"")),heads};
   if(I.op==="jump"){pc=I.next;continue;}steps++;
   if(I.op==="read"){pc=I.next[J.alphabet.indexOf(a)];continue;}
   if(I.op==="write"){ok(a!=="L"&&I.next.v!=="L","sentinel");tapes[k][heads[k]]=I.next.v;}
   else if(I.op==="move"){heads[k]+=I.next.dir;ok(heads[k]>=0,"left");if(heads[k]===tapes[k].length)tapes[k].push("_");}
   else throw Error("opcode");pc=I.next.d;
  }
 }
 const rows=[];
 for(let [m,pins,B] of [[2,[1,0],[[-1,-3,-5],[-2,-4,-7],[-1,-6,-8]]],[3,[1,0,1],[[-1,-4,-7],[-2,-6,-10],[-3,-8,-11]]]]){
  let raw=E.encode(m,pins,B),p=C.run(producer,raw,3000000000,null,true),input=p.snapshot.replaceAll("_","b"),a=run(J0,input),b=run(J,input),D=E.decode(raw);
  ok(p.status==="WIDTH_THREE_FACTORS"&&a.status==="COMPLETE"&&JSON.stringify(a)===JSON.stringify(b),"IR equivalence");
  let want=(m-1).toString(2).split("").reverse().join(""),V=[0,1,2,3,4,5,6,7,8],scopes=[1,2,3].flatMap(k=>[...E.subsets(V,k)]),masks=scopes.map(h=>{
   const f=D.F.find(f=>f.h.join()===h.join());return [...E.tup(m,h.length)].map(z=>+(!!f&&!f.S.has(z.join()))).join("");
  });
  ok(b.tapes[0]===input&&b.tapes[1]===want&&b.tapes[2]===pins.join("")&&b.tapes[3]===masks.join(";")+";"&&masks.join()===p.checkpoint.masks.join(),"bound/pin/all masks");
  rows.push({m,producer:p.t,steps:b.steps,input:input.length,bound:b.tapes[1],pins:b.tapes[2],maskBits:masks.join("").length,maskStream:b.tapes[3].length});
 }
 return{ir:J.stats,rows};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_MASK_LOADER_OK '+JSON.stringify(audit(require('./f038_rex_width_three_mask_loader.js'),require('./f038_rex_width_three_projection.js'),require('./f038_rex_width_three_factors.js'),require('./f038_tga_normalized_integration.js').engine())));
