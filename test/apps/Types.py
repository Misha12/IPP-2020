from enum import Enum
from typing import Any, Union

class Scope(Enum):
	""" Rozsah platnosti proměnné (Typ rámce) """
	GLOBAL	= 1	# GF
	LOCAL	= 2	# LF
	TEMP	= 4	# TF

class Variable():
	""" Třída reprezentující proměnnou v IPPcode19 """
	def __init__(self, scope: Scope, name: str):
		# Rozsah platnosti proměnné
		self.scope = scope

		# Název proměnné
		self.name = name
	
	def __str__(self):
		return f"{self.scope} {self.name}"

class Nil():
	""" Typ nil v IPPcode19 """
	def __str__(self):
		return ""

class Label(str):
	""" Název návěští v IPPcode19 """
	pass

# Typy součástí symbolu
Symbol = Union[Variable, int, float, str, bool, Nil]

def IsSymbol(value: Any) -> bool:
	""" Test, zda je hodnota typu symbol """
	return type(value) in (Variable, int, float, str, bool, Nil)