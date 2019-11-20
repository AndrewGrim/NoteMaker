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
	f = open("Notes/tmp.html", "w")
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

# TODO inserting to many line breaks!
def parse(tokens: List[LexerToken]) -> None:
	html = []
	i = 0
	linkText = ""
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
		elif t.id == MD.CHECKED:
			html.append(f'<input type="checkbox" checked>')
		elif t.id == MD.UNCHECKED:
			html.append(f'<input type="checkbox">')
		elif t.id == MD.CHECK_TEXT:
			html.append(t.content)
		elif t.id == MD.CHECK_END:
			html.append("<br>")
		elif t.id == MD.BOLD_BEGIN:
			html.append("<b>")
		elif t.id == MD.BOLD_END:
			html.append("</b>")
		elif t.id == MD.BOLD:
			html.append(t.content)
		elif t.id == MD.NEWLINE:
			html.append("\n<br>")
		elif t.id == MD.SPACE:
			html.append(" ")
		elif t.id == MD.TAB:
			html.append("\t")
		elif t.id == MD.ITALIC_BEGIN:
			html.append("<i>")
		elif t.id == MD.ITALIC_END:
			html.append("</i>")
		elif t.id == MD.ITALIC:
			html.append(t.content)
		elif t.id == MD.STRIKE_BEGIN:
			html.append("<strike>")
		elif t.id == MD.STRIKE_END:
			html.append("</strike>")
		elif t.id == MD.STRIKE:
			html.append(t.content)
		elif t.id == MD.CODE_BEGIN:
			html.append("<code>")
		elif t.id == MD.CODE_END:
			html.append("</code>")
		elif t.id == MD.CODE:
			html.append(t.content)
		elif t.id == MD.UNDERLINE_BEGIN:
			html.append("<u>")
		elif t.id == MD.UNDERLINE_END:
			html.append("</u>")
		elif t.id == MD.UNDERLINE:
			html.append(t.content)
		elif t.id == MD.HORIZONTAL_RULE:
			html.append("<hr>")
		elif t.id == MD.BLOCKQUOTE_BEGIN:
			html.append("<blockquote>")
		elif t.id == MD.BLOCKQUOTE_END:
			html.append("</blockquote>")
		elif t.id == MD.BLOCKQUOTE_TEXT:
			html.append(t.content)
		elif t.id == MD.LINK_ALT_BEGIN:
			html.append('<a ')
		elif t.id == MD.LINK_ALT_TEXT:
			linkText += t.content
		elif t.id == MD.LINK_PATH_BEGIN:
			html.append('href="')
		elif t.id == MD.LINK_PATH_END:
			html.append(f'">{linkText}</a><br>')
			linkText = ""
		elif t.id == MD.LINK_PATH_TEXT:
			html.append(t.content)
		elif t.id == MD.IMAGE_ALT_BEGIN:
			html.append('<img alt="')
		elif t.id == MD.IMAGE_ALT_END:
			html.append('" ')
		elif t.id == MD.IMAGE_ALT_TEXT:
			html.append(t.content)
		elif t.id == MD.IMAGE_PATH_BEGIN:
			html.append('src="')
		elif t.id == MD.IMAGE_PATH_END:
			html.append(f'"><br>')
		elif t.id == MD.IMAGE_PATH_TEXT:
			html.append(t.content)
		elif t.id == MD.ULIST_BEGIN:
			html.append(f'<ul>')
		elif t.id == MD.ULIST_END:
			html.append(f'</ul>')
		elif t.id == MD.OLIST_BEGIN:
			html.append(f'<ol>')
		elif t.id == MD.OLIST_END:
			html.append(f'</ol>')
		elif t.id == MD.LIST_ITEM_BEGIN:
			html.append(f'<li>')
		elif t.id == MD.LIST_ITEM_END:
			html.append(f'</li>')
		elif t.id == MD.LIST_ITEM_TEXT:
			html.append(t.content)
		elif t.id == MD.HTML_BEGIN:
			html.append("<")
		elif t.id == MD.HTML_END:
			html.append(">")
		elif t.id == MD.HTML_TEXT:
			html.append(t.content)
		elif t.id == MD.HTML_ATTRIBUTE_TEXT:
			html.append(t.content)
		elif t.id == MD.TEXT:
			html.append(t.content)
		i += 1
	generateHTML(html)