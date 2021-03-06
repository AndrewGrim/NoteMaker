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
        tokens.push(Token::new(TokenType::Heading as usize, i - (h_count - 1) - 1, i, h_count.to_string(), format!("<h{}>", h_count)));

        return (i, line);
    }

    tokens.push(Token::new(TokenType::Heading as usize, i - (h_count - 1) - 1, i, h_count.to_string(), format!("<h{}>", h_count)));
    tokens.push(Token::space(i));
    i += 1;

    let mut heading_text: String = String::new();
    let start: usize = i;
    while let Some(c) = text.get(i..=i) {
        match c {
            "\n" => {
                line += 1;
                tokens.push(Token::new(TokenType::HeadingText as usize, start, i, heading_text.clone(), heading_text));
                tokens.push(Token::new(TokenType::HeadingEnd as usize, 0, 0, h_count.to_string(), format!("</h{}>", h_count)));
                break;
            }
            _ => heading_text += c,
        }
        i += 1;
    }

    (i, line)
}

pub fn match_bold(text: &str, mut i: usize, line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.push(Token::new_double(TokenType::BoldBegin as usize, i - 1, String::from("**"), String::from("<b>")));
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
                        tokens.push(Token::new(TokenType::Bold as usize, start, i - 1, matched_text.clone(), matched_text));
                        tokens.push(Token::new_double(TokenType::BoldEnd as usize, i - 1, String::from("**"), String::from("</b>")));
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
    tokens.push(Token::new_single(TokenType::ItalicBegin as usize, i - 1, String::from("*"), String::from("<i>")));
    let mut matched_text: String = String::new();

    let start: usize = i;
    while let Some(c) = text.get(i..=i) {
        match c {
            "*" => {
                tokens.push(Token::new(TokenType::Italic as usize, start, i, matched_text.clone(), matched_text));
                tokens.push(Token::new_single(TokenType::ItalicEnd as usize, i, String::from("*"), String::from("</i>")));
                break;
            }
            _ => matched_text += c,
        }

        i += 1;
    }

    (i, line)
}

pub fn match_strike(text: &str, mut i: usize, line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.push(Token::new_double(TokenType::StrikeBegin as usize, i - 1, String::from("~~"), String::from("<strike>")));
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
                        tokens.push(Token::new(TokenType::Strike as usize, start, i - 1, matched_text.clone(), matched_text));
                        tokens.push(Token::new_double(TokenType::StrikeEnd as usize, i - 1, String::from("~~"), String::from("</strike>")));
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
    tokens.push(Token::new_double(TokenType::UnderlineBegin as usize, i - 1, String::from("__"), String::from("<u>")));
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
                        tokens.push(Token::new(TokenType::Underline as usize, start, i - 1, matched_text.clone(), matched_text));
                        tokens.push(Token::new_double(TokenType::UnderlineEnd as usize, i - 1, String::from("__"), String::from("</u>")));
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
    let mut l_count: usize = 0;
    let mut list_index: Vec<Token> = Vec::new();
    let mut list_item: bool = true;

    i += 1;
    let mut c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
    match c {
        "*" => {
            tokens.push(Token::new(TokenType::UnorderedListBegin as usize, i - 2, i + 1, String::from("::*"), String::from("<ul>")));
            tokens.push(Token::new_single(TokenType::ListItemBegin as usize, i, String::from("::*"), String::from("<li>")));
            list_index.push(Token::new_single(TokenType::UnorderedListEnd as usize, 0, String::new(), String::from("</ul>")));
        }
        "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9" => {
            tokens.push(Token::new(TokenType::OrderedListBegin as usize, i - 2, i + 1, String::from("::1"), String::from("<ol>")));
            tokens.push(Token::new_single(TokenType::ListItemBegin as usize, i, String::from("::1"), String::from("<li>")));
            list_index.push(Token::new_single(TokenType::UnorderedListEnd as usize, 0, String::new(), String::from("</ol>")));
        }
        _ => {
            debug::warn(format!("Line: {}, Index: {} -> Incorrect list start! Expected '*' or a digit, found '{}'", line, i, c).as_str());
            tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c), String::new()));
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
                tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c), String::new()));
            }
            break;
        } else if c == "\n" && &text[i - 1..i] != ";" {
            list_item = false;
            tokens.push(Token::new_single(TokenType::ListItemEnd as usize, i, String::from(c), String::from("</li>")));
        } else if c == ":" && match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} == ":" {
            i += 2;
            c = match text.get(i..=i) { Some(val) => val, None => break,};
            
            match c {
                "*" => {
                    tokens.push(Token::new(TokenType::UnorderedListBegin as usize, i - 2, i + 1, String::from("::*"), String::from("<ul>")));
                    tokens.push(Token::new_single(TokenType::ListItemBegin as usize, i, String::from("::*"), String::from("<li>")));
                    list_index.push(Token::new_single(TokenType::UnorderedListEnd as usize, 0, String::new(), String::from("</ul>")));
                }
                "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9" => {
                    tokens.push(Token::new(TokenType::OrderedListBegin as usize, i - 2, i + 1, String::from("::1"), String::from("<ol>")));
                    tokens.push(Token::new_single(TokenType::ListItemBegin as usize, i, String::from("::1"), String::from("<li>")));
                    list_index.push(Token::new_single(TokenType::UnorderedListEnd as usize, 0, String::new(), String::from("</ol>")));
                }
                _ => {
                    debug::warn(format!("Line: {}, Index: {} -> Incorrect list start! Expected '*' or a digit, found '{}'", line, i, c).as_str());
                    tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c), String::new()));
                    break;
                }
            }
            list_item = true;
            l_count += 1;
            i += 1;
            c = match text.get(i..=i) { Some(val) => val, None => break,};

        } else if ["*", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"].contains(&c) && !list_item {
            tokens.push(Token::new_single(TokenType::ListItemBegin as usize, i, String::from(c), String::from("<li>")));
            list_item = true;
            i += 1;
            c = match text.get(i..=i) { Some(val) => val, None => break,};
        }

        if list_item {
            tokens.push(Token::new_single(TokenType::ListItemText as usize, i, String::from(c), String::from(c)));
        } else if c == " " || c == "\t" || c == "\n" {

        } else if c == ";" {
            let mut t = list_index.last().expect("list index crash").clone();
            t.begin = i;
            t.end = i + 1;
            tokens.push(t);
            match list_index.pop() {
                Some(index) => l_count -= 1,
                None => {
                    debug::fail(format!("Line: {}, Index: {} -> Tried to pop and index from vector with none left!", line, i).as_str());
                    tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c), String::new()));
                }
            }
        } else {
            debug::warn(format!("Line: {}, Index: {} -> Improper list formatting! Found an alphanumeric symbol!", line, i).as_str());
            tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c), String::new()));
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
    tokens.push(Token::new_single(TokenType::BlockquoteBegin as usize, i, String::from(">"), String::from("<blockquote>")));
    tokens.push(Token::space(i + 1));
    i += 2;

    let start = i;
    let mut blockquote_text: String = String::new();
    while let Some(next_c) = text.get(i..=i) {
        match next_c {
            "\n" => {
                tokens.push(Token::new(TokenType::BlockquoteText as usize, start, i, blockquote_text.clone(), blockquote_text));
                tokens.push(Token::new_single(TokenType::BlockquoteEnd as usize, i, String::from("\n"), String::from("</blockquote>")));
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
        let result = match_preblock(text, i, line, tokens);
        i = result.0;
        line = result.1;
    } else if text.get(i - 1..i).expect("panic at format block") == "f" && match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} != "\n" {
        let result = match_codeblock(text, i, line, tokens);
        i = result.0;
        line = result.1;
    } else {
        let result = match_code(text, i, line, tokens);
        i = result.0;
        line = result.1;
    }

    (i, line)
}

fn match_preblock(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.pop().expect("failed at removing 'p'");
    tokens.push(Token::new_single(TokenType::Format as usize, i - 1, String::from("f"), String::new()));
    tokens.push(Token::new_single(TokenType::FormatBlockBegin as usize, i, String::from("`"), String::from("<pre style=\"color: #787726; background-color: #FEFFCC;\">")));
    i += 1;
    while let Some(c) = text.get(i..=i) {
        match c {
            "`" => {
                tokens.push(Token::new_single(TokenType::FormatBlockEnd as usize, i, String::from("`"), String::from("</pre>")));
                i += 1; // to step over the following newline
                break;
            }
            "\n" =>  {
                tokens.push(Token::new_single(TokenType::FormatBlockText as usize, i, String::from(c), String::from(c)));
                line += 1;
            }
            _ => tokens.push(Token::new_single(TokenType::FormatBlockText as usize, i, String::from(c), String::from(c))),
        }
        i += 1;
    }

    (i, line)
}

fn match_code(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.push(Token::new_single(TokenType::CodeBegin as usize, i, String::from("`"), String::from("<code>")));
    let start = i;
    let mut code_text: String = String::new();
    i += 1;
    while let Some(next_c) = text.get(i..=i) {
        match next_c {
            "`" => {
                tokens.push(Token::new(TokenType::Code as usize, start, i, code_text.clone(), code_text));
                tokens.push(Token::new_single(TokenType::CodeEnd as usize, i, String::from("`"), String::from("</code>")));
                break;
            }
            "\n" => line += 1, // this should prob break since its now goint to keep the formatting anyway
            _ => code_text += next_c,
        }
        i += 1;
    }

    (i, line)
}

fn match_codeblock(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.pop().expect("failed at removing 'f'");
    tokens.push(Token::new_single(TokenType::Format as usize, i - 1, String::from("f"), String::new()));
    tokens.push(Token::new_single(TokenType::CodeBlockBegin as usize, i, String::from("`"), String::from("<pre>")));
    i += 1;
    let language = match_language_name(text, i, line, tokens);
    i += language.len();
    let path = format!("Syntax/{}", language.to_ascii_lowercase());
    let lang_path = Path::new(path.as_str());
    let mut keywords: Vec<String> = Vec::new();
    let mut flow: Vec<String> = Vec::new();
    let mut types: Vec<String> = Vec::new();
    let mut declaration: Vec<String> = Vec::new();

    let keywords_exists = {
        if lang_path.exists() {
            read_syntax_file(language.to_ascii_lowercase(), "keywords.txt", &mut keywords)
        } else {
            false
        }
    };
    let flow_exists = {
        if lang_path.exists() {
            read_syntax_file(language.to_ascii_lowercase(), "flow.txt", &mut flow)
        } else {
            false
        }
    };
    let types_exists = {
        if lang_path.exists() {
            read_syntax_file(language.to_ascii_lowercase(), "types.txt", &mut types)
        } else {
            false
        }
    };
    let declaration_exists = {
        if lang_path.exists() {
            read_syntax_file(language.to_ascii_lowercase(), "declaration.txt", &mut declaration)
        } else {
            false
        }
    };

    while let Some(c) = text.get(i..=i) {
        match c {
            "`" => {
                tokens.push(Token::new_single(TokenType::CodeBlockEnd as usize, i, String::from("`"), String::from("</pre>")));
                i += 1; // to step over the following newline
                break;
            }
            "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9" =>  {
                tokens.push(Token::new_single(TokenType::CodeBlockDigit as usize, i, String::from(c), format!("<div class=\"digit\">{}</div>", c)));
            }
            ";"|":"|"("|")"|"{"|"}"|"["|"]"|"."|","|"+"|"-"|"*"|"\\"|"<"|">"|"&"|"="|"!"|"%" =>  {
                tokens.push(Token::new_single(TokenType::CodeBlockSymbol as usize, i, String::from(c), format!("<div class=\"symbol\">{}</div>", c)));
            }
            "\""|"'" => {
                tokens.push(Token::new_single(TokenType::CodeBlockString as usize, i, String::from(c), format!("<div class=\"string\">{}</div>", c)));
                i += 1;
                while let Some(c) = text.get(i..=i) {
                    match c {
                        "\""|"'" => {
                            tokens.push(Token::new_single(TokenType::CodeBlockString as usize, i, String::from(c), format!("<div class=\"string\">{}</div>", c)));
                            break;
                        }
                        "`" => {
                            line += 1;
                            i -= 1; // to make the outer loop match the closing `
                            break;
                        }
                        _ => tokens.push(Token::new_single(TokenType::CodeBlockString as usize, i, String::from(c), format!("<div class=\"string\">{}</div>", c))),
                    }
                    i += 1;
                }
            }
            "/" => {
                let result = match_codeblock_comment(&text, i, line, tokens);
                i = result.0;
                line = result.1;
            }
            _ => {
                if lang_path.exists() {
                    let mut key = false;
                    for k in keywords.iter() {
                        if match_keyword(k, &text, i) {
                            tokens.push(Token::new(TokenType::CodeBlockKeyword as usize, i, i + k.len(), String::from(k), format!("<div class=\"keyword\">{}</div>", k)));
                            i += k.len() - 1;
                            key = true;
                            if declaration_exists {
                                for d in declaration.iter() {
                                    if k == d {
                                        i += 1;
                                        while let Some(c) = text.get(i..=i) {
                                            match c {
                                                ":"|"("|"{"|"<" => {
                                                    tokens.push(Token::new_single(TokenType::CodeBlockSymbol as usize, i, String::from(c), format!("<div class=\"symbol\">{}</div>", c)));
                                                    break;
                                                }
                                                _ => tokens.push(Token::new_single(TokenType::CodeBlockClass as usize, i, String::from(c), format!("<div class=\"class\">{}</div>", c))),
                                            }
                                            i += 1;
                                        }
                                        break;
                                    }
                                }
                            }
                            break;
                        }
                    }
                    if !key {
                        for f in flow.iter() {
                            if match_keyword(f, &text, i) {
                                tokens.push(Token::new(TokenType::CodeBlockFlow as usize, i, i + f.len(), String::from(f), format!("<div class=\"flow\">{}</div>", f)));
                                i += f.len() - 1;
                                key = true;
                                break;
                            }
                        }
                        if !key {
                            for t in types.iter() {
                                if match_keyword(t, &text, i) {
                                    tokens.push(Token::new(TokenType::CodeBlockType as usize, i, i + t.len(), String::from(t), format!("<div class=\"type\">{}</div>", t)));
                                    i += t.len() - 1;
                                    key = true;
                                    break;
                                }
                            }
                        }
                    }

                    if !key {
                        tokens.push(Token::new_single(TokenType::CodeBlock as usize, i, String::from(c), String::from(c)));
                    }
                } else {
                    tokens.push(Token::new_single(TokenType::CodeBlock as usize, i, String::from(c), String::from(c)));
                }
            }
        }
        i += 1;
    }

    (i, line)
}

fn match_language_name(text: &str, mut i: usize, line: usize, tokens: &mut Vec<Token>) -> String {
    let mut language = String::new();
    
    let start = i;
    while let Some(c) = text.get(i..=i) {
        match c {
            "\n" => {
                tokens.push(Token::new(TokenType::Format as usize, start, i, String::from(&language), String::new()));
                break;
            }
            _ => language += c,
        }
        i += 1;
    }

    language
}

pub fn read_syntax_file(language: String, file: &str, syntax: &mut Vec<String>) -> bool {
    let mut exists = false;

    let syntax_path = format!("Syntax/{}/{}", language, file);
    let x_file = match fs::read_to_string(syntax_path) {
        Ok(val) => {
            exists = true;
            val
        }
        Err(e) => e.to_string(),
    };

    if exists {
        for line in x_file.split('\n') {
            syntax.push(String::from(line));
        }
    }

    exists
}

pub fn match_image(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    let mut next_c = match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),};
    if next_c == "[" {
        tokens.push(Token::new_double(TokenType::ImageAltBegin as usize, i, String::from("!["), String::from("<img alt=\"")));
        i += 2;
        let start: usize = i;
        let mut alt_text: String = String::new();
        while let Some(c) = text.get(i..=i) {
            match c {
                "]" => {
                    tokens.push(Token::new(TokenType::ImageAltText as usize, start, i, alt_text.clone(), alt_text));
                    tokens.push(Token::new_single(TokenType::ImageAltEnd as usize, i, String::from("]"), String::from("\" ")));
                    i += 1;
                    break;
                }
                "\n" => {
                    debug::warn(format!("Line: {} Index: {} -> Couldn't find closing ']' before a newline!", line, i).as_str());
                    tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c), String::new()));
                    line += 1;
                    break;
                }
                _ => alt_text += c,
            }
            i += 1;
        }
        next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
        match next_c {
            "(" => {
                tokens.push(Token::new_single(TokenType::ImagePathBegin as usize, i, String::from("("), String::from("src=\"")));
                i += 1;
                let start: usize = i;
                let mut image_path: String = String::new();
                while let Some(c) = text.get(i..=i) {
                    match c {
                        ")" => {
                            tokens.push(Token::new(TokenType::ImagePathText as usize, start, i, image_path.clone(), image_path));
                            tokens.push(Token::new_single(TokenType::ImagePathEnd as usize, i, String::from(")"), String::from("\">")));
                            break;
                        }
                        "\n" => {
                            debug::warn(format!("Line: {} Index: {} -> Couldn't find closing ']' before a newline!", line, i).as_str());
                            tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c), String::new()));
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
                tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(next_c), String::new()));
            }
        }
    }

    (i, line)
}

pub fn match_link(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    let mut next_c = match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),};
    if next_c == "[" {
        tokens.push(Token::new_double(TokenType::LinkAltBegin as usize, i, String::from("!["), String::from("<a ")));
        i += 2;
        let start: usize = i;
        let mut alt_text: String = String::new();
        while let Some(c) = text.get(i..=i) {
            match c {
                "]" => {
                    tokens.push(Token::new(TokenType::LinkAltText as usize, start, i, alt_text.clone(), String::new()));
                    tokens.push(Token::new_single(TokenType::LinkAltEnd as usize, i, String::from("]"), String::new()));
                    i += 1;
                    break;
                }
                "\n" => {
                    debug::warn(format!("Line: {} Index: {} -> Couldn't find closing ']' before a newline!", line, i).as_str());
                    tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c), String::new()));
                    line += 1;
                    break;
                }
                _ => alt_text += c,
            }
            i += 1;
        }
        next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
        match next_c {
            "(" => {
                tokens.push(Token::new_single(TokenType::LinkPathBegin as usize, i, String::from("("), String::from("href=\"")));
                i += 1;
                let start: usize = i;
                let mut link_path: String = String::new();
                while let Some(c) = text.get(i..=i) {
                    match c {
                        ")" => {
                            tokens.push(Token::new(TokenType::LinkPathText as usize, start, i, link_path.clone(), link_path));
                            tokens.push(Token::new_single(TokenType::LinkPathEnd as usize, i, String::from(")"), format!("\">{}</a>", alt_text)));
                            break;
                        }
                        "\n" => {
                            debug::warn(format!("Line: {} Index: {} -> Couldn't find closing ']' before a newline!", line, i).as_str());
                            tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c), String::new()));
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
                tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(next_c), String::new()));
            }
        }
    }

    (i, line)
}

pub fn match_html(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    let mut html: bool = false;
    if match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} == "<" {
        tokens.push(Token::new_double(TokenType::HtmlBegin as usize, i, String::from("<<"), String::from("<")));
        i += 1;
        html = true;
    } else if match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} == "/" {
        tokens.push(Token::new_double(TokenType::HtmlBegin as usize, i, String::from("</"), String::from("</")));
        i += 1;
        html = true;
    }

    if html {
        i += 1;
        let start: usize = i;
        while let Some(c) = text.get(i..=i) {
            match c {
                ">" => {
                    tokens.push(Token::new_single(TokenType::HtmlEnd as usize, i, String::from(">"), String::from(">")));
                    break;
                }
                "\"" => {
                    tokens.push(Token::new_single(TokenType::HtmlAttributeText as usize, i, String::from("\""), String::from("\"")));
                    i += 1;
                    while let Some(c) = text.get(i..=i) {
                        match c {
                            "\"" => {
                                tokens.push(Token::new_single(TokenType::HtmlAttributeText as usize, i, String::from("\""), String::from("\"")));
                                break;
                            }
                            "\n" => {
                                debug::warn(format!("Line: {} Index: {} -> Couldn't find closing '\"' before a newline!", line, i).as_str());
                                tokens.push(Token::new_single(TokenType::Error as usize, i, String::from(c), String::new()));
                                line += 1;
                                i += 1;
                                break;
                            }
                            _ => tokens.push(Token::new_single(TokenType::HtmlAttributeText as usize, i, String::from(c) , String::from(c))),
                        }
                        i += 1;
                    }
                }
                _ => tokens.push(Token::new_single(TokenType::HtmlText as usize, i, String::from(c), String::from(c))),
            }
            i += 1;
        }
    }
    
    (i, line)
}

pub fn match_codeblock_comment(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    i += 1;
    let mut next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
    if next_c == "/" {
        tokens.push(Token::new_single(TokenType::CodeBlockComment as usize, i - 1, String::from(next_c), format!("<div class=\"comment\">{}</div>", next_c)));
        tokens.push(Token::new_single(TokenType::CodeBlockComment as usize, i, String::from(next_c), format!("<div class=\"comment\">{}</div>", next_c)));
        while next_c != "\n" {
            i += 1;
            next_c = match text.get(i..=i) { Some(val) => val, None => break,};
            tokens.push(Token::new_single(TokenType::CodeBlockComment as usize, i, String::from(next_c), format!("<div class=\"comment\">{}</div>", next_c)));
        }
    } else if next_c == "*" {
        tokens.push(Token::new_single(TokenType::CodeBlockComment as usize, i - 1, String::from("/"), String::from("<div class=\"comment\">/</div>")));
        tokens.push(Token::new_single(TokenType::CodeBlockComment as usize, i, String::from(next_c), format!("<div class=\"comment\">{}</div>", next_c)));
        i += 1;
        next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
        while next_c != "*" && match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} != "/"{
            if next_c == "\n" {
                line += 1;
                tokens.push(Token::new_single(TokenType::Newline as usize, i, String::from(next_c), format!("<div class=\"comment\">{}</div>", next_c))); // might be problematic
            } else {
                tokens.push(Token::new_single(TokenType::CodeBlockComment as usize, i, String::from(next_c), format!("<div class=\"comment\">{}</div>", next_c)));
            }
            i += 1;
            next_c = match text.get(i..=i) { Some(val) => val, None => break,};
        }
        tokens.push(Token::new_single(TokenType::CodeBlockComment as usize, i, String::from("*"), String::from("<div class=\"comment\">*</div>")));
        tokens.push(Token::new_single(TokenType::CodeBlockComment as usize, i + 1, String::from("/"), String::from("<div class=\"comment\">/</div>")));
    }

    (i, line)
}

pub fn match_comment(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    i += 1;
    let mut next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
    if next_c == "/" {
        tokens.push(Token::new_single(TokenType::Comment as usize, i - 1, String::from(next_c), String::new()));
        tokens.push(Token::new_single(TokenType::Comment as usize, i, String::from(next_c), String::new()));
        while next_c != "\n" {
            i += 1;
            next_c = match text.get(i..=i) { Some(val) => val, None => break,};
            tokens.push(Token::new_single(TokenType::Comment as usize, i, String::from(next_c), String::new()));
        }
    } else if next_c == "*" {
        tokens.push(Token::new_single(TokenType::Comment as usize, i - 1, String::from("/"), String::new()));
        tokens.push(Token::new_single(TokenType::Comment as usize, i, String::from(next_c), String::new()));
        i += 1;
        next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
        while next_c != "*" && match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} != "/"{
            if next_c == "\n" {
                line += 1;
            } else {
                tokens.push(Token::new_single(TokenType::Comment as usize, i, String::from(next_c), String::new()));
            }
            i += 1;
            next_c = match text.get(i..=i) { Some(val) => val, None => break,};
        }
        tokens.push(Token::new_single(TokenType::Comment as usize, i + 1, String::from("/"), String::new()));
    }

    (i, line)
}

pub fn match_table(text: &str, mut i: usize, mut line: usize, tokens: &mut Vec<Token>) -> (usize, usize) {
    tokens.push(Token::new_single(TokenType::TableBegin as usize, i, String::from("|"), String::from("<table>\n")));
    tokens.push(Token::new_single(TokenType::TableRowBegin as usize, i, String::from("|"), String::from("<tr>\n")));

    let mut col_count: usize = 0;
    let mut col_alignment: Vec<String> = Vec::new();

    i += 5;
    let mut next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
    let mut start: usize = i;
    while next_c != "\n" {
        let mut table_text = String::new();
        if next_c == "^" {
            col_alignment.insert(col_count, String::from("\"center\""))
        } else if next_c == ">" {
            col_alignment.insert(col_count, String::from("\"right\""))
        } else {
            col_alignment.insert(col_count, String::from("\"left\""))
        }
        i += 1;
        next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
        while next_c != "|" {
            table_text += next_c;
            i += 1;
            next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
        }
        i += 1;
        tokens.push(
            Token::new(
                TokenType::TableHeading as usize, 
                start + 1, i, table_text.clone(), 
                format!("<th align={}>{}</th>\n", 
                    match col_alignment.get(col_count) { Some(val) => val, None => return (i, line),}, 
                    table_text
                )
            )
        );
        col_count += 1;
        next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
    }
    tokens.push(Token::new_single(TokenType::TableRowEnd as usize, i, String::from("|"), String::from("</tr>\n")));
    line += 1;

    i += 1;
    next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
    while next_c != "\n" && match text.get(i + 1..=i + 1) { Some(val) => val, None => return (i, line),} != "\n" {
        col_count = 0;
        while next_c != "\n" {
            let mut table_text = String::new();
            i += 1;
            next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
            start = i;
            while next_c != "|" {
                table_text += next_c;
                i += 1;
                next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
            }
            i += 1;
            tokens.push(
                Token::new(
                    TokenType::TableData as usize, 
                    start + 1, i, table_text.clone(), 
                    format!("<td align={}>{}</td>\n", 
                        match col_alignment.get(col_count) { Some(val) => val, None => return (i, line),}, 
                        table_text
                    )
                )
            );
            col_count += 1;
            next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
        }
        tokens.push(Token::new_single(TokenType::TableRowEnd as usize, i, String::from("|"), String::from("</tr>\n")));
        line += 1;
        i += 1;
        next_c = match text.get(i..=i) { Some(val) => val, None => return (i, line),};
    }
    tokens.push(Token::new_single(TokenType::TableEnd as usize, i, String::from("|"), String::from("</table>\n")));

    (i, line)
}