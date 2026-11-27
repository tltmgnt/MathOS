// D6M: shared boundary rewind and canonical token skipping.
// Demand-driven append-only cache, exact D6L candidate traces.
// Genuine normalized canonical stream only. No host partition certificate.
function uncompressedMachine(full=false){
 const alphabet=["L","0","_","1","x"],ins=[];
 const add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const halt=add("halt",0,0),reject=add("reject",0,0),rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const Q=19,A=15,V=[16,17,18],G=Array.from({length:9},(_,i)=>i+1),R=[10,11,12],D=13,P=14,X=0;
 const CQ=V[1],CD=V[2];
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const app=(t,v,d)=>wr(t,v,mv(t,1,d));
 function word(t,s,d){for(let i=s.length-1;i>=0;i--)d=app(t,s[i],d);return d;}
 const clear=(t,d)=>start(t,loop(n=>rd(t,x=>x==="_"?start(t,d):bit(x)?app(t,"_",n):reject)));
 const copy=(a,b,d)=>start(a,loop(n=>rd(a,x=>x==="_"?d:bit(x)?app(b,x,mv(a,1,n)):reject)));
 const domain=x=>bit(x)||x==="x";
 function chosen(a,b,d){return start(a,loop(n=>rd(a,x=>x==="_"?d:domain(x)?app(b,x==="x"?"1":"0",mv(a,1,n)):reject)));}
 function field(out,d){return loop(n=>rd(Q,x=>x==="0"?(out===null?mv(Q,1,mv(Q,1,n)):mv(Q,1,rd(Q,y=>bit(y)?app(out,y,mv(Q,1,n)):reject))):x==="1"?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,d),reject)):reject));}
 // Generate original X words and cumulative Y words only after every mask passes.
 const done=start(X,halt),tail=copy(P,X,word(X,"00",done));
 function cumulative(t,d){
  const before=label(),after=label();
  bind(before,rd(t,x=>x==="_"?d:domain(x)?app(X,x==="x"?"1":"0",mv(t,1,x==="x"?after:before)):reject));
  bind(after,rd(t,x=>x==="_"?d:domain(x)?app(X,"1",mv(t,1,after)):reject));
  // omit rank-zero Y; if X0=1, all subsequent Y bits are one.
  return start(t,rd(t,x=>domain(x)?mv(t,1,x==="x"?after:before):reject));
 }
 let emit=tail;for(let t of G.slice().reverse())emit=cumulative(t,emit);
 for(let t of G.slice().reverse())emit=chosen(t,X,emit);
 emit=start(X,emit);
 const componentDone=label(),componentEntry=label(),selectComponent=label(),closure=label(),finish=test(CQ,x=>x==="_",componentDone,reject);
 const exhausted=label(),restart=label(),separatorEntry=label(),graphStart=label(),graphDone=label(),probeDone=label(),actualComponent=label();
 const retry=label(),attempt=label(),dispatch=label(),row=label(),advance0=label(),advance1=label(),advance2=label();
 const probeEntry=label(),probeAbort=label(),conflictDispatch=label(),resumeAdmission=label(),resumeDirect=label();
 const cachePrep=label(),cacheEntry=label(),cacheReady=label(),cacheAppend=label(),cacheSelect=label(),candidateEntry=label();
 // A pair uses a one-symbol third rank word. All other words are nonempty one-hot.
 function next(t,carry,normal){return mv(t,1,rd(t,x=>x==="_"?start(t,carry):bit(x)?normal:reject));}
 const end=rd(CQ,x=>x==="1"?mv(CQ,1,test(CQ,y=>y==="0",mv(CQ,1,dispatch),reject)):reject);
 bind(advance0,next(R[0],end,row));bind(advance1,next(R[1],advance0,row));bind(advance2,next(R[2],advance1,row));
 // Exactly one row can match a one-hot candidate. On a passing match,
 // consume the remaining field tokens without rank-cursor updates.
 // Skip the remaining whole tokens after the selected tuple. Run tokens
 // are restored before entering this routine, including an interrupted run.
 // Genuine canonical literal 00/01 has known length two. Its value
 // is irrelevant only in a skipped suffix/field, never in validation.
 function skipMask(d,t=Q){return loop(n=>rd(t,x=>x==="0"?mv(t,1,mv(t,1,n)):x==="1"?mv(t,1,rd(t,y=>y==="0"?mv(t,1,d):y==="1"?mv(t,1,n):reject)):reject));}
 const suffix=skipMask(dispatch,CQ);
 // Run tokens advance CQ immediately. Three virtual zero rows are
 // represented in finite control, with no tape mutation or decompression.
 function candidateRow(d,any,all){bind(d,rd(R[0],x=>x==="0"?any:x==="1"?rd(R[1],y=>y==="0"?any:y==="1"?rd(R[2],z=>z==="0"?any:z==="1"?all:reject):reject):reject));}
 let runAdvance=advance2;
 for(let k=3;k>=1;k--){
  const virtual=label();
  candidateRow(virtual,runAdvance,suffix);
  runAdvance=next(R[2],next(R[1],next(R[0],reject,virtual),virtual),virtual);
 }
 const token=selected=>rd(CQ,x=>x==="0"?mv(CQ,1,rd(CQ,y=>y==="0"?mv(CQ,1,selected?suffix:advance2):y==="1"?mv(CQ,1,selected?retry:advance2):reject)):x==="1"?mv(CQ,1,test(CQ,y=>y==="1",mv(CQ,1,selected?suffix:runAdvance),reject)):reject);
 candidateRow(row,token(false),token(true));
 const beginRows=start(R[0],start(R[1],start(R[2],row)));
 const load3=label(),load2=label(),load1=label(),kind=label();
 // Fixed-width binary scope IDs consume exactly four tape cells.
 function idRead(choose,p="",t=D){return p.length===4?(parseInt(p,2)<9?choose(parseInt(p,2)):reject):rd(t,x=>bit(x)?mv(t,1,idRead(choose,p+x,t)):reject);}
 function load(slot,d){return clear(R[slot],idRead(g=>chosen(G[g],R[slot],d),"",CD));}
 bind(load3,load(2,beginRows));bind(load2,load(1,kind));
 // A positions 1..5 retain the GAC budget, position 6 is a blank
 // delimiter, 7..15 are membership (0 unseen, 1 current, x solved).
 // After GAC, support scratch V0 is reused for a compact edge list.
 const graphTape=V[0];
 const offsets=new Map(),starts=new Map();
 function atA(pos,d){
  const k=pos+":"+d;if(starts.has(k))return starts.get(k);
  function advance(n){if(n===0)return d;const key=n+":"+d;if(!offsets.has(key))offsets.set(key,mv(A,1,advance(n-1)));return offsets.get(key);}
  const q=start(A,advance(pos-1));starts.set(k,q);return q;
 }
 function member(g,yes,no){return atA(7+g,rd(A,x=>x==="1"?yes:x==="0"||x==="x"?no:reject));}
 bind(load1,load(0,load2));
 bind(kind,rd(CD,x=>x==="0"?mv(CD,1,clear(R[2],app(R[2],"1",beginRows))):x==="1"?mv(CD,1,load3):reject));
 // A flag is consumed at each scope dispatch. Skip only masks proved all-zero.
 function skipScope(d){
  let tail=rd(D,x=>x==="0"?mv(D,1,d):x==="1"?mv(D,1,walkD(4,d)):reject);
  return walkD(8,tail);
 }
 function walkD(k,d){while(k--)d=mv(D,1,d);return d;}
 function indexed(d,active,end){
  const inactive=mv(Q,1,skipScope(d));
  return rd(Q,x=>x==="1"?mv(Q,1,rd(Q,y=>y==="0"?inactive:y==="1"?mv(Q,-1,active):reject)):x==="0"?active:x==="_"?test(D,y=>y==="_",end,reject):reject);
 }
 // The compact directory and stream contain active local factors only.
 bind(dispatch,rd(CQ,x=>bit(x)?load1:x==="_"||x==="x"?test(CD,y=>y===x,componentDone,reject):reject));
 const code=g=>g.toString(2).padStart(4,"0"),scopes=[];for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)scopes.push(code(i)+code(j)+"0");
 for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)for(let k=j+1;k<9;k++)scopes.push(code(i)+code(j)+"1"+code(k));
 scopes.sort((a,b)=>parseInt(a.length===9?a.slice(4,8):a.slice(9),2)-parseInt(b.length===9?b.slice(4,8):b.slice(9),2)||a.length-b.length||a.localeCompare(b));
 // Bounded GAC: every scope projects all currently supported tuples.
 // For a pair the third rank and support scratch each have length one.
 const pass=label(),prop=label(),pLoad2=label(),pKind=label(),pLoad3=label(),pRow=label(),pNext=label(),pCarry1=label(),pCarry0=label(),pEnd=label(),writeFirst=label(),writeSecond=label(),writeKind=label(),writeThird=label(),propDone=label(),candidateStart=label();
 function zeros(a,b,d){return start(a,loop(n=>rd(a,x=>x==="_"?d:bit(x)?app(b,"0",mv(a,1,n)):reject)));}
 // Prep must initialize supports before rewinding rank/support heads.
 const rewinds=R.reduceRight((d,t,i)=>start(t,start(V[i],d)),pRow);
 let prepared=rewinds;for(let i=2;i>=0;i--)prepared=clear(V[i],zeros(R[i],V[i],prepared));
 function adv(i,carry){return mv(R[i],1,mv(V[i],1,rd(R[i],x=>x==="_"?start(R[i],start(V[i],carry)):bit(x)?pRow:reject)));}
 bind(pNext,adv(2,pCarry1));bind(pCarry1,adv(1,pCarry0));bind(pCarry0,adv(0,pEnd));
 function support(d){return wr(V[0],"1",wr(V[1],"1",wr(V[2],"1",d)));}
 function propRow(d,pt0,pt1){bind(d,rd(R[0],x=>x==="0"?pt0:x==="1"?rd(R[1],y=>y==="0"?pt0:y==="1"?rd(R[2],z=>z==="0"?pt0:z==="1"?pt1:reject):reject):reject));}
 function virtualAdv(i,carry,d){return mv(R[i],1,mv(V[i],1,rd(R[i],x=>x==="_"?start(R[i],start(V[i],carry)):bit(x)?d:reject)));}
 let runNext=pNext;
 for(let k=3;k>=1;k--){
  const virtual=label();
  propRow(virtual,runNext,support(runNext));
  runNext=virtualAdv(2,virtualAdv(1,virtualAdv(0,reject,virtual),virtual),virtual);
 }
 const tokenP=allowed=>rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?mv(Q,1,allowed&&y==="0"?support(pNext):pNext):reject)):x==="1"?mv(Q,1,test(Q,y=>y==="1",mv(Q,1,allowed?support(runNext):runNext),reject)):reject);
 propRow(pRow,tokenP(false),tokenP(true));
 function back(t,k,d){while(k--)d=mv(t,-1,d);return d;}
 // At record end, the third scratch length distinguishes pair and triple.
 const pairBack=back(D,9,writeFirst),tripleBack=back(D,13,writeFirst);
 const rewindD=start(R[2],mv(R[2],1,rd(R[2],x=>x==="_"?pairBack:bit(x)?tripleBack:reject)));
 bind(pEnd,rd(Q,x=>x==="1"?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,rewindD),reject)):reject));
 function loadDomain(slot,d){return clear(R[slot],idRead(g=>copy(G[g],R[slot],d)));}
 bind(pLoad3,loadDomain(2,prepared));
 bind(pKind,rd(D,x=>x==="0"?mv(D,1,clear(R[2],app(R[2],"1",prepared))):x==="1"?mv(D,1,pLoad3):reject));
 bind(pLoad2,loadDomain(1,pKind));
 const pLoad1=loadDomain(0,pLoad2);
 bind(prop,indexed(prop,pLoad1,propDone));
 function update(t,v,d){
  const scan=[label(),label()];
  for(let seen=0;seen<2;seen++)bind(scan[seen],rd(v,x=>x==="_"?(seen?test(t,y=>y==="_",d,reject):reject):bit(x)?rd(t,y=>!bit(y)||x==="1"&&y==="0"?reject:(()=>{
   const cont=mv(v,1,mv(t,1,scan[seen||+(x==="1")]));
   return x===y?cont:wr(t,"0",start(A,wr(A,"1",cont)));
  })()):reject));
  return start(t,start(v,scan[0]));
 }
 function putDomain(v,d){return idRead(g=>update(G[g],v,d));}
 bind(writeFirst,putDomain(V[0],writeSecond));bind(writeSecond,putDomain(V[1],writeKind));
 bind(writeKind,rd(D,x=>x==="0"?mv(D,1,prop):x==="1"?mv(D,1,writeThird):reject));bind(writeThird,putDomain(V[2],prop));
 let skip=start(D,prop);for(let j=0;j<11;j++)skip=field(null,skip);
 bind(pass,start(A,wr(A,"0",start(Q,skip))));
 // A is change flag plus four budget slots. A changed pass consumes one
 // slot; the fourth changed pass ends at its resulting (possibly nonfixed) domains.
 const consume=loop(n=>rd(A,x=>x==="1"?mv(A,1,n):x==="0"?wr(A,"1",mv(A,1,rd(A,y=>y==="_"?candidateStart:y==="0"?pass:reject))):reject));
 bind(propDone,start(A,rd(A,x=>x==="1"?(full?pass:mv(A,1,consume)):x==="0"?candidateStart:reject)));
 // Complete candidate enumeration of the surviving domain product.
 // x is the selected allowed rank; 1 is an unselected allowed rank.
 // Last group is fastest, reset to first allowed rank on carry.
 function first(t,d){return start(t,loop(n=>rd(t,x=>x==="0"?mv(t,1,n):x==="1"?wr(t,"x",d):reject)));}
 // Reset a selected suffix domain to its first surviving rank.
 function reset(t,d){
  const restore=loop(n=>rd(t,x=>bit(x)?mv(t,1,n):x==="x"?wr(t,"1",d):reject));
  return start(t,loop(n=>rd(t,x=>x==="0"?mv(t,1,n):x==="x"?d:x==="1"?wr(t,"x",mv(t,1,restore)):reject)));
 }
 function increment(t,carry){
  const seekNext=loop(n=>rd(t,x=>x==="0"?mv(t,1,n):x==="1"?wr(t,"x",attempt):x==="_"?first(t,carry):reject));
  return start(t,loop(n=>rd(t,x=>bit(x)?mv(t,1,n):x==="x"?wr(t,"1",mv(t,1,seekNext)):reject)));
 }
 const prior=[];let carry=exhausted;for(let g=0;g<9;g++){prior.push(carry);carry=member(g,increment(G[g],carry),carry);}
 // The failed selected tuple belongs to the current D record.
 // Its largest group index is the second ID for pairs, third for triples.
 // At failure D is just after the record, R2 has length 1 for pairs.
 // On a selected forbidden row Q already points to the next token.
 // While earlier coordinates of this factor stay fixed, its remaining
 // last-coordinate rows are contiguous. Scan only until domain exhaustion.
 // A four-zero run may cross the slice boundary: never advance beyond it.
 function extend(g){
  const t=G[g],scan=label(),overflow=first(t,prior[g]);
  const choose=wr(t,"x",attempt);
  function advance(d){return mv(t,1,d);}
  const allowed=d=>rd(t,x=>x==="1"?choose:x==="0"?advance(d):x==="_"?overflow:reject);
  let run=scan;for(let k=0;k<4;k++)run=allowed(run);
  const literal=rd(CQ,x=>x==="0"?mv(CQ,1,rd(CQ,y=>y==="0"?mv(CQ,1,allowed(scan)):y==="1"?mv(CQ,1,advance(scan)):reject)):x==="1"?mv(CQ,1,test(CQ,y=>y==="1",mv(CQ,1,run),reject)):reject);
  bind(scan,rd(t,x=>bit(x)?literal:x==="_"?overflow:reject));
  const seek=loop(n=>rd(t,x=>bit(x)?mv(t,1,n):x==="x"?wr(t,"1",advance(scan)):reject));
  return start(t,seek);
 }
 const targets=G.map((t,g)=>G.reduceRight((next,u,j)=>j>g?member(j,reset(u,next),next):next,extend(g)));
 // A conflict entirely in the two-coordinate prefix rejects that branch.
 const selectConflict=idRead(g=>g===1?atA(18,rd(A,x=>x==="1"?exhausted:x==="0"?targets[g]:reject)):targets[g],"",CD);
 bind(conflictDispatch,start(R[2],mv(R[2],1,rd(R[2],x=>x==="_"?back(CD,5,selectConflict):bit(x)?back(CD,4,selectConflict):reject))));
 // A20=1 during direct probe, 0 otherwise. A21..24 count failed
 // complete candidates; the fourth failed validation triggers restart.
 const budget=loop(n=>rd(A,x=>x==="1"?mv(A,1,n):x==="0"?wr(A,"1",mv(A,1,rd(A,y=>y==="_"?probeAbort:y==="0"?conflictDispatch:reject))):reject));
 bind(retry,atA(20,rd(A,x=>x==="1"?mv(A,1,budget):x==="0"?conflictDispatch:reject)));
 // A25 stays blank (probe-budget terminator).
 // Every cached block begins with x on both tapes; internal tokens are binary.
 // On retry, the failed field has been consumed at least partly. Move
 // left once (CD may be at the next boundary), then seek the nearest x.
 // A direct block starts at L; cached blocks start at x. A retry
 // starts after a consumed field/row, and never needs a mode test.
 function rewindBlock(t,d){return mv(t,-1,loop(n=>rd(t,x=>x==="x"||x==="L"?mv(t,1,d):bit(x)?mv(t,-1,n):reject)));}
 // At aligned block boundaries, x means already built, blank means
 // demand for the next block. Both tapes must agree.
 const nextBlock=rd(CQ,x=>x==="x"?test(CD,y=>y==="x",mv(CQ,1,mv(CD,1,candidateEntry)),reject):x==="_"?test(CD,y=>y==="_",cacheEntry,reject):reject);
 bind(cacheSelect,start(CQ,start(CD,nextBlock)));
 bind(candidateEntry,dispatch);
 bind(attempt,rewindBlock(CQ,rewindBlock(CD,candidateEntry)));
 let initCandidate=selectComponent;for(const t of G.slice().reverse())initCandidate=first(t,initCandidate);
 // Prefix separator is the first original coordinate: the first feasible
 // surviving separator rank gives the global lexicographic minimum.
 function advanceRoot(t,overflow){
  const nextRoot=loop(n=>rd(t,x=>x==="0"?mv(t,1,n):x==="1"?wr(t,"x",restart):x==="_"?overflow:reject));
  const seekRoot=loop(n=>rd(t,x=>bit(x)?mv(t,1,n):x==="x"?wr(t,"1",mv(t,1,nextRoot)):reject));
  return start(t,seekRoot);
 }
 const advance0Root=advanceRoot(G[0],reject),advance1Root=advanceRoot(G[1],first(G[1],advance0Root));
 bind(exhausted,atA(17,rd(A,x=>x==="1"?atA(18,rd(A,y=>y==="0"?advance0Root:y==="1"?advance1Root:reject)):reject)));
 let resetResidual=separatorEntry;for(const t of G.slice(2).reverse())resetResidual=reset(t,resetResidual);
 // A19: 1 first residual block, 0 later/direct, x reuse pending.
 // A failure in the first block leaves the same membership; the cache
 // contains every reached residual block and remains immutable across prefixes.
 const resetBranch=atA(18,rd(A,x=>x==="1"?resetResidual:x==="0"?reset(G[1],resetResidual):reject));
 bind(restart,atA(19,rd(A,x=>x==="1"?wr(A,"x",resetBranch):x==="0"?resetBranch:reject)));
 const freshBranch=atA(18,rd(A,x=>x==="1"?atA(7,word(A,"xx0000000",selectComponent)):x==="0"?atA(7,word(A,"x00000000",selectComponent)):reject));
 bind(separatorEntry,atA(19,rd(A,x=>x==="x"?componentEntry:x==="0"?wr(A,"1",freshBranch):reject)));
 // candidateStart is bound below, after constructing the edge-list producer.
 // Mark one solved component and choose the smallest still-unseen group.
 let mark=selectComponent;
 for(let g=8;g>=0;g--){const d=mark;mark=atA(7+g,rd(A,x=>x==="1"?wr(A,"x",d):x==="0"||x==="x"?d:reject));}
 bind(componentDone,atA(17,rd(A,x=>x==="1"?atA(19,wr(A,"0",mark)):x==="0"?mark:reject)));
 let seed=emit;
 for(let g=8;g>=0;g--){const d=seed;seed=atA(7+g,rd(A,x=>x==="0"?wr(A,"1",closure):x==="x"?d:reject));}
 bind(selectComponent,seed);
 // Closure scans only the scratch edge list, never the source stream.
 // A1 is the change flag. An 8-bit edge consists of two 4-bit IDs.
 const edgeLoop=label();
 function addMember(g,d){return atA(7+g,rd(A,x=>x==="0"?wr(A,"1",atA(1,wr(A,"1",d))):x==="1"?d:reject));}
 function graphId(choose,p=""){return p.length===4?(parseInt(p,2)<9?choose(parseInt(p,2)):reject):rd(graphTape,x=>bit(x)?mv(graphTape,1,graphId(choose,p+x)):reject);}
 function walk(t,k,d){while(k--)d=mv(t,1,d);return d;}
 const backwards=back(graphTape,8,graphId(g=>addMember(g,walk(graphTape,4,edgeLoop))));
 const secondNo=graphId(g=>member(g,backwards,edgeLoop));
 const secondYes=graphId(g=>addMember(g,edgeLoop));
 const edgeFirst=graphId(g=>member(g,secondYes,secondNo));
 const afterClosure=label(),sweepEnd=atA(1,rd(A,x=>x==="1"?closure:x==="0"?afterClosure:reject));
 bind(edgeLoop,rd(graphTape,x=>bit(x)?edgeFirst:x==="_"?sweepEnd:reject));
 bind(closure,atA(1,wr(A,"0",start(graphTape,edgeLoop))));
 // Singleton components have no active higher-arity factors: their
 // first surviving unary rank already solves them, so skip candidate scans.
 const buildLocal=label();let zero=reject,one=componentDone;
 for(let g=8;g>=0;g--){const z=zero,o=one;zero=member(g,o,z);one=member(g,buildLocal,o);}
 const conditionedComponent=atA(19,rd(A,x=>x==="x"?wr(A,"1",cacheSelect):x==="1"?cacheSelect:x==="0"?nextBlock:reject));
 bind(actualComponent,atA(17,rd(A,x=>x==="1"?conditionedComponent:x==="0"?zero:reject)));
 // Probe events are not candidate/component trace events.
 bind(componentEntry,actualComponent);
 const componentOrProbe=atA(17,rd(A,x=>x==="1"?componentEntry:x==="0"?atA(16,rd(A,y=>y==="0"?componentEntry:y==="1"||y==="x"?probeDone:reject)):reject));
 bind(afterClosure,componentOrProbe);
 // Materialize only active local records, in the original prefix order.
 const local=label(),localEnd=atA(17,rd(A,x=>x==="1"?cacheReady:x==="0"?attempt:reject));
 const fieldCopy=loop(n=>rd(Q,x=>x==="0"?app(CQ,x,mv(Q,1,rd(Q,y=>bit(y)?app(CQ,y,mv(Q,1,n)):reject))):x==="1"?app(CQ,x,mv(Q,1,rd(Q,y=>y==="0"?app(CQ,y,mv(Q,1,local)):y==="1"?app(CQ,y,mv(Q,1,n)):reject))):reject));
 function copyDir(k,d){if(!k)return d;const next=copyDir(k-1,d);return rd(D,x=>bit(x)?app(CD,x,mv(D,1,next)):reject);}
 const copyKind=rd(D,x=>x==="0"?app(CD,x,mv(D,1,fieldCopy)):x==="1"?app(CD,x,mv(D,1,copyDir(4,fieldCopy))):reject);
 const copyRecord=back(D,4,copyDir(8,copyKind)),omit=walkD(4,rd(D,x=>x==="0"?mv(D,1,skipMask(local)):x==="1"?mv(D,1,walkD(4,skipMask(local))):reject));
 // For conditioned factors starting with 0, select by the second ID;
 // the residual graph ensures that all remaining IDs are in that block.
 const copyRootRecord=back(D,8,copyDir(8,copyKind)),omitRoot=rd(D,x=>x==="0"?mv(D,1,skipMask(local)):x==="1"?mv(D,1,walkD(4,skipMask(local))):reject);
 const rootOnlyThird=idRead(g=>member(g,back(D,13,copyDir(8,copyKind)),skipMask(local)));
 // Prefix-only pair is checked in the first residual block only.
 // It remains true for all later blocks in the same prefix branch.
 const prefixPair=atA(19,rd(A,x=>x==="1"?copyRootRecord:x==="0"?mv(D,1,skipMask(local)):reject));
 const bothRootLocal=rd(D,x=>x==="0"?prefixPair:x==="1"?mv(D,1,rootOnlyThird):reject);
 const rootLocal=idRead(g=>g===1?atA(18,rd(A,x=>x==="1"?bothRootLocal:x==="0"?member(g,copyRootRecord,omitRoot):reject)):member(g,copyRootRecord,omitRoot));
 const localActive=idRead(g=>g===0?atA(17,rd(A,x=>x==="1"?rootLocal:x==="0"?member(g,copyRecord,omit):reject)):g===1?atA(18,rd(A,x=>x==="1"?rootLocal:x==="0"?member(g,copyRecord,omit):reject)):member(g,copyRecord,omit));
 bind(local,indexed(local,localActive,localEnd));
 let localScan=start(D,local);for(let i=0;i<11;i++)localScan=field(null,localScan);
 bind(buildLocal,clear(CQ,clear(CD,start(Q,localScan))));
 function clearCache(t,d){return start(t,loop(n=>rd(t,x=>x==="_"?start(t,d):domain(x)?app(t,"_",n):reject)));}
 // Both heads already point to the append frontier. No global scan.
 bind(cacheEntry,cacheAppend);
 bind(cacheAppend,app(CQ,"x",app(CD,"x",start(Q,localScan))));
 bind(cachePrep,clearCache(CQ,clearCache(CD,separatorEntry)));
 // After construction, rewind just the appended block, including empty blocks.
 bind(cacheReady,attempt);
 // Load unary domains once; pass and candidate scans never alter Q.
 function unary(t,d){const seen=[label(),label()];for(let k=0;k<=1;k++)bind(seen[k],rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?app(t,y==="0"?"1":"0",mv(Q,1,seen[k||+(y==="0")])):reject)):x==="1"&&k===1?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,d),reject)):reject));return start(t,seen[0]);}
 let init=start(A,word(A,"00000",pass));for(let t of G.slice().reverse())init=unary(t,init);
 const initEntry=start(Q,field(null,start(P,field(P,init))));
 // Scan the actual producer stream once after GAC. Append one edge
 // for a pair and two star edges for a triple. D is the genuine
 // fixed scope directory; no host graph or partition is supplied.
 const graph=label(),afterField=skipMask(graph);
 function copyId(n,d){if(!n)return d;const next=copyId(n-1,d);return rd(D,x=>bit(x)?app(graphTape,x,mv(D,1,next)):reject);}
 const third=back(D,8,copyId(4,walkD(5,copyId(4,afterField))));
 const kindEdge=rd(D,x=>x==="0"?mv(D,1,afterField):x==="1"?third:reject);
 // In residual mode a pair (0,j) contributes no edge; a triple
 // (0,j,k) contributes the essential residual edge (j,k).
 const residualKind=rd(D,x=>x==="0"?mv(D,1,afterField):x==="1"?back(D,4,copyId(4,mv(D,1,copyId(4,afterField)))):reject);
 const rootGraph=walkD(4,residualKind);
 const bothRootGraph=rd(D,x=>x==="0"?mv(D,1,afterField):x==="1"?mv(D,1,walkD(4,afterField)):reject);
 const twoRootGraph=idRead(g=>g===1?bothRootGraph:residualKind);
 const ordinaryGraph=back(D,4,copyId(8,kindEdge));
 const graphActive=idRead(g=>g===0?atA(16,rd(A,x=>x==="x"?atA(18,rd(A,y=>y==="1"?twoRootGraph:y==="0"?rootGraph:reject)):x==="0"||x==="1"?ordinaryGraph:reject)):g===1?atA(18,rd(A,x=>x==="1"?rootGraph:x==="0"?ordinaryGraph:reject)):ordinaryGraph);
 bind(graph,indexed(graph,graphActive,graphDone));
 let scanGraph=start(D,graph);for(let j=0;j<11;j++)scanGraph=field(null,scanGraph);
 // Probe original connectedness first. A16=1 original probe,
 // x residual probe/conditioned, 0 direct. A17=1 actual conditioning.
 bind(graphStart,clear(graphTape,start(Q,scanGraph)));
 bind(candidateStart,atA(7,word(A,"000000000100000000",graphStart)));
 const directInit=atA(7,word(A,"000000000000000000",initCandidate));
 const rootProbe=atA(7,word(A,"100000000",closure));
 const residualProbe=atA(18,rd(A,x=>x==="1"?atA(7,word(A,"xx1000000",closure)):x==="0"?atA(7,word(A,"x10000000",closure)):reject));
 bind(graphDone,atA(16,rd(A,x=>x==="0"?atA(7,word(A,"111111111",resumeDirect)):x==="1"?rootProbe:x==="x"?residualProbe:reject)));
 const directRebuild=atA(18,wr(A,"0",atA(16,wr(A,"0",graphStart))));
 const twoRebuild=atA(18,wr(A,"1",graphStart));
 const residualRebuild=atA(16,wr(A,"x",graphStart));
 // Probe only an actually connected original graph. All nine groups
 // are already current after closure. Probe uses unchanged local search.
 let probeInit=probeEntry;for(const t of G.slice().reverse())probeInit=first(t,probeInit);
 bind(probeEntry,atA(20,word(A,"10000",componentEntry)));
 // No propagation domain is changed by candidate enumeration. Clear
 // exactly the chosen marker in each rank word, so first() remains valid.
 function unchoose(t,d){return start(t,loop(n=>rd(t,x=>bit(x)?mv(t,1,n):x==="x"?wr(t,"1",d):reject)));}
 let uninit=resumeAdmission;for(const t of G.slice().reverse())uninit=unchoose(t,uninit);
 // Preserve the fourth conflict checkpoint while probing residual graphs.
 // Q/D/graphTape/A are the only tapes touched by the graph probes.
 // If neither separator splits, resume the exact failed tuple extension.
 // Only an admitted separator discards the joint enumeration checkpoint.
 bind(probeAbort,atA(20,wr(A,"0",residualRebuild)));
 bind(resumeDirect,conflictDispatch);
 let conditionedInit=cachePrep;for(const t of G.slice().reverse())conditionedInit=first(t,conditionedInit);
 bind(resumeAdmission,conditionedInit);
 const admit=atA(17,wr(A,"1",uninit));
 let allOriginal=probeInit,allResidual=twoRebuild,allTwo=directRebuild;
 for(let g=8;g>=0;g--){allOriginal=member(g,allOriginal,directInit);if(g>0)allResidual=member(g,allResidual,admit);if(g>1)allTwo=member(g,allTwo,admit);}
 bind(probeDone,atA(16,rd(A,x=>x==="1"?allOriginal:x==="x"?atA(18,rd(A,y=>y==="1"?allTwo:y==="0"?allResidual:reject)):reject)));
 const entry=start(D,word(D,scopes.join(""),initEntry));
 return {alphabet,ins,tapes:20,entry,witnessTape:X,streamTape:Q,candidateEntry,conflictEntry:retry,componentDone,componentEntry,separatorEntry,probeEntry,probeAbort,resumeDirect,cachePrep,cacheEntry,cacheReady};
}

function executeIR(J,inputs,trace=null){
 const T=inputs.map(s=>["L",...s,"_"]),h=T.map(()=>0);let pc=J.entry,steps=0,jumps=0;
 while(true){if(trace&&(pc===J.candidateEntry||pc===J.conflictEntry||pc===J.componentEntry||pc===J.separatorEntry||pc===J.probeEntry||pc===J.probeAbort||pc===J.resumeDirect||pc===J.cachePrep||pc===J.cacheEntry||pc===J.cacheReady))trace(pc,T,h);const a=J.ins[pc];if(a.op==="halt"||a.op==="reject")return {status:a.op,steps,tapes:T.map(t=>t.slice(1).join("").replace(/_+$/,"")),heads:h};if(a.op==="jump"){if(++jumps>10000000)throw Error("jump limit");pc=a.next;continue;}if(++steps>10000000)throw Error("step limit");const k=a.t,x=T[k][h[k]];
  if(a.op==="read"){pc=a.next[J.alphabet.indexOf(x)];continue;}
  if(a.op==="write"){if(x==="L")throw Error("sentinel");T[k][h[k]]=a.next.v;}
  else if(a.op==="move"){h[k]+=a.next.dir;if(h[k]<0)throw Error("left");if(h[k]===T[k].length)T[k].push("_");}else throw Error("op");pc=a.next.d;
 }
}

function stream(E,raw){
 const d=E.decode(raw);if(!d)throw Error("normalized precondition");
 const groups=[0,1,2,3,4,5,6,7,8],fields=[(d.m-1).toString(2).split("").reverse().join(""),d.pins.join("")];
 const order=[...E.subsets(groups,1),...[2,3].flatMap(k=>[...E.subsets(groups,k)]).sort((a,b)=>a.at(-1)-b.at(-1)||a.length-b.length||a.join().localeCompare(b.join()))];
 for(const h of order){const k=h.length;const f=d.F.find(x=>x.h.join()===h.join());fields.push([...E.tup(d.m,k)].map(z=>f&&!f.S.has(z.join())?"1":"0").join(""));}
 return fields.map((s,i)=>{if(i>=11&&!s.includes("1"))return "10";let out="";for(let k=0;k<s.length;){if(i>=11&&s.slice(k,k+4)==="0000"){out+="11";k+=4;}else out+="0"+s[k++];}return out+"10";}).join("");
}

// Contract unobservable jumps and refine the deterministic instruction
// graph by opcode, tape, action, trace tag and successor classes.
// Trace entries are unique observable barriers; no primitive is removed
// by this pass. Each retained instruction has identical local semantics.
function compactIR(J){
 const eventKeys=["candidateEntry","conflictEntry","componentDone","componentEntry","separatorEntry","probeEntry","probeAbort","resumeDirect","cachePrep","cacheEntry","cacheReady"];
 const tags=new Map();for(const k of eventKeys){const i=J[k];tags.set(i,(tags.get(i)||[]).concat(k));}
 const resolve=i=>{let n=0;while(J.ins[i].op==="jump"&&!tags.has(i)){i=J.ins[i].next;if(++n>J.ins.length||i<0)throw Error("jump cycle");}return i;};
 const dest=I=>I.op==="read"?I.next:I.op==="jump"?[I.next]:I.op==="write"||I.op==="move"?[I.next.d]:[];
 const ids=[],pos=new Map(),visit=i=>{i=resolve(i);if(!pos.has(i)){pos.set(i,ids.length);ids.push(i);}return pos.get(i);};
 visit(J.entry);for(const k of eventKeys)visit(J[k]);
 for(let i=0;i<ids.length;i++)for(const d of dest(J.ins[ids[i]]))visit(d);
 const rows=ids.map(i=>{const I=J.ins[i];return {base:JSON.stringify([I.op,I.t,I.op==="write"?I.next.v:I.op==="move"?I.next.dir:null,tags.get(i)||[]]),dest:dest(I).map(d=>pos.get(resolve(d)))};});
 function partition(prev){const map=new Map();const cls=rows.map((r,i)=>{const key=r.base+"|"+(prev?r.dest.map(d=>prev.cls[d]).join(","):"");if(!map.has(key))map.set(key,map.size);return map.get(key);});return {cls,n:map.size};}
 let old=partition(null),rounds=0;
 for(;;){const now=partition(old);rounds++;if(now.n===old.n){old=now;break;}if(now.n<old.n||rounds>rows.length)throw Error("refinement");old=now;}
 const map=i=>old.cls[pos.get(resolve(i))],ins=new Array(old.n);
 for(const i of ids){const j=map(i),I=J.ins[i];if(ins[j])continue;let next=I.next;
  if(I.op==="read")next=next.map(map);else if(I.op==="jump")next=map(next);else if(I.op==="write"||I.op==="move")next={...next,d:map(next.d)};
  ins[j]={...I,next};
 }
 // Verify every original reachable/observable instruction against its
 // representative, including the exact order of all five read branches.
 for(const i of ids){const I=J.ins[i],K=ins[map(i)],a=dest(I).map(map),b=dest(K);if(I.op!==K.op||I.t!==K.t||JSON.stringify(a)!==JSON.stringify(b)||I.op==="write"&&I.next.v!==K.next.v||I.op==="move"&&I.next.dir!==K.next.dir)throw Error("quotient simulation");}
 const out={...J,ins,entry:map(J.entry),compaction:{original:J.ins.length,retained:ids.length,compact:ins.length,rounds,checks:ids.length}};
 for(const k of eventKeys)out[k]=map(J[k]);
 return out;
}

function machine(full=false){return compactIR(uncompressedMachine(full));}
module.exports={machine,uncompressedMachine,compactIR,executeIR,stream};
