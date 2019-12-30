debug: lexer
	python src/Application.py "Notes/test.amd"
parser:
	python src/ParseMarkdown.py Notes/test.md
exe:
	pyinstaller -w -F -i images/amd.ico src/Application.py && cp dist/Application.exe ../NoteMaker && mv Application.exe NoteMaker.exe
lexer:
	cargo fmt && cargo build --release && cp target/release/keywords.dll src/keywords.pyd