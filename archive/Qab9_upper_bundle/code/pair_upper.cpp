#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

constexpr uint32_t DMAX = 175394637u;
constexpr uint32_t DUNIT = 6816242u;
constexpr uint32_t SCALE_MAX = 139u;
// A deliberately conservative, entirely integer support cap.  Section 18
// of Qab9 proves rad(A B (A+B))*scale < 4,398,937 in the unit range.
constexpr uint64_t SUPPORT_PRODUCT_CAP = 4398937ull;

struct Shape {
    uint32_t a, b, n;
    uint32_t rad_a, rad_b, rad_n, rad_product;
    uint32_t support5;
    std::vector<uint32_t> total_primes;
    std::vector<uint32_t> all_primes;
};

struct Survivor {
    uint32_t i, j;
    uint16_t r, s;
    uint32_t D;
    uint32_t k_lo, k_hi;
    bool operator<(const Survivor& o) const {
        return std::tie(D,r,s,i,j,k_lo,k_hi) < std::tie(o.D,o.r,o.s,o.i,o.j,o.k_lo,o.k_hi);
    }
};

static uint64_t parse_u64(const char* s) {
    char* e = nullptr;
    unsigned long long v = std::strtoull(s, &e, 10);
    if (!e || *e) throw std::runtime_error(std::string("invalid integer: ") + s);
    return static_cast<uint64_t>(v);
}

static std::vector<uint32_t> factor_squarefree(uint32_t x) {
    std::vector<uint32_t> out;
    if ((x & 1u) == 0) { out.push_back(2); while ((x & 1u) == 0) x >>= 1; }
    for (uint32_t p = 3; static_cast<uint64_t>(p) * p <= x; p += 2) {
        if (x % p == 0) {
            out.push_back(p);
            while (x % p == 0) x /= p;
        }
    }
    if (x > 1) out.push_back(x);
    return out;
}

static uint32_t support_ge5(uint32_t squarefree) {
    if (squarefree % 2 == 0) squarefree /= 2;
    if (squarefree % 3 == 0) squarefree /= 3;
    return squarefree;
}

static std::vector<Shape> read_shapes(const std::string& path) {
    std::ifstream f(path);
    if (!f) throw std::runtime_error("cannot open shape CSV: " + path);
    std::string line;
    std::getline(f, line); // header
    std::vector<Shape> shapes;
    while (std::getline(f, line)) {
        if (line.empty()) continue;
        std::replace(line.begin(), line.end(), ',', ' ');
        std::istringstream in(line);
        Shape sh{};
        in >> sh.a >> sh.b >> sh.n >> sh.rad_a >> sh.rad_b >> sh.rad_n >> sh.rad_product;
        if (!in) throw std::runtime_error("malformed CSV row: " + line);
        sh.support5 = support_ge5(sh.rad_product);
        sh.total_primes = factor_squarefree(sh.rad_n);
        sh.all_primes = factor_squarefree(sh.rad_product);
        shapes.push_back(std::move(sh));
    }
    return shapes;
}

static uint32_t degree_lower(uint32_t D) {
    // The exact algebraic certificate theta_0^70 > 2*DMAX gives
    // log(theta_0)/(2 log(2D)) > 1/140 for every D <= DMAX.
    // Therefore d > D/140.
    return D / 140u + 1u;
}

static uint32_t degree_upper(uint32_t D) {
    // Largest integer d satisfying d^3 < 64 D^2, exactly equivalent to
    // d < 4 D^(2/3).  All arithmetic is performed in 128 bits.
    const __uint128_t target = static_cast<__uint128_t>(64u) * D * D;
    uint32_t lo = 0, hi = 2000000u;
    while (lo < hi) {
        const uint32_t mid = lo + (hi - lo + 1u) / 2u;
        const __uint128_t cube = static_cast<__uint128_t>(mid) * mid * mid;
        if (cube < target) lo = mid;
        else hi = mid - 1u;
    }
    return lo;
}

static uint64_t mod_pow(uint64_t a, uint64_t e, uint64_t mod) {
    uint64_t r = 1;
    while (e) {
        if (e & 1) r = static_cast<uint64_t>((static_cast<__uint128_t>(r) * a) % mod);
        a = static_cast<uint64_t>((static_cast<__uint128_t>(a) * a) % mod);
        e >>= 1;
    }
    return r;
}

static uint64_t inv_prime(uint64_t a, uint64_t p) {
    return mod_pow(a % p, p - 2, p);
}

static std::vector<uint32_t> allowed_residues(uint32_t prime,
                                               bool applies1, uint32_t coeff1,
                                               bool applies2, uint32_t coeff2) {
    std::vector<uint32_t> cur;
    auto one_side = [prime](uint32_t coeff) {
        std::vector<uint32_t> a;
        if (coeff % prime == 0) return a; // empty denotes all residues
        const uint64_t inv = inv_prime(coeff, prime);
        const uint32_t z = static_cast<uint32_t>((prime - (2 * inv) % prime) % prime);
        a.push_back(0);
        if (z != 0) a.push_back(z);
        return a;
    };
    const auto a1 = applies1 ? one_side(coeff1) : std::vector<uint32_t>{};
    const auto a2 = applies2 ? one_side(coeff2) : std::vector<uint32_t>{};
    const bool all1 = !applies1 || coeff1 % prime == 0;
    const bool all2 = !applies2 || coeff2 % prime == 0;
    if (all1 && all2) return {}; // all residues
    if (all1) return a2;
    if (all2) return a1;
    for (uint32_t x : a1) {
        if (std::find(a2.begin(), a2.end(), x) != a2.end()) cur.push_back(x);
    }
    return cur; // possibly empty; caller distinguishes using all flags below
}

static bool interval_contains_residue(uint64_t lo, uint64_t hi,
                                      uint64_t residue, uint64_t modulus) {
    if (lo > hi) return false;
    if (modulus == 1) return true;
    const uint64_t rem = lo % modulus;
    const uint64_t delta = (residue + modulus - rem) % modulus;
    return delta <= hi - lo;
}

static bool k_congruence_exists(uint32_t klo, uint32_t khi,
                                uint32_t r, uint32_t s,
                                const Shape& x, const Shape& y) {
    if (klo > khi) return false;
    std::vector<uint32_t> primes = x.all_primes;
    for (uint32_t p : y.all_primes) {
        if (std::find(primes.begin(), primes.end(), p) == primes.end()) primes.push_back(p);
    }
    std::sort(primes.begin(), primes.end());

    std::vector<uint64_t> residues{0};
    uint64_t modulus = 1;
    for (uint32_t p : primes) {
        const bool in_x = x.rad_product % p == 0;
        const bool in_y = y.rad_product % p == 0;
        const bool all_x = !in_x || s % p == 0;
        const bool all_y = !in_y || r % p == 0;
        std::vector<uint32_t> allow = allowed_residues(p, in_x, s, in_y, r);
        if (!all_x && !all_y && allow.empty()) return false;
        if (all_x && all_y) continue;
        if (allow.empty()) return false; // defensive; non-all side always supplies >=1 root

        const uint64_t inv = inv_prime(modulus % p, p);
        std::vector<uint64_t> next;
        next.reserve(residues.size() * allow.size());
        for (uint64_t a : residues) {
            for (uint32_t b : allow) {
                const uint64_t rhs = (b + p - (a % p)) % p;
                const uint64_t t = (rhs * inv) % p;
                next.push_back(a + modulus * t);
            }
        }
        modulus *= p;
        residues.swap(next);
    }
    for (uint64_t a : residues) {
        if (interval_contains_residue(klo, khi, a, modulus)) return true;
    }
    return false;
}

static uint32_t role_value(uint32_t p, const Shape& sh) {
    uint32_t value = 0;
    unsigned hits = 0;
    for (uint32_t v : {sh.a, sh.b, sh.n}) {
        if (v % p == 0) {
            value = v;
            ++hits;
        }
    }
    if (hits != 1) throw std::runtime_error("invalid primitive p-role");
    return value;
}

static uint32_t role_binomial_degree_bound(uint32_t r, uint32_t s,
                                           const Shape& x, const Shape& y) {
    std::vector<uint32_t> primes = x.all_primes;
    for (uint32_t p : y.all_primes) {
        if (std::find(primes.begin(), primes.end(), p) == primes.end()) primes.push_back(p);
    }
    uint64_t bound = std::numeric_limits<uint32_t>::max();
    for (uint32_t p : primes) {
        const bool in_x = x.rad_product % p == 0;
        const bool in_y = y.rad_product % p == 0;
        const uint64_t e1 = in_x ? static_cast<uint64_t>(r) * role_value(p, x) : 0;
        const uint64_t e2 = in_y ? static_cast<uint64_t>(s) * role_value(p, y) : 0;
        const uint64_t g = in_x && in_y ? std::gcd(e1, e2) : (in_x ? e1 : e2);
        bound = std::min(bound, g);
    }
    return static_cast<uint32_t>(bound);
}

static bool disjoint_scaled_triples(const Shape& x, uint32_t r,
                                    const Shape& y, uint32_t s) {
    const std::array<uint64_t, 3> a{{
        static_cast<uint64_t>(r) * x.a,
        static_cast<uint64_t>(r) * x.b,
        static_cast<uint64_t>(r) * x.n
    }};
    const std::array<uint64_t, 3> b{{
        static_cast<uint64_t>(s) * y.a,
        static_cast<uint64_t>(s) * y.b,
        static_cast<uint64_t>(s) * y.n
    }};
    for (uint64_t u : a) for (uint64_t v : b) if (u == v) return false;
    return true;
}

static std::vector<uint32_t> scale_primes_ge5(uint32_t n) {
    std::vector<uint32_t> out;
    // The support index deliberately omits 2 and 3, so remove their full
    // powers before extracting the remaining prime support.  Without this
    // step a scale such as 2*prime could be mistaken for one composite atom.
    while (n % 2u == 0u) n /= 2u;
    while (n % 3u == 0u) n /= 3u;
    for (uint32_t p = 5; static_cast<uint64_t>(p) * p <= n; p += 2) {
        if (n % p == 0) {
            out.push_back(p);
            while (n % p == 0) n /= p;
        }
    }
    if (n >= 5) out.push_back(n);
    return out;
}

static std::vector<uint32_t> compatible_target_supports(uint32_t supp1,
                                                         uint32_t r,
                                                         uint32_t s) {
    // For p >= 5, support1 \ support2 may only be supplied by scale s,
    // while support2 \ support1 may only be supplied by scale r.
    const auto ps = scale_primes_ge5(s);
    const auto pr = scale_primes_ge5(r);
    std::vector<uint32_t> drops, adds;
    for (uint32_t p : ps) if (supp1 % p == 0) drops.push_back(p);
    for (uint32_t p : pr) if (supp1 % p != 0) adds.push_back(p);
    std::vector<uint32_t> out;
    for (uint32_t dm = 0; dm < (1u << drops.size()); ++dm) {
        uint32_t base = supp1;
        for (size_t i = 0; i < drops.size(); ++i) if ((dm >> i) & 1u) base /= drops[i];
        for (uint32_t am = 0; am < (1u << adds.size()); ++am) {
            uint32_t v = base;
            for (size_t i = 0; i < adds.size(); ++i) if ((am >> i) & 1u) v *= adds[i];
            out.push_back(v);
        }
    }
    std::sort(out.begin(), out.end());
    out.erase(std::unique(out.begin(), out.end()), out.end());
    return out;
}

static void self_test_support_targets() {
    for (uint32_t n = 1; n <= SCALE_MAX; ++n) {
        auto expected = factor_squarefree(n);
        expected.erase(std::remove_if(expected.begin(), expected.end(),
                                      [](uint32_t p) { return p < 5; }),
                       expected.end());
        const auto actual = scale_primes_ge5(n);
        if (actual != expected) {
            throw std::runtime_error("scale support self-test failed at n=" + std::to_string(n));
        }
    }

    const std::vector<uint32_t> sample_supports{
        1u, 5u, 7u, 11u, 23u, 5u*7u, 5u*23u, 7u*11u*23u
    };
    for (uint32_t r = 1; r <= SCALE_MAX; ++r) {
        for (uint32_t s = 1; s <= SCALE_MAX; ++s) {
            for (uint32_t supp1 : sample_supports) {
                auto actual = compatible_target_supports(supp1, r, s);
                std::vector<uint32_t> universe = factor_squarefree(supp1);
                for (uint32_t p : factor_squarefree(r)) {
                    if (p >= 5 && std::find(universe.begin(), universe.end(), p) == universe.end()) {
                        universe.push_back(p);
                    }
                }
                universe.erase(std::remove_if(universe.begin(), universe.end(),
                                              [](uint32_t p) { return p < 5; }),
                               universe.end());
                std::sort(universe.begin(), universe.end());

                std::vector<uint32_t> expected;
                const uint32_t masks = 1u << universe.size();
                for (uint32_t mask = 0; mask < masks; ++mask) {
                    uint32_t supp2 = 1;
                    for (size_t i = 0; i < universe.size(); ++i) {
                        if ((mask >> i) & 1u) supp2 *= universe[i];
                    }
                    bool ok = true;
                    for (uint32_t p : factor_squarefree(supp1)) {
                        if (p >= 5 && supp2 % p != 0 && s % p != 0) ok = false;
                    }
                    for (uint32_t p : factor_squarefree(supp2)) {
                        if (p >= 5 && supp1 % p != 0 && r % p != 0) ok = false;
                    }
                    if (ok) expected.push_back(supp2);
                }
                std::sort(expected.begin(), expected.end());
                expected.erase(std::unique(expected.begin(), expected.end()), expected.end());
                if (actual != expected) {
                    throw std::runtime_error("support-target self-test failed");
                }
            }
        }
    }
    std::cout << "support_target_generation=PASS\n";
}

int main(int argc, char** argv) {
    std::string input = "generic_shapes.csv";
    std::string output;
    int threads = 0;
    uint32_t dmin = DUNIT;
    uint32_t dmax = DMAX;
    bool self_test_support = false;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--input" && i + 1 < argc) input = argv[++i];
        else if (a == "--output" && i + 1 < argc) output = argv[++i];
        else if (a == "--threads" && i + 1 < argc) threads = std::stoi(argv[++i]);
        else if (a == "--dmin" && i + 1 < argc) dmin = static_cast<uint32_t>(parse_u64(argv[++i]));
        else if (a == "--dmax" && i + 1 < argc) dmax = static_cast<uint32_t>(parse_u64(argv[++i]));
        else if (a == "--self-test-support") self_test_support = true;
        else {
            std::cerr << "usage: " << argv[0]
                      << " [--input shapes.csv] [--output survivors.csv]"
                      << " [--threads T] [--dmin D] [--dmax D] [--self-test-support]\n";
            return 2;
        }
    }
#ifdef _OPENMP
    if (threads > 0) omp_set_num_threads(threads);
#else
    (void)threads;
#endif

    if (self_test_support) {
        self_test_support_targets();
        return 0;
    }

    const auto t0 = std::chrono::steady_clock::now();
    const auto shapes = read_shapes(input);
    const auto t1 = std::chrono::steady_clock::now();

    // groups[scale][support outside {2,3}] = shape indices satisfying the
    // scale-independent conservative support cap.
    using GroupMap = std::unordered_map<uint32_t, std::vector<uint32_t>>;
    std::array<GroupMap, SCALE_MAX + 1> groups;
    uint64_t scaled_records = 0;
    for (uint32_t i = 0; i < shapes.size(); ++i) {
        const Shape& sh = shapes[i];
        for (uint32_t r = 1; r <= SCALE_MAX; ++r) {
            if (static_cast<uint64_t>(r) * sh.n > dmax) break;
            if (static_cast<uint64_t>(sh.rad_product) * r > SUPPORT_PRODUCT_CAP) continue;
            groups[r][sh.support5].push_back(i);
            ++scaled_records;
        }
    }
    const auto t2 = std::chrono::steady_clock::now();

    int max_threads = 1;
#ifdef _OPENMP
    max_threads = omp_get_max_threads();
#endif
    std::vector<std::vector<Survivor>> local_surv(static_cast<size_t>(max_threads));
    std::vector<uint64_t> local_support_pairs(static_cast<size_t>(max_threads), 0);
    std::vector<uint64_t> local_shape_pairs(static_cast<size_t>(max_threads), 0);
    std::vector<uint64_t> local_after_exact_cap(static_cast<size_t>(max_threads), 0);
    std::vector<uint64_t> local_after_degree(static_cast<size_t>(max_threads), 0);
    std::vector<uint64_t> local_after_role_binomial(static_cast<size_t>(max_threads), 0);
    std::vector<std::pair<uint32_t,uint32_t>> scale_pairs;
    for (uint32_t r = 1; r <= SCALE_MAX; ++r) {
        for (uint32_t s = r; s <= SCALE_MAX; ++s) {
            if (std::gcd(r, s) == 1) scale_pairs.push_back({r,s});
        }
    }

#pragma omp parallel for schedule(dynamic, 1)
    for (int64_t z = 0; z < static_cast<int64_t>(scale_pairs.size()); ++z) {
        int tid = 0;
#ifdef _OPENMP
        tid = omp_get_thread_num();
#endif
        const uint32_t r = scale_pairs[static_cast<size_t>(z)].first;
        const uint32_t s = scale_pairs[static_cast<size_t>(z)].second;
        const auto& g1 = groups[r];
        const auto& g2 = groups[s];
        auto& survivors = local_surv[static_cast<size_t>(tid)];

        for (const auto& kv : g1) {
            const uint32_t supp1 = kv.first;
            const auto targets = compatible_target_supports(supp1, r, s);
            for (uint32_t supp2 : targets) {
                auto it2 = g2.find(supp2);
                if (it2 == g2.end()) continue;
                ++local_support_pairs[static_cast<size_t>(tid)];
                const auto& v1 = kv.second;
                const auto& v2 = it2->second;
                for (uint32_t i : v1) {
                    for (uint32_t j : v2) {
                        if (r == s && j <= i) continue; // only possible for r=s=1
                        ++local_shape_pairs[static_cast<size_t>(tid)];
                        const Shape& x = shapes[i];
                        const Shape& y = shapes[j];
                        const uint32_t D = static_cast<uint32_t>(std::max<uint64_t>(
                            static_cast<uint64_t>(r) * x.n,
                            static_cast<uint64_t>(s) * y.n));
                        if (D < dmin || D > dmax) continue;
                        if (!disjoint_scaled_triples(x, r, y, s)) continue;
                        if (static_cast<uint64_t>(x.rad_product) * r > SUPPORT_PRODUCT_CAP) continue;
                        if (static_cast<uint64_t>(y.rad_product) * s > SUPPORT_PRODUCT_CAP) continue;
                        ++local_after_exact_cap[static_cast<size_t>(tid)];

                        const uint32_t dl = degree_lower(D);
                        const uint32_t du = degree_upper(D);
                        const uint32_t L = std::min(x.n, y.n) - 2;
                        const uint64_t rs = static_cast<uint64_t>(r) * s;
                        const uint32_t klo = static_cast<uint32_t>((dl + rs - 1) / rs);
                        // The primitive factors are proper: their degrees s*k and r*k
                        // leave a nonconstant complementary factor.  Degree one is
                        // impossible by the rational-root theorem, so leave at least 2.
                        uint64_t kbound = std::min<uint64_t>(du, L) / rs;
                        if (x.n >= 4) kbound = std::min<uint64_t>(kbound, (x.n - 4) / s);
                        else kbound = 0;
                        if (y.n >= 4) kbound = std::min<uint64_t>(kbound, (y.n - 4) / r);
                        else kbound = 0;
                        uint32_t khi = static_cast<uint32_t>(kbound);
                        if (klo > khi) continue;
                        ++local_after_degree[static_cast<size_t>(tid)];

                        const uint32_t role_bound = role_binomial_degree_bound(r, s, x, y);
                        khi = std::min<uint32_t>(khi, role_bound / rs);
                        if (klo > khi) continue;
                        ++local_after_role_binomial[static_cast<size_t>(tid)];

                        if (!k_congruence_exists(klo, khi, r, s, x, y)) continue;
                        survivors.push_back({i,j,static_cast<uint16_t>(r),static_cast<uint16_t>(s),D,klo,khi});
                    }
                }
            }
        }
    }

    uint64_t support_group_pairs = 0, shape_pairs = 0, after_cap = 0, after_degree = 0, after_role = 0;
    size_t survivor_count = 0;
    for (int t = 0; t < max_threads; ++t) {
        support_group_pairs += local_support_pairs[static_cast<size_t>(t)];
        shape_pairs += local_shape_pairs[static_cast<size_t>(t)];
        after_cap += local_after_exact_cap[static_cast<size_t>(t)];
        after_degree += local_after_degree[static_cast<size_t>(t)];
        after_role += local_after_role_binomial[static_cast<size_t>(t)];
        survivor_count += local_surv[static_cast<size_t>(t)].size();
    }

    std::vector<Survivor> all;
    if (!output.empty()) {
        all.reserve(survivor_count);
        for (auto& v : local_surv) all.insert(all.end(), v.begin(), v.end());
        std::sort(all.begin(), all.end());
        std::ofstream f(output);
        if (!f) throw std::runtime_error("cannot open output: " + output);
        f << "r,a,b,n,s,c,d,m,D,k_lo,k_hi,radprod1,radprod2,support1,support2\n";
        for (const Survivor& z : all) {
            const Shape& x = shapes[z.i];
            const Shape& y = shapes[z.j];
            f << z.r << ',' << x.a << ',' << x.b << ',' << x.n << ','
              << z.s << ',' << y.a << ',' << y.b << ',' << y.n << ','
              << z.D << ',' << z.k_lo << ',' << z.k_hi << ','
              << x.rad_product << ',' << y.rad_product << ','
              << x.support5 << ',' << y.support5 << '\n';
        }
    }

    const auto t3 = std::chrono::steady_clock::now();
    auto sec = [](auto a, auto b) { return std::chrono::duration<double>(b-a).count(); };
    std::cout << "shapes=" << shapes.size() << "\n"
              << "scaled_records=" << scaled_records << "\n"
              << "scale_pairs=" << scale_pairs.size() << "\n"
              << "support_group_pairs=" << support_group_pairs << "\n"
              << "shape_pairs_considered=" << shape_pairs << "\n"
              << "after_support_cap_and_disjointness=" << after_cap << "\n"
              << "after_degree_interval=" << after_degree << "\n"
              << "after_role_binomial_interval=" << after_role << "\n"
              << "after_full_radical_CRT=" << survivor_count << "\n"
              << "seconds_read=" << sec(t0,t1) << "\n"
              << "seconds_group=" << sec(t1,t2) << "\n"
              << "seconds_pair=" << sec(t2,t3) << "\n";
    return 0;
}
