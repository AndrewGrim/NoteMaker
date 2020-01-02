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

def match_tag(tag, text, i, keyword=False, data_type=False):
	assert len(tag) > 0, "Tag length must be greater than zero!"

	matched = True
	for num in range(len(tag)):
		if text[i + num + 1] != tag[num]:
			matched = False
			return matched
	if keyword:
		if matched and text[i + num + 2] not in [" ", "\n", "\t", "."]:
			matched = False
			return matched
	if data_type:
		if matched and text[i + num + 2] not in [":", ")", "\n", " "]:
			matched = False
			return matched

	return matched


def lex(text: str) -> List[LexerToken]:
	if len(text) < 264:
		if os.path.exists(text):
			text = open(text, "r").read()

	tokens = []
	keywords = [
		'as', 'assert', 'async', 'await', 'class', 'continue', 'def', 'del',  
		'from', 'global',  'import',  'lambda', 'nonlocal', 'self',
	]
	flow = [
		'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield', 'if', 
		'in', 'is', 'elif', 'else', 'except', 'finally', 'for', 'and', 'break', 
		'not', 
	]
	types = [
		"None", "str", "int", "bool", "float", "False", "True",
	]

	i = 0
	heading = False
	code = False
	codeBlock = False
	formatBlock = False
	line = 0
	check = False

	html = False
	htmlAttribute = False
	
	bold = False
	underline = False
	italic = False
	image = False
	link = False
	strike = False
	block = False

	lCount = 0
	listBlock = False
	listItem = False
	listIndex = []

	while i < len(text):
		char = text[i]
		if char == "\n":
			line += 1

		if code or codeBlock:
			if char == "`":
				if codeBlock:
					codeBlock = False
					tokens.append(Token(MD.CODEBLOCK_END, i, i + 1))
				else:
					code = False
					tokens.append(Token(MD.CODE_END, i, i + 1))
			else:
				if codeBlock:
					key = False
					if text[i] in [" ", "\t", "\n", "`",]:
						for k in keywords:
							if match_tag(k, text, i, keyword=True):
								tokens.append(Token(MD.CODEBLOCK_KEYWORD, i, i + len(k) + 1, text[i] + k))
								i += len(k)
								key = True

								if k == "class":
									i += 1
									tokens.append(Token(MD.SPACE, i, i + 1, text[i]))
									i += 1
									index = 1
									while text[i + index] != ":":
										index += 1
									tokens.append(Token(MD.CODEBLOCK_CLASS, i, i + index + 1, text[i:i + index]))
									i += index - 1

								elif k == "def":
									i += 1
									tokens.append(Token(MD.SPACE, i, i + 1, text[i]))
									i += 1
									index = 1
									while text[i + index] != "(":
										index += 1
									tokens.append(Token(MD.CODEBLOCK_FUNCTION, i, i + index + 1, text[i:i + index]))
									i += index - 1
								

						for t in types:
							if match_tag(t, text, i, data_type=True):
								tokens.append(Token(MD.CODEBLOCK_TYPE, i, i + len(t) + 1, text[i] + t))
								i += len(t)
								key = True

						for f in flow:
							if match_tag(f, text, i, keyword=True):
								tokens.append(Token(MD.CODEBLOCK_FLOW, i, i + len(f) + 1, text[i] + f))
								i += len(f)
								key = True

						if not key:
							tokens.append(Token(MD.CODEBLOCK, i, i + 1, char))

					elif char in ["\"", "'"]:
						index = 1
						while text[i + index] not in ["\"", "'"]:
							index += 1
						tokens.append(Token(MD.CODEBLOCK_STRING, i, i + index + 1, text[i:i + index + 1]))
						i += index
					elif char in [";", ":", "(", ")", "{", "}", "[", "]", ".", ",", "+", "-", "*", "/", "<", ">", "\\", "&", "=", "!", "%"]:
						tokens.append(Token(MD.CODEBLOCK_SYMBOL, i, i + 1, char))
					elif char.isdigit():
						tokens.append(Token(MD.CODEBLOCK_DIGIT, i, i + 1, char))
					else:
						tokens.append(Token(MD.CODEBLOCK, i, i + 1, char))
				else:
					tokens.append(Token(MD.CODE, i, i + 1, char))
		elif formatBlock:
			if char == "`":
				tokens.append(Token(MD.FORMATBLOCK_END, i, i + 1))
				formatBlock = False
			else:
				tokens.append(Token(MD.FORMATBLOCK_TEXT, i, i + 1, char))
		elif heading:
			if char == "\n":
				tokens.append(Token(MD.HEADING_END, i, i + 1))
				heading = False
			else:
				tokens.append(Token(MD.HEADING_TEXT, i, i + 1, char))
		elif bold:
			if char == "*":
				bold = False
				tokens.append(Token(MD.BOLD_END, i, i + 2))
				i += 1
			else:
				tokens.append(Token(MD.BOLD, i, i + 1, char))
		elif block:
			if char == "\n":
				block = False
				tokens.append(Token(MD.BLOCKQUOTE_END, i, i + 1))
			else:
				tokens.append(Token(MD.BLOCKQUOTE_TEXT, i, i + 1, char))
		elif underline:
			if char == "_":
				underline = False
				tokens.append(Token(MD.UNDERLINE_END, i, i + 2))
				i += 1
			else:
				tokens.append(Token(MD.UNDERLINE, i, i + 1, char))
		elif italic:
			if char == "*":
				italic = False
				tokens.append(Token(MD.ITALIC_END, i, i + 1))
			else:
				tokens.append(Token(MD.ITALIC, i, i + 1, char))
		elif strike:
			if char == "~" and text[i + 1] == "~":
				strike = False
				tokens.append(Token(MD.STRIKE_END, i, i + 2))
				i += 1
			else:
				tokens.append(Token(MD.STRIKE, i, i + 1, char))
		elif check:
			if char == "\n":
				check = False
				tokens.append(Token(MD.CHECK_END, i, i + 1))
			else:
				tokens.append(Token(MD.CHECK_TEXT, i, i + 1, char))
		elif image:
			if char == "\n":
				image = False
			elif char == ")":
				tokens.append(Token(MD.IMAGE_PATH_END, i, i + 1))
			else:
				tokens.append(Token(MD.IMAGE_PATH_TEXT, i, i + 1, char))
		elif link:
			if char == "\n":
				link = False
			elif char == ")":
				tokens.append(Token(MD.LINK_PATH_END, i, i + 1))
			else:
				tokens.append(Token(MD.LINK_PATH_TEXT, i, i + 1, char))
		elif html:
			if char == ">":
				tokens.append(Token(MD.HTML_END, i, i + 1))
				html = False
			elif char == '"':
				if htmlAttribute:
					htmlAttribute = False
				else:
					htmlAttribute = True
				tokens.append(Token(MD.HTML_ATTRIBUTE_TEXT, i, i + 1, char))
			elif htmlAttribute:
				tokens.append(Token(MD.HTML_ATTRIBUTE_TEXT, i, i + 1, char))
			else:
				tokens.append(Token(MD.HTML_TEXT, i, i + 1, char))
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
				tokens.append(Token(MD.LIST_ITEM_TEXT, i, i + 1, text[i]))
			elif char in [" ", "\t", "\n"]:
				pass
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
					tokens.append(Token(MD.SPACE, i, i + 1))
					break
				elif c == "\n":
					warn(f"Line: {line}, Index: {i} -> Improperly formatted heading! You need a space after the # !")
					tokens.append(Token(MD.ERROR, i - hCount, i))
					break
				elif c == "#":
					hCount += 1
					if hCount > 6:
						warn(f"Line: {line}, Index: {i} -> Too many #! You can only use up to 6 # !")
						tokens.append(Token(MD.ERROR, i - hCount, i + 1))
				i += 1
			tokens.append(Token(MD.HEADING, i - hCount - 1, i + 1))
			heading = True
		elif char == "`":
			if text[i - 1].lower() == "f":
				tokens.pop()
				tokens.append(Token(MD.FORMAT, i - 1, i))
				if text[i + 1] != "\n":
					tokens.append(Token(MD.CODEBLOCK_BEGIN, i, i + 1))
					codeBlock = True
					index = 1
					language = ""
					while text[i + index] != "\n":
						language += text[i + index]
						index += 1
					tokens.append(Token(MD.FORMAT, i + 1, i + index + 1, language))
					i += index - 1
				else:
					tokens.append(Token(MD.FORMATBLOCK_BEGIN, i, i + 1))
					formatBlock = True
			else:
				tokens.append(Token(MD.CODE_BEGIN, i, i + 1))
				code = True
		elif char == ">":
			tokens.append(Token(MD.BLOCKQUOTE_BEGIN, i, i + 1))
			block = True
		elif char == "~":
			nextC = text[i + 1]
			if nextC == "~":
				tokens.append(Token(MD.STRIKE_BEGIN, i, i + 2))
				strike = True
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
		elif char == "!" and text[i + 1] == "[":
			index = i + 2
			tokens.append(Token(MD.IMAGE_ALT_BEGIN, i, i + 2))
			while True:
				c = text[index]
				if c == "]":
					tokens.append(Token(MD.IMAGE_ALT_END, index, index + 1))
					i = index
					if text[i + 1] == "(":
						tokens.append(Token(MD.IMAGE_PATH_BEGIN, i + 1, i + 2))
						image = True
						i += 1
					else:
						tokens.append(Token(MD.ERROR, i + 1, i + 2))
						warn(f"Line: {line}, Index: {i} -> Improper image formatting! Expected '('! Found '{char}'!")
					break
				elif c == "\n":
					tokens.append(Token(MD.ERROR, index, index + 1))
					print(f"Line: {line}, TotalChar: {i} -> Improper image formatting! Couldn't find the closing ']' bracket!")
					break
				else:
					tokens.append(Token(MD.IMAGE_ALT_TEXT, index, index + 1, c))
					index += 1
		elif char == "?" and text[i + 1] == "[":
			index = i + 2
			tokens.append(Token(MD.LINK_ALT_BEGIN, i, i + 2))
			while True:
				c = text[index]
				if c == "]":
					tokens.append(Token(MD.LINK_ALT_END, index, index + 1))
					i = index
					if text[i + 1] == "(":
						tokens.append(Token(MD.LINK_PATH_BEGIN, i + 1, i + 2)) 
						link = True
						i += 1
					else:
						tokens.append(Token(MD.ERROR, i + 1, i + 2))
						warn(f"Line: {line}, Index: {i} -> Improper link formatting! Expected '('! Found '{char}'!")
					break
				elif c == "\n":
					tokens.append(Token(MD.ERROR, index, index + 1))
					print(f"Line: {line}, TotalChar: {i} -> Improper link formatting! Couldn't find the closing ']' bracket!")
					break
				else:
					tokens.append(Token(MD.LINK_ALT_TEXT, index, index + 1, c))
					index += 1
		elif char == "<" and text[i + 1] == "<":
			tokens.append(Token(MD.HTML_BEGIN, i, i + 2))
			i += 1
			html = True
		else:
			tokens.append(Token(MD.TEXT, i, i + 1, char))
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