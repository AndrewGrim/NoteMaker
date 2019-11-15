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

"""
A very simple and naive markdown parser.
Reads a file a char at a time and writes the equivalent html to another file.
Currently supported markdown:
	headings
	bold
	italic
	underline
	strikethrough
	horizontal rule
	img
	link
	blockquote
	code
	checkboxes
	inline html
	unordered list(WIP) atm only 1 inner list supported

	todo:
		better ul
		ol
		code blocks ie ```code``` these should work across multiple lines
			later add support for synatx highlighting, prob just keywords using regex within the code block
		term definitions
		tables
		footnotes
"""

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

	def __init__(self, id: MD_ENUM, content: str = "", end: str = "") -> None:
		self.id = id
		self.content = content
		self.end = end

	
	def __str__(self) -> str:
		return f"\nToken:\n\tid:{self.id}\n\tcontent:{self.content}\n\tend:{self.end}\n"


	def __repr__(self) -> str:
		return self.__str__()


def parse(mdFile: str) -> List[Token]:
	"""
	This will read from the specified markdown file.
	Write the html to the same name with an html extension and
	make a css file again with the same name but .css
	"""

	tokens = []

	def fileSize(fname):
		statinfo = os.stat(fname)

		return statinfo.st_size

	#files = ["basic", "advanced_supported"]#, "advanced"]
	#for f in files: 
	f = os.path.splitext(mdFile)[0]
	r = open(f"{f}.md", "r")
	
	html = f[f.rfind("/") + 1:]
	w = open(f"Notes/html/{html}.html", "w")

	fSize = fileSize(f"{f}.md")
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
	# TODO should probably go back to a line by line read and check only the first index at first, more if needed
	# cause at the moment if i put a hash anywhere in text it will check if its a heading
	# even if its a quote or a coment or whatever
	# TODO add default styling and allow for custom styles
	css = f[f.rfind("/") + 1:]
	css = f"Notes/css/{css}.css"
	c = open(css, "w")
	style = open("css/default.css", "r").read()
	c.write(style)
	css = css.replace("Notes", "..")
	w.write(f'<link rel="stylesheet" href="{css}">\n\n\n')
	w.write('<div class="markdown-body">\n')
	while r.tell() < fSize:
		char = r.read(1)
		if char == "\n":
			line += 1

		if code:
			if char == "`":
				code = False
				if r.read(1) == "\n":
					lineEnd += "<br><br>"
					r.seek(r.tell() - 1)
				else:
					r.seek(r.tell() - 1)
			else:
				w.write(char)
		elif uList:
			if char == "\n" and lastC == "\n":
				uList = False
				w.write(lineEnd)
				lineEnd = ""
			elif char == "\n" and li:
				w.write("</li>")
				li = False
			elif char == "*":
				"""if lastC == " ":
					indent = 1
					startPos = r.tell()
					offset = 4
					r.seek(startPos - 2)
					while True:
						c = r.read(1)
						if c == "\n":
							break
						elif c == " ":
							r.seek(r.tell() - offset)
							offset += 1"""
				#if lastOffset == offset:
				if lastC == "\t" or lastC == " ":
					c = r.read(1)
					if c == " " and not innerList:
						w.write("\n<ul>\n<li>")
						li = True
						lineEnd = "\n</ul>\n\n"
						innerList = True
						lCount += 1
						lineEnd = "\n</ul>" * lCount
					elif c == " ":
						w.write("\n<li>")
						li = True
						lineEnd += "\n\n"
					else:
						r.seek(r.tell() - 1)
				else:
					w.write("\n<ul>\n<li>")
					li = True
					lCount += 1
					lineEnd = "\n</ul>" * lCount + "\n\n"
					innerList = False
				#lastOffset = offset
			else:
				w.write(char)
		elif html:
			if char == ">":
				html = False
				lineEnd = "<br><br>"
				if r.read(1) == "\n":
					pass
				else:
					r.seek(r.tell() - 1)
			w.write(char)
		elif char == "\n":
			if lineEnd != "":
				w.write(lineEnd)
				lineEnd = ""
				if check and r.read(1) == "\n":
					w.write("<br>")
					check = False
				elif check:
					check = False
				r.seek(r.tell() - 1)
			w.write("\n")
		elif char == "#":
			hCount = 1
			while True:
				c = r.read(1)
				if c == " ":
					break
				elif c == "\n":
					print(f"Line: {line}, TotalChar: {i} -> Improperly formatted heading!")
					break
				hCount += 1
			if hCount > 6:
				print(f"Line: {line}, TotalChar: {i} -> Heading number is too high!")
			else:
				tokens.append(Token(MD.HEADING))
				w.write(f'<h{hCount}>')
				lineEnd = f"</h{hCount}>"
		elif char == "*":
			nextC = r.read(1)
			if nextC == " ":
				w.write("<ul>\n<li>")
				lineEnd = "\n</ul>"
				uList = True
				li = True
				lCount += 1
			elif nextC not in ["\n", " ", "*"]:
				r.seek(r.tell() - 1)
				c = ""
				italic = ""
				new = ""
				while True:
					c = r.read(1)
					if c == "*":
						if r.read(1) == "\n":
							new = "<br><br>"
							r.seek(r.tell() - 1)
							break
						else:
							r.seek(r.tell() - 1)
							break
					elif c == "\n":
						print(f"Line: {line}, TotalChar: {i} -> Closing italic asterisk not found!")
						break
					else:
						italic += c
				w.write(f"<i>{italic}</i>{new}")
			elif nextC == "*":
				c = ""
				bold = ""
				new = ""
				while True:
					c = r.read(1)
					if c == "*":
						if r.read(1) == "*":
							if r.read(1) == "\n":
								new = "<br><br>"
								r.seek(r.tell() - 1)
								break
							else:
								r.seek(r.tell() - 1)
								break
						else:
							print(f"Line: {line}, TotalChar: {i} -> Closing bold asterisk not found!")
					elif c == "\n":
						print(f"Line: {line}, TotalChar: {i} -> Closing bold asterisk not found!")
						break
					else:
						bold += c
				w.write(f"<b>{bold}</b>{new}")
			elif nextC == "\n":
				print(f"Line: {line}, TotalChar: {i} -> newline following asterisk")
		elif char == "!":
			nextC = r.read(1)
			new = ""
			if nextC == "[":
				c = ""
				alt = ""
				while True:
					c = r.read(1)
					if c == "]":
						break
					elif c == "\n":
						print(f"Line: {line}, TotalChar: {i} -> Couldn't find the closing square bracket!")
						break
					else:
						alt += c
				nextC = r.read(1)
				if nextC == "(":
					img = ""
					while True:
						c = r.read(1)
						if c == ")":
							if r.read(1) == "\n":
								new = "<br><br>"
								r.seek(r.tell() - 1)
								break
							else:
								r.seek(r.tell() - 1)
								break
						elif c == "\n":
							print(f"Line: {line}, TotalChar: {i} -> Couldn't find the closing parenthases!")
							break
						else:
							img += c
					w.write(f'<img src="{img}" alt="{alt}">{new}')
		elif char == "[":
			text = ""
			new = ""
			while True:
				c = r.read(1)
				if c == "]":
					break
				elif c == "\n":
					print(f"Line: {line}, TotalChar: {i} -> Couldn't find the closing square bracket!")
					break
				else:
					text += c
			nextC = r.read(1)
			if nextC == "(":
				link = ""
				while True:
					c = r.read(1)
					if c == ")":
						if r.read(1) == "\n":
							new = "<br><br>"
							r.seek(r.tell() - 1)
							break
						else:
							r.seek(r.tell() - 1)
							break
					elif c == "\n":
						print(f"Line: {line}, TotalChar: {i} -> Couldn't find the closing parenthases!")
						break
					else:
						link += c
				w.write(f'<a href="{link}">{text}</a>{new}')
		elif char == ">":
			if lastC in [" ", "\n", "\t"]:
				c = ""
				block = ""
				while True:
					c = r.read(1)
					if c == "\n":
						break
					else:
						block += c
				w.write(f"<blockquote>{block}</blockquote>\n")
			else:
				print(f"Line: {line}, TotalChar: {i} -> Improperly formatted blockquote!")
		elif char == "`":
			w.write("<code>")
			lineEnd = "</code>"
			code = True
		elif char == "-":
			nextC = r.read(1)
			if nextC == " ":
				c = r.read(1)
				if c == "[":
					checked = ""
					c = r.read(1)
					if c == "x" and r.read(1) == "]":
						checked = "checked"
					elif c == " " and r.read(1) == "]":
						pass
					else:
						print(f"Line: {line}, TotalChar: {i} -> Improperly formatted checklist! Missing space or x in brackets!")
					w.write(f'<input type="checkbox" {checked}>')
					lineEnd = "<br>"
					check = True
			elif nextC == "-":
				c = r.read(1)
				if c == "-":
					w.write("<hr>")
				else:
					print(f"Line: {line}, TotalChar: {i} -> Improperly formatted horizontal rule!")
			else:
				print(f"Line: {line}, TotalChar: {i} -> Improperly formatted checklist!")
		elif char == "~":
			nextC = r.read(1)
			if nextC == "~":
				new = ""
				text = ""
				while True:
					c = r.read(1)
					if c == "~":
						if r.read(1) == "~":
							if r.read(1) == "\n":
								new = "<br><br>"
								r.seek(r.tell() - 1)
								break
							else:
								r.seek(r.tell() - 1)
								break
						else:
							print(f"Line: {line}, TotalChar: {i} -> Improperly formatted strikethrough!")
					elif c == "\n":
						print(f"Line: {line}, TotalChar: {i} -> Couldn't find the closing ~!")
						break
					else:
						text += c
				w.write(f'<strike>{text}</strike>{new}')
			else:
				print(f"Line: {line}, TotalChar: {i} -> Improperly formatted strikethrough!")
		elif char == "_":
			nextC = r.read(1)
			if nextC == "_":
				new = ""
				text = ""
				while True:
					c = r.read(1)
					if c == "_":
						if r.read(1) == "_":
							if r.read(1) == "\n":
								new = "<br><br>"
								r.seek(r.tell() - 1)
								break
							else:
								r.seek(r.tell() - 1)
								break
						else:
							print(f"Line: {line}, TotalChar: {i} -> Improperly formatted underline!")
					elif c == "\n":
						print(f"Line: {line}, TotalChar: {i} -> Couldn't find the closing _!")
						break
					else:
						text += c
				w.write(f'<u>{text}</u>{new}')
			else:
				print(f"Line: {line}, TotalChar: {i} -> Improperly formatted underline!")
		elif char == "<":
			w.write(char)
			html = True
		else:
			w.write(char)
		lastC = char
		i += 1
	w.write('</div>\n')

	return tokens

if __name__ == "__main__":
	args = sys.argv
	if len(args) == 2:
		print(parse(args[1]))
	elif len(args) == 1:
		print("You need to specify the file to parse!")
		print("""
	Usage:
		ParseMarkdown <file.md>
	""")
	else:
		print("The program only supports one file argument atm!")