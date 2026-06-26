CXX ?= g++
CXXFLAGS ?= -O3 -std=c++20 -fopenmp -Wall -Wextra -Wpedantic
THREADS ?= 25

.PHONY: q12-build q12-verify-light q12-verify-modular q12-verify-irreducibility-direct q12-verify-upper q12-one-nonunit-all clean

q12-build:
	mkdir -p build
	$(CXX) $(CXXFLAGS) code/qab12/enumerate_one_nonunit_packages.cpp -o build/qab12_enumerate_one_nonunit_packages
	$(CXX) $(CXXFLAGS) code/qab12/pair_one_nonunit.cpp -o build/qab12_pair_one_nonunit
	$(CXX) $(CXXFLAGS) code/qab12/enumerate_two_nonunit_packages.cpp -o build/qab12_enumerate_two_nonunit_packages
	$(CXX) $(CXXFLAGS) code/qab12/pair_two_nonunit.cpp -o build/qab12_pair_two_nonunit
	$(CXX) $(CXXFLAGS) code/qab12/enumerate_unit_small_packages.cpp -o build/qab12_enumerate_unit_small_packages
	$(CXX) $(CXXFLAGS) code/qab12/pair_unit_small.cpp -o build/qab12_pair_unit_small

q12-verify-light: q12-build
	python3 code/qab12/certify_qab12_constants.py
	python3 code/qab12/verify_two_nonunit.py --packages data/qab12/two_nonunit_packages.csv --state-pairs data/qab12/two_nonunit_state_pairs.csv
	python3 code/qab12/verify_one_nonunit.py --data-dir data/qab12
	python3 code/qab12/test_one_nonunit_small.py
	python3 code/qab12/test_two_nonunit_small.py

q12-verify-modular:
	python3 code/qab12/verify_modular_gcd_certificates.py --pairs data/qab12/unit_large_modular_input.csv --certificates data/qab12/unit_large_modular_certificates.csv
	python3 code/qab12/verify_modular_gcd_certificates.py --pairs data/qab12/unit_small_modular_input.csv --certificates data/qab12/unit_small_modular_certificates.csv

q12-verify-irreducibility-direct:
	python3 code/qab12/verify_irreducibility_certificates_direct.py --states data/qab12/unit_defect_state_pairs.csv --certificates data/qab12/unit_defect_irreducibility_certificates.jsonl

q12-verify-upper:
	python3 code/qab12/verify_upper_safe.py

q12-one-nonunit-all: q12-build
	THREADS=$(THREADS) bash code/qab12/run_all_one_nonunit_unfiltered.sh

clean:
	rm -rf build
