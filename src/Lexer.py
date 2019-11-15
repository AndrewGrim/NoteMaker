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
	HEADING1 = 1
	HEADING2 = 2
	HEADING3 = 3
	HEADING4 = 4
	HEADING5 = 5
	HEADING6 = 6
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
			pass
			"""if lineEnd != "":
				lineEnd = ""
				if check and r.read(1) == "\n":
					check = False
				elif check:
					check = False
				r.seek(r.tell() - 1)"""
		if char == "#":
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
				lineEnd = f"</h{hCount}>"
		i += 1

	return tokens

if __name__ == "__main__":
	print(lex())