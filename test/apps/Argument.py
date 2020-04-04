import re
from Common import throwErr, ExitCode
from Types import Label, Nil, Variable, Scope
from typing import Any, List
from xml.etree.ElementTree import Element

# Regex pravidlo pro kontrolu správnosti názvu proměnných
RegexVar = re.compile("^[_\\-\\$&\\%\\*!\\?a-zA-Z][_\\-\\$&\\%\\*!\\?\\w]*$")

# Regex pravidlo pro kontrolu správnosti formátu řetězců
RegexString = re.compile("^([^#\\\\]|\\\\\\d{3})*$")

def ParseString(rawStr: str) -> str:
	""" Převod řetězce z XML reprezentace do python typu str """
	# Rozdělit řetězec podle zpětných lomítek.
	# První tři znaky převést na písmena na symbol a řetězec znovu poskládat
	parts = rawStr.split("\\")
	finalStr = parts[0]
	del parts[0]
	
	for part in parts:
		finalStr += chr(int(part[:3]))
		finalStr += part[3:]
	
	return finalStr

def ParseInstructionArguments(XMLinstrNode: Element) -> List:
	""" Získání argumentů z XML elementu instrukce do seznamu argumentů """
	args: List = []
	XMLarg1 = XMLinstrNode.findall("arg1")
	XMLarg2 = XMLinstrNode.findall("arg2")
	XMLarg3 = XMLinstrNode.findall("arg3")
	
	# Argumenty musí být za sebou
	if len(XMLarg3) > 0 and (len(XMLarg2) == 0 or len(XMLarg1) == 0):
		throwErr("Third argument is present but first or second is missing", ExitCode.XML_STRUCTURE)
	elif len(XMLarg2) > 0 and len(XMLarg1) == 0:
		throwErr("Second argument is present but first is missing", ExitCode.XML_STRUCTURE)
	
	if len(XMLarg1) == 1:
		args.append(ParseXMLArgument(XMLarg1[0]))
	elif len(XMLarg1) > 1:
		throwErr("Found multiple first arguments", ExitCode.XML_STRUCTURE)
	
	if len(XMLarg2) == 1:
		args.append(ParseXMLArgument(XMLarg2[0]))
	elif len(XMLarg2) > 1:
		throwErr("Found multiple second arguments", ExitCode.XML_STRUCTURE)
	
	if len(XMLarg3) == 1:
		args.append(ParseXMLArgument(XMLarg3[0]))
	elif len(XMLarg3) > 1:
		throwErr("Found multiple third arguments", ExitCode.XML_STRUCTURE)
	
	return args

def ParseXMLArgument(XMLnode: Element) -> Any:
	""" Získání hodnoty z XML elementu argumentu """
	argType = XMLnode.get("type")
	
	# Hodnota argumentu
	value = XMLnode.text
	if value == None: value = ""
	
	# Získat hodnotu podle typu argumentu
	if argType == "type": # Typ
		if value == "int": return int
		if value == "float": return float
		elif value == "string": return str
		elif value == "bool": return bool
	elif argType == "label": # Návěští
		if RegexVar.match(value): return Label(value)
	elif argType == "var": # Proměnná
		valSplit = value.split("@", 1)
		if len(valSplit) == 2:
			scope = None
			if valSplit[0] == "GF": scope = Scope.GLOBAL
			elif valSplit[0] == "LF": scope = Scope.LOCAL
			elif valSplit[0] == "TF": scope = Scope.TEMP
			
			if scope != None and RegexVar.match(valSplit[1]): 
				return Variable(scope, valSplit[1])
	elif argType == "int": # Číslo
		try: return int(value)
		except ValueError: pass
	elif argType == "float": # Float rozšíření
		try: return float.fromhex(value)
		except ValueError: pass
	elif argType == "string": # Řetězec
		if RegexString.match(value): return ParseString(value)
	elif argType == "bool": # Boolean
		if value == "true": return True
		elif value == "false": return False
	elif argType == "nil": # Nil
		if value == "nil": return Nil()
	else:
		throwErr("Argument type is missing or invalid", ExitCode.XML_STRUCTURE)

	# Neznámý typ nebo nevalidní hodnota typu
	throwErr(f"Argument \"{argType}\" contains invalid value: {value}", ExitCode.XML_STRUCTURE)