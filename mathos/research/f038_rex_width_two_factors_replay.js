// Independent sparse replay of the full factor-forest descriptor.
function replay(P,E){
 const C=P.compile(),ok=(v,s)=>{if(!v)throw Error(s)},raw=E.encode(2,[1,0],[[-1,-9,-17]]),clock=26693134;
 let j=3;while(C.desc[j]==="1")j++;let q=j-3,b=q.toString(2).length;j++;
 const table=new Uint32Array(3*q);
 for(let i=0;i<table.length;i++){let a=parseInt(C.desc.slice(j,j+b),2),w=parseInt(C.desc.slice(j+b,j+b+2),2),d=parseInt(C.desc.slice(j+b+2,j+b+4),2);j+=b+4;ok(a<=q&&w<=2&&d<=2,"descriptor field");table[i]=(a<<4)|(w<<2)|d;}
 ok(j===C.desc.length,"descriptor length");
 let tape=new Map([...raw].map((x,i)=>[i,+x])),h=0,state=0,t=0;
 while(state!==q&&t<clock){let v=table[3*state+(tape.get(h)??2)],a=v>>>4,w=(v>>2)&3,d=(v&3)-1;if(w===2)tape.delete(h);else tape.set(h,w);h+=d;state=a;t++;}
 ok(state===q&&t===clock&&h===raw.length-1&&!tape.has(h),"exact halt");
 const plan=[[0,4,8],[1,9,9],[2,9,9],[3,9,9],[4,8,9],[5,9,9],[6,9,9],[7,9,9],[8,9,9]],parents=[4,9,9,9,8,9,9,9,9],bin=x=>x.toString(2).padStart(4,"0");
 let expected="0".repeat(45)+plan.flat().map(bin).join("")+"1"+parents.map(bin).join("");
 ok(Array.from({length:190},(_,i)=>tape.get(h+1+i)).join("")===expected&&!tape.has(h+191),"exact forest word");
 const work=25,end=h-work-1,start=end-(raw.length-32);
 ok(Array.from({length:end-start},(_,i)=>tape.get(start+i)).join("")===raw.slice(32),"preserved selector");
 const V=[...Array(9).keys()],blocks=[];
 for(let a=0;a<9;a++)for(let b=a+1;b<9;b++)blocks.push(a===0&&(b===4||b===8)||a===4&&b===8?"1":"");
 blocks.push("10");
 for(let k=1;k<=3;k++)for(let s of E.subsets(V,k))blocks.push(s.join()==="0,4,8"?"10000000":"0".repeat(2**k));
 let cursor=start-1;
 for(let want of blocks){ok(!tape.has(cursor),"separator");cursor--;let bits="";while(tape.has(cursor))bits+=tape.get(cursor--);ok(bits===want,"physical block");}
 ok(tape.size===end-start+work+3+2+834+190,"canonical sparse layout");
 return{q,descriptorBits:C.desc.length,transitions:t,maskBlocks:129,maskBits:834,outputBits:190,parentRecords:9};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_WIDTH_TWO_FACTORS_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_width_two_factors.js'),require('./f038_tga_normalized_integration.js').engine())));
