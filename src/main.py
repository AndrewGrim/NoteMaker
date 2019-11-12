"""
A very simple and naive markdown parser.
Reads a file a char at a time and writes the equivalent html to another file.
Currently supported markdown:
	all headings 1-6
	bold
	italic
	img
	blockquote
	unordered list(WIP)
"""

r = open("testFile.md", "r")
w = open("GENERATED_HTML.HTML", "w")

def fileSize(fname):
	import os
	statinfo = os.stat(fname)
	return statinfo.st_size

#w.write(r.read(1))
#print(fileSize("testFile.md"))
#r.tell() -> 105
#r.seek(105)
fSize = fileSize("testFile.md")
i = 0
lineEnd = ""
ignore = False
# TODO should probably go back to a line by line read and check only the first index at first, more if needed
# cause at the moment if i put a hash anywhere in text it will check if its a heading
# even if its a quote or a coment or whatever
# TODO add default styling and allow for custom styles
while r.tell() < fSize:
	char = r.read(1)

	if ignore:
		if char == "`":
			ignore = False
		else:
			w.write(char)
	elif char == "\n":
		if lineEnd != "":
			w.write(lineEnd)
			w.write("\n")
			lineEnd = ""
		else:
			w.write("\n")
	elif char == "#":
		hCount = 1
		while True:
			c = r.read(1)
			if c == " ":
				break
			elif c == "\n":
				print("Improperly formatted heading!")
			hCount += 1
		if hCount > 6:
			print("Heading number is too high!")
		else:
			w.write(f'<h{hCount}>')
			if hCount == 1:
				lineEnd = f"</h{hCount}><hr>"
			else:
				lineEnd = f"</h{hCount}>"
	elif char == "*" or char == "-":
		nextC = r.read(1)
		# TODO this needs to look at the next line since we want to allow numbered lists
		if nextC == " ":
			w.write("<ul>\n<li>")
			lineEnd = "</li>\n</ul>"
		elif nextC not in ["\n", " ", "*"]:
			r.seek(r.tell() - 1)
			c = ""
			italic = ""
			while True:
				c = r.read(1)
				if c == "*":
					break
				elif c == "\n":
					print("Closing italic asterisk not found!")
					break
				else:
					italic += c
			w.write(f"<i>{italic}</i>")
		elif nextC == "*":
			c = ""
			bold = ""
			while True:
				c = r.read(1)
				if c == "*":
					if r.read(1) == "*":
						break
					else:
						print("Closing bold asterisk not found!")
				elif c == "\n":
					print("Closing bold asterisk not found!")
					break
				else:
					bold += c
			w.write(f"<b>{bold}</b>")
		elif nextC == "\n":
			print("newline following asterisk")
	elif char == "!":
		nextC = r.read(1)
		if nextC == "[":
			c = ""
			alt = ""
			while True:
				c = r.read(1)
				if c == "]":
					break
				elif c == "\n":
					print("Couldn't find the closing square bracket!")
					break
				else:
					alt += c
			nextC = r.read(1)
			if nextC == "(":
				img = ""
				while True:
					c = r.read(1)
					if c == ")":
						break
					elif c == "\n":
						print("Couldn't find the closing parenthases!")
						break
					else:
						img += c
				w.write(f'<img src="{img}" alt="{alt}">')
	elif char == "[":
		text = ""
		while True:
			c = r.read(1)
			if c == "]":
				break
			elif c == "\n":
				print("Couldn't find the closing square bracket!")
				break
			else:
				text += c
		nextC = r.read(1)
		if nextC == "(":
			link = ""
			while True:
				c = r.read(1)
				if c == ")" or c == "\n":
					break
				else:
					link += c
			w.write(f'<a href="{link}">{text}</a>')
	elif char == ">":
		nextC = r.read(1)
		if nextC == " ":
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
			print("Improperly formatted blockquote!")
	elif char == "`":
		w.write("<code>")
		lineEnd = "</code>"
		ignore = True
	elif char == "<":
		# inline html, i could just leave this for else since the end result is the same
		w.write(char)
	else:
		w.write(char)
	i += 1
print(i)