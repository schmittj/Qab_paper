#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

struct RadNum {
    uint32_t n;
    uint32_t rad;
};

struct Triple {
    uint32_t a, b, n;
    bool operator<(const Triple& o) const {
        return std::tie(n, a, b) < std::tie(o.n, o.a, o.b);
    }
    bool operator==(const Triple& o) const {
        return a == o.a && b == o.b && n == o.n;
    }
};

static uint64_t parse_u64(const char* s) {
    char* e = nullptr;
    const unsigned long long v = std::strtoull(s, &e, 10);
    if (!e || *e) throw std::runtime_error(std::string("invalid integer: ") + s);
    return static_cast<uint64_t>(v);
}

static uint32_t floor_sqrt_u64(uint64_t x) {
    uint64_t r = static_cast<uint64_t>(std::sqrt(static_cast<long double>(x)));
    while ((r + 1) * (r + 1) <= x) ++r;
    while (r * r > x) --r;
    return static_cast<uint32_t>(r);
}

static uint32_t floor_cuberoot_u64(uint64_t x) {
    uint64_t r = static_cast<uint64_t>(std::cbrt(static_cast<long double>(x)));
    auto cube = [](uint64_t y) -> __uint128_t { return static_cast<__uint128_t>(y) * y * y; };
    while (cube(r + 1) <= x) ++r;
    while (cube(r) > x) --r;
    return static_cast<uint32_t>(r);
}

static std::vector<uint32_t> small_primes(uint32_t n) {
    std::vector<bool> composite(static_cast<size_t>(n) + 1, false);
    std::vector<uint32_t> primes;
    for (uint32_t i = 2; i <= n; ++i) {
        if (!composite[i]) {
            primes.push_back(i);
            if (static_cast<uint64_t>(i) * i <= n) {
                for (uint64_t j = static_cast<uint64_t>(i) * i; j <= n; j += i) {
                    composite[static_cast<size_t>(j)] = true;
                }
            }
        }
    }
    return primes;
}

static void gen_rad_bounded_rec(const std::vector<uint32_t>& primes,
                                size_t start,
                                uint64_t n,
                                uint64_t r,
                                uint32_t limit,
                                uint32_t rcap,
                                std::vector<RadNum>& out) {
    for (size_t i = start; i < primes.size(); ++i) {
        const uint64_t p = primes[i];
        if (r * p > rcap || n * p > limit) break;
        uint64_t pp = p;
        while (n * pp <= limit) {
            const uint64_t nn = n * pp;
            out.push_back({static_cast<uint32_t>(nn), static_cast<uint32_t>(r * p)});
            gen_rad_bounded_rec(primes, i + 1, nn, r * p, limit, rcap, out);
            if (pp > limit / p) break;
            pp *= p;
        }
    }
}

static std::vector<RadNum> gen_rad_bounded(uint32_t limit, uint32_t rcap) {
    const auto primes = small_primes(rcap);
    std::vector<RadNum> out;
    out.reserve(100000);
    out.push_back({1, 1});
    gen_rad_bounded_rec(primes, 0, 1, 1, limit, rcap, out);
    std::sort(out.begin(), out.end(), [](const RadNum& x, const RadNum& y) {
        return std::tie(x.n, x.rad) < std::tie(y.n, y.rad);
    });
    return out;
}

static std::vector<uint32_t> radical_sieve(uint32_t n) {
    std::vector<uint32_t> rad(static_cast<size_t>(n) + 1, 1);
    rad[0] = 0;
    for (uint32_t p = 2; p <= n; ++p) {
        if (rad[p] == 1) {
            for (uint64_t j = p; j <= n; j += p) rad[static_cast<size_t>(j)] *= p;
        }
    }
    return rad;
}

// role 0 = smaller endpoint a, role 1 = larger endpoint b, role 2 = total n.
// Require the supplied (x,role_x) and (y,role_y) to be exactly the first two
// entries in lexicographic order (radical, role).  This makes every triple
// appear once, including radical ties.
static inline bool canonical_witness(uint32_t a,
                                     uint32_t b,
                                     uint32_t n,
                                     uint32_t x,
                                     int role_x,
                                     uint32_t y,
                                     int role_y,
                                     const std::vector<uint32_t>& rad) {
    std::array<std::pair<uint32_t, int>, 3> key{{
        {rad[a], 0}, {rad[b], 1}, {rad[n], 2}
    }};
    std::sort(key.begin(), key.end());
    return key[0] == std::make_pair(rad[x], role_x) &&
           key[1] == std::make_pair(rad[y], role_y);
}

struct LocalResult {
    uint64_t count = 0;
    std::vector<Triple> triples;
};

int main(int argc, char** argv) {
    uint32_t limit = 1000000;
    uint64_t cap = 4398937;
    uint32_t min_total = 3;
    int threads = 0;
    std::string output;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--limit" && i + 1 < argc) limit = static_cast<uint32_t>(parse_u64(argv[++i]));
        else if (arg == "--rad-cap" && i + 1 < argc) cap = parse_u64(argv[++i]);
        else if (arg == "--min-total" && i + 1 < argc) min_total = static_cast<uint32_t>(parse_u64(argv[++i]));
        else if (arg == "--threads" && i + 1 < argc) threads = std::atoi(argv[++i]);
        else if (arg == "--output" && i + 1 < argc) output = argv[++i];
        else {
            std::cerr << "usage: " << argv[0]
                      << " [--limit N] [--rad-cap B] [--min-total N]"
                      << " [--threads T] [--output file]\n";
            return 2;
        }
    }
#ifdef _OPENMP
    if (threads > 0) omp_set_num_threads(threads);
#else
    (void)threads;
#endif

    const auto t0 = std::chrono::steady_clock::now();
    const auto rad = radical_sieve(limit);
    const auto t1 = std::chrono::steady_clock::now();
    const uint32_t cbrt_cap = floor_cuberoot_u64(cap);
    const uint32_t sqrt_cap = floor_sqrt_u64(cap);
    const auto small1 = gen_rad_bounded(limit, cbrt_cap);
    const auto small2 = gen_rad_bounded(limit, sqrt_cap);
    const auto t2 = std::chrono::steady_clock::now();

    std::cerr << "limit=" << limit << " cap=" << cap
              << " cbrt=" << cbrt_cap << " sqrt=" << sqrt_cap
              << " list1=" << small1.size() << " list2=" << small2.size() << "\n";

    int max_threads = 1;
#ifdef _OPENMP
    max_threads = omp_get_max_threads();
#endif
    std::vector<LocalResult> local(static_cast<size_t>(max_threads));

#pragma omp parallel for schedule(dynamic, 8)
    for (int64_t ii = 0; ii < static_cast<int64_t>(small1.size()); ++ii) {
        int tid = 0;
#ifdef _OPENMP
        tid = omp_get_thread_num();
#endif
        auto& out = local[static_cast<size_t>(tid)];
        const RadNum x = small1[static_cast<size_t>(ii)];

        for (const RadNum& y : small2) {
            const uint64_t rxy = static_cast<uint64_t>(x.rad) * y.rad;
            if (rxy > cap) continue;
            const uint32_t max_rz = static_cast<uint32_t>(cap / rxy);

            // Case I: the two least-radical roles are the two endpoints.
            // Their numerical order is irrelevant; canonicalize to a < b.
            if (static_cast<uint64_t>(x.n) + y.n <= limit && x.n != y.n) {
                const uint32_t a = std::min(x.n, y.n);
                const uint32_t b = std::max(x.n, y.n);
                const uint32_t n = a + b;
                const int role_x = (x.n == a) ? 0 : 1;
                const int role_y = (y.n == a) ? 0 : 1;
                if (n >= min_total && rad[n] <= max_rz &&
                    canonical_witness(a, b, n, x.n, role_x, y.n, role_y, rad) &&
                    std::gcd(a, b) == 1) {
                    ++out.count;
                    if (!output.empty()) out.triples.push_back({a, b, n});
                }
            }

            // Case II: x is an endpoint and y is the total.
            if (y.n > x.n) {
                const uint32_t other = y.n - x.n;
                if (other != x.n) {
                    const uint32_t a = std::min(x.n, other);
                    const uint32_t b = std::max(x.n, other);
                    const uint32_t n = y.n;
                    const int role_x = (x.n == a) ? 0 : 1;
                    if (n >= min_total && rad[other] <= max_rz &&
                        canonical_witness(a, b, n, x.n, role_x, y.n, 2, rad) &&
                        std::gcd(a, b) == 1) {
                        ++out.count;
                        if (!output.empty()) out.triples.push_back({a, b, n});
                    }
                }
            }

            // Case III: x is the total and y is an endpoint.
            if (x.n > y.n) {
                const uint32_t other = x.n - y.n;
                if (other != y.n) {
                    const uint32_t a = std::min(y.n, other);
                    const uint32_t b = std::max(y.n, other);
                    const uint32_t n = x.n;
                    const int role_y = (y.n == a) ? 0 : 1;
                    if (n >= min_total && rad[other] <= max_rz &&
                        canonical_witness(a, b, n, x.n, 2, y.n, role_y, rad) &&
                        std::gcd(a, b) == 1) {
                        ++out.count;
                        if (!output.empty()) out.triples.push_back({a, b, n});
                    }
                }
            }
        }
    }

    uint64_t count = 0;
    for (const auto& lr : local) count += lr.count;

    std::vector<Triple> all;
    if (!output.empty()) {
        size_t total = 0;
        for (const auto& lr : local) total += lr.triples.size();
        all.reserve(total);
        for (auto& lr : local) {
            all.insert(all.end(), lr.triples.begin(), lr.triples.end());
            std::vector<Triple>().swap(lr.triples);
        }
        std::sort(all.begin(), all.end());
        all.erase(std::unique(all.begin(), all.end()), all.end());
        std::ofstream f(output);
        if (!f) throw std::runtime_error("cannot open output file: " + output);
        f << "a,b,n,rad_a,rad_b,rad_n,rad_product\n";
        for (const Triple& tr : all) {
            f << tr.a << ',' << tr.b << ',' << tr.n << ','
              << rad[tr.a] << ',' << rad[tr.b] << ',' << rad[tr.n] << ','
              << static_cast<uint64_t>(rad[tr.a]) * rad[tr.b] * rad[tr.n] << '\n';
        }
    }

    const auto t3 = std::chrono::steady_clock::now();
    auto seconds = [](auto a, auto b) { return std::chrono::duration<double>(b - a).count(); };
    std::cout << "primitive_candidates=" << count << "\n";
    if (!output.empty()) std::cout << "unique_written=" << all.size() << "\n";
    std::cout << "seconds_radical_sieve=" << seconds(t0, t1) << "\n"
              << "seconds_small_lists=" << seconds(t1, t2) << "\n"
              << "seconds_pair_scan=" << seconds(t2, t3) << "\n";
    return 0;
}
