from enum import IntEnum

class STYLE(IntEnum):
	TEXT = 0
	HEADING = 1
	HIDDEN = 3
	CODE = 4
	SYMBOL = 5
	TEST = 6
	STRIKE = 7
	BOLD = 8
	UNDERLINE = 9
	ITALIC = 11
	IMAGE = 12
	LINK = 13
	HTML = 14
	HTML_ATTRIBUTE = 15

class INDICATOR(IntEnum):
	ERROR = 32