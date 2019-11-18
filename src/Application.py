import time
import os
import sys
import platform
import subprocess
import keyword

import wx
import wx.html2 as webview
import wx.stc as stc

from ParseMarkdown import parse
from Lexer import *
from Styles import *
from TokenTypes import *
from Token import *
from Debug import *

class Application(wx.Frame):

	def __init__(self, *args, **kw):
		super(Application, self).__init__(*args, **kw)
		if platform.system() == "Windows":
			os.system("color")

		args = sys.argv
		if len(args) == 2:
			self.currentAMD = args[1]
		else:
			warn("no file passed")
			self.currentAMD = "Notes/test.amd" # at some point change this load nothing
		self.currentHTML = f"{os.getcwd()}/Notes/html/test.html"

		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.edit = stc.StyledTextCtrl(panel)
		#self.edit.SetLexer(stc.STC_LEX_MARKDOWN)
		self.edit.SetMarginType(1, stc.STC_MARGIN_NUMBER)
		self.edit.SetMarginWidth(1, 30)
		self.edit.SetWrapMode(stc.STC_WRAP_WORD)
		self.edit.SetSelBackground(True, "#384539")
		self.edit.SetCaretForeground("WHITE")
		self.edit.SetBackgroundColour("WHITE")
		self.edit.SetWhitespaceSize(2)
		# TODO implement line and column in status bar, and line endings 
		self.edit.SetTabWidth(4)
		#self.edit.SetUseTabs(True) true by default make it an option
		self.setupStyling()
		self.edit.Bind(wx.EVT_KEY_UP, self.onKeyUp)
		self.edit.Bind(stc.EVT_STC_UPDATEUI, self.onUpdateUI)
		#self.setColors()

		sizer.Add(self.edit, 4, wx.EXPAND)

		self.wv = webview.WebView.New(panel)
		sizer.Add(self.wv, 5, wx.EXPAND)

		panel.SetSizer(sizer)

		self.edit.LoadFile(self.currentAMD)
		self.wv.LoadURL(self.currentHTML)

		self.makeMenuBar()
		self.SetSize((1280, 720))
		self.Center()
		icon = wx.Icon("images/amd.png")
		self.SetIcon(icon)
		self.SetTitle("NoteMaker")
		self.status = self.CreateStatusBar()
		self.status.SetFieldsCount(7)
		w = self.GetSize()[0]
		w = w - 7 * 100
		self.status.SetStatusWidths([100, 100, 100, 100, w, 100, 100])

		self.onKeyUp(wx.KeyEvent(wx.wxEVT_NULL))
		self.Bind(wx.EVT_SIZE, self.onSize)
		self.Show()


	def onSize(self, event):
		w = self.GetSize()[0]
		w = w - 7 * 100
		self.status.SetStatusWidths([100, 100, 100, 100, w, 100, 100])
		event.Skip()

	
	def onUpdateUI(self, event):
		self.Freeze()
		selectionBegin: int = self.edit.GetSelection()[0]
		selectionEnd: int = self.edit.GetSelection()[1]
		selectedCount: int = 0
		currentLine: int = self.edit.GetCurrentLine() + 1 # because lines start at 0, but not in the margin line count
		currentPosition: int = self.edit.GetCurrentPos()
		currentColumn: int = self.edit.GetColumn(currentPosition)
		if selectionBegin != selectionEnd:
			selectedCount = selectionEnd - selectionBegin
		self.SetStatusText(f"Line: {currentLine}", 0)
		self.SetStatusText(f"Column: {currentColumn}", 1)
		self.SetStatusText(f"Position: {currentPosition}", 2)
		self.SetStatusText(f"Selected: {selectedCount}", 3)
		self.SetStatusText(f"UTF-8", 5)
		self.SetStatusText(f"LF", 6)
		self.Thaw()

	def onKeyUp(self, event):
		start = time.time()
		tokens = lex(self.edit.GetValue())
		error = False
		keywords = (" ".join(keyword.kwlist) + " self").split()
		for i, t in enumerate(tokens):
			#if i == 20:
			#	break
			""" if t.id in [MD.IMAGE_PATH_BEGIN]:
				debug(t) """
			self.edit.StartStyling(t.begin, 0xff)
			if not error:
				if t.id == MD.ERROR:
					self.edit.SetStyling(t.end - t.begin, INDICATOR.ERROR | STYLE.TEXT)
					error = True
				elif t.id == MD.HEADING:
					self.edit.SetStyling(t.end - t.begin, STYLE.HEADING)
				elif t.id in [MD.SPACE, MD.TAB, MD.NEWLINE]:
					self.edit.SetStyling(t.end - t.begin, STYLE.HIDDEN)
				elif t.id in [MD.CODE, MD.CODE_BEGIN, MD.CODE_END]:
					self.edit.SetStyling(t.end - t.begin, STYLE.CODE)
				elif t.id == MD.BLOCKQUOTE:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id in [MD.STRIKE_BEGIN, MD.STRIKE_END]:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id == MD.STRIKE:
					self.edit.SetStyling(t.end - t.begin, STYLE.STRIKE)
				elif t.id in [MD.BOLD_BEGIN, MD.BOLD_END]:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id == MD.BOLD:
					self.edit.SetStyling(t.end - t.begin, STYLE.BOLD)
				elif t.id in [MD.UNDERLINE_BEGIN, MD.UNDERLINE_END]:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id == MD.UNDERLINE:
					self.edit.SetStyling(t.end - t.begin, STYLE.UNDERLINE)
				elif t.id in [MD.ITALIC_BEGIN, MD.ITALIC_END]:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id == MD.ITALIC:
					self.edit.SetStyling(t.end - t.begin, STYLE.ITALIC)
				elif t.id == MD.HORIZONTAL_RULE:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id == MD.LIST_ITEM_BEGIN:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id in [MD.ULIST_END, MD.OLIST_END]:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id in [MD.CHECKED, MD.UNCHECKED]:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id in [MD.IMAGE_ALT_BEGIN, MD.IMAGE_ALT_END, MD.IMAGE_PATH_BEGIN, MD.IMAGE_PATH_END]:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id in [MD.IMAGE_ALT_TEXT, MD.IMAGE_PATH_TEXT]:
					self.edit.SetStyling(t.end - t.begin, STYLE.IMAGE)
				elif t.id in [MD.LINK_ALT_BEGIN, MD.LINK_ALT_END, MD.LINK_PATH_BEGIN, MD.LINK_PATH_END]:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id in [MD.LINK_ALT_TEXT, MD.LINK_PATH_TEXT]:
					self.edit.SetStyling(t.end - t.begin, STYLE.LINK)
				elif t.id in [MD.HTML_BEGIN, MD.HTML_END]:
					self.edit.SetStyling(t.end - t.begin, STYLE.SYMBOL)
				elif t.id == MD.HTML_TEXT:
					self.edit.SetStyling(t.end - t.begin, STYLE.HTML)
				elif t.id == MD.HTML_ATTRIBUTE_TEXT:
					self.edit.SetStyling(t.end - t.begin, STYLE.HTML_ATTRIBUTE)
				else:
					self.edit.SetStyling(t.end - t.begin, STYLE.TEXT)
			elif t.id == MD.NEWLINE:
				error = False

		# Doesnt work all that well
		# most of the keywords do get highlighted but not all of them
		# initially i though this was because i had a ` in my code which would disable the highlight
		# but this doesnt seem to be the case	
		"""codeBegin = -1
		codeEnd = -1
		for i, t in enumerate(tokens):
			if t.id == MD.CODE_BEGIN:
				codeBegin = i
			elif t.id == MD.CODE_END:
				codeEnd = i
		print("code: ", codeBegin)
		print("len: ", self.edit.GetLength())
		for key in keywords:
			begin = self.edit.FindText(codeBegin, codeEnd, key)
			if begin != -1:
				self.edit.StartStyling(begin, 0xff)
				self.edit.SetStyling(len(key), 6)"""
		end = time.time()
		info(f"Lex and highlight time: {round(end - start, 2)}")
		event.Skip()


	def makeMenuBar(self):
		fileMenu = wx.Menu()
		saveItem = fileMenu.Append(-1, "&Save\tCtrl-S")
		openItem = fileMenu.Append(-1, "&Open\tCtrl-O")
		reloadItem = fileMenu.Append(-1, "&Reload\tCtrl-R")
		hiddenItem = fileMenu.Append(-1, "&Show Hidden Symbols\tCtrl-D")
		
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.onSave, saveItem)
		self.Bind(wx.EVT_MENU, self.onOpen, openItem)
		self.Bind(wx.EVT_MENU, self.onReload, reloadItem)
		self.Bind(wx.EVT_MENU, self.onShowHidden, hiddenItem)


	def onSave(self, event):
		try:
			f = open(self.currentAMD, "wb")
			f.write(self.edit.GetValue().encode("UTF-8").replace(b"\r\n", b"\n")) # TODO line endings, encoding settings
			f.close() 
		except:
			fail("Could not save file!")
			self.SetStatusText(f"Could not save file: {self.currentAMD}!")

		start = time.time()
		#parse(self.currentAMD) # currently disabled because the parser hasnt been updated
		end = time.time()
		print(f"Parse time: {round(end - start, 2)}s")
		self.wv.Reload()
		self.edit.SetFocus()


	def onOpen(self, event):
		fd = wx.FileDialog(self, "Open...", wildcard="Markdown files (*.md)|*.md", style=wx.FD_OPEN)

		if fd.ShowModal() == wx.ID_CANCEL:
			return     

		pathname = fd.GetPath()
		try:
			f = open(pathname, 'r')
			f.close()
			self.edit.LoadFile(pathname)
			parse(pathname)
			bName = os.path.basename(os.path.splitext(pathname)[0])
			html = f"{os.getcwd()}/Notes/html/{bName}.html"
			self.wv.LoadURL(html)
		except IOError:
			wx.LogError("Cannot open the specified file '%s'." % pathname)

	
	def onReload(self, event):
		self.wv.Reload()
		self.edit.SetFocus()


	def onShowHidden(self, event):
		if self.edit.GetViewWhiteSpace() == 0:	
			self.edit.SetViewWhiteSpace(True)
			self.edit.SetViewEOL(True)
		else:
			self.edit.SetViewWhiteSpace(False)
			self.edit.SetViewEOL(False)


	def setupStyling(self):
		faces = {
			'times': 'Times New Roman',
			'mono' : 'Courier New',
			'helv' : 'Arial',
			'other': 'Comic Sans MS',
			'size' : 10,
			'size2': 8,
		}

		self.edit.StyleSetSpec(stc.STC_STYLE_DEFAULT, "back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleClearAll()
		self.edit.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "fore:#928374,back:#212121,face:%(mono)s,size:%(size2)d" % faces)
		self.edit.StyleSetSpec(0, "fore:#d5c4a1,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(1, "fore:#EFCD1E,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(3, "fore:#00FF00,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(4, "fore:#b8bb26,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(5, "fore:#81ac71,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(6, "fore:#ff00ff,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(7, "fore:#e44533,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(11, "fore:#7d9d90,italic,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(12, "fore:#cb8296,size:%(size)d" % faces)
		self.edit.StyleSetSpec(13, "fore:#cb8296,size:%(size)d" % faces)
		self.edit.StyleSetSpec(14, "fore:#cb8296,size:%(size)d" % faces)
		self.edit.StyleSetSpec(15, "fore:#d9a62e,size:%(size)d" % faces)
		# maybe have additional styles for the inside which is bold/underlined
		# and maybe lex these same way that i do code?
		self.edit.StyleSetSpec(8, "fore:#d9a62e,bold,size:%(size)d" % faces)
		self.edit.StyleSetSpec(9, "fore:#d9a62e,underline,size:%(size)d" % faces)
		self.edit.IndicatorSetStyle(0, stc.STC_INDIC_SQUIGGLE)
		self.edit.IndicatorSetForeground(0, wx.RED)


	def setColors(self):
		# custom highlight link and html

		faces = {
			'times': 'Times New Roman',
			'mono' : 'Courier New',
			'helv' : 'Arial',
			'other': 'Comic Sans MS',
			'size' : 10,
			'size2': 8,
		}

		self.edit.StyleSetSpec(stc.STC_STYLE_DEFAULT, "back:#282828,face:%(mono)s,size:%(size)d" % faces)
		#self.edit.StyleSetSpec(0, "fore:#FF00FF,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		#self.edit.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleClearAll()  # Reset all to be like the default

		self.edit.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "fore:#928374,back:#212121,face:%(mono)s,size:%(size2)d" % faces)
		self.edit.StyleSetSpec(stc.STC_STYLE_INDENTGUIDE, "fore:#FF00FF,back:#FF0000,bold")
		self.edit.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
		self.edit.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
		self.edit.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#FFFFFF,back:#FF0000,bold")

		self.edit.StyleSetSpec(stc.STC_MARKDOWN_DEFAULT, "fore:#d5c4a1,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_ULIST_ITEM, "fore:#81ac71,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_OLIST_ITEM, "fore:#81ac71,bold,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_BLOCKQUOTE, "fore:#81ac71,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_HRULE, "fore:#81ac71,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_LINK, "fore:#cb8296,bold,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_CODEBK, "bold,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_CODE, "fore:#b8bb26,face:%(other)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_CODE2, "fore:#b8bb26,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_STRONG1, "fore:#d9a62e,bold,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_STRONG2, "fore:#d9a62e,underline,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_EM1, "fore:#7d9d90,italic,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_EM2, "fore:#7d9d90,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_STRIKEOUT, "fore:#e44533,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_PRECHAR, "fore:#FFFFFF,face:%(mono)s,back:#282828,eol,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_HEADER1, "fore:#EFCD1E,face:%(mono)s,back:#282828,eol,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_HEADER2, "fore:#EFCD1E,face:%(mono)s,back:#282828,eol,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_HEADER3, "fore:#EFCD1E,face:%(mono)s,back:#282828,eol,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_HEADER4, "fore:#EFCD1E,face:%(mono)s,back:#282828,eol,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_HEADER5, "fore:#EFCD1E,face:%(mono)s,back:#282828,eol,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_HEADER6, "fore:#EFCD1E,face:%(mono)s,back:#282828,eol,size:%(size)d" % faces)

		self.edit.SetSelBackground(True, "#384539")
		self.edit.SetCaretForeground("WHITE")
		self.edit.SetBackgroundColour("GRAY")


if __name__ == '__main__':
	start = time.time()
	app = wx.App()
	frm = Application(None)
	end = time.time()
	info(f"Application load time: {round(end - start, 2)}s")
	app.MainLoop()