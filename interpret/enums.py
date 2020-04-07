from enum import IntEnum, Enum


class exitCodes(IntEnum):
    INVALID_ARGUMENTS = 10
    CANNOT_READ_FILE = 11
    INVALID_XML_FORMAT = 31
    INVALID_XML_STRUCT = 32


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
