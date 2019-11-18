from enum import IntEnum
import typing

class MD(IntEnum):
	HEADING = 0
	BOLD = 7
	ITALIC = 8
	UNDERLINE = 9
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

	NEWLINE = 20
	TAB = 21
	SPACE = 22
	TEXT = 23
	ERROR = 24

	CODE_BEGIN = 25
	CODE_END = 26

	BOLD_BEGIN = 27
	BOLD_END = 28

	UNDERLINE_BEGIN = 29
	UNDERLINE_END = 30

	ITALIC_BEGIN = 31
	ITALIC_END = 32

	HORIZONTAL_RULE = 33

	ULIST_BEGIN = 34
	ULIST_END = 35
	LIST_ITEM_BEGIN = 36
	LIST_ITEM_END = 37
	LIST_ITEM_TEXT = 38
	OLIST_BEGIN = 39
	OLIST_END = 40

	CHECK_TEXT = 41
	CHECK_END = 42

	IMAGE_ALT_BEGIN = 43
	IMAGE_ALT_END = 44
	IMAGE_ALT_TEXT = 45

	IMAGE_PATH_BEGIN = 46
	IMAGE_PATH_END = 47
	IMAGE_PATH_TEXT = 48

	LINK_ALT_BEGIN = 49
	LINK_ALT_END = 50
	LINK_ALT_TEXT = 51

	LINK_PATH_BEGIN = 52
	LINK_PATH_END = 53
	LINK_PATH_TEXT = 54