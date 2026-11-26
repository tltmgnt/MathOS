#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using U = std::uint64_t;
constexpr int n=52, L=182261, cap2=4096, limit=2000000;
constexpr U pin=0x123456789abcdULL, mask=(1ULL<<50)-1, cap1=1ULL<<34;
void require(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
struct Tr{int a,w,m;};
Tr tr(int v){return {v/9,v/3%3,v%3-1};}
struct Two {
 static constexpr int off=cap2+5, size=2*cap2+n+12;
 std::array<int,size> A{}; std::array<int,6> T{};
 std::vector<std::pair<int,int>> undo;
 U leaves=0,covered=0,steps=0,halts=0,well=0,branches=0;
 std::set<U> outputs; std::array<U,7> powers{};
 void visit(int state,int h,int elapsed,int unknown){
  const auto root=undo.size();
  if(unknown==0&&std::all_of(T.begin(),T.end(),[](int a){return a<18;})){++leaves;++covered;return;}
  while(elapsed<cap2){
   int k=3*state+A.at(h),a=T.at(k);
   if(a<0){++branches;for(int v=0;v<27;v++){T[k]=v;visit(state,h,elapsed,unknown-1);}T[k]=-1;while(undo.size()>root){auto [i,v]=undo.back();undo.pop_back();A[i]=v;}return;}
   auto u=tr(a);if(A[h]!=u.w){undo.emplace_back(h,A[h]);A[h]=u.w;}
   h+=u.m;++elapsed;++steps;
   if(u.a==2){++halts;U x=0;bool ok=true;for(int j=0;j<n;j++){int v=A.at(h+j);if(v==2){ok=false;break;}x|=U(v)<<j;}if(ok){++well;outputs.insert(x&mask);}break;}
   state=u.a;
  }
  ++leaves;covered+=powers.at(unknown);
  while(undo.size()>root){auto [i,v]=undo.back();undo.pop_back();A[i]=v;}
 }
 void run(){powers[0]=1;for(int i=1;i<=6;i++)powers[i]=27*powers[i-1];A.fill(2);std::fill(A.begin()+off,A.begin()+off+n,1);std::fill(A.begin()+off+n,A.end(),0);T.fill(-1);visit(0,off,0,6);require(covered==powers[6]&&!outputs.count(pin),"two-state coverage or pin failure");std::cout<<"\"two\":["<<leaves<<','<<covered<<','<<steps<<','<<halts<<','<<well<<','<<outputs.size()<<','<<branches<<']';}
};
std::vector<int> input(){std::vector<int>S(n,1);S.push_back(0);for(int i=1;i<=n;i++)for(int b=0;b<2;b++)S.push_back(0);for(int i=1;i<=n;i++)for(int j=i+1;j<=n;j++)for(int b=0;b<4;b++)S.push_back(0);for(int i=1;i<=n;i++)for(int j=i+1;j<=n;j++)for(int k=j+1;k<=n;k++)for(int b=0;b<8;b++)S.push_back(j==51&&k==52&&i<=50&&((b>>2)&1)==((pin>>(i-1))&1));require(S.size()==L&&std::count(S.begin()+n+1,S.end(),1)==200,"input geometry");return S;}
void one(){
 auto S=input();std::array<U,6> counts{};std::set<U> outputs;U steps=0;const int off=2*limit+5;std::vector<int> V(L+4*limit+2*n+12,2);std::vector<U> salts(V.size());U z=0xabcdef;for(auto &v:salts){z^=z<<13;z^=z>>7;z^=z<<17;v=z;}
 for(int d=0;d<5832;d++){
  int k=d;Tr T[3];bool halt=false;for(auto &t:T){t=tr(k%18);k/=18;halt|=t.a!=0;}
  if(!halt){++counts[0];continue;}
  // Exact left-growing invariant: 1 moves left, blank writes 1 and moves right,
  // then two left moves encounter the next new blank; zero is never read.
  if(T[0].a==1&&T[1].a==0&&T[1].w==1&&T[1].m==-1&&T[2].a==0&&T[2].w==1&&T[2].m==1){++counts[5];continue;}
  std::fill(V.begin(),V.end(),2);std::copy(S.begin(),S.end(),V.begin()+off);
  int h=off,lo=off,hi=off+L-1;U hash=0;std::unordered_map<U,int> seen;int i=0;
  for(;i<limit;i++){
   int sym=V.at(h);auto t=T[sym];
   if(h<lo||h>hi){int dir=h<lo?-1:1;int u=2;bool escape=false;for(int j=0;j<3;j++){auto a=T[u];if(a.a)break;if(a.m==dir){escape=true;break;}if(a.m)break;u=a.w;}if(escape){++counts[1];break;}lo=std::min(lo,h);hi=std::max(hi,h);}
   if(t.a){V[h]=t.w;h+=t.m;U x=0;bool ok=true;for(int j=0;j<n;j++){int v=V.at(h+j);if(v==2){ok=false;break;}x|=U(v)<<j;}++counts[ok?2:3];if(ok){outputs.insert(x&mask);require((x&mask)!=pin,"one-state witness found");}break;}
   U key=hash^(salts.at(h)*0x9e3779b97f4a7c15ULL);auto it=seen.find(key);
   if(it!=seen.end()){
    int p=i-it->second,hh=h;bool stop=false;std::vector<std::pair<int,int>> undo;
    // Hashes only suggest a period. Replay and compare every changed cell exactly.
    for(int j=0;j<p;j++){auto u=T[V.at(hh)];if(u.a){stop=true;break;}undo.emplace_back(hh,V[hh]);V[hh]=u.w;hh+=u.m;}
    bool equal=!stop&&hh==h;std::unordered_map<int,int> first;for(auto [pos,v]:undo)first.emplace(pos,v);for(auto [pos,v]:first)if(V[pos]!=v)equal=false;for(auto j=undo.rbegin();j!=undo.rend();++j)V[j->first]=j->second;
    if(equal){++counts[4];break;}
   }
   seen[key]=i;hash^=salts.at(h)*U(V[h]+1);V[h]=t.w;hash^=salts.at(h)*U(V[h]+1);h+=t.m;
  }
  require(i<limit&&U(i+1)<=cap1,"unresolved one-state run");steps+=i;
 }
 U total=0;for(auto v:counts)total+=v;require(total==5832&&!outputs.count(pin),"one-state coverage");std::cout<<",\"one\":[";for(auto v:counts)std::cout<<v<<',';std::cout<<outputs.size()<<','<<steps<<']';
}
int main(){require(cap2+n<5409&&pin<=mask&&cap1==(1ULL<<(54-20)),"clock");std::string parent;require(bool(std::cin>>parent),"missing actual parent input");auto S=input();require(parent.size()==S.size(),"parent length");for(std::size_t i=0;i<S.size();i++)require(parent[i]=='0'+S[i],"parent input mismatch");std::cout<<'{';Two{}.run();one();std::cout<<"}\n";}
