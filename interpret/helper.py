from sys import stderr, stdout
from models import Symbol
from enums import DataTypes, exitCodes
from typing import List


def exit_app(code: int, message: str = '', use_stderr: bool = False):
    print(message, file=stderr if use_stderr else stdout)
    exit(int(code.value))


def validate_math_symbols(opcode: str, symb1: Symbol,
                          symb2: Symbol):
    if symb1.data_type != DataTypes.INT and \
            symb1.data_type != DataTypes.FLOAT:
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Incomatible type in second operand at instruction {}.'
                 .format(opcode) + ' Expected: int or float', True)

    if symb2.data_type != DataTypes.INT and\
            symb2.data_type != DataTypes.FLOAT:
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Incomatible type in first operand at instruction {}.'
                 .format(opcode) + ' Expected: int or float', True)

    if symb1.data_type != symb2.data_type and\
            symb1.data_type != DataTypes.NIL and\
            symb2.data_type != DataTypes.NIL:
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Data types at instruction {} must be same.'
                 .format(opcode), True)


def validate_comparable_symbols(opcode: str, symb1: Symbol,
                                symb2: Symbol, allowedTypes: List[DataTypes]):

    if not any(symb1.data_type == t for t in allowedTypes):
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Incomatible type in second operand at instruction {}.'
                 .format(opcode), True)

    if not any(symb2.data_type == t for t in allowedTypes):
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Incomatible type in second operand at instruction {}.'
                 .format(opcode), True)

    if symb1.data_type != symb2.data_type and\
        symb1.data_type != DataTypes.NIL and\
            symb2.data_type != DataTypes.NIL:
        exit_app(exitCodes.INVALID_DATA_TYPE,
                 'Data types must be same.', True)
