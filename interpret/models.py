from enums import ArgumentTypes, Frames, DataTypes
from typing import Any


class InstructionArgument():
    arg_type: ArgumentTypes


class SymbolInstructionArgument(InstructionArgument):
    def __init__(self, data_type: DataTypes, value: Any):
        self.arg_type = ArgumentTypes.SYMBOL
        self.data_type = data_type
        self.value = value


class VariableInstructionArgument(InstructionArgument):
    def __init__(self, frame: Frames, value: Any):
        self.arg_type = ArgumentTypes.VARIABLE
        self.frame = frame
        self.value = value
