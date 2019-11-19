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

def generateHTML(html: List[str]):
	try:
		os.remove("tmp.html")
	except Exception as e:
		print(e)
	f = open("tmp.html", "w")
	f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
<title>Document</title>
</head>
	""")
	style = open("css/default.css", "r").read()
	f.write(f"<style>\n{style}\n</style>\n")
	f.write("<body>")
	f.write('<div class="markdown-body">')
	for item in html:
		f.write(item)
	f.write("</div>")
	f.write("</body>")
	f.write("</html>")
	f.close()


def parse(tokens: List[LexerToken]) -> None:
	html = []
	i = 0
	while i < len(tokens):
		t = tokens[i]
		if t.id == MD.HEADING:
			html.append(f"<h{t.end - t.begin - 2}>")
		elif t.id == MD.HEADING_TEXT:
			html.append(t.content)
		elif t.id == MD.HEADING_END:
			token = None
			tt = None
			index = 1
			while token != MD.HEADING:
				token = tokens[i - index].id
				if token == MD.HEADING:
					tt = tokens[i - index]
				index += 1
			html.append(f"</h{tt.end - tt.begin - 2}>")
		i += 1
	generateHTML(html)