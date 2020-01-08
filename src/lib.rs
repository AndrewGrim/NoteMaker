#![allow(dead_code)]
#![allow(unused_variables)]
#![allow(unused_imports)]
#![allow(unused_assignments)]

use std::fs;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::PyObjectProtocol;
use regex::Regex;

mod debug;

mod token;
use token::Token;

mod token_type;
use token_type::TokenType;

mod lexer;
use lexer::*;

mod position;
use position::Position;

#[pyfunction]
fn lex(_py: Python, text: String) -> PyResult<Vec<Token>> {
    let mut tokens: Vec<Token> = Vec::with_capacity(text.len());

    let mut pos: Position = Position::new(0, 0);
    while pos.index < text.len() {
        let c = match text.get(pos.index..=pos.index) { Some(val) => val, None => break,};

        match c {
            "\n" => {
                tokens.push(Token::new_single(TokenType::Newline as usize, pos.index, String::from(c)));
                pos.newline();
            }
            "\t" => tokens.push(Token::new_single(TokenType::Tab as usize, pos.index, String::from(c))),
            " " => tokens.push(Token::new_single(TokenType::Tab as usize, pos.index, String::from(c))),
            "#" => {
                pos.update(match_heading(&text, pos.index, pos.line, &mut tokens));
            }
            "*" => { // TODO rework to just parse the opening or closing tag not text within
                pos.increment();
                let next_c = match text.get(pos.index..=pos.index) { Some(val) => val, None => break,};
                match next_c {
                    "*" => {
                        pos.update(match_bold(&text, pos.index, pos.line, &mut tokens));
                    }
                    _ => {
                        pos.update(match_italic(&text, pos.index, pos.line, &mut tokens));
                    }
                }
            }
            "~" => { // TODO rework to just parse the opening or closing tag not text within
                pos.increment();
                let next_c = match text.get(pos.index..=pos.index) { Some(val) => val, None => break,};
                if let "~" = next_c {
                    pos.update(match_strike(&text, pos.index, pos.line, &mut tokens));
                }
            }
            "_" => { // TODO rework to just parse the opening or closing tag not text within
                pos.increment();
                let next_c = match text.get(pos.index..=pos.index) { Some(val) => val, None => break,};
                if let "_" = next_c {
                    pos.update(match_underline(&text, pos.index, pos.line, &mut tokens));
                }
            }
            ":" => { // TODO allow for formatting within list text
                pos.increment();
                let next_c = match text.get(pos.index..=pos.index) { Some(val) => val, None => break,};
                if let ":" = next_c {
                    pos.update(match_list(&text, pos.index, pos.line, &mut tokens));
                } else {
                    tokens.push(Token::new_single(TokenType::Text as usize, pos.index, String::from(c)));
                }
            }
            ">" => {
                let next_c = match text.get(pos.index + 1..=pos.index + 1) { Some(val) => val, None => break,};
                if let " " = next_c {
                    pos.update(match_blockquote(&text, pos.index, pos.line, &mut tokens));
                }
            }
            "-" => {
                let next_c = match text.get(pos.index + 1..=pos.index + 1) { Some(val) => val, None => break,}; // TODO this and other occurances might be better with a return or a continue??
                if next_c == "-" && match text.get(pos.index + 2..=pos.index + 2) { Some(val) => val, None => break,} == "-" {
                    tokens.push(Token::new(TokenType::HorizontalRule as usize, pos.index, pos.index + 3, String::from("---")));
                    pos.index += 3; // to step over the newline following the hr
                    pos.newline();
                } else if next_c == " " {
                    if match text.get(pos.index + 2..=pos.index + 5) { Some(val) => val, None => break,} == "[ ] " {
                        tokens.push(Token::new(TokenType::UnChecked as usize, pos.index, pos.index + 6, String::from("- [ ] ")));
                        pos.index += 5;
                    } else if next_c == " " && match text.get(pos.index + 2..=pos.index + 5) { Some(val) => val, None => break,} == "[x] " {
                        tokens.push(Token::new(TokenType::Checked as usize, pos.index, pos.index + 6, String::from("- [x] ")));
                        pos.index += 5;
                    } 
                    tokens.push(Token::space(pos.index));
                }
            }
            "`" => {
                pos.update(match_backticks(&text, pos.index, pos.line, &mut tokens));
            }
            "!" => {
                pos.update(match_image(&text, pos.index, pos.line, &mut tokens));
            }
            "?" => {
                pos.update(match_link(&text, pos.index, pos.line, &mut tokens));
            }
            "<" => {
                pos.update(match_html(&text, pos.index, pos.line, &mut tokens));
            }
            "/" => {
                pos.update(match_comment(&text, pos.index, pos.line, &mut tokens));
            }
            _ => tokens.push(Token::new_single(TokenType::Text as usize, pos.index, String::from(c))),
        }

        pos.increment();
    }

    Ok(tokens)
}

#[pyfunction]
fn regex_lex(_py: Python, text: String) -> PyResult<Vec<Token>> {
    let keywords = [
		String::from("as"), String::from("assert"), String::from("async"), String::from("await"), String::from("class"), String::from("continue"), String::from("def"), String::from("del"),  
		String::from("from"), String::from("global"),  String::from("import"),  String::from("lambda"), String::from("nonlocal"), String::from("self"),
    ];

    let flow = [
		String::from("or"), String::from("pass"), String::from("raise"), String::from("return"), String::from("try"), String::from("while"), String::from("with"), String::from("yield"), String::from("if"), 
		String::from("in"), String::from("is"), String::from("elif"), String::from("else"), String::from("except"), String::from("finally"), String::from("for"), String::from("and"), String::from("break"), 
		String::from("not"), 
    ];
    
	let types = [
		String::from("None"), String::from("str"), String::from("int"), String::from("bool"), String::from("float"), String::from("False"), String::from("True"),
    ];
    
    let declaration = [String::from("class"), String::from("def")];

    let mut tokens: Vec<Token> = Vec::new();

    for mat in Regex::new(r"#+").unwrap().find_iter(&text) {
        tokens.push(Token::new(1, mat.start(), mat.end(), String::from(mat.as_str())));
    }

    for o_mat in Regex::new(r"<<[^>]+>").unwrap().find_iter(&text) {
        tokens.push(Token::new(14, o_mat.start(), o_mat.end(), String::from(o_mat.as_str())));
        for mat in Regex::new(r#""[^"]+""#).unwrap().find_iter(o_mat.as_str()) {
            tokens.push(Token::new(15, mat.start() + o_mat.start(), mat.end() + o_mat.start(), String::from(mat.as_str())));
        }
    }

    for mat in Regex::new(r"<</[^>]+>").unwrap().find_iter(&text) {
        tokens.push(Token::new(14, mat.start(), mat.end(), String::from(mat.as_str())));
    }
    
    for mat in Regex::new(r"[!?]\[[\w\s]+\]").unwrap().find_iter(&text) {
        tokens.push(Token::new(12, mat.start(), mat.end(), String::from(mat.as_str())));
    }
    
    for mat in Regex::new(r"\]\([\w\s.-_']+\)").unwrap().find_iter(&text) {
        tokens.push(Token::new(12, mat.start(), mat.end(), String::from(mat.as_str())));
    }

    for mat in Regex::new(r"[<>\\/*:;!?\[\]>\(\)\-~_,.=]").unwrap().find_iter(&text) {
        tokens.push(Token::new(5, mat.start(), mat.end(), String::from(mat.as_str())));
    }

    for mat in Regex::new(r"__[^_]+__").unwrap().find_iter(&text) {
        tokens.push(Token::new(9, mat.start() + 2, mat.end() - 2, String::from(mat.as_str())));
    }

    for mat in Regex::new(r"~~[^~]+~~").unwrap().find_iter(&text) {
        tokens.push(Token::new(7, mat.start() + 2, mat.end() - 2, String::from(mat.as_str())));
    }

    for mat in Regex::new(r"\*\*[^*]+\*\*").unwrap().find_iter(&text) {
        tokens.push(Token::new(8, mat.start() + 2, mat.end() - 2, String::from(mat.as_str())));
    }

    for mat in Regex::new(r"`[^`]+`").unwrap().find_iter(&text) {
        tokens.push(Token::new(4, mat.start(), mat.end(), String::from(mat.as_str())));
    }

    for mat in Regex::new(r"p`").unwrap().find_iter(&text) {
        tokens.push(Token::new_single(16, mat.start(), String::from("p")));
    }

    for mat in Regex::new(r"\- \[.\]").unwrap().find_iter(&text) {
        tokens.push(Token::new_single(13, mat.end() - 2, String::from(mat.as_str())));
    }

    for mat in Regex::new(r"\s//[^\n]+\s").unwrap().find_iter(&text) {
        tokens.push(Token::new(27, mat.start(), mat.end(), String::from(mat.as_str())));
    }

    for o_mat in Regex::new(r"f`[^`]+`").unwrap().find_iter(&text) {
        for mat in Regex::new(r".").unwrap().find_iter(o_mat.as_str()) {
            tokens.push(Token::new_single(19, mat.start() + o_mat.start(), String::from(mat.as_str())));
        }

        tokens.push(Token::new_single(16, o_mat.start(), String::from("f")));
        tokens.push(Token::new_single(4, o_mat.start() + 1, String::from("`")));
        tokens.push(Token::new_single(4, o_mat.end() - 1, String::from("`")));

        for key in keywords.iter() {
            for mat in Regex::new((r"\b".to_string() + key + r"\b").as_str()).unwrap().find_iter(o_mat.as_str()) {
                tokens.push(Token::new(17, mat.start() + o_mat.start(), mat.end() + o_mat.start(), String::from(mat.as_str())));
            }
        }

        for f in flow.iter() {
            for mat in Regex::new((r"\b".to_string() + f + r"\b").as_str()).unwrap().find_iter(o_mat.as_str()) {
                tokens.push(Token::new(25, mat.start() + o_mat.start(), mat.end() + o_mat.start(), String::from(mat.as_str())));
            }
        }

        for t in types.iter() {
            for mat in Regex::new((r"\b".to_string() + t + r"\b").as_str()).unwrap().find_iter(o_mat.as_str()) {
                tokens.push(Token::new(24, mat.start() + o_mat.start(), mat.end() + o_mat.start(), String::from(mat.as_str())));
            }
        }

        for mat in Regex::new(r"\d").unwrap().find_iter(o_mat.as_str()) {
            tokens.push(Token::new(26, mat.start() + o_mat.start(), mat.end() + o_mat.start(), String::from(mat.as_str())));
        }

        for mat in Regex::new(r"[<>\\/*:;!?\[\]>\(\)\-~_,.=]").unwrap().find_iter(o_mat.as_str()) {
            tokens.push(Token::new(18, mat.start() + o_mat.start(), mat.end() + o_mat.start(), String::from(mat.as_str())));
        }

        for d in declaration.iter() {
            for mat in Regex::new((r"\b".to_string() + d + r"\b[^({:<]+[\({:<]").as_str()).unwrap().find_iter(o_mat.as_str()) {
                tokens.push(Token::new(22, mat.start() + o_mat.start() + d.len(), mat.end() + o_mat.start() - 1, String::from(mat.as_str())));
            }
        }

        for mat in Regex::new(r#"['"][^"']+["']"#).unwrap().find_iter(o_mat.as_str()) {
            tokens.push(Token::new(20, mat.start() + o_mat.start(), mat.end() + o_mat.start(), String::from(mat.as_str())));
        }
    }

    Ok(tokens)
}

#[pymodule]
fn lexer(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(lex))?;
    m.add_wrapped(wrap_pyfunction!(regex_lex))?;

    Ok(())
}
