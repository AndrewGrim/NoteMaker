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

mod token_type;
use token_type::TokenType;

mod lexer;
use lexer::*;

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
fn lex(_py: Python, text: String) -> PyResult<Vec<Token>> {
    let mut tokens: Vec<Token> = Vec::with_capacity(text.len());

    let mut i: usize = 0;
    let mut line: usize = 1;
    while i < text.len() {
        let c = match text.get(i..=i) { Some(val) => val, None => break,};

        match c {
            "\n" => {
                tokens.push(Token::new_single(TokenType::Newline as usize, i, String::from(c)));
                line += 1;
            }
            "\t" => tokens.push(Token::new_single(TokenType::Tab as usize, i, String::from(c))),
            " " => tokens.push(Token::new_single(TokenType::Tab as usize, i, String::from(c))),
            "#" => {
                let result = match_heading(&text, i, line, &mut tokens);
                i = result.0;
                line = result.1;
            }
            "*" => {
                i += 1;
                let next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                match next_c {
                    "*" => {
                        let result = match_bold(&text, i, line, &mut tokens);
                        i = result.0;
                        line = result.1;
                    }
                    _ => {
                        let result = match_italic(&text, i, line, &mut tokens);
                        i = result.0;
                        line = result.1;
                    }
                }
            }
            "~" => {
                i += 1;
                let next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                if let "~" = next_c {
                    let result = match_strike(&text, i, line, &mut tokens);
                    i = result.0;
                    line = result.1;
                }
            }
            "_" => {
                i += 1;
                let next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                if let "_" = next_c {
                    let result = match_underline(&text, i, line, &mut tokens);
                    i = result.0;
                    line = result.1;
                }
            }
            ":" => {
                i += 1;
                let next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                if let ":" = next_c {
                    let result = match_list(&text, i, line, &mut tokens);
                    i = result.0;
                    line = result.1;
                } else {
                    tokens.push(Token::new_single(TokenType::Text as usize, i, String::from(c)));
                }
            }
            ">" => {
                let next_c = match text.get(i + 1..=i + 1) { Some(val) => val, None => break,};
                if let " " = next_c {
                    tokens.push(Token::new_single(TokenType::BlockquoteBegin as usize, i, String::from(">")));
                    tokens.push(Token::space(i + 1));
                    i += 2;

                    let start = i;
                    let mut blockquote_text: String = String::new();
                    while let Some(next_c) = text.get(i..=i) {
                        match next_c {
                            "\n" => {
                                tokens.push(Token::new(TokenType::BlockquoteText as usize, start, i, blockquote_text));
                                tokens.push(Token::new_single(TokenType::BlockquoteEnd as usize, i, String::from("\n")));
                                line += 1;
                                break;
                            }
                            _ => blockquote_text += next_c,
                        }
                        i += 1;
                    }
                }
            }
            "-" => {
                let next_c = match text.get(i + 1..=i + 1) { Some(val) => val, None => break,}; // TODO this and other occurances might be better with a return or a continue??
                if next_c == "-" && match text.get(i + 2..=i + 2) { Some(val) => val, None => break,} == "-" {
                    tokens.push(Token::new(TokenType::HorizontalRule as usize, i, i + 3, String::from("---")));
                    i += 3; // to step over the newline following the hr
                    line += 1;
                } else if next_c == " " {
                    if match text.get(i + 2..=i + 5) { Some(val) => val, None => break,} == "[ ] " {
                        tokens.push(Token::new(TokenType::UnChecked as usize, i, i + 6, String::from("- [ ] ")));
                        i += 5;
                    } else if next_c == " " && match text.get(i + 2..=i + 5) { Some(val) => val, None => break,} == "[x] " {
                        tokens.push(Token::new(TokenType::Checked as usize, i, i + 6, String::from("- [x] ")));
                        i += 5;
                    } 
                    tokens.push(Token::space(i));
                }
            }
            "`" => {
                if text.get(i - 1..i).expect("panic at format block") == "f" {
                    tokens.push(Token::new_single(TokenType::Format as usize, i - 1, String::from("f")));
                    // TODO format block
                } else {
                    tokens.push(Token::new_single(TokenType::CodeBegin as usize, i, String::from("`")));
                    let start = i;
                    let mut code_text: String = String::new();
                    i += 1;
                    while let Some(next_c) = text.get(i..=i) {
                        match next_c {
                            "`" => {
                                tokens.push(Token::new(TokenType::Code as usize, start, i, code_text));
                                tokens.push(Token::new_single(TokenType::CodeEnd as usize, i, String::from("`")));
                                break;
                            }
                            "\n" => line += 1,
                            _ => code_text += next_c,
                        }
                        i += 1;
                    }
                }
            }
            "!" => {
                let mut next_c = match text.get(i + 1..=i + 1) { Some(val) => val, None => break,};
                if next_c == "[" {
                    tokens.push(Token::new_double(TokenType::ImageAltBegin as usize, i, String::from("![")));
                    i += 2;
                    let start: usize = i;
                    let mut alt_text: String = String::new();
                    while let Some(c) = text.get(i..=i) {
                        match c {
                            "]" => {
                                tokens.push(Token::new(TokenType::ImageAltText as usize, start, i, alt_text));
                                tokens.push(Token::new_single(TokenType::ImageAltEnd as usize, i, String::from("]")));
                                i += 1;
                                break;
                            }
                            "\n" => {
                                debug::warn(format!("Line: {} Index: {} -> Couldn't find closing ']' before a newline!", line, i).as_str());
                                tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c)));
                                line += 1;
                                break;
                            }
                            _ => alt_text += c,
                        }
                        i += 1;
                    }
                    next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                    match next_c {
                        "(" => {
                            tokens.push(Token::new_single(TokenType::ImagePathBegin as usize, i, String::from("(")));
                            i += 1;
                            let start: usize = i;
                            let mut image_path: String = String::new();
                            while let Some(c) = text.get(i..=i) {
                                match c {
                                    ")" => {
                                        tokens.push(Token::new(TokenType::ImagePathText as usize, start, i, image_path));
                                        tokens.push(Token::new_single(TokenType::ImagePathEnd as usize, i, String::from(")")));
                                        i += 1;
                                        break;
                                    }
                                    "\n" => {
                                        debug::warn(format!("Line: {} Index: {} -> Couldn't find closing ']' before a newline!", line, i).as_str());
                                        tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c)));
                                        line += 1;
                                        break;
                                    }
                                    _ => image_path += c,
                                }
                                i += 1;
                            }
                        }
                        _ => {
                            debug::warn(format!("Line: {} Index: {} -> Incorrect image declaration! Expected '(' found '{}'", line, i, next_c).as_str());
                            tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(next_c)));
                        }
                    }
                }
            }
            "?" => {
                let mut next_c = match text.get(i + 1..=i + 1) { Some(val) => val, None => break,};
                if next_c == "[" {
                    tokens.push(Token::new_double(TokenType::LinkAltBegin as usize, i, String::from("![")));
                    i += 2;
                    let start: usize = i;
                    let mut alt_text: String = String::new();
                    while let Some(c) = text.get(i..=i) {
                        match c {
                            "]" => {
                                tokens.push(Token::new(TokenType::LinkAltText as usize, start, i, alt_text));
                                tokens.push(Token::new_single(TokenType::LinkAltEnd as usize, i, String::from("]")));
                                i += 1;
                                break;
                            }
                            "\n" => {
                                debug::warn(format!("Line: {} Index: {} -> Couldn't find closing ']' before a newline!", line, i).as_str());
                                tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c)));
                                line += 1;
                                break;
                            }
                            _ => alt_text += c,
                        }
                        i += 1;
                    }
                    next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                    match next_c {
                        "(" => {
                            tokens.push(Token::new_single(TokenType::LinkPathBegin as usize, i, String::from("(")));
                            i += 1;
                            let start: usize = i;
                            let mut link_path: String = String::new();
                            while let Some(c) = text.get(i..=i) {
                                match c {
                                    ")" => {
                                        tokens.push(Token::new(TokenType::LinkPathText as usize, start, i, link_path));
                                        tokens.push(Token::new_single(TokenType::LinkPathEnd as usize, i, String::from(")")));
                                        i += 1;
                                        break;
                                    }
                                    "\n" => {
                                        debug::warn(format!("Line: {} Index: {} -> Couldn't find closing ']' before a newline!", line, i).as_str());
                                        tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c)));
                                        line += 1;
                                        break;
                                    }
                                    _ => link_path += c,
                                }
                                i += 1;
                            }
                        }
                        _ => {
                            debug::warn(format!("Line: {} Index: {} -> Incorrect link declaration! Expected '(' found '{}'", line, i, next_c).as_str());
                            tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(next_c)));
                        }
                    }
                }
            }
            "<" => {
                let mut html: bool = false;
                if match text.get(i + 1..=i + 1) { Some(val) => val, None => break,} == "<" {
                    tokens.push(Token::new_double(TokenType::HtmlBegin as usize, i, String::from("<<")));
                    i += 1;
                    html = true;
                } else if match text.get(i + 1..=i + 1) { Some(val) => val, None => break,} == "/" {
                    tokens.push(Token::new_double(TokenType::HtmlBegin as usize, i, String::from("</")));
                    i += 1;
                    html = true;
                }

                if html {
                    i += 1;
                    let start: usize = i;
                    while let Some(c) = text.get(i..=i) {
                        match c {
                            ">" => {
                                tokens.push(Token::new_single(TokenType::HtmlEnd as usize, i, String::from(">")));
                                break;
                            }
                            "\"" => {
                                tokens.push(Token::new_single(TokenType::HtmlAttributeText as usize, i, String::from("\"")));
                                i += 1;
                                while let Some(c) = text.get(i..=i) {
                                    match c {
                                        "\"" => {
                                            tokens.push(Token::new_single(TokenType::HtmlAttributeText as usize, i, String::from("\"")));
                                            break;
                                        }
                                        "\n" => {
                                            debug::warn(format!("Line: {} Index: {} -> Couldn't find closing '\"' before a newline!", line, i).as_str());
                                            tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c)));
                                            line += 1;
                                            i += 1;
                                            break;
                                        }
                                        _ => tokens.push(Token::new_single(TokenType::HtmlAttributeText as usize, i, String::from(c))),
                                    }
                                    i += 1;
                                }
                            }
                            _ => tokens.push(Token::new_single(TokenType::HtmlText as usize, i, String::from(c))),
                        }
                        i += 1;
                    }
                }
            }
            "/" => {
                i += 1;
                let mut next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                if let "/" = next_c {
                    tokens.push(Token::new_single(TokenType::Comment as usize, i - 1, String::from(next_c)));
                    tokens.push(Token::new_single(TokenType::Comment as usize, i, String::from(next_c)));
                    while next_c != "\n" {
                        i += 1;
                        next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                        tokens.push(Token::new_single(TokenType::Comment as usize, i, String::from(next_c)));
                    }
                }   
            }
            _ => tokens.push(Token::new_single(TokenType::Text as usize, i, String::from(c))),
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
