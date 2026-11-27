// D6W: independently test all ordinary scope/bit deposit continuations.
function audit(P,Old){
 const ok=(v,m)=>{if(!v)throw Error(m);};
 const make=P=>{const c=P.compile(true),m=P.decode(c.desc);return {c,m,ids:new Map(c.names.map(([n,f],i)=>[n+"|"+f,i]))};};
 const A=make(P),B=make(Old),scopes=[[]];
 for(let k=1;k<=3;k++){function sub(a,j){if(a.length===k){scopes.push(a);return;}for(let g=j;g<9;g++)sub([...a,g],g+1);}sub([],0);}
 const layout=blocks=>"2"+blocks.slice().reverse().map(x=>x+"2").join("");
 function run(X,start,end,s,h,expected,delta){
  const a=new Uint8Array(4096);a.fill(2);const base=512;for(let i=0;i<s.length;i++)a[base+i]=+s[i];
  let q=X.ids.get(start+"|0"),dest=X.ids.get(end+"|0"),head=base+h,t=0;
  ok(q!==undefined&&dest!==undefined,"root "+start+" "+end);
  while(q!==dest&&q<X.m.q&&t<100000){const v=X.m.T[3*q+a[head]];a[head]=v>>2&3;head+=(v&3)-1;q=v>>>4;t++;}
  ok(q===dest&&head===base+h+1,"boundary "+start+" "+JSON.stringify({q,dest,head,h,t}));
  for(let i=0;i<a.length;i++){const j=i-base+delta;ok(a[i]===(j>=0&&j<expected.length?+expected[j]:2),"buffer "+start+" "+i);}
  return t;
 }
 let checks=0,pins=0,unary=0,packed=0,folds=0,transitions=0;
 for(let target=0;target<130;target++){
  const h=scopes[target],k=h.length,start=k?"covered"+h.join("_"):"pinFirst";
  for(const bit of [0,1])for(const z of [0,1,2,3])for(const rest of ["","11","10111"]){
   const blocks=Array.from({length:130},(_,i)=>i%3===0?"":i%3===1?"11":"101");
   blocks[target]="0".repeat(z)+rest;
   const pre=layout(blocks),workspace="0101010012"+"001010010010100101002",tail=workspace+bit+"0000000";
   const s=pre+tail,pos=pre.length+workspace.length-1;
   const v=k?bit:1-bit;let word;
   if(k>=2&&v===0&&z===3){word="101"+rest;folds++;}
   else word=(k>=2&&v===1?"11":String(v))+blocks[target];
   const delta=word.length-blocks[target].length;blocks[target]=word;
   const expected=layout(blocks)+workspace+"2"+"0000000",end=k?"bits"+k+"OptionalS0V"+bit:"pinStart"+bit;
   const a=run(A,start,end,s,pos,expected,delta),b=run(B,start,end,s,pos,expected,delta);
   ok(a===b,"clock parity "+start);checks++;transitions+=a;if(k===0)pins++;else if(k===1)unary++;else packed++;
  }
 }
 return {checks,pins,unary,packed,folds,transitions};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require("./f038_rex_width_three_shared_deposit_producer.js"),require("./f038_rex_width_three_batched_deposit_producer.js"))));
