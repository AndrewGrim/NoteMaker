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
from Tokens import *
from Debug import *

TToken = NewType('TToken', None)

def lex(text: str) -> List[TToken]:
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
	listItem = False
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
		elif listBlock:
			try:
				text[i + 1]
			except IndexError:
				text += "\n"
			if char == "\n" and text[i + 1] == "\n":
				for num in range(lCount):
					tokens.append(ListToken(MD.ULIST_END, i - 1, i, indent))
					lCount -= 1
				tokens.append(Token(MD.NEWLINE, i, i + 1))
				listBlock = False
				listItem = False
				assert lCount == 0, fail(f"lCount should be 0 instead is {lCount}!")
			elif char == "\n":
				listItem = False
				tokens.append(ListToken(MD.ULIST_ITEM_END, i, i + 1, indent))
			elif char == "*":
				nextC = text[i + 1]
				if nextC == " ":
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
						for t in tokens.__reversed__():
							if t.id in [MD.ULIST_BEGIN, MD.ULIST_ITEM_BEGIN]: # prob can compare only against item_begin
								if t.indent == indent:
									tokens.append(ListToken(MD.ULIST_ITEM_BEGIN, i, i + 1, indent))
									i += 1
									tokens.append(Token(MD.SPACE, i, i + 1))
									listItem = True
									break
								elif t.indent < indent:
									tokens.append(ListToken(MD.ULIST_BEGIN, i, i + 1, indent))
									lCount += 1
									tokens.append(ListToken(MD.ULIST_ITEM_BEGIN, i, i + 1, indent))
									i += 1
									tokens.append(Token(MD.SPACE, i, i + 1))
									listItem = True
									break
								elif t.indent > indent:
									for num in range(lCount - 1):
										tokens.append(ListToken(MD.ULIST_END, i, i + 1, indent))
										lCount -= 1
									tokens.append(ListToken(MD.ULIST_ITEM_BEGIN, i, i + 1, indent))
									i += 1
									tokens.append(Token(MD.SPACE, i, i + 1))
									listItem = True
									break
			if listItem:
				tokens.append(ListToken(MD.ULIST_ITEM_TEXT, i, i + 1, indent))
			elif char == " ":
				tokens.append(Token(MD.SPACE, i, i + 1))
			elif char == "\t":
				tokens.append(Token(MD.TAB, i, i + 1))
			elif char == "\n":
				tokens.append(Token(MD.NEWLINE, i, i + 1))
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
				indent = 0
				if text[i - 1] == "\n" or i == 0:
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
				if text[i - 1].isalnum() and i != 0:
					tokens.append(Token(MD.ERROR, i - 1, i))
					warn(f"Line: {line}, Index: {i} -> Improper list formatting! Could not find whitespace or newline!")
				else:
					tokens.append(ListToken(MD.ULIST_BEGIN, i, i + 1, indent))
					tokens.append(ListToken(MD.ULIST_ITEM_BEGIN, i, i + 1, indent))
					i += 1
					tokens.append(Token(MD.SPACE, i, i + 1))
					lCount = 1
					listBlock = True
					listItem = True
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