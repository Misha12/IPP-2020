from typing import List, Dict
from enums import ArgumentTypes, exitCodes
from helper import exit_app


class InstructionBase():
    expectedArgTypes = []

    def __init__(self, args: List[Dict]):
        if len(self.expectedArgTypes) != len(args):
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Invalid count of arguments')

        self.args = args

    def execute(self):
        pass


class Move(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE, ArgumentTypes.SYMBOL]


class Defvar(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE]

    pass


OPCODE_TO_CLASS_MAP = {
    # Prace s ramci, volani funkci
    "MOVE": Move,
    "DEFVAR": Defvar
}
