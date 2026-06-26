#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_set>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

struct PrimeExp{uint32_t p,a;};
struct Core{uint32_t r,t,d,n_limit,defect_rad;};
struct Record{
    uint32_t d,r,t,e,a,b,n,defect_rad;
    bool operator<(const Record&o)const{return std::tie(d,r,t,e,n,a,b,defect_rad)<std::tie(o.d,o.r,o.t,o.e,o.n,o.a,o.b,o.defect_rad);}
    bool operator==(const Record&o)const{return d==o.d&&r==o.r&&t==o.t&&e==o.e&&a==o.a&&b==o.b&&n==o.n&&defect_rad==o.defect_rad;}
};
static std::vector<PrimeExp> factorization(uint32_t x){
    std::vector<PrimeExp>o;if(x%2==0){uint32_t a=0;do{x/=2;++a;}while(x%2==0);o.push_back({2,a});}
    for(uint32_t p=3;(uint64_t)p*p<=x;p+=2)if(x%p==0){uint32_t a=0;do{x/=p;++a;}while(x%p==0);o.push_back({p,a});}
    if(x>1)o.push_back({x,1});return o;
}
static uint32_t valuation(uint32_t x,uint32_t p){uint32_t a=0;while(x%p==0){x/=p;++a;}return a;}
static std::vector<uint32_t> support(uint32_t x){std::vector<uint32_t>o;for(auto z:factorization(x))o.push_back(z.p);return o;}
static void generate_smooth(const std::vector<uint32_t>&p,size_t i,uint64_t x,uint32_t L,std::vector<uint32_t>&o){
    if(i==p.size()){o.push_back((uint32_t)x);return;}while(x<=L){generate_smooth(p,i+1,x,L,o);if(x>L/p[i])break;x*=p[i];}
}
int main(int argc,char**argv){
    uint32_t e_start=2,e_end=19043,D_max=2666019,r_max=139,d_max=19043;int threads=25;std::string output;
    for(int i=1;i<argc;++i){std::string a=argv[i];
        if(a=="--e-start"&&i+1<argc)e_start=std::stoul(argv[++i]);
        else if(a=="--e-end"&&i+1<argc)e_end=std::stoul(argv[++i]);
        else if(a=="--D-max"&&i+1<argc)D_max=std::stoul(argv[++i]);
        else if(a=="--r-max"&&i+1<argc)r_max=std::stoul(argv[++i]);
        else if(a=="--d-max"&&i+1<argc)d_max=std::stoul(argv[++i]);
        else if(a=="--threads"&&i+1<argc)threads=std::stoi(argv[++i]);
        else if(a=="--output"&&i+1<argc)output=argv[++i];
        else throw std::runtime_error("bad command line");}
    if(output.empty()||e_start<2||e_start>e_end||r_max<1||r_max>139)throw std::runtime_error("invalid domain");
#ifdef _OPENMP
    omp_set_num_threads(threads);int nt=omp_get_max_threads();
#else
    (void)threads;int nt=1;
#endif
    std::vector<std::vector<Record>> local((size_t)nt);
    std::vector<uint64_t> smooth_count(nt),pair_tests(nt),triple_count(nt),core_tests(nt),raw_count(nt);
    auto begin=std::chrono::steady_clock::now();
#pragma omp parallel for schedule(dynamic,1)
    for(int64_t ee=e_start;ee<=(int64_t)e_end;++ee){
        int tid=0;
#ifdef _OPENMP
        tid=omp_get_thread_num();
#endif
        uint32_t e=(uint32_t)ee;std::vector<Core> cores;uint32_t n_limit_max=0;
        for(uint32_t r=1;r<=r_max;++r){auto rf=factorization(r);
            for(uint32_t t=1;t<=r;++t){uint64_t d64=(uint64_t)t*e;if(d64>d_max)continue;uint32_t defect_rad=1;bool ok=true;
                for(auto z:rf)if(valuation(t,z.p)<z.a){if(e>z.p-2){ok=false;break;}defect_rad*=z.p;}
                if(!ok)continue;uint32_t d=(uint32_t)d64;
                uint32_t nlim=std::min<uint32_t>(D_max/r,(uint32_t)(((uint64_t)140*d-1)/r));
                if(nlim<e+4||nlim<d+2)continue;cores.push_back({r,t,d,nlim,defect_rad});n_limit_max=std::max(n_limit_max,nlim);
            }
        }
        if(cores.empty())continue;
        auto primes=support(e);auto q=support(e+2);primes.insert(primes.end(),q.begin(),q.end());std::sort(primes.begin(),primes.end());primes.erase(std::unique(primes.begin(),primes.end()),primes.end());
        std::vector<uint32_t> vals;generate_smooth(primes,0,1,n_limit_max,vals);std::sort(vals.begin(),vals.end());vals.erase(std::unique(vals.begin(),vals.end()),vals.end());smooth_count[tid]+=vals.size();std::unordered_set<uint32_t>M(vals.begin(),vals.end());
        for(size_t i=0;i<vals.size();++i){uint32_t a=vals[i];for(size_t j=i+1;j<vals.size();++j){uint32_t b=vals[j];if((uint64_t)a+b>n_limit_max)break;++pair_tests[tid];if(std::gcd(a,b)!=1)continue;uint32_t n=a+b;if(!M.count(n)||n<e+4)continue;++triple_count[tid];
            for(const Core&c:cores){if(n>c.n_limit||n<c.d+2)continue;++core_tests[tid];if(c.defect_rad>1&&((uint64_t)a*b*n)%c.defect_rad==0)continue;++raw_count[tid];local[tid].push_back({c.d,c.r,c.t,e,a,b,n,c.defect_rad});}
        }}
    }
    std::vector<Record> records;for(auto&v:local)records.insert(records.end(),v.begin(),v.end());std::sort(records.begin(),records.end());records.erase(std::unique(records.begin(),records.end()),records.end());
    std::ofstream out(output);if(!out)throw std::runtime_error("cannot open output");out<<"d,r,t,e,a,b,n,defect_rad\n";for(auto&z:records)out<<z.d<<','<<z.r<<','<<z.t<<','<<z.e<<','<<z.a<<','<<z.b<<','<<z.n<<','<<z.defect_rad<<'\n';
    uint64_t sc=0,pt=0,tc=0,ct=0,rc=0;for(int i=0;i<nt;++i){sc+=smooth_count[i];pt+=pair_tests[i];tc+=triple_count[i];ct+=core_tests[i];rc+=raw_count[i];}
    std::cout<<"smooth_entries="<<sc<<" pair_tests="<<pt<<" additive_triples="<<tc<<" core_tests="<<ct<<" raw_records="<<rc<<" unique_records="<<records.size()<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count()<<"\n";
}
