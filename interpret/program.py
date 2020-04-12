from typing import List, IO, Dict
from models import Symbol, Variable, is_symbol_variable
from enums import Frames, exitCodes
from helper import exit_app
import instructions as instrs
from sys import stdin
from stats import Stats


class Program():
    def __init__(self, instructions: List, data_input: IO, stats: Stats):
        self.input = data_input
        self.instruction_pointer = 0
        self.GF: Dict[str, Symbol] = dict()
        self.TF: Dict[str, Symbol] = None
        self.LFStack: List[Dict[str, Symbol]] = list()
        self.dataStack: List[Symbol] = list()
        self.callStack: List[int] = list()
        self.exit_code = 0
        self.stats = stats

        # <label, instructionPointerPosition>
        self.labels: Dict[str, int] = dict()
        self.instructions: List[instrs.InstructionBase] = list()

        for instruction in instructions:
            if type(instruction) is instrs.Label:
                if instruction.name.name in self.labels:
                    exit_app(exitCodes.SEMANTIC_ERROR,
                             'Detected label redefinition.', True)

                self.labels.update(
                    {instruction.name.name: len(self.instructions)})
            else:
                self.instructions.append(instruction)

    def run(self):
        while len(self.instructions) > self.instruction_pointer:
            instruction = self.instructions[self.instruction_pointer]
            self.instruction_pointer += 1
            instruction.execute(self)

            if self.stats is not None:
                self.stats.increment_insts()
                self.stats.increment_vars(self.GF, self.LFStack, self.TF)

    def var_exists(self, var: Variable):
        if var.frame == Frames.GLOBAL:
            return var.value in self.GF
        elif var.frame == Frames.TEMPORARY:
            if self.TF is None:
                exit_app(exitCodes.INVALID_FRAME,
                         'Temporary frame is unitialized', True)

            return var.value in self.TF
        elif var.frame == Frames.LOCAL:
            if len(self.LFStack) == 0:
                exit_app(exitCodes.INVALID_FRAME,
                         'Local frame stack is empty.', True)
            return var.value in self.LFStack[-1]

    def var_set(self, opcode: str, var: Variable, value: Symbol):
        if not self.var_exists(var):
            exit_app(exitCodes.UNDEFINED_VARIABLE,
                     '{}\nVariable {} not exists'.format(opcode, var.value),
                     True)

        if var.frame == Frames.GLOBAL:
            self.GF[var.value] = value
        elif var.frame == Frames.LOCAL:
            self.LFStack[-1][var.value] = value
        elif var.frame == Frames.TEMPORARY:
            self.TF[var.value] = value

    def var_get(self, opcode: str, var: Variable) -> Symbol:
        if not self.var_exists(var):
            exit_app(exitCodes.UNDEFINED_VARIABLE,
                     '{}\nVariable {} not exists'.format(opcode, var.value),
                     True)

        if var.frame == Frames.TEMPORARY:
            return self.TF[var.value]
        elif var.frame == Frames.GLOBAL:
            return self.GF[var.value]
        elif var.frame == Frames.LOCAL:
            return self.LFStack[-1][var.value]

    def get_symb(self, opcode: str, symb: Symbol or Variable,
                 required_value: bool = False):
        result = symb
        if is_symbol_variable(symb):
            result = self.var_get(opcode, symb)

        if required_value and result is None:
            exit_app(exitCodes.UNDEFINED_VALUE,
                     '{}\nSymbol or variable is undefined.'.format(opcode))

        return result

    def exit(self, code: int):
        self.instruction_pointer = len(self.instructions)
        self.exit_code = code

    def get_state(self):
        return "\n".join([
            "Input type: {}".format(
                'stdin' if self.input == stdin else 'file'),
            "IP: {}".format(self.instruction_pointer),
            "GlobalFrame: {}".format(self.GF),
            "LocalFrame: {}".format(self.LFStack),
            "TemporaryFrame: {}".format(self.TF),
            "DataStack: {}".format(self.dataStack),
            "CallStack: {}".format(self.callStack),
            "Labels: {}".format(self.labels)
        ])
