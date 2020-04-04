from sys import stderr, stdin, exit, modules
from xml.etree.ElementTree import Element
from typing import Tuple, Any, List, Union
from Types import Nil, Label, Scope, Variable, Symbol, IsSymbol
from Common import throwErr, ExitCode
from Argument import ParseInstructionArguments
from Program import Program

class Instruction:
	""" Reprezentace instrukce jazyka IPPcode19 """
	
	# Počet, typ a pořadí povinných argumentů
	argumentTypes = []

	def __init__(self, args: List):
		""" Při inicializaci se k instrukci přidají načtené argumenty z XML souboru """
		self.args = args

	def Run(self, data: Program) -> None:
		""" Spuštění dané instrukce (konrétní instrukce musí přetížit tuto metodu) """
		raise NotImplementedError

class Move(Instruction):
	""" Přidání hodnoty do proměnné """
	argumentTypes = [Variable, Symbol]

	def Run(self, data: Program) -> None:
		data.VariableSetValue(self.args[0], data.SymbolValue(self.args[1]))

class Createframe(Instruction):
	""" Inicializace dočasného rámce """
	def Run(self, data: Program) -> None:
		data.temporaryFrame = {}

class Pushframe(Instruction):
	""" Vložení dočasného rámce na zásobník lokálních rámců """
	def Run(self, data: Program) -> None:
		if data.temporaryFrame == None:
			throwErr("PUSHFRAME - Temporary frame is undefined", ExitCode.UNINITIALISED_FRAME)
		
		data.localFrameStack.append(data.temporaryFrame)
		data.temporaryFrame = None

class Popframe(Instruction):
	""" Vyjmutí lokálního rámce ze zásobníku a vložení do dočasného rámce """
	def Run(self, data: Program) -> None:
		if len(data.localFrameStack) == 0:
			throwErr("POPFRAME - Local frame is undefined", ExitCode.UNINITIALISED_FRAME)
		
		data.temporaryFrame = data.localFrameStack.pop()

class Defvar(Instruction):
	""" Definice proměnné """
	argumentTypes = [Variable]
	
	def Run(self, data: Program) -> None:
		# Proměnná musí existovat 
		if data.VariableExist(self.args[0]):
			throwErr("DEFVAR - Variable is already defined", ExitCode.SEMANTIC)
		
		if self.args[0].scope == Scope.GLOBAL:
			data.globalFrame[self.args[0].name] = None
		
		if self.args[0].scope == Scope.LOCAL:
			data.localFrameStack[-1][self.args[0].name] = None
		
		if self.args[0].scope == Scope.TEMP:
			data.temporaryFrame[self.args[0].name] = None

class Pushs(Instruction):
	""" Vložení hodnoty na datový zásobník """
	argumentTypes = [Symbol]
	
	def Run(self, data: Program) -> None:
		data.dataStack.append(data.SymbolValue(self.args[0]))

class Pops(Instruction):
	""" Vyjmutí hodnoty do proměnné z datového zásobníku """
	argumentTypes = [Variable]
	
	def Run(self, data: Program) -> None:
		if len(data.dataStack) == 0:
			throwErr("POPS - Data stack is empty", ExitCode.UNDEFINED_VALUE)
		
		data.VariableSetValue(self.args[0], data.dataStack.pop())

class ArithmeticInstruction(Instruction):
	""" Virtuální třída definující obecnou aritmetickou instrukci """
	argumentTypes = [Variable, Symbol, Symbol]

	# Povolené typy nad kterými lze provádět aritmetickou operaci
	arithmeticTypes = [int, float]
	
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		""" Provedení aritmetické operace """
		raise NotImplementedError

	def Run(self, data: Program) -> None:
		val1 = data.SymbolValue(self.args[1])
		val2 = data.SymbolValue(self.args[2])
		
		# Oba symboly musí být stejného typu a musí být jedním z povolených typů
		if type(val1) in self.arithmeticTypes and type(val2) in self.arithmeticTypes:
			if type(val1) == type(val2) or type(val1) is Nil or type(val2) is Nil:
				data.VariableSetValue(self.args[0], self.ArithmeticOp(val1, val2))
			else: throwErr("ARITHMETIC - Types must be equal", ExitCode.INCORRECT_TYPE)
		else:
			throwErr(f"ARITHMETIC - Incopatible types {type(val1)} and {type(val2)}", ExitCode.INCORRECT_TYPE)

class Add(ArithmeticInstruction):
	""" Aritmetický součet """
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		return value1 + value2

class Sub(ArithmeticInstruction):
	""" Aritmetický rozdíl """
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		return value1 - value2

class Mul(ArithmeticInstruction):
	""" Aritmetické násobení """
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		return value1 * value2

class Idiv(ArithmeticInstruction):
	""" Aritmetické dělení celého čísla """
	arithmeticTypes = [int]
	
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		if value2 == 0:
			throwErr("IDIV - Division by zero", ExitCode.INCORRECT_VALUE)
		
		return value1 // value2

class Div(ArithmeticInstruction):
	""" Aritmetické dělení jako číslo s plovoucí čárkou """
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		if value2 == 0:
			throwErr("DIV - Division by zero", ExitCode.INCORRECT_VALUE)
		
		return value1 / value2

class Lt(ArithmeticInstruction):
	""" Měnší """
	arithmeticTypes = [int, float, bool, str]
	
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		return value1 < value2

class Gt(Lt):
	""" Větší """
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		return value1 > value2

class Eq(Lt):
	""" Rovná se """
	arithmeticTypes = [int, float, bool, str, Nil]
	
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		# Typy se musí rovnat, jedinou vyjímkou je typ nil.
		# Pokud je jedním z typů nil, výsledkem je False.
		if type(value1) is Nil:
			return type(value2) is Nil
		elif type(value2) is Nil:
			return False
		
		return value1 == value2

class And(ArithmeticInstruction):
	""" Logické a """
	arithmeticTypes = [bool]
	
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		return value1 and value2

class Or(And):
	""" Logické nebo """
	def ArithmeticOp(self, value1: Symbol, value2: Symbol) -> Symbol:
		return value1 or value2

class Not(Instruction):
	""" Inverze (bere jen jeden sambol typu Boolean) """
	argumentTypes = [Variable, Symbol]
	
	def Run(self, data: Program) -> None:
		val = data.SymbolValue(self.args[1])
		
		if type(val) != bool:
			throwErr("NOT - argument must be type bool", ExitCode.INCORRECT_TYPE)
		
		data.VariableSetValue(self.args[0], not val)

class Int2char(Instruction):
	""" Převod čisla na unicode znak """
	argumentTypes = [Variable, Symbol]

	def Run(self, data: Program) -> None:
		try:
			data.VariableSetValue(self.args[0], chr(data.SymbolValue(self.args[1])))
		except ValueError:
			throwErr("INT2CHAR - INT must be in valid unicode range", ExitCode.INVALID_STRING_OP)
		except TypeError:
			throwErr("INT2CHAR - Expected INT as a type of the second argument", ExitCode.INCORRECT_TYPE)

class Stri2int(Instruction):
	""" Získání číselné reprezentaci znaku řetězce args(1) na indexu args(2) """
	argumentTypes = [Variable, Symbol, Symbol]
	
	def Run(self, data: Program) -> None:
		string = data.SymbolValue(self.args[1])
		index = data.SymbolValue(self.args[2])

		if type(string) is not str or type(index) is not int:
			throwErr("STRI2INT - Expected types STRING and INT", ExitCode.INCORRECT_TYPE)

		try: data.VariableSetValue(self.args[0], ord(string[index]))
		except IndexError:
			throwErr("STRI2INT - Index out of range", ExitCode.INVALID_STRING_OP)

class Int2float(Instruction):
	""" Převod celého čísla na číslo s plovoucí čárkou """
	argumentTypes = [Variable, Symbol]

	def Run(self, data: Program):
		val = data.SymbolValue(self.args[1])

		if type(val) is not int:
			throwErr("INT2FLOAT - Expected type INT", ExitCode.INCORRECT_TYPE)
		else: data.VariableSetValue(self.args[0], float(val))

class Float2int(Instruction):
	""" Převod čísla s plovoucí čárkou na celé číslo """
	argumentTypes = [Variable, Symbol]

	def Run(self, data: Program):
		val = data.SymbolValue(self.args[1])

		if type(val) is not float:
			throwErr("FLOAT2INT - Expected type FLOAT", ExitCode.INCORRECT_TYPE)
		else: data.VariableSetValue(self.args[0], int(val))

class Read(Instruction):
	""" Načíst ze vstupu hodnotu podle daného typu """
	argumentTypes = [Variable, type]
	
	def Run(self, data: Program) -> None:
		try:
			if data.readFile == stdin: receive = input()
			else: receive = data.readFile.readline().rstrip("\r\n")
		except:
			receive = ""
		
		# Pokus o převod na požadovaný typ, uložit výchozí hodnotu pokud se převod nezadřil
		if self.args[1] is float:
			try: receive = float.fromhex(receive)
			except ValueError: receive = float(0)
		elif self.args[1] is int:
			try: receive = int(receive)
			except ValueError: receive = 0
		elif self.args[1] is bool:
			receive = receive.strip().lower() == "true"
		
		data.VariableSetValue(self.args[0], receive)
	
class Write(Instruction):
	""" Vypsat na standartní výstup hodnotu """
	argumentTypes = [Symbol]

	def Run(self, data: Program) -> None:
		val = data.SymbolValue(self.args[0])
		
		if type(val) is bool:
			# Vypsat Boolean podle požadavků IPPcode19
			print("true" if val else "false", end='')
		elif type(val) is float:
			# Float musí být vypsát v hexadecimální reprezentaci
			print(val.hex(), end='')
		else:
			print(val, end='')

class Concat(Instruction):
	""" Spojení dvou řetězců """
	argumentTypes = [Variable, Symbol, Symbol]
	
	def Run(self, data: Program) -> None:
		str1 = data.SymbolValue(self.args[1])
		str2 = data.SymbolValue(self.args[2])

		if type(str1) is not str or type(str2) is not str:
			throwErr("CONCAT - Last two arguments must be STRING", ExitCode.INCORRECT_TYPE)

		data.VariableSetValue(self.args[0], f"{str1}{str2}")

class Strlen(Instruction):
	""" Zjistí délku řětězce """
	argumentTypes = [Variable, Symbol]
	
	def Run(self, data: Program) -> None:
		string = data.SymbolValue(self.args[1])
		
		if type(string) is not str:
			throwErr("STRLEN - Second argument must be STRING", ExitCode.INCORRECT_TYPE)
		
		data.VariableSetValue(self.args[0], len(string))

class Getchar(Instruction):
	""" Získání znaku řetězce args(1) na pozici args(2) """
	argumentTypes = [Variable, Symbol, Symbol]
	
	def Run(self, data: Program) -> None:
		string = data.SymbolValue(self.args[1])
		index = data.SymbolValue(self.args[2])

		if(type(string) is not str or type(index) is not int):
			throwErr("GETCHAR - Expected arguments types VAR, STRING, INT", ExitCode.INCORRECT_TYPE)
		
		try:
			data.VariableSetValue(self.args[0], string[index])
		except IndexError:
			throwErr("GETCHAR - Index out of range", ExitCode.INVALID_STRING_OP)

class Setchar(Instruction):
	""" Nahrazení znaku v proměnné args(0) na pozici args(1) za znak args(2) """
	argumentTypes = [Variable, Symbol, Symbol]
	
	def Run(self, data: Program) -> None:
		string = data.VariableGetValue(self.args[0])
		index = data.SymbolValue(self.args[1])
		char  = data.SymbolValue(self.args[2])

		# kontrola typů
		if(type(string) is not str or type(char) is not str or type(index) is not int):
			throwErr("SETCHAR - Expected arguments types VAR(STRING), STRING, INT", ExitCode.INCORRECT_TYPE)
		if len(char) == 0 or len(string) <= index:
			throwErr("SETCHAR - Index out of range", ExitCode.INVALID_STRING_OP)
		
		# Pokus o změnu znaku
		try:
			string = f"{string[:index]}{char[0]}{string[index+1:]}" 
		except IndexError:
			throwErr("SETCHAR - Index out of range", ExitCode.INVALID_STRING_OP)
		
		data.VariableSetValue(self.args[0], string)

class Type(Instruction):
	""" Získání typu symbolu """
	argumentTypes = [Variable, Symbol]
	
	def Run(self, data: Program) -> None:
		if type(self.args[1]) is Variable:
			val = data.VariableGetValue(self.args[1], False)
		else:
			val = data.SymbolValue(self.args[1])
		
		strType = ""
		if type(val) is int: strType = "int"
		elif type(val) is float: strType = "float"
		elif type(val) is bool: strType = "bool"
		elif type(val) is Nil: strType = "nil"
		elif type(val) is str: strType = "string"
		
		data.VariableSetValue(self.args[0], strType)

class LabelInstruction(Instruction):
	""" 
	Speciální instrukce definující návěští. 
	
	Neukládá se do seznamu instrukcí programu ani není spustitelná.
	Před spuštěním programu se hodnota návěští přidá do seznamu návěští programu.
	"""
	argumentTypes = [Label]

	def __init__(self, args):
		self.name: Label = args[0]

class Jump(Instruction):
	""" Skok na návěští """
	argumentTypes = [Label]

	def Run(self, data: Program) -> None:
		if self.args[0] not in data.labels:
			throwErr(f"JUMP - Label {self.args[0]} is not defined", ExitCode.SEMANTIC)
		data.programCounter = data.labels[self.args[0]]

class Jumpifeq(Jump):
	""" Skok na návěští pokud se hodnoty rovnají """
	argumentTypes = [Label, Symbol, Symbol]
	
	def Run(self, data: Program) -> None:
		val1 = data.SymbolValue(self.args[1])
		val2 = data.SymbolValue(self.args[2])

		if type(val1) != type(val2):
			throwErr("JUMPIFEQ - Last two arguments have different type", ExitCode.INCORRECT_TYPE)
		if type(val1) is Nil or val1 == val2: 
			super().Run(data)

class Jumpifneq(Jump):
	""" Skok na návěští, pokud se hodnoty nerovnají """
	argumentTypes = [Label, Symbol, Symbol]
	
	def Run(self, data: Program) -> None:
		val1 = data.SymbolValue(self.args[1])
		val2 = data.SymbolValue(self.args[2])
		
		if type(val1) != type(val2):
			throwErr("JUMPIFNEQ - Last two arguments have different type", ExitCode.INCORRECT_TYPE)
		if type(val1) is not Nil and val1 != val2:
			super().Run(data)

class Call(Jump):
	""" Uložení aktuální pozice na zásobník volání a provedení skoku na návěští """
	def Run(self, data: Program) -> None:
		data.callStack.append(data.programCounter)
		super().Run(data)


class Return(Instruction):
	""" Návrat na adresu na vrcholu zásobníku volání """
	def Run(self, data: Program) -> None:
		if len(data.callStack) == 0:
			throwErr("RETURN - Call stack is empty", ExitCode.UNDEFINED_VALUE)
		data.programCounter = data.callStack.pop()

class Exit(Instruction):
	""" Předčasné ukončení programu s vlastním návratovým kódem """
	argumentTypes = [Symbol]
	
	def Run(self, data: Program) -> None:
		val = data.SymbolValue(self.args[0])
		if type(val) is not int:
			throwErr("EXIT - Exit code must be INT", ExitCode.INCORRECT_TYPE)
		elif val < 0 or val > 49:
			throwErr("EXIT - Exit code must be in the range of <0;49>", ExitCode.INCORRECT_VALUE)
		data.programCounter = len(data.instructions)
		data.exitCode = val

class Dprint(Instruction):
	""" Vypsání informací o symbolu na chybový výstup """
	argumentTypes = [Symbol]

	def Run(self, data: Program) -> None:
		val = data.SymbolValue(self.args[0])
		if type(self.args[0]) is Variable:
			print(f"[DEBUG] VarName: {self.args[0]} Type: {type(val)} Value: {val}", file=stderr)
		else:	
			print(f"[DEBUG] Type: {type(val)} Value: {val}", file=stderr)

class Break(Instruction):
	""" Vypsání debug informací o aktuálním stavu interpretace na chybový výstup """
	def Run(self, data: Program) -> None:
		print("[BREAK INFO START]", file=stderr)
		print(f"PC: {data.programCounter - 1}", file=stderr)
		print(f"DATA STACK: {data.dataStack}", file=stderr)
		print(f"CALL STACK: {data.callStack}", file=stderr)
		print(f"GF:{data.globalFrame}", file=stderr)
		print(f"LF:{data.localFrameStack}", file=stderr)
		print(f"TF:{data.temporaryFrame}", file=stderr)
		print("[BREAK INFO END]", file=stderr)

# Rozšíření STACK -------------------------------------------------------------

class StackInstruction(Instruction):
	""" Obecná definice zásobníkové instrukce """
	# Povolené načtené typy ze zásobníku
	arithmeticTypes = [int, float]

	# Počet načtených informací
	argumentCount = 2

	def ArithmeticOp(self) -> Symbol:
		""" Provedení operacena zásobníku """
		raise NotImplementedError

	def Run(self, data: Program) -> None:
		if len(data.dataStack) < self.argumentCount:
			throwErr(f"STACK - Instruction requires at least {self.argumentCount} values on the stack", ExitCode.UNDEFINED_VALUE)
		
		# Získání symbolů ze zásobníku a validace typů
		self.args.clear()

		commonType = None
		for i in range(self.argumentCount):
			val = data.dataStack.pop()
			if type(val) not in self.arithmeticTypes:
				throwErr(f"STACK - Incompatible types (arg {i})", ExitCode.INCORRECT_TYPE)
			if commonType not in (None, Nil) and type(val) not in (commonType, Nil):
				throwErr(f"STACK - Types must be equal (arg {i})", ExitCode.INCORRECT_TYPE)

			if commonType is None: commonType = type(val)
			self.args.append(val)

		data.dataStack.append(self.ArithmeticOp())

class Clears(Instruction):
	""" Vymazení všech hodnot z datového zásobníku """
	def Run(self, data: Program) -> None:
		data.dataStack = []

class Adds(StackInstruction):
	""" Sečtení dvou hodnot na vrcholu zásobníku """
	def ArithmeticOp(self) -> Symbol:
		return self.args[1] + self.args[0]

class Subs(StackInstruction):
	""" Odečtení dvou hodnot na vrcholu zásobníku """
	def ArithmeticOp(self) -> Symbol:
		return self.args[1] - self.args[0]

class Muls(StackInstruction):
	""" Vynásobení dvou hodnot na vrcholu zásobníku """
	def ArithmeticOp(self) -> Symbol:
		return self.args[1] * self.args[0]

class Idivs(StackInstruction):
	""" Celočíselné dělení dvou hodnot na vrcholu zásobníku """
	arithmeticTypes = [int]
	
	def ArithmeticOp(self) -> Symbol:
		if self.args[0] == 0:
			throwErr("IDIVS - Division by zero", ExitCode.INCORRECT_VALUE)
		
		return self.args[1] // self.args[0]

class Lts(StackInstruction):
	""" Porovnání menší než dvou hodnot na vrcholu zásobníku """
	arithmeticTypes = [int, float, bool, str]
	
	def ArithmeticOp(self) -> Symbol:
		return self.args[1] < self.args[0]

class Gts(Lts):
	""" Porovnání větší než dvou hodnot na vrcholu zásobníku """
	def ArithmeticOp(self) -> Symbol:
		return self.args[1] > self.args[0]

class Eqs(StackInstruction):
	""" Kontrola rovnosti dvou hodnot na vrcholu zásobníku """
	arithmeticTypes = [int, float, bool, str, Nil]
	
	def ArithmeticOp(self) -> Symbol:
		if type(self.args[1]) is Nil:
			return type(self.args[0]) is Nil
		elif type(self.args[0]) is Nil:
			return False
		
		return self.args[1] == self.args[0]

class Ands(StackInstruction):
	""" Logické 'a' dvou hodnot na vrcholu zásobníku """
	arithmeticTypes = [bool]
	
	def ArithmeticOp(self) -> Symbol:
		return self.args[1] and self.args[0]

class Ors(Ands):
	""" Logické 'nebo' dvou hodnot na vrcholu zásobníku """
	def ArithmeticOp(self) -> Symbol:
		return self.args[1] or self.args[0]

class Nots(StackInstruction):
	""" Logická inverze hodnoty na vrcholu zásobníku """
	arithmeticTypes = [bool]
	argumentCount = 1
	
	def ArithmeticOp(self) -> Symbol:
		return not self.args[0]

class Int2chars(Instruction):
	""" Převod čísla na vrcholu zásobníku na znak """
	def Run(self, data: Program) -> None:
		if len(data.dataStack) < 1:
			throwErr("INT2CHARS - Stack is empty", ExitCode.UNDEFINED_VALUE)
		
		try:
			data.dataStack.append(chr(data.dataStack.pop()))
		except ValueError:
			throwErr("INT2CHARS - INT must be in valid unicode range", ExitCode.INVALID_STRING_OP)
		except TypeError:
			throwErr("INT2CHARS - Expected INT on top of the stack", ExitCode.INCORRECT_TYPE)

class Stri2ints(Instruction):
	""" Vrátí číselnou hodnotu znaku na indexu řetězce na vrcholu datového zásobníku """
	def Run(self, data: Program) -> None:
		if len(data.dataStack) < 2:
			throwErr("STRI2INTS - Expected at least two values on the stack", ExitCode.UNDEFINED_VALUE)
		
		index = data.dataStack.pop()
		string = data.dataStack.pop()

		if type(string) is not str or type(index) is not int:
			throwErr("STRI2INTS - Expected types STRING and INT", ExitCode.INCORRECT_TYPE)

		try: data.dataStack.append(ord(string[index]))
		except IndexError:
			throwErr("STRI2INTS - Index out of range", ExitCode.INVALID_STRING_OP)

class Jumpifeqs(Jump):
	""" Skočit na návěští pokud se dvě hodnoty na vrcholu zásobníku rovnají """
	def Run(self, data: Program) -> None:
		if len(data.dataStack) < 2:
			throwErr("JUMPIFEQS - Expected at least two values on the stack", ExitCode.UNDEFINED_VALUE)
		
		val2 = data.dataStack.pop()
		val1 = data.dataStack.pop()

		if type(val1) != type(val2):
			throwErr("JUMPIFEQS - Last two items on the stack have different type", ExitCode.INCORRECT_TYPE)
		if type(val1) is Nil or val1 == val2: 
			super().Run(data)

class Jumpifneqs(Jump):
	""" Skočit na návěští pokud se dvě hodnoty na vrcholu zásobníku nerovnají """
	def Run(self, data: Program) -> None:
		if len(data.dataStack) < 2:
			throwErr("JUMPIFEQS - Expected at least two values on the stack", ExitCode.UNDEFINED_VALUE)
		
		val2 = data.dataStack.pop()
		val1 = data.dataStack.pop()

		if type(val1) != type(val2):
			throwErr("JUMPIFEQS - Last two items on the stack have different type", ExitCode.INCORRECT_TYPE)
		if type(val1) is not Nil and val1 != val2:
			super().Run(data)

# Převod řetězce na třídu instrukce
InstructionClasses = {
	"MOVE": Move,
	"CREATEFRAME": Createframe,
	"PUSHFRAME": Pushframe,
	"POPFRAME": Popframe,
	"DEFVAR": Defvar,
	"CALL": Call,
	"RETURN": Return,
	"PUSHS": Pushs,
	"POPS": Pops,
	"ADD": Add,
	"SUB": Sub,
	"MUL": Mul,
	"DIV": Div,
	"IDIV": Idiv,
	"LT": Lt,
	"GT": Gt,
	"EQ": Eq,
	"AND": And,
	"OR": Or,
	"NOT": Not,
	"INT2CHAR": Int2char,
	"STRI2INT": Stri2int,
	"READ": Read,
	"WRITE": Write,
	"CONCAT": Concat,
	"STRLEN": Strlen,
	"GETCHAR": Getchar,
	"SETCHAR": Setchar,
	"TYPE": Type,
	"LABEL": LabelInstruction,
	"JUMP": Jump,
	"JUMPIFEQ": Jumpifeq,
	"JUMPIFNEQ": Jumpifneq,
	"EXIT": Exit,
	"DPRINT": Dprint,
	"BREAK": Break,
	# Stack rozšíření
	"CLEARS": Clears,
	"ADDS": Adds,
	"SUBS": Subs,
	"MULS": Muls,
	"IDIVS": Idivs,
	"LTS": Lts,
	"GTS": Gts,
	"EQS": Eqs,
	"ANDS": Ands,
	"ORS": Ors,
	"NOTS": Nots,
	"INT2CHARS": Int2chars,
	"STRI2INTS": Stri2ints,
	"JUMPIFEQS": Jumpifeqs,
	"JUMPIFNEQS": Jumpifneqs,
	# Float rozšíření
	"INT2FLOAT": Int2float,
	"FLOAT2INT": Float2int
}

def ParseXMLInstruction(XMLnode: Element) -> Instruction:
	""" Získání reprezentace instrukce z XML elementu instrukce """
	
	opcode = XMLnode.get("opcode")
	if type(opcode) is None:
		throwErr("Opcode argument is missing", ExitCode.XML_STRUCTURE)
	
	# OPCODE není case sensitive
	opcode = opcode.upper()
	args = ParseInstructionArguments(XMLnode)
	
	if opcode not in InstructionClasses:
		throwErr( f"Unknown instruction {opcode}" , ExitCode.XML_STRUCTURE)

	# Získání třídy podle názvu opcode
	instr = InstructionClasses[opcode]	
	types = instr.argumentTypes

	# POčet argumentů musí souhlasit
	if len(types) != len(args):
		throwErr(f"{opcode} expected {len(types)} argument(s), found {len(args)}", ExitCode.XML_STRUCTURE)

	# Všechny typy argumentů musí souhlasit
	for i in range(0, len(args)):
		if not (types[i] == Symbol and IsSymbol(args[i]) or types[i] == type(args[i])):
			throwErr(f"{opcode} expected {i+1}. argument {types[i]}, found {type(args[i])}", ExitCode.XML_STRUCTURE)
	
	return instr(args)