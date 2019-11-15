import os
import sys
from enum import Enum
import typing
from typing import List
from typing import Union
from typing import Tuple
from typing import Dict
from typing import NewType

MD_ENUM = NewType('MD_ENUM', int)
Token = NewType('Token', None)

class MD(Enum):
	HEADING = 0
	HEADING1 = 1 # these are probably not neccessary since we know the begin and end points
	HEADING2 = 2 # these are probably not neccessary since we know the begin and end points
	HEADING3 = 3 # these are probably not neccessary since we know the begin and end points
	HEADING4 = 4 # these are probably not neccessary since we know the begin and end points
	HEADING5 = 5 # these are probably not neccessary since we know the begin and end points
	HEADING6 = 6 # these are probably not neccessary since we know the begin and end points
	BOLD = 7
	ITALIC = 8
	UNDER = 9
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


def lex(mdFile: str = "Notes/test.md") -> List[Token]:
	tokens = []

	def fileSize(fname):
		statinfo = os.stat(fname)

		return statinfo.st_size


	f = mdFile
	r = open(f, "r")
	fSize = fileSize(f)
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
	innerList = False
	check = False
	html = False
	while r.tell() < fSize:
		char = r.read(1)
		if char == "\n":
			line += 1 # a rough approximation

		if char == "\n":
			tokens.append(Token(MD.NEWLINE, i, i + 1))
			"""if lineEnd != "":
				lineEnd = ""
				if check and r.read(1) == "\n":
					check = False
				elif check:
					check = False
				r.seek(r.tell() - 1)"""
		elif char == " ":
			tokens.append(Token(MD.SPACE, i, i + 1))
		elif char == "\t":
			tokens.append(Token(MD.TAB, i, i + 1))
		elif char == "#":
			hCount = 1
			while True:
				c = r.read(1)
				i += 1
				if c == " ":
					break
				elif c == "\n":
					print(f"Line: {line}, TotalChar: {i} -> Improperly formatted heading!")
					break
				hCount += 1
			if hCount > 6:
				print(f"Line: {line}, TotalChar: {i} -> Heading number is too high!")
			else:
				tokens.append(Token(MD.HEADING, i - hCount, i))
		elif char == "`":
			tokens.append(Token(MD.CODE, i, i + 1))
		else:
			tokens.append(Token(MD.TEXT, i, i + 1))
		i += 1

	return tokens

if __name__ == "__main__":
	print(lex())