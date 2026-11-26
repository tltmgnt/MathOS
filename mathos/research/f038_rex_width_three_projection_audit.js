// Exact projected tuple and independent finite-IR differential checks.
function audit(P,K,suite="small"){
 const J0=P.machine(),J=P.compact(J0),M=K.compile(J),ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 function reference(J,inputs){
  let tapes=inputs.map(s=>["L",...s,"_"]),heads=inputs.map(()=>0),pc=J.entry,steps=0;
  for(;;){
   let I=J.ins[pc],k=I.t,a=tapes[k][heads[k]]??"_";
   if(I.op==="halt"||I.op==="reject")return{status:I.op==="halt"?"COMPLETE":"REJECT",steps,tapes:tapes.map(t=>t.slice(1).join("").replace(/_+$/,"")),heads};
   if(I.op==="jump"){pc=I.next;continue;}
   steps++;
   if(I.op==="read"){pc=I.next[J.alphabet.indexOf(a)];continue;}
   if(I.op==="write"){if(a==="L"||I.next.v==="L")throw Error("sentinel write");tapes[k][heads[k]]=I.next.v;}
   else if(I.op==="move"){heads[k]+=I.next.dir;if(heads[k]<0)throw Error("left");if(heads[k]===tapes[k].length)tapes[k].push("_");}
   else throw Error("opcode");
   pc=I.next.d;
  }
 }
 const tuple=r=>r.join(",")+";",enc=r=>r.map(s=>[...s].map(b=>"0"+b).join("")+"10").join(""),key=(r,m)=>enc(r.filter((_,i)=>m[i]==="1"));
 const input=(p,c,pm,cm)=>[p,c,"","","","","",pm,cm,""];
 function check(name,P,C,pm,cm){
  const I=input(P.map(tuple).join(""),C.map(tuple).join(""),pm,cm),raw=K.encode(M,J,I),r=K.run(M,raw,1000000000);
  ok(r.status==="COMPLETE"&&r.head===0&&r.tapes.length===10,"halt "+name+" "+JSON.stringify(r));
  const pp=P.map(r=>[key(r,pm),r]),cc=C.map(r=>[key(r,cm),r]),cmp=(a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0,rec=([k,r])=>k+":"+enc(r)+";";
  const support=[...new Set(cc.map(x=>x[0]))].sort(),set=new Set(support),wanted=pp.slice().sort(cmp).filter(x=>set.has(x[0]));
  ok(r.tapes[0]===pp.slice().sort(cmp).map(rec).join("")+(P.length?"|":"")&&r.tapes[1]===cc.slice().sort(cmp).map(rec).join("")+(C.length?"|":""),"projected sorted inputs "+name);
  ok(r.tapes[4]===support.map(k=>k+":;").join("")&&r.tapes[6]===wanted.map(rec).join("")&&r.tapes[9]===wanted.map(x=>tuple(x[1])).join(""),"joint output "+name);
  ok(r.tapes[7]===pm&&r.tapes[8]===cm,"mask preservation");
  const a=reference(J0,I),b=reference(J,I);
  ok(a.status===b.status&&a.steps===b.steps&&a.tapes.join("\n")===b.tapes.join("\n")&&a.heads.join()===b.heads.join(),"IR quotient");
  ok(b.status===r.status&&b.tapes.join("\n")===r.tapes.join("\n")&&b.heads.join()===r.heads.join(),"all virtual tapes and heads");
  rows.push({name,pm,cm,parent:P.length,child:C.length,retained:wanted.length,inputBits:raw.length,t:r.t,span:r.span,primitives:b.steps,output:r.tapes[9],support:r.tapes[4]});return{raw,r};
 }
 const bits=n=>n.toString(2).padStart(3,"0").split("");
 let cutoffs=[],rejects=[];
 if(suite==="small"){
  check("empty",[],[],"1","1");
  check("empty-parent",[],[["1"]],"1","1");
  check("empty-child",[["0","1"],["1","0"]],[],"00","0");
  check("empty-separator",[["0","1"],["1","0"]],[["1"]],"00","0");
  let a=check("nonadjacent-three",[["0","1","0","1"],["1","0","0","1"],["1","1","1","0"]],[["0","0","1"],["1","1","0"]],"1011","111");
  check("stable-duplicates",[["1","0"],["0","1"],["1","1"],["1","0"]],[["1"],["0"],["1"]],"10","1");
  check("variable-width-no-collision",[["0","01"],["00","1"]],[["00","1"]],"11","11");
  const even=[0,3,5,6].map(bits),odd=[1,2,4,7].map(bits);
  check("joint-three-parity",odd,even,"111","111");
  check("joint-three-compatible",[...odd,...even].slice(0,5),even,"111","111");
  for(let t of [0,1,100,a.r.t-1]){let r=K.run(M,a.raw,t);ok(r.status==="TIMEOUT"&&r.t===t,"cutoff");cutoffs.push(t);}
  ok(K.run(M,a.raw,a.r.t).tapes[9]===a.r.tapes[9],"exact budget");
  for(let [p,c,pm,cm] of [["0;","1;","","1"],["0;","1;","00000","0"],["0;","1;","1111","111"],["0;","1;","1","0"],["0;","1;",";","1"],["0,;","0,1;","11","11"],["0;","0,1;","11","11"],["0,1,0;","0,1;","11","11"],["0,1","0,1;","11","11"],["0,1;","0,;","11","11"]]){
   const I=input(p,c,pm,cm),r=K.run(M,K.encode(M,J,I),100000000),v=reference(J,I);
   ok(r.status==="REJECT"&&v.status==="REJECT","malformed "+JSON.stringify(I));rejects.push(r.t);
  }
 }else if(suite==="seeded"){
  let seed=0x52455825;const rnd=n=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)>>>8)%n,word=n=>Array.from({length:n},()=>rnd(2)).join("");
  const masks=[];for(let r=1;r<=4;r++)for(let n=0;n<2**r;n++){let m=n.toString(2).padStart(r,"0"),k=m.split("1").length-1;if(k<=3)masks.push({m,k});}
  // Every legal mask appears at least once on the parent side, with
  // another compatible mask on the child side; random rows include duplicates.
  for(let {m:pm,k} of masks){
   let options=masks.filter(x=>x.k===k),cm=options[rnd(options.length)].m,tuples=(m,n)=>Array.from({length:n},()=>Array.from({length:m.length},()=>word(1+rnd(2))));
   let p=tuples(pm,1+rnd(3)),c=tuples(cm,1+rnd(3));
   let match=p[0].filter((_,i)=>pm[i]==="1"),j=0;c[0]=c[0].map((s,i)=>cm[i]==="1"?match[j++]:s);
   check("mask-"+pm,p,c,pm,cm);
  }
 }else throw Error("suite");
 return{suite,ir:J.stats,q:M.q,logical:M.logicalStates,bits:4+M.q+3*M.q*(M.q.toString(2).length+4),width:M.w,rows,cutoffs,rejects,transitions:rows.reduce((a,r)=>a+r.t,0),primitives:rows.reduce((a,r)=>a+r.primitives,0)};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_PROJECTION_OK '+JSON.stringify(audit(require('./f038_rex_width_three_projection.js'),require('./f038_rex_width_three_compiler.js'),process.argv[2]||'small')));
