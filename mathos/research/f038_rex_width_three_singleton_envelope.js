// D5H conditional quadratic source-level bound and adaptive IR reference checks.
function envelope(m,ell=124696396n){
 m=BigInt(m);ell=BigInt(ell);if(m<2n||![124696396n,124697764n].includes(ell))throw Error("scope");
 const b=BigInt((m-1n).toString(2).length),n=19n*m-7n,L=n+1n+2n*n*n+8n*n*(n-1n)*(n-2n)/6n,H=BigInt((L-1n).toString(2).length);
 const B=9n*m+36n*m*m+84n*m**3n,S=2n*(b+m+B+131n);
 const N=S+32n*m+486n,T=32n*B+16000n*(m+1n)+5000n;
 const P=256n*L*(131n*L+2176n)+(1n<<40n),I=128n*S*S,W=(26n*N+16n)*T+8n,O=16n*(n+1n)*(5n*N+n+1n);
 const total=P+I+W+O,ok=(v,s)=>{if(!v)throw Error(s)};
 ok(L>=4096n*m**3n&&S<=256n*m**3n&&16n*S<=L,"layout");
 ok(N<=2n*S&&T<=128n*S&&n+1n<=S&&S>=1936n,"IR");
 ok(P<=35000n*L*L&&W<=8192n*S*S&&O<=256n*S*S,"phase");
 ok(total<=65536n*L*L,"quadratic");
 return {m,n,L,H,b,B,S,N,T,P,I,W,O,total,H0:ell+16n};
}

function arithmetic(){
 let count=0;for(let m=2n;m<=10000n;m++){envelope(m);count++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n]){envelope((1n<<k)+d);count++;}
 let boundary=0;for(const ell of [124696396n,124697764n])for(const d of [-1n,0n,1n]){const h=ell+16n+d;if((h>=ell+16n)!==(ell+16n+2n*h<=3n*h))throw Error("threshold");boundary++;}
 return {count,boundary,thresholds:[124696412n,124697780n].map(String)};
}

function experiment(U,E,Fast,Ad){
 const J=U.machine(true),strict=U.machine(false),rows=[];let checked=0,accepted=0,refused=0,falseNegative=0,strictChecked=0;
 const test=(name,m,pins,clauses)=>{
  const raw=E.encode(m,pins,clauses),decoded=E.decode(raw),s=U.stream(E,raw),I=[...Array(15).fill(""),s],allowed=Array.from({length:9},(_,g)=>Array.from({length:m},(_,i)=>i).filter(i=>!clauses.some(c=>c.length===1&&c[0]===-(g*m+i+1))));
  const z=allowed.map(a=>a[0]),valid=z.every(x=>x!==undefined)&&clauses.every(c=>!c.every(x=>z[Math.floor((-x-1)/m)]===(-x-1)%m)),forced=allowed.every(a=>a.length===1),r=U.executeIR(J,I),q=U.executeIR(strict,I);
  if((r.status==="halt")!==valid||(q.status==="halt")!==(valid&&forced))throw Error("oracle "+name);
  checked++;strictChecked++;if(valid){accepted++;if(r.tapes[0]!==E.witness(m,pins,z)||!E.valid(raw,r.tapes[0]))throw Error("raw witness");const a=Fast.count(J,I),e=envelope(m,124697764n);
   if(BigInt(a.steps)>e.T||BigInt(a.N)>e.N||BigInt(a.clock)>e.W||a.tapes[0]!==r.tapes[0])throw Error("resource");
   rows.push({name,m,steps:a.steps,N:a.N,worker:a.clock});
  }else{refused++;if(allowed.every(a=>a.length)&&m<=4){let sat=false;for(const z of E.tup(m,9)){if(decoded.F.every(f=>f.S.has(f.h.map(g=>z[g]).join()))){sat=true;break;}}if(sat)falseNegative++;}}
 };
 for(let m=2;m<=6;m++){
  const pins=Array.from({length:m},(_,i)=>i%2),z=Array.from({length:9},(_,g)=>(g+1)%m),un=z.flatMap((a,g)=>Array.from({length:m},(_,i)=>i===a?null:[-(g*m+i+1)]).filter(Boolean));
  test("empty-"+m,m,pins,[]);test("forced-"+m,m,pins,un);
  const partial=un.filter(c=>Math.floor((-c[0]-1)/m)<4);
  const chosen=z.map((a,g)=>g<4?a:0),forbid=gs=>gs.map(g=>-(g*m+chosen[g]+1));
  test("partial-"+m,m,pins,partial);
  test("partial-conflict-"+m,m,pins,partial.concat([forbid([3,4])]));
  test("triple-conflict-"+m,m,pins,partial.concat([forbid([3,4,5])]));
  test("triple-safe-"+m,m,pins,partial.concat([[-(3*m+(chosen[3]+1)%m+1),...forbid([4,5])]]));
  test("empty-domain-"+m,m,pins,un.concat([[-(z[0]+1)]]));
 }
 for(const f of Ad.fixtures(E,"all"))if(f.name!=="K5-refusal")test(f.name,f.m,f.pins,f.B);
 return {checked,strictChecked,accepted,refused,falseNegative,rows};
}
function parentLedger(){
 // D5G completed physical CI run 45938789950; transition counts, not fresh execution.
 const rows=[[2,104551138,127995984,288770504,289549660],[3,1191370586,1376249438,2149443850,2152510163],[4,6899458662,7805874734,10990889184,10999810416]];
 return rows.map(([m,p,i,w,t])=>{const B=envelope(m),a=[p,i-p,w-i,t-w];if(a.some((v,j)=>BigInt(v)>[B.P,B.I,B.W,B.O][j])||BigInt(t)>B.total)throw Error("parent phase ledger");return {m,phases:a,total:t};});
}
module.exports={envelope,arithmetic,experiment,parentLedger};
if(require.main===module){const U=require('./f038_rex_width_three_adaptive_ir.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),Ad=require('./f038_rex_width_three_admission.js');console.log(JSON.stringify({arithmetic:arithmetic(),experiment:experiment(U,E,F,Ad),parentLedger:parentLedger()}));}
