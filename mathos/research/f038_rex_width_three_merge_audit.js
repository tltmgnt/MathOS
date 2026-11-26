// REX-024C2: independent sort/projection/semijoin differential tests.
function audit(K,suite="kernel"){
 const ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 const enc=(r)=>r.map(x=>x.map(b=>"0"+b).join("")+"10").join(""); // fields are arrays of bits
 const tuple=r=>r.map(a=>a.join("")).join(",")+";";
 const pick=(r,mask)=>r.filter((_,i)=>mask&(1<<i));
 const record=([key,payload])=>key+":"+payload+";";
 const cmp=(a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0;
 function check(name,P,C,config=null){
  const p=config?P.map(tuple).join(""):P.map(record).join(""),c=config?C.map(tuple).join(""):C.map(record).join("");
  const pp=config?P.map(r=>[enc(pick(r,config.parentMask)),enc(r)]):P;
  const cc=config?C.map(r=>[enc(pick(r,config.childMask)),enc(r)]):C;
  const keys=[...new Set(cc.map(r=>r[0]))].sort(),keySet=new Set(keys);
  const expected=pp.slice().sort(cmp).filter(r=>keySet.has(r[0])).map(record).join("");
  const r=K.kernel(p,c,Infinity,config);
  ok(r.status==="COMPLETE"&&r.filtered===expected&&r.support===keys.map(k=>k+":;").join(""),"differential "+name);
  ok(r.tapes===7&&Object.values(r.ledger).reduce((a,b)=>a+b,0)===r.steps,"charged ledger");
  ok(r.passes.parentSort===Math.ceil(Math.log2(Math.max(1,P.length)))&&r.passes.childSort===Math.ceil(Math.log2(Math.max(1,C.length))),"merge pass count");
  rows.push({name,parentRows:P.length,childRows:C.length,inputSymbols:p.length+c.length,outputRows:pp.filter(r=>keySet.has(r[0])).length,keys:keys.length,steps:r.steps,span:r.span,passes:r.passes,ledger:r.ledger});
  return{p,c,r};
 }
 if(suite==="kernel"){
  check("empty",[],[]);check("empty-child",[["","1"],["1","0"]],[]);check("empty-parent",[],[["1",""]]);
  check("stable-duplicates",[["01","10"],["00","01"],["01","11"],["11","00"]],[["01","1"],["00","0"],["01","0"]]);
  check("variable-keys",[["1",""],["","1"],["00",""],["0",""]],[["",""],["0",""]]);
  const keys=["00","01","10","11"];
  for(let p=0;p<16;p++)for(let c=0;c<16;c++)check("exhaustive-"+p+"-"+c,keys.filter((_,i)=>p>>i&1).reverse().flatMap(k=>[[k,"1"],[k,"0"]]),keys.filter((_,i)=>c>>i&1).reverse().flatMap(k=>[[k,""],[k,"1"]]));
  let seed=0x52455824,rnd=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;},word=n=>Array.from({length:n},()=>rnd(2)).join("");
  for(let i=0;i<128;i++){
   let P=Array.from({length:rnd(40)},()=>[word(rnd(8)),word(rnd(12))]),C=Array.from({length:rnd(40)},()=>[word(rnd(8)),word(rnd(12))]);
   check("random-"+i,P,C);
  }
  const bits=(n,w)=>n.toString(2).padStart(w,"0").split("");
  const t=(a)=>a.map(v=>bits(v,1));
  check("joint-three-parity",[...Array(8).keys()].filter(i=>((i>>2)^(i>>1)^i)&1).map(i=>t([i>>2,i>>1&1,i&1])),[...Array(8).keys()].filter(i=>!(((i>>2)^(i>>1)^i)&1)).map(i=>t([i>>2,i>>1&1,i&1])),{parentArity:3,childArity:3,parentMask:7,childMask:7});
  check("nonadjacent-three",[[0,1,0,1],[1,0,0,1],[1,1,1,0]].map(t),[[0,0,1],[1,1,0]].map(t),{parentArity:4,childArity:3,parentMask:13,childMask:7});
  check("empty-separator",[[0,1],[1,0]].map(t),[[1]].map(t),{parentArity:2,childArity:1,parentMask:0,childMask:0});
  check("empty-separator-empty-child",[[0,1],[1,0]].map(t),[],{parentArity:2,childArity:1,parentMask:0,childMask:0});
  check("variable-width-no-collision",[[["0"],["0","1"]],[["0","0"],["1"]]],[[["0","0"],["1"]]],{parentArity:2,childArity:2,parentMask:3,childMask:3});
  const x=check("cutoff-fixture",[["10","01"],["01","11"],["10","00"]],[["10","1"]]);
  for(let n of [0,1,10,x.r.ledger.parentSort-1,x.r.ledger.parentSort,x.r.steps-1]){let r=K.kernel(x.p,x.c,n);ok(r.status==="TIMEOUT"&&r.steps===n&&r.filtered===null&&r.support===null,"cutoff");}
  ok(K.kernel(x.p,x.c,x.r.steps).filtered===x.r.filtered,"exact clock");
  const bad=[["0",""],["0:1",""],["0:2;",""],["0::;",""],["0:;|",""],["","0:;x"],["0,;","1,0;"],["0;","1,0;"],["0,1,0;","1,0;"],["0,1;","0,;"]];
  for(let i=0;i<bad.length;i++){let [p,c]=bad[i],r=K.kernel(p,c,Infinity,i>=6?{parentArity:2,childArity:2,parentMask:3,childMask:3}:null);ok(r.status==="MALFORMED"&&r.filtered===null,"malformed "+i);}
  return{suite,cases:rows.length,cutoffs:6,malformed:bad.length,rows:rows.filter(x=>!x.name.startsWith("random-")&&!x.name.startsWith("exhaustive-")),totals:sum(rows)};
 }else if(suite==="scale"){
  for(let m of [2,3,4,5,8]){
   let w=Math.ceil(Math.log2(m)),P=[],C=[];
   for(let a=m-1;a>=0;a--)for(let b=m-1;b>=0;b--)for(let c=m-1;c>=0;c--)for(let d=m-1;d>=0;d--){
    const row=[a,b,c,d].map(x=>x.toString(2).padStart(w,"0").split(""));P.push(row);if((a+c+d)%2===0)C.push([row[0],row[2],row[3],row[1]]);
   }
   check("domain-"+m,P,C,{parentArity:4,childArity:4,parentMask:13,childMask:7});
  }return{suite,cases:rows.length,rows,totals:sum(rows)};
 }else throw Error("suite");
 function sum(rows){return rows.reduce((a,r)=>({steps:a.steps+r.steps,parentRows:a.parentRows+r.parentRows,childRows:a.childRows+r.childRows,outputRows:a.outputRows+r.outputRows,keys:a.keys+r.keys,inputSymbols:a.inputSymbols+r.inputSymbols}),{steps:0,parentRows:0,childRows:0,outputRows:0,keys:0,inputSymbols:0});}
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_MERGE_OK '+JSON.stringify(audit(require('./f038_rex_width_three_merge.js'),process.argv[2]||'kernel')));
