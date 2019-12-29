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

def generateHTML(htmlTags: List[str], html: str, css: str) -> None:
	f = open(html, "w")
	f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
<title>Document</title>
</head>
	""")
	if os.path.exists("css/default.css"):
		style = open("css/default.css", "r").read()
	else:
		style = open(f"{css}css/default.css", "r").read()
	f.write(f"<style>\n{style}\n</style>\n")
	f.write("<body>")
	f.write('<div class="markdown-body">')
	for item in htmlTags:
		f.write(item)
	f.write("</div>")
	f.write("</body>")
	f.write("</html>")
	f.close()

# TODO inserting to many line breaks!
def parse(tokens: List[LexerToken], html: str, css: str) -> None:
	htmlTags = []
	i = 0
	linkText = ""
	while i < len(tokens):
		t = tokens[i]
		if t.id == MD.HEADING:
			htmlTags.append(f"<h{t.end - t.begin - 2}>")
		elif t.id == MD.HEADING_TEXT:
			htmlTags.append(t.content)
		elif t.id == MD.HEADING_END:
			token = None
			tt = None
			index = 1
			while token != MD.HEADING:
				token = tokens[i - index].id
				if token == MD.HEADING:
					tt = tokens[i - index]
				index += 1
			htmlTags.append(f"</h{tt.end - tt.begin - 2}>")
		elif t.id == MD.CHECKED:
			htmlTags.append(f'<input type="checkbox" checked>')
		elif t.id == MD.UNCHECKED:
			htmlTags.append(f'<input type="checkbox">')
		elif t.id == MD.CHECK_TEXT:
			htmlTags.append(t.content)
		elif t.id == MD.CHECK_END:
			htmlTags.append("<br>")
		elif t.id == MD.BOLD_BEGIN:
			htmlTags.append("<b>")
		elif t.id == MD.BOLD_END:
			htmlTags.append("</b>")
		elif t.id == MD.BOLD:
			htmlTags.append(t.content)
		elif t.id == MD.NEWLINE:
			htmlTags.append("\n<br>")
		elif t.id == MD.SPACE:
			htmlTags.append(" ")
		elif t.id == MD.TAB:
			htmlTags.append("\t")
		elif t.id == MD.ITALIC_BEGIN:
			htmlTags.append("<i>")
		elif t.id == MD.ITALIC_END:
			htmlTags.append("</i>")
		elif t.id == MD.ITALIC:
			htmlTags.append(t.content)
		elif t.id == MD.STRIKE_BEGIN:
			htmlTags.append("<strike>")
		elif t.id == MD.STRIKE_END:
			htmlTags.append("</strike>")
		elif t.id == MD.STRIKE:
			htmlTags.append(t.content)
		elif t.id == MD.CODE_BEGIN:
			htmlTags.append("<code>")
		elif t.id == MD.CODE_END:
			htmlTags.append("</code>")
		elif t.id == MD.CODE_BLOCK_BEGIN:
			htmlTags.append("<code><pre>")
		elif t.id == MD.CODE_BLOCK_END:
			htmlTags.append("</pre></code>")
		elif t.id == MD.CODE:
			htmlTags.append(t.content)
		elif t.id == MD.UNDERLINE_BEGIN:
			htmlTags.append("<u>")
		elif t.id == MD.UNDERLINE_END:
			htmlTags.append("</u>")
		elif t.id == MD.UNDERLINE:
			htmlTags.append(t.content)
		elif t.id == MD.HORIZONTAL_RULE:
			htmlTags.append("<hr>")
		elif t.id == MD.BLOCKQUOTE_BEGIN:
			htmlTags.append("<blockquote>")
		elif t.id == MD.BLOCKQUOTE_END:
			htmlTags.append("</blockquote>")
		elif t.id == MD.BLOCKQUOTE_TEXT:
			htmlTags.append(t.content)
		elif t.id == MD.LINK_ALT_BEGIN:
			htmlTags.append('<a ')
		elif t.id == MD.LINK_ALT_TEXT:
			linkText += t.content
		elif t.id == MD.LINK_PATH_BEGIN:
			htmlTags.append('href="')
		elif t.id == MD.LINK_PATH_END:
			htmlTags.append(f'">{linkText}</a><br>')
			linkText = ""
		elif t.id == MD.LINK_PATH_TEXT:
			htmlTags.append(t.content)
		elif t.id == MD.IMAGE_ALT_BEGIN:
			htmlTags.append('<img alt="')
		elif t.id == MD.IMAGE_ALT_END:
			htmlTags.append('" ')
		elif t.id == MD.IMAGE_ALT_TEXT:
			htmlTags.append(t.content)
		elif t.id == MD.IMAGE_PATH_BEGIN:
			htmlTags.append('src="')
		elif t.id == MD.IMAGE_PATH_END:
			htmlTags.append(f'"><br>')
		elif t.id == MD.IMAGE_PATH_TEXT:
			htmlTags.append(t.content)
		elif t.id == MD.ULIST_BEGIN:
			htmlTags.append(f'<ul>')
		elif t.id == MD.ULIST_END:
			htmlTags.append(f'</ul>')
		elif t.id == MD.OLIST_BEGIN:
			htmlTags.append(f'<ol>')
		elif t.id == MD.OLIST_END:
			htmlTags.append(f'</ol>')
		elif t.id == MD.LIST_ITEM_BEGIN:
			htmlTags.append(f'<li>')
		elif t.id == MD.LIST_ITEM_END:
			htmlTags.append(f'</li>')
		elif t.id == MD.LIST_ITEM_TEXT:
			htmlTags.append(t.content)
		elif t.id == MD.HTML_BEGIN:
			htmlTags.append("<")
		elif t.id == MD.HTML_END:
			htmlTags.append(">")
		elif t.id == MD.HTML_TEXT:
			htmlTags.append(t.content)
		elif t.id == MD.HTML_ATTRIBUTE_TEXT:
			htmlTags.append(t.content)
		elif t.id == MD.KEYWORD:
			htmlTags.append(f'<div class="keyword">{t.content}</div>')
		elif t.id == MD.TEXT:
			htmlTags.append(t.content)
		i += 1
	generateHTML(htmlTags, html, css)