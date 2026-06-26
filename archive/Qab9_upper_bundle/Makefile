CXX ?= g++
CXXFLAGS ?= -O3 -std=c++20 -fopenmp -Wall -Wextra -Wpedantic
THREADS ?= 25
BUILD := build
DATA := data
CODE := code

.PHONY: all upper verify test factor60 lower-catalog deep-diagnostic modular-sample clean distclean

all: upper verify

$(BUILD):
	mkdir -p $(BUILD)

$(DATA):
	mkdir -p $(DATA)

$(BUILD)/enumerate_shapes: $(CODE)/enumerate_shapes.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ $<

$(BUILD)/pair_upper: $(CODE)/pair_upper.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ $<

upper: $(BUILD)/enumerate_shapes $(BUILD)/pair_upper | $(DATA)
	@set -e; : > $(DATA)/upper_pipeline_output.txt; \
	python3 $(CODE)/certify_constants.py | tee -a $(DATA)/upper_pipeline_output.txt; \
	$(BUILD)/enumerate_shapes --limit 175394637 --rad-cap 4398937 --min-total 3 \
	  --threads $(THREADS) --output $(DATA)/upper_shapes.csv | tee -a $(DATA)/upper_pipeline_output.txt; \
	$(BUILD)/pair_upper --input $(DATA)/upper_shapes.csv \
	  --output $(DATA)/upper_pair_survivors.csv --threads $(THREADS) \
	  --dmin 6816242 --dmax 175394637 | tee -a $(DATA)/upper_pipeline_output.txt; \
	python3 $(CODE)/same_shape_screen.py --input $(DATA)/upper_pair_survivors.csv \
	  --output $(DATA)/upper_residual_candidates.csv | tee -a $(DATA)/upper_pipeline_output.txt

verify:
	@python3 $(CODE)/verify_upper.py --data-dir $(DATA) | tee $(DATA)/verification_output.txt

test: $(BUILD)/enumerate_shapes $(BUILD)/pair_upper
	$(BUILD)/pair_upper --self-test-support
	python3 $(CODE)/test_small.py --enumerator $(BUILD)/enumerate_shapes

factor60:
	python3 $(CODE)/factor_through_60.py --max-total 60 --workers $(THREADS) | tee $(DATA)/factor60_output.txt

lower-catalog:
	python3 $(CODE)/lower_exception_catalog.py | tee $(DATA)/lower_exception_catalog.txt

deep-diagnostic:
	python3 $(CODE)/postfilter_upper.py --input $(DATA)/upper_pair_survivors.csv \
	  --output $(DATA)/upper_exact_degree_candidates.csv

modular-sample:
	python3 $(CODE)/modular_screen.py --input $(DATA)/upper_exact_degree_candidates.csv \
	  --pair-limit 1 --workers 1 --timeout 30 --attempts 3 \
	  --certificates $(DATA)/sample_certificates.csv \
	  --unresolved $(DATA)/sample_unresolved.jsonl

clean:
	rm -rf $(BUILD)

distclean: clean
	rm -f $(DATA)/upper_shapes.csv $(DATA)/upper_pair_survivors.csv \
	  $(DATA)/upper_exact_degree_candidates.csv $(DATA)/upper_residual_candidates.csv \
	  $(DATA)/upper_pipeline_output.txt $(DATA)/verification_output.txt
