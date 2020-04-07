import sys
from sys import stdin
from helper import exit_app
from enums import exitCodes
from argparse import ArgumentParser
from instruction_parser import InstructionsParser


def argument_parse_error(message: str):
    exit_app(exitCodes.INVALID_ARGUMENTS, message)


if '--help' in sys.argv and len(sys.argv) > 2:
    exit_app(exitCodes.INVALID_ARGUMENTS,
             '--help cannot be combined with another parameters')

parser = ArgumentParser()
parser.add_argument('--source', type=str)
parser.add_argument('--input', type=str)
parser.error = argument_parse_error

arguments = parser.parse_args()

if arguments.source is None and arguments.input is None:
    exit_app(exitCodes.INVALID_ARGUMENTS,
             '--source or --input or both parameters are required.')

xml_file = stdin
try:
    if arguments.source is not None:
        xml_file = open(arguments.source, 'r')
except Exception:
    exit_app(exitCodes.CANNOT_READ_FILE, 'Cannot open XML file.')

input_file = stdin
try:
    if arguments.input is not None:
        input_file = open(arguments.input, 'r')
except Exception:
    exit_app(exitCodes.CANNOT_READ_FILE, 'Cannot open inputs file')

instructions = InstructionsParser.parse_file(xml_file)

print(instructions)

for instruction in instructions.values():
    print(instruction)
    print(instruction.expectedArgTypes)
    print(instruction.args)
