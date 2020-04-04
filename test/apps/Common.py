import sys
from enum import IntEnum

class ExitCode(IntEnum):
	""" Seznam návratových kódů programu při předčasném ukončení """
	# Obecné návratové kódy
	PROGRAM_ARGUMENT = 10
	FILE_READ = 11
	FILE_WRITE = 12
	INTERNAL = 99

	# Chyby týkající se XML
	XML_FORMAT = 31
	XML_STRUCTURE = 32

	# Chyby interpretace
	SEMANTIC = 52 
	INCORRECT_TYPE = 53
	UNDEFINED_VARIABLE = 54
	UNINITIALISED_FRAME = 55
	UNDEFINED_VALUE = 56
	INCORRECT_VALUE = 57
	INVALID_STRING_OP = 58


def throwErr(reason: str, exitcode: ExitCode) -> None:
	""" Předčasné ukončení programu s návratovým kódem a vypsáním důvodu chyby """
	print("Error: {}".format(reason))
	sys.exit(exitcode)