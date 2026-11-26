// REX-024C3: fixed-multitape checkpoint parser, mask cursor tuple expansion and forest controller.
function controller(snapshot,mergeTapes,limit=Infinity,observe=false){
 // Fixed tapes and bounded controller data only. Snapshot is the literal
 // C1 visited tape with '_' blanks and 'H' marking its blank halt cell.
 if(limit!==Infinity&&(!Number.isSafeInteger(limit)||limit<0))throw Error("budget");
 let steps=0,phase="load",ledger={load:0,expand:0,route:0,projection:0,parentSort:0,childSort:0,dedup:0,join:0,retain:0,roots:0},passes=0;
 const tick=()=>{if(steps>=limit)throw "TIMEOUT";steps++;ledger[phase]++;};
 const all=[];
 class Tape{
  constructor(input=""){this.cells=["L",...input];this.h=0;this.max=0;all.push(this);}
  read(){tick();return this.cells[this.h]??null;}
  put(v){tick();this.cells[this.h]=v;}
  move(d){if(d!==1&&d!==-1)throw Error("unit move");tick();this.h+=d;if(this.h<0)throw Error("left boundary");this.max=Math.max(this.max,this.h);}
  observe(){let e=1;while(this.cells[e]!=null)e++;if(this.cells.slice(e).some(v=>v!=null))throw Error("noncontiguous tape");return this.cells.slice(1,e).join("");}
 }
 const I=new Tape(snapshot),bound=new Tape(),rank=Array.from({length:4},()=>new Tape()),domain=Array.from({length:3},()=>new Tape()),masks=Array.from({length:129},()=>new Tape()),rel=Array.from({length:9},()=>new Tape()),P=new Tape(),C=new Tape(),A=new Tape(),B=new Tape(),S=new Tape(),K=new Tape(),O=new Tape(),decision=new Tape();
 const V=[0,1,2,3,4,5,6,7,8],scopes=[];
 for(let k=1;k<=3;k++){function sub(a,at){if(a.length===k){scopes.push(a);return;}for(let i=at;i<9;i++)sub([...a,i],i+1);}sub([],0);}
 const bit=x=>x==="0"||x==="1",fail=()=>{throw "MALFORMED_CHECKPOINT";};
 const rewind=t=>{while(t.read()!=="L")t.move(-1);},start=t=>{rewind(t);t.move(1);},append=(t,v)=>{t.put(v);t.move(1);};
 const clear=t=>{start(t);while(t.read()!==null){t.put(null);t.move(1);}start(t);};
 const end=t=>{start(t);while(t.read()!==null)t.move(1);};
 function copy(src,dst){clear(dst);start(src);while(src.read()!==null){append(dst,src.read());src.move(1);}}
 function readBit(t,d){let v=t.read();if(!bit(v))fail();t.move(d);return v;}
 function skipBits(t,d,k){for(let i=0;i<k;i++)readBit(t,d);}
 function seekH(){start(I);while(I.read()!=="H"){if(I.read()===null)fail();I.move(1);}}
 function word4(){let n=0;for(let i=0;i<4;i++)n=2*n+Number(readBit(I,1));return n;}
 function equal(a,b){start(a);start(b);let eq=true;while(a.read()!==null&&b.read()!==null){if(a.read()!==b.read())eq=false;a.move(1);b.move(1);}return eq&&a.read()===null&&b.read()===null;}
 function zero(t){start(t);while(t.read()!==null){t.put("0");t.move(1);}}
 function inc(t){start(t);while(t.read()==="1"){t.put("0");t.move(1);}if(t.read()!=="0")throw Error("counter overflow");t.put("1");}
 function rankEmit(t,out){end(t);t.move(-1);while(t.read()!=="L"){append(out,t.read());t.move(-1);}}
 let headers=[],local=null,edges=0,sat=null;
 function result(status){return {status,steps,ledger,passes,tapes:all.length,span:all.reduce((s,t)=>s+t.max+1,0),edges,decision:status==="COMPLETE"?decision.observe():null,local:status==="COMPLETE"&&observe?local:null,relations:status==="COMPLETE"&&observe?rel.map(t=>t.observe()):null,headers:status==="COMPLETE"&&observe?headers:null};}
 try{
  seekH();I.move(1);
  for(let i=0;i<10;i++){
   skipBits(I,1,54);let v=word4(),root=+readBit(I,1),status=+readBit(I,1);
   if(i===0&&!status)return result("STRUCTURAL_REFUSAL");
   if(root!==+(i===0)||status!==+(i===0))fail();
   let ns=[word4(),word4(),word4()],parent=word4(),slots="";
   for(let j=0;j<7;j++)slots+=readBit(I,1);
   if(readBit(I,1)!=="0"||I.read()!=="_")fail();
   if(i===9){if(v!==9||ns.some(x=>x!==0)||parent!==0||slots!=="0000000")fail();break;}
   if(v>8||parent>9||ns.some((x,j)=>x>9||x===v||j>0&&ns[j-1]!==9&&x<=ns[j-1]||j>0&&ns[j-1]===9&&x!==9)||headers.some(h=>h.v===v))fail();
   const [a,b,c]=ns,owned=[[v],[v,a],[v,b],[v,c],[v,a,b],[v,a,c],[v,b,c]],valid=owned.map(h=>+h.every(x=>x!==9)).join("");
   if(slots!==valid)fail();
   let h=[v,...ns.filter(x=>x!==9)].sort((a,b)=>a-b);
   headers.push({v,h,parent,sep:ns.filter(x=>x!==9),owned:owned.filter(s=>s.every(x=>x!==9)).map(s=>s.sort((a,b)=>a-b))});
   I.move(1);
  }
  // Read the M=m-1 binary lane directly, LSB first, stripping redundant
  // high zero columns. No numerical m or width is supplied.
  seekH();I.move(-1);skipBits(I,-1,15);start(bound);
  while(I.read()!=="_"){skipBits(I,-1,4);append(bound,readBit(I,-1));}
  bound.move(-1);while(bound.read()==="0"){bound.put(null);bound.move(-1);}if(bound.read()!=="1")fail();
  // Read leftward over the selector, then edge and pin blocks, then masks.
  I.move(-1);while(bit(I.read()))I.move(-1);if(I.read()!=="_")fail();
  for(let k=0;k<166;k++){
   I.move(-1);let t=k>=37?masks[k-37]:null;if(t)start(t);
   while(bit(I.read())){let x=readBit(I,-1);if(t)append(t,x);}
   if(I.read()!=="_")fail();
  }
  for(let t of rank){start(bound);start(t);while(bound.read()!==null){append(t,"0");bound.move(1);}}
  for(let t of domain)start(t);
  // Generate three identical unary domain tapes by a charged binary loop.
  while(true){for(let t of domain)append(t,"x");if(equal(rank[0],bound))break;inc(rank[0]);}
  zero(rank[0]);
  phase="expand";
  function rewindCount(t,k){
   let first=true;
   function loop(j){if(j===k){if(first)first=false;else t.move(-1);return;}const d=domain[j];start(d);while(d.read()!==null){loop(j+1);d.move(1);}}
   loop(0);
  }
  for(let i=0;i<9;i++){
   let bag=headers[i],r=bag.h.length,out=rel[i];
   const owned=bag.owned.map(s=>({t:masks[scopes.findIndex(x=>x.join()===s.join())],mask:s.reduce((a,v)=>a|(1<<bag.h.indexOf(v)),0)}));
   for(let {t} of owned)start(t);
   for(let t of rank)zero(t);start(out);
   while(true){
    let allowed=true;for(let {t} of owned){let v=t.read();if(!bit(v))fail();if(v==="1")allowed=false;}
    if(allowed)for(let j=0;j<r;j++){rankEmit(rank[j],out);append(out,j===r-1?";":",");}
    let c=r-1;while(c>=0&&equal(rank[c],bound)){zero(rank[c]);c--;}
    if(c<0)break;inc(rank[c]);
    for(let {t,mask} of owned){
     if(mask&(1<<c))t.move(1);
     else {let k=0;for(let j=c+1;j<r;j++)if(mask&(1<<j))k++;if(k)rewindCount(t,k);}
    }
   }
   // Every owned mask ends at its final cell. Verify length at the next
   // cell and rewind. Nonowned masks are preserved, never overwritten.
   for(let {t} of owned){t.move(1);if(t.read()!==null)fail();start(t);}
  }
  if(observe)local=rel.map(t=>t.observe());
  for(let i=0;i<9;i++){
   phase="route";let b=headers[i];if(b.parent===9){if(b.sep.length)fail();continue;}
   let j=headers.findIndex(h=>h.v===b.parent);if(j<=i||!b.sep.length||!b.sep.every(v=>headers[j].h.includes(v)))fail();
   let par=headers[j],mask=h=>h.reduce((s,g,k)=>s|(b.sep.includes(g)?1<<k:0),0);
   copy(rel[j],P);copy(rel[i],C);
   mergeTapes(P,C,A,B,S,K,O,{parentArity:par.h.length,childArity:b.h.length,parentMask:mask(par.h),childMask:mask(b.h)},p=>{phase=p;},()=>{passes++;});
   phase="retain";clear(rel[j]);start(O);
   while(O.read()!==null){
    while(bit(O.read()))O.move(1);if(O.read()!==":")throw Error("key");O.move(1);
    for(let f=0;f<par.h.length;f++){
     while(true){let a=readBit(O,1),b=readBit(O,1);if(a==="1"){if(b!=="0")throw Error("payload delimiter");break;}append(rel[j],b);}
     append(rel[j],f===par.h.length-1?";":",");
    }
    if(O.read()!==";")throw Error("payload end");O.move(1);
   }
   edges++;
  }
  phase="roots";sat=true;for(let i=0;i<9;i++)if(headers[i].parent===9){start(rel[i]);if(rel[i].read()===null)sat=false;}
  start(decision);append(decision,sat?"1":"0");return result("COMPLETE");
 }catch(e){if(e==="TIMEOUT"||e==="MALFORMED_CHECKPOINT"||e==="MALFORMED")return result(e);throw e;}
}
module.exports={controller};
