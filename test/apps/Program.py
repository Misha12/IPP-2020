from Common import throwErr, ExitCode
from Types import Label, Nil, Scope, Variable, Symbol
from typing import Tuple, Dict, List, Any
import sys

# Typ rámce
Frame = Dict[str, Symbol]

class Program:
	""" 
	Třída reprezentující interpretovaný program.
	Obsahuje seznam prováděných instrukcí a zavedených proměnných.
	"""
	def __init__(self, readFile):
		# Seznam instrukcí
		self.instructions: List[Any] = []
		
		# Aktuálně prováděná instrukce
		self.programCounter: int = 0
		
		# Seznam návěští, klíč je název návěští a hodnota je index instrukce
		self.labels: Dict[Label, int] = {}
		
		# Globání rámec proměnných (klíč je název proměnné)
		self.globalFrame: Frame = {}

		# Zásobník lokálních rámců proměnných (klíč je název proměnné)
		self.localFrameStack: List[Frame] = []
		
		# Dočasný rámec proměnných (klíč je název proměnné)
		self.temporaryFrame: Frame = None
		
		# Zásobník volání obsahujicí návratový index instrukce
		self.callStack: List[int] = []

		# Datový zásobník
		self.dataStack: List[Symbol] = []
		
		# Soubor pro čtení instrukcí READ
		self.readFile = readFile

		# Návratový kód programu
		self.exitCode = 0

		# Rozšíření STATI
		self.statsActive = False
		self.statsMaxVars = 0
		self.statsInstrCount = 0

	def VariableExist(self, var: Variable) -> bool:
		""" Kontrola, zda proměnná existuje """
		if var.scope == Scope.GLOBAL:
			return var.name in self.globalFrame
		elif var.scope == Scope.LOCAL:
			if len(self.localFrameStack) == 0:
				throwErr("Local frame is not initialised", ExitCode.UNINITIALISED_FRAME)
			return var.name in self.localFrameStack[-1]
		elif var.scope == Scope.TEMP: 
			if self.temporaryFrame == None:
				throwErr("Temporary frame is not initialised", ExitCode.UNINITIALISED_FRAME)
			return var.name in self.temporaryFrame
		
		return False
	
	def VariableSetValue(self, var: Variable, value: Symbol) -> None:
		""" Uložení nové hodnoty do proměnné. Proměnná musí být definovanáj inak se jedná o chybu. """
		if not self.VariableExist(var):
			throwErr(f"Variable {var} is not defined", ExitCode.UNDEFINED_VARIABLE)
		
		if var.scope == Scope.GLOBAL: self.globalFrame[var.name] = value
		elif var.scope == Scope.LOCAL: self.localFrameStack[-1][var.name] = value
		elif var.scope == Scope.TEMP: self.temporaryFrame[var.name] = value


	def VariableGetValue(self, var: Variable, errorOnUninit: bool = True) -> Symbol:
		""" 
		Získání hodnoty z proměnné. 
		
		Pokud je volitelný druhý parametr nastavený na true (výchozí), proměnná musí existovat. 
		Pokud proměnná neexsistuje je vrácena hodnota None
		"""
		if not self.VariableExist(var):
			throwErr(f"Variable {var} is not defined", ExitCode.UNDEFINED_VARIABLE)
		
		value = None
		if var.scope == Scope.GLOBAL: value = self.globalFrame[var.name]
		elif var.scope == Scope.LOCAL: value = self.localFrameStack[-1][var.name]
		elif var.scope == Scope.TEMP: value = self.temporaryFrame[var.name]
		
		if errorOnUninit and value == None:
			throwErr(f"Variable {var} is not initialised", ExitCode.UNDEFINED_VALUE)
		return value
	
	def SymbolValue(self, symb: Symbol) -> Symbol:
		""" Získání skutečné hodnoty ze symbolu (symbol může např. být proměnná) """
		if type(symb) is Variable:
			return self.VariableGetValue(symb)
		return symb

	def Run(self):
		""" Spustit interpretaci načteného programu """
		# Provádět instrukce, dokud program counter ukozuje na validní index
		while len(self.instructions) > self.programCounter:
			# Inkrementovat program counter a spustit instrukci
			self.programCounter += 1
			self.instructions[self.programCounter - 1].Run(self)

			# Sbírání statistik o inpterpretaci
			if self.statsActive:
				self.statsInstrCount += 1

				# Aktualizace maximálního počtu definovaných proměnných
				varcnt = len(self.globalFrame) 
				if self.temporaryFrame is not None: 
					varcnt += len(self.temporaryFrame)
				
				if len(self.localFrameStack) > 0:
					varcnt += len(self.localFrameStack[-1])
				
				if varcnt > self.statsMaxVars:
					self.statsMaxVars = varcnt
