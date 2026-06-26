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

struct Record {
    uint32_t d,r,e,a,b,n;
    bool operator<(const Record& o) const {
        return std::tie(d,r,e,n,a,b)<std::tie(o.d,o.r,o.e,o.n,o.a,o.b);
    }
    bool operator==(const Record& o) const {
        return d==o.d&&r==o.r&&e==o.e&&a==o.a&&b==o.b&&n==o.n;
    }
};

static std::vector<uint32_t> support(uint32_t x){
    std::vector<uint32_t> out;
    if(x%2==0){out.push_back(2);while(x%2==0)x/=2;}
    for(uint32_t p=3;(uint64_t)p*p<=x;p+=2){
        if(x%p==0){out.push_back(p);while(x%p==0)x/=p;}
    }
    if(x>1)out.push_back(x);
    return out;
}
static void generate_smooth(const std::vector<uint32_t>& primes,size_t i,
                            uint64_t cur,uint32_t limit,std::vector<uint32_t>& out){
    if(i==primes.size()){out.push_back((uint32_t)cur);return;}
    while(cur<=limit){
        generate_smooth(primes,i+1,cur,limit,out);
        if(cur>limit/primes[i])break;
        cur*=primes[i];
    }
}

int main(int argc,char**argv){
    uint32_t e_start=2,e_end=5428,D_min=1,D_max=49999,r_max=139;
    int threads=25; std::string output;
    for(int i=1;i<argc;++i){
        std::string a=argv[i];
        if(a=="--e-start"&&i+1<argc)e_start=std::stoul(argv[++i]);
        else if(a=="--e-end"&&i+1<argc)e_end=std::stoul(argv[++i]);
        else if(a=="--D-min"&&i+1<argc)D_min=std::stoul(argv[++i]);
        else if(a=="--D-max"&&i+1<argc)D_max=std::stoul(argv[++i]);
        else if(a=="--r-max"&&i+1<argc)r_max=std::stoul(argv[++i]);
        else if(a=="--threads"&&i+1<argc)threads=std::stoi(argv[++i]);
        else if(a=="--output"&&i+1<argc)output=argv[++i];
        else throw std::runtime_error("bad command line");
    }
    if(output.empty()||e_start<2||e_start>e_end||D_min>D_max||r_max<1||r_max>139)
        throw std::runtime_error("invalid domain");
#ifdef _OPENMP
    omp_set_num_threads(threads);
    int nt=omp_get_max_threads();
#else
    (void)threads; int nt=1;
#endif
    std::vector<std::vector<Record>> local((size_t)nt);
    std::vector<uint64_t> smooth_count(nt),pair_tests(nt),triple_count(nt),raw_records(nt);
    auto begin=std::chrono::steady_clock::now();
#pragma omp parallel for schedule(dynamic,1)
    for(int64_t ee=e_start;ee<=(int64_t)e_end;++ee){
        int tid=0;
#ifdef _OPENMP
        tid=omp_get_thread_num();
#endif
        const uint32_t e=(uint32_t)ee;
        // D<140d and d=r e imply n<140e, independent of r.
        const uint32_t n_limit=std::min<uint32_t>(D_max,140*e-1);
        auto primes=support(e); auto q=support(e+2);
        primes.insert(primes.end(),q.begin(),q.end());
        std::sort(primes.begin(),primes.end());
        primes.erase(std::unique(primes.begin(),primes.end()),primes.end());
        std::vector<uint32_t> vals;
        generate_smooth(primes,0,1,n_limit,vals);
        std::sort(vals.begin(),vals.end());
        vals.erase(std::unique(vals.begin(),vals.end()),vals.end());
        smooth_count[tid]+=vals.size();
        std::unordered_set<uint32_t> membership(vals.begin(),vals.end());
        for(size_t i=0;i<vals.size();++i){
            uint32_t a=vals[i];
            for(size_t j=i+1;j<vals.size();++j){
                uint32_t b=vals[j];
                if((uint64_t)a+b>n_limit)break;
                ++pair_tests[tid];
                if(std::gcd(a,b)!=1)continue;
                uint32_t n=a+b;
                if(!membership.count(n)||n<e+4)continue; // proper primitive factor
                ++triple_count[tid];
                uint32_t max_r=std::min<uint32_t>(r_max,5428/e);
                for(uint32_t r=1;r<=max_r;++r){
                    uint32_t d=r*e;
                    uint64_t D=(uint64_t)r*n;
                    if(D<D_min||D>D_max)continue;
                    if(n<d+2)continue; // confluent Schinzel degree bound
                    ++raw_records[tid];
                    local[tid].push_back({d,r,e,a,b,n});
                }
            }
        }
    }
    std::vector<Record> records;
    for(auto& v:local)records.insert(records.end(),v.begin(),v.end());
    std::sort(records.begin(),records.end());
    records.erase(std::unique(records.begin(),records.end()),records.end());
    std::ofstream out(output);
    if(!out)throw std::runtime_error("cannot open output");
    out<<"d,r,e,a,b,n\n";
    for(const auto& z:records)out<<z.d<<','<<z.r<<','<<z.e<<','<<z.a<<','<<z.b<<','<<z.n<<'\n';
    uint64_t sc=0,pt=0,tc=0,rr=0;
    for(int i=0;i<nt;++i){sc+=smooth_count[i];pt+=pair_tests[i];tc+=triple_count[i];rr+=raw_records[i];}
    std::cout<<"smooth_entries="<<sc
             <<" pair_tests="<<pt
             <<" additive_triples="<<tc
             <<" raw_records="<<rr
             <<" unique_records="<<records.size()
             <<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count()<<"\n";
}
