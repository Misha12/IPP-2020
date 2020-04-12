from enum import IntEnum, Enum


class exitCodes(IntEnum):
    INVALID_ARGUMENTS = 10
    CANNOT_READ_FILE = 11
    CANNOT_WRITE_FILE = 12
    INVALID_XML_FORMAT = 31
    INVALID_XML_STRUCT = 32
    SEMANTIC_ERROR = 52
    INVALID_DATA_TYPE = 53
    UNDEFINED_VARIABLE = 54
    INVALID_FRAME = 55
    UNDEFINED_VALUE = 56
    INVALID_OPERAND_VALUE = 57
    INVALID_STRING_OPERATION = 58


class ArgumentTypes(Enum):
    VARIABLE = 'var'
    SYMBOL = 'symb'
    LABEL = 'label'
    TYPE = 'type'


class Frames(Enum):
    GLOBAL = 'GF'
    LOCAL = 'LF'
    TEMPORARY = 'TF'


class DataTypes(Enum):
    NIL = 'nil'
    INT = 'int'
    BOOL = 'bool'
    STRING = 'string'
    FLOAT = 'float'
