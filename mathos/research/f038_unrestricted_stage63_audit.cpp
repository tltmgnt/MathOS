// Exact finite stage-63 audit. Default is PARTIAL. Full clock is opt-in.
#include <array>
#include <vector>
#include <unordered_map>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <algorithm>
#include <string>
using U=uint64_t;
using W=__uint128_t;
constexpr int n=93,L=1055520,full=1<<21;
constexpr W pin=(W(0x1234567)<<64)|W(0x123456789abcdef0ULL);
void req(bool b,const char*s){if(!b)throw std::runtime_error(s);}
struct Tr{int a,w,m;};
Tr tr(int v){return{v/9,v/3%3,v%3-1};}
std::vector<uint8_t> input(){
 std::vector<uint8_t>S(n+1+2*n+2*n*(n-1),0);
 std::fill_n(S.begin(),n,1);S.reserve(L);
 for(int i=1;i<=n;i++)for(int j=i+1;j<=n;j++)for(int k=j+1;k<=n;k++)
  for(int b=0;b<8;b++)S.push_back(j==n-1&&k==n&&bool(b&4)==bool((pin>>(i-1))&1));
 req(S.size()==L&&std::count(S.begin()+n+1,S.end(),1)==364,"input geometry");
 return S;
}
template<size_t N>void print(const std::array<U,N>&a){std::cout<<'[';for(size_t i=0;i<N;i++){if(i)std::cout<<',';std::cout<<a[i];}std::cout<<']';}
struct Scalar{
 int q,cap,off,sz;std::vector<uint8_t>A;std::array<int,6>T;
 std::vector<std::pair<int,int>>undo;std::array<U,7>pow{};
 // Malformed, wrong, closed state set, cycle, drift, horizon, witness.
 std::array<U,7>cnt{},leaves{};U branches=0,steps=0;
 struct Rec{int h,a,old;bool fresh;U hash;};
 static U mix(U x){x+=0x9e3779b97f4a7c15ULL;x=(x^(x>>30))*0xbf58476d1ce4e5b9ULL;x=(x^(x>>27))*0x94d049bb133111ebULL;return x^(x>>31);}
 void leaf(int k,int u){cnt[k]+=pow[u];leaves[k]++;}
 bool closed(int a){
  int reachable=1<<a;
  for(int i=0;i<q;i++){int old=reachable;for(int s=0;s<q;s++)if(reachable>>s&1)for(int b=0;b<3;b++){
    int v=T[3*s+b];if(v<0||tr(v).a==q)return false;reachable|=1<<tr(v).a;
  }if(reachable==old)return true;}
  return true;
 }
 Scalar(int q0,int c,const std::vector<uint8_t>&S):q(q0),cap(c),off(c+2),sz(S.size()),A(2*c+S.size()+n+8,2){
  std::copy(S.begin(),S.end(),A.begin()+off);T.fill(-1);pow[0]=1;
  for(int i=1;i<=3*q;i++)pow[i]=pow[i-1]*9*(q+1);
 }
 void visit(int a,int h,int t,int u,int lo,int hi,U hash){
  size_t root=undo.size();std::array<Rec,16>R{};int len=0;
  int ca=a,ch=h,ct=t,span=1;U ck=hash;size_t cu=undo.size();
  std::array<std::array<int,2>,2>frontier{};
  std::array<std::array<std::array<uint8_t,16>,2>,2>band{};
  for(auto&f:frontier)f.fill(-1);
  bool safe_state[2]={closed(0),q==2&&closed(1)};
  if(closed(a)){leaf(2,u);return;}
  while(t<cap){
   bool fresh=h<lo||h>hi;int dir=h<lo?-1:1;bool done=false;
   if(safe_state[a]){leaf(2,u);break;}
   // A hash only proposes a recurrence; all cells touched since checkpoint
   // must equal their exact original values.
   if(t>ct&&a==ca&&h==ch&&hash==ck){
    std::unordered_map<int,int>before;
    for(size_t j=cu;j<undo.size();j++)before.emplace(undo[j].first,undo[j].second);
    bool equal=true;for(auto [i,v]:before)if(A[i]!=v){equal=false;break;}
    if(equal){leaf(3,u);break;}
   }
   if(t-ct>=span){ct=t;ca=a;ch=h;ck=hash;cu=undo.size();span*=2;}
   // Fresh exterior blank plus identical 16-cell inward band; the prior
   // trace must never have read beyond that band.
   for(int s=0;s<q;s++){
    if(frontier[0][s]>=0&&h>frontier[0][s]+16)frontier[0][s]=-1;
    if(frontier[1][s]>=0&&h<frontier[1][s]-16)frontier[1][s]=-1;
   }
   if(fresh&&(h<off||h>=off+sz)){
    int side=h<off?0:1,prev=frontier[side][a];
    if(prev>=0&&prev!=h){
     bool same=true;for(int j=1;j<=16;j++)if(A[h-dir*j]!=band[side][a][j-1]){same=false;break;}
     if(same){leaf(4,u);break;}
    }
    frontier[side][a]=h;for(int j=1;j<=16;j++)band[side][a][j-1]=A[h-dir*j];
   }
   for(int lag=1;lag<=std::min(len,16);lag++){
    const auto&r=R[(len-lag)&15];if(r.a!=a)continue;
    if(r.h==h&&r.hash==hash){
     bool equal=true;
     for(int j=len-lag;j<len;j++){
      const auto&v=R[j&15];bool first=true;
      for(int k=len-lag;k<j;k++)if(R[k&15].h==v.h){first=false;break;}
      if(first&&A[v.h]!=v.old){equal=false;break;}
     }
     if(equal){leaf(3,u);done=true;break;}
    }
    if(fresh&&r.fresh&&((dir==-1&&h<r.h&&r.h<off)||(dir==1&&h>r.h&&r.h>=off+sz))){
     bool safe=true;
     for(int j=len-lag;j<len;j++){int x=R[j&15].h;if(dir*(x-r.h)<0||dir*(h-x)<=0){safe=false;break;}}
     if(safe){leaf(4,u);done=true;break;}
    }
   }
   if(done)break;
   int sym=A[h],k=3*a+sym,v=T[k];
   if(v<0){++branches;for(int b=0;b<9*(q+1);b++){T[k]=b;visit(a,h,t,u-1,lo,hi,hash);}T[k]=-1;break;}
   R[len&15]={h,a,sym,fresh,hash};len++;lo=std::min(lo,h);hi=std::max(hi,h);
   auto b=tr(v);
   if(sym!=b.w){undo.emplace_back(h,sym);hash^=mix(U(h)*3+sym)^mix(U(h)*3+b.w);A[h]=b.w;}
   h+=b.m;t++;steps++;
   if(b.a==q){
    W w=0;bool ok=true;for(int i=0;i<n;i++){int x=A[h+i];if(x==2){ok=false;break;}w|=W(x)<<i;}
    leaf(!ok?0:((w&((W(1)<<91)-1))==pin?6:1),u);break;
   }
   a=b.a;if(t==cap){leaf(5,u);break;}
  }
  while(undo.size()>root){auto[i,v]=undo.back();undo.pop_back();A[i]=v;}
 }
 void run(){visit(0,off,0,3*q,off,off+sz-1,0);U sum=0;for(auto x:cnt)sum+=x;req(sum==pow[3*q],"scalar coverage");}
 void report(){std::cout<<'[';print(cnt);std::cout<<',';print(leaves);std::cout<<','<<branches<<','<<steps<<']';}
};
// Persistent, canonically interned binary tape blocks. Node equality is exact,
// not hash equality; unordered_map compares its full keys.
struct Node{int a,b;};
struct Tape{
 std::vector<Node>V{{-1,-1},{-1,-1},{-1,-1}};std::unordered_map<U,int>I;
 int node(int a,int b){U k=(U(a)<<32)|U(b);auto it=I.find(k);if(it!=I.end())return it->second;int id=V.size();V.push_back({a,b});I.emplace(k,id);return id;}
 int uniform(int b,int lev){for(int i=0;i<lev;i++)b=node(b,b);return b;}
 int get(int id,int lev,int p){while(lev){int h=1<<--lev;auto v=V[id];if(p<h)id=v.a;else{id=v.b;p-=h;}}return id;}
 int put(int id,int lev,int p,int b){if(!lev)return b;int h=1<<(lev-1);auto v=V[id];return p<h?node(put(v.a,lev-1,p,b),v.b):node(v.a,put(v.b,lev-1,p-h,b));}
 int range(int id,int lev,int a,int b,int sym){
  if(a==b)return id;
  int sz=1<<lev;if(a==0&&b==sz)return uniform(sym,lev);
  int h=sz/2;auto v=V[id];if(a<h)v.a=range(v.a,lev-1,a,std::min(h,b),sym);
  if(b>h)v.b=range(v.b,lev-1,std::max(0,a-h),b-h,sym);
  return node(v.a,v.b);
 }
};
enum{EXIT,HALT,UNKNOWN,LOOP,TIME};
struct Result{int id,p,a,t,kind;};
struct Key{int id,p,a,tab;bool operator==(const Key&k)const{return id==k.id&&p==k.p&&a==k.a&&tab==k.tab;}};
struct Hash{size_t operator()(const Key&k)const{U x=U(k.id)*0x9e3779b97f4a7c15ULL^U(k.p)*0xbf58476d1ce4e5b9ULL^U(k.tab)*0x94d049bb133111ebULL^U(k.a);x^=x>>30;x*=0xbf58476d1ce4e5b9ULL;x^=x>>27;return x;}};
struct Blocks{
 int q,cap,lev,off,root,base;Tape tape;std::array<int,6>T;std::array<U,7>power{};std::array<U,5>cnt{},leaves{};U branches=0,calls=0,hits=0;
 std::unordered_map<Key,Result,Hash>cache;
 Blocks(int q0,int c,const std::vector<uint8_t>&S):q(q0),cap(c),lev(0),off(c+2),base(9*(q+1)+1){
  while((1<<lev)<=off+int(S.size())+c+n+2)lev++;
  root=tape.uniform(2,lev);root=tape.range(root,lev,off,off+S.size(),0);
  for(int i=0;i<int(S.size());i++)if(S[i])root=tape.put(root,lev,off+i,S[i]);
  T.fill(-1);power[0]=1;for(int i=1;i<=3*q;i++)power[i]=power[i-1]*(base-1);
  cache.reserve(262144);
 }
 bool closed(int a){int r=1<<a;for(int i=0;i<q;i++)for(int s=0;s<q;s++)if(r>>s&1)for(int b=0;b<3;b++){int v=T[3*s+b];if(v<0||tr(v).a==q)return false;r|=1<<tr(v).a;}return true;}
 Result leaf(int id,int a){
  int t=0,p=0,seen=0;
  while(t<cap){int k=3*a+id,v=T[k];if(v<0)return{id,p,a,t,UNKNOWN};if(seen>>k&1)return{id,p,a,t,LOOP};
   seen|=1<<k;auto b=tr(v);id=b.w;p=b.m;a=b.a;t++;
   if(a==q)return{id,p,a,t,HALT};
   if(p)return{id,p,a,t,EXIT};
  }return{id,p,a,t,TIME};
 }
 Result macro(int id,int l,int p,int a,int tab){
  ++calls;if(!l)return leaf(id,a);
  Key key{id,p,a,tab};auto it=cache.find(key);if(it!=cache.end()){++hits;return it->second;}
  int t=0,sz=1<<l,half=sz/2,kind=EXIT,ckid=id,ckp=p,cka=a,ckt=0,span=1;
  while(p>=0&&p<sz){
   auto v=tape.V[id];bool r=p>=half;auto z=macro(r?v.b:v.a,l-1,p-(r?half:0),a,tab);
   if(z.t>cap-t||z.kind==TIME){kind=TIME;t=cap;break;}
   t+=z.t;if(r)v.b=z.id;else v.a=z.id;id=tape.node(v.a,v.b);p=z.p+(r?half:0);a=z.a;kind=z.kind;
   if(kind==HALT||kind==UNKNOWN||kind==LOOP)break;
   if(t==cap){kind=TIME;break;}
   if(id==ckid&&p==ckp&&a==cka){kind=LOOP;break;}
   if(t-ckt>=span){ckid=id;ckp=p;cka=a;ckt=t;span=std::min(span*2,cap+1);}
  }
  Result z{id,p,a,t,kind};if(cache.size()<600000)cache.emplace(key,z);return z;
 }
 void leafcount(int k,int u){cnt[k]+=power[u];leaves[k]++;}
 void visit(int id,int p,int a,int t,int u,int tab){
  if(closed(a)){leafcount(2,u);return;}
  if(cache.size()>=600000)cache.clear();
  auto z=macro(id,lev,p,a,tab);
  if(z.kind==TIME||z.t>cap-t||(z.t==cap-t&&z.kind!=HALT)){leafcount(4,u);return;}
  if(z.kind==LOOP){leafcount(2,u);return;}t+=z.t;
  if(z.kind==HALT){
   W w=0;bool ok=true;for(int i=0;i<n;i++){int b=tape.get(z.id,lev,z.p+i);if(b==2){ok=false;break;}w|=W(b)<<i;}
   leafcount(!ok?0:((w&((W(1)<<91)-1))==pin?3:1),u);return;
  }
  req(z.kind==UNKNOWN,"unexpected root exit");
  int k=3*z.a+tape.get(z.id,lev,z.p);req(T[k]<0,"assigned unknown");
  int weight=1;for(int i=0;i<k;i++)weight*=base;
  branches++;
  for(int v=0;v<base-1;v++){T[k]=v;visit(z.id,z.p,z.a,t,u-1,tab+(v+1)*weight);}
  T[k]=-1;
 }
 void run(){visit(root,off,0,0,3*q,0);U sum=0;for(auto x:cnt)sum+=x;req(sum==power[3*q],"block coverage");}
 void report(){std::cout<<'[';print(cnt);std::cout<<',';print(leaves);std::cout<<','<<branches<<','<<calls<<','<<hits<<','<<tape.V.size()<<']';}
};
int main(int argc,char**argv){
 auto S=input();std::string parent;req(bool(std::cin>>parent)&&parent.size()==S.size(),"missing parent tape");
 for(size_t i=0;i<S.size();i++)req(parent[i]=='0'+S[i],"parent tape mismatch");
 if(argc==2&&std::string(argv[1])=="full"){Blocks A(2,full,S);A.run();A.report();std::cout<<'\n';return 0;}
 req(argc==1,"use default partial audit or full");
 auto P=S;P.resize(2*n+1);
 Scalar one(1,32768,P);one.run();
 Scalar short2(2,512,S);short2.run();
 Scalar long2(2,4096,S);long2.run();
 Blocks block2(2,512,S);block2.run();
 req(one.cnt[5]==0&&one.cnt[6]==0,"unresolved one-state");
 req(short2.cnt[0]==block2.cnt[0]&&short2.cnt[1]==block2.cnt[1]&&short2.cnt[6]==block2.cnt[3],"different halt census");
 req(long2.cnt[6]==0&&long2.cnt[5]>0,"partial result changed");
 std::cout<<"{\"one\":";one.report();
 std::cout<<",\"scalar512\":";short2.report();
 std::cout<<",\"scalar4096\":";long2.report();
 std::cout<<",\"block512\":";block2.report();std::cout<<"}\n";
}
