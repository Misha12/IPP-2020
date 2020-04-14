from sys import stderr, stdout
from models import Symbol
from enums import DataTypes, exitCodes
from typing import List


def exit_app(code: int, message: str = '', use_stderr: bool = False):
    print(message, file=stderr if use_stderr else stdout)
    exit(int(code.value))


def validate_math_symbols(opcode: str, symb1: Symbol,
                          symb2: Symbol):
    types = [DataTypes.FLOAT, DataTypes.INT]

    if not symb1.one_of_types(types):
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Incomatible type in second operand at instruction {}.'
                 .format(opcode) + ' Expected: int or float', True)

    if not symb2.one_of_types(types):
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Incomatible type in first operand at instruction {}.'
                 .format(opcode) + ' Expected: int or float', True)

    if not symb1.equal_type(symb2.data_type) and\
            not symb1.is_nil() and not symb2.is_nil():
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Data types at instruction {} must be same.'
                 .format(opcode), True)


def validate_comparable_symbols(opcode: str, symb1: Symbol,
                                symb2: Symbol, allowedTypes: List[DataTypes]):

    if not symb1.one_of_types(allowedTypes):
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Incomatible type in second operand at instruction {}.'
                 .format(opcode), True)

    if not symb2.one_of_types(allowedTypes):
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Incomatible type in second operand at instruction {}.'
                 .format(opcode), True)

    if not symb1.equal_type(symb2.data_type) and not symb1.is_nil() and\
            not symb2.is_nil():
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Data types must be same.', True)
