KOULE_PATH=test/tests/koule_pol.xml
KOULE_STATS_DIR=data/koule_pol_stats.stats
NATI_TESTS=../testy/interpret-only/
NATI_HTML=data/nati_int-tests.html
NATI_TESTS_BOTH=../testy/both/
NATI_HTML_BOTH=data/nati_both-tests.html

int-only:
	php test/test.php --int-script=interpret/interpret.py --directory=test/tests/int-only --recursive --int-only --debug > test-int.html

int-stati:
	python3.8 interpret/interpret.py --stats=interpret/data/stats.txt --insts --vars --insts --source=test/tests/int-only/vyzi_tests/should-pass/from-parse-only/every_instruction_program.src --input=test/tests/int-only/vyzi_tests/should-pass/from-parse-only/every_instruction_program.in
	@echo
	@echo
	@cat interpret/data/stats.txt

nati-tests-int:
	php test/test.php --int-script=interpret/interpret.py --int-only --recursive --debug --directory=$(NATI_TESTS) > $(NATI_HTML)

koule-pol:
	python3.8 interpret/interpret.py --source=$(KOULE_PATH) --stats=$(KOULE_STATS_DIR) --insts --vars 

koule-pol-no-stats:
	python3.8 interpret/interpret.py --source=$(KOULE_PATH)

nati-tests-both:
	php test/test.php --int-script=interpret/interpret.py --parse-script=test/apps/parse.php --recursive --debug --directory=$(NATI_TESTS_BOTH) > $(NATI_HTML_BOTH)
