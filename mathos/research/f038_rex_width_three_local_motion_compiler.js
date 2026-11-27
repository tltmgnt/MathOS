// D6T: local continuation after interior moves; growth returns globally.
function compile(J,paired=true,special=true,serial=paired&&special,fused=serial,blind=fused,local=blind,motion=local){
 if(motion&&!local)throw Error('motion requires local');
 if(local&&!blind)throw Error('local requires blind');
 if(blind&&!fused)throw Error("blind requires fused");
 if(fused&&!serial)throw Error('fused requires serial paired layout');
 if(serial&&(!paired||!special))throw Error('serial requires paired specialized layout');
 const {alphabet,ins,tapes}=J,syms=["G","D","E","~",...alphabet.flatMap(x=>["u"+x,"h"+x])],w=Math.ceil(Math.log2(syms.length-1)),blank="~";
 const codes=Object.fromEntries(syms.filter(s=>s!==blank).map((s,i)=>[s,i.toString(2).padStart(w,"0")]));if(paired){if(alphabet.length!==5||w!==4)throw Error("paired codebook domain");for(let i=0;i<alphabet.length;i++){codes["u"+alphabet[i]]=(4+2*i).toString(2).padStart(w,"0");codes["h"+alphabet[i]]=(5+2*i).toString(2).padStart(w,"0");}}codes[blank]="2".repeat(w);
 const dec=new Map(Object.entries(codes).map(([s,c])=>[c,s])),prefixes=new Set(Object.values(codes).flatMap(c=>Array.from({length:w-1},(_,i)=>c.slice(0,i+1))));
 const logical=new Map(),add=(n,f)=>{if(logical.has(n))throw Error(n);logical.set(n,f);},r=(n,a)=>[n,a,1],l=(n,a)=>[n,a,-1],z=(n,a)=>[n,a,0],bad=()=>z("HALT",blank);
 function resolve(i){let k=0;while(ins[i].op==="jump"){i=ins[i].next;if(++k>ins.length||i<0)throw Error("jump cycle");}return i;}
 const dest=i=>"i"+resolve(i);
 for(let i=0;i<ins.length;i++){
  const I=ins[i],n="i"+i;if(I.op==="jump")continue;
  if(I.op==="halt"||I.op==="reject"){add(n,a=>a==="G"?z(I.op==="halt"?"SUCCESS":"HALT",I.op==="halt"?a:blank):bad());continue;}
  add(n,a=>a==="G"?r(n+"s"+I.t,a):bad());
  for(let t=I.t;t>=0;t--)add(n+"s"+t,a=>a==="D"&&t>0?r(n+"s"+(t-1),a):a.startsWith("h")&&t===0?logical.get(n+"act")(a):a==="E"||a===blank?bad():r(n+"s"+t,a));
  function ret(d){const s="ret"+resolve(d);if(!logical.has(s))add(s,a=>a==="G"?z(dest(d),a):a===blank?bad():l(s,a));return s;}
  // Read/write preserve the marked cell and its index. A successor
  // on the same tape can enter at that cell's first digit.
  function after(d,a){const k=resolve(d),J2=ins[k];return local&&J2.t===I.t&&["read","write","move"].includes(J2.op)?z("i"+k+"act",a):l(ret(d),a);}
  if(I.op==="read")add(n+"act",a=>a.startsWith("h")?after(I.next[alphabet.indexOf(a.slice(1))],a):bad());
  else if(I.op==="write")add(n+"act",a=>a.startsWith("h")&&a!=="hL"&&I.next.v!=="L"?after(I.next.d,"h"+I.next.v):bad());
  else if(I.op==="move"){
   const next=ret(I.next.d),dir=I.next.dir;
   const k=resolve(I.next.d),I2=ins[k],near=motion&&I2.t===I.t&&["read","write","move"].includes(I2.op),target=near?"i"+k+"act":next;
   const mark=fused?(dir===1?"markR":"markL")+target:n+"mark";
   add(n+"act",a=>a.startsWith("h")&&(dir===1||a!=="hL")?(dir===1?r:l)(mark,"u"+a.slice(1)):bad());
   if(!logical.has(mark))add(mark,a=>a.startsWith("u")?(near?z:l)(target,"h"+a.slice(1)):dir===1&&(a==="D"||a==="E")?r(serial?"shift"+next+":"+codes[a]:n+"carry"+syms.indexOf(a),"h_"):bad());
   if(dir===1&&!serial)for(let c of syms.filter(x=>x!=="G"&&x!==blank))add(n+"carry"+syms.indexOf(c),a=>c==="E"?a===blank?l(next,"E"):bad():a===blank||a==="G"?bad():r(n+"carry"+syms.indexOf(a),c));
  }else throw Error("opcode");
 }

 // Intern physical continuation rows directly, not string-named physical
 // states. Logical roots are reserved first, so cycles need no recursion.
 const roots=[],rootId=new Map(),logicalRows=[],symbolIds=new Map(syms.map((x,i)=>[x,i]));
 const H=0xfffffff,pack=(n,v,d)=>((n<<4)|(v<<2)|(d+1))>>>0;
 function root(n){if(n==="HALT")return H;if(n==="SUCCESS")return H-1;if(!rootId.has(n)){rootId.set(n,roots.length);roots.push(n);}return rootId.get(n);}
 root(dest(J.entry));
 for(let i=0;i<roots.length;i++){
 const shift=/^shift(ret[0-9]+):([01]+)$/.exec(roots[i]);
 if(shift){const [,d,c]=shift;if(c.length!==w)throw Error("FIFO width");root(d);for(const a of [0,1])root("shift"+d+":"+c.slice(1)+a);for(const a of syms)logicalRows.push(0,0);continue;}
 for(let a of syms){let [n,v,d]=logical.get(roots[i])(a);logicalRows.push(pack(root(n),0,0));logicalRows.push(3*symbolIds.get(v)+d+1);}
}
 const rootCount=roots.length,CH=1<<18,chunks=[];let q=rootCount;
 function slot(i){let k=Math.floor(i/CH);while(chunks.length<=k)chunks.push(new Uint32Array(3*CH));return [chunks[k],3*(i%CH)];}
 function get(i,a){let [t,j]=slot(i);return t[j+a];}
 function put(i,a,b,c){let [t,j]=slot(i);t[j]=a;t[j+1]=b;t[j+2]=c;}
 let hashTable=new Uint32Array(1<<20),used=0;
 function hash(a,b,c){let x=Math.imul(a^0x9e3779b9,0x85ebca6b)^Math.imul(b^0x7f4a7c15,0xc2b2ae35)^Math.imul(c^0x165667b1,0x27d4eb2d);return (x^(x>>>16))>>>0;}
 function grow(){let old=hashTable;hashTable=new Uint32Array(old.length*2);let mask=hashTable.length-1;for(let e of old)if(e){let i=e-1,j=hash(get(i,0),get(i,1),get(i,2))&mask;while(hashTable[j])j=(j+1)&mask;hashTable[j]=e;}}
 function intern(a,b,c){if(used*10>=hashTable.length*7)grow();let mask=hashTable.length-1,j=hash(a,b,c)&mask;
  while(hashTable[j]){let i=hashTable[j]-1;if(get(i,0)===a&&get(i,1)===b&&get(i,2)===c)return i;j=(j+1)&mask;}
  if(q>=H-1)throw Error("packed state capacity");let i=q++;put(i,a,b,c);hashTable[j]=i+1;used++;return i;
 }
 function moveTail(n,dir,k){for(let i=0;i<k;i++)n=intern(pack(n,0,dir),pack(n,1,dir),pack(n,2,dir));return n;}
 const reversePrefixes=new Set(Object.values(codes).flatMap(c=>Array.from({length:w-1},(_,i)=>c.slice(w-i-1))));
 const invalid=pack(H,2,0);
 function transition(i,p,a){
  const returning=roots[i].startsWith("ret"),bits=returning?a+p:p+a;
  if(blind&&/^i[0-9]+(s0|act)$/.test(roots[i])){
   const name=roots[i].replace(/(s0|act)$/,""),I=ins[+name.slice(1)],atAct=roots[i].endsWith("act");
   if(I.op==="move"||I.op==="write"){
    // Valid IR never writes L or moves left from L. At the target
    // tape the last bit alone identifies the head.
    const act=logical.get(name+"act")("h0"),d=rootId.get(act[0]);
    let last;
    if(I.op==="move")last=I.next.dir===1?pack(d,0,1):pack(moveTail(d,-1,w-1),0,-1);
    else{
     const c=codes["h"+I.next.v];let tail=d;
     for(let j=0;j<w-1;j++){const a=pack(tail,+c[j],j===0&&act[2]===0?0:-1);tail=intern(a,a,a);}
     last=pack(tail,1,-1);
    }
    const end=intern(atAct?invalid:pack(i,0,1),last,invalid);
    if(p==="")return a<2?pack(moveTail(end,1,w-2),a,1):invalid;
   }
  }
  if(fused){
   const mark=/^mark([LR])(ret[0-9]+|i[0-9]+act)$/.exec(roots[i]);
   if(mark){
    const d=rootId.get(mark[2]),distance=mark[2].startsWith("ret")?w-1:w-2;
    // Left neighbour is a genuine unmarked data cell. Its final
    // digit is already under the physical head.
    if(mark[1]==="L"&&p==="")return a===0?pack(moveTail(d,-1,distance),1,-1):invalid;
    // Right neighbour is data or D/E. Data needs only its final bit.
    if(mark[1]==="R"){
     const markLast=intern(pack(moveTail(d,-1,distance),1,-1),invalid,invalid);
     if(bits.length===1&&a===1)return pack(moveTail(markLast,1,w-2),a,1);
     if(bits.length===2&&p==="0"&&a===1)return pack(moveTail(markLast,1,w-3),a,1);
    }
   }
  }
  if(paired&&special){
   // Valid return blocks are binary; G is the unique all-zero code.
   // Once any 1 is seen, cross the remaining digits without decoding.
   if(returning&&a===1)return pack(moveTail(i,-1,w-bits.length),a,-1);
   const scan=/^(i[0-9]+)s([0-9]+)$/.exec(roots[i]);
   if(scan&&+scan[2]>0&&bits.length===2&&a<2&&p==="0"){
    // G/E cannot occur before the target tape; 00 identifies D.
    const d=bits==="00"?rootId.get(scan[1]+"s"+(+scan[2]-1)):i;
    return pack(moveTail(d,1,w-2),a,1);
   }
   if(scan&&+scan[2]>0&&bits.length===1&&a===1)return pack(moveTail(i,1,w-1),a,1);
   // Instruction entry is aligned at G. Nonterminal instruction
   // consumes its known four binary digits without decoding.
   if(/^i[0-9]+$/.test(roots[i])&&bits.length===1&&a===0){
    const I=ins[+roots[i].slice(1)];if(I.op!=="halt"&&I.op!=="reject")return pack(moveTail(rootId.get(roots[i]+"s"+I.t),1,w-1),a,1);
   }
   // At the target tape, only genuine data blocks precede the head.
   // All unmarked codewords have final bit zero, including unused
   // binary words which cannot occur under the layout invariant.
   if(scan&&+scan[2]===0&&bits.length===w&&a===0&&/^[01]+$/.test(bits))return pack(i,a,1);
  }
  if(bits.length<w)return (returning?reversePrefixes:prefixes).has(bits)?pack(node(i,bits),a,returning?-1:1):invalid;
  const sym=dec.get(bits);if(!sym)return invalid;
  let j=2*(i*syms.length+symbolIds.get(sym)),n=logicalRows[j]>>>4,act=logicalRows[j+1],v=syms[Math.floor(act/3)],dir=act%3-1;
  // Return roots decode right-to-left, ending at the first digit.
  // On G, dispatch without repositioning. Otherwise continue left.
  if(returning){
   if(v===sym)return pack(n,a,dir);
   // On invalid blank/malformed symbols the logical ret rejects;
   // valid returns never rewrite. For blank, its first digit is 2.
   return invalid;
  }
  const toReturn=dir===-1&&n<rootCount&&(roots[n].startsWith("ret")||fused&&roots[n].startsWith("markL"));
  if(v===sym){
   if(dir===1)return pack(n,a,1);
   if(toReturn)return pack(moveTail(n,-1,w-1),a,-1);
   let distance=dir===0?w-1:2*w-1;return pack(moveTail(n,-1,distance-1),a,-1);
  }
  // Decoder has reached the last digit. A rightward rewrite need
  // visit only as far left as the first differing digit.
  const code=codes[v],old=codes[sym];
  let first=0;while(old[first]===code[first])first++;
  if(dir===1){
   if(first===w-1)return pack(n,+code[w-1],1);
   let tail=moveTail(n,1,w-first-1);
   let a=pack(tail,+code[first],1);tail=intern(a,a,a);
   for(let k=first+1;k<w-1;k++){
    if(old[k]===code[k])tail=intern(pack(tail,0,-1),pack(tail,1,-1),pack(tail,2,-1));
    else{a=pack(tail,+code[k],-1);tail=intern(a,a,a);}
   }
   return pack(tail,+code[w-1],-1);
  }
  // Left and stay already traverse the entire word; preserve known
  // unchanged digits to enable continuation sharing.
  let tail=dir===-1&&!toReturn?moveTail(n,-1,w-1):n;
  for(let k=0;k<w-1;k++){
   const direction=k===0&&dir===0?0:-1;
   if(old[k]===code[k])tail=intern(pack(tail,0,direction),pack(tail,1,direction),pack(tail,2,direction));
   else{const a=pack(tail,+code[k],direction);tail=intern(a,a,a);}
  }
  return pack(tail,+code[w-1],-1);
 }
 function node(i,p){return intern(transition(i,p,0),transition(i,p,1),transition(i,p,2));}
 for(let i=0;i<rootCount;i++){
 const shift=/^shift(ret[0-9]+):([01]+)$/.exec(roots[i]);
 if(!shift){put(i,transition(i,"",0),transition(i,"",1),transition(i,"",2));continue;}
 const [,d,c]=shift;let finish=invalid;
 // First physical blank is reached with exactly E in the FIFO.
 // Flush E into fresh blank cells and return aligned to previous block.
 if(c===codes.E){let tail=moveTail(rootId.get(d),-1,w-1);
  for(let j=w-1;j>=1;j--)tail=intern(invalid,invalid,pack(tail,+c[j],j===w-1?-1:1));
  finish=pack(tail,+c[0],1);
 }
 put(i,pack(rootId.get("shift"+d+":"+c.slice(1)+"0"),+c[0],1),pack(rootId.get("shift"+d+":"+c.slice(1)+"1"),+c[0],1),finish);
}
 const T=new Uint32Array(3*q);for(let i=0;i<q;i++)for(let a=0;a<3;a++){let v=get(i,a);T[3*i+a]=(v>>>4)>=H-1?pack(q+((v>>>4)===H-1?1:0),(v>>>2)&3,(v&3)-1):v;}
 return{q,T,w,codes,syms,logicalStates:logical.size,logicalRoots:rootCount,interned:used,entry:0};
}
module.exports={compile};
