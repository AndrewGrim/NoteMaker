#![allow(dead_code)]
#![allow(unused_variables)]
#![allow(unused_imports)]

use std::fs;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod debug;
use debug::ok;

#[derive(Debug)]
enum TokenType {
	Heading,
	CodeKeyword,
}

#[derive(Debug)]
struct Token {
	token_type: TokenType, 
	begin: usize,
	end: usize,
}

impl Token {
	fn new(token_type: TokenType, begin: usize) -> Token {
		return Token {
			token_type, 
			begin, 
			end: begin + 1
		}
	}

	fn new_tag(token_type: TokenType, begin: usize, tag: &str) -> Token {
		return Token {
			token_type, 
			begin, 
			end: begin + tag.len()
		}
	}
}

fn check_for_tag(tag: &str, text: &str, i: &usize) -> bool {
	assert!(tag.len() > 0, "Tag length must be greater than zero!");

	let mut matched: bool = true;

	for num in 0..tag.len() {
		let c = text.chars().nth(i + num).expect("error");
		let t = tag.chars().nth(num).expect("error");

		if c != t {
			matched = false;
			return matched;
		}
	}

	return matched;
}

#[pyfunction]
fn find_keywords(_py: Python, path: &str) -> PyResult<Vec<(usize, usize)>> {
	let text = fs::read_to_string(path)
		.expect("Something went wrong reading the file");

	//let mut tokens: Vec<Token> = Vec::new();
	let mut tokens: Vec<(usize, usize)> = Vec::new();
	let keywords = ["class", "def", "if", "else", "elif", "return", "yield", "self"];

	let mut i: usize = 0;
	let mut line: usize = 1;
	while i < text.len() {
		let c = text.chars().nth(i).expect("error");
	
		for key in keywords.iter() {
			if c == key.chars().nth(0).expect("error") {
				if check_for_tag(key, &text, &i) {
					ok(format!("Line: {} Index: {}->{} Tag: '{}'", line, i, i + key.len(), key).as_str());
					//tokens.push(Token::new_tag(TokenType::CodeKeyword, i, key));
					tokens.push((i, i + key.len()));
				}
			}
		}

		if c == '\n' {
			line += 1;
		}

		i += 1;
	}

	return Ok(tokens);
	//debug::test();
	//println!("{:#?}", tokens);
}

#[pymodule]
fn keywords(py: Python, m: &PyModule) -> PyResult<()> {
	m.add_wrapped(wrap_pyfunction!(find_keywords))?;

	return Ok(());
}