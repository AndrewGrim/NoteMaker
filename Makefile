debug:
	python src/Application.py "Notes/Terminal Colors.amd"
parser:
	python src/ParseMarkdown.py Notes/test.md
exe:
	pyinstaller -w -F -i images/amd.ico src/Application.py && cp dist/Application.exe ../NoteMaker && mv Application.exe NoteMaker.exe
lexer:
	cargo +nightly build --release && cp target/release/keywords.dll src/keywords.pyd