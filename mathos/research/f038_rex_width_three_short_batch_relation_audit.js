// D6W: exhaustive transition-row simulation certificate for ordinary
// deposit regions, including malformed internal symbols up to exits.
// No execution/tape-length assumption in this local relation.
function audit(P,Old){
 const make=P=>{const c=P.compile(true),m=P.decode(c.desc);return {c,m,ids:new Map(c.names.map(([n,f],i)=>[n+"|"+f,i]))};};
 const A=make(P),B=make(Old),ok=(v,m)=>{if(!v)throw Error(m);};
 const relation=new Map(),queue=[],ends=new Set(),targets=new Set();
 const name=(X,q)=>q===X.m.q?"HALT":X.c.names[q].join("|");
 const exit=n=>/^(bits[123]OptionalS0V[01]|pinStart[01]|clean0|BROKEN)\|0$/.test(n)||n==="HALT";
 function pair(b,a){
  const bn=name(B,b),an=name(A,a);
  if(exit(bn)||exit(an)){ok(bn===an,"exit "+bn+" "+an);ends.add(bn);return;}
  if(relation.has(b)){ok(relation.get(b)===a,"inconsistent mapping "+bn+" "+an);return;}
  relation.set(b,a);targets.add(a);queue.push([b,a]);
 }
 let roots=0,checks=0;
 for(const [n,f] of B.c.names)if(f===0&&(n==="pinFirst"||/^covered[0-8](?:_[0-8]){0,2}$/.test(n))){
  const b=B.ids.get(n+"|0"),a=A.ids.get(n+"|0");ok(a!==undefined,"root "+n);pair(b,a);roots++;
 }
 for(let i=0;i<queue.length;i++){
  const [b,a]=queue[i];for(let s=0;s<3;s++){
   const u=B.m.T[3*b+s],v=A.m.T[3*a+s];
   ok((u&15)===(v&15),"write/direction "+name(B,b)+" "+name(A,a)+" symbol "+s);
   pair(u>>>4,v>>>4);checks++;
  }
 }
 ok(roots===130&&ends.size===10,"coverage "+JSON.stringify([...ends]));
 return {roots,predecessorStates:relation.size,sharedStates:targets.size,transitionChecks:checks,exits:[...ends].sort()};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require("./f038_rex_width_three_short_batch_producer.js"),require("./f038_rex_width_three_batched_deposit_producer.js"))));
