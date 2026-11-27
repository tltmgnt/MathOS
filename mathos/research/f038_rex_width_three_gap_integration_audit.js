// D5U in-place integration regression, independent decoder budget fault
// injection, conditional source-level resource accounting.
function envelope(V,m,full=false){
 const e=V.envelope(m),k=BigInt(m),S=e.S,b=BigInt((k**3n+1n).toString(2).length),N=S+35n*k+1479n+5n*k**3n+4n*b+32n,
 T=S*(49152n*(full?k:1n)+2048n*(b+1n)),W=(20n*N+12n)*T+6n,P=4n*e.P+32n*e.L,total=P+128n*S*S+W+256n*S*S;
 const scale=full?k:b+1n;
 if(N>3n*S||b+1n>4n*k||b>e.H||total>262144n*scale*e.L*e.L)throw Error("envelope");
 return {N,T,W,total};
}
function audit(U,Copy,W,Gap,E,F,V,R,K){
 const J=[U.machine(W,Gap,false),U.machine(W,Gap,true)],O=[W.machine(false),W.machine(true)],C=Copy.machine(W,Gap,false),ok=(x,s)=>{if(!x)throw Error(s)};
 let cases=0,accepted=0,refused=0,arith=0,regressions=0,budgetChecks=0,budgetRefusals=0,physicalFaults=0;const rows=[];
 for(let m=2;m<=10000;m++)for(const full of [false,true]){envelope(V,m,full);arith++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n])for(const full of [false,true]){envelope(V,(1n<<k)+d,full);arith++;}
 function test(name,m,clauses,detail=false){
  const pins=Array.from({length:m},(_,i)=>i%2),raw=E.encode(m,pins,clauses),s=W.stream(E,raw),I=[...Array(19).fill(""),s];
  for(let i=0;i<2;i++){
   const a=W.executeIR(J[i],I),p=W.executeIR(O[i],I),e=envelope(V,m,!!i);
   ok(a.status===p.status&&a.tapes[0]===p.tapes[0]&&a.tapes[19]===s,"witness/stream "+name);
   ok(a.tapes.slice(1,19).join("|")===p.tapes.slice(1,19).join("|"),"terminal worker tapes "+name);
   if(a.status==="halt"){const v=F.count(J[i],I),z=F.count(O[i],I);ok(E.valid(raw,a.tapes[0])&&BigInt(v.N)<=e.N&&BigInt(v.steps)<=e.T&&BigInt(v.clock)<=e.W,"resource");accepted++;if(v.clock>z.clock)regressions++;
    if(detail&&i===0){const c=F.count(C,[...Array(20).fill(""),s]);rows.push({name,m,prior:z.clock,copy:c.clock,inplace:v.clock,regions:[z.N,c.N,v.N],steps:v.steps});}
   }else refused++;
  }cases++;
 }
 test("empty",2,[],true);test("chain",2,[[-1],[-3],[-2,-4,-5],[-4,-6,-7],[-6,-8,-9]],true);
 test("third",3,[[-1],[-2],[-4],[-5],[-3,-6,-7],[-3,-6,-8]],true);
 test("all-active",2,[2,3].flatMap(k=>[...E.subsets([0,1,2,3,4,5,6,7,8],k)].map(h=>h.map(g=>-(2*g+2)))),true);
 test("empty-domain",2,[[-1],[-2]]);test("radius-three",2,[[-1,-3],[-5,-7],[-9,-11]]);
 // All truth masks for one ternary scope; two-bit rank values, both modes.
 for(let v=0;v<256;v++){const clauses=[];for(let i=0;i<8;i++)if(v>>i&1)clauses.push([-(1+(i>>2)),-(3+((i>>1)&1)),-(5+(i&1))]);test("mask-"+v,2,clauses);}
 // Fault injection into the actual spliced decoder. Isolate its entry and
 // successful exit; leave all budget guards and decoding instructions unchanged.
 const B=U.machine(W,Gap,false);B.entry=B.budgetEntry;B.ins[B.decodeExit]={op:"jump",t:0,next:B.ins.findIndex(i=>i.op==="halt")};const M=K.compile(B);
 function check(code,n,expected,physical=false){
  const I=Array(20).fill("");I[2]=code;I[6]="1".repeat(n);
  const a=W.executeIR(B,I);ok(a.status===(expected===null?"reject":"halt")&&a.tapes[1].length<=n&&(expected===null||a.tapes[1]===expected),"budget "+code+" "+n);
  budgetChecks++;if(expected===null)budgetRefusals++;
  if(physical){const raw=["G",...I.flatMap((v,k)=>["hL",...[...v].map(x=>"u"+x),"u_",k===19?"E":"D"])].map(x=>M.codes[x]).join("");let tape=new Uint8Array(raw.length+8192);tape.fill(2);tape.set([...raw].map(Number),100);let h=100,s=0,t=0;while(s<M.q&&t<10000000){const v=M.T[3*s+tape[h]];tape[h]=v>>2&3;h+=(v&3)-1;s=v>>>4;t++;}
   ok(s===M.q+(expected!==null?1:0),"physical budget exit");physicalFaults++;}
 }
 for(let n=0;n<=8;n++)for(let v=0;v<2**n;v++){
  const s=n?v.toString(2).padStart(n,"0"):"",b=(n+1).toString(2),code="0".repeat(b.length-1)+b+R.encode(s);
  check(code,n,s);check(code,n+1,null);if(n)check(code,n-1,null);
 }
 // Header claims 64 zeros, but only two output positions are authorized.
 check("00000010000011",2,null,true);check("0101",0,null,true);check("0101",2,null,true);check("0101",1,"0",true);
 return {cases,accepted,refused,regressions,arith,budgetChecks,budgetRefusals,physicalFaults,rows};
}
module.exports={envelope,audit};
if(require.main===module){const U=require('./f038_rex_width_three_gap_inplace_ir.js'),Copy=require('./f038_rex_width_three_gap_integration_ir.js'),W=require('./f038_rex_width_three_cost_ir.js'),Gap=require('./f038_rex_width_three_gap_ir.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),R=require('./f038_rex_width_three_gap_reference.js'),K=require('./f038_rex_width_three_exit_compiler.js');console.log(JSON.stringify(audit(U,Copy,W,Gap,E,F,V,R,K)));}
