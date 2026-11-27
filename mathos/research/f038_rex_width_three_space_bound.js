// Conservative explicit storage envelope for the 61-tape legitimate worker layout.
function space(m){
 if(!Number.isSafeInteger(m)||m<2)throw Error("domain");
 const M=BigInt(m),b=BigInt((M-1n).toString(2).length),B=9n*M+36n*M*M+84n*M*M*M,S=2n*(b+M+B+131n),R=4n*(b+1n)*M**4n,K=(14n*b+17n)*M**4n;
 const max=(...xs)=>xs.reduce((a,b)=>a>b?a:b);
 // Data word capacities by tape, before adding L and one spare blank.
 const caps=[b,4n,28n,...Array(7).fill(M**3n),...Array(4).fill(max(27n,b)),...Array(3).fill(max(7n,M)),R,1n,851n,S,9n,...Array(9).fill(R),180n,81n,4n,...Array(7).fill(K),4n,4n,R,1n,...Array(9).fill(b),9n,b,b,19n*M-7n,9n*(M-1n),1n,1n];
 if(caps.length!==61)throw Error("layout");
 // Each tape has L, its maximum word, and a blank at its end.
 // 1 global G and 61 separators.
 return {m,b,B,S,R,K,caps,N:1n+BigInt(caps.length)*3n+caps.reduce((a,b)=>a+b,0n)};
}
module.exports={space};
