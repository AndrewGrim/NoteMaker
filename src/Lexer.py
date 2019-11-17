import os
import sys
from enum import IntEnum
import typing
from typing import List
from typing import Union
from typing import Tuple
from typing import Dict
from typing import NewType

from TokenTypes import *
from Token import *
from Debug import *

LexerToken = NewType('Token', None)

def lex(text: str) -> List[LexerToken]:
	if os.path.exists(text):
		text = open(text, "r").read()

	tokens = []

	i = 0
	code = False
	line = 0
	check = False
	html = False
	bold = False
	underline = False
	italic = False

	lCount = 0
	listBlock = False
	listItem = False
	listIndex = []
	while i < len(text):
		char = text[i]
		if char == "\n":
			line += 1

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
		elif check:
			if char == "\n":
				check = False
				tokens.append(Token(MD.CHECK_END, i, i + 1))
			else:
				tokens.append(Token(MD.CHECK_TEXT, i, i + 1))
		elif listBlock:
			try:
				text[i + 1]
			except IndexError:
				text += "\n"
			if char == "\n" and text[i + 1] == "\n":
				listIndex = []
				listBlock = False
				if lCount > 0:
					tokens.append(Token(MD.ERROR, i - 1, i))
					warn(f"Found unclosed list/s! lCount should be 0 instead is {lCount}!")
			elif char == "\n" and text[i - 1] != ";":
				listItem = False
				tokens.append(Token(MD.LIST_ITEM_END, i, i + 1))
			elif char == ":" and text[i + 1] == ":":
				nextC = text[i + 2]
				if nextC == "*" or nextC.isnumeric():
					c = text[i + 3]
					if c == " ":
						if nextC == "*":
							tokens.append(Token(MD.ULIST_BEGIN, i, i + 3))
							listIndex.append(MD.ULIST_END)
						else:
							tokens.append(Token(MD.OLIST_BEGIN, i, i + 3))
							listIndex.append(MD.OLIST_END)
						tokens.append(Token(MD.LIST_ITEM_BEGIN, i, i + 3))
						i += 3
						tokens.append(Token(MD.SPACE, i, i + 1))
						lCount += 1
						listItem = True
					else:
						tokens.append(Token(MD.ERROR, i, i + 1))
						warn(f"Line: {line}, Index: {i} -> Improper list formatting! Expected a space after the '*' or digit!")
				else:
					tokens.append(Token(MD.ERROR, i, i + 1))
					warn(f"Line: {line}, Index: {i} -> Improper list formatting! Expected '*' or a digit!")
			elif char == "*" or char.isnumeric() and not listItem:
				nextC = text[i + 1]
				if nextC == " ":
					tokens.append(Token(MD.LIST_ITEM_BEGIN, i, i + 1))
					i += 1
					tokens.append(Token(MD.SPACE, i, i + 1))
					listItem = True
				else:
					tokens.append(Token(MD.ERROR, i, i + 1))
					warn(f"Line: {line}, Index: {i} -> Improper list formatting! Expected a space after the '*' or digit!")
				
			if listItem:
				tokens.append(Token(MD.LIST_ITEM_TEXT, i, i + 1))
			elif char == " ":
				tokens.append(Token(MD.SPACE, i, i + 1))
			elif char == "\t":
				tokens.append(Token(MD.TAB, i, i + 1))
			elif char == "\n":
				tokens.append(Token(MD.NEWLINE, i, i + 1))
			elif char == ";":
				try:
					tokens.append(Token(listIndex[-1], i, i + 1))
					del listIndex[-1]
					lCount -= 1
				except IndexError:
					tokens.append(Token(MD.ERROR, i, i + 1))
					warn(f"Line: {line}, Index: {i} -> Tried to close more lists than were declared!")
			else:
				tokens.append(Token(MD.ERROR, i - 1, i))
				warn(f"Line: {line}, Index: {i} -> Improper list formatting! Found an alphanumeric symbol!")
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
				warn(f"Line: {line}, Index: {i} -> Improperly formatted underline! Missing '_'!")
		elif char == "*":
			nextC = text[i + 1]
			if nextC == "*":
				tokens.append(Token(MD.BOLD_BEGIN, i, i + 2))
				bold = True
				i += 1
			elif nextC.isalnum():
				tokens.append(Token(MD.ITALIC_BEGIN, i, i + 1))
				italic = True
			else:
				tokens.append(Token(MD.ERROR, i, i + 1))
				warn(f"Line: {line}, Index: {i} -> Unexpected symbol! '{nextC}'. Expected bold or italic found neither!")
		elif char == ":" and text[i + 1] == ":":
			nextC = text[i + 2]
			if nextC == "*" or nextC.isnumeric():
				c = text[i + 3]
				if c == " ":
					if nextC == "*":
						tokens.append(Token(MD.ULIST_BEGIN, i, i + 3))
						listIndex.append(MD.ULIST_END)
					else:
						tokens.append(Token(MD.OLIST_BEGIN, i, i + 3))
						listIndex.append(MD.OLIST_END)
					tokens.append(Token(MD.LIST_ITEM_BEGIN, i, i + 3))
					i += 3
					tokens.append(Token(MD.SPACE, i, i + 1))
					lCount = 1
					listBlock = True
					listItem = True
				else:
					tokens.append(Token(MD.ERROR, i, i + 1))
					warn(f"Line: {line}, Index: {i} -> Improper list formatting! Expected a space after the '*' or digit!")
			else:
				tokens.append(Token(MD.ERROR, i, i + 1))
				warn(f"Line: {line}, Index: {i} -> Improper list formatting! Expected '*' or a digit!")
		elif char == "-":
			nextC = text[i + 1]
			if nextC == "-":
				c = text[i + 2]
				if c == "-":
					tokens.append(Token(MD.HORIZONTAL_RULE, i, i + 3))
					i += 2
			elif nextC == " " and text[i + 2] == "[":
				c = text[i + 3]
				if c == " ":
					if text[i + 4] == "]" and text[i + 5] == " ":
						tokens.append(Token(MD.UNCHECKED, i, i + 5))
						i += 5
						tokens.append(Token(MD.SPACE, i, i + 1))
						check = True
					else:
						tokens.append(Token(MD.ERROR, i, i + 5))
						warn(f"Line: {line}, Index: {i} -> Improper check formatting! Expected ']' and space! Found '{text[i + 4]}' and '{text[i + 5]}'!")
				elif c == "x":
					if text[i + 4] == "]" and text[i + 5] == " ":
						tokens.append(Token(MD.CHECKED, i, i + 5))
						i += 5
						tokens.append(Token(MD.SPACE, i, i + 1))
						check = True
					else:
						tokens.append(Token(MD.ERROR, i, i + 5))
						warn(f"Line: {line}, Index: {i} -> Improper check formatting! Expected ']' and space! Found '{text[i + 4]}' and '{text[i + 5]}'!")
				else:
					tokens.append(Token(MD.ERROR, i, i + 4))
					warn(f"Line: {line}, Index: {i} -> Improper check formatting! Expected either 'space' or 'x'! Found '{c}'!")
			else:
				tokens.append(Token(MD.ERROR, i, i + 1))
				warn(f"Line: {line}, Index: {i} -> Expected either horizontal rule or check! Found '{nextC}'!")
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