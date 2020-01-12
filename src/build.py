import utilities as util

util.ZipDir(
    "NoteMaker",
    ["src/lexer.pyd", "NoteMaker.exe"],
    ["Notes", "images", "css", "Syntax"]
)