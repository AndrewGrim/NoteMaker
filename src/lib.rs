#![allow(dead_code)]
#![allow(unused_variables)]
#![allow(unused_imports)]
#![allow(unused_assignments)]

use std::fs;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::PyObjectProtocol;

mod debug;

mod token;
use token::Token;
use token::TokenType as tt;

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

fn match_heading(text: &str, mut i: usize, line: usize) -> (usize, usize, Token) {
    let mut heading: String = String::new();
    let mut h_count: usize = 0;

    loop {
        let next_c = &text[i..=i];

        match next_c {
            "#" => {
                h_count += 1;
                heading += next_c;
            }
            _ => break,
        }
        i += 1;
    }

    if h_count > 6 {
        debug::warn(
            format!(
                "Line: {}, Index: {} -> Too many #! Heading only go up to 6!",
                line, i
            )
            .as_str(),
        );

        return (
            i,
            line,
            Token::new(tt::Error as usize, i - (h_count - 1) - 1, i, heading),
        );
    }

    (
        i,
        line,
        Token::new(tt::Heading as usize, i - (h_count - 1) - 1, i, heading),
    )
}

#[pyfunction]
fn lex(_py: Python, text: String) -> PyResult<Vec<Token>> {
    let mut tokens: Vec<Token> = Vec::new();

    let mut i: usize = 0;
    let mut line: usize = 1;
    while i < text.len() {
        let c = &text[i..=i];

        match c {
            "\n" => {
                line += 1;
            }
            "#" => {
                let result = match_heading(&text, i, line);
                i = result.0;
                line = result.1;
                tokens.push(result.2);
                tokens.push(Token::new_space(i));
            }
            // "*" if &text[i + 1..i + 2] == "*" => {
            //     tokens.push(Token::new(TokenType::Bold as usize, i, String::from("**")));
            //     i += 1
            // }
            // "*" if &text[i + 1..i + 2] != "*" => {
            //     tokens.push(Token::new(TokenType::Italic as usize, i, String::from("*")));
            // }
            _ => (),
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
