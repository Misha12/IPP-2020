import sys
from argparse import ArgumentParser
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from typing import Dict
from Types import Label
from Common import throwErr, ExitCode
from Instruction import Instruction, LabelInstruction, ParseXMLInstruction
from Program import Program

if "--help"  in sys.argv and len(sys.argv) > 2:
	throwErr("Argument --help cannot be used in combination with other arguments", ExitCode.PROGRAM_ARGUMENT)

# Zpracování argumentů --------------------------------------------------------

def argError(message: str):
	""" Změnit chybovou hlášku analyzátoru argumentů """
	throwErr(message.replace("Error:", "", 1), ExitCode.PROGRAM_ARGUMENT)

argparser = ArgumentParser()
argparser.add_argument("--source", type=str)
argparser.add_argument("--input", type=str)
argparser.add_argument("--stats", type=str)
argparser.add_argument("--insts", action='store_true')
argparser.add_argument("--vars", action='store_true')
argparser.error = argError

args = argparser.parse_args()
if args.input is None and args.source is None:
	argError("Argument --source and/or --input must be defined")

# Vstupní soubor
inputFile = sys.stdin
if args.input is not None:
	try: inputFile = open(args.input, "r")
	except: throwErr("Cannot read input file", ExitCode.FILE_READ)

# Soubor se zdrojovým kódem v XML
sourceFile = sys.stdin
if args.source is not None:
	try: sourceFile = open(args.source, "rb")
	except: throwErr("Cannot read source file", ExitCode.FILE_READ)

# Soubor se statistikami
statsFile = None
if args.stats is not None:
	try: statsFile = open(args.stats, "w")
	except: throwErr("Cannot read source file", ExitCode.FILE_WRITE)
elif "--insts" in sys.argv or "--vars" in sys.argv:
	throwErr("Argument --insts and/or --vars must be used with argument --stats", ExitCode.PROGRAM_ARGUMENT)

# Načtení instrukcí z XML souboru ---------------------------------------------

try: XMLroot = ElementTree.parse(sourceFile).getroot()
except: throwErr("Failed to parse source XML code", ExitCode.XML_FORMAT)

if XMLroot.tag != "program":
	throwErr("Exprected <program> as root element", ExitCode.XML_STRUCTURE)

langIdentifier = XMLroot.get("language")
if langIdentifier != "IPPcode20":
	throwErr("Expected language attribute with a value \"IPPcode19\" in the root element", ExitCode.XML_STRUCTURE)

# Asociativní pole instrukcí
instructions: Dict[int, Instruction] = {}

XMLinstrNode: Element # XML element instrukce
for XMLinstrNode in XMLroot.findall("instruction"):
	try:
		order = int(XMLinstrNode.get("order"))
	except ValueError:
		throwErr("Instruction order attribute must be integer", ExitCode.XML_STRUCTURE)
	
	if order in instructions:
		throwErr("Found two instructions with the same order", ExitCode.XML_STRUCTURE)
	
	# Získání objekt instrukce z XML elementu
	instructions[order] = ParseXMLInstruction(XMLinstrNode)

# Zpracování samotného programu (seznamu instrukcí) ---------------------------

program = Program(inputFile)

# Uložit instrukce do programu seřazeně podle atributu order
index: int
prevIndex: int = None
for index in sorted(instructions):
	# indexy instrukcí musí jít sekvenčně
	if prevIndex is not None and prevIndex != index - 1:
		throwErr("Instruction order is not sequential", ExitCode.XML_STRUCTURE)
	prevIndex = index
	
	instr = instructions[index]

	if type(instr) is LabelInstruction:
		# Instrukce je definování návěští, uložíme nové návěští pokud již neexistuje
		if instr.name in program.labels:
			throwErr("Label redefinition", ExitCode.SEMANTIC)
		program.labels[instr.name] = len(program.instructions)
	else:
		program.instructions.append(instr)

# Spuštění samotné interpretace
program.statsActive = statsFile is not None
program.Run()

# Pokud je zapnuto sbírání statistik, zapsat je po inpterpretaci do souboru
if statsFile is not None:
	for arg in sys.argv:
		if arg == "--insts":
			statsFile.write(f"{program.statsInstrCount}\n")
		elif arg == "--vars":
			statsFile.write(f"{program.statsMaxVars}\n")

	statsFile.close()

if inputFile is not sys.stdin: inputFile.close()
if sourceFile is not sys.stdin: sourceFile.close()

# ukončit se s návratovým kódem interpretovaného programu
exit(program.exitCode)
