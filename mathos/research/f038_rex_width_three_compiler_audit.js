// Independent host stable-sort/set oracle for standalone ternary merge machine.
function audit(K,suite="small"){
 const J=K.machine(),M=K.compile(J),ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 const rec=([k,v])=>k+":"+v+";";
 function check(name,P,C){
  let p=P.map(rec).join(""),c=C.map(rec).join(""),raw=K.encode(M,J,[p,c,"","","","",""]),r=K.run(M,raw,500000000);
  let keys=[...new Set(C.map(x=>x[0]))].sort(),wanted=P.slice().sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0).filter(x=>keys.includes(x[0])).map(rec).join("");
  ok(r.status==="COMPLETE"&&r.head===0&&r.tapes.length===7&&r.tapes[4]===keys.map(k=>k+":;").join("")&&r.tapes[6]===wanted,"semijoin "+name+" "+JSON.stringify(r));
  ok(r.tapes[0]===P.slice().sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0).map(rec).join("")+(P.length?"|":"")&&r.tapes[1]===C.slice().sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0).map(rec).join("")+(C.length?"|":""),"stable sort");
  rows.push({name,parent:P.length,child:C.length,inputBits:raw.length,t:r.t,span:r.span,output:wanted,support:r.tapes[4]});return{raw,r};
 }
 if(suite==="small"){
  check("empty",[],[]);check("empty-parent",[],[["1",""]]);check("empty-child",[["","1"],["1","0"]],[]);
  let a=check("stable-duplicates",[["01","10"],["00","01"],["01","11"],["11","00"]],[["01","1"],["00","0"],["01","0"]]);
  check("variable-keys",[["1",""],["","1"],["00",""],["0",""]],[["",""],["0",""]]);
  check("empty-key",[["","01"],["","10"],["1","0"]],[["",""]]);
  check("joint-three-parity",["001","010","100","111"].map(k=>[k,"0"]),["000","011","101","110"].map(k=>[k,""]));
  check("joint-three-compatible",["111","011","000","101","110"].map(k=>[k,"1"]),["110","000","011","101"].map(k=>[k,""]));
  for(let [p,c] of [["0",""],["0:1",""],["0::;",""],["0:;|",""],["","0:;|"]]){
   let v=K.run(M,K.encode(M,J,[p,c,"","","","",""]),100000000);ok(v.status==="REJECT","malformed");
  }
  for(let t of [0,1,100,a.r.t-1])ok(K.run(M,a.raw,t).status==="TIMEOUT","cutoff");
  ok(K.run(M,a.raw,a.r.t).tapes[6]===a.r.tapes[6],"exact clock");
 }else if(suite==="seeded"){
  let seed=0x52455824;const rand=n=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)>>>8)%n,word=n=>Array.from({length:n},()=>rand(2)).join("");
  for(let i=0;i<24;i++){let p=Array.from({length:rand(7)},()=>[word(rand(4)),word(rand(4))]),c=Array.from({length:rand(7)},()=>[word(rand(4)),word(rand(4))]);check("seed-"+i,p,c);}
 }else throw Error("suite");
 return{suite,instructions:J.ins.length,logical:M.logicalStates,q:M.q,rules:3*M.q,bits:4+M.q+3*M.q*(M.q.toString(2).length+4),width:M.w,rows,transitions:rows.reduce((a,r)=>a+r.t,0)};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_COMPILER_OK '+JSON.stringify(audit(require('./f038_rex_width_three_compiler.js'),process.argv[2]||'small')));
