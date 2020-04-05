ok:
	php test.php --parse-script=apps/parse.php --directory=tests/parse-only/ --recursive --parse-only > test-parse.html
	php test.php --int-script=apps/interpret.py --directory=tests/int-only --recursive --int-only > test-int.html
	php test.php --parse-script=apps/parse.php --int-script=apps/interpret.py --directory=tests/both --recursive > test-both.html

error:
	php test.php --parse-only --int-only --recursive

