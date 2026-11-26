// Reusable C2 merge on existing charged tapes. No string export/import.
function mergeTapes(P,C,A,B,S,K,O,projection,setPhase,countPass){
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
 // Optional physical projection from tuple-only streams. Each input row
 // has 1..4 nonempty binary fields separated by commas and ended by ';'.
 // A selected field is encoded 00/01 per digit and 10 at its end,
 // so even variable-length fields and empty separators are unambiguous.
 // The entire tuple is retained as an identically encoded payload.
 function project(W,arity,mask){
  start(W);clear(A);
  while(W.read()!==null){
   for(let j=0;j<arity;j++){
    if(!bit(W.read()))fail();
    while(bit(W.read())){let v=W.read();if(mask&(1<<j)){append(A,"0");append(A,v);}W.move(1);}
    if(W.read()!==(j===arity-1?";":","))fail();
    if(mask&(1<<j)){append(A,"1");append(A,"0");}
    if(j<arity-1)W.move(1);
   }
   append(A,":");backRecord(W);
   while(true){let v=W.read();if(bit(v)){append(A,"0");append(A,v);}
    else if(v===","||v===";"){append(A,"1");append(A,"0");}else throw Error("validated tuple");
    W.move(1);if(v===";"){append(A,";");break;}
   }
  }
  clear(W);start(A);while(A.read()!==null){append(W,A.read());A.move(1);}
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
   countPass(); // observation only
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

 clear(S);clear(K);clear(O);
  if(projection!==null){
   const {parentArity:pa,childArity:ca,parentMask:pm,childMask:cm}=projection;
   const valid=(r,m)=>Number.isInteger(r)&&r>=1&&r<=4&&Number.isInteger(m)&&m>=0&&m<(1<<r);
   const count=m=>[0,1,2,3].filter(i=>m&(1<<i)).length;
   if(!valid(pa,pm)||!valid(ca,cm)||count(pm)!==count(cm)||count(pm)>3)throw Error("projection config");
   setPhase("projection");project(P,pa,pm);project(C,ca,cm);
  }
  setPhase("parentSort");sort(P);setPhase("childSort");sort(C);
  setPhase("dedup");start(C);start(S);let previous=false;
  while(atRecord(C)){
   if(!previous||compare(C,K)!==0){
    clear(K);emitKey(C,K);backRecord(C);emitKey(C,S);backRecord(C);start(K);previous=true;
   }
   skipRecord(C);
  }
  setPhase("join");start(P);start(S);start(O);
  while(atRecord(P)&&atRecord(S)){
   let cmp=compare(P,S);
   if(cmp<0)skipRecord(P);
   else if(cmp>0)skipRecord(S);
   else copyRecord(P,O);
  }

}
module.exports={mergeTapes};
