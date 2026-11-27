// D6V: independent emitted-table audit for all triple-scope batch roots.
// Checks actual tape rows, not helper implementation.
function audit(P){
 const C=P.compile(true),M=P.decode(C.desc),ids=new Map(C.names.map(([n,f],i)=>[n+"|"+f,i])),ok=(v,m)=>{if(!v)throw Error(m);};
 function id(n){const i=ids.get(n+"|0");ok(i!==undefined,"missing "+n);return i;}
 let fitChecks=0,scopeRoots=0,tailChecks=0,failChecks=0,truncationChecks=0,transitions=0;
 function run(start,ends,layout,h,expected,offset=0){
  const a=new Uint8Array(4096);a.fill(2);const base=256;for(let i=0;i<layout.length;i++)a[base+i]=+layout[i];
  let q=id(start),head=base+h,t=0;const endIds=ends.map(id);
  while(!endIds.includes(q)&&q<M.q&&t<100000){const v=M.T[3*q+a[head]];a[head]=(v>>>2)&3;head+=(v&3)-1;q=v>>>4;t++;}
  ok(endIds.includes(q)&&head===base+h,"alignment "+start+" "+JSON.stringify({q,t,head,h:base+h}));
  for(let i=0;i<a.length;i++){const j=i-base-offset;ok(a[i]===(j>=0&&j<expected.length?+expected[j]:2),"buffer "+start+" at "+i);}
  transitions+=t;return C.names[q][0];
 }
 // Independent arithmetic comparison on all ranks for small domains,
 // and boundary cases across wide binary counters.
 const bounds=[];for(let m=2;m<=65;m++)for(let c=0;c<m;c++)bounds.push([BigInt(m-1),BigInt(c)]);
 for(const k of [8n,16n,32n,64n,128n])for(const d of [-1n,0n,1n]){const m=(1n<<k)+d;for(const c of [0n,1n,m-4n,m-3n,m-2n,m-1n])bounds.push([m-1n,c]);}
 for(const [M0,c] of bounds){const w=M0.toString(2).length,cols=Array.from({length:w},(_,i)=>{const bit=BigInt(w-1-i);return String((M0>>bit)&1n)+"000"+String((c>>bit)&1n);}).join(""),s="2"+cols+"0000000000000002";
  const result=run("class3",["class3Fast","class3Normal"],s,s.length-1,s);
  ok(result===(c+3n<=M0?"class3Fast":"class3Normal"),"fit "+M0+" "+c);fitChecks++;
 }
 // Independently enumerate 130 scope blocks in canonical source order.
 const scopes=[];for(let k=1;k<=3;k++){function sub(a,j){if(a.length===k){scopes.push(a);return;}for(let g=j;g<9;g++)sub([...a,g],g+1);}sub([],0);}
 const build=(blocks)=>"2"+blocks.slice().reverse().map(x=>x+"2").join("");
 for(let j=0;j<scopes.length;j++){const h= scopes[j];if(h.length!==3)continue;const n="covered"+h.join("_"),target=j+1;scopeRoots++;
  // Distinct nonempty, empty and packed blocks exercise separator carries.
  for(let z=0;z<=3;z++)for(const rest of ["","11","10111"]){
   const blocks=Array.from({length:130},(_,i)=>i%3===0?"":i%3===1?"11":"101");blocks[target]="0".repeat(z)+rest;
   const prefix=build(blocks),tail="0101010012"+"001010010010100101002",raw="0".repeat(32)+"10000111",layout=prefix+tail+raw,head=prefix.length+tail.length-1;
   blocks[target]="0".repeat(z)+"101"+rest;
   const expected=build(blocks)+tail+raw;
   run(n+"Try4",["fastConsume0"],layout,head,expected,-3);tailChecks++;
  }
  // Failed lookahead must not mutate the tape or move the head.
  for(let i=0;i<32;i++){
   const prefix="2010020002",layout=prefix+"0".repeat(i)+"1"+"0".repeat(31-i)+"1";
   run(n+"Try4",[n],layout,prefix.length-1,layout);failChecks++;
   const short=prefix+"0".repeat(i);
   run(n+"Try4",[n],short,prefix.length-1,short);truncationChecks++;
  }
 }
 return {fitChecks,scopeRoots,tailChecks,failChecks,truncationChecks,transitions};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require("./f038_rex_width_three_batched_deposit_producer.js"))));
