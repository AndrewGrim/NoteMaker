import time
import os

import wx
import wx.html2 as webview
import wx.stc as stc

class Application(wx.Frame):

	def __init__(self, *args, **kw):
		super(Application, self).__init__(*args, **kw)

		self.currentHTML = f"{os.getcwd()}/basic.html"
		self.currentMD = f"{os.getcwd()}/basic.md"

		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.edit = stc.StyledTextCtrl(panel)
		self.edit.SetLexer(stc.STC_LEX_MARKDOWN)
		self.edit.SetMarginType(1, stc.STC_MARGIN_NUMBER)
		self.edit.SetMarginWidth(1, 25)
		#self.edit.SetViewWhiteSpace(True)
		self.setColors()

		sizer.Add(self.edit, 4, wx.EXPAND)

		self.wv = webview.WebView.New(panel)
		sizer.Add(self.wv, 5, wx.EXPAND)

		panel.SetSizer(sizer)

		self.edit.LoadFile(self.currentMD)
		self.wv.LoadURL(self.currentHTML)

		self.makeMenuBar()
		self.SetSize((1280, 720))
		self.Center()
		self.SetTitle("NoteMaker")
		self.Show()


	def makeMenuBar(self):
		fileMenu = wx.Menu()
		saveItem = fileMenu.Append(-1, "&Save\tCtrl-S")
		
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.onSave, saveItem)


	def onSave(self, event):
		f = open(self.currentMD, "w")
		f.write(self.edit.GetValue())
		

	def setColors(self):
		faces = {
			'times': 'Times New Roman',
			'mono' : 'Courier New',
			'helv' : 'Arial',
			'other': 'Comic Sans MS',
			'size' : 10,
			'size2': 8,
		}

		self.edit.StyleSetSpec(stc.STC_STYLE_DEFAULT, "back:#282828,face:%(helv)s,size:%(size)d" % faces)
		#self.edit.StyleSetSpec(0, "fore:#FF00FF,back:#282828,face:%(helv)s,size:%(size)d" % faces)
		#self.edit.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)
		self.edit.StyleClearAll()  # Reset all to be like the default

		self.edit.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "fore:#928374,back:#212121,face:%(helv)s,size:%(size2)d" % faces)
		self.edit.StyleSetSpec(stc.STC_STYLE_INDENTGUIDE, "fore:#FF00FF,back:#FF0000,bold")
		self.edit.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
		self.edit.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
		self.edit.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#FFFFFF,back:#FF0000,bold")

		self.edit.StyleSetSpec(stc.STC_MARKDOWN_DEFAULT, "fore:#d5c4a1,face:%(helv)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_ULIST_ITEM, "fore:#81ac71,face:%(helv)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_OLIST_ITEM, "fore:#81ac71,bold,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_BLOCKQUOTE, "fore:#81ac71,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_HRULE, "fore:#81ac71,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_LINK, "fore:#cb8296,bold,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_CODEBK, "bold,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_CODE, "fore:#b8bb26,face:%(other)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_CODE2, "fore:#b8bb26,face:%(helv)s,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_STRONG1, "fore:#d9a62e,bold,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_STRONG2, "fore:#d9a62e,underline,size:%(size)d" % faces)
		self.edit.StyleSetSpec(stc.STC_MARKDOWN_EM1, "fore:#7d9d90,italic,face:%(helv)s,size:%(size)d" % faces)
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
    print(f"Application load time: {round(end - start, 2)}s")
    app.MainLoop()