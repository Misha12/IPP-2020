int-only:
	php test/test.php --int-script=interpret/interpret.py --directory=test/tests/int-only --recursive --int-only > test-int.html

int-stati:
	python3.8 interpret/interpret.py --stats=interpret/data/stats.txt --insts --vars --insts --source=test/tests/int-only/vyzi_tests/should-pass/from-parse-only/every_instruction_program.src --input=test/tests/int-only/vyzi_tests/should-pass/from-parse-only/every_instruction_program.in
	@echo
	@echo
	@cat interpret/data/stats.txt
