import os
import sys
from enum import IntEnum
import typing
from typing import List
from typing import Union
from typing import Tuple
from typing import Dict
from typing import NewType

MD_ENUM = NewType('MD_ENUM', int)
Token = NewType('Token', None)

def fail(message: str) -> None:
	print(f"{TCOLOR.FAIL}FAILURE! {message}{TCOLOR.ENDC}")


def warn(message: str) -> None:
	print(f"{TCOLOR.WARNING}WARNING! {message}{TCOLOR.ENDC}")


def ok(message: str) -> None:
	print(f"{TCOLOR.OKGREEN}{message}{TCOLOR.ENDC}")

def debug(message: str) -> None:
	print(f"{TCOLOR.HEADER}DEBUG:\n{message}{TCOLOR.ENDC}")


class TCOLOR:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


class MD(IntEnum):
	HEADING = 0
	HEADING1 = 1 # these are probably not neccessary since we know the begin and end points
	HEADING2 = 2 # these are probably not neccessary since we know the begin and end points
	HEADING3 = 3 # these are probably not neccessary since we know the begin and end points
	HEADING4 = 4 # these are probably not neccessary since we know the begin and end points
	HEADING5 = 5 # these are probably not neccessary since we know the begin and end points
	HEADING6 = 6 # these are probably not neccessary since we know the begin and end points
	BOLD = 7
	ITALIC = 8
	UNDERLINE = 9
	STRIKE = 10
	BLOCKQUOTE = 11
	CODE = 12
	ULIST = 13
	OLIST = 14
	CHECKED = 15
	UNCHECKED = 16
	IMAGE = 17
	LINK = 18
	HTML = 19

	NEWLINE = 20
	TAB = 21
	SPACE = 22
	TEXT = 23
	ERROR = 24

	CODE_BEGIN = 25
	CODE_END = 26

	BOLD_BEGIN = 27
	BOLD_END = 28

	UNDERLINE_BEGIN = 29
	UNDERLINE_END = 30

	ITALIC_BEGIN = 31
	ITALIC_END = 32

	HORIZONTAL_RULE = 33

	ULIST_BEGIN = 34
	ULIST_END = 35


class Token:

	def __init__(self, id: MD_ENUM, begin: int = None, end: int = None) -> None:
		self.id = id
		self.begin = begin
		self.end = end
		#self.content = content

	
	def __str__(self) -> str:
		return f"\nToken:\n\tid:{self.id}\n\tbegin:{self.begin}\n\tend:{self.end}\n"


	def __repr__(self) -> str:
		return self.__str__()


class ListToken(Token):

	def __init__(self, id: MD_ENUM, begin: int = None, end: int = None, indent: int = None) -> None:
		super().__init__(id, begin, end)
		self.indent = indent

	
	def __str__(self) -> str:
		return f"\nListToken:\n\tid:{self.id}\n\tbegin:{self.begin}\n\tend:{self.end}\n\tindent:{self.indent}\n"


	def __repr__(self) -> str:
		return self.__str__()


def lex(text: str) -> List[Token]:
	if os.path.exists(text):
		text = open(text, "r").read()

	tokens = []

	i = 0
	lineEnd = ""
	code = False
	uList = False
	oList = False
	line = 0
	lastC = ""
	li = False
	lCount = 0
	indent = 0
	lastOffset = 0
	listBlock = False
	check = False
	html = False
	bold = False
	underline = False
	italic = False
	while i < len(text):
		char = text[i]
		if char == "\n":
			line += 1 # a rough approximation

		if code:
			if char == "`":
				code = False
				tokens.append(Token(MD.CODE_END, i, i + 1))
			else:
				tokens.append(Token(MD.CODE, i, i + 1))
		elif bold:
			if char == "*":
				bold = False
				tokens.append(Token(MD.BOLD_END, i, i + 2))
				i += 1
			else:
				tokens.append(Token(MD.BOLD, i, i + 1))
		elif underline:
			if char == "_":
				underline = False
				tokens.append(Token(MD.UNDERLINE_END, i, i + 2))
				i += 1
			else:
				tokens.append(Token(MD.UNDERLINE, i, i + 1))
		elif italic:
			if char == "*":
				italic = False
				tokens.append(Token(MD.ITALIC_END, i, i + 1))
			else:
				tokens.append(Token(MD.ITALIC, i, i + 1))
		elif char == "\n":
			tokens.append(Token(MD.NEWLINE, i, i + 1))
		elif char == " ":
			tokens.append(Token(MD.SPACE, i, i + 1))
		elif char == "\t":
			tokens.append(Token(MD.TAB, i, i + 1))
		elif char == "#":
			hCount = 0
			while True:
				c = text[i]
				if c == " ":
					i -= 1
					break
				elif c == "\n":
					warn(f"Line: {line}, Index: {i} -> Improperly formatted heading! You need a space after the # !")
					tokens.append(Token(MD.ERROR, i - hCount, i))
					break
				elif c == "#":
					hCount += 1
					if hCount > 6:
						warn(f"Line: {line}, Index: {i} -> Too many #! You can only use up to 6 # !")
						tokens.append(Token(MD.ERROR, (i - hCount) + 1, i + 1))
				i += 1
			tokens.append(Token(MD.HEADING, (i + 1) - hCount, i + 1))
		elif char == "`":
			tokens.append(Token(MD.CODE_BEGIN, i, i + 1))
			code = True
		elif char == ">":
			tokens.append(Token(MD.BLOCKQUOTE, i, i + 1))
		elif char == "~":
			nextC = text[i + 1]
			if nextC == "~":
				tokens.append(Token(MD.STRIKE, i, i + 2))
				i += 1
			else:
				tokens.append(Token(MD.ERROR, i, i + 1))
				warn(f"Line: {line}, Index: {i} -> Improperly formatted strikethrough! Missing ~ !")
		elif char == "_":
			nextC = text[i + 1]
			if nextC == "_":
				tokens.append(Token(MD.UNDERLINE_BEGIN, i, i + 2))
				underline = True
				i += 1
			else:
				tokens.append(Token(MD.ERROR, i, i + 1))
				warn(f"Line: {line}, Index: {i} -> Improperly formatted underline! Missing _ !")
		elif char == "*":
			nextC = text[i + 1]
			if nextC == "*":
				tokens.append(Token(MD.BOLD_BEGIN, i, i + 2))
				bold = True
				i += 1
			elif nextC.isalnum():
				tokens.append(Token(MD.ITALIC_BEGIN, i, i + 1))
				italic = True
			elif nextC == " ":
				listBlock = True
				indent = 0
				if text[i - 1] == "\n":
					indent = 0
				else:
					index = 2
					while True:
						if text[i - index] == "\n":
							indent = index - 1
							break
						elif text[i - index] in [" ", "\t"]:
							index += 1
						else:
							tokens.append(Token(MD.ERROR, i, i + 1))
							warn(f"Line: {line}, Index: {i} -> Improper list formatting! Could not find whitespace or newline!")
							break
				if text[i - 1].isalnum():
					tokens.append(Token(MD.ERROR, i - 1, i))
					warn(f"Line: {line}, Index: {i} -> Improper list formatting! Could not find whitespace or newline!")
				else:
					tokens.append(ListToken(MD.ULIST_BEGIN, i, i + 1, 0))
					lCount = 1
			else:
				tokens.append(Token(MD.ERROR, i, i + 1))
				fail(f"Line: {line}, Index: {i} -> UNRECOGNIZED SYMBOL! * ")
		elif char == "-":
			nextC = text[i + 1]
			if nextC == "-":
				c = text[i + 2]
				if c == "-":
					tokens.append(Token(MD.HORIZONTAL_RULE, i, i + 3))
					i += 2
			else:
				tokens.append(Token(MD.ERROR, i, i + 1))
				fail(f"Line: {line}, Index: {i} -> UNRECOGNIZED SYMBOL! - ")
		else:
			tokens.append(Token(MD.TEXT, i, i + 1))
		i += 1

	return tokens

if __name__ == "__main__":
	args = sys.argv
	if len(args) == 2:
		print(lex(args[1]))
	elif len(args) == 1:
		print("You need to specify the text to lex!")
		print("""
	Usage:
		Lexer <file.md> or
		Lexer <string>
	""")
	else:
		print("The program only supports one argument atm!")