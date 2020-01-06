import time
import os
import sys
import platform
import subprocess
import keyword
import multiprocessing as mp

import wx
import wx.html2 as webview
import wx.stc as stc
from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
from asyncio.events import get_event_loop

from Lexer import *
from Styles import *
from TokenTypes import *
from Token import *
from Debug import *
from Parser import *

import lexer


class Application(wx.Frame):

	def __init__(self, *args, **kw):
		super(Application, self).__init__(*args, **kw)
		if platform.system() == "Windows":
			os.system("color")

		args = sys.argv
		self.exeDir = args[0].replace(os.path.basename(args[0]), "")


		self.currentAMD = None
		if len(args) == 2:
			self.currentAMD = args[1]
			self.html = f"{os.getcwd()}/tmp.html"
		else:
			self.html = f"{os.getcwd()}/Notes/tmp.html"
			f = open(self.html, "w")
			f.close()

		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.edit = stc.StyledTextCtrl(panel)
		self.edit.SetMarginType(1, stc.STC_MARGIN_NUMBER)
		self.edit.SetMarginWidth(1, 30)
		self.edit.SetWrapMode(stc.STC_WRAP_WORD)
		self.edit.SetSelBackground(True, "#384539")
		self.edit.SetCaretForeground("WHITE")
		self.edit.SetBackgroundColour("WHITE")
		self.edit.SetWhitespaceSize(2)
		# TODO implement line and column in status bar, and line endings 
		self.edit.SetTabWidth(2)
		self.edit.SetIndent(2)
		self.edit.SetUseTabs(False) # true by default make it an option
		self.setupStyling()

		self.edit.Bind(wx.EVT_KEY_UP, self.onKeyUp)
		self.edit.Bind(stc.EVT_STC_UPDATEUI, self.onUpdateUI)

		sizer.Add(self.edit, 4, wx.EXPAND)

		self.wv = webview.WebView.New(panel)
		sizer.Add(self.wv, 5, wx.EXPAND)

		panel.SetSizer(sizer)

		if self.currentAMD != None:
			try:
				self.edit.LoadFile(self.currentAMD)
			except:
				fail(f"Unable to load the file: {self.currentAMD}")
		
		if self.currentAMD != None:
			try:
				self.wv.LoadURL(self.html)
			except:
				fail(f"Unable to load the html file: {self.html}")

		self.makeMenuBar()
		self.SetSize((1280, 720))
		self.Center()
		if os.path.exists("images/amd.png"):
			icon = wx.Icon("images/amd.png")
		else:
			icon = wx.Icon(args[0].replace(os.path.basename(args[0]), "images/amd.png"))
		self.SetIcon(icon)
		self.SetTitle("NoteMaker")
		self.status = self.CreateStatusBar()
		self.status.SetFieldsCount(7)
		w = self.GetSize()[0]
		w = w - 7 * 100
		self.status.SetStatusWidths([100, 100, 100, 100, w, 100, 100])
		self.onKeyUp(wx.KeyEvent(wx.wxEVT_NULL))
		self.Bind(wx.EVT_SIZE, self.onSize)
		self.Bind(wx.EVT_CLOSE, self.onClose)
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
		#start = time.time()
		tokens = lexer.regex_lex(self.edit.GetValue())
		#end = time.time()
		#print(f"reg lex: {end - start}")
		#start = time.time()
		for t in tokens:
			self.edit.StartStyling(t.begin, 0xff)
			self.edit.SetStyling(t.end - t.begin, t.id)
		#end = time.time()
		#print(f"color: {end - start}")
		event.Skip()


	def makeMenuBar(self):
		fileMenu = wx.Menu()
		newItem = fileMenu.Append(-1, "&New\tCtrl-N")
		saveItem = fileMenu.Append(-1, "&Save\tCtrl-S")
		openItem = fileMenu.Append(-1, "&Open\tCtrl-O")
		reloadItem = fileMenu.Append(-1, "&Reload\tCtrl-R")
		hiddenItem = fileMenu.Append(-1, "&Show Hidden Symbols\tCtrl-D")
		quitItem = fileMenu.Append(-1, "&Quit\tCtrl-Q")
		
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.onNew, newItem)
		self.Bind(wx.EVT_MENU, self.onSave, saveItem)
		self.Bind(wx.EVT_MENU, self.onOpen, openItem)
		self.Bind(wx.EVT_MENU, self.onReload, reloadItem)
		self.Bind(wx.EVT_MENU, self.onShowHidden, hiddenItem)
		self.Bind(wx.EVT_MENU, self.onQuit, quitItem)

	
	def onQuit(self, event):
		sys.exit()


	def onNew(self, event):
		self.currentAMD = None
		self.edit.ClearAll()
		open(self.html, "w").write("")
		self.wv.LoadURL(self.html)


	def onSave(self, event):
		if self.currentAMD != None:
			f = open(self.currentAMD, "wb")
			f.write(self.edit.GetValue().encode("UTF-8").replace(b"\r\n", b"\n")) # TODO line endings, encoding settings
			f.close() 
		else:
			fileDialog = wx.FileDialog(self, "Save As...", wildcard="AlmostMarkdown (*.amd)|*.amd", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return     

			self.currentAMD = fileDialog.GetPath()
			try:
				f = open(self.currentAMD, "wb")
				f.write(self.edit.GetValue().encode("UTF-8").replace(b"\r\n", b"\n")) # TODO line endings, encoding settings
				f.close() 
			except IOError:
				fail(f"Cannot save current data in file '{self.currentAMD}'.")

		if self.currentAMD != None:
			self.wv.LoadURL(self.html)
		else:
			self.onReload(None)
		self.edit.SetFocus()


	def onOpen(self, event):
		fd = wx.FileDialog(self, "Open...", wildcard="AlmostMarkdown files (*.amd)|*.amd", style=wx.FD_OPEN)

		if fd.ShowModal() == wx.ID_CANCEL:
			return     

		pathname = fd.GetPath()
		try:
			f = open(pathname, 'r')
			f.close()
			self.currentAMD = pathname
			self.edit.LoadFile(pathname)
			self.onKeyUp(wx.KeyEvent(wx.wxEVT_NULL))
			self.wv.LoadURL(self.html)
		except IOError:
			wx.LogError("Cannot open the specified file '%s'." % pathname)

	
	def onReload(self, event):
		self.wv.Reload()
		self.edit.SetFocus()


	def onShowHidden(self, event):
		if self.edit.GetViewWhiteSpace() == 0:
			self.edit.StyleSetSpec(3, "fore:#00ff00,back:#282828,face:Courier New,size:10")	
			self.edit.SetViewWhiteSpace(True)
			self.edit.SetViewEOL(True)
		else:
			self.edit.StyleSetSpec(3, "fore:#d5c4a1,back:#282828,face:Courier New,size:10")
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
		self.edit.StyleSetSpec(STYLE.TEXT, "fore:#d5c4a1,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.HEADING, "fore:#EFCD1E,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.HIDDEN, "fore:#d5c4a1,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.CODE, "fore:#b8bb26,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.SYMBOL, "fore:#81ac71,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.TEST, "fore:#ff00ff,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.STRIKE, "fore:#e44533,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.BOLD, "fore:#d9a62e,bold,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.UNDERLINE, "fore:#d9a62e,underline,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.ITALIC, "fore:#7d9d90,italic,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.IMAGE, "fore:#cb8296,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.IMAGE_UNDERLINED, "fore:#cb8296,underline,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.LINK, "fore:#cb8296,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.LINK_UNDERLINED, "fore:#cb8296,underline,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.HTML, "fore:#cb8296,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.HTML_ATTRIBUTE, "fore:#d9a62e,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.FORMAT, "fore:#e44533,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.COMMENT, "fore:#928372,back:#282828,face:%(mono)s,size:%(size)d" % faces)

		self.edit.StyleSetSpec(STYLE.CODEBLOCK_KEYWORD, "fore:#569cd6,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.CODEBLOCK_SYMBOL, "fore:#9cdcfe,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.CODEBLOCK_TEXT, "fore:#F9FFE0,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.CODEBLOCK_STRING, "fore:#d69d73,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.CODEBLOCK_COMMENT, "fore:#57a64a,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.CODEBLOCK_FUNCTION, "fore:#4ec9b0,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.CODEBLOCK_CLASS, "fore:#4ec9b0,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.CODEBLOCK_TYPE, "fore:#EFCD1E,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.CODEBLOCK_FLOW, "fore:#d8a0df,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(STYLE.CODEBLOCK_DIGIT, "fore:#b5ce92,back:#282828,face:%(mono)s,size:%(size)d" % faces)
		self.edit.IndicatorSetStyle(0, stc.STC_INDIC_SQUIGGLE)
		self.edit.IndicatorSetForeground(0, wx.RED)


	def onClose(self, event):
		os.remove(self.html)
		sys.exit()


if __name__ == '__main__':
	start = time.time()
	app = WxAsyncApp()
	frm = Application(None)
	end = time.time()
	info(f"Application load time: {round(end - start, 2)}s")
	loop = get_event_loop()
	loop.run_until_complete(app.MainLoop())