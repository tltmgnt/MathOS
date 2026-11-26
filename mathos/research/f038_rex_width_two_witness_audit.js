// REX-023D3 original Boolean witness differential tests.
function audit(P,E,suite="small"){
 const C=P.compile(),M={...P.decode(C.desc),workerEntry:C.workerEntry,selectionEntry:C.selectionEntry,witnessEntry:C.witnessEntry,translationEntry:C.translationEntry},ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 const equality=(m,a,b)=>[...E.tup(m,2)].filter(([x,y])=>x!==y).map(([x,y])=>[-(m*a+x+1),-(m*b+y+1)]);
 function check(name,m,pins,B,want,expected=null){
  const raw=E.encode(m,pins,B),D=E.decode(raw),r=P.run(M,raw,3000000000,true);
  ok(D&&r.status===want,name+" "+JSON.stringify(r));let models=0;
  for(let z of E.tup(m,9))if(D.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))models++;
  let ranks=null;
  if(want==="WITNESS"){
   const w=Math.ceil(Math.log2(m)),R=27*(w+1);ok(r.rankWord.length===R&&r.forestWord.endsWith("1"+r.rankWord),"rank suffix");
   ranks=[];for(let i=0;i<9;i++){let field=r.rankWord.slice(i*3*(w+1),(i+1)*3*(w+1)),z=0;for(let j=0;j<w;j++){let tok=field.slice(3*j,3*j+3);ok(tok==="000"||tok==="001","rank token");z=2*z+Number(tok[2]);}ok(field.endsWith("010")&&z<m,"rank field");ranks.push(z);}
   if(expected)ok(ranks.join()===expected.join(),"expected deterministic ranks");
   ok(models>0&&r.bits===E.witness(m,pins,ranks)&&r.bits.length===19*m-7&&E.valid(raw,r.bits),"original witness");
   ok(r.head===raw.length-1+r.forestWord.length+2,"physical halt head");
   ok(r.workerAt<r.selectionAt&&r.selectionAt<r.witnessAt&&r.witnessAt<r.translationAt&&r.translationAt<r.t,"phase order");
  }else{
   ok(r.bits===null&&r.witnessAt===null&&r.translationAt===null&&r.selectionAt===null,"blank refusal");
   ok(want==="FOREST_UNSAT"?models===0&&r.workerAt!==null:models>0&&r.workerAt===null,"decision scope");
  }
  rows.push({name,m,L:raw.length,models,status:r.status,t:r.t,head:r.head,span:r.span,workerAt:r.workerAt,selectionAt:r.selectionAt,witnessAt:r.witnessAt,translationAt:r.translationAt,translation:r.witnessAt===null?0:r.t-r.witnessAt,rankBits:r.rankWord?.length??0,ranks,bits:r.bits});
  return{raw,r};
 }
 if(suite==="small"){
  check("empty",2,[0,0],[],"WITNESS",Array(9).fill(0));
  check("outside-triple",2,[1,0],[[-1,-9,-17]],"WITNESS",[1,0,0,0,0,0,0,0,0]);
  check("nonmonotone-star",2,[1,1],[[-1,-3],[-2,-5],[-1,-7],[-2,-9],[-1,-11],[-2,-13],[-1,-15],[-2,-17],[-4]],"WITNESS",[1,0,1,0,1,0,1,0,1]);
  check("nonfirst-chain",2,[0,1],[...equality(2,0,4),...equality(2,4,8),[-17]],"WITNESS",[1,0,0,0,1,0,0,0,1]);
  let B=[...E.tup(2,3)].filter(z=>z[0]!==z[2]).map(z=>[0,1,8].map((v,i)=>-(2*v+z[i]+1)));for(let v=2;v<=7;v++)B.push([-1,-(2*v+1)],[-(2*v+1),-17]);B.push([-1],[-17]);
  check("middle-owner-joint-sat",2,[1,1],B,"WITNESS",[1,0,0,0,0,0,0,0,1]);
  check("nonempty-inconsistent",2,[0,1],[...equality(2,0,4),...equality(2,4,8),[-2],[-17]],"FOREST_UNSAT");
  let pair=[...E.tup(2,3)].filter(z=>z[1]!==z[2]).map(z=>[0,4,8].map((v,i)=>-(2*v+z[i]+1)));pair.push([-9,-17],[-10,-18]);check("joint-pair-inconsistent",2,[1,0],pair,"FOREST_UNSAT");
  check("disconnected-unsat",2,[0,0],[[-1,-7,-17],[-3],[-4],[-5,-13]],"FOREST_UNSAT");
  check("unary-unsat",2,[0,1],[[-1],[-2]],"FOREST_UNSAT");
  check("K4-SAT-refusal",2,[1,1],[...E.subsets([0,1,2,3],2)].map(h=>h.map(v=>-(2*v+1))),"REFUSAL");
 }else if(suite==="larger"){
  let seed=0x52455823;const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  let H=[[0,4,8],[1,4,8],[2,5,6],[3,7],[0],[8],[4,8]];
  check("m3-mixed",3,[1,0,1],H.flatMap(h=>[...E.tup(3,h.length)].filter(()=>rnd()>>>24<100).map(z=>h.map((g,i)=>-(3*g+z[i]+1)))),"WITNESS",[1,1,0,0,1,0,0,0,0]);
 }else if(suite==="ranktwo"){
  const z=[2,1,0,2,0,1,2,1,0],B=z.flatMap((a,g)=>[0,1,2].filter(i=>i!==a).map(i=>[-(3*g+i+1)]));
  B.push([-1,-13,-25]);check("m3-rank-two",3,[0,1,1],B,"WITNESS",z);
 }else if(suite==="controls"){
  let raw=E.encode(2,[1,0],[[-1,-9,-17]]),r=P.run(M,raw,100000000),controls=[];
  for(let k of [0,1,100,r.workerAt-1,r.workerAt,r.selectionAt-1,r.selectionAt,r.witnessAt-1,r.witnessAt,r.translationAt-1,r.translationAt,r.t-1]){
   let x=P.run(M,raw,k);ok(x.status==="TIMEOUT"&&x.t===k,"cutoff");controls.push(k);
  }ok(P.run(M,raw,r.t).bits===r.bits,"exact budget");
  let n=31,pos=new Map(),at=n+1;for(let c of E.pool(n))pos.set(c.join(),at++);
  const flip=(s,i)=>s.slice(0,i)+(s[i]==="1"?"0":"1")+s.slice(i+1),rejects=[];
  for(let [name,s] of [["empty",""],["n1","1000"],["n2","110"+"0".repeat(8)],["header","1".repeat(32)+"0"],["mandatory",flip(raw,pos.get("-31"))],["late-pin",flip(raw,pos.get("-28,-30,-31"))],["truncated",raw.slice(0,-1)],["extra",raw+"1"],["invalid-positive",flip(raw,pos.get("1,17"))]]){
   let v=P.run(M,s,100000000);ok(v.status==="REFUSAL"&&v.bits===null&&v.workerAt===null,"blank refusal "+name);rejects.push({name,t:v.t});
  }
  return{suite,q:C.q,descriptorBits:C.desc.length,controls,rejects,exactBudget:r.t};
 }else throw Error("suite");
 return{suite,q:C.q,descriptorBits:C.desc.length,rows,totals:rows.reduce((a,r)=>({rawBits:a.rawBits+r.L,transitions:a.transitions+r.t,translation:a.translation+r.translation,witnessBits:a.witnessBits+(r.bits?.length??0),rankBits:a.rankBits+r.rankBits,sat:a.sat+ +(r.status==="WITNESS"),unsat:a.unsat+ +(r.status==="FOREST_UNSAT"),refused:a.refused+ +(r.status==="REFUSAL")}),{rawBits:0,transitions:0,translation:0,witnessBits:0,rankBits:0,sat:0,unsat:0,refused:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_WIDTH_TWO_WITNESS_OK '+JSON.stringify(audit(require('./f038_rex_width_two_witness.js'),require('./f038_tga_normalized_integration.js').engine(),process.argv[2]||'small')));
