from enums import ArgumentTypes, Frames, DataTypes
from typing import Any


class InstructionArgument():
    arg_type: ArgumentTypes


class Symbol(InstructionArgument):
    def __init__(self, data_type: DataTypes, value: Any):
        self.arg_type = ArgumentTypes.SYMBOL
        self.data_type = data_type
        self.value = value


class Variable(InstructionArgument):
    def __init__(self, frame: Frames, value: Any):
        self.arg_type = ArgumentTypes.VARIABLE
        self.frame = frame
        self.value = value


def is_symbol_variable(value: Any):
    return type(value) is Variable


class Type(InstructionArgument):
    def __init__(self, type: Any):
        self.arg_type = ArgumentTypes.TYPE
        self.type = type


class Label(InstructionArgument):
    def __init__(self, name: str):
        self.arg_type = ArgumentTypes.LABEL
        self.name = name
