// REX-024D2C: compare complete preserved C1 checkpoint and direct physical output against independent original factors.
function audit(P,C,E,suite="small"){
 const M=P.compile(),D={...P.decode(M.desc),plannerEntry:M.plannerEntry,pushEntry:M.pushEntry,popEntry:M.popEntry,loaderEntry:M.loaderEntry},G=C.compile(),B={...C.decode(G.desc),plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry},ok=(v,s)=>{if(!v)throw Error(s)},V=[...Array(9).keys()],scopes=[1,2,3].flatMap(k=>[...E.subsets(V,k)]),rows=[];
 const trap=[[0,1],[0,2],[0,6],[1,3],[1,8],[2,5],[2,7],[3,6],[3,7],[3,8],[4,6],[5,8],[6,7],[7,8]],make=(m,H)=>H.map(h=>h.map(v=>-(m*v+1)));
 function check(name,m,pins,clauses,accepted=true){
  const raw=E.encode(m,pins,clauses),p=C.run(B,raw,3000000000,null,true),r=P.run(D,raw,5000000000,null,true),d=E.decode(raw);
  ok(p.status===(accepted?"WIDTH_THREE_FACTORS":"OUTSIDE_WIDTH_THREE")&&r.status===(accepted?"MASK_STREAM_LOADED":"OUTSIDE_WIDTH_THREE"),"status "+name+" "+r.status);
  ok(JSON.stringify(p.checkpoint)===JSON.stringify(r.checkpoint),"preserved checkpoint "+name);
  let ph=p.snapshot.indexOf("H"),rh=r.snapshot.indexOf("H");
  ok(ph===rh,"preserved left extent");
  let end=ph+85*(accepted?10:1)+1;
  ok(p.snapshot.slice(0,end)===r.snapshot.slice(0,end),"literal preserved prefix/stack");
  let bound="",maskBits=0,streamBits=0;
  if(accepted){
   const masks=scopes.map(h=>{let f=d.F.find(f=>f.h.join()===h.join());return [...E.tup(m,h.length)].map(z=>+(!!f&&!f.S.has(z.join()))).join("");});
   bound=(m-1).toString(2).split("").reverse().join("");
   const fields=[bound,pins.join(""),...masks],word=fields.map(s=>[...s].map(x=>"0"+x).join("")+"10").join("");
   ok(r.fields.join(";")===fields.join(";")&&r.stream===word&&r.checkpoint.masks.join()===masks.join(),"exact canonical output "+name);
   ok(r.loaderAt===p.t-1,"exact inherited prefix clock");
   maskBits=masks.join("").length;streamBits=word.length;
  }else ok(r.loaderAt===null&&r.t===p.t&&r.stream===""&&r.fields.length===0&&r.snapshot===p.snapshot,"unchanged refusal");
  rows.push({name,m,L:raw.length,producer:p.t,t:r.t,loaderAt:r.loaderAt,loader:accepted?r.t-r.loaderAt:0,span:r.span,maskBits,streamBits,bound,pins:pins.join(""),status:r.status});
  return{raw,r};
 }
 if(suite==="small"){
  check("empty",2,[0,0],[]);
  check("four-bag-triples",2,[1,0],[[-1,-3,-5],[-2,-4,-7],[-1,-6,-8],[-3,-5,-7],[-2],[-1,-4]]);
  check("greedy-trap",2,[0,1],make(2,trap));
  check("unary-UNSAT",2,[1,1],[[-1],[-2]]);
  check("K5-SAT-refusal",2,[1,1],make(2,[...E.subsets([0,1,2,3,4],2)]),false);
 }else if(suite==="larger"){
  check("m3-mixed",3,[1,0,1],[[-1,-4,-7],[-2,-6,-10],[-3,-8,-11],[-4,-7,-10],[-1],[-5,-9]]);
 }else if(suite==="controls"){
  const a=check("empty",2,[1,0],[]),cutoffs=[0,1,100,a.r.loaderAt-1,a.r.loaderAt,a.r.loaderAt+1,a.r.t-1];
  for(let t of cutoffs){let r=P.run(D,a.raw,t);ok(r.status==="TIMEOUT"&&r.t===t,"cutoff "+t);}
  ok(P.run(D,a.raw,a.r.t).stream===a.r.stream,"exact budget");
  const bad=["","1000","1".repeat(32)+"0",a.raw.slice(0,-1),a.raw+"1"],rejects=[];
  for(let raw of bad){let p=C.run(B,raw,100000000),r=P.run(D,raw,100000000);ok(r.status==="OUTSIDE_NORMALIZED"&&r.t===p.t,"inherited malformed refusal");rejects.push(r.t);}
  return{suite,q:M.q,bits:M.desc.length,loaderEntry:M.loaderEntry,cutoffs,rejects,exactBudget:a.r.t};
 }else throw Error("suite");
 return{suite,q:M.q,bits:M.desc.length,loaderEntry:M.loaderEntry,rows,totals:rows.reduce((a,r)=>({raw:a.raw+r.L,transitions:a.transitions+r.t,loader:a.loader+r.loader,maskBits:a.maskBits+r.maskBits,streamBits:a.streamBits+r.streamBits}),{raw:0,transitions:0,loader:0,maskBits:0,streamBits:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_DIRECT_LOADER_OK '+JSON.stringify(audit(require('./f038_rex_width_three_direct_loader.js'),require('./f038_rex_width_three_factors.js'),require('./f038_tga_normalized_integration.js').engine(),process.argv[2]||'small')));
