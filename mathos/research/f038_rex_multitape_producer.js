// F038-REX-022A fixed-path normalized producer; charged multitape microprogram, not a single-tape descriptor.
function producer(raw,limit=Infinity){
 // Fixed controller, fixed number of tapes. Only Tape methods touch tape contents.
 // One charged primitive is one stationary read/write or unit head move.
 if(limit!==Infinity&&(!Number.isSafeInteger(limit)||limit<0))throw Error("invalid limit");
 let steps=0,phase="header",ledger={header:0,metadata:0,selector:0,output:0};
 const tick=()=>{if(steps>=limit)throw "TIMEOUT";steps++;ledger[phase]++;};
 class Tape{
  constructor(input=""){this.cells=Array.from(input);this.h=0;}
  read(){tick();return this.cells[this.h]??null;}
  put(a){tick();this.cells[this.h]=a;}
  move(d){if(d!==1&&d!==-1)throw Error("unit move");tick();this.h+=d;if(this.h<0)throw Error("left boundary");}
 }
 try{
 const I=new Tape(raw),work=()=>{let t=new Tape();t.put("L");return t;};
 const M=work(),M2=work(),Ym=work(),meta=[work(),work(),work()],tmp=work(),r1=work(),r2=work(),pins=work(),out=work(),width=work(),coord=[work(),work(),work()],bin=[work(),work(),work()];
 const masks=Array.from({length:7},()=>Array.from({length:7},work));
 function rewind(t){while(t.read()!=="L")t.move(-1);}
 function start(t){rewind(t);t.move(1);}
 function end(t){rewind(t);t.move(1);while(t.read()!==null)t.move(1);}
 function append(t,a){t.put(a);t.move(1);}
 function each(t,fn){start(t);while(t.read()!==null){fn();t.move(1);}rewind(t);}
 function clear(t){start(t);while(t.read()!==null){t.put(null);t.move(1);}rewind(t);}
 function inc(t){start(t);while(t.read()==="1"){t.put("0");t.move(1);}t.put("1");rewind(t);}
 function zero(t){each(t,()=>t.put("0"));}
 function result(status){return {status,steps,ledger,prepared:status==="PREPARED"?out.cells.slice(1).join(""):null,pins:status==="PREPARED"?pins.cells.slice(1).join(""):null};}
 const fail=()=>{throw "OUTSIDE_NORMALIZED";};
 const rawBit=()=>{const a=I.read();if(a!=="0"&&a!=="1")fail();I.move(1);return a;};
  M.move(1);M2.move(1);let rem=7,atLeast=0;
  while(I.read()==="1"){I.move(1);if(++rem===19){rem=0;append(M,"x");append(M2,"x");atLeast=Math.min(2,atLeast+1);}}
  if(I.read()!=="0"||rem!==0||atLeast!==2)fail();I.move(1);
  phase="metadata";
  Ym.move(1);let first=true;
  each(M,()=>{if(first)first=false;else append(Ym,"x");});
  function group(t,count,label){
   let f=true;start(count);
   while(count.read()!==null){count.move(1);let last=count.read()===null;count.move(-1);
    append(t,label+(f?(last?"B":"F"):(last?"E":"M")));f=false;count.move(1);}
   rewind(count);
  }
  for(let t of meta){t.move(1);for(let g=0;g<9;g++)group(t,M,"X"+g);for(let g=0;g<9;g++)group(t,Ym,"Y"+g);group(t,M,"P0");append(t,"G1B");append(t,"G2B");start(t);}
  for(let t of [pins,out,...masks.flat()])t.move(1);
  function rank(t,s){
   clear(s);s.move(1);
   while(!["F","B"].includes(t.read()[2])){t.move(-1);append(s,"x");}
   while(s.read()!=="L"){s.move(-1);if(s.read()==="x")t.move(1);}
  }
  function diff(a,b,d){ // rank(a) = rank(b)+d; d is 0 or 1.
   rank(a,r1);rank(b,r2);start(r1);start(r2);
   if(d){if(r1.read()===null)return false;r1.move(1);}
   while(r1.read()==="x"&&r2.read()==="x"){r1.move(1);r2.move(1);}
   return r1.read()===null&&r2.read()===null;
  }
  const f=a=>a[2]==="F"||a[2]==="B",last=a=>a[2]==="E"||a[2]==="B";
  const same=(a,b)=>a.slice(0,2)===b.slice(0,2);
  const grp=(a,b)=>a[1]===b[1];
  function seekAfter(src,dst){ // dst is positioned one variable past src, without using a numerical address.
   clear(tmp);tmp.move(1);rewind(dst);
   while(src.read()!=="L"){src.move(-1);append(tmp,"x");}
   while(tmp.read()!=="L"){tmp.move(-1);if(tmp.read()==="x"){src.move(1);dst.move(1);}}
   dst.move(1);
  }
  let outside=false;
  function support(k){
   const ts=meta.slice(0,k),a=ts.map(t=>t.read()),[x,y,z]=a;
   let req=-1,pin=false,optional=a.every(s=>s[0]==="X")&&new Set(a.map(s=>s[1])).size===k;
   if(k===1){if(x[0]==="Y"&&last(x))req=1;else if(x[0]==="G")req=0;}
   if(k===2){
    if(x[0]==="X"&&same(x,y))req=0;
    else if(x[0]==="X"&&y[0]==="Y"&&grp(x,y)&&(f(x)&&f(y)||diff(ts[0],ts[1],1)))req=1;
    else if(x[0]==="Y"&&same(x,y)&&diff(ts[1],ts[0],1))req=1;
   }
   if(k===3){
    if(x[0]==="X"&&same(x,y)&&z[0]==="Y"&&grp(x,z)&&f(x)&&f(z)&&diff(ts[1],ts[0],1))req=6;
    else if(x[0]==="X"&&y[0]==="Y"&&same(y,z)&&grp(x,y)&&diff(ts[2],ts[1],1)&&diff(ts[0],ts[2],1))req=6;
    else if(x[0]==="P"&&y==="G1B"&&z==="G2B")pin=true;
   }
   let negative=null;
   for(let s=0;s<2**k;s++){
    let b=rawBit();
    if(pin){if(s===0)negative=b;else if(b!==(s<4?negative:negative==="0"?"1":"0"))fail();}
    else if(s===req){if(b!=="1")fail();}
    else if(optional&&s===0){
     let gs=a.map(v=>+v[1]),covered=false;
     for(let j=0;j<7;j++)if(gs.every(g=>g>=j&&g<=j+2)){
      covered=true;let mask=gs.reduce((p,g)=>p|(1<<(g-j)),0);append(masks[j][mask-1],b);
     }
     if(!covered&&b==="1")outside=true;
    }else if(b!=="0")fail();
   }
   if(pin)append(pins,negative==="1"?"0":"1");
  }
  phase="selector";
  for(let k=1;k<=3;k++){
   start(meta[0]);while(meta[0].read()!==null){
    if(k===1)support(1);
    else{seekAfter(meta[0],meta[1]);while(meta[1].read()!==null){
     if(k===2)support(2);
     else{seekAfter(meta[1],meta[2]);while(meta[2].read()!==null){support(3);meta[2].move(1);}}
     meta[1].move(1);
    }}
    meta[0].move(1);
   }
  }
  if(I.read()!==null)fail();
  if(outside)return result("OUTSIDE_FIXED_PATH");
  phase="output";
  first=true;each(M,()=>{if(first)first=false;else inc(width);});
  for(let i=0;i<3;i++){
   coord[i].move(1);group(coord[i],M,"C0");start(coord[i]);
   bin[i].move(1);each(width,()=>append(bin[i],"0"));rewind(bin[i]);
  }
  const emit=s=>{for(let b of s)append(out,b);}; // s is a fixed token or a scanned bit.
  function emitRank(t){end(t);t.move(-1);while(t.read()!=="L"){emit("00");emit(t.read());t.move(-1);}emit("010");}
  function resetLower(t,k){
   let skip=true;const one=()=>{if(skip)skip=false;else t.move(-1);};
   if(k===1)each(M,one);else if(k===2)each(M,()=>each(M2,one));
  }
  for(let j=0;j<7;j++){
   emit(j===0?"11111":"11110");for(let t of masks[j])start(t);
   while(true){
    let allowed=true;for(let t of masks[j]){let v=t.read();if(v!=="0"&&v!=="1")throw Error("mask invariant");if(v==="1")allowed=false;}
    if(allowed){emit("011");for(let t of bin)emitRank(t);emit("101");}
    let c=2;while(c>=0){coord[c].move(1);if(coord[c].read()!==null){inc(bin[c]);break;}start(coord[c]);zero(bin[c]);c--;}
    if(c<0)break;
    for(let mask=1;mask<8;mask++){
     let t=masks[j][mask-1];
     if(mask&(1<<c))t.move(1);
     else{let k=0;for(let p=c+1;p<3;p++)if(mask&(1<<p))k++;resetLower(t,k);}
    }
   }
   emit("110");
  }
  for(let j=0;j<7;j++)emit("010");
  return result("PREPARED");
 }catch(e){if(e==="TIMEOUT"||e==="OUTSIDE_NORMALIZED")return {status:e,steps,ledger,prepared:null,pins:null};throw e;}
}
function audit(produce){
 const ok=(v,s)=>{if(!v)throw Error(s)};
 function* pool(n){for(let a=1;a<=n;a++)for(let x of [-1,1])yield [a*x];for(let a=1;a<=n;a++)for(let b=a+1;b<=n;b++)for(let x of [-1,1])for(let y of [-1,1])yield [a*x,b*y];for(let a=1;a<=n;a++)for(let b=a+1;b<=n;b++)for(let c=b+1;c<=n;c++)for(let x of [-1,1])for(let y of [-1,1])for(let z of [-1,1])yield [a*x,b*y,c*z];}
 function fixture(m,pins,B){
  let n=19*m-7,S=new Set(),add=c=>S.add(c.slice().sort((a,b)=>Math.abs(a)-Math.abs(b)).join(","));
  for(let g=0;g<9;g++){let X=Array.from({length:m},(_,j)=>g*m+j+1),Y=Array.from({length:m-1},(_,j)=>9*m+g*(m-1)+j+1);
   for(let i=0;i<m;i++)for(let j=i+1;j<m;j++)add([-X[i],-X[j]]);
   for(let j=0;j<Y.length;j++){let a=j?Y[j-1]:X[0],b=X[j+1],y=Y[j];add([-a,y]);add([-b,y]);add([a,b,-y]);}add([Y[Y.length-1]]);
  }
  add([1-n]);add([-n]);for(let i=0;i<m;i++)for(let a of [1-n,n-1])for(let b of [-n,n])add([pins[i]?(n-m-1+i):-(n-m-1+i),a,b]);
  for(let c of B)add(c);
  return "1".repeat(n)+"0"+Array.from(pool(n),c=>S.has(c.join(","))?"1":"0").join("");
 }
 function expected(m,B){
  let w=Math.ceil(Math.log2(m)),o="";
  for(let j=0;j<7;j++){o+=j?"11110":"11111";for(let a=0;a<m;a++)for(let b=0;b<m;b++)for(let c=0;c<m;c++){
   let z=[a,b,c];if(B.some(cl=>cl.every(x=>{let g=Math.floor((-x-1)/m);return g>=j&&g<=j+2&&z[g-j]===(-x-1)%m;})))continue;
   o+="011"+z.map(x=>x.toString(2).padStart(w,"0").split("").map(b=>"00"+b).join("")+"010").join("")+"101";
  }o+="110";}return o+"010".repeat(7);
 }
 let results=[],seed=0x52455822,rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let m of [2,3,4,5])for(let mode=0;mode<3;mode++){
  let B=[],pins=Array.from({length:m},(_,i)=>(i+mode)%2);
  if(mode===1)for(let g=0;g<9;g++)for(let a=0;a<m-1;a++)B.push([-(g*m+a+1)]);
  if(mode===2){for(let j=0;j<7;j++)for(let a=0;a<m;a++)for(let b=0;b<m;b++)for(let c=0;c<m;c++)if((rand()>>>24)<70)B.push([-(j*m+a+1),-((j+1)*m+b+1),-((j+2)*m+c+1)]);
   for(let g=0;g<9;g++)for(let h=g+1;h<Math.min(9,g+3);h++)for(let a=0;a<m;a++)for(let b=0;b<m;b++)if((rand()>>>24)<80)B.push([-(g*m+a+1),-(h*m+b+1)]);
   for(let g=0;g<9;g++)for(let a=0;a<m;a++)if((rand()>>>24)<50)B.push([-(g*m+a+1)]);
  }
  let raw=fixture(m,pins,B),r=produce(raw),e=expected(m,B);
  ok(r.status==="PREPARED"&&r.prepared===e&&r.pins===pins.join(""),"producer differential "+m+":"+mode+":"+r.status+" "+r.prepared?.length+" "+e.length);
  results.push({m,mode,L:raw.length,N:e.length,steps:r.steps,ledger:r.ledger});
 }
 let good=fixture(2,[0,1],[]),n=31,pos=n+1,required=[],optional=[];
 for(let c of pool(n)){if(good[pos]==="1")required.push(pos);if(c.length===1&&c[0]>0&&c[0]<=18)optional.push(pos);pos++;}
 let controls=0;
 for(let p of [...required.slice(0,5),...required.slice(-5),...optional.slice(0,5)]){let bad=good.slice(0,p)+(good[p]==="1"?"0":"1")+good.slice(p+1);ok(produce(bad).status==="OUTSIDE_NORMALIZED","bad clause");controls++;}
 for(let bad of ["",good.slice(1),good+"0",good.slice(0,-1),good.slice(0,-1)+"2"]){ok(produce(bad).status==="OUTSIDE_NORMALIZED","bad length");controls++;}
 let pinPositions=[],idx=n+1;
 for(let c of pool(n)){if(c.length===3&&Math.abs(c[0])===n-3&&Math.abs(c[1])===n-1&&Math.abs(c[2])===n)pinPositions.push(idx);idx++;}
 ok(pinPositions.length===8,"pin fixture");
 const flip=(s,i)=>s.slice(0,i)+(s[i]==="1"?"0":"1")+s.slice(i+1);
 for(let p of pinPositions){ok(produce(flip(good,p)).status==="OUTSIDE_NORMALIZED","pin lift mutation");controls++;}
 let both=good;for(let p of pinPositions)if(both[p]==="0")both=flip(both,p);
 ok(produce(both).status==="OUTSIDE_NORMALIZED","both pin signs");controls++;
 let unsupported=fixture(2,[0,1],[[-1,-17]]);
 ok(produce(unsupported).status==="OUTSIDE_FIXED_PATH","outside path");ok(produce(flip(unsupported,optional[0])).status==="OUTSIDE_NORMALIZED","malformed priority");controls++;
 ok(produce(good,100).status==="TIMEOUT","timeout");
 return {results,controls,unsupported:1,timeout:1,totals:results.reduce((a,r)=>({rawBits:a.rawBits+r.L,preparedBits:a.preparedBits+r.N,steps:a.steps+r.steps}),{rawBits:0,preparedBits:0,steps:0})};
}
function integration(P,E,A){
 const ok=(v,s)=>{if(!v)throw Error(s)};
 const results=[];
 function plan(D){
  let root=null,prev=null,bags=[];
  for(let j=0;j<7;j++){let scope=[j,j+1,j+2],F=D.F.filter(f=>f.h.every(g=>scope.includes(g))),w=Math.ceil(Math.log2(D.m)),rows=[];
   for(let z of E.tup(D.m,3))if(F.every(f=>f.S.has(f.h.map(g=>z[g-j]).join(","))))rows.push([...z.map(a=>a.toString(2).padStart(w,"0")),1]);
   let bag={k:j?2:3,scope,rows,children:[]};if(prev)prev.children.push(bag);else root=bag;prev=bag;bags.push(bag);
  }return {root,bags};
 }
 let J=A.worker(),M=A.compile(J.rules,J.symbols,J.projection);
 for(let m of [2,3,4])for(let mode=0;mode<2;mode++){
  let B=[];for(let g=0;g<9;g++)for(let a=0;a<m-1;a++)B.push([-(g*m+a+1)]);
  for(let g=0;g<7;g++)B.push([-(g*m+1),-((g+1)*m+1),-((g+2)*m+1)]);
  if(mode)B.push([-9*m]);
  let pins=Array.from({length:m},(_,i)=>(i+mode)%2),raw=E.encode(m,pins,B),D=E.decode(raw),r=P(raw),p=plan(D),N=A.encode(p.root);
  ok(r.status==="PREPARED"&&r.prepared===N&&r.pins===pins.join(""),"inherited decoder/encoder differential");
  let q=A.physical(M,r.prepared,120000000);ok(q.state===M.q,"physical cutoff");let physicalSat=q.tape.has(q.head);ok(physicalSat===!mode,"physical status");
  let witness=null;
  if(physicalSat){let at=0,z=Array(9).fill(-1);
   for(let b of p.bags){let s=Array.from({length:b.rows.length},(_,i)=>q.tape.get(q.head+at+i)).join("");at+=b.rows.length;ok(s.length===b.rows.length&&s.split("1").length===2,"row selection");let row=b.rows[s.indexOf("1")];b.scope.forEach((g,i)=>{let a=parseInt(row[i],2);ok(z[g]===-1||z[g]===a,"separator");z[g]=a;});}
   ok(z.every(a=>a===m-1),"forced ranks");witness=E.witness(m,D.pins,z);ok(E.valid(raw,witness),"original clauses");
  }
  results.push({m,status:mode?"UNSAT":"SAT",rawBits:raw.length,preparedBits:N.length,producerSteps:r.steps,workerTransitions:q.t,witnessVerified:!!witness});
 }
 let raw=E.encode(2,[0,1],[]);for(let limit of [0,1,66,67,100]){let r=P(raw,limit);ok(r.status==="TIMEOUT"&&r.steps===limit,"early cutoff "+limit);}
 // Distinguish a width-two graph outside this *fixed* path from malformed input.
 let wide=E.encode(2,[0,1],[[-1,-17]]);ok(E.decode(wide)&&P(wide).status==="OUTSIDE_FIXED_PATH","fixed path restriction");
 return {results,earlyCutoffs:5,descriptorBits:M.desc.length};
}
module.exports={producer,audit,integration};
if(require.main===module){if(process.argv.includes('--produce'))console.log(JSON.stringify(producer(require('fs').readFileSync(0,'utf8'))));else if(process.argv.includes('--integration'))console.log('F038_REX_MULTITAPE_INTEGRATION_OK '+JSON.stringify(integration(producer,require('./f038_tga_normalized_integration.js').engine(),require('./f038_rex_nested_variable_overlap.js'))));else console.log('F038_REX_MULTITAPE_PRODUCER_OK '+JSON.stringify(audit(producer)));}
