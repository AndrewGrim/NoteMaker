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
    tokens.push(Token::new_space(i));
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