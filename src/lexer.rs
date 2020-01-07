use std::path::Path;
use std::fs;

use crate::debug;
use crate::token::Token;
use crate::token_type::TokenType;

pub fn match_heading(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    let mut heading: String = String::new();
    let mut h_count: usize = 0;

    while let Some(c) = text.get(i..=i) {
        match c {
            "#" => {
                h_count += 1;
                heading += c;
            }
            _ => break,
        }
        i += 1;
    }

    if h_count > 6 {
        debug::warn(format!("Line: {}, Index: {} -> Too many #! Heading only go up to 6!", line, i).as_str());
        tokens.push(Token::new(TokenType::Error as usize, i - (h_count - 1) - 1, i, heading));

        return (i, line);
    }

    tokens.push(Token::new(TokenType::Heading as usize, i - (h_count - 1) - 1, i, heading,));
    tokens.push(Token::space(i));
    i += 1;

    let mut heading_text: String = String::new();
    let start: usize = i;
    while let Some(c) = text.get(i..=i) {
        match c {
            "\n" => {
                line += 1;
                tokens.push(Token::new(TokenType::HeadingText as usize, start, i, heading_text));
                tokens.push(Token::empty(TokenType::HeadingEnd as usize));
                break;
            }
            _ => heading_text += c,
        }
        i += 1;
    }

    (i, line)
}

pub fn match_bold(text: &str, mut i: usize, line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.push(Token::new_double(TokenType::BoldBegin as usize, i - 1, String::from("**")));
    i += 1;
    let mut matched_text: String = String::new();

    let start: usize = i;
    while let Some(c) = text.get(i..=i) {
        match c {
            "*" => {
                i += 1;
                let next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                match next_c {
                    "*" => {
                        tokens.push(Token::new(TokenType::Bold as usize, start, i - 1, matched_text));
                        tokens.push(Token::new_double(TokenType::BoldEnd as usize, i - 1, String::from("**")));
                        break;
                    }
                    _ => break,
                }
            }
            _ => matched_text += c,
        }
        i += 1;
    }

    (i, line)
}

pub fn match_italic(text: &str, mut i: usize, line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.push(Token::new_single(TokenType::ItalicBegin as usize, i - 1, String::from("*")));
    let mut matched_text: String = String::new();

    let start: usize = i;
    while let Some(c) = text.get(i..=i) {
        match c {
            "*" => {
                tokens.push(Token::new(TokenType::Italic as usize, start, i, matched_text));
                tokens.push(Token::new_single(TokenType::ItalicEnd as usize, i, String::from("*")));
                break;
            }
            _ => matched_text += c,
        }

        i += 1;
    }

    (i, line)
}

pub fn match_strike(text: &str, mut i: usize, line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.push(Token::new_double(TokenType::StrikeBegin as usize, i - 1, String::from("~~")));
    i += 1;
    let mut matched_text: String = String::new();

    let start: usize = i;
    while let Some(c) = text.get(i..=i) {
        match c {
            "~" => {
                i += 1;
                let next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                match next_c {
                    "~" => {
                        tokens.push(Token::new(TokenType::Strike as usize, start, i - 1, matched_text));
                        tokens.push(Token::new_double(TokenType::StrikeEnd as usize, i - 1, String::from("~~")));
                        break;
                    }
                    _ => break,
                }
            }
            _ => matched_text += c,
        }
        i += 1;
    }

    (i, line)
}

pub fn match_underline(text: &str, mut i: usize, line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.push(Token::new_double(TokenType::UnderlineBegin as usize, i - 1, String::from("__")));
    i += 1;
    let mut matched_text: String = String::new();

    let start: usize = i;
    while let Some(c) = text.get(i..=i) {
        match c {
            "_" => {
                i += 1;
                let next_c = match text.get(i..=i) { Some(val) => val, None => break,};
                match next_c {
                    "_" => {
                        tokens.push(Token::new(TokenType::Underline as usize, start, i - 1, matched_text));
                        tokens.push(Token::new_double(TokenType::UnderlineEnd as usize, i - 1, String::from("__")));
                        break;
                    }
                    _ => break,
                }
            }
            _ => matched_text += c,
        }
        i += 1;
    }

    (i, line)
}

pub fn match_list(text: &str, mut i: usize, line: usize, tokens: &mut Vec<Token>) -> (usize, usize) { 
    // TODO change "1" to check for any digit
    let mut l_count: usize = 0;
    let mut list_index: Vec<usize> = Vec::new();
    let mut list_item: bool = true;

    i += 1;
    let mut c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
    match c {
        "*" => {
            tokens.push(Token::new(TokenType::UnorderedListBegin as usize, i - 2, i + 1, String::from("::*")));
            tokens.push(Token::empty(TokenType::ListItemBegin as usize));
            list_index.push(TokenType::UnorderedListEnd as usize);
        }
        "1" => {
            tokens.push(Token::new(TokenType::OrderedListBegin as usize, i - 2, i + 1, String::from("::1")));
            tokens.push(Token::empty(TokenType::ListItemBegin as usize));
            list_index.push(TokenType::OrderedListEnd as usize);
        }
        _ => {
            debug::warn(format!("Line: {}, Index: {} -> Incorrect list start! Expected '*' or a digit, found '{}'", line, i, c).as_str());
            tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c)));
            return (i, line);
        }
    }
    l_count += 1;
    i += 1;

    loop {
        c = match text.get(i..=i) { Some(val) => val, None => break,};
        
        if c == "\n" && match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} == "\n" {
            if l_count > 0 {
                debug::warn(format!("Line: {}, Index: {} -> Found unclosed list/s! l_count should be 0 instead is '{}'!", line, i, l_count).as_str());
                tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c)));
            }
            break;
        } else if c == "\n" && &text[i - 1..i] != ";" {
            list_item = false;
            tokens.push(Token::new_single(TokenType::ListItemEnd as usize, i, String::from(c)));
        } else if c == ":" && match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} == ":" {
            i += 2;
            c = match text.get(i..=i) { Some(val) => val, None => break,};
            
            match c {
                "*" => {
                    tokens.push(Token::new(TokenType::UnorderedListBegin as usize, i - 2, i + 1, String::from("::*")));
                    tokens.push(Token::empty(TokenType::ListItemBegin as usize));
                    list_index.push(TokenType::UnorderedListEnd as usize);
                }
                "1" => {
                    tokens.push(Token::new(TokenType::OrderedListBegin as usize, i - 2, i + 1, String::from("::1")));
                    tokens.push(Token::empty(TokenType::ListItemBegin as usize));
                    list_index.push(TokenType::OrderedListEnd as usize);
                }
                _ => {
                    debug::warn(format!("Line: {}, Index: {} -> Incorrect list start! Expected '*' or a digit, found '{}'", line, i, c).as_str());
                    tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c)));
                    break;
                }
            }
            list_item = true;
            l_count += 1;
            i += 1;
            c = match text.get(i..=i) { Some(val) => val, None => break,};

        } else if c == "*" || c == "1" && !list_item {
            tokens.push(Token::new_single(TokenType::ListItemBegin as usize, i, String::from(c)));
            list_item = true;
            i += 1;
            c = match text.get(i..=i) { Some(val) => val, None => break,};
        }

        if list_item {
            tokens.push(Token::new_single(TokenType::ListItemText as usize, i, String::from(c)));
        } else if c == " " || c == "\t" || c == "\n" {

        } else if c == ";" {
            tokens.push(Token::new_single(*list_index.last().expect("list crash"), i, String::from(c)));
            match list_index.pop() {
                Some(index) => l_count -= 1,
                None => {
                    debug::fail(format!("Line: {}, Index: {} -> Tried to pop and index from vector with none left!", line, i).as_str());
                    tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c)));
                }
            }
        } else {
            debug::warn(format!("Line: {}, Index: {} -> Improper list formatting! Found an alphanumeric symbol!", line, i).as_str());
            tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c)));
            break;
        }

        i += 1;
    }

    (i, line)
}

pub fn match_keyword(keyword: &str, text: &str, i: usize) -> bool {
    assert!(!keyword.is_empty(), "Keyword length must be greater than zero!");

    let mut matched: bool = true;

    for num in 0..keyword.len() {
        let c = text.chars().nth(i + num).expect("error");
        let t = keyword.chars().nth(num).expect("error");

        if c != t {
            matched = false;
            return matched;
        }
    }

    if matched && text.chars().nth(i + keyword.len()).expect("error").is_alphanumeric() || text.chars().nth(i - 1).expect("error").is_alphanumeric() {
        matched = false;
        return matched;
    }

    matched
}

pub fn match_blockquote(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
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

    (i, line)
}

pub fn match_backticks(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    if text.get(i - 1..i).expect("panic at pre block") == "p" && match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} == "\n" {
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
    } else if text.get(i - 1..i).expect("panic at format block") == "f" && match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} != "\n" {
        tokens.pop().expect("failed at removing 'f'");
        tokens.push(Token::new_single(TokenType::Format as usize, i - 1, String::from("f")));
        tokens.push(Token::new_single(TokenType::CodeBlockBegin as usize, i, String::from("`")));
        i += 1;
        let start = i;
        let mut language = String::new(); // TODO use language to read in file with grammar?
        while let Some(c) = text.get(i..=i) {
            match c {
                "\n" => {
                    tokens.push(Token::new(TokenType::Format as usize, start, i, String::from(&language)));
                    break;
                }
                _ => language += c,
            }
            i += 1;
        }

        let path = format!("Syntax/{}", language.to_ascii_lowercase());
        let lang_path = Path::new(path.as_str());
        let mut keywords: Vec<String> = Vec::new();
        let mut flow: Vec<String> = Vec::new();
        let mut types: Vec<String> = Vec::new();
        let mut declaration: Vec<String> = Vec::new();

        if lang_path.exists() {
            let syntax_path = format!("Syntax/{}/keywords.txt", language.to_ascii_lowercase());
            let keywords_file = fs::read_to_string(syntax_path).expect("couldnt find 'keywords' file");
            for line in keywords_file.split('\n') {
                keywords.push(String::from(line));
            }

            let syntax_path = format!("Syntax/{}/flow.txt", language.to_ascii_lowercase());
            let flow_file = fs::read_to_string(syntax_path).expect("couldnt find 'flow' file");
            for line in flow_file.split('\n') {
                flow.push(String::from(line));
            }

            let syntax_path = format!("Syntax/{}/types.txt", language.to_ascii_lowercase());
            let types_file = fs::read_to_string(syntax_path).expect("couldnt find 'types' file");
            for line in types_file.split('\n') {
                types.push(String::from(line));
            }

            let syntax_path = format!("Syntax/{}/declaration.txt", language.to_ascii_lowercase());
            let declaration_file = fs::read_to_string(syntax_path).expect("couldnt find 'declaration' file");
            for line in declaration_file.split('\n') {
                declaration.push(String::from(line));
            }
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
                    
                    if lang_path.exists() {
                        let mut key = false;
                        for k in keywords.iter() {
                            if match_keyword(k, &text, i) {
                                tokens.push(Token::new(TokenType::CodeBlockKeyword as usize, i, i + k.len(), String::from(k)));
                                i += k.len() - 1;
                                key = true;
                                for d in declaration.iter() {
                                    if k == d {
                                        i += 1;
                                        while let Some(c) = text.get(i..=i) {
                                            match c {
                                                ":"|"("|"{"|"<" => {
                                                    tokens.push(Token::new_single(TokenType::CodeBlockSymbol as usize, i, String::from(c)));
                                                    break;
                                                }
                                                _ => tokens.push(Token::new_single(TokenType::CodeBlockClass as usize, i, String::from(c))),
                                            }
                                            i += 1;
                                        }
                                        break;
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
                    } else {
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

    (i, line)
}