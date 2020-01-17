import time
import os
import sys
import platform
import typing

import wx
import wx.html2 as webview
import wx.stc as stc

from Styles import *
import utilities as util

import lexer


class Application(wx.Frame):

	def __init__(self, *args, **kw):
		"""
		Initializes the application:\n
			* On windows machines it enables colored output first.
			* Sets up the UI.
			* Sets the various preferences.
			* Does the inital lexing and parsing.
		"""

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
				util.fail(f"Unable to load the file: {self.currentAMD}")
		
		if self.currentAMD != None:
			try:
				self.wv.LoadURL(f"file://{self.html}") 
			except:
				util.fail(f"Unable to load the html file: {self.html}")

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
		tokens = lexer.lex(self.edit.GetValue())
		self.generateHtml(tokens, self.html, self.exeDir)

		self.Bind(wx.EVT_SIZE, self.onSize)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Show()	


	def generateHtml(self, tokens, html, css):
		"""
		Generates the html from the given lexer tokens.
		"""

		f = open(html, "w")
		f.write("""<!DOCTYPE html>
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
		for t in tokens:
			f.write(t.html)
		f.write("</div>")
		f.write("</body>")
		f.write("</html>")
		f.close()


	def onSize(self, event):
		"""
		Runs when the window is resized:\n
			* Resizes the status bar to fit the new size of the window.
		"""

		w = self.GetSize()[0]
		w = w - 7 * 100
		self.status.SetStatusWidths([100, 100, 100, 100, w, 100, 100])
		event.Skip()

	
	def onUpdateUI(self, event):
		"""
		Runs when UpdateUI event is triggerd:\n
			* Refreshes the status bar values.
		"""

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
		"""
		Runs when any key is pressed:\n
			* Redoes the entire syntax highlight using regex from the dynamic module written in Rust.
		"""

		text = self.edit.GetValue()
		tokens = lexer.regex_lex(text)
		for t in tokens:
			self.edit.StartStyling(t.begin, 0xff)
			self.edit.SetStyling(t.end - t.begin, t.id)
		event.Skip()


	def makeMenuBar(self):
		"""
		Sets up the menu bar.
		"""

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
		"""
		Closes the application by using the menu or by using the hotkey "Ctrl-Q". Runs onClose() to remove the temporary html file.
		"""

		self.onClose(None)


	def onNew(self, event):
		"""
		Creates a new document.
		"""

		self.currentAMD = None
		self.edit.ClearAll()
		open(self.html, "w").write("")
		self.wv.LoadURL(f"file://{self.html}") 


	def onSave(self, event):
		"""
		Runs when the current document is saved:\n
			* If the current file is known it just saves the file, and lexes and parses it.
			* If its not then it shows a filedialog to save file and get its path.
		In either scenario the files is saved as UTF-8 with LF line endings.
		"""

		if self.currentAMD != None:
			f = open(self.currentAMD, "wb")
			f.write(self.edit.GetValue().encode("UTF-8").replace(b"\r\n", b"\n")) # TODO line endings, encoding settings
			f.close() 
			tokens = lexer.lex(self.edit.GetValue())
			self.generateHtml(tokens, self.html, self.exeDir)
			self.onReload(None)
			self.edit.SetFocus()
		else:
			fileDialog = wx.FileDialog(self, "Save As...", wildcard="AlmostMarkdown (*.amd)|*.amd", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return     

			self.currentAMD = fileDialog.GetPath()
			try:
				f = open(self.currentAMD, "wb")
				f.write(self.edit.GetValue().encode("UTF-8").replace(b"\r\n", b"\n")) # TODO line endings, encoding settings
				f.close()
				tokens = lexer.lex(self.edit.GetValue())
				self.generateHtml(tokens, self.html, self.exeDir)
				self.wv.LoadURL(f"file://{self.html}") 
			except IOError:
				util.fail(f"Cannot save current data in file '{self.currentAMD}'.")


	def onOpen(self, event):
		"""
		Runs when you try to open a file:\n
			* Lexes and parses the document and loads it into webview.
		"""

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
			tokens = lexer.lex(self.edit.GetValue())
			self.generateHtml(tokens, self.html, self.exeDir)
			self.wv.LoadURL(f"file://{self.html}") 
		except IOError:
			wx.LogError("Cannot open the specified file '%s'." % pathname)

	
	def onReload(self, event):
		"""
		Reloads the webview keeping the current position.
		"""

		self.wv.Reload()


	def onShowHidden(self, event):
		"""
		Shows normally hidden symbols like line endings and whitespace characters.
		"""

		if self.edit.GetViewWhiteSpace() == 0:
			self.edit.StyleSetSpec(3, "fore:#00ff00,back:#282828,face:Courier New,size:10")	
			self.edit.SetViewWhiteSpace(True)
			self.edit.SetViewEOL(True)
		else:
			self.edit.StyleSetSpec(3, "fore:#d5c4a1,back:#282828,face:Courier New,size:10")
			self.edit.SetViewWhiteSpace(False)
			self.edit.SetViewEOL(False)


	def setupStyling(self):
		"""
		Sets up the styling colors and style of the stc editor.
		"""

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
		"""
		Runs when the application is being closed:\n
			* Removes the temporary html file and closes the application.
		"""

		os.remove(self.html)
		sys.exit()


if __name__ == '__main__':
	start = time.time()
	app = wx.App()
	frm = Application(None)
	end = time.time()
	util.info(f"Application load time: {round(end - start, 2)}s")
	app.MainLoop()