del /f "ParseMarkdown.exe" & 
pyinstaller -F src/ParseMarkdown.py &
move dist\ParseMarkdown.exe "..\NoteMaker"