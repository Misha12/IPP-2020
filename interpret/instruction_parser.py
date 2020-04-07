from typing import IO, Dict, List
import instructions
from xml.etree.ElementTree import parse as parse_xml, ParseError, Element
from helper import exit_app
from enums import exitCodes, ArgumentTypes, Frames, DataTypes
import re
from models import (InstructionArgument, SymbolInstructionArgument,
                    VariableInstructionArgument)


class InstructionsParser():

    @staticmethod
    def parse_file(file: IO) -> Dict[int, instructions.InstructionBase]:
        try:
            return InstructionsParser.parse(file)
        except ParseError:
            exit_app(exitCodes.INVALID_XML_FORMAT, 'Invalid XML format.', True)

    @staticmethod
    def parse(file: IO) -> Dict[int, instructions.InstructionBase]:
        """ Nacitani XML dat a jejich rozbiti do struktur."""

        xml_data = parse_xml(file).getroot()

        if xml_data.tag != 'program':
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Invalid XML root Element. Expected program', True)

        if 'language' not in xml_data.attrib.get('language') != 'IPPcode20':
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Invalid XML structure. Expected language IPPCode20',
                     True)

        result: Dict[int, instructions.InstructionBase] = dict()
        for element in list(xml_data):
            if element.tag != 'instruction':
                exit_app(exitCodes.INVALID_XML_STRUCT,
                         'Unknown element in program element.', True)

            try:
                order = int(element.attrib.get('order'))

                if order <= 0:
                    exit_app(exitCodes.INVALID_XML_STRUCT,
                             'Negative instructions order', True)
            except ValueError:
                exit_app(exitCodes.INVALID_XML_STRUCT,
                         'Order attribute must be integer', True)
            except TypeError:
                exit_app(exitCodes.INVALID_XML_STRUCT,
                         'Order element not found.', True)

            if order in result:
                exit_app(exitCodes.INVALID_XML_STRUCT,
                         'Found element with same order.', True)

            result[order] = InstructionsParser.parse_instruction(
                element, order)

        return dict(sorted(result.items()))

    @staticmethod
    def parse_instruction(element: Element, order: int) -> \
            instructions.InstructionBase:
        opcode = element.get('opcode')

        if opcode is None or len(opcode) == 0:
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Missing element at {}'.format(order), True)

        opcode = opcode.upper()
        if opcode not in instructions.OPCODE_TO_CLASS_MAP:
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Unknown opcode. ({})'.format(opcode), True)

        args = InstructionsParser.parse_arguments(element)
        return instructions.OPCODE_TO_CLASS_MAP[opcode](args)

    @staticmethod
    def parse_arguments(element: Element) -> List[InstructionArgument]:
        arg1 = element.findall('arg1')
        arg2 = element.findall('arg2')
        arg3 = element.findall('arg3')

        if len(arg1) > 1:
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Multiple elements named arg1', True)
        elif len(arg2) > 1:
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Multiple elements named arg2', True)
        elif len(arg3) > 1:
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Multiple elements named arg3', True)

        if len(arg3) > 0 and (len(arg1) == 0 or len(arg2) == 0):
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Third argument was set, but first or second missing.',
                     True)
        if len(arg2) > 0 and len(arg1) == 0:
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Second argument was set, but first missing.', True)

        args = list()

        if len(arg1) > 0:
            args.append(InstructionsParser.parse_argument(arg1[0]))
        if len(arg2) > 0:
            args.append(InstructionsParser.parse_argument(arg2[0]))
        if len(arg3) > 0:
            args.append(InstructionsParser.parse_argument(arg3[0]))

        return args

    @staticmethod
    def parse_argument(arg: Element) -> InstructionArgument:
        arg_type = arg.attrib.get('type')
        arg_value = arg.text if arg.text is not None else ''

        if arg_type == ArgumentTypes.VARIABLE.value:
            variable_parts = arg_value.split('@', 1)

            if len(variable_parts) == 2:
                InstructionsParser.validate_scope(variable_parts[0])
                InstructionsParser.validate_variable(variable_parts[1])

                if variable_parts[0] == 'GF':
                    return VariableInstructionArgument(Frames.GLOBAL,
                                                       variable_parts[1])
                elif variable_parts[0] == 'TF':
                    return VariableInstructionArgument(Frames.TEMPORARY,
                                                       variable_parts[1])
                elif variable_parts[0] == 'LF':
                    return VariableInstructionArgument(Frames.LOCAL,
                                                       variable_parts[1])
            else:
                exit_app(exitCodes.INVALID_XML_STRUCT,
                         'Invalid variable. ({})'.format(arg_value), True)
        elif arg_type == 'nil':
            if arg_value != 'nil':
                exit_app(exitCodes.INVALID_XML_STRUCT,
                         'Invalid value of nil. ({})'.format(arg_value), True)

            return SymbolInstructionArgument(DataTypes.NIL, None)
        elif arg_type == 'int':
            try:
                return SymbolInstructionArgument(DataTypes.INT, int(arg_value))
            except ValueError:
                exit_app(exitCodes.INVALID_XML_STRUCT,
                         'Invalid int value. ({})'.format(arg_value), True)
        elif arg_type == 'bool':
            if arg_value == 'true':
                return SymbolInstructionArgument(DataTypes.BOOL, True)
            elif arg_value == 'false':
                return SymbolInstructionArgument(DataTypes.BOOL, False)
            else:
                exit_app(exitCodes.INVALID_XML_STRUCT,
                         'Invalid boolean value. ({})'.format(arg_value), True)
        elif arg_type == 'string':
            if re.compile('.*#.*').match(arg_value):
                exit_app(exitCodes.INVALID_XML_STRUCT,
                         'Text cannot contains #.', True)

            fixed_string = InstructionsParser.fix_string(arg_value)
            return SymbolInstructionArgument(DataTypes.STRING, fixed_string)
        else:
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Unknown argument type. ({})'.format(arg_type), True)

    @staticmethod
    def validate_scope(scope: str):
        if scope != Frames.GLOBAL.value and scope != Frames.LOCAL.value and \
                scope != Frames.TEMPORARY.value:
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Invalid scope. ({})'.format(scope), True)

    @staticmethod
    def validate_variable(name: str):
        if re.compile("^[^(LGT)F][_\\-$&%*!?a-zA-Z]\\S*$").match(name) is None:
            exit_app(exitCodes.INVALID_XML_STRUCT,
                     'Invalid variable name. ({})'.format(name), True)

    @staticmethod
    def fix_string(value: str) -> str:
        result: List[str] = list()

        splitedParts = value.split('\\')
        result.append(splitedParts[0])

        number_regex = re.compile("\\d{3}")

        for item in splitedParts[1:]:
            number_matched = number_regex.match(item[:3])

            if not number_matched:
                exit_app(exitCodes.INVALID_XML_STRUCT,
                         'Invalid hexadecimal escape.', True)

            result.append(chr(int(item[:3])))
            result.append(item[3:])

        return str().join(result)
