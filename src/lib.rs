#![allow(dead_code)]
#![allow(unused_variables)]
#![allow(unused_imports)]

use std::fs;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::PyObjectProtocol;

mod debug;
use debug::ok;

#[derive(Debug)]
enum TokenType {
	Heading,
	CodeKeyword,
}

#[pyclass]
#[derive(Debug)]
struct Token {
	token_type: usize, 
	begin: usize,
	end: usize,
	content: String,
}

#[pymethods]
impl Token {
	#[getter]
	fn get_token_type(&self) -> PyResult<u32>  {
		Ok(self.token_type as u32) 
	}

	#[setter]
	fn set_token_type(&mut self, token_type: usize) -> PyResult<()> {
		self.token_type = token_type;
		Ok(())
	}

	#[getter]
	fn get_begin(&self) -> PyResult<u32>  {
		Ok(self.begin as u32) 
	}

	#[setter]
	fn set_begin(&mut self, begin: usize) -> PyResult<()> {
		self.begin = begin;
		Ok(())
	}

	#[getter]
	fn get_end(&self) -> PyResult<u32>  {
		Ok(self.end as u32) 
	}

	#[setter]
	fn set_end(&mut self, end: usize) -> PyResult<()> {
		self.end = end;
		Ok(())
	}

	#[getter]
	fn get_content(&self) -> PyResult<&str> {
		Ok(&self.content.as_str())
	}

	#[setter]
	fn set_content(&mut self, content: String) -> PyResult<()> {
		self.content = content;
		Ok(())
	}
}

#[pyproto]
impl PyObjectProtocol for Token {
	fn __str__(&self) -> PyResult<String> {
		Ok(format!("Token {{\n\ttoken_type: {}\n\tbegin: {}\n\tend: {}\n\tcontent: {}\n}}", self.token_type, self.begin, self.end, self.content).to_string())
	}

	fn __repr__(&self) -> PyResult<String> {
		Ok(format!("Token {{\n\ttoken_type: {}\n\tbegin: {}\n\tend: {}\n\tcontent: {}\n}}", self.token_type, self.begin, self.end, self.content).to_string())
	}
}

impl Token {
	fn new(token_type: usize, begin: usize, content: String) -> Token {
		return Token {
			token_type, 
			begin, 
			end: begin + 1,
			content,
		}
	}

	fn new_tag(token_type: usize, begin: usize, content: String, tag: &str) -> Token {
		return Token {
			token_type, 
			begin, 
			end: begin + tag.len(),
			content,
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
fn find_keywords(_py: Python, path: &str) -> PyResult<Vec<Token>> {
	let text = fs::read_to_string(path)
		.expect("Something went wrong reading the file");

	let mut tokens: Vec<Token> = Vec::new();
	//let mut tokens: Vec<(usize, usize)> = Vec::new();
	let keywords = ["class", "def", "if", "else", "elif", "return", "yield", "self"];

	let mut i: usize = 0;
	let mut line: usize = 1;
	while i < text.len() {
		let c = text.chars().nth(i).expect("error");
	
		for key in keywords.iter() {
			if c == key.chars().nth(0).expect("error") {
				if check_for_tag(key, &text, &i) {
					ok(format!("Line: {} Index: {}->{} Tag: '{}'", line, i, i + key.len(), key).as_str());
					tokens.push(Token::new_tag(1, i, key.to_string(), key));
					//tokens.push((i, i + key.len()));
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