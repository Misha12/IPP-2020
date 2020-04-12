from typing import List
from enums import ArgumentTypes, exitCodes, Frames, DataTypes
from helper import exit_app
from program import Program
from models import InstructionArgument, Symbol, Label as LabelModel
from sys import stdin, stderr


class InstructionBase():
    expectedArgTypes = []

    def __init__(self, args: List[InstructionArgument], opcode: str):
        if len(self.expectedArgTypes) != len(args):
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Invalid count of arguments at opcode {}'.format(opcode),
                     True)

        self.opcode = opcode
        self.args = args

    def execute(self, program: Program):
        raise NotImplementedError


# 6.4.1 Prace s ramci, volani funkci
class Move(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        symb = program.get_symb('MOVE', self.args[1])
        program.var_set('MOVE', self.args[0], symb)


class Createframe(InstructionBase):
    def execute(self, program: Program):
        program.TF = dict()


class Pushframe(InstructionBase):
    def execute(self, program: Program):
        if program.TF is None:
            exit_app(exitCodes.INVALID_FRAME,
                     'PUSHFRAME\nInvalid access to undefined temporary frame.',
                     True)

        program.LFStack.append(program.TF)
        program.TF = None


class Popframe(InstructionBase):
    def execute(self, program: Program):
        if len(program.LFStack) == 0:
            exit_app(exitCodes.INVALID_FRAME,
                     'POPFRAME\nNo available local frame.', True)

        program.TF = program.LFStack.pop()


class Defvar(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE]

    def execute(self, program: Program):
        arg = self.args[0]

        if program.var_exists(arg):
            exit_app(exitCodes.SEMANTIC_ERROR,
                     'DEFVAR\nVariable {} now exists. Cannot redefine.', True)

        if arg.frame == Frames.GLOBAL:
            program.GF.update({arg.value: None})
        elif arg.frame == Frames.LOCAL:
            program.LFStack[-1].update({arg.value: None})
        elif arg.frame == Frames.TEMPORARY:
            if program.TF is None:
                exit_app(exitCodes.INVALID_FRAME,
                         'DEFVAR\nTemporary frame is not defined.', True)

            program.TF.update({arg.value: None})


class Return(InstructionBase):
    def execute(self, program: Program):
        if len(program.callStack) == 0:
            exit_app(exitCodes.UNDEFINED_VALUE,
                     'RETURN\nEmpty call stack.', True)
        program.instruction_pointer = program.callStack.pop()


# Prace s datovym zasobnikem
class PushS(InstructionBase):
    expectedArgTypes = [ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        symb = program.get_symb('PUSHS', self.args[0], True)
        program.dataStack.append(symb)


class PopS(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE]

    def execute(self, program: Program):
        if len(program.dataStack) == 0:
            exit_app(exitCodes.UNDEFINED_VALUE,
                     'POPS\nInstruction {}. Data Stack is empty.'.format(
                         self.opcode), True)

        var = self.args[0]
        program.var_set('POPS', var, program.dataStack.pop())


# 6.4.3 Aritmeticke, relacni, booleovske a konverzni instrukce
class MathInstructionBase(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE,
                        ArgumentTypes.SYMBOL,
                        ArgumentTypes.SYMBOL]

    def compute(self, symb1: Symbol, symb2: Symbol):
        raise NotImplementedError

    def execute(self, program: Program):
        symb1 = program.get_symb(self.opcode, self.args[1])
        symb2 = program.get_symb(self.opcode, self.args[2])

        if symb1.data_type != DataTypes.INT:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'Incomatible type in second operand at instruction {}.'
                     .format(self.opcode) + ' Expected: int', True)

        if symb2.data_type != DataTypes.INT:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'Incomatible type in first operand at instruction {}.'
                     .format(self.opcode) + ' Expected: int', True)

        if symb1.data_type != symb1.data_type and\
                symb1.data_type != DataTypes.NIL and\
                symb2.data_type != DataTypes.NIL:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'Data types must be same.', True)

        result = self.compute(symb1, symb2)
        program.var_set(self.opcode, self.args[0], result)


class Add(MathInstructionBase):
    def compute(self, symb1: Symbol, symb2: Symbol):
        return Symbol(symb1.data_type, symb1.value + symb2.value)


class Sub(MathInstructionBase):
    def compute(self, symb1: Symbol, symb2: Symbol):
        return Symbol(symb1.data_type, symb1.value - symb2.value)


class Mul(MathInstructionBase):
    def compute(self, symb1: Symbol, symb2: Symbol):
        return Symbol(symb1.data_type, symb1.value * symb2.value)


class IDiv(MathInstructionBase):
    def compute(self, symb1: Symbol, symb2: Symbol):
        if symb2.value == 0:
            exit_app(exitCodes.INVALID_OPERAND_VALUE,
                     'Detected zero division.', True)

        return Symbol(DataTypes.INT, symb1.value // symb2.value)


class ComparableInstruction(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE,
                        ArgumentTypes.SYMBOL,
                        ArgumentTypes.SYMBOL]

    allowedTypes = [DataTypes.INT, DataTypes.BOOL, DataTypes.STRING]

    def compare(self, symb1: Symbol, symb2: Symbol) -> bool:
        raise NotImplementedError

    def execute(self, program: Program):
        symb1 = program.get_symb(self.opcode, self.args[1])
        symb2 = program.get_symb(self.opcode, self.args[2])

        if not any(symb1.data_type == t for t in self.allowedTypes):
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'Incomatible type in second operand at instruction {}.'
                     .format(self.opcode) + ' Expected: int, bool, string',
                     True)

        if not any(symb2.data_type == t for t in self.allowedTypes):
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'Incomatible type in second operand at instruction {}.'
                     .format(self.opcode) + ' Expected: int, bool, string',
                     True)

        if symb1.data_type != symb2.data_type and\
                symb1.data_type != DataTypes.NIL and\
                symb2.data_type != DataTypes.NIL:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'Data types must be same.', True)

        result = Symbol(DataTypes.BOOL, self.compare(symb1, symb2))
        program.var_set(self.opcode, self.args[0], result)


class Lt(ComparableInstruction):
    def compare(self, symb1: Symbol, symb2: Symbol) -> bool:
        return symb1.value < symb2.value


class Gt(ComparableInstruction):
    def compare(self, symb1: Symbol, symb2: Symbol) -> bool:
        return symb1.value > symb2.value


class Eq(ComparableInstruction):
    allowedTypes = [DataTypes.INT, DataTypes.BOOL,
                    DataTypes.STRING, DataTypes.NIL]

    def compare(self, symb1: Symbol, symb2: Symbol) -> bool:
        if symb1.data_type == DataTypes.NIL:
            return symb2.data_type == DataTypes.NIL
        elif symb2.data_type == DataTypes.NIL:
            return False

        return symb1.value == symb2.value


class And(ComparableInstruction):
    allowedTypes = [DataTypes.BOOL]

    def compare(self, symb1: Symbol, symb2: Symbol) -> bool:
        return symb1.value and symb2.value


class Or(ComparableInstruction):
    allowedTypes = [DataTypes.BOOL]

    def compare(self, symb1: Symbol, symb2: Symbol) -> bool:
        return symb1.value or symb2.value


class Not(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        symb = program.get_symb('NOT', self.args[1])

        if symb.data_type != DataTypes.BOOL:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'NOT\nInvalid data type. Expected: bool. Have: ({})'
                     .format(symb.data_type.value), True)

        result = Symbol(DataTypes.BOOL, not symb.value)
        program.var_set('NOT', self.args[0], result)


class Int2Char(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        var = self.args[0]
        symb = self.args[1]

        symb_val = program.get_symb('INT2CHAR', symb).value

        try:
            char = chr(symb_val)
            program.var_set('INT2CHAR', var, Symbol(DataTypes.STRING, char))
        except ValueError:
            exit_app(exitCodes.INVALID_STRING_OPERATION,
                     'INT2CHAR\nInvalid int to char conversion value. {}'
                     .format(symb_val))
        except TypeError:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'INT2CHAR\nInvalid data type.' +
                     ' Expected INT in second parameter.')


class Stri2Int(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE,
                        ArgumentTypes.SYMBOL, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        string = program.get_symb('STRI2INT', self.args[1])
        index = program.get_symb('STRI2INT', self.args[2])

        if string.data_type != DataTypes.STRING or\
                index.data_type != DataTypes.INT:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'STRI2INT\nInvalid data type. Expected: string and int.' +
                     ' Have: {} and {}'.format(string.data_type.value,
                                               index.data_type.value), True)

        try:
            ordinary = ord(string.value[index.value])
            program.var_set('STRI2INT', self.args[0], Symbol(DataTypes.INT,
                                                             ordinary))
        except IndexError:
            exit_app(exitCodes.INVALID_STRING_OPERATION,
                     'String is out of range.', True)


# 6.4.4 Vstupne-vystupni instrukce
class Read(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE, ArgumentTypes.TYPE]

    def execute(self, program: Program):
        try:
            if program.input == stdin:
                line = input()
            else:
                line = program.input.readline().rstrip()
        except Exception:
            line = None
        
        arg_type = self.args[1]

        if line is None:
            program.var_set('READ', self.args[0], Symbol(DataTypes.NIL, None))
        elif arg_type.type is bool:
            program.var_set('READ', self.args[0],
                            Symbol(DataTypes.BOOL, line.lower() == 'true'))
        elif arg_type.type is str:
            program.var_set('READ', self.args[0], Symbol(DataTypes.STRING,
                                                         line))
        elif arg_type.type is int:
            try:
                temp_val = int(line)
                if str(temp_val) != line:
                    program.var_set(
                        'READ', self.args[0], Symbol(DataTypes.NIL, None))
                else:
                    program.var_set('READ', self.args[0], Symbol(
                        DataTypes.INT, temp_val))
            except ValueError:
                program.var_set(
                    'READ', self.args[0], Symbol(DataTypes.NIL, None))


class Write(InstructionBase):
    expectedArgTypes = [ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        symb = program.get_symb('WRITE', self.args[0], True)

        if symb.data_type == DataTypes.NIL:
            print('', end='')
        elif symb.data_type == DataTypes.BOOL:
            if symb.value:
                print('true', end='')
            else:
                print('false', end='')
        else:
            print(symb.value, end='')


# 6.4.5 Prace s retezci
class Concat(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE,
                        ArgumentTypes.SYMBOL, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        symb1 = program.get_symb('CONCAT', self.args[1], True)

        if symb1.data_type != DataTypes.STRING:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'CONCAT\nInvalid type at second operand.', True)

        symb2 = program.get_symb('CONCAT', self.args[2], True)

        if symb2.data_type != DataTypes.STRING:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'CONCAT\nInvalid type at third operand.', True)

        result = Symbol(DataTypes.STRING, symb1.value + symb2.value)
        program.var_set('CONCAT', self.args[0], result)


class Strlen(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        string = program.get_symb('STRLEN', self.args[1], True)

        if string.data_type != DataTypes.STRING:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'STRLEN\nExpected string', True)

        string_length = Symbol(DataTypes.INT, len(string.value))
        program.var_set('STRLEN', self.args[0], string_length)


class Getchar(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE,
                        ArgumentTypes.SYMBOL, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        string = program.get_symb('GETCHAR', self.args[1], True)
        index = program.get_symb('GETCHAR', self.args[2], True)

        if string.data_type != DataTypes.STRING or\
                index.data_type != DataTypes.INT:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'GETCHAR\nExpected string and int', True)

        try:
            result = Symbol(DataTypes.STRING, string.value[index.value])
            program.var_set('GETCHAR', self.args[0], result)
        except IndexError:
            exit_app(exitCodes.INVALID_STRING_OPERATION,
                     'GETCHAR\nIndex out of range.', True)


class Setchar(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE,
                        ArgumentTypes.SYMBOL, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        variable = program.var_get('SETCHAR', self.args[0])
        index = program.get_symb('SETCHAR', self.args[1])
        toModify = program.get_symb('SETCHAR', self.args[2])

        if index.data_type != DataTypes.INT or\
                variable.data_type != DataTypes.STRING or\
                toModify.data_type != DataTypes.STRING:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'SETCHAR\nExpected: string variable, int, string', True)

        if len(toModify.value) == 0 or index.value >= len(variable.value):
            exit_app(exitCodes.INVALID_STRING_OPERATION,
                     'SETCHAR\nZero length of to modify characters.', True)

        try:
            result = "{}{}{}".format(variable.value[:index.value],
                                     toModify.value[0],
                                     variable.value[index.value + 1:])
            program.var_set('SETCHAR', self.args[0],
                            Symbol(DataTypes.STRING, result))
        except IndexError:
            exit_app(exitCodes.INVALID_STRING_OPERATION,
                     'SETCHAR\nIndex is out of range.', True)


# 6.4.6 Prace s typy
class Type(InstructionBase):
    expectedArgTypes = [ArgumentTypes.VARIABLE, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        symb = program.get_symb('TYPE', self.args[1])

        if symb is None:
            program.var_set('TYPE', self.args[0], Symbol(DataTypes.STRING, ''))
        else:
            program.var_set('TYPE', self.args[0], Symbol(
                DataTypes.STRING, symb.data_type.value))


# 6.4.7 Instrukce pro rizeni toku programu
class Label(InstructionBase):
    expectedArgTypes = [ArgumentTypes.LABEL]

    def __init__(self, args: List, opcode: str):
        InstructionBase.__init__(self, args, opcode)
        self.name = args[0]


class Jump(InstructionBase):
    expectedArgTypes = [ArgumentTypes.LABEL]

    def execute(self, program: Program):
        label: LabelModel = self.args[0]
        if label.name not in program.labels:
            exit_app(exitCodes.SEMANTIC_ERROR,
                     'Undefined label to jump. ({})'.format(label.name), True)

        program.instruction_pointer = program.labels[label.name]


class Call(Jump):
    def execute(self, program: Program):
        program.callStack.append(program.instruction_pointer)
        Jump.execute(self, program)


class Jumpifeq(Jump):
    expectedArgTypes = [ArgumentTypes.LABEL,
                        ArgumentTypes.SYMBOL, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        symb1 = program.get_symb('JUMPIFEQ', self.args[1])
        symb2 = program.get_symb('JUMPIFEQ', self.args[2])

        if symb1.data_type != symb2.data_type:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'JUMPIFEQ\nOperands must have same type.', True)
        elif symb1.data_type == DataTypes.NIL or symb1.value == symb2.value:
            Jump.execute(self, program)


class Jumpifneq(Jump):
    expectedArgTypes = [ArgumentTypes.LABEL,
                        ArgumentTypes.SYMBOL, ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        symb1 = program.get_symb('JUMPNIFEQ', self.args[1])
        symb2 = program.get_symb('JUMPNIFEQ', self.args[2])

        if symb1.data_type != symb2.data_type:
            exit_app(exitCodes.INVALID_DATA_TYPE,
                     'JUMPNIFEQ\nOperands must have same type.', True)
        elif symb1.data_type == DataTypes.NIL or symb1.value != symb2.value:
            Jump.execute(self, program)


class Exit(InstructionBase):
    expectedArgTypes = [ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        symb = program.get_symb('EXIT', self.args[0], True)

        if symb.data_type != DataTypes.INT:
            exit_app(exitCodes.INVALID_OPERAND_VALUE,
                     'EXIT\nInvalid exit code', True)
        elif symb.value < 0 or symb.value > 49:
            exit_app(exitCodes.INVALID_OPERAND_VALUE,
                     'EXIT\nInvalid exit code. Allowed range is <0; 49>.',
                     True)
        else:
            program.exit(symb.value)


# 6.4.8 Ladici instrukce
class DPrint(InstructionBase):
    expectedArgTypes = [ArgumentTypes.SYMBOL]

    def execute(self, program: Program):
        symb = program.get_symb('DPRINT', self.args[0])
        print(symb.value, file=stderr)


class Break(InstructionBase):
    def execute(self, program: Program):
        print(program.get_state(), file=stderr)


OPCODE_TO_CLASS_MAP = {
    # 6.4.1 Prace s ramci, volani funkci
    "MOVE": Move,
    "CREATEFRAME": Createframe,
    "PUSHFRAME": Pushframe,
    "POPFRAME": Popframe,
    "DEFVAR": Defvar,
    "CALL": Call,
    "RETURN": Return,

    # Prace s datvym zasobnikem
    "PUSHS": PushS,
    "POPS": PopS,

    # 6.4.3 Aritmeticke, relacni, booleovske a konverzni instrukce
    "ADD": Add,
    "SUB": Sub,
    "MUL": Mul,
    "IDIV": IDiv,
    "LT": Lt,
    "GT": Gt,
    "EQ": Eq,
    "AND": And,
    "OR": Or,
    "NOT": Not,
    "INT2CHAR": Int2Char,
    "STRI2INT": Stri2Int,

    # 6.4.4 Vstupne vystupni instrukce
    "READ": Read,
    "WRITE": Write,

    # 6.4.5 Prace s retezci
    "CONCAT": Concat,
    "STRLEN": Strlen,
    "GETCHAR": Getchar,
    "SETCHAR": Setchar,

    # 6.4.6 Prace s typy
    "TYPE": Type,

    # 6.4.7 Instrukce pro rizeni toku programu
    "LABEL": Label,
    "JUMP": Jump,
    "JUMPIFEQ": Jumpifeq,
    "JUMPIFNEQ": Jumpifneq,
    "EXIT": Exit,

    # 6.4.8 Ladici instrukce
    "DPRINT": DPrint,
    "BREAK": Break
}
