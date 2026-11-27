// F038-REX-024D5F independent arithmetic and normalized-rank shortcut experiment.
// The shortcut assumes a validated normalized selector and optional negative clauses.
// Host-level only: no physical compiler, no original descriptor, no admission claim.
function audit(){
 const assert=(p,s)=>{if(!p)throw Error(s)}, cl=x=>x===1n?0n:BigInt((x-1n).toString(2).length),ell=928445994n,C=3n*ell+120n;
 const rhs=h=>C+cl((h+1n)**9n), old=2785338390n;
 let h=C;while(h<rhs(h))h=rhs(h);
 assert(h===2785338385n&&rhs(h)===h&&rhs(h-1n)>h-1n,"threshold");
 assert(18n**9n<2n*17n**9n,"monotone ceiling growth for H>=16");
 const desc=q=>4n+q+3n*q*(BigInt(q.toString(2).length)+4n);
 assert(desc(10922894n)===ell&&desc(1n)===20n&&desc(2n)===42n&&desc(3n)===61n,"descriptor grammar");
 let paths=1n,p=1n;for(let j=9n;j>=1n;j--){p*=j;paths+=p;}
 assert(paths===986410n&&paths<2n**20n,"DFS path count");
 let algebra=0;
 for(let m=2n;m<=10001n;m++){
  const n=19n*m-7n,L=n+1n+2n*n*n+8n*n*(n-1n)*(n-2n)/6n,b=cl(m),H=cl(L),B=9n*m+36n*m*m+84n*m**3n,S=2n*(b+m+B+131n),N=512n*(b+1n)*m**4n;
  const P=2n**21n*L*L,I=2n**16n*L*L,W=2n**39n*(b+1n)**3n*m**8n,O=2n**20n*(b+1n)*m**5n;
  assert(m**3n<=L&&b<=H&&L>=37914n&&S<=4n*L,"layout algebra");
  assert(256n*L*(128n*(L+1n)+2048n+3n*L)+2n**40n<=P,"producer arithmetic");
  assert((5n*L+2n)*128n*L<=I,"bridge arithmetic");
  assert(16n*(n+1n)*(5n*N+n+1n)<=O,"projection arithmetic");
  assert((P+I+W+O)**3n<=2n**120n*(H+1n)**9n*L**8n,"combined arithmetic");algebra++;
 }
 let boundary=0;for(const v of [h-1n,h,h+1n,old,...Array.from({length:64},(_,i)=>1n<<BigInt(i+32)).flatMap(v=>[v-1n,v,v+1n])]){assert((v>=h)===(v>=rhs(v)),"boundary");boundary++}
 const finite=[[2n,825112955n],[2n,1297519076n],[3n,72540199790n],[4n,299944027294n]].map(([m,t])=>{
  const n=19n*m-7n,L=n+1n+2n*n*n+8n*n*(n-1n)*(n-2n)/6n,H=cl(L),s=3n*H,maxBits=s-cl(t),oneBudget=2n**(s-desc(1n)),twoBudget=2n**(s-desc(2n));
  assert(maxBits<desc(1n)&&desc(2n)<=s&&desc(3n)>s&&twoBudget<L-1n,"finite tradeoff");
  return {m,L,H,s,t,maxBits,oneBudget,twoBudget};
 });
 return {algebra,boundary,threshold:h,old,paths,finite};
}

function singleton(m,clauses){
 const allowed=Array.from({length:9},()=>Array(m).fill(true));
 for(const c of clauses)if(c.length===1){const v=-c[0]-1;allowed[Math.floor(v/m)][v%m]=false;}
 const ranks=allowed.map(a=>a.flatMap((v,i)=>v?[i]:[]));
 if(ranks.some(a=>!a.length))return {status:"UNSAT"};
 if(ranks.some(a=>a.length!==1))return {status:"FALLBACK"};
 const z=ranks.map(a=>a[0]);
 const ok=clauses.every(c=>!c.every(x=>{const v=-x-1;return z[Math.floor(v/m)]===v%m;}));
 return ok?{status:"SAT",z}:{status:"UNSAT"};
}

function singletonAudit(){
 const assert=(p,s)=>{if(!p)throw Error(s)};
 let cases=0,tuples=0;
 for(const m of [2,3,4]){
  const z=Array.from({length:9},(_,g)=>(m-1-(g%m))),u=z.flatMap((a,g)=>Array.from({length:m},(_,i)=>i).filter(i=>i!==a).map(i=>[-(g*m+i+1)]));
  const p=[0,3,6,8],edges=p.flatMap((a,i)=>p.slice(i+1).map(b=>[-(a*m+1),-(b*m+1)]));
  for(const [B,status] of [[u.concat(edges),"SAT"],[u.concat([[-(z[0]+1),-(m+z[1]+1)]]),"UNSAT"],[u.concat([[-(z[0]+1)]]),"UNSAT"],[[],"FALLBACK"]]){
   const r=singleton(m,B);assert(r.status===status,"shortcut status");
   let hits=0;for(let i=0;i<m**9;i++){const a=Array.from({length:9},(_,g)=>Math.floor(i/m**g)%m);if(B.every(c=>!c.every(x=>{const v=-x-1;return a[Math.floor(v/m)]===v%m;})))hits++;tuples++;}
   assert(status==="FALLBACK"?hits===m**9:status==="SAT"?hits===1&&r.z.join()===z.join():hits===0,"exhaustive reference");cases++;
  }
 }
 return {cases,tuples};
}
module.exports={audit,singleton,singletonAudit};
if(require.main===module)console.log(JSON.stringify({...audit(),shortcut:singletonAudit()},(_,v)=>typeof v==='bigint'?v.toString():v));
