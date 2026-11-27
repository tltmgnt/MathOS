// D5Y in-place hybrid interval, independent witness and clock comparison.
function envelope(V,m,full=false){
 const e=V.envelope(m),k=BigInt(m),S=e.S,b=BigInt((k**3n+1n).toString(2).length);
 const N=S+35n*k+1600n+5n*k**3n+4n*b+32n,T=65536n*S*(b+1n)*(full?k:1n),W=(20n*N+12n)*T+6n,P=4n*e.P+32n*e.L,total=P+128n*S*S+W+1024n*S*S;
 if(N>3n*S||b>e.H||total>1048576n*(b+1n)*e.L*e.L*(full?k:1n))throw Error("envelope");
 return {N,T,W,total};
}
function audit(U,W,Gap,Old,E,F,V,R,Prior,PriorW){
 const J=[U.machine(W,Gap,false),U.machine(W,Gap,true)],O=[Old.machine(false),Old.machine(true)],ok=(x,s)=>{if(!x)throw Error(s)};
 const H=[Prior.machine(PriorW,Gap,false),Prior.machine(PriorW,Gap,true)];let cases=0,accepted=0,refused=0,arith=0,regressions=0,streamChecks=0,vsPersistentGain=0,vsPersistentLoss=0,gammaFields=0,runFields=0;const rows=[];
 for(let m=2;m<=10000;m++)for(const full of [false,true]){envelope(V,m,full);arith++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n])for(const full of [false,true]){envelope(V,(1n<<k)+d,full);arith++;}
 function test(name,m,clauses,detail=false){
  const pins=Array.from({length:m},(_,i)=>i%2),raw=E.encode(m,pins,clauses),s=Old.stream(E,raw),I=[...Array(21).fill(""),s],want=W.persistentStream(E,raw,R);
  const fields=want.match(/(?:00|01|11|xx)*10/g),original=s.match(/(?:00|01|11)*10/g);ok(fields.join("")===want&&fields.length===131&&want.length===s.length,"framing");for(let j=0;j<131;j++){const f=fields[j];ok(f.length===original[j].length,"interval");if(f.startsWith("xx")){gammaFields++;let g=f.slice(2,-2).replace(/xx+$/,"");ok(R.decode("1"+g.match(/0[01]/g).map(t=>t[1]).join(""),original[j].slice(0,-2).match(/../g).reduce((a,t)=>a+(t==="11"?4:1),0))===original[j].slice(0,-2).match(/../g).map(t=>t==="11"?"0000":t[1]).join(""),"gap expansion");}else {ok(f===original[j],"run interval changed");if(j>=11&&f!=="10")runFields++;}}
  for(let i=0;i<2;i++){
   const a=Old.executeIR(J[i],I),p=Old.executeIR(O[i],[...Array(19).fill(""),s]),e=envelope(V,m,!!i);
   ok(a.status===p.status&&a.tapes[0]===p.tapes[0]&&a.tapes[21]===want,"witness/stream "+name);
   ok(a.tapes.slice(1,10).join("|")===p.tapes.slice(1,10).join("|"),"domains "+name);streamChecks++;
   if(a.status==="halt"){const v=F.count(J[i],I),z=F.count(O[i],[...Array(19).fill(""),s]),h=F.count(H[i],I);if(v.clock<h.clock)vsPersistentGain++;else if(v.clock>h.clock)vsPersistentLoss++;ok(E.valid(raw,a.tapes[0])&&BigInt(v.N)<=e.N&&BigInt(v.steps)<=e.T&&BigInt(v.clock)<=e.W,"resource");accepted++;if(v.clock>z.clock)regressions++;
    if(detail&&i===0)rows.push({name,m,prior:z.clock,persistent:h.clock,hybrid:v.clock,regions:[z.N,h.N,v.N],stream:[s.length,want.length],steps:v.steps});
   }else refused++;
  }cases++;
 }
 test("empty",2,[],true);test("chain",2,[[-1],[-3],[-2,-4,-5],[-4,-6,-7],[-6,-8,-9]],true);
 test("third",3,[[-1],[-2],[-4],[-5],[-3,-6,-7],[-3,-6,-8]],true);
 test("all-active",2,[2,3].flatMap(k=>[...E.subsets([0,1,2,3,4,5,6,7,8],k)].map(h=>h.map(g=>-(2*g+2)))),true);
 test("empty-domain",2,[[-1],[-2]]);test("radius-three",2,[[-1,-3],[-5,-7],[-9,-11]]);
 test("reverse-chain",2,[[-18],...Array.from({length:8},(_,i)=>[-(2*i+2),-(2*(i+1)+1)])]);
 for(let v=0;v<256;v++){const clauses=[];for(let i=0;i<8;i++)if(v>>i&1)clauses.push([-(1+(i>>2)),-(3+((i>>1)&1)),-(5+(i&1))]);test("mask-"+v,2,clauses);}
 test("sparse-m5",5,[[-5,-10,-15]],true);
 test("multi-sparse-m5",5,[[-5,-10,-15],[-10,-15,-20]],true);
 test("long-dense-m3",3,[...E.tup(3,3)].map(z=>z.map((v,i)=>-(3*i+v+1))),true);
 return {cases,accepted,refused,regressions,streamChecks,arith,vsPersistentGain,vsPersistentLoss,gammaFields,runFields,rows};
}
module.exports={envelope,audit};
if(require.main===module){const p='./f038_rex_width_three_';console.log(JSON.stringify(audit(require(p+'inplace_hybrid_integration_ir.js'),require(p+'inplace_hybrid_gac_ir.js'),require(p+'persistent_gap_encoder.js'),require(p+'cost_ir.js'),require('./f038_tga_normalized_integration.js').engine(),require(p+'fast_clock.js'),require(p+'singleton_envelope.js'),require(p+'gap_reference.js'),require(p+'hybrid_integration_ir.js'),require(p+'hybrid_gac_ir.js'))));}
