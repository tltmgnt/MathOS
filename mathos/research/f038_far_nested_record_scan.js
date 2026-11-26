// FAR-003: nested physical list/key transport; prepared record layout, not normalized SAT.
function compile(){
 const width=6,S="_AL01RED",M="_AD01R",I="_L01R",O="_01",symbols=[],codes=[];
 for(let s of S)for(let m of M)for(let i of I)for(let o of O){symbols.push([s,m,i,o]);codes.push(symbols.length===1?"222222":(symbols.length-2).toString(3).padStart(width,"0"));}
 const id=(s,m,i,o)=>((S.indexOf(s)*M.length+M.indexOf(m))*I.length+I.indexOf(i))*O.length+O.indexOf(o);
 const bit=v=>v==="0"||v==="1";
 function logical(q,j){
  let [s,m,i,o]=symbols[j],p=q.split(":"),a=p[1],b=p[2];
  const go=(q,d)=>[q,j,d],put=(q,d,mm=m,ii=i,oo=o)=>[q,id(s,mm,ii,oo),d];
  switch(p[0]){
   case "seek":return go(s==="E"?"copyList":"seek",1);
   case "copyList":
    if(s==="R")return put("listBack",-1,"R");
    if(s==="D"||s==="L"||bit(s))return put("copyList",1,s==="D"?"A":s==="L"?"D":s);
    break;
   case "listBack":return m==="A"?go("park",0):go("listBack",-1);
   case "park":return s==="A"?put("copyKey",1,m,"L"):go("leftEnd",1);
   case "leftEnd":return m==="R"?put("leftCarry:R",-1,"_"):go("leftEnd",1);
   case "leftCarry":return m==="_"?put("park",0,a):put("leftCarry:"+m,-1,a);
   case "copyKey":
    if(bit(s))return put("copyKey",1,m,s);
    if(s==="R")return put("keyBack",-1,m,"R");
    break;
   case "keyBack":return i==="L"?go("compare:0:1",1):go("keyBack",-1);
   case "compare":
    if(bit(i)&&bit(m))return go("compare:"+a+":"+(+b&+(i===m)),1);
    if(i==="R"&&(m==="D"||m==="R"))return go("return:"+(+a|+b)+":"+(m==="R"?1:0),-1);
    break;
   case "return":
    if(bit(i))return go(q,-1);
    if(i==="L")return b==="1"?put("eraseKey:"+a,1,m,"_"):put("innerCarry:"+a+":L",1,m,"_");
    break;
   case "innerCarry":
    if(i==="_")return put("innerBack:"+a,-1,m,b);
    return put("innerCarry:"+a+":"+i,1,m,b);
   case "innerBack":
    if(i==="L")return m==="D"?go("compare:"+a+":1",1):put("innerCarry:"+a+":L",1,m,"_");
    return go(q,-1);
   case "eraseKey":
    if(i==="R")return put("resultBack:"+a,-1,m,"_");
    return put(q,1,m,"_");
   case "resultBack":
    if(m==="A")return put("nextKey",1,m,i,a);
    return go(q,-1);
   case "nextKey":return go(s==="R"?"lookAhead":"nextKey",1);
   case "lookAhead":
    if(s==="E"||s==="L")return go("outerBack:"+(s==="E"?1:0),-1);
    break;
   case "outerBack":
    if(m==="A")return a==="1"?put("clearList",1,"_","L"):put("outerCarry:A",1,"_");
    return go(q,-1);
   case "outerCarry":
    if(m==="_")return put("outerRewind",-1,a);
    return put("outerCarry:"+m,1,a);
   case "outerRewind":
    if(m==="A")return s==="L"?put("copyKey",1,m,"L"):put("outerCarry:A",1,"_");
    return go(q,-1);
   case "clearList":
    if(m==="R")return put("clearBack",-1,"_");
    return put(q,1,"_");
   case "clearBack":
    if(i==="L")return put("HALT",0,m,"_");
    return go(q,-1);
  }
  return go("HALT",0);
 }
 const states=[],ids=new Map(),rows=[];
 function state(k){let s=k.join("|");if(!ids.has(s)){ids.set(s,states.length);states.push(k);}return ids.get(s);}
 state(["r","seek",""]);
 const target=q=>q==="HALT"?-1:state(["r",q,""]);
 const codeIds=new Map(codes.map((c,i)=>[c,i]));
 for(let h=0;h<states.length;h++){
  let k=states[h];
  for(let a=0;a<3;a++){
   let r;
   if(k[0]==="r"){
    let p=k[2]+a;
    if(p.length<width)r=[state(["r",k[1],p]),a,1];
    else{let j=codeIds.get(p);
     if(j===undefined)r=[-1,a,0];
     else{let [next,out,d]=logical(k[1],j);r=[state(["w",next,codes[out],d,width-1]),a,0];}
    }
   }else if(k[0]==="w"){
    let [,next,out,d,j]=k;
    r=j?[state(["w",next,out,d,j-1]),+out[j],-1]:[d===0?target(next):state(["m",next,d,width-1]),+out[0],d];
   }else{
    let [,next,d,left]=k;r=[left===1?target(next):state(["m",next,d,left-1]),a,d];
   }
   rows.push(...r);
  }
 }
 const q=states.length,T=Int32Array.from(rows.map((v,i)=>i%3===0&&v<0?q:v)),b=q.toString(2).length;
 function description(){let a=["111","1".repeat(q),"0"];for(let j=0;j<T.length;j+=3)a.push(T[j].toString(2).padStart(b,"0"),T[j+1].toString(2).padStart(2,"0"),(T[j+2]+1).toString(2).padStart(2,"0"));return a.join("");}
 return {q,T,width,symbols,codes,id,description,descriptionBits:4+q+3*q*(b+4)};
}
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},M=compile(),{q,T,width,symbols,codes,id}=M;
 let desc=M.description(),b=q.toString(2).length,at=q+4;
 ok(desc.length===M.descriptionBits&&desc.slice(0,at)==="111"+"1".repeat(q)+"0","header");
 for(let j=0;j<T.length;j+=3){ok(parseInt(desc.slice(at,at+b),2)===T[j]&&parseInt(desc.slice(at+b,at+b+2),2)===T[j+1]&&parseInt(desc.slice(at+b+2,at+b+4),2)-1===T[j+2],"decode");at+=b+4;}
 function run(keys,records,limit=Infinity){
  let Q=keys.length,R=records.length,k=keys[0].length,H=Q*(k+2),L=R*(k+1)+1;
  let stationary=keys.map((s,i)=>(i?"L":"A")+s+"R").join("")+"E"+records.map((s,i)=>(i?"L":"D")+s).join("")+"R";
  ok(stationary.length===H+1+L,"layout");
  let tape=new Uint8Array((stationary.length+2)*width);tape.fill(2);
  const set=(i,s,m="_",inn="_",o="_")=>{let c=codes[id(s,m,inn,o)];for(let j=0;j<width;j++)tape[(i+1)*width+j]=+c[j];};
  set(-1,"1","D","1","1");set(stationary.length,"0","R","R","0");
  for(let i=0;i<stationary.length;i++)set(i,stationary[i]);
  let head=width,state=0,steps=0,low=head,high=head;
  while(state!==q&&steps<limit){
   let j=3*(3*state+tape[head]),next=T[j],w=T[j+1],d=T[j+2];tape[head]=w;head+=d;state=next;steps++;low=Math.min(low,head);high=Math.max(high,head);
   ok(head>=width&&head<(stationary.length+1)*width,"outside");
  }
  if(state!==q)return {halt:false,steps};
  function read(i){let c=Array.from(tape.slice((i+1)*width,(i+2)*width)).join("");let j=codes.indexOf(c);ok(j>=0,"code");return symbols[j];}
  let output="";
  for(let i=0;i<stationary.length;i++){
   let [s,m,inn,o]=read(i);ok(s===stationary[i]&&m==="_"&&inn==="_","preservation and cleanup");
   let j=i/(k+2),want=Number.isInteger(j)&&j<Q?String(+records.includes(keys[j])):"_";ok(o===want,"membership");if(want!=="_")output+=o;
  }
  ok(read(-1).join("")==="1D11"&&read(stationary.length).join("")==="0RR0","sentinels");
  ok(head===width*(1+(Q-1)*(k+2))&&low===width&&high===width*(stationary.length+1)-1,"head/span");
  // Exact data-independent logical counts, derived in report.
  let prep=H+1+L+(L-2)+1+2*L*(H+1);
  let keyCopy=2*k+2,compare=R*(2*k+2)+(R-1)*(k+1)*(2*k+3);
  let keyErase=k+2+(L-2),next=2*(k+2);
  let shift=(Q-1)*(k+2)*(2*L-1),clean=2*L-1;
  let logical=prep+Q*(keyCopy+compare+keyErase+next)+shift+clean;
  let stays=H+3;
  let expected=17*logical-5*stays;
  ok(steps===expected,"clock "+[Q,R,k,steps,expected,logical,stays].join(","));
  return {halt:true,steps,logical,span:high-low+1,output};
 }
 let tests=0,transitions=0,answers=0,cutoffs=0,scaling=[];
 for(let k=1;k<=3;k++)for(let Q=1;Q<=2;Q++)for(let R=1;R<=2;R++)for(let v=0;v<2**(k*(Q+R));v++){
  let words=v.toString(2).padStart(k*(Q+R),"0").match(new RegExp(".{"+k+"}","g")),keys=words.slice(0,Q),records=words.slice(Q),r=run(keys,records);tests++;transitions+=r.steps;answers+=Q;
  if(v===0){ok(!run(keys,records,r.steps-1).halt,"timeout");cutoffs++;}
 }
 for(let [Q,R,k] of [[1,1,1],[4,8,3],[8,16,4],[16,32,5],[32,64,6],[8,8,12]]){
  let keys=Array.from({length:Q},(_,i)=>(i%2**k).toString(2).padStart(k,"0")),records=Array.from({length:R},(_,i)=>((i*3+1)%2**k).toString(2).padStart(k,"0"));
  let r=run(keys,records);scaling.push([Q,R,k,r.steps,r.logical,r.span,r.output]);
 }
 return {states:q,descriptionBits:desc.length,alphabet:symbols.length,blockWidth:width,tests,transitions,answers,cutoffs,scaling};
}
if(process.argv.includes('--description')) console.log(compile().description()); else console.log('F038_FAR_NESTED_RECORD_SCAN_OK '+JSON.stringify(audit()));
