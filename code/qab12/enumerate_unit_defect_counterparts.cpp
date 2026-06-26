#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_set>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif
struct PrimeExp{uint32_t p,a;};
struct Core{uint32_t d,r,t,e,n_limit,defect_rad;};
struct Record{uint32_t d,r,t,e,a,b,n,defect_rad;bool operator<(const Record&o)const{return std::tie(d,r,t,e,n,a,b,defect_rad)<std::tie(o.d,o.r,o.t,o.e,o.n,o.a,o.b,o.defect_rad);}bool operator==(const Record&o)const{return d==o.d&&r==o.r&&t==o.t&&e==o.e&&a==o.a&&b==o.b&&n==o.n&&defect_rad==o.defect_rad;}};
static std::vector<PrimeExp> factorization(uint32_t x){std::vector<PrimeExp>o;if(x%2==0){uint32_t a=0;do{x/=2;++a;}while(x%2==0);o.push_back({2,a});}for(uint32_t p=3;(uint64_t)p*p<=x;p+=2)if(x%p==0){uint32_t a=0;do{x/=p;++a;}while(x%p==0);o.push_back({p,a});}if(x>1)o.push_back({x,1});return o;}
static uint32_t valuation(uint32_t x,uint32_t p){uint32_t a=0;while(x%p==0){x/=p;++a;}return a;}
static std::vector<uint32_t> support(uint32_t x){std::vector<uint32_t>o;for(auto z:factorization(x))o.push_back(z.p);return o;}
static void gen(const std::vector<uint32_t>&p,size_t i,uint64_t x,uint32_t L,std::vector<uint32_t>&o){if(i==p.size()){o.push_back((uint32_t)x);return;}while(x<=L){gen(p,i+1,x,L,o);if(x>L/p[i])break;x*=p[i];}}
static std::set<uint32_t> read_degrees(const std::string&path){std::ifstream f(path);if(!f)throw std::runtime_error("cannot open degree source");std::string line;std::getline(f,line);if(!line.empty()&&line.back()=='\r')line.pop_back();if(line!="d,r,t,e,a,b,n,defect_rad")throw std::runtime_error("bad degree-source header");std::set<uint32_t>D;while(std::getline(f,line))if(!line.empty()){std::stringstream ss(line);std::string x;std::getline(ss,x,',');D.insert(std::stoul(x));}return D;}
int main(int argc,char**argv){std::string degree_source,output;uint32_t Dmax=2666019,rmax=139;int threads=25;for(int i=1;i<argc;++i){std::string a=argv[i];if(a=="--degree-source"&&i+1<argc)degree_source=argv[++i];else if(a=="--output"&&i+1<argc)output=argv[++i];else if(a=="--D-max"&&i+1<argc)Dmax=std::stoul(argv[++i]);else if(a=="--r-max"&&i+1<argc)rmax=std::stoul(argv[++i]);else if(a=="--threads"&&i+1<argc)threads=std::stoi(argv[++i]);else throw std::runtime_error("bad command line");}if(degree_source.empty()||output.empty())throw std::runtime_error("missing path");
#ifdef _OPENMP
omp_set_num_threads(threads);int nt=omp_get_max_threads();
#else
(void)threads;int nt=1;
#endif
    auto degrees=read_degrees(degree_source);std::map<uint32_t,std::vector<Core>> by_e;uint64_t core_count=0;
    for(uint32_t d:degrees)for(uint32_t t=1;t<=std::min<uint32_t>(rmax,d);++t)if(d%t==0){uint32_t e=d/t;if(e<2)continue;for(uint32_t r=t;r<=rmax;++r){uint32_t defect_rad=1;bool ok=true;for(auto z:factorization(r))if(valuation(t,z.p)<z.a){if(e>z.p-2){ok=false;break;}defect_rad*=z.p;}if(!ok)continue;uint32_t nlim=std::min<uint32_t>(Dmax/r,(uint32_t)(((uint64_t)140*d-1)/r));if(nlim<e+4||nlim<d+2)continue;by_e[e].push_back({d,r,t,e,nlim,defect_rad});++core_count;}}
    std::vector<std::pair<uint32_t,std::vector<Core>>> tasks;for(auto&kv:by_e)tasks.push_back(kv);std::vector<std::vector<Record>>local((size_t)nt);std::vector<uint64_t>smooth(nt),pairs(nt),triples(nt),tests(nt),kept(nt);auto begin=std::chrono::steady_clock::now();
#pragma omp parallel for schedule(dynamic,1)
    for(int64_t ii=0;ii<(int64_t)tasks.size();++ii){int tid=0;
#ifdef _OPENMP
        tid=omp_get_thread_num();
#endif
        uint32_t e=tasks[(size_t)ii].first;auto&cores=tasks[(size_t)ii].second;uint32_t nmax=0;for(auto&c:cores)nmax=std::max(nmax,c.n_limit);auto ps=support(e);auto q=support(e+2);ps.insert(ps.end(),q.begin(),q.end());std::sort(ps.begin(),ps.end());ps.erase(std::unique(ps.begin(),ps.end()),ps.end());std::vector<uint32_t>vals;gen(ps,0,1,nmax,vals);std::sort(vals.begin(),vals.end());vals.erase(std::unique(vals.begin(),vals.end()),vals.end());smooth[tid]+=vals.size();std::unordered_set<uint32_t>M(vals.begin(),vals.end());
        for(size_t i=0;i<vals.size();++i){uint32_t a=vals[i];for(size_t j=i+1;j<vals.size();++j){uint32_t b=vals[j];if((uint64_t)a+b>nmax)break;++pairs[tid];if(std::gcd(a,b)!=1)continue;uint32_t n=a+b;if(!M.count(n)||n<e+4)continue;++triples[tid];for(const Core&c:cores){if(n>c.n_limit||n<c.d+2)continue;++tests[tid];if(c.defect_rad>1&&((uint64_t)a*b*n)%c.defect_rad==0)continue;++kept[tid];local[tid].push_back({c.d,c.r,c.t,e,a,b,n,c.defect_rad});}}}
    }
    std::vector<Record>records;for(auto&v:local)records.insert(records.end(),v.begin(),v.end());std::sort(records.begin(),records.end());records.erase(std::unique(records.begin(),records.end()),records.end());std::ofstream out(output);out<<"d,r,t,e,a,b,n,defect_rad\n";for(auto&z:records)out<<z.d<<','<<z.r<<','<<z.t<<','<<z.e<<','<<z.a<<','<<z.b<<','<<z.n<<','<<z.defect_rad<<'\n';uint64_t sc=0,pa=0,tr=0,te=0,ke=0;for(int i=0;i<nt;++i){sc+=smooth[i];pa+=pairs[i];tr+=triples[i];te+=tests[i];ke+=kept[i];}std::cout<<"common_degrees="<<degrees.size()<<" unique_factor_degrees="<<tasks.size()<<" cores="<<core_count<<" smooth_entries="<<sc<<" pair_tests="<<pa<<" additive_triples="<<tr<<" state_tests="<<te<<" raw_records="<<ke<<" unique_records="<<records.size()<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count()<<"\n";
}
