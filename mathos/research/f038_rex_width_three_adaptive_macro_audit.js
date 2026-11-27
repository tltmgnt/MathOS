// D5R actual compiled full deposit/return audit; synthetic valid local layouts.
function pack(word){const i=word.indexOf("1"),z=i<0?word.length:i,p="101".repeat(Math.floor(z/4))+"0".repeat(z%4);return i<0?p+"0":p+"11"+word.slice(i+1)+"1";}

function macroAudit(P){
 const C=P.compile(true),M=P.decode(C.desc),ids=new Map(C.names.map(([n,f],i)=>[n+"|"+f,i])),entries=new Map(),ok=(v,s)=>{if(!v)throw Error(s)};
 for(let i=0;i<C.names.length;i++){
  const [n,f]=C.names[i];if(f!==0||!/^deposit\d+$/.test(n))continue;
  let target=0;while(ids.has(n+"Seek"+(target+1)+"|0"))target++;
  const mode=ids.get(n+"Mode|0"),insert=ids.get(n+"Insert|0"),bit=(M.T[mode===undefined?3*insert+2:3*mode+1]>>2)&3;
  const end=M.T[3*ids.get(n+"BackWork|0")+2]>>>4;
  entries.set(target+":"+bit,{entry:i,end,packed:mode!==undefined});
 }
 ok(entries.size===260,"entries "+entries.size);
 let cases=0,maxSteps=0,maxRatio=0,folds=0,switches=0,literal=0,malformed=0;
 function check(target,word,bit,variant){
  const {entry,end,packed}=entries.get(target+":"+bit);
  const workspace=variant?"010101101010101":"01010",prefix=variant?"101010010101":"101",blocks=Array.from({length:130},(_,j)=>j<10?(j%3===0?"10":""):j%3===0?"1010":"0");
  blocks[target]=packed?pack(word):word;
  const serialize=()=>("2"+workspace+"2"+prefix+"2"+blocks.join("2")+"2");
  const before=serialize(),tape=new Uint8Array(before.length+8);tape.fill(2);tape.set([...before].map(Number));
  let h=0,s=entry,t=0;while(s!==end){ok(s!==M.q&&h>=0&&h<tape.length&&t<4*before.length+32,"macro timeout "+target);const v=M.T[3*s+tape[h]];tape[h]=v>>2&3;h-=((v&3)-1);s=v>>>4;t++;}
  const old=blocks[target];blocks[target]=packed?pack(word+bit):word+bit;const after=serialize();
  ok(h===0&&Array.from(tape.slice(0,after.length)).join("")===after&&tape.slice(after.length).every(x=>x===2),"layout "+JSON.stringify({target,word,bit,old,expected:blocks[target],h,t}));
  if(packed&&bit===0&&!word.includes("1")&&word.length%4===3)folds++;else if(packed&&bit===1&&!word.includes("1"))switches++;else literal++;
  cases++;maxSteps=Math.max(maxSteps,t);maxRatio=Math.max(maxRatio,t/before.length);
 }
 for(let j=0;j<130;j++)for(let n=0;n<=4;n++)for(let v=0;v<2**n;v++)for(const bit of [0,1])check(j,n?v.toString(2).padStart(n,"0"):"",bit,(j+v)%2);
 for(const j of [10,69,129])for(let n=5;n<=8;n++)for(let v=0;v<2**n;v++)for(const bit of [0,1])check(j,v.toString(2).padStart(n,"0"),bit,v%2);
 return {entries:entries.size,cases,folds,switches,literal,maxSteps,maxRatio};
}
module.exports={pack,macroAudit};
if(require.main===module)console.log(JSON.stringify(macroAudit(require('./f038_rex_width_three_adaptive_producer.js'))));
