// REX-024C1 independent sparse interpreter and full DFS-stack comparison.
function replay(P,E){
 const C=P.compile(),ok=(v,s)=>{if(!v)throw Error(s)};
 let j=3;while(C.desc[j]==="1")j++;let q=j-3,b=q.toString(2).length;j++;
 const table=[];for(let i=0;i<3*q;i++){let a=parseInt(C.desc.slice(j,j+b),2),w=parseInt(C.desc.slice(j+b,j+b+2),2),d=parseInt(C.desc.slice(j+b+2,j+b+4),2)-1;j+=b+4;ok(a<=q&&w<=2&&d>=-1&&d<=1,"descriptor field");table.push([a,w,d]);}
 ok(j===C.desc.length,"descriptor length");
 const V=[...Array(9).keys()],edges=V.flatMap(a=>V.filter(b=>b>a).map(b=>[a,b])),bin=x=>x.toString(2).padStart(4,"0"),rows=[];
 const trap=[[0,1],[0,2],[0,6],[1,3],[1,8],[2,5],[2,7],[3,6],[3,7],[3,8],[4,6],[5,8],[6,7],[7,8]];
 for(let [name,H,pins,clock,order] of [["greedy-trap",trap,[0,1],26957865,[1,2,4,5,6,0,3,7,8]],["K5",edges.filter(([a,b])=>b<5),[1,1],27879500,null]]){
  const raw=E.encode(2,pins,H.map(h=>h.map(v=>-(2*v+1)))),tape=new Map([...raw].map((x,i)=>[i,+x]));let state=0,h=0,t=0;
  while(state!==q&&t<clock){let [a,w,d]=table[3*state+(tape.get(h)??2)];if(w===2)tape.delete(h);else tape.set(h,w);h+=d;state=a;t++;}
  ok(state===q&&t===clock&&h===raw.length-1&&!tape.has(h),"exact halt");
  let G=V.map(()=>new Set()),active=new Set(V);for(let [a,b] of H){G[a].add(b);G[b].add(a);}
  let words=[];
  for(let i=0;i<(order?10:1);i++){
   let v=order?(order[i]??9):8,eligible=V.filter(x=>active.has(x)&&G[x].size<=3&&x<=v);
   let word=edges.map(([a,b])=>+G[a].has(b)).join("")+V.map(x=>+active.has(x)).join("")+V.map(x=>+eligible.includes(x)).join("")+bin(v)+ +(i===0)+ +(i===0&&!!order);
   let ns=[...G[v]??[]].sort((a,b)=>a-b);if(order&&i<9){let par=order.slice(i+1).find(x=>ns.includes(x))??9;let [a,b,c]=[0,1,2].map(j=>ns[j]??9);word+=[a,b,c,par].map(bin).join('')+[true,a!==9,b!==9,c!==9,b!==9,c!==9,c!==9].map(Number).join('')+'0';}else word+='0'.repeat(24);words.push(word);if(order&&i<9){let ns=[...G[v]];for(let a of ns){G[a].delete(v);for(let b of ns)if(a!==b)G[a].add(b);}G[v].clear();active.delete(v);}
  }
  for(let i=0;i<words.length;i++){let start=h+85*i;ok(!tape.has(start)&&Array.from({length:84},(_,j)=>tape.get(start+1+j)).join("")===words[i],"exact frame");}
  ok(!tape.has(h+85*words.length),"terminal delimiter");
  const end=h-26,start=end-(raw.length-32);
  ok(Array.from({length:end-start},(_,i)=>tape.get(start+i)).join("")===raw.slice(32),"selector");
  let cursor=start-1,blocks=edges.map(e=>H.some(h=>h.join()===e.join())?"1":"").concat(pins.join(""));let selected=new Set(H.map(h=>h.join()));for(let k=1;k<=3;k++)for(let h of E.subsets(V,k))blocks.push([...E.tup(2,k)].map(z=>+(k===2&&selected.has(h.join())&&z.every(x=>x===0))).join(""));
  for(let want of blocks){ok(!tape.has(cursor),"separator");cursor--;let got="";while(tape.has(cursor))got+=tape.get(cursor--);ok(got===want,"original graph/pins");}
  ok(tape.size===end-start+25+H.length+2+834+84*words.length,"complete tape shape");
  rows.push({name,t,frames:words.length,order,status:order?"WIDTH_THREE_FACTORS":"OUTSIDE_WIDTH_THREE"});
 }
 return{q,descriptorBits:C.desc.length,rows,transitions:rows.reduce((a,r)=>a+r.t,0)};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_width_three_factors.js'),require('./f038_tga_normalized_integration.js').engine())));
