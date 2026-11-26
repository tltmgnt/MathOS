// Independent sparse original-descriptor replay for SAT and joint-pair UNSAT.
function replay(P,E){
 const C=P.compile(),ok=(v,s)=>{if(!v)throw Error(s)};
 let j=3;while(C.desc[j]==="1")j++;let q=j-3,b=q.toString(2).length;j++;
 const T=new Uint32Array(3*q);
 for(let i=0;i<T.length;i++){let a=parseInt(C.desc.slice(j,j+b),2),w=parseInt(C.desc.slice(j+b,j+b+2),2),d=parseInt(C.desc.slice(j+b+2,j+b+4),2);j+=b+4;ok(a<=q&&w<=2&&d<=2,"descriptor field");T[i]=(a<<4)|(w<<2)|d;}
 ok(j===C.desc.length,"descriptor length");
 const pair=[...E.tup(2,3)].filter(z=>z[1]!==z[2]).map(z=>[0,4,8].map((v,i)=>-(2*v+z[i]+1)));pair.push([-9,-17],[-10,-18]);
 const plan=[[0,4,8],[1,9,9],[2,9,9],[3,9,9],[4,8,9],[5,9,9],[6,9,9],[7,9,9],[8,9,9]],parents=[4,9,9,9,8,9,9,9,9],bin=x=>x.toString(2).padStart(4,"0"),rows=[];
 for(let [name,B,clock,sat,entry] of [["sat",[[-1,-9,-17]],34376351,true,34283827],["joint-unsat",pair,34465372,false,34340699]]){
  const raw=E.encode(2,[1,0],B),tape=new Map([...raw].map((x,i)=>[i,+x]));let h=0,state=0,t=0,worker=null;
  while(state!==q&&t<clock){if(state===C.workerEntry&&worker===null)worker=t;let v=T[3*state+(tape.get(h)??2)],a=v>>>4,w=(v>>2)&3,d=(v&3)-1;if(w===2)tape.delete(h);else tape.set(h,w);h+=d;state=a;t++;}
  ok(state===q&&t===clock&&worker===entry&&h===raw.length-1&&!tape.has(h),"exact halt/entry");
  let forest="0".repeat(45)+plan.flat().map(bin).join("")+"1"+parents.map(bin).join(""),relations="";
  for(let i=0;i<9;i++){
   const scope=plan[i].filter(x=>x!==9);relations+="11111";
   for(let z of E.tup(2,scope.length)){
    const allow=sat?i!==0||z.some(x=>x===1):i===0?z[1]===z[2]:i===4?z[0]!==z[1]:true;
    if(allow)relations+="011"+z.map(x=>"00"+x+"010").join("")+(!sat&&(i===4||i===8)?"100":"101");
   }relations+="110";
  }
  const expected=forest+"0".repeat(12)+relations+Number(sat);
  ok(Array.from({length:expected.length},(_,i)=>tape.get(h+1+i)).join("")===expected&&!tape.has(h+expected.length+1),"exact physical flags");
  const work=25,end=h-work-1,start=end-(raw.length-32);
  ok(Array.from({length:end-start},(_,i)=>tape.get(start+i)).join("")===raw.slice(32),"selector");
  const V=[...Array(9).keys()],blocks=[],selected=new Set(B.map(c=>c.join()));
  for(let a=0;a<9;a++)for(let b=a+1;b<9;b++)blocks.push(a===0&&(b===4||b===8)||a===4&&b===8?"1":"");
  blocks.push("10");for(let k=1;k<=3;k++)for(let s of E.subsets(V,k))blocks.push([...E.tup(2,k)].map(z=>+selected.has(s.map((g,i)=>-(2*g+z[i]+1)).join())).join(""));
  let cursor=start-1;for(let want of blocks){ok(!tape.has(cursor),"separator");cursor--;let bits="";while(tape.has(cursor))bits+=tape.get(cursor--);ok(bits===want,"preserved mask/graph/pins");}
  ok(tape.size===end-start+work+3+2+834+expected.length,"canonical sparse layout");
  rows.push({name,t,worker:t-worker,relationBits:relations.length,decision:+sat});
 }
 return{q,descriptorBits:C.desc.length,rows,transitions:rows.reduce((a,r)=>a+r.t,0)};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_WIDTH_TWO_ELIMINATION_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_width_two_elimination.js'),require('./f038_tga_normalized_integration.js').engine())));
