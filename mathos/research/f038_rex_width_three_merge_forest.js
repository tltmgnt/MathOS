// REX-024C2: HOST orchestration of real physical C1 checkpoints and charged merge calls; no physical handoff claimed.
function forestAudit(P,K,E){
 const ok=(v,s)=>{if(!v)throw Error(s)},C=P.compile(),M={...P.decode(C.desc),plannerEntry:C.plannerEntry,pushEntry:C.pushEntry,popEntry:C.popEntry},V=[...Array(9).keys()],scopes=[1,2,3].flatMap(k=>[...E.subsets(V,k)]),index=new Map(scopes.map((h,i)=>[h.join(),i])),results=[];
 function check(name,m,pins,B,want){
  const raw=E.encode(m,pins,B),D=E.decode(raw),r=P.run(M,raw,2000000000),p=r.checkpoint;
  ok(r.status==="WIDTH_THREE_FACTORS","admitted header");
  const w=Math.ceil(Math.log2(m)),word=z=>z.toString(2).padStart(w,"0"),field=s=>[...s].map(b=>"0"+b).join("")+"10",encode=z=>z.map(x=>word(x)).join(",")+";";
  const bags=p.frames.slice(0,9).map(f=>{
   const h=[f.choice,...f.neighbors.filter(x=>x!==9)].sort((a,b)=>a-b),v=f.choice;
   const owned=scopes.filter(s=>s.includes(v)&&s.every(g=>h.includes(g)));
   const rows=[...E.tup(m,h.length)].filter(z=>owned.every(s=>p.masks[index.get(s.join())][s.reduce((a,g)=>a*m+z[h.indexOf(g)],0)]==="0"));
   const direct=[...E.tup(m,h.length)].filter(z=>D.F.filter(f=>owned.some(s=>s.join()===f.h.join())).every(f=>f.S.has(f.h.map(g=>z[h.indexOf(g)]).join())));
   ok(JSON.stringify(rows)===JSON.stringify(direct),"host initial relation oracle");
   return {h,v,parent:f.parent,sep:f.neighbors.filter(x=>x!==9),rows,oracle:direct};
  });
  const initial=bags.map(b=>b.rows.length),edges=[];let steps=0;
  for(let i=0;i<9;i++){
   const b=bags[i];if(b.parent===9)continue;const j=bags.findIndex(x=>x.v===b.parent),par=bags[j];
   ok(j>i,"parent order");
   const mask=h=>h.reduce((s,g,k)=>s|(b.sep.includes(g)?1<<k:0),0),pm=mask(par.h),cm=mask(b.h);
   const conf={parentArity:par.h.length,childArity:b.h.length,parentMask:pm,childMask:cm};
   const z=K.kernel(par.rows.map(encode).join(""),b.rows.map(encode).join(""),Infinity,conf);
   ok(z.status==="COMPLETE","merge");
   const projected=(h,t)=>b.sep.map(v=>t[h.indexOf(v)]),support=new Set(b.oracle.map(t=>projected(b.h,t).join()));
   par.oracle=par.oracle.filter(t=>support.has(projected(par.h,t).join()));
   const keyed=par.rows.map(t=>[projected(par.h,t).map(v=>field(word(v))).join(""),t]);
   const expected=keyed.filter(([,t])=>support.has(projected(par.h,t).join())).sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0);
   ok(z.filtered===expected.map(([k,t])=>k+":"+t.map(v=>field(word(v))).join("")+";").join(""),"exact filtered word");
   // Decode actual output rather than use oracle rows as next edge input.
   par.rows=z.filtered.split(";").filter(Boolean).map(s=>{let data=s.split(":")[1],out=[],bits="";for(let k=0;k<data.length;k+=2){let t=data.slice(k,k+2);if(t==="10"){out.push(parseInt(bits,2));bits="";}else {ok(t==="00"||t==="01","payload token");bits+=t[1];}}ok(!bits&&out.length===par.h.length,"decoded payload");return out;});
   ok(par.rows.map(t=>t.join()).sort().join("|")===par.oracle.map(t=>t.join()).sort().join("|"),"propagated rows");
   steps+=z.steps;edges.push({child:i,parent:j,separator:b.sep.length,keys:support.size,remaining:par.rows.length,steps:z.steps});
  }
  const roots=bags.filter(b=>b.parent===9),sat=roots.every(b=>b.rows.length>0);
  let models=0;for(let z of E.tup(m,9))if(D.F.every(f=>f.S.has(f.h.map(g=>z[g]).join())))models++;
  ok(sat===want&&sat===(models>0),"forest decision");
  results.push({name,m,L:raw.length,producerTransitions:r.t,kernelSteps:steps,initial,live:bags.map(b=>b.rows.length),sat,models,edges});
 }
 // Width-three K4: x=a XOR b, x=c, then impose opposite or same parity
 // on the three later variables. Child projected support is even parity;
 // every one- and two-coordinate projection is full.
 function parity(consistent){
  let B=[];
  for(let [x,a,b] of E.tup(2,3))if(x!==(a^b))B.push([-(x+1),-(6+a+1),-(10+b+1)]);
  for(let [x,c] of E.tup(2,2))if(x!==c)B.push([-(x+1),-(16+c+1)]);
  for(let [a,b,c] of E.tup(2,3))if((a^b^c)!==(consistent?0:1))B.push([-(6+a+1),-(10+b+1),-(16+c+1)]);
  return B;
 }
 check("joint-three-UNSAT",2,[0,1],parity(false),false);
 ok(results.at(-1).initial.every(x=>x>0)&&results.at(-1).edges[0].separator===3&&results.at(-1).edges[0].keys===4&&results.at(-1).edges[0].remaining===0,"nonempty joint obstruction");
 check("joint-three-SAT",2,[1,0],parity(true),true);
 const trap=[[0,1],[0,2],[0,6],[1,3],[1,8],[2,5],[2,7],[3,6],[3,7],[3,8],[4,6],[5,8],[6,7],[7,8]];
 check("greedy-trap",2,[1,1],trap.map(h=>h.map(v=>-(2*v+1))),true);
 check("disconnected-UNSAT",2,[0,0],parity(true).concat([[-3],[-4]]),false);
 return {results,totals:results.reduce((a,r)=>({producerTransitions:a.producerTransitions+r.producerTransitions,kernelSteps:a.kernelSteps+r.kernelSteps,edges:a.edges+r.edges.length,rawBits:a.rawBits+r.L}),{producerTransitions:0,kernelSteps:0,edges:0,rawBits:0})};
}
module.exports={forestAudit};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_MERGE_FOREST_OK '+JSON.stringify(forestAudit(require('./f038_rex_width_three_factors.js'),require('./f038_rex_width_three_merge.js'),require('./f038_tga_normalized_integration.js').engine())));
