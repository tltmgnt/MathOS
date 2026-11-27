// REX-024D5E: explicit conservative whole-machine source-level resource envelope.
function ceilLog(x){if(x<1n)throw Error("positive integer");return x===1n?0n:BigInt((x-1n).toString(2).length);}
function bound(m){
 const M=BigInt(m);if(M<2n)throw Error("domain");
 const n=19n*M-7n,L=n+1n+2n*n*n+8n*n*(n-1n)*(n-2n)/6n,b=ceilLog(M),H=ceilLog(L);
 const B=9n*M+36n*M*M+84n*M**3n,S=2n*(b+M+B+131n);
 const N=512n*(b+1n)*M**4n;
 const P=(1n<<21n)*L*L,I=(1n<<16n)*L*L,W=(1n<<39n)*(b+1n)**3n*M**8n,O=(1n<<20n)*(b+1n)*M**5n;
 const total=P+I+W+O,span=16n*L+5n*N+n+4n;
 if(M**3n>L||b>H||S>4n*L||total**3n>(1n<<120n)*(H+1n)**9n*L**8n)throw Error("uniform algebra");
 return{m:M,n,L,b,H,B,S,N,P,I,W,O,total,span};
}
function threshold(ell=928445994n){
 ell=BigInt(ell);if(ell!==928445994n)throw Error("fixed audited quotient only");
 const C=40n,first=3n*(ell+C+96n),need=H=>3n*(ell+C+3n*ceilLog(H+1n));
 if(first<2n**31n||first>=2n**32n||need(first)!==first||need(first-1n)<=first-1n||2n**32n<need(2n**32n))throw Error("threshold");
 // On [first,2^32-1] the ceiling logarithm is 32.
 // On [2^k,2^(k+1)-1], k>=32, it is k+1; the lower
 // endpoint grows by 2^k while the required RHS grows by 9.
 return{ell,C,H0:first,LstrictExponent:first-1n,listingH:ceilDiv(ell,3n),proof:"dyadic lower endpoints"};
 function ceilDiv(a,b){return(a+b-1n)/b;}
}
function check(rows){
 return rows.map(r=>{
  const B=bound(r.m),ok=(v,s)=>{if(!v)throw Error(r.name+" "+s)};
  for(let [k,v] of [["P",r.producer],["I",r.bridge],["W",r.worker],["O",r.projection]])ok(BigInt(v)<=B[k],"phase "+k);
  ok(BigInt(r.t)===BigInt(r.producer)+BigInt(r.bridge)+BigInt(r.worker)+BigInt(r.projection)&&BigInt(r.t)<=B.total,"total");
  ok(BigInt(r.span)<=B.span,"span");
  const ell=928445994n,slot=ell+ceilLog(BigInt(r.t));
  return{...r,slot:r.witness===null?null:slot.toString(),bounds:Object.fromEntries(Object.entries(B).map(([k,v])=>[k,v.toString()]))};
 });
}
module.exports={ceilLog,bound,threshold,check};
