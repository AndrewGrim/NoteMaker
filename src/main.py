"""
A very simple and naive markdown parser.
Reads a file a char at a time and writes the equivalent html to another file.
Currently supported markdown:
	headings
	bold
	italic
	img
	link
	blockquote
	code
	unordered list(WIP)
"""

def fileSize(fname):
	import os
	statinfo = os.stat(fname)
	return statinfo.st_size


files = ["basic", "advanced_supported", "advanced"]
for f in files: 
	r = open(f"{f}.md", "r")
	w = open(f"{f}.html", "w")

	#w.write(r.read(1))
	#print(fileSize("testFile.md"))
	#r.tell() -> 105
	#r.seek(105)
	fSize = fileSize(f"{f}.md")
	i = 0
	lineEnd = ""
	ignore = False
	line = 0
	# TODO should probably go back to a line by line read and check only the first index at first, more if needed
	# cause at the moment if i put a hash anywhere in text it will check if its a heading
	# even if its a quote or a coment or whatever
	# TODO add default styling and allow for custom styles
	while r.tell() < fSize:
		char = r.read(1)
		if char == "\n":
			line += 1

		if ignore:
			if char == "`":
				ignore = False
				if r.read(1) == "\n":
					lineEnd += "<br><br>"
					r.seek(r.tell() - 1)
				else:
					r.seek(r.tell() - 1)
			else:
				w.write(char)
		elif char == "\n":
			if lineEnd != "":
				w.write(lineEnd)
				lineEnd = ""
			w.write("\n")
		elif char == "#":
			hCount = 1
			while True:
				c = r.read(1)
				if c == " ":
					break
				elif c == "\n":
					print(f"Line: {line}, TotalChar: {i} -> Improperly formatted heading!")
				hCount += 1
			if hCount > 6:
				print(f"Line: {line}, TotalChar: {i} -> Heading number is too high!")
			else:
				w.write(f'<h{hCount}>')
				if hCount == 1:
					lineEnd = f"</h{hCount}><hr>"
				else:
					lineEnd = f"</h{hCount}>"
		elif char in ["*", "-", "+"]: # or char == "-" # or char == "+"
			nextC = r.read(1)
			# TODO this needs to look at the next line since we want to allow numbered lists
			if nextC == " ":
				w.write("<ul>\n<li>")
				lineEnd = "</li>\n</ul>"
			elif nextC not in ["\n", " ", "*"]:
				r.seek(r.tell() - 1)
				c = ""
				italic = ""
				new = ""
				while True:
					c = r.read(1)
					if c == "*":
						if r.read(1) == "\n":
							new = "<br><br>"
							r.seek(r.tell() - 1)
							break
						else:
							r.seek(r.tell() - 1)
							break
					elif c == "\n":
						print(f"Line: {line}, TotalChar: {i} -> Closing italic asterisk not found!")
						break
					else:
						italic += c
				w.write(f"<i>{italic}</i>{new}")
			elif nextC == "*":
				c = ""
				bold = ""
				new = ""
				while True:
					c = r.read(1)
					if c == "*":
						if r.read(1) == "*":
							if r.read(1) == "\n":
								new = "<br><br>"
								r.seek(r.tell() - 1)
								break
							else:
								r.seek(r.tell() - 1)
								break
						else:
							print(f"Line: {line}, TotalChar: {i} -> Closing bold asterisk not found!")
					elif c == "\n":
						print(f"Line: {line}, TotalChar: {i} -> Closing bold asterisk not found!")
						break
					else:
						bold += c
				w.write(f"<b>{bold}</b>{new}")
			elif nextC == "\n":
				print(f"Line: {line}, TotalChar: {i} -> newline following asterisk")
		elif char == "!":
			nextC = r.read(1)
			new = ""
			if nextC == "[":
				c = ""
				alt = ""
				while True:
					c = r.read(1)
					if c == "]":
						break
					elif c == "\n":
						print(f"Line: {line}, TotalChar: {i} -> Couldn't find the closing square bracket!")
						break
					else:
						alt += c
				nextC = r.read(1)
				if nextC == "(":
					img = ""
					while True:
						c = r.read(1)
						if c == ")":
							if r.read(1) == "\n":
								new = "<br><br>"
								r.seek(r.tell() - 1)
								break
							else:
								r.seek(r.tell() - 1)
								break
						elif c == "\n":
							print(f"Line: {line}, TotalChar: {i} -> Couldn't find the closing parenthases!")
							break
						else:
							img += c
					w.write(f'<img src="{img}" alt="{alt}">{new}')
		elif char == "[":
			text = ""
			new = ""
			while True:
				c = r.read(1)
				if c == "]":
					break
				elif c == "\n":
					print(f"Line: {line}, TotalChar: {i} -> Couldn't find the closing square bracket!")
					break
				else:
					text += c
			nextC = r.read(1)
			if nextC == "(":
				link = ""
				while True:
					c = r.read(1)
					if c == ")":
						if r.read(1) == "\n":
							new = "<br><br>"
							r.seek(r.tell() - 1)
							break
						else:
							r.seek(r.tell() - 1)
							break
					elif c == "\n":
						print(f"Line: {line}, TotalChar: {i} -> Couldn't find the closing parenthases!")
						break
					else:
						link += c
				w.write(f'<a href="{link}">{text}</a>{new}')
		elif char == ">": # TODO this is currently bothersome when parsing inline html
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
				print(f"Line: {line}, TotalChar: {i} -> Improperly formatted blockquote!")
		elif char == "`":
			w.write("<code>")
			lineEnd = "</code>"
			ignore = True
		elif char == "<":
			# start state html tag
			w.write(char)
		else:
			w.write(char)
		i += 1