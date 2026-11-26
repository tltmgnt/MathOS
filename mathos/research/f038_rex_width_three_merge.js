// F038-REX-024C2: charged fixed-seven-tape stable sort, key deduplication and semijoin.
function kernel(parent,child,limit=Infinity){
 // Input records: binary key ':' binary payload ';'. Empty fields allowed.
 // Seven fixed tapes. JS controller uses only finite flags and symbols;
 // steps, ledger, maximum head positions are observational counters.
 if(limit!==Infinity&&(!Number.isSafeInteger(limit)||limit<0))throw Error("budget");
 let steps=0,phase="init",ledger={init:0,parentSort:0,childSort:0,dedup:0,join:0},passes={parentSort:0,childSort:0};
 const tick=()=>{if(steps>=limit)throw "TIMEOUT";steps++;ledger[phase]++;};
 class Tape{
  constructor(input=""){this.cells=["L",...input];this.h=0;this.max=0;}
  read(){tick();return this.cells[this.h]??null;}
  put(v){tick();this.cells[this.h]=v;}
  move(d){if(d!==1&&d!==-1)throw Error("unit move");tick();this.h+=d;if(this.h<0)throw Error("left boundary");if(this.h>this.max)this.max=this.h;}
  observe(){return this.cells.slice(1).filter(v=>v!==null).join("");}
 }
 const P=new Tape(parent),C=new Tape(child),A=new Tape(),B=new Tape(),S=new Tape(),K=new Tape(),O=new Tape(),all=[P,C,A,B,S,K,O];
 const bit=v=>v==="0"||v==="1";
 const fail=()=>{throw "MALFORMED";};
 const rewind=t=>{while(t.read()!=="L")t.move(-1);};
 const start=t=>{rewind(t);t.move(1);};
 const append=(t,v)=>{t.put(v);t.move(1);};
 const clear=t=>{start(t);while(t.read()!==null){t.put(null);t.move(1);}start(t);};
 const copyRecord=(src,dst)=>{
  while(true){let v=src.read();if(!bit(v)&&v!==":"&&v!==";")throw Error("record invariant");append(dst,v);src.move(1);if(v===";")return;}
 };
 const skipRecord=src=>{while(src.read()!==";")src.move(1);src.move(1);};
 const backRecord=t=>{t.move(-1);while(true){let v=t.read();if(v===";"||v==="|"||v==="L"){t.move(1);return;}t.move(-1);}};
 function compare(a,b){
  let result=0;
  while(true){
   let x=a.read(),y=b.read();
   if(x!==y){result=x===":"?-1:y===":"?1:x==="0"?-1:1;break;}
   if(x===":")break;if(!bit(x))throw Error("key invariant");a.move(1);b.move(1);
  }
  backRecord(a);backRecord(b);return result;
 }
 // Convert the raw input stream to singleton runs on scratch A,
 // validating it sequentially. Copy back to input tape; no array access.
 function singleton(W){
  start(W);clear(A);let any=false,many=false;
  while(W.read()!==null){
   while(bit(W.read())){append(A,W.read());W.move(1);}
   if(W.read()!==":")fail();append(A,":");W.move(1);
   while(bit(W.read())){append(A,W.read());W.move(1);}
   if(W.read()!==";")fail();append(A,";");W.move(1);append(A,"|");
   if(any)many=true;any=true;
  }
  clear(W);start(A);while(A.read()!==null){append(W,A.read());A.move(1);}
  return many;
 }
 // Delimited runs eliminate unbounded host run-length counters.
 // Split alternately, then merge one run from each tape, stably.
 function sort(W){
  let many=singleton(W);
  while(many){
   passes[phase]++; // observation only
   clear(A);clear(B);start(W);let left=true;
   while(W.read()!==null){
    let out=left?A:B;
    while(W.read()!=="|")copyRecord(W,out);
    append(out,"|");W.move(1);left=!left;
   }
   clear(W);start(A);start(B);let any=false;many=false;
   while(A.read()!==null||B.read()!==null){
    while(A.read()!==null&&A.read()!=="|"&&B.read()!==null&&B.read()!=="|"){
     if(compare(A,B)<=0)copyRecord(A,W);else copyRecord(B,W);
    }
    while(A.read()!==null&&A.read()!=="|")copyRecord(A,W);
    while(B.read()!==null&&B.read()!=="|")copyRecord(B,W);
    if(A.read()==="|")A.move(1);if(B.read()==="|")B.move(1);
    append(W,"|");if(any)many=true;any=true;
   }
  }
 }
 const atRecord=t=>{let v=t.read();return v!==null&&v!=="|";};
 function emitKey(src,dst){while(src.read()!==":"){let v=src.read();if(!bit(v))throw Error("key grammar");append(dst,v);src.move(1);}append(dst,":");append(dst,";");}
 function result(status){
  return{status,steps,ledger,passes,tapes:all.length,span:all.reduce((s,t)=>s+t.max+1,0),support:status==="COMPLETE"?S.observe():null,filtered:status==="COMPLETE"?O.observe():null};
 }
 try{
  phase="parentSort";sort(P);phase="childSort";sort(C);
  phase="dedup";start(C);start(S);let previous=false;
  while(atRecord(C)){
   if(!previous||compare(C,K)!==0){
    clear(K);emitKey(C,K);backRecord(C);emitKey(C,S);backRecord(C);start(K);previous=true;
   }
   skipRecord(C);
  }
  phase="join";start(P);start(S);start(O);
  while(atRecord(P)&&atRecord(S)){
   let cmp=compare(P,S);
   if(cmp<0)skipRecord(P);
   else if(cmp>0)skipRecord(S);
   else copyRecord(P,O);
  }
  return result("COMPLETE");
 }catch(e){if(e==="TIMEOUT"||e==="MALFORMED")return result(e);throw e;}
}
module.exports={kernel};
