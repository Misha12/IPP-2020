int-only:
	php test/test.php --int-script=interpret/interpret.py --directory=test/tests/int-only --recursive --int-only --debug > test-int.html

int-stati:
	python3.8 interpret/interpret.py --stats=interpret/data/stats.txt --insts --vars --insts --source=test/tests/int-only/vyzi_tests/should-pass/from-parse-only/every_instruction_program.src --input=test/tests/int-only/vyzi_tests/should-pass/from-parse-only/every_instruction_program.in
	@echo
	@echo
	@cat interpret/data/stats.txt

nati-tests-int:
	php test/test.php --int-script=interpret/interpret.py --int-only --recursive --debug --directory=/mnt/c/Users/mhala/OneDrive/Vyvoj/GitHub/ipp-2020-tests/interpret-only/ > test-int-nati.html

koule-pol:
	python3.8 interpret/interpret.py --source=/mnt/c/Users/mhala/OneDrive/Vyvoj/GitHub/ipp-2020-tests/koule/pol/koule_pol.xml --stats=koule_pol_stats.stats --insts --vars 

koule-pol-no-stats:
	python3.8 interpret/interpret.py --source=/mnt/c/Users/mhala/OneDrive/Vyvoj/GitHub/ipp-2020-tests/koule/pol/koule_pol.xml
