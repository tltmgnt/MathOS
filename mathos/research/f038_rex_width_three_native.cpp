// REX-024D5A: independent memory-bounded original descriptor interpreter.
// No JS table, phase metadata, or witness hints enter the transition loop.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
static void require(bool b,const char* s){if(!b)throw runtime_error(s);}
struct Reader{
 FILE* f; vector<unsigned char> buf; size_t i=0,n=0; uint64_t bits=0;
 explicit Reader(const char* p):f(fopen(p,"rb")),buf(1<<20){require(f!=nullptr,"descriptor open");}
 ~Reader(){fclose(f);}
 int get(){if(i==n){n=fread(buf.data(),1,buf.size(),f);i=0;if(!n){require(!ferror(f),"read error");return -1;}}++bits;return buf[i++];}
 uint32_t field(unsigned w){uint32_t v=0;while(w--){int c=get();require(c=='0'||c=='1',"nonbinary/truncated field");v=(v<<1)|(c-'0');}return v;}
};
struct Machine{uint32_t q;uint64_t bits;vector<uint32_t> T;};
Machine decode(const char* p){
 Reader r(p);require(r.field(3)==7,"prefix");
 uint32_t q=0;int c;while((c=r.get())=='1'){require(q<0x0ffffffd,"packed state capacity");++q;}
 require(c=='0'&&q>0,"unary state count");unsigned b=0;for(uint32_t x=q;x;x>>=1)++b;
 Machine M{q,0,vector<uint32_t>(size_t(3)*q)};
 for(auto& v:M.T){uint32_t s=r.field(b),w=r.field(2),d=r.field(2);require(s<=q&&w<=2&&d<=2,"rule range");v=(s<<4)|(w<<2)|d;}
 require(r.get()==-1,"trailing descriptor");M.bits=r.bits;require(M.bits==4ull+q+3ull*q*(b+4),"descriptor length");return M;
}
struct Result{uint64_t t;int64_t head,span;bool halt;string word;unsigned headSymbol,nextSymbol;};
// Growable two-sided tape. The origin and span are observation only.
Result run(const Machine& M,const string& raw,unsigned n,uint64_t limit){
 vector<uint8_t> tape(2*raw.size()+2048,2);int64_t base=-1024,h=0,lo=0,hi=0;
 for(size_t i=0;i<raw.size();++i){require(raw[i]=='0'||raw[i]=='1',"raw alphabet");tape[1024+i]=raw[i]-'0';}
 uint32_t s=0;uint64_t t=0;const uint32_t* T=M.T.data();
 // Bounds checks only concern physical representation, never state dispatch.
 while(s!=M.q&&t<limit){
  auto i=size_t(h-base);uint32_t v=T[3ull*s+tape[i]];
  tape[i]=(v>>2)&3;h+=int(v&3)-1;s=v>>4;++t;
  if(h<base){size_t old=tape.size();vector<uint8_t> a(2*old,2);copy(tape.begin(),tape.end(),a.begin()+old);base-=int64_t(old);tape.swap(a);}
  else if(h-base>=int64_t(tape.size()))tape.resize(2*tape.size(),2);
  if(h<lo)lo=h;if(h>hi)hi=h;
 }
 auto cell=[&](int64_t j)->unsigned{return j<base||j-base>=int64_t(tape.size())?2:tape[size_t(j-base)];};
 string word="-";
 if(s==M.q){string a;for(unsigned j=0;j<n;++j){auto b=cell(h+j);if(b==2){a.clear();break;}a.push_back(char('0'+b));}if(a.size()==n)word=move(a);}
 return{t,h,hi-lo+1,s==M.q,word,cell(h),cell(h+n)};
}
int main(int argc,char** argv){
 try{
  require(argc==3||argc==4,"usage: native descriptor fixtures [case]");auto M=decode(argv[1]);
  cout<<"CODEC "<<M.q<<" "<<M.bits<<" "<<M.T.size()<<endl;
  ifstream f(argv[2]);require(bool(f),"fixture open");string name,raw,expected,head,span;unsigned n;uint64_t budget;
  unsigned count=0;
  while(f>>name>>n>>budget>>raw>>expected>>head>>span){
   if(argc==4&&name!=argv[3])continue;
   require(n>0,"n");auto r=run(M,raw,n,budget);
   require(r.halt&&r.word==expected,"halt witness mismatch");
   if(head!="-"){require(r.t==budget&&r.head==stoll(head)&&r.span==stoll(span),"exact inherited clock/head/span");}
   if(expected=="-")require(r.headSymbol==2,"blank halt");else require(r.nextSymbol==2,"output delimiter");
   // Replay one step short with the same immutable table.
   auto shortRun=run(M,raw,n,r.t-1);require(!shortRun.halt&&shortRun.t==r.t-1&&shortRun.word=="-","one-step-short cutoff");
   cout<<"RUN "<<name<<" "<<r.t<<" "<<r.head<<" "<<r.span<<" "<<r.word<<" "<<r.headSymbol<<" "<<r.nextSymbol<<endl;++count;
  }
  require(f.eof()&&count>0,"fixture parse/selection");
  return 0;
 }catch(const exception& e){cerr<<e.what()<<endl;return 1;}
}
