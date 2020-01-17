import utilities as util

util.ZipDir(
    "NoteMaker",
    ["src/lexer.pyd", "NoteMaker.exe", "README.md", "LICENSE"],
    ["Notes", "images", "css", "Syntax"]
)