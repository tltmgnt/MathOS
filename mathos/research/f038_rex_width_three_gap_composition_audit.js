// D5T composition audit: actual FIFO producer from original selector through
// normalized checkpoint and loader. Independently inspect all 130 live blocks.
function audit(P,E,U){
 const C=P.compile(true),M=P.decode(C.desc),id=n=>C.names.findIndex(([x,f])=>x===n&&f===0),stop=id("loadStart"),header=id("class1"),ok=(x,s)=>{if(!x)throw Error(s)};
 const tags=Uint8Array.from(C.names,([n,f])=>f?0:/^class[123]$/.test(n)?1:/^advance[123]$/.test(n)?2:/^deposit\d+$/.test(n)?3:0);
 let cases=0,blocks=0,positions=0,rawBits=0;const rows=[];
 function test(name,m,pins,clauses){
  const raw=E.encode(m,pins,clauses),d=E.decode(raw),origin=raw.length+4096,T=new Uint8Array(3*raw.length+8192);T.fill(2);T.set([...raw].map(Number),origin);let s=0,h=origin,t=0,headerAt=-1,counts=[0,0,0,0];
  const step=()=>{ok(h>=0&&h<T.length&&s<M.q&&t<3000000000,"path");const v=M.T[3*s+T[h]];T[h]=v>>2&3;h+=(v&3)-1;s=v>>>4;t++;};
  while(s!==stop){if(s===header&&headerAt<0)headerAt=t;counts[tags[s]]++;step();}
  const normalizeAt=t;ok(h===origin+raw.length-1&&T[h]===2,"checkpoint head");let ptr=h,fields=[];
  for(let j=0;j<132;j++){const end=--ptr;while(T[ptr]<2)ptr--;fields.push(Array.from(T.slice(ptr+1,end+1)).join(""));}
  ok(T.slice(0,ptr+1).every(x=>x===2)&&T.slice(h+1).every(x=>x===2),"extent");
  ok(fields[1]===raw.slice(d.n+1)&&fields[2].split("").reverse().join("")===pins.join(""),"prefix/pins");
  const w=(fields[0].length-15)/5,lanes=[0,1].map(i=>parseInt(Array.from({length:w},(_,j)=>fields[0][5*j+i]).join(""),2));ok(lanes.join()===`${m-1},${m-2}`,"bound lanes");
  let j=3;const groups=[0,1,2,3,4,5,6,7,8];
  for(let k=1;k<=3;k++)for(const scope of E.subsets(groups,k)){
   const f=d.F.find(f=>f.h.join()===scope.join()),want=[...E.tup(m,k)].map(z=>f&&!f.S.has(z.join())?"1":"0").join("");
   const src=fields[j++].split("").reverse().join("");let decoded="";
   if(k===1)decoded=src;else for(let i=0;i<src.length;){if(src[i]==="0"){decoded+="0";i++;}else if(src.slice(i,i+2)==="11"){decoded+="1";i+=2;}else if(src.slice(i,i+3)==="101"){decoded+="0000";i+=3;}else throw Error("packed block");}
   ok(decoded===want,"checkpoint mask "+name+" "+scope);positions+=want.length;blocks++;
  }
  blocks++;const combinations=d.n+d.n*(d.n-1)/2+d.n*(d.n-1)*(d.n-2)/6,deposits=10*m+36*m*m+84*m*m*m;
  ok(counts[1]===combinations&&counts[2]===combinations&&counts[3]===deposits,"entry counts "+name+" "+counts);
  while(s!==C.bridgeReady)step();
  const end=h+1+U.stream(E,raw).length,stream=Array.from(T.slice(h+1,end)).join("");ok(stream===U.stream(E,raw)&&T[end]===2&&T[h]===2,"loader");step();ok(s===M.q,"producer halt");
  rawBits+=raw.length;cases++;rows.push({name,m,L:raw.length,header:headerAt,normalization:normalizeAt-headerAt,loader:t-normalizeAt,total:t,combinations,deposits,stream:stream.length});
 }
 test("empty",2,[0,0],[]);
 test("chain",2,[0,1],[[-1],[-3],[-2,-4,-5],[-4,-6,-7],[-6,-8,-9]]);
 test("all-active",2,[1,0],[2,3].flatMap(k=>[...E.subsets([0,1,2,3,4,5,6,7,8],k)].map(h=>h.map(g=>-(2*g+2)))));
 test("third-rank",3,[0,1,0],[[-1],[-2],[-4],[-5],[-3,-6,-7],[-3,-6,-8]]);
 return {cases,blocks,positions,rawBits,rows};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_width_three_fifo_producer.js'),require('./f038_tga_normalized_integration.js').engine(),require('./f038_rex_width_three_cost_ir.js'))));
