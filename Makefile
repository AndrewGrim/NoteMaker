release: lexer.release
	python src/Application.py "Notes/test.amd"
debug: lexer
	python src/Application.py "Notes/test.amd"
lexer:
	cargo build && cp target/debug/lexer.dll src/lexer.pyd 
lexer.release:
	cargo build --release && cp target/release/lexer.dll src/lexer.pyd
test:
	cargo test
commit:
	cargo test && cargo clippy
exe:
	pyinstaller -w -F -i images/amd.ico src/Application.py && cp dist/Application.exe ../NoteMaker && mv Application.exe NoteMaker.exe
zip: exe
	python src/build.py
doc:
	cargo doc --open --no-deps --document-private-items