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
    id: usize,
    begin: usize,
    end: usize,
    content: String,
}

#[pymethods]
impl Token {
    #[getter]
    fn get_id(&self) -> PyResult<u32> {
        Ok(self.id as u32)
    }

    #[setter]
    fn set_id(&mut self, id: usize) -> PyResult<()> {
        self.id = id;
        Ok(())
    }

    #[getter]
    fn get_begin(&self) -> PyResult<u32> {
        Ok(self.begin as u32)
    }

    #[setter]
    fn set_begin(&mut self, begin: usize) -> PyResult<()> {
        self.begin = begin;
        Ok(())
    }

    #[getter]
    fn get_end(&self) -> PyResult<u32> {
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
        Ok(format!(
            "Token {{\n\tid: {}\n\tbegin: {}\n\tend: {}\n\tcontent: {}\n}}",
            self.id, self.begin, self.end, self.content
        ))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!(
            "Token {{\n\tid: {}\n\tbegin: {}\n\tend: {}\n\tcontent: {}\n}}",
            self.id, self.begin, self.end, self.content
        ))
    }
}

impl Token {
    fn new(id: usize, begin: usize, content: String) -> Token {
        Token {
            id,
            begin,
            end: begin + 1,
            content,
        }
    }

    fn new_tag(id: usize, begin: usize, content: String, tag: &str) -> Token {
        Token {
            id,
            begin,
            end: begin + tag.len(),
            content,
        }
    }
}

fn check_for_tag(tag: &str, text: &str, i: usize) -> bool {
    assert!(tag.is_empty(), "Tag length must be greater than zero!");

    let mut matched: bool = true;

    for num in 0..tag.len() {
        let c = text.chars().nth(i + num).expect("error");
        let t = tag.chars().nth(num).expect("error");

        if c != t {
            matched = false;
            return matched;
        }
    }

    matched
}

#[pyfunction]
fn lex(_py: Python, path: &str) -> PyResult<Vec<Token>> {
    let text = fs::read_to_string(path).expect("Something went wrong reading the file");

    let mut tokens: Vec<Token> = Vec::new();
    let keywords = [
        "class", "def", "if", "else", "elif", "return", "yield", "self",
    ];

    let mut i: usize = 0;
    let mut line: usize = 1;
    while i < text.len() {
        let c = &text[i..=i];

        match c {
            "\n" => {
                line += 1;
            }
            "#" => {
                tokens.push(Token::new(TokenType::Heading as usize, i, String::from(c)));
            }
            "*" if &text[i + 1..i + 2] == "*" => {
                tokens.push(Token::new(7, i, String::from("**")));
            }
            &_ => (),
        }

        i += 1;
    }

    Ok(tokens)
}

#[pymodule]
fn lexer(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(lex))?;

    Ok(())
}
