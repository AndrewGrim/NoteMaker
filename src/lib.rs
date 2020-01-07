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

#[pyfunction]
fn lex(_py: Python, text: String) -> PyResult<Vec<Token>> {
    let mut tokens: Vec<Token> = Vec::with_capacity(text.len());

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
            "*" => { // TODO rework to just parse the opening or closing tag not text within
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
            "~" => { // TODO rework to just parse the opening or closing tag not text within
                i += 1;
                let next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                if let "~" = next_c {
                    let result = match_strike(&text, i, line, &mut tokens);
                    i = result.0;
                    line = result.1;
                }
            }
            "_" => { // TODO rework to just parse the opening or closing tag not text within
                i += 1;
                let next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                if let "_" = next_c {
                    let result = match_underline(&text, i, line, &mut tokens);
                    i = result.0;
                    line = result.1;
                }
            }
            ":" => { // TODO allow for formatting within list text
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
                    let result = match_blockquote(&text, i, line, &mut tokens);
                    i = result.0;
                    line = result.1;
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
                if text.get(i - 1..i).expect("panic at pre block") == "p" && match text.get(i + 1..=i + 1) { Some(val) => val, None => break,} == "\n" {
                    tokens.pop().expect("failed at removing 'p'");
                    tokens.push(Token::new_single(TokenType::Format as usize, i - 1, String::from("f")));
                    tokens.push(Token::new_single(TokenType::FormatBlockBegin as usize, i, String::from("`")));
                    i += 1;
                    while let Some(c) = text.get(i..=i) {
                        match c {
                            "`" => {
                                tokens.push(Token::new_single(TokenType::FormatBlockEnd as usize, i, String::from("`")));
                                i += 1; // to step over the following newline
                                break;
                            }
                            "\n" =>  {
                                tokens.push(Token::new_single(TokenType::FormatBlockText as usize, i, String::from(c)));
                                line += 1;
                            }
                            _ => tokens.push(Token::new_single(TokenType::FormatBlockText as usize, i, String::from(c))),
                        }
                        i += 1;
                    }
                } else if text.get(i - 1..i).expect("panic at format block") == "f" && match text.get(i + 1..=i + 1) { Some(val) => val, None => break,} != "\n" {
                    tokens.pop().expect("failed at removing 'f'");
                    tokens.push(Token::new_single(TokenType::Format as usize, i - 1, String::from("f")));
                    tokens.push(Token::new_single(TokenType::CodeBlockBegin as usize, i, String::from("`")));
                    i += 1;
                    let start = i;
                    let mut language = String::new(); // TODO use language to read in file with grammar?
                    while let Some(c) = text.get(i..=i) {
                        match c {
                            "\n" => {
                                tokens.push(Token::new(TokenType::Format as usize, start, i, language));
                                break;
                            }
                            _ => language += c,
                        }
                        i += 1;
                    }
                    while let Some(c) = text.get(i..=i) {
                        match c {
                            "`" => {
                                tokens.push(Token::new_single(TokenType::CodeBlockEnd as usize, i, String::from("`")));
                                i += 1; // to step over the following newline
                                break;
                            }
                            "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9" =>  {
                                tokens.push(Token::new_single(TokenType::CodeBlockDigit as usize, i, String::from(c)));
                            }
                            ";"|":"|"("|")"|"{"|"}"|"["|"]"|"."|","|"+"|"-"|"*"|"/"|"<"|">"|"\\"|"&"|"="|"!"|"%" =>  {
                                tokens.push(Token::new_single(TokenType::CodeBlockSymbol as usize, i, String::from(c)));
                            }
                            "\""|"'" => {
                                tokens.push(Token::new_single(TokenType::CodeBlockString as usize, i, String::from(c)));
                                i += 1;
                                while let Some(c) = text.get(i..=i) {
                                    match c {
                                        "\""|"'" => {
                                            tokens.push(Token::new_single(TokenType::CodeBlockString as usize, i, String::from(c)));
                                            break;
                                        }
                                        "`" => {
                                            line += 1;
                                            i -= 1; // to make the outer loop match the closing `
                                            break;
                                        }
                                        _ => tokens.push(Token::new_single(TokenType::CodeBlockString as usize, i, String::from(c))),
                                    }
                                    i += 1;
                                }
                            }
                            _ => {
                                let mut key = false;
                                for k in keywords.iter() {
                                    if match_keyword(k, &text, i) {
                                        tokens.push(Token::new(TokenType::CodeBlockKeyword as usize, i, i + k.len(), String::from(k)));
                                        i += k.len() - 1;
                                        key = true;
                                        if k == "class" {
                                            i += 1;
                                            while let Some(c) = text.get(i..=i) {
                                                match c {
                                                    ":"|"(" => {
                                                        tokens.push(Token::new_single(TokenType::CodeBlockSymbol as usize, i, String::from(c)));
                                                        break;
                                                    }
                                                    _ => tokens.push(Token::new_single(TokenType::CodeBlockClass as usize, i, String::from(c))),
                                                }
                                                i += 1;
                                            }
                                        } else if k == "def" {
                                            i += 1;
                                            while let Some(c) = text.get(i..=i) {
                                                match c {
                                                    "(" => {
                                                        tokens.push(Token::new_single(TokenType::CodeBlockSymbol as usize, i, String::from(c)));
                                                        break;
                                                    }
                                                    _ => tokens.push(Token::new_single(TokenType::CodeBlockClass as usize, i, String::from(c))),
                                                }
                                                i += 1;
                                            }
                                        }
                                        break;
                                    }
                                }
                                if !key {
                                    for f in flow.iter() {
                                        if match_keyword(f, &text, i) {
                                            tokens.push(Token::new(TokenType::CodeBlockFlow as usize, i, i + f.len(), String::from(f)));
                                            i += f.len() - 1;
                                            key = true;
                                            break;
                                        }
                                    }
                                    if !key {
                                        for t in types.iter() {
                                            if match_keyword(t, &text, i) {
                                                tokens.push(Token::new(TokenType::CodeBlockType as usize, i, i + t.len(), String::from(t)));
                                                i += t.len() - 1;
                                                key = true;
                                                break;
                                            }
                                        }
                                    }
                                }

                                if !key {
                                    tokens.push(Token::new_single(TokenType::CodeBlock as usize, i, String::from(c)));
                                }
                            }
                        }
                        i += 1;
                    }
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
                            "\n" => line += 1, // this should prob break since its now goint to keep the formatting anyway
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
    m.add_wrapped(wrap_pyfunction!(regex_lex))?;

    Ok(())
}
