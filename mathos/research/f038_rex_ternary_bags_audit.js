// F038-REX-022B4 split audit suites; host oracles never control the machine.
function audit(P,R,E,A,which="small"){
 const C=P.compile(),M={...P.decode(C.desc),serializationEntry:C.serializationEntry},ok=(v,s)=>{if(!v)throw Error(s)},rows=[],controls=[];
 let seed=0x52455824;const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 function fixture(m,mode){
  const B=[];for(let c of E.pool(19*m-7))if(c.every(x=>x<0&&-x<=9*m)){
   let gs=c.map(x=>Math.floor((-x-1)/m));if(new Set(gs).size!==c.length||gs[gs.length-1]-gs[0]>2)continue;
   if(mode===1&&c.length===1&&(-c[0]-1)%m!==m-1||mode===2||mode===3&&(rnd()>>>24)<101)B.push(c);
  }return B;
 }
 const probe=new Function("return ("+R.producer.toString().replace('phase="output";','return {...result("PREPARED"), masks:masks.flat().map(t=>t.cells.slice(1).join(""))};')+")")();
 function check(m,mode,pins){
  let B=fixture(m,mode),raw=E.encode(m,pins,B),ref=R.producer(raw),p0=probe(raw),bags=[];
  for(let j=0;j<7;j++){
   let scope=[j,j+1,j+2],rows=[];
   for(let z of E.tup(m,3))if(!B.some(c=>c.every(x=>{let g=Math.floor((-x-1)/m);return g>=j&&g<=j+2&&z[g-j]===(-x-1)%m;})))rows.push([...z.map(a=>a.toString(2).padStart(Math.ceil(Math.log2(m)),"0")),1]);
   bags.push({k:j?2:3,scope,rows,children:[]});
  }
  for(let j=0;j<6;j++)bags[j].children.push(bags[j+1]);
  const v=P.run(M,raw,6000000000),p=v.checkpoint;
  ok(v.status==="BAGS_PREPARED","status "+m+":"+mode+" "+v.status+" "+v.t);
  ok(v.prepared===ref.prepared&&v.prepared===A.encode(bags[0]),"grammar "+m+":"+mode);
  ok(p.m===m&&p.pins===pins.join("")&&p.selector===raw.slice(19*m-6)&&p.masks.every((x,i)=>x===p0.masks[i]),"restored checkpoint");
  ok(p.ranks.join()==="0,0,0"&&p.rankBounds.join()===[m-1,m-2].join()&&p.groups.join()==="19,20,20","rank reset");
  rows.push({m,mode,pins:p.pins,L:raw.length,N:v.prepared.length,maskBits:p.maskBits,allowedRows:bags.map(b=>b.rows.length),t:v.t,serializationAt:v.serializationAt,serializationTransitions:v.serializationTransitions,span:v.span});
  return{raw,v};
 }
 let worker=[];
 if(which==="small"){
  let sat,dense;for(let mode=0;mode<4;mode++){let v=check(2,mode,[mode&1,mode>>1]);if(mode===1)sat=v;if(mode===2)dense=v;}
  const J=A.worker(),Q=A.compile(J.rules,J.symbols,J.projection);
  for(let [v,want] of [[sat,true],[dense,false]]){
   let x=A.physical(Q,v.v.prepared,120000000);ok(x.state===Q.q&&x.tape.has(x.head)===want,"worker status");
   if(want){ok(Array.from({length:7},(_,i)=>x.tape.get(x.head+i)).join("")==="1111111","worker cert");ok(E.valid(v.raw,E.witness(2,[1,0],Array(9).fill(1))),"original witness");}
   worker.push({status:want?"SAT":"UNSAT",transitions:x.t,witnessVerified:want});
  }
 }else if(which==="three"){check(3,0,[0,1,0]);check(3,3,[1,0,1]);}
 else if(which==="four")check(4,3,[0,1,0,1]);
 else if(which==="five")check(5,1,[1,0,1,0,1]);
 else if(which==="controls"){
  let raw=E.encode(2,[0,1],[]),n=31,pos=new Map(),at=n+1;for(let c of E.pool(n))pos.set(c.join(","),at++);
  const flip=(s,i)=>s.slice(0,i)+(s[i]==="1"?"0":"1")+s.slice(i+1),wide=E.encode(2,[0,1],[[-1,-17]]);
  for(let [name,bad,want] of [["empty","","OUTSIDE_NORMALIZED"],["header","1".repeat(32)+"0","OUTSIDE_NORMALIZED"],["mandatory",flip(raw,pos.get("-31")),"OUTSIDE_NORMALIZED"],["latePin",flip(raw,pos.get("-28,-30,-31")),"OUTSIDE_NORMALIZED"],["truncated",raw.slice(0,-1),"OUTSIDE_NORMALIZED"],["extra",raw+"1","OUTSIDE_NORMALIZED"],["outside",wide,"OUTSIDE_FIXED_PATH"],["outsideLateMalformed",flip(wide,pos.get("-28,-30,-31")),"OUTSIDE_NORMALIZED"]]){
   let v=P.run(M,bad,100000000);ok(v.status===want,"control "+name);controls.push({name,status:v.status,t:v.t});
  }
  const entry=7649151,clock=61579486;
  for(let limit of [0,1,100,entry-1,entry,entry+1,clock-1]){let v=P.run(M,raw,limit);ok(v.status==="TIMEOUT"&&v.t===limit,"cutoff "+limit);}
  ok(P.run(M,raw,clock).prepared===R.producer(raw).prepared,"exact budget");
  return{which,q:C.q,descriptorBits:C.desc.length,controls,cutoffs:7,exactBudget:clock};
 }else throw Error("unknown suite");
 return{which,q:C.q,descriptorBits:C.desc.length,serializationEntry:C.serializationEntry,rows,worker,totals:rows.reduce((a,r)=>({rawBits:a.rawBits+r.L,preparedBits:a.preparedBits+r.N,maskBits:a.maskBits+r.maskBits,rows:a.rows+r.allowedRows.reduce((p,q)=>p+q,0),transitions:a.transitions+r.t,serializationTransitions:a.serializationTransitions+r.serializationTransitions}),{rawBits:0,preparedBits:0,maskBits:0,rows:0,transitions:0,serializationTransitions:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_TERNARY_BAGS_OK '+JSON.stringify(audit(require('./f038_rex_ternary_bags.js'),require('./f038_rex_multitape_producer.js'),require('./f038_tga_normalized_integration.js').engine(),require('./f038_rex_nested_variable_overlap.js'),process.argv[2]||'small')));
