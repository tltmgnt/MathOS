// D5S actual compiled FIFO relocation and classification path audit.
function audit(P,E){
 const C=P.compile(true),M=P.decode(C.desc),ids=new Map(C.names.map(([n,f],i)=>[n+"|"+f,i])),ok=(x,s)=>{if(!x)throw Error(s)};
 const id=n=>{const i=ids.get(n+"|0");ok(i!==undefined,"missing "+n);return i;};
 function run(layout,h,start,stop,limit){let T=Uint8Array.from([...layout].map(Number)),s=id(start),t=0;while(!stop(C.names[s]?.[0])){ok(s!==M.q&&h>=0&&h<T.length&&t<limit,"path "+start+" "+C.names[s]?.[0]);const v=M.T[3*s+T[h]];T[h]=v>>2&3;h+=(v&3)-1;s=v>>>4;t++;}return {t,h,tape:Array.from(T).join(""),name:C.names[s][0]};}
 const batch=[];
 for(const [name,flag] of C.names){if(flag!==0||!name.endsWith("V0"))continue;const n=name.slice(0,-2);if(!ids.has(n+"ValidBack1|0"))continue;let word="",s=id(name);
  while(/^.*V\d+$/.test(C.names[s][0])){let a=[0,1].find(b=>!C.names[M.T[3*s+b]>>>4]?.[0].includes("Fail")&&C.names[M.T[3*s+b]>>>4]?.[0]!=="clean0");ok(a!==undefined,"word");word+=a;s=M.T[3*s+a]>>>4;}batch.push({n,word});}
 let relocations=0,invalid=0,maxExtra=0,classifications=0,maxClass=0;const rows=[];
 for(const {n,word} of batch){
  const k=word.length;let tested=0;
  for(const w of [20,25,30,40,80])for(let v=0;v<64;v++){
   const work=Array.from({length:w},(_,i)=>String((v>>(i%6))&1)).join(""),pre="201012101",tail="010112222",h=pre.length+1+w;
   const layout=pre+"2"+work+"2"+word+tail,expected=pre+word+"2"+work+"2"+tail;
   const q=run(layout,h,n,x=>/^(advance[123])$/.test(x),2*w+3*k+20);
   ok(q.tape===expected&&q.h===h+k,"relocate "+n);ok(q.t<=2*w+3*k+8,"clock "+q.t);maxExtra=Math.max(maxExtra,q.t-2*w);relocations++;tested++;
   if(v===0)for(let i=0;i<k;i++)for(const bit of [String(1-Number(word[i])),"2"]){
    const bad=word.slice(0,i)+bit+word.slice(i+1),a=pre+"2"+work+"2"+bad+tail,b=run(a,h,n,x=>x==="clean0",2*k+5);ok(b.tape===a&&b.h===h,"invalid "+n);invalid++;
   }
  }rows.push({n,word,tested});
 }
 for(const m of [2,3,4]){
  const n=19*m-7,coords=[];for(let g=0;g<21;g++){const count=g<9||g===18?m:g<18?m-1:1;for(let rank=0;rank<count;rank++)coords.push([g,rank]);}
  ok(coords.length===n,"coordinate count");const req=new Map(E.fixed(m,null).map(c=>[c.map(Math.abs).join(),c.reduce((a,x)=>2*a+(x>0?1:0),0)])),width=m.toString(2).length;
  for(let k=1;k<=3;k++)for(const a of E.subsets(Array.from({length:n},(_,i)=>i+1),k)){
   const q=a.map(x=>coords[x-1]),gs=q.map(x=>x[0]),rs=q.map(x=>x[1]);while(gs.length<3){gs.push(0);rs.push(0);}
   const lanes=[m-1,m-2,...rs].map(v=>v.toString(2).padStart(width,"0")),work=Array.from({length:width},(_,i)=>lanes.map(s=>s[i]).join("")).join("")+gs.map(g=>g.toString(2).padStart(5,"0")).join("");
   const layout="22"+work+"20222",head=2+work.length,expected=gs.slice(0,k).every(g=>g<9)&&new Set(gs.slice(0,k)).size===k?"covered"+gs.slice(0,k).join("_"):k===3&&gs.join()==="18,19,20"?"pinFirst":req.has(a.join())?"bits"+k+"Req"+req.get(a.join())+"S0":"bits"+k+"NoneS0";
   const out=run(layout,head,"class"+k,x=>x==="pinFirst"||/^covered/.test(x)||/^bits\d+(Req\d+|None)S0$/.test(x),500);
   ok(out.name===expected&&out.h===head&&out.tape===layout,"class "+JSON.stringify({m,a,out:out.name,expected,gs,rs}));classifications++;maxClass=Math.max(maxClass,out.t);
  }
 }
 return {batchEntries:batch.length,relocations,invalid,maxExtra,classifications,maxClass,rows};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_width_three_fifo_producer.js'),require('./f038_tga_normalized_integration.js').engine())));
